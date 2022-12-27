#!/usr/bin/env python3

from typing import Sequence

import asyncpraw  # type: ignore

from mewbot.api.v1 import Output

from ..io_configs import RedditIOBase
from .credentials import RedditSelfCredentials


class RedditSelfIO(RedditIOBase):
    """
    Allows mewbot to connect to Reddit using a user's credentials.
    Self bots may not be fully supported and may not present all facets of the API.
    """

    self_credentials: RedditSelfCredentials = RedditSelfCredentials(
        username="Probably not an actual username",
        password="Not a real password",
        redirect_uri="http://localhost:8080",
        user_agent="testscript by some guy",
    )

    @property
    def username(self) -> str:
        """
        Get the username being used to connected to reddit.
        :return:
        """
        return self.self_credentials.username

    @username.setter
    def username(self, value: str) -> None:
        """
        Set the value of the username used to connect to reddit.
        :param value:
        :return:
        """
        self.self_credentials.username = value

    @property
    def password(self) -> str:
        """
        Get the password you use to connect to reddit.
        :return:
        """
        return self.self_credentials.password

    @password.setter
    def password(self, value: str) -> None:
        """
        Set the password used to connect to reddit.
        :param value:
        :return:
        """
        self.self_credentials.password = value

    @property
    def user_agent(self) -> str:
        """
        Get the user_agent used to connect to reddit.
        :return:
        """
        return self.self_credentials.user_agent

    @user_agent.setter
    def user_agent(self, value: str) -> None:
        """
        Set the user agent you're using to connect to reddit
        :param value:
        :return:
        """
        self.self_credentials.user_agent = value

    def complete_authorization_flow(self) -> None:
        """
        Login to reddit using bot credentials.
        :return:
        """
        reddit = asyncpraw.Reddit(
            username=self.self_credentials.username,
            password=self.self_credentials.password,
            redirect_uri=self.self_credentials.redirect_uri,
            user_agent=self.self_credentials.user_agent,
        )
        print(reddit.auth.url(["identity"], "...", "permanent"))

    def get_outputs(self) -> Sequence[Output]:
        """
        At the moment, this class does not support outputs.
        :return:
        """
        return []
