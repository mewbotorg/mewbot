import dataclasses


@dataclasses.dataclass
class RedditCredentials:
    """
    Base class for credential storage for reddit.
    Contains the common properties.
    """

    user_agent: str  # A description of your bot
    redirect_uri: str


@dataclasses.dataclass
class RedditBotCredentials(RedditCredentials):
    """
    Storage for all the credentials a script based app needs to connect to reddit.
    """

    client_id: str
    client_secret: str


@dataclasses.dataclass
class RedditSelfCredentials(RedditCredentials):
    """
    Storage for all the credentials a user needs to connect to reddit using their name.
    """

    username: str
    password: str


@dataclasses.dataclass
class RedditPasswordCredentials(RedditSelfCredentials, RedditBotCredentials):
    """
    Some login modes seem to require both types of credentials.
    """
