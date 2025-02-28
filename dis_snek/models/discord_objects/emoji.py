from attr.converters import optional

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, Awaitable

import attr
from dis_snek.mixins.serialization import DictSerializationMixin
from dis_snek.models.snowflake import SnowflakeObject, to_snowflake
from dis_snek.utils.attr_utils import define, field
from dis_snek.utils.converters import list_converter
from dis_snek.utils.proxy import CacheProxy, CacheView
from dis_snek.utils.serializer import dict_filter_none, no_export_meta

if TYPE_CHECKING:
    from dis_snek.client import Snake
    from dis_snek.models.discord_objects.guild import Guild
    from dis_snek.models.discord_objects.user import User
    from dis_snek.models.discord_objects.role import Role
    from dis_snek.models.snowflake import Snowflake_Type


@define()
class Emoji(SnowflakeObject, DictSerializationMixin):
    """Represent a basic emoji used in discord."""

    id: Optional["Snowflake_Type"] = attr.ib(
        default=None, converter=optional(to_snowflake)
    )  # can be None for Standard Emoji
    """The custom emoji id. Leave empty if you are using standard unicode emoji."""
    name: Optional[str] = attr.ib(default=None)
    """The custom emoji name, or standard unicode emoji in string"""
    animated: bool = attr.ib(default=False)
    """Whether this emoji is animated"""

    @classmethod
    def unicode(cls, emoji: str):
        return cls(name=emoji)

    def __str__(self) -> str:
        return f"<{'a:' if self.animated else ''}{self.name}:{self.id}>"  # <:thinksmart:623335224318754826>

    @property
    def req_format(self) -> str:
        """
        Format used for web request.
        """
        if self.id:
            return f"{self.name}:{self.id}"
        else:
            return self.name


@define()
class CustomEmoji(Emoji):
    """Represent a custom emoji in a guild with all its properties."""

    _client: "Snake" = field(metadata=no_export_meta)

    require_colons: bool = attr.ib(default=False)
    """Whether this emoji must be wrapped in colons"""
    managed: bool = attr.ib(default=False)
    """Whether this emoji is managed"""
    available: bool = attr.ib(default=False)
    """Whether this emoji can be used, may be false due to loss of Server Boosts."""

    _creator_id: Optional["Snowflake_Type"] = attr.ib(default=None, converter=optional(to_snowflake))
    _role_ids: List["Snowflake_Type"] = attr.ib(factory=list, converter=optional(list_converter(to_snowflake)))
    _guild_id: Optional["Snowflake_Type"] = attr.ib(default=None, converter=optional(to_snowflake))

    @classmethod
    def _process_dict(cls, data: Dict[str, Any], client: "Snake") -> Dict[str, Any]:
        creator_dict = data.pop("user", None)
        data["creator_id"] = client.cache.place_user_data(creator_dict).id if creator_dict else None

        if "roles" in data:
            data["role_ids"] = data.pop("roles")

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any], client: "Snake") -> "CustomEmoji":
        data = cls._process_dict(data, client)
        return cls(client=client, **cls._filter_kwargs(data, cls._get_init_keys()))

    @property
    def creator(self) -> Optional[Union[CacheProxy, Awaitable["User"], "User"]]:
        """User that made this emoji."""
        if self._creator_id:
            return CacheProxy(id=self._creator_id, method=self._client.cache.get_user)

    @property
    def roles(self) -> Union[CacheProxy, Awaitable["Role"], "Role"]:
        """Roles allowed to use this emoji"""
        return CacheView(id=self._role_ids, method=self._client.cache.get_role)

    @property
    def guild(self) -> Union[CacheProxy, Awaitable["Guild"], "Guild"]:
        """The guild that this custom emoji is created in."""
        return CacheProxy(id=self._guild_id, method=self._client.cache.get_guild)

    @property
    def is_usable(self) -> bool:
        """
        Determines if this emoji is usable by the current user.
        """
        if not self.available:
            return False
        # todo: check roles
        return True

    async def edit(
        self,
        name: Optional[str] = None,
        roles: Optional[List[Union["Snowflake_Type", "Role"]]] = None,
        reason: Optional[str] = None,
    ) -> "CustomEmoji":
        """
        Modify the custom emoji information.

        parameters:
            name: The name of the emoji.
            roles: The roles allowed to use this emoji.
            reason: Attach a reason to this action, used for audit logs.

        returns:
            The newly modified custom emoji.
        """
        data_payload = dict_filter_none(
            dict(
                name=name,
                roles=roles,
            )
        )

        updated_data = await self._client.http.modify_guild_emoji(data_payload, self._guild_id, self.id, reason=reason)
        self.update_from_dict(updated_data)
        return self

    async def delete(self, reason: Optional[str] = None) -> None:
        """
        Deletes the custom emoji from the guild.

        parameters:
            reason: Attach a reason to this action, used for audit logs.
        """
        if not self._guild_id:
            raise ValueError("Cannot delete emoji, no guild id set.")

        await self._client.http.delete_guild_emoji(self._guild_id, self.id, reason=reason)


def process_emoji_req_format(emoji: Optional[Union[Emoji, dict, str]]) -> Optional[str]:
    if not emoji:
        return emoji

    if isinstance(emoji, str):
        return emoji

    if isinstance(emoji, dict):
        emoji = Emoji.from_dict(emoji)

    if isinstance(emoji, Emoji):
        return emoji.req_format

    raise ValueError(f"Invalid emoji: {emoji}")


def process_emoji(emoji: Optional[Union[Emoji, dict, str]]) -> Optional[dict]:
    if not emoji:
        return emoji

    if isinstance(emoji, dict):
        return emoji

    if isinstance(emoji, str):
        emoji = Emoji.unicode(emoji)

    if isinstance(emoji, Emoji):
        return emoji.to_dict()

    raise ValueError(f"Invalid emoji: {emoji}")
