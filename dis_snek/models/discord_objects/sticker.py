from enum import IntEnum
from typing import TYPE_CHECKING, List, Optional, Union, Awaitable

import attr
from attr.converters import optional

from dis_snek.const import MISSING
from dis_snek.models.discord import DiscordObject
from dis_snek.models.snowflake import to_snowflake
from dis_snek.utils.attr_utils import define
from dis_snek.utils.proxy import CacheProxy
from dis_snek.utils.serializer import dict_filter_none

if TYPE_CHECKING:
    from dis_snek.models.discord_objects.guild import Guild
    from dis_snek.models.discord_objects.user import User
    from dis_snek.models.snowflake import Snowflake_Type


class StickerTypes(IntEnum):
    """Types of sticker."""

    STANDARD = 1
    """An official sticker in a pack, part of Nitro or in a removed purchasable pack."""
    GUILD = 2
    """A sticker uploaded to a Boosted guild for the guild's members."""


class StickerFormatTypes(IntEnum):
    """File formats for stickers."""

    PNG = 1
    APNG = 2
    LOTTIE = 3


@define(kw_only=False)
class StickerItem(DiscordObject):
    name: str = attr.ib()
    """Name of the sticker."""
    format_type: StickerFormatTypes = attr.ib(converter=StickerFormatTypes)
    """Type of sticker image format."""


@define()
class Sticker(StickerItem):
    """Represents a sticker that can be sent in messages."""

    pack_id: Optional["Snowflake_Type"] = attr.ib(default=None, converter=optional(to_snowflake))
    """For standard stickers, id of the pack the sticker is from."""
    description: Optional[str] = attr.ib(default=None)
    """Description of the sticker."""
    tags: str = attr.ib()
    """autocomplete/suggestion tags for the sticker (max 200 characters)"""
    type: Union[StickerTypes, int] = attr.ib(converter=StickerTypes)
    """Type of sticker."""
    available: Optional[bool] = attr.ib(default=True)
    """Whether this guild sticker can be used, may be false due to loss of Server Boosts."""
    sort_value: Optional[int] = attr.ib(default=None)
    """The standard sticker's sort order within its pack."""

    _user_id: Optional["Snowflake_Type"] = attr.ib(default=None, converter=optional(to_snowflake))
    _guild_id: Optional["Snowflake_Type"] = attr.ib(default=None, converter=optional(to_snowflake))

    @property
    def user(self) -> Optional[Union[CacheProxy, Awaitable["User"], "User"]]:
        """Get the user that uploaded this sticker. This will not be present for standard type.

        ??? warning "Awaitable Property:"
            This property must be awaited.

        returns:
            The user object.
        """
        if self._user_id:
            return CacheProxy(id=self._user_id, method=self._client.cache.get_user)

    @property
    def guild(self) -> Optional[Union[CacheProxy, Awaitable["Guild"], "Guild"]]:
        """Get the guild this sticker belongs to. This will not be present for standard type.

        ??? warning "Awaitable Property:"
            This property must be awaited.

        returns:
            The guild object.
        """
        if self._guild_id:
            return CacheProxy(id=self._guild_id, method=self._client.cache.get_guild)

    async def edit(
        self,
        name: Optional[str] = MISSING,
        description: Optional[str] = MISSING,
        tags: Optional[str] = MISSING,
        reason: Optional[str] = MISSING,
    ) -> "Sticker":
        """
        # TODO
        """
        if not self._guild_id:
            raise ValueError("You can only edit guild stickers.")

        payload = dict_filter_none(dict(name=name, description=description, tags=tags))
        sticker_data = await self._client.http.modify_guild_sticker(payload, self._guild_id, self.id, reason)
        return self.update_from_dict(sticker_data)

    async def delete(self, reason: Optional[str] = MISSING):
        """
        # TODO
        """
        if not self._guild_id:
            raise ValueError("You can only delete guild stickers.")

        await self._client.http.delete_guild_sticker(self._guild_id, self.id, reason)


@define()
class StickerPack(DiscordObject):
    """Represents a pack of standard stickers."""

    stickers: List["Sticker"] = attr.ib(factory=list)
    """The stickers in the pack."""
    name: str = attr.ib()
    """Name of the sticker pack."""
    sku_id: "Snowflake_Type" = attr.ib()
    """id of the pack's SKU."""
    cover_sticker_id: Optional["Snowflake_Type"] = attr.ib(default=None)
    """id of a sticker in the pack which is shown as the pack's icon."""
    description: str = attr.ib()
    """Description of the sticker pack."""
    banner_asset_id: "Snowflake_Type" = attr.ib()  # TODO CDN Asset
    """id of the sticker pack's banner image."""
