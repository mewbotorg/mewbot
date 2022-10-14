#!/usr/bin/env python3

from typing import Tuple, Type, Dict

from mewbot.api.v1 import IOConfig, Input, InputEvent
from mewbot.plugins.hook_specs import mewbot_ext_hook_impl

from .io_configs.reddit_password_io import RedditPasswordIO
from .io_configs import RedditSubredditInput, RedditRedditorInput
from .input_events import (
    # subreddit first events
    # - a submission has been manipulated in a subreddit
    SubRedditSubmissionCreationInputEvent,
    SubRedditSubmissionEditInputEvent,
    SubRedditSubmissionDeletedInputEvent,
    SubRedditSubmissionRemovedInputEvent,
    SubRedditSubmissionPinnedInputEvent,  # Todo: Implement this
    # - a comment has been manipulated in the subreddit
    SubRedditCommentCreationInputEvent,
    SubRedditCommentEditInputEvent,
    SubRedditCommentDeletedInputEvent,
    SubRedditCommentRemovedInputEvent,
    # - a user has interacted with the subreddit
    RedditUserJoinedSubredditInputEvent,
    RedditUserLeftSubredditInputEvent,
    RedditUserBannedFromSubredditInputEvent,
    # user first events
    # - a user has manipulated a submission in a subreddit
    RedditUserCreatedSubredditSubmissionInputEvent,
    RedditUserEditedSubredditSubmissionInputEvent,
    RedditUserDeletedSubredditSubmissionInputEvent,
    RedditUserRemovedSubredditSubmissionInputEvent,
    # - a user has manipulated a comment in a subreddit
    RedditUserCreatedCommentOnSubredditSubmissionInputEvent,
    RedditUserEditedCommentOnSubredditSubmissionInputEvent,
    RedditUserDeletedCommentOnSubredditSubmissionInputEvent,
    RedditUserRemovedCommentOnSubredditSubmissionInputEvent,
    # - a user has manipulated a submission in their profile
    RedditUserCreatedProfileSubmissionInputEvent,
    RedditUserEditProfileSubmissionInputEvent,
    RedditUserDeletedProfileSubmissionInputEvent,
    RedditUserRemovedProfileSubmissionInputEvent,
    # - a user has manipulated a comment in their profile
    RedditUserCreatedCommentOnProfileSubmissionInputEvent,
    RedditUserEditedCommentOnProfileSubmissionInputEvent,
    RedditUserDeletedCommentOnProfileSubmissionInputEvent,
    RedditUserRemovedCommentOnProfileSubmissionInputEvent,
    # - Not entirely sure how to implement this
    RedditPersonaVoteInputEvent,
    RedditPostVoteInputEvent,
)

# This is the name which will actually show up in the plugin manager.
# Note - this also allows you to extend an existing plugin - just set the name
# of your new plugin to the same as the one you wish to extend.
#
__mewbot_plugin_name__ = "reddit"


@mewbot_ext_hook_impl  # type: ignore
def get_io_config_classes() -> Dict[str, Tuple[Type[IOConfig], ...]]:
    """
    Return the IOConfigs defined by this plugin module.
    Note - IOConfig needs to be extended with YAML signature info - though this can also
    be generated from properties.
    :return:
    """
    return {__mewbot_plugin_name__: tuple(
        [
            RedditPasswordIO,
        ]
    )
    }


@mewbot_ext_hook_impl  # type: ignore
def get_input_classes() -> Dict[str, Tuple[Type[Input], ...]]:
    """
    Returns the Input classes defined by this plugin.
    In this case, there are two.
    :return:
    """
    return {__mewbot_plugin_name__: tuple([RedditSubredditInput, RedditRedditorInput])}


@mewbot_ext_hook_impl
def get_input_event_classes() -> Dict[str, Tuple[Type[InputEvent], ...]]:
    """
    Returns all the InputEvent subclasses defined by this plugin.
    :return:
    """
    return {__mewbot_plugin_name__: tuple([
        # subreddit first events
        # - a submission has been manipulated in a subreddit
        SubRedditSubmissionCreationInputEvent,
        SubRedditSubmissionEditInputEvent,
        SubRedditSubmissionDeletedInputEvent,
        SubRedditSubmissionRemovedInputEvent,
        SubRedditSubmissionPinnedInputEvent,  # Todo: Implement this
        # - a comment has been manipulated in the subreddit
        SubRedditCommentCreationInputEvent,
        SubRedditCommentEditInputEvent,
        SubRedditCommentDeletedInputEvent,
        SubRedditCommentRemovedInputEvent,
        # - a user has interacted with the subreddit
        RedditUserJoinedSubredditInputEvent,
        RedditUserLeftSubredditInputEvent,
        RedditUserBannedFromSubredditInputEvent,
        # user first events
        # - a user has manipulated a submission in a subreddit
        RedditUserCreatedSubredditSubmissionInputEvent,
        RedditUserEditedSubredditSubmissionInputEvent,
        RedditUserDeletedSubredditSubmissionInputEvent,
        RedditUserRemovedSubredditSubmissionInputEvent,
        # - a user has manipulated a comment in a subreddit
        RedditUserCreatedCommentOnSubredditSubmissionInputEvent,
        RedditUserEditedCommentOnSubredditSubmissionInputEvent,
        RedditUserDeletedCommentOnSubredditSubmissionInputEvent,
        RedditUserRemovedCommentOnSubredditSubmissionInputEvent,
        # - a user has manipulated a submission in their profile
        RedditUserCreatedProfileSubmissionInputEvent,
        RedditUserEditProfileSubmissionInputEvent,
        RedditUserDeletedProfileSubmissionInputEvent,
        RedditUserRemovedProfileSubmissionInputEvent,
        # - a user has manipulated a comment in their profile
        RedditUserCreatedCommentOnProfileSubmissionInputEvent,
        RedditUserEditedCommentOnProfileSubmissionInputEvent,
        RedditUserDeletedCommentOnProfileSubmissionInputEvent,
        RedditUserRemovedCommentOnProfileSubmissionInputEvent,
        # - Not entirely sure how to implement this
        RedditPersonaVoteInputEvent,
        RedditPostVoteInputEvent,
    ])}
