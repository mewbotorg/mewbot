#!/usr/bin/env python3

"""
Contains all the input events which could be produced by a reddit client.
"""

from typing import Optional

import dataclasses

import asyncpraw  # type: ignore

from mewbot.api.v1 import InputEvent


@dataclasses.dataclass
class RedditInputEvent(InputEvent):
    """
    Base class for all reddit input events.
    """


# -------------
# - SUBMISSIONS

# There seems to be a little divergence as to what things are called
# Many people call an entry in a subreddit a "post"
# PRAW calls them "submissions" - so going with that
# These are intended for the subreddit input class
# Which watches subreddits and notifies the user when submissions or posts are made into them


@dataclasses.dataclass
class SubRedditSubmissionInputEvent(RedditInputEvent):

    submission: asyncpraw.reddit.Submission

    subreddit: str  # Which subreddit is the post in?

    submission_title: str  # Title of the post in the subreddit
    submission_id: str  # id number for the string
    submission_content: str  # String contents
    submission_image: Optional[str]  # A URL to the image associated with the post
    # (if there is one)

    author_str: str  # Author string for the post - should serve as an id


@dataclasses.dataclass
class SubRedditSubmissionCreationInputEvent(SubRedditSubmissionInputEvent):
    """
    A post was created in a monitored subreddit.
    """

    creation_timestamp: str  # When the post was created


@dataclasses.dataclass
class SubRedditSubmissionEditInputEvent(SubRedditSubmissionInputEvent):
    """
    A post was edited in a monitored subreddit.
    """

    # the titles of reddit posts cannot be changed - neither can their author?
    pre_edit_submission: Optional[
        asyncpraw.reddit.Submission
    ]  # We might not be able to get hold of the pre-edit text

    edit_timestamp: str  # When the post was edited


@dataclasses.dataclass
class SubRedditSubmissionDeletedInputEvent(SubRedditSubmissionInputEvent):
    """
    A post was deleted in a monitored subreddit.
    """

    del_timestamp: str  # When was the post deleted


@dataclasses.dataclass
class SubRedditSubmissionRemovedInputEvent(SubRedditSubmissionInputEvent):
    """
    A post was removed in a monitored subreddit.
    """

    remove_timestamp: str  # When was the post removed


@dataclasses.dataclass
class SubRedditSubmissionPinnedInputEvent(SubRedditSubmissionInputEvent):
    """
    A post was pinned to the top of the subreddit.
    """

    pinned_timestamp: str


#
# -------
# ----------
# - COMMENTS


@dataclasses.dataclass
class SubRedditCommentInputEvent(RedditInputEvent):
    """
    A comment is made to a post in a subreddit.
    """

    comment: asyncpraw.reddit.Comment

    subreddit: str  # Which subreddit is the post in?

    parent_id: str  # Which comment is this comment attached to?

    author_str: str  # Author string for the post - should serve as an id

    top_level: bool  # Is the comment top level for the post, or is it a comment of a comment


@dataclasses.dataclass
class SubRedditCommentCreationInputEvent(SubRedditCommentInputEvent):
    """
    An  event involving a comment has occurred in a monitored subreddit.
    There are two types of InputEvent that can be generated from a comment
    - A change occurs involving a top level comment - one at the root of a subreddit
    - A comment is added/edited/deleted/removed to the comment forest of an existing submission.
    """

    creation_timestamp: str  # When the post was created


@dataclasses.dataclass
class SubRedditCommentEditInputEvent(SubRedditCommentInputEvent):
    """
    A top level post was modified in a monitored subreddit.
    """

    parent_id: str  # Which comment is this comment attached to

    # the titles of reddit posts cannot be changed - neither can their author?
    pre_edit_message: Optional[
        asyncpraw.reddit.Comment
    ]  # We might not be able to get hold of the pre-edit text

    edit_timestamp: str  # When the post was edited


@dataclasses.dataclass
class SubRedditCommentDeletedInputEvent(SubRedditCommentInputEvent):
    """
    A top level post was deleted in a monitored subreddit.
    """

    parent_id: str  # Which comment is this comment attached to

    del_timestamp: str  # When was the post deleted


