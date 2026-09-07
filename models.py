"""
Copyright (c) 2024-2026 AstreaTSS

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

from datetime import date, datetime
from typing import Any

import msgspec


class SizeProperties(msgspec.Struct):
    width: int
    height: int
    size: str
    aspect: int


class AttachmentMeta(msgspec.Struct):
    original: SizeProperties
    small: SizeProperties


class MediaAttachment(msgspec.Struct):
    id: str
    type: str
    url: str
    preview_url: str
    remote_url: str | None
    preview_remote_url: str | None
    text_url: str | None
    meta: AttachmentMeta
    description: str | None
    blurhash: str | None


class PreviewCard:
    url: str
    title: str
    description: str | None
    language: str
    type: str
    author_name: str
    author_url: str
    provider_name: str
    provider_url: str
    html: str
    width: int
    height: int
    image: str | None
    image_description: str | None
    embed_url: str
    blurhash: str | None
    published_at: Any | None


class Field(msgspec.Struct):
    name: str
    value: str
    verified_at: datetime | None


class Account(msgspec.Struct):
    id: str
    username: str
    acct: str
    display_name: str
    locked: bool
    bot: bool
    discoverable: bool
    indexable: bool
    group: bool
    created_at: datetime
    note: str
    url: str
    uri: str
    avatar: str
    avatar_static: str
    header: str
    header_static: str
    followers_count: int
    following_count: int
    statuses_count: int
    last_status_at: date | None
    hide_collections: bool
    noindex: bool | None
    emojis: list[Any]
    roles: list[Any]
    fields: list[Field]


class MastodonStatus(msgspec.Struct):
    id: str
    created_at: datetime
    in_reply_to_id: str | None
    in_reply_to_account_id: str | None
    sensitive: bool
    spoiler_text: str
    visibility: str
    language: str | None
    uri: str
    url: str | None
    replies_count: int
    reblogs_count: int
    favourites_count: int
    edited_at: str | None
    local_only: bool
    content: str
    reblog: Any
    application: Any
    account: Account
    media_attachments: list[MediaAttachment]
    mentions: list[Any]
    tags: list[Any]
    emojis: list[Any]
    card: PreviewCard | None
    poll: Any
    favourited: bool
    reblogged: bool
    muted: bool
    bookmarked: bool
    pinned: bool
    filtered: list[Any]

    @property
    def pretty_url(self) -> str:
        return self.url or self.uri


class Event(msgspec.Struct):
    stream: list[str]
    event: str
    payload: str


mastodon_status_decoder = msgspec.json.Decoder(MastodonStatus)
account_decoder = msgspec.json.Decoder(Account)
event_decoder = msgspec.json.Decoder(Event)
