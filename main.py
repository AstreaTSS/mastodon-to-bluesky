"""
Copyright (c) 2024 AstreaTSS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import contextlib
import logging
import os
import sys
from html.parser import HTMLParser
from typing import TYPE_CHECKING, Any, NamedTuple

import aiohttp
import atproto
import msgspec
from dotenv import load_dotenv

from models import event_decoder, update_payload_decoder

if TYPE_CHECKING:
    from atproto_client.models.blob_ref import BlobRef

load_dotenv()

decoder = msgspec.json.Decoder()
log = logging.getLogger("mastodon-bluesky")

log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))


class LinkData(NamedTuple):
    start_index: int
    end_index: int
    url: str


class ContentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.data: list[str] = []
        self.links: list[LinkData] = []
        self.double_line: bool = False
        self.character_index = 0

    def handle_data(self, data: str) -> None:
        if self.double_line:
            self.data.append("\n\n")
            self.character_index += 2
        self.data.append(data)
        self.character_index += len(data)
        self.double_line = True

    def handle_startendtag(self, tag: str, _: Any) -> None:
        if tag == "br":
            self.data.append("\n")
            self.character_index += 1
            self.double_line = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        if tag == "span":
            self.double_line = False
        elif tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    self.links.append(
                        LinkData(
                            self.character_index,
                            -1,
                            attr[1],
                        )
                    )

    def handle_endtag(self, tag: str) -> None:
        if tag == "span":
            self.double_line = True
        elif tag == "a":
            self.links[-1] = self.links[-1]._replace(end_index=self.character_index)


async def main() -> None:
    bluesky = atproto.AsyncClient()
    await bluesky.login(os.environ["BLUESKY_USERNAME"], os.environ["BLUESKY_PASSWORD"])

    log.info("Logged into Bluesky! Setting up Mastodon connection...")

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(
            f"wss://{os.environ['MASTODON_INSTANCE']}/api/v1/streaming",
            headers={"Authorization": f"Bearer {os.environ['MASTODON_ACCESS_TOKEN']}"},
        ) as ws:
            await ws.send_json({
                "type": "subscribe",
                "stream": "list",
                "list": os.environ["MASTODON_LIST_ID"],
                "access_token": os.environ["MASTODON_ACCESS_TOKEN"],
            })

            log.info("Connected to Mastodon! Listening for updates...")

            async for msg in ws:
                try:
                    data = event_decoder.decode(msg.data)

                    if data.event != "update":
                        continue

                    payload = update_payload_decoder.decode(data.payload)

                    log.info("Received post: %s", payload.url)

                    if payload.in_reply_to_id is not None:
                        log.info("Ignoring reply post: %s", payload.url)
                        continue

                    if payload.reblog is not None:
                        log.info("Ignoring reblog: %s", payload.url)
                        continue

                    data_parser = ContentParser()
                    data_parser.feed(payload.content)
                    data_parser.close()

                    parsed_content = "".join(data_parser.data).strip()

                    if len(parsed_content) > 300:
                        log.info("Ignoring post with too much text: %s", payload.url)
                        continue

                    if parsed_content.startswith("[Mastodon]"):
                        log.info(
                            "Ignoring post meant for Mastodon only: %s", payload.url
                        )
                        continue

                    if payload.visibility != "public":
                        log.info("Ignoring non-public post: %s", payload.url)
                        continue

                    image_blobs: list[tuple["BlobRef", str | None]] = []

                    for attachment in payload.media_attachments:
                        if attachment.type == "image":
                            async with session.get(attachment.url) as resp:
                                if resp.status != 200:
                                    continue

                                img_data = await resp.read()
                                resp = await bluesky.upload_blob(img_data)
                                image_blobs.append((resp.blob, attachment.description))

                    images = [
                        atproto.models.AppBskyEmbedImages.Image(
                            alt=image_alt or "", image=blob
                        )
                        for blob, image_alt in image_blobs
                    ]

                    embed = None

                    if images:
                        embed = atproto.models.AppBskyEmbedImages.Main(images=images)
                    elif payload.card is not None:
                        if payload.card.image is not None:
                            async with session.get(payload.card.image) as resp:
                                if resp.status != 200:
                                    continue

                                img_data = await resp.read()
                                resp = await bluesky.upload_blob(img_data)
                                blob = resp.blob
                        else:
                            blob = None

                        embed = atproto.models.AppBskyEmbedExternal.Main(
                            external=atproto.models.AppBskyEmbedExternal.External(
                                title=payload.card.title,
                                description=payload.card.description or "",
                                uri=payload.card.url,
                                thumb=blob,
                            )
                        )

                    bluesky_post = await bluesky.send_post(
                        text=parsed_content,
                        embed=embed,
                        facets=[
                            atproto.models.AppBskyRichtextFacet.Main(
                                features=[
                                    atproto.models.AppBskyRichtextFacet.Link(
                                        uri=link_data.url
                                    )
                                ],
                                index=atproto.models.AppBskyRichtextFacet.ByteSlice(
                                    byteEnd=link_data.end_index,
                                    byteStart=link_data.start_index,
                                ),
                            )
                            for link_data in data_parser.links
                        ],
                    )

                    log.info("Posted %s to Bluesky: %s", payload.url, bluesky_post.uri)
                except Exception as e:
                    log.error("Error processing message", exc_info=e)


async def wrapped_main() -> None:
    with contextlib.suppress(asyncio.CancelledError, KeyboardInterrupt):
        await main()


asyncio.run(wrapped_main())
