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

from dataclasses import dataclass
from enum import IntEnum
from html.parser import HTMLParser
from typing import Any

import atproto


class LinkMode(IntEnum):
    URL = 0
    HASHTAG = 1
    MENTION = 2


@dataclass
class LinkData:
    start_index: int
    end_index: int
    url: str


@dataclass
class HashtagData:
    start_index: int
    end_index: int
    hashtag: str


class ContentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.data: list[str] = []
        self.hashtags: list[HashtagData] = []
        self.links: list[LinkData] = []
        self.link_mode = LinkMode.URL
        self.double_line: bool = False
        self.character_index = 0

    def handle_data(self, data: str) -> None:
        if self.double_line:
            self.data.append("\n\n")
            self.character_index += 2

        if self.link_mode == LinkMode.HASHTAG:
            self.hashtags[-1].hashtag += data

        self.data.append(data)
        self.character_index += len(data)
        self.double_line = True

    def handle_startendtag(self, tag: str, _: Any) -> None:
        if tag == "br":
            self._handle_single_line()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        if tag == "a":
            if class_attr := next(
                (attr[1] for attr in attrs if attr[0] == "class"), None
            ):
                if "mention hashtag" in class_attr:
                    self.link_mode = LinkMode.HASHTAG
                    self.hashtags.append(
                        HashtagData(
                            self.character_index,
                            -1,
                            "",
                        )
                    )
                elif "u-url mention" in class_attr:
                    self.link_mode = LinkMode.MENTION
            elif href_attr := next(
                (attr[1] for attr in attrs if attr[0] == "href"), None
            ):
                self.link_mode = LinkMode.URL
                self.links.append(
                    LinkData(
                        self.character_index,
                        -1,
                        href_attr,
                    )
                )

        elif tag == "br":
            self._handle_single_line()
        elif tag == "span":
            self.double_line = False

    def _handle_single_line(self) -> None:
        self.data.append("\n")
        self.character_index += 1
        self.double_line = False

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            if self.link_mode == LinkMode.MENTION:
                return

            if self.link_mode == LinkMode.HASHTAG:
                self.hashtags[-1].end_index = self.character_index
                self.link_mode = LinkMode.URL
            else:
                self.links[-1].end_index = self.character_index
        elif tag == "p":
            self.double_line = True
        elif tag == "span":
            self.double_line = False

    @property
    def content(self) -> str:
        return "".join(self.data).strip()

    def build_facets(self) -> list[atproto.models.AppBskyRichtextFacet.Main]:
        link_facets = [
            atproto.models.AppBskyRichtextFacet.Main(
                features=[
                    atproto.models.AppBskyRichtextFacet.Link(uri=link_data.url.strip())
                ],
                index=atproto.models.AppBskyRichtextFacet.ByteSlice(
                    byteEnd=link_data.end_index,
                    byteStart=link_data.start_index,
                ),
            )
            for link_data in self.links
        ]
        hashtag_facets = [
            atproto.models.AppBskyRichtextFacet.Main(
                features=[
                    atproto.models.AppBskyRichtextFacet.Tag(
                        tag=hashtag_data.hashtag.strip()
                    )
                ],
                index=atproto.models.AppBskyRichtextFacet.ByteSlice(
                    byteEnd=hashtag_data.end_index,
                    byteStart=hashtag_data.start_index,
                ),
            )
            for hashtag_data in self.hashtags
        ]
        return link_facets + hashtag_facets


if __name__ == "__main__":
    import json

    input_str = input("Enter test string: ")

    try:
        test_str = json.loads(f'"{input_str}"')
    except json.JSONDecodeError:
        test_str = input_str

    parser = ContentParser()
    parser.feed(test_str)
    print(parser.content)  # noqa: T201
    print(parser.hashtags)  # noqa: T201
    print(parser.links)  # noqa: T201