@dataclasses.dataclass
class SubRedditCommentRemovedInputEvent(SubRedditCommentInputEvent):
    """
    A top level post was removed in a monitored subreddit.
    """

    parent_id: str  # Which comment is this comment attached to

    remove_timestamp: str  # When was the post removed?


#
# ----------
# -----------------------
# - USERS - IN SUBREDDITS
# These are intended to be produced by the subreddit input
# They are concerned with how users interact with the subreddit


@dataclasses.dataclass
class RedditUserInteractedWithSubredditInputEvent(RedditInputEvent):
    """
    A user interacted with a subreddit.
    This is intended for when you're watching a subreddit, rather than watching a user.
    Either
     - leaving
     - joining
     - being banned
    """

    user_id: str  # The name/id of a user who has interacted with the subreddit


@dataclasses.dataclass
class RedditUserJoinedSubredditInputEvent(RedditUserInteractedWithSubredditInputEvent):
    """
    A user has joined a monitored subreddit.
    """


@dataclasses.dataclass
class RedditUserLeftSubredditInputEvent(RedditUserInteractedWithSubredditInputEvent):
    """
    A user has left a monitored subreddit.
    """


@dataclasses.dataclass
class RedditUserBannedFromSubredditInputEvent(RedditUserInteractedWithSubredditInputEvent):
    """
    A user has been banned from a monitored subreddit.
    """


#
# -----------------------
# ---------------
# - USER FOCUSSED
# These are intended for the redditor input class
# Which watches redditor
# These events are for user focussed events - when the users make changes


@dataclasses.dataclass
class RedditUserInputEvent(RedditInputEvent):
    """
    Something has happened involving a reddit user that you watch.
    Please don't make it weird.
    """

    user_id: str  # The name/id of the user who has done a thing


# ------------------------------------------
#
# - USER MAKES A SUBMISSION - TO A SUBREDDIT


@dataclasses.dataclass
class RedditUserCreatedSubredditSubmissionInputEvent(
    RedditUserInputEvent, SubRedditSubmissionCreationInputEvent
):
    """
    A user that you follow has posted to a subreddit.
    This might, or might not, be a subreddit that your currently following.
    """


@dataclasses.dataclass
class RedditUserEditedSubredditSubmissionInputEvent(
    RedditUserInputEvent, SubRedditSubmissionEditInputEvent
):
    """
    A user has edited one of the submission.
    This might, or might not, be a subreddit that your currently following.
    """


@dataclasses.dataclass
class RedditUserDeletedSubredditSubmissionInputEvent(
    RedditUserInputEvent, SubRedditSubmissionDeletedInputEvent
):
    """
    A user that you follow has deleted one of their submissions.
    This might, or might not, be a subreddit that your currently following.
    """


@dataclasses.dataclass
class RedditUserRemovedSubredditSubmissionInputEvent(
    RedditUserInputEvent, SubRedditSubmissionRemovedInputEvent
):
    """
    A user that you follow has posted to a subreddit.
    This might, or might not, be a subreddit that your currently following.
    """


#
# ------------------------------------------
# ------------------------------
#
# - USE COMMENTS ON A SUBMISSION


@dataclasses.dataclass
class RedditUserCreatedCommentOnSubredditSubmissionInputEvent(
    RedditUserInputEvent, SubRedditCommentCreationInputEvent
):
    """
    A user that you follow has commented on a post (submission) in a subreddit.
    This might, or might not, be a subreddit that your currently following.
    """


@dataclasses.dataclass
class RedditUserEditedCommentOnSubredditSubmissionInputEvent(
    RedditUserInputEvent, SubRedditCommentEditInputEvent
):
    """
    A user that you follow has edited one of their comments on a post (submission).
    This might, or might not, be a subreddit that your currently following.
    """


@dataclasses.dataclass
class RedditUserDeletedCommentOnSubredditSubmissionInputEvent(
    RedditUserInputEvent, SubRedditCommentDeletedInputEvent
):
    """
    A user that you follow has had one of their comments deleted.
    This could have been done by the user - or it could have been done by a mod.
    This might, or might not, have happened in a subreddit that your currently following.
    """


