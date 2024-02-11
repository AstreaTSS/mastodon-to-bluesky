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

from datetime import date, datetime
from typing import Any, Optional

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
    remote_url: Optional[str]
    preview_remote_url: Optional[str]
    text_url: Optional[str]
    meta: AttachmentMeta
    description: Optional[str]
    blurhash: Optional[str]


class Card:
    url: str
    title: str
    description: Optional[str]
    language: str
    type: str
    author_name: str
    author_url: str
    provider_name: str
    provider_url: str
    html: str
    width: int
    height: int
    image: Optional[str]
    image_description: Optional[str]
    embed_url: str
    blurhash: Optional[str]
    published_at: Optional[Any]


class Field(msgspec.Struct):
    name: str
    value: str
    verified_at: Optional[datetime]


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
    last_status_at: date
    hide_collections: bool
    noindex: bool
    emojis: list[Any]
    roles: list[Any]
    fields: list[Field]


class UpdatePayload(msgspec.Struct):
    id: str
    created_at: datetime
    in_reply_to_id: Any
    in_reply_to_account_id: Any
    sensitive: bool
    spoiler_text: str
    visibility: str
    language: str
    uri: str
    url: str
    replies_count: int
    reblogs_count: int
    favourites_count: int
    edited_at: None
    local_only: bool
    content: str
    reblog: Any
    application: Any
    account: Account
    media_attachments: list[MediaAttachment]
    mentions: list[Any]
    tags: list[Any]
    emojis: list[Any]
    card: Optional[Card]
    poll: Any
    favourited: bool
    reblogged: bool
    muted: bool
    bookmarked: bool
    pinned: bool
    filtered: list[Any]


class Event(msgspec.Struct):
    stream: list[str]
    event: str
    payload: str


update_payload_decoder = msgspec.json.Decoder(UpdatePayload)
event_decoder = msgspec.json.Decoder(Event)
