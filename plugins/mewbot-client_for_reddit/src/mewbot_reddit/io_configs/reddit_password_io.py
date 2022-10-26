#!/usr/bin/env python3

from typing import List

import logging

import asyncpraw  # type: ignore

from ..io_configs import RedditIOBase
from .credentials import RedditPasswordCredentials


class RedditPasswordIO(RedditIOBase):
    """
    Allows mewbot to connect to Reddit using a user's credentials along with a bots.
    If you do not want to provide user credential (in plain text in a YAML file) then use
    the RedditBotIO config - where a browser will be opened and you will be prompted to
    authenticate into reddit.
    """

    # Credentials to store all the info needed to log into reddit
    hybrid_credentials: RedditPasswordCredentials = RedditPasswordCredentials(
        username="Probably not an actual username",
        password="Not a real password",
        client_id="SI8pN3DSbt0zor",
        client_secret="xaxkj7HNh8kwg8e5t4m6KvSrbTI",
        redirect_uri="http://localhost:8080",
        user_agent="testscript by some guy",
    )

    _subreddits: List[str]

    _logger: logging.Logger

    def __init__(self) -> None:

        super().__init__()

        self._logger = logging.getLogger(__name__ + ":" + type(self).__name__)

    # This mode requires quite a lot of info from the user
    @property
    def client_id(self) -> str:
        """
        Get the id of your bot within reddit.
        :return:
        """
        return self.hybrid_credentials.client_id

    @client_id.setter
    def client_id(self, value: str) -> None:
        """
        Set the id of your bot
        :param value:
        :return:
        """
        self.hybrid_credentials.client_id = value

    @property
    def client_secret(self) -> str:
        """
        Get the client secret
        :return:
        """
        return self.hybrid_credentials.client_secret

    @client_secret.setter
    def client_secret(self, value: str) -> None:
        """
        Set the client secret.
        :param value:
        :return:
        """
        self.hybrid_credentials.client_secret = value

    @property
    def user_agent(self) -> str:
        """
        Get the user_agent used to connect to reddit.
        :return:
        """
        return self.hybrid_credentials.user_agent

    @user_agent.setter
    def user_agent(self, value: str) -> None:
        """
        Set the user agent you're using to connect to reddit
        :param value:
        :return:
        """
        self.hybrid_credentials.user_agent = value

    @property
    def username(self) -> str:
        """
        Get the username being used to connected to reddit.
        :return:
        """
        return self.hybrid_credentials.username

    @username.setter
    def username(self, value: str) -> None:
        """
        Set the value of the username used to connect to reddit.
        :param value:
        :return:
        """
        self.hybrid_credentials.username = value

    @property
    def password(self) -> str:
        """
        Get the password you use to connect to reddit.
        :return:
        """
        return self.hybrid_credentials.password

    @password.setter
    def password(self, value: str) -> None:
        """
        Set the password used to connect to reddit.
        :param value:
        :return:
        """
        self.hybrid_credentials.password = value

    def complete_authorization_flow(self) -> None:
        """
        Login to reddit using bot credentials.
        :return:
        """
        reddit = asyncpraw.Reddit(
            username=self.hybrid_credentials.username,
            password=self.hybrid_credentials.password,
            client_id=self.hybrid_credentials.client_id,
            client_secret=self.hybrid_credentials.client_secret,
            redirect_uri=self.hybrid_credentials.redirect_uri,
            user_agent=self.hybrid_credentials.user_agent,
        )
        self._logger.info(reddit.auth.url(["identity"], "...", "permanent"))

        self.praw_reddit = reddit