@dataclasses.dataclass
class RedditUserRemovedCommentOnSubredditSubmissionInputEvent(
    RedditUserInputEvent, SubRedditCommentRemovedInputEvent
):
    """
    A user that you follow has had one of their comments removed.
    This could have been done by the user - or it could have been done by a mod.
    This might, or might not, have happened in a subreddit that your currently following.
    """


#
# ------------------------------


# ------------------------------------------
#
# - USER MAKES A SUBMISSION - TO THEIR PROFILE


@dataclasses.dataclass
class RedditUserCreatedProfileSubmissionInputEvent(
    RedditUserInputEvent, SubRedditSubmissionCreationInputEvent
):
    """
    A user that you follow has posted to a subreddit.
    This might, or might not, be a subreddit that your currently following.
    """


@dataclasses.dataclass
class RedditUserEditProfileSubmissionInputEvent(
    RedditUserInputEvent, SubRedditSubmissionEditInputEvent
):
    """
    A user has edited one of the submission.
    This might, or might not, be a subreddit that your currently following.
    """


@dataclasses.dataclass
class RedditUserDeletedProfileSubmissionInputEvent(
    RedditUserInputEvent, SubRedditSubmissionDeletedInputEvent
):
    """
    A user that you follow has deleted one of their submissions.
    This might, or might not, be a subreddit that your currently following.
    """


@dataclasses.dataclass
class RedditUserRemovedProfileSubmissionInputEvent(
    RedditUserInputEvent, SubRedditSubmissionRemovedInputEvent
):
    """
    A user that you follow has posted to a subreddit.
    This might, or might not, be a subreddit that your currently following.
    """


#
# ------------------------------------------
# ------------------------------
#
# - USE COMMENTS ON A SUBMISSION IN THEIR PROFILE


@dataclasses.dataclass
class RedditUserCreatedCommentOnProfileSubmissionInputEvent(
    RedditUserInputEvent, SubRedditCommentCreationInputEvent
):
    """
    A user that you follow has commented on a post (submission) in a subreddit.
    This might, or might not, be a subreddit that your currently following.
    """


@dataclasses.dataclass
class RedditUserEditedCommentOnProfileSubmissionInputEvent(
    RedditUserInputEvent, SubRedditCommentEditInputEvent
):
    """
    A user that you follow has edited one of their comments on a post (submission).
    This might, or might not, be a subreddit that your currently following.
    """


@dataclasses.dataclass
class RedditUserDeletedCommentOnProfileSubmissionInputEvent(
    RedditUserInputEvent, SubRedditCommentDeletedInputEvent
):
    """
    A user that you follow has had one of their comments deleted.
    This could have been done by the user - or it could have been done by a mod.
    This might, or might not, have happened in a subreddit that your currently following.
    """


@dataclasses.dataclass
class RedditUserRemovedCommentOnProfileSubmissionInputEvent(
    RedditUserInputEvent, SubRedditCommentRemovedInputEvent
):
    """
    A user that you follow has had one of their comments removed from their profile.
    This could have been done by the user - or it could have been done by a mod.
    This might, or might not, have happened in a subreddit that your currently following.
    """


#
# ------------------------------
#
# ---------------


# --------------------
# - UPVVOTES/DOWNVOTES


@dataclasses.dataclass
class RedditVoteInputEvent(RedditInputEvent):
    """
    There are a number of ways to gie kudos.
    This is the base class for all of them.
    """

    positive: bool  # Did the user add or remove Kudos from you?
    user_id: str  # Who-ever was responsible for the vote event


@dataclasses.dataclass
class RedditPersonaVoteInputEvent(RedditVoteInputEvent):
    """
    Your bio has been upvoted or downvoted
    """


@dataclasses.dataclass
class RedditPostVoteInputEvent(RedditVoteInputEvent):
    """
    A post, made by you, has been upvoted or downvoted.
    """


#
# --------------------
