from typing import TYPE_CHECKING, List, Optional

import attr
from dis_snek.models.discord import DiscordObject
from dis_snek.models.enums import ApplicationFlags

if TYPE_CHECKING:
    from dis_snek.models.discord_objects.team import Team
    from dis_snek.models.discord_objects.user import User
    from dis_snek.models.snowflake import Snowflake_Type


@attr.s(slots=True, kw_only=True)
class Application(DiscordObject):
    """
    Represents a discord application.
    Attributes:
        name str: The name of the application.
        icon str: The icon of the application
        description str: The description of the application
        rpc_origins List[str]: an array of rpc origin urls, if rpc is enabled
        bot_public bool: when false only app owner can join the app's bot to guilds
        bot_require_code_grant bool: when true the app's bot will only join upon completion of the full oauth2 code grant flow
        terms_of_service_url str: the url of the app's terms of service
        privacy_policy_url str: the url of the app's privacy policy
        owner [User][dis_snek.models.discord_objects.user.BaseUser] : partial user object containing info on the owner of the application
        summary str: if this application is a game sold on Discord, this field will be the summary field for the store page of its primary sku
        verify_key str: the hex encoded key for verification in interactions and the GameSDK's GetTicket
        team Team: if the application belongs to a team, this will be a list of the members of that team
        guild_id Snowflake_Type: if this application is a game sold on Discord, this field will be the guild to which it has been linked
        primary_sku_id Snowflake_Type: if this application is a game sold on Discord, this field will be the id of the "Game SKU" that is created, if exists
        slug str: if this application is a game sold on Discord, this field will be the URL slug that links to the store page
        cover_image str: the application's default rich presence invite cover image hash
        flags int: the application's public flags
    """

    name: str = attr.ib()
    icon: Optional[str] = attr.ib(default=None)
    description: Optional[str] = attr.ib()
    rpc_origins: Optional[List[str]] = attr.ib(default=None)
    bot_public: bool = attr.ib(default=True)
    bot_require_code_grant: bool = attr.ib(default=False)
    terms_of_service_url: Optional[str] = attr.ib(default=None)
    privacy_policy_url: Optional[str] = attr.ib(default=None)
    owner: Optional["User"] = attr.ib(default=None)
    summary: str = attr.ib()
    verify_key: str = attr.ib()
    team: Optional["Team"] = attr.ib(default=None)
    guild_id: Optional["Snowflake_Type"] = attr.ib(default=None)
    primary_sku_id: Optional["Snowflake_Type"] = attr.ib(default=None)
    slug: Optional[str] = attr.ib(default=None)
    cover_image: Optional[str] = attr.ib(default=None)
    flags: Optional["ApplicationFlags"] = attr.ib(default=None, converter=ApplicationFlags)
