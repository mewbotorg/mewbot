#!/usr/bin/env python3

from __future__ import annotations

from typing import Optional, Sequence, Union, Set, Type, List, SupportsInt, Dict

import asyncio
import dataclasses
import logging
import time

import asyncpraw  # type: ignore
import asyncprawcore

from mewbot.api.v1 import IOConfig, Input, Output, InputEvent, OutputEvent
from mewbot.core import InputQueue

from ..input_events import (
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


class RedditIOBase(IOConfig):
    """
    Base class for either a bot of self reddit client.
    Note - because of implementation details of how praw works under the hood, you cannot
    have more than one instance of praw active in one program at any one time.
    """

    _subreddit_input: Optional[RedditSubredditInput] = None
    _redditor_input: Optional[RedditRedditorInput] = None
    _output: Optional[RedditOutput] = None

    praw_reddit: asyncpraw.reddit

    _subreddits: List[str]
    _redditors: List[str]

    @property
    def subreddits(self) -> List[str]:
        """
        Return the subreddits being watched by the bot.
        :return:
        """
        return self._subreddits

    @subreddits.setter
    def subreddits(self, new_subreddits: List[str]) -> None:
        """
        Update the monitored subreddits.
        :param new_subreddits:
        :return:
        """
        if not isinstance(new_subreddits, list):
            raise AttributeError("Please provide a list of sites.")

        self._subreddits = new_subreddits

        if self._subreddit_input is not None:
            self._subreddit_input.subreddits = new_subreddits

    @property
    def redditors(self) -> List[str]:
        """
        Return the subreddits being watched by the bot.
        :return:
        """
        return self._redditors

    @redditors.setter
    def redditors(self, new_redditors: List[str]) -> None:
        """
        Update the monitored subreddits.
        :param new_redditors:
        :return:
        """
        if not isinstance(new_redditors, list):
            raise AttributeError("Please provide a list of sites.")

        self._redditors = new_redditors

        if self._redditor_input is not None:
            self._redditor_input.subreddits = new_redditors

    @staticmethod
    def enable_praw_logging() -> None:
        """
        Install log handlers for praw.
        :return:
        """
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        for logger_name in ("asyncpraw", "asyncprawcore"):
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)
            logger.addHandler(handler)

    def get_inputs(self) -> Sequence[Input]:
        """
        Return the inputs offered by the class.
        In this case , there are two
         - RedditSubredditInput - for watching subreddits
         - RedditUserInput - for watching users
        :return:
        """
        # Setup and store a praw_reddit instance
        # self.enable_praw_logging()
        self.complete_authorization_flow()

        inputs: List[Union[RedditSubredditInput, RedditRedditorInput]] = []
        if not self._subreddit_input:
            self._subreddit_input = RedditSubredditInput(
                praw_reddit=self.praw_reddit,
                subreddits=self._subreddits,
            )
            inputs.append(self._subreddit_input)
        if not self._redditor_input:
            self._redditor_input = RedditRedditorInput(
                praw_reddit=self.praw_reddit, redditors=self._redditors
            )
            inputs.append(self._redditor_input)

        return inputs

    def get_outputs(self) -> Sequence[Output]:
        """
        Return the reddit outputs - in this case
        :return:
        """
        if not self._output:
            self._output = RedditOutput()

        return [self._output]

    def complete_authorization_flow(self) -> None:
        """
        Login to reddit using bot credentials.
        Needs to happen slightly differently for all the different ways you can login to reddit.
        :return:
        """
        raise NotImplementedError("This should never be called directly")


@dataclasses.dataclass
class RedditState:
    """
    Contains cached comments and the state of the monitored subreddits.
    """

    target_subreddits: List[str]  # All the subreddits to be monitored by the bot
    started_subreddits: Set[str]  # The subreddits where monitoring has started

    target_redditors: List[str]  # All of the redditors to be monitored
    started_redditors: Set[str]  # The redditors where monitoring has started

    # To provide services related to edited/deleted/remove comments (such as "what was the contents of this
    # before the event") it's necessary to cache the contents of some messages against future need
    # Currently this is done with dicts - this will change later bcause it presents a sever memory leak

    # Keyed with the subreddit and valued with a set of the ids which have been seen
    seen_comments: Dict[str, Set[str]]
    # Keyed with the id of the comment (which should not change) and valued with the current val
    # of that comment. The idea being to retrieve the original value
    # Then update it with the new value
    # The size of this cache needs to be kept under control - as it stores every comment the system
    # sees
    seen_comment_contents: Dict[str, asyncpraw.Reddit.comment]
    # Used after an edit - in case we see the same comment multiple times
    # (the problem is some subreddits are composed of composites of other subreddits - so it might
    # well be that you see the same comment in multiple different subreddits.
    # The seen_comment_contents stores the CURRENT contents of the comment
    # So it will be updated the first time that an edit occurs
    # In order to have the old message contents available we need to cache it before it's overwritten
    # in seen_comment_contents hence
    # Keyed with the hash of a comment and valued with the value of the previous message of that hash
    previous_comment_map: Dict[str, asyncpraw.Reddit.comment]

    # Likewise we have submissions
    seen_submissions: Dict[str, Set[str]]
    seen_submission_contents: Dict[str, asyncpraw.Reddit.submission]
    previous_submission_map: Dict[str, asyncpraw.Reddit.submission]


class RedditSubredditInput(Input):
    """
    Receives input from reddit.
    In particular, watches for events generated by a monitored list of subreddits.
    """

    _loop: Union[None, asyncio.events.AbstractEventLoop]
    _logger: logging.Logger

    praw_reddit: asyncpraw.Reddit

    reddit_state: RedditState

    def __init__(
        self,
        praw_reddit: asyncpraw.Reddit,
        subreddits: List[str],
        override_logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        :param praw_reddit: There can only be one asyncpraw instance - so it needs to be
                            passed in
        :param subreddits: The subreddits to monitor
        """

        super().__init__()

        self.praw_reddit = praw_reddit

        self.reddit_state = RedditState(
            target_subreddits=subreddits,
            started_subreddits=set(),
            target_redditors=[],
            started_redditors=set(),
            seen_comments=dict(),
            seen_comment_contents=dict(),
            previous_comment_map=dict(),
            seen_submissions=dict(),
            seen_submission_contents=dict(),
            previous_submission_map=dict(),
        )

        self._logger = (
            logging.getLogger(__name__ + ":" + type(self).__name__)
            if override_logger is None
            else override_logger
        )
        self._logger.info("Monitoring subreddits - %s", self.reddit_state.target_subreddits)

        self._loop = None

    @staticmethod
    def produces_inputs() -> Set[Type[InputEvent]]:
        """
        Depending on the setup, this input could produce any of the below.
        This method produces subreddit specific input events - events which could be best
        gathered by watching a subreddit.
        :return:
        """
        return {
            SubRedditSubmissionCreationInputEvent,
            SubRedditSubmissionEditInputEvent,
            SubRedditSubmissionDeletedInputEvent,
            SubRedditSubmissionRemovedInputEvent,
            SubRedditSubmissionPinnedInputEvent,
            SubRedditCommentCreationInputEvent,
            SubRedditCommentEditInputEvent,
            SubRedditCommentDeletedInputEvent,
            SubRedditCommentRemovedInputEvent,
            RedditUserJoinedSubredditInputEvent,
            RedditUserLeftSubredditInputEvent,
            RedditUserBannedFromSubredditInputEvent,
        }

    @property
    def subreddits(self) -> List[str]:
        """
        :return:
        """
        return self.reddit_state.target_subreddits

    @subreddits.setter
    def subreddits(self, values: List[str]) -> None:
        """
        Update the subreddits.
        :param values:
        :return:
        """
        self.reddit_state.target_subreddits = values

    @property
    def loop(self) -> asyncio.events.AbstractEventLoop:
        """
        Gets the current event loop.
        :return:
        """
        if self._loop is not None:
            return self._loop
        self._loop = asyncio.get_running_loop()
        return self._loop

    async def run(self, profiles: bool = False) -> None:
        """
        Start polling Reddit.
        :param profiles: Are the subreddits being monitored _actually_ redditor profiles.
                         (Currently this only affects the logging message)
        :return:
        """
        me = await self.praw_reddit.user.me()

        if not profiles:
            self._logger.info(
                "About to start watching Reddit - subreddits '%s' will be watched  - logged in as %s",
                self.reddit_state.target_subreddits,
                me,
            )
        else:
            self._logger.info(
                "About to start watching Reddit - redditors profiles '%s' will be watched  - logged in as %s",
                self.reddit_state.target_subreddits,
                me,
            )

        for subreddit in self.reddit_state.target_subreddits:
            self.loop.create_task(self.monitor_subreddit_comments(subreddit))
            self.loop.create_task(self.monitor_subreddit_submissions(subreddit))

            self.reddit_state.started_subreddits.add(subreddit)

    # ----------------
    # MONITOR COMMENTS

    async def monitor_subreddit_comments(self, target_subreddit: str) -> None:
        """
        Monitor a subreddit for comments and put them on the wire.
        :param target_subreddit:
        :return:
        """
        self._logger.info(
            "Monitoring subreddit '%s' for comments",
            target_subreddit,
        )

        multireddit = await self.praw_reddit.subreddit(target_subreddit, fetch=True)

        # async-praw offers a comment stream - so processing comments as they come off the stream
        async for comment in multireddit.stream.comments():
            print("-------------")
            print(self.render_comment(comment))
            print("-------------")
            await self.subreddit_comment_to_event(
                subreddit=target_subreddit, reddit_comment=comment
            )

    @staticmethod
    def render_comment(
        reddit_comment: asyncpraw.reddit.Comment, prefix: str = "subreddit"
    ) -> str:
        """
        Produce a human-readable version of a reddit comment.
        :param reddit_comment:
        :param prefix: The prefix for all the printed info lines
        :return:
        """
        comment_contents = [
            f"{prefix}_comment.id: {reddit_comment.id}",
            f"{prefix}_comment.author: {reddit_comment.author}",
            f"{prefix}_comment.body: {reddit_comment.body}",
            f"{prefix}_comment.created_utc: {reddit_comment.created_utc}",
            f"{prefix}_comment.distinguished: {reddit_comment.distinguished}",
            f"{prefix}_comment.edited: {reddit_comment.edited}",
            f"{prefix}_comment.is_submitter: {reddit_comment.is_submitter}",
            f"{prefix}_comment.subreddit_id: {reddit_comment.subreddit_id}",
        ]
        return "\n".join(comment_contents)

    # Todo: RSS comments can be edited. Would be good to implement edit detection there as well
    @staticmethod
    def hash_comment(reddit_comment: asyncpraw.reddit.Comment) -> str:
        """
        Take a comment and return a hash for it.
        This is pretty simple - just a str of a tuple of the comment_id and contents
        :param reddit_comment:
        :return:
        """
        return str((reddit_comment.id, reddit_comment.body))

    def is_comment_top_level(self, reddit_comment: praw_reddit.comment) -> bool:
        """
        Return True if a comment is top level and False otherwise.
        :param reddit_comment:
        :return:
        """
        # Parse the parent_id to determine the type of comment this is
        comment_parent_id = reddit_comment.parent_id

        # Comment is definitely attached to another comment - so note it as such in the event
        if comment_parent_id.startswith("t1_"):
            top_level = False
        # Comment has the submission id of a parent as a post - so it's definitely top level
        elif comment_parent_id.startswith("t3_"):
            top_level = True
        else:
            # This should never happen
            self._logger.info(
                "Unexpected case when trying to comment_parent_id - %s", comment_parent_id
            )
            top_level = False

        return top_level

    async def subreddit_comment_to_event(
        self, subreddit: str, reddit_comment: praw_reddit.comment
    ) -> None:
        """
        Takes a comment posted in a subreddit and puts it on the wire as an event.
        :param subreddit: The declared subreddit we are polling from
                          (There may be multi-subreddit or composite subreddit shennanigans going on -
                          so just declaring the subreddit mewbot _thinks_ it's drawing from)
        :param reddit_comment:
        :return:
        """
        top_level = self.is_comment_top_level(reddit_comment)

        # "Detect" removed or deleted comments - a poor method, but the best that can be done atm
        # Note - there may be issues where this does not work for non-english language subreddits
        if reddit_comment.body == r"[removed]":

            # Per notes in reddit-dev-notes.md
            # Not sure if removed events are being broadcast by the API
            if reddit_comment.author == r"[deleted]":

                await self.process_subreddit_removed_comment_on_submission(
                    subreddit, reddit_comment, top_level=top_level
                )

                return

        if reddit_comment.body == r"[deleted]":

            await self.process_subreddit_deleted_comment_on_submission(
                subreddit, reddit_comment, top_level
            )

            return

        # Not sure if editing a comment produces a separate event in this result
        # Or if it just happens to change the status of the observed event to edited
        # Given this is intended to be the backend for a _display_ system - it probably
        # DOES NOT produce a separate event

        # Note - depending on the cache size events will start falling out of it
        # So it's fairly certain that we won't be able to provide the pre-edit content

        # If a comment has been edited, then it needs to go on the wire as an edited event
        if reddit_comment.edited:

            await self.process_subreddit_edited_comment_on_submission(
                subreddit, reddit_comment, top_level
            )

            return

        # If a message is not declared as edited, deleted or removed, just put it on the wire
        await self.process_subreddit_created_comment_on_submission(
            subreddit, reddit_comment, top_level
        )

    async def process_subreddit_created_comment_on_submission(
        self, subreddit: str, reddit_comment: asyncpraw.reddit.Comment, top_level: bool
    ) -> None:
        """
        Subreddit first.
        A comment has been created in a monitored subreddit - either on a submission directly
        :param subreddit:
        :param reddit_comment:
        :param top_level:
        :return:
        """
        comment_creation_input_event = SubRedditCommentCreationInputEvent(
            comment=reddit_comment,
            subreddit=subreddit,
            parent_id=reddit_comment.parent_id,
            author_str=str(reddit_comment.author),
            top_level=top_level,
            creation_timestamp=reddit_comment.created_utc,
        )

        await self.send(comment_creation_input_event)

    async def process_subreddit_edited_comment_on_submission(
        self, subreddit: str, reddit_comment: asyncpraw.reddit.Comment, top_level: bool
    ) -> None:
        """
        Subreddit first.
        A comment has been edited in a monitored subreddit.
        :param subreddit:
        :param reddit_comment:
        :param top_level:
        :return:
        """
        message_id = reddit_comment.id

        # Check if we have an existing old message to assign to this message
        message_hash = self.hash_comment(reddit_comment)
        if message_hash in self.reddit_state.previous_comment_map:
            old_message = self.reddit_state.previous_comment_map[message_hash]
        else:
            old_message = self.reddit_state.seen_comment_contents.get(message_id, None)

        comment_edit_input_event = SubRedditCommentEditInputEvent(
            comment=reddit_comment,
            subreddit=subreddit,
            parent_id=reddit_comment.parent_id,
            author_str=str(reddit_comment.author),
            top_level=top_level,
            # If we have it in our internal cache
            pre_edit_message=old_message,
            # This may be the best we can do - as the message doesn't seem to have a "last edited"
            # or similar field
            edit_timestamp=str(time.time()),
        )
        await self.send(comment_edit_input_event)

        self.reddit_state.previous_comment_map[message_hash] = old_message
        # Store the current state of the message - in case it's edited again
        self.reddit_state.seen_comment_contents[message_id] = reddit_comment

    async def process_subreddit_deleted_comment_on_submission(
        self, subreddit: str, reddit_comment: asyncpraw.reddit.Comment, top_level: bool
    ) -> None:
        """
        Subreddit first.
        A comment has been deleted from a submission (on from somewhere in it's comment forest).
        :param subreddit:
        :param reddit_comment:
        :param top_level:
        :return:
        """
        # Check to see if we have an old message
        comment_hash = self.hash_comment(reddit_comment)
        old_reddit_message = self.reddit_state.previous_comment_map.get(comment_hash, None)

        # If we don't, try in the seen comments
        if old_reddit_message is None:
            old_reddit_message = self.reddit_state.seen_comment_contents[subreddit].get(
                reddit_comment.id, None
            )

        # Update the cache - if a message has been removed it should never change again
        self.reddit_state.previous_comment_map[comment_hash] = None
        # Indicate that the comment is gone by setting the contents to None
        self.reddit_state.seen_comment_contents[subreddit][reddit_comment.id] = None

        deleted_message_event = SubRedditCommentDeletedInputEvent(
            comment=reddit_comment,
            subreddit=reddit_comment.subreddit,
            author_str=old_reddit_message.author.id,
            top_level=top_level,
            del_timestamp=str(time.time()),
            parent_id=reddit_comment.parent_id,
        )
        await self.send(deleted_message_event)

    async def process_subreddit_removed_comment_on_submission(
        self, subreddit: str, reddit_comment: asyncpraw.reddit.Comment, top_level: bool
    ) -> None:
        """
        Subreddit first.
        A comment has been removed from a submission (on from somewhere in it's comment forest).
        :param subreddit:
        :param reddit_comment:
        :param top_level:
        :return:
        """

        # Check to see if we have an old message
        comment_hash = self.hash_comment(reddit_comment)
        old_reddit_message = self.reddit_state.previous_comment_map.get(comment_hash, None)

        # If we don't, try in the seen comments
        if old_reddit_message is None:
            old_reddit_message = self.reddit_state.seen_comment_contents[subreddit].get(
                reddit_comment.id, None
            )

        # Update the cache - if a message has been removed it should never change again
        self.reddit_state.previous_comment_map[comment_hash] = None
        # Indicate that the comment is gone by setting the contents to None
        self.reddit_state.seen_comment_contents[subreddit][reddit_comment.id] = None

        # Without the old message there is no good way to know who the author was
        old_author_str = (
            "" if old_reddit_message is None else str(old_reddit_message.author.id)
        )

        removed_message_event = SubRedditCommentRemovedInputEvent(
            comment=reddit_comment,
            subreddit=reddit_comment.subreddit,
            author_str=old_author_str,
            top_level=top_level,
            remove_timestamp=str(time.time()),
            parent_id=reddit_comment.parent_id,
        )

        await self.send(removed_message_event)

    # -------------------
    # MONITOR SUBMISSIONS

    async def monitor_subreddit_submissions(self, target_subreddit: str) -> None:
        """
        Monitor a subreddit for submissions and put them on the wire.
        :param target_subreddit:
        :return:
        """
        self._logger.info(
            "Monitoring subreddit '%s' for submissions",
            target_subreddit,
        )

        try:
            multireddit = await self.praw_reddit.subreddit(target_subreddit, fetch=True)
        except asyncprawcore.exceptions.NotFound:
            self._logger.info(
                "Subreddit could not be found - hence polling cannot start - '%s'",
                target_subreddit,
            )
            return

        # async-praw offers a comment stream - so processing comments as they come off the stream
        async for submission in multireddit.stream.submissions():
            print("-------------")
            print(self.render_submission(submission))
            print("-------------")
            await self.subreddit_submission_to_event(
                subreddit=target_subreddit, reddit_submission=submission
            )

    @staticmethod
    def render_submission(
        reddit_submission: asyncpraw.reddit.Submission, prefix: str = "subreddit"
    ) -> str:
        """
        Produce a human-readable version of a reddit submission.
        :param reddit_submission:
        :param prefix: To prepend to all the printed lines
        :return:
        """
        submission_contents = [
            f"{prefix}_submission.id: {reddit_submission.id}",
            f"{prefix}_submission.subreddit: {reddit_submission.subreddit}",
            f"{prefix}_submission.name: {reddit_submission.name}",
            f"{prefix}_submission.title: {reddit_submission.title}",
            f"{prefix}_submission.author: {reddit_submission.author}",
            f"{prefix}_submission.stickied: {reddit_submission.stickied}",
            f"{prefix}_submission.selftext: {reddit_submission.selftext}",
            f"{prefix}_submission.url: {reddit_submission.url}",
        ]
        return "\n".join(submission_contents)

    @staticmethod
    def hash_submission(submission_comment: asyncpraw.reddit.Submission) -> str:
        """
        Take a comment and return a hash for it.
        This is pretty simple - just a str of a tuple of the comment_id and contents
        :param submission_comment:
        :return:
        """
        return str(
            (submission_comment.id, submission_comment.selftext, submission_comment.author)
        )

    async def subreddit_submission_to_event(
        self, subreddit: str, reddit_submission: praw_reddit.submission
    ) -> None:
        """
        Takes a reddit comment and puts it on the wire as an event.
        :param subreddit: The declared subreddit we are polling from
                          (There may be multi-subreddit or composite subreddit shennanigans going on -
                          so just declaring the subreddit mewbot _thinks_ it's drawing from)
        :param reddit_submission:
        :return:
        """
        # "Detect" removed or deleted comments - a poor method, but the best that can be done atm
        # Note - there may be issues where this does not work for non-english language subreddits
        if reddit_submission.selftext == r"[removed]":

            # Per notes in reddit-dev-notes.md
            # Not sure if removed events are being broadcast by the API
            if reddit_submission.author == r"[deleted]":
                await self.process_subreddit_removed_submission(subreddit, reddit_submission)

                return

        if reddit_submission.selftext == r"[deleted]":

            await self.process_subreddit_deleted_submission(subreddit, reddit_submission)

            return

        # Not sure if editing a submission produces a separate event in this stream
        # Or if it just happens to change the status of the observed event to edited
        # Given this is intended to be the backend for a _display_ system - it probably
        # DOES NOT produce a separate event

        # Note - depending on the cache size events will start falling out of it
        # So it's fairly certain that we won't be able to provide the pre-edit content

        # If a submission has been edited, then it needs to go on the wire as an edited event
        if reddit_submission.edited:

            await self.process_subreddit_edited_submission(subreddit, reddit_submission)

            return

        # If a message is not declared as edited, deleted or removed, just put it on the wire
        await self.process_subreddit_created_submission(subreddit, reddit_submission)

    async def process_subreddit_created_submission(
        self, subreddit: str, reddit_submission: asyncpraw.reddit.Submission
    ) -> None:
        """
        A submission has been created in a monitored subreddit.
        :param subreddit:
        :param reddit_submission:
        :return:
        """
        submission_creation_input_event = SubRedditSubmissionCreationInputEvent(
            submission=reddit_submission,
            subreddit=subreddit,
            author_str=str(reddit_submission.author),
            creation_timestamp=reddit_submission.created_utc,
            submission_content=reddit_submission.selftext,
            submission_id=reddit_submission.id,
            submission_image=reddit_submission.url,
            submission_title=reddit_submission.title,
        )

        await self.send(submission_creation_input_event)

    async def process_subreddit_edited_submission(
        self, subreddit: str, reddit_submission: asyncpraw.reddit.Submission
    ) -> None:
        """
        A submission has been edited in a monitored subreddit.
        :param subreddit:
        :param reddit_submission:
        :return:
        """

        message_id = reddit_submission.id

        # Check if we have an existing old message to assign to this message
        message_hash = self.hash_submission(reddit_submission)
        if message_hash in self.reddit_state.previous_submission_map:
            old_message = self.reddit_state.previous_submission_map[message_hash]
        else:
            old_message = self.reddit_state.seen_submission_contents.get(message_id, None)

        submission_edit_input_event = SubRedditSubmissionEditInputEvent(
            submission=reddit_submission,
            author_str=str(reddit_submission.author),
            submission_image=None,
            submission_title=reddit_submission.title,
            # If we have it in our internal cache
            pre_edit_submission=old_message,
            # This may be the best we can do - as the message doesn't seem to have a "last edited"
            # or similar field
            edit_timestamp=str(time.time()),
            subreddit=subreddit,
            submission_content=reddit_submission.selftext,
            submission_id=reddit_submission.id,
        )
        await self.send(submission_edit_input_event)

        self.reddit_state.previous_submission_map[message_hash] = old_message
        # Store the current state of the message - in case it's edited again
        self.reddit_state.seen_submission_contents[message_id] = reddit_submission

    async def process_subreddit_deleted_submission(
        self, subreddit: str, reddit_submission: asyncpraw.reddit.Submission
    ) -> None:
        """
        A submission has been deleted in a monitored subreddit.
        :param subreddit:
        :param reddit_submission:
        :return:
        """

        # Check to see if we have an old message
        submission_hash = self.hash_submission(reddit_submission)
        old_reddit_submission = self.reddit_state.previous_submission_map.get(
            submission_hash, None
        )

        # If we don't, try in the seen submissions
        if old_reddit_submission is None:
            old_reddit_submission = self.reddit_state.seen_submission_contents[subreddit].get(
                reddit_submission.id, None
            )

        # Update the cache - if a message has been removed it should never change again
        self.reddit_state.previous_submission_map[submission_hash] = None
        # Indicate that the submission is gone by setting the contents to None
        self.reddit_state.seen_submission_contents[subreddit][reddit_submission.id] = None

        deleted_message_event = SubRedditSubmissionDeletedInputEvent(
            submission=reddit_submission,
            subreddit=reddit_submission.subreddit,
            submission_title=reddit_submission.title,
            author_str=old_reddit_submission.author.id,
            del_timestamp=str(time.time()),
            submission_content=reddit_submission.selftext,
            submission_id=reddit_submission.id,
            submission_image=None,
        )
        await self.send(deleted_message_event)

    async def process_subreddit_removed_submission(
        self, subreddit: str, reddit_submission: asyncpraw.reddit.Submission
    ) -> None:
        """
        A submission has been deleted in a monitored subreddit.
        :param subreddit:
        :param reddit_submission:
        :return:
        """

        # Check to see if we have an old message
        submission_hash = self.hash_submission(reddit_submission)
        old_reddit_submission = self.reddit_state.previous_submission_map.get(
            submission_hash, None
        )

        # If we don't, try in the seen submissions
        if old_reddit_submission is None:
            old_reddit_submission = self.reddit_state.seen_submission_contents[subreddit].get(
                reddit_submission.id, None
            )

        # Update the cache - if a message has been removed it should never change again
        self.reddit_state.previous_submission_map[submission_hash] = None
        # Indicate that the submission is gone by setting the contents to None
        self.reddit_state.seen_submission_contents[subreddit][reddit_submission.id] = None

        # Without the old message there is no good way to know who the author was
        old_author_str = (
            "" if old_reddit_submission is None else str(old_reddit_submission.author.id)
        )

        removed_message_event = SubRedditSubmissionRemovedInputEvent(
            submission_id=reddit_submission.id,
            submission_title=reddit_submission.title,
            submission=reddit_submission,
            subreddit=reddit_submission.subreddit,
            author_str=old_author_str,
            remove_timestamp=str(time.time()),
            submission_content=reddit_submission.selftext,
            submission_image=reddit_submission.url,  # Not very sure how this is stored - working on it
        )

        await self.send(removed_message_event)

    # -------------------

    async def send(self, reddit_input_event: InputEvent) -> None:
        """
        Put a created InputEvent on the wire.
        :param reddit_input_event:
        :return:
        """
        if self.queue is not None:
            await self.queue.put(reddit_input_event)


class RedditRedditorInput(RedditSubredditInput):
    """
    Receives input from reddit.
    In particular, watches for events generated by a monitored list of redditors.
    """

    def __init__(
        self, praw_reddit: asyncpraw.Reddit, redditors: Optional[List[str]] = None
    ) -> None:
        """
        :param praw_reddit: There can only be one asyncpraw instance so it needs to be
                            passed in
        :param redditors: A list of the redditors to watch. They might be up to something.
        """

        self._logger = logging.getLogger(__name__ + ":" + type(self).__name__)

        # The users profile seem to act like a subreddit.
        # Monitoring them using the existing subreddit monitor
        super().__init__(
            praw_reddit=praw_reddit, subreddits=self.get_redditor_profile_names(redditors)
        )

        self._logger.info("Monitoring redditors - %s", self.reddit_state.target_redditors)

        # Todo: This should probably be a common state between the two inputs
        self.reddit_state.target_redditors = redditors

        self.praw_reddit = praw_reddit

        self._loop = None

    @staticmethod
    def get_redditor_profile_names(redditors: List[str]) -> List[str]:
        """
        Profiles act like subreddits - but their name is "u_{redditor_name}".
        Take a list of redditors and output their profiles.
        :param redditors:
        :return:
        """
        return [f"u_{rn}" for rn in redditors]

    @staticmethod
    def produces_inputs() -> Set[Type[InputEvent]]:
        """
        Depending on the setup, this input could produce any of the above.
        This method produces redditor specific input events - events which could be best
        gathered by watching a reddit.
        :return:
        """
        return {
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
        }

    @property
    def subreddits(self) -> List[str]:
        """
        :return:
        """
        raise AttributeError("Subreddits cannot be directly got")

    @subreddits.setter
    def subreddits(self, values: List[str]) -> None:
        """
        Update the subreddits.
        :param values:
        :return:
        """
        raise AttributeError("Subreddits cannot be directly set")

    @property
    def redditors(self) -> List[str]:
        """
        :return:
        """
        raise self.reddit_state.target_redditors

    @redditors.setter
    def redditors(self, values: List[str]) -> None:
        """
        Update the subreddits.
        :param values:
        :return:
        """
        self.reddit_state.target_redditors = values

    async def run(self, profiles: bool = True) -> None:
        """
        Monitoring redditors
        :return:
        """
        # Todo: This will not be yielding the right type of events
        # Monitoring the redditor's profiles - which act like subreddits
        await super().run(profiles=profiles)

        for redditor in self.reddit_state.target_redditors:
            self.loop.create_task(self.monitor_redditor_comments(redditor))
            self.loop.create_task(self.monitor_redditor_submissions(redditor))

    # ----------------
    # MONITOR COMMENTS

    async def monitor_redditor_comments(self, target_redditor: str) -> None:
        """
        Monitor comments made by the target redditor.
        :param target_redditor:
        :return:
        """
        self.reddit_state.started_redditors.add(target_redditor)

        self._logger.info("Monitoring redditor '%s' for comments", target_redditor)

        redditor = await self.praw_reddit.redditor(name=target_redditor)

        async for comment in redditor.stream.comments():
            print("-------------")
            print(self.render_comment(comment, prefix="redditor"))
            print("-------------")
            await self.redditor_comment_to_event(redditor=redditor, reddit_comment=comment)

    async def redditor_comment_to_event(
        self, redditor: str, reddit_comment: asyncpraw.reddit.Comment
    ) -> None:
        """
        Takes a comment made by a redditor posting in a subreddit (or a profile) a puts it on the wire as an event.
        :param redditor:
        :param reddit_comment:
        :return:
        """
        top_level = self.is_comment_top_level(reddit_comment)

        # "Detect" removed or deleted comments - a poor method, but the best that can be done atm
        # Note - there may be issues where this does not work for non-english language subreddits
        if reddit_comment.body == r"[removed]":

            # Per notes in reddit-dev-notes.md
            # Not sure if removed events are being broadcast by the API
            if reddit_comment.author == r"[deleted]":
                await self.process_redditor_removed_comment_on_submission(
                    reddit_comment, top_level
                )
                return

        if reddit_comment.body == r"[deleted]":

            await self.process_redditor_deleted_comment_on_submission(
                reddit_comment, top_level
            )

            return

        # Not sure if editing a comment produces a separate event in this result
        # Or if it just happens to change the status of the observed event to edited
        # Given this is intended to be the backend for a _display_ system - it probably
        # DOES NOT produce a separate event

        # Note - depending on the cache size events will start falling out of it
        # So it's fairly certain that we won't be able to provide the pre-edit content

        # If a comment has been edited, then it needs to go on the wire as an edited event
        if reddit_comment.edited:

            await self.process_redditor_edited_comment_on_submission(
                reddit_comment, top_level
            )

            return

        # If a message is not declared as edited, deleted or removed, just put it on the wire
        await self.process_redditor_created_comment_on_submission(reddit_comment, top_level)

    async def process_redditor_created_comment_on_submission(
        self, reddit_comment: asyncpraw.reddit.Comment, top_level: bool
    ) -> None:
        """
        A redditor has been detected making a comment.
        :param reddit_comment:
        :param top_level:
        :return:
        """
        self.reddit_state.seen_comment_contents[reddit_comment.id] = reddit_comment

        # Todo: Should be some hash work here?
        comment_creation_input_event = SubRedditCommentCreationInputEvent(
            comment=reddit_comment,
            subreddit=reddit_comment.subreddit,
            parent_id=reddit_comment.parent_id,
            author_str=str(reddit_comment.author),
            top_level=top_level,
            creation_timestamp=reddit_comment.created_utc,
        )

        await self.send(comment_creation_input_event)

    async def process_redditor_edited_comment_on_submission(
        self, reddit_comment: asyncpraw.reddit.Comment, top_level: bool
    ) -> None:
        """
        Edits have been detected to a redditor's comment.
        :param reddit_comment:
        :param top_level:
        :return:
        """

        message_id = reddit_comment.id

        # Check if we have an existing old message to assign to this message
        message_hash = self.hash_comment(reddit_comment)
        if message_hash in self.reddit_state.previous_comment_map:
            old_message = self.reddit_state.previous_comment_map[message_hash]
        else:
            old_message = self.reddit_state.seen_comment_contents.get(message_id, None)

        comment_edit_input_event = SubRedditCommentEditInputEvent(
            comment=reddit_comment,
            subreddit=reddit_comment.subreddit,
            parent_id=reddit_comment.parent_id,
            author_str=str(reddit_comment.author),
            top_level=top_level,
            # If we have it in our internal cache
            pre_edit_message=old_message,
            # This may be the best we can do - as the message doesn't seem to have a "last edited"
            # or similar field
            edit_timestamp=str(time.time()),
        )
        await self.send(comment_edit_input_event)

        self.reddit_state.previous_comment_map[message_hash] = old_message
        # Store the current state of the message - in case it's edited again
        self.reddit_state.seen_comment_contents[message_id] = reddit_comment

    async def process_redditor_deleted_comment_on_submission(
        self, reddit_comment: asyncpraw.reddit.Comment, top_level: bool
    ) -> None:
        """
        A redditor comment has been processed as deleted.
        :param reddit_comment:
        :param top_level:
        :return:
        """

        # Check to see if we have an old message
        comment_hash = self.hash_comment(reddit_comment)
        old_reddit_message = self.reddit_state.previous_comment_map.get(comment_hash, None)

        # If we don't, try in the seen comments
        if old_reddit_message is None:
            old_reddit_message = self.reddit_state.seen_comment_contents[
                reddit_comment.subreddit
            ].get(reddit_comment.id, None)

        # Update the cache - if a message has been removed it should never change again
        self.reddit_state.previous_comment_map[comment_hash] = None
        # Indicate that the comment is gone by setting the contents to None
        self.reddit_state.seen_comment_contents[reddit_comment.subreddit][
            reddit_comment.id
        ] = None

        deleted_message_event = SubRedditCommentDeletedInputEvent(
            comment=reddit_comment,
            subreddit=reddit_comment.subreddit,
            author_str=old_reddit_message.author.id,
            top_level=top_level,
            del_timestamp=str(time.time()),
            parent_id=reddit_comment.parent_id,
        )
        await self.send(deleted_message_event)

    async def process_redditor_removed_comment_on_submission(
        self, reddit_comment: asyncpraw.reddit.Comment, top_level: bool
    ) -> None:
        """
        A redditor comment has been detected as removed.

        :param reddit_comment:
        :param top_level: Is the comment to be processed top level
        :return:
        """

        # Check to see if we have an old message
        comment_hash = self.hash_comment(reddit_comment)
        old_reddit_message = self.reddit_state.previous_comment_map.get(comment_hash, None)

        # If we don't, try in the seen comments
        if old_reddit_message is None:
            old_reddit_message = self.reddit_state.seen_comment_contents[
                reddit_comment.subreddit
            ].get(reddit_comment.id, None)

        # Update the cache - if a message has been removed it should never change again
        self.reddit_state.previous_comment_map[comment_hash] = None
        # Indicate that the comment is gone by setting the contents to None
        self.reddit_state.seen_comment_contents[reddit_comment.subreddit][
            reddit_comment.id
        ] = None

        # Without the old message there is no good way to know who the author was
        old_author_str = (
            "" if old_reddit_message is None else str(old_reddit_message.author.id)
        )

        removed_message_event = SubRedditCommentRemovedInputEvent(
            comment=reddit_comment,
            subreddit=reddit_comment.subreddit,
            author_str=old_author_str,
            top_level=top_level,
            remove_timestamp=str(time.time()),
            parent_id=reddit_comment.parent_id,
        )

        await self.send(removed_message_event)

    # ----------------
    # ---------------------
    # - MONITOR SUBMISSIONS

    async def monitor_redditor_submissions(self, target_redditor: str) -> None:
        """
        Monitor submission made by the target redditor.
        :param target_redditor:
        :return:
        """
        self.reddit_state.started_redditors.add(target_redditor)

        self._logger.info("Monitoring redditor '%s' for submissions", target_redditor)

        redditor = await self.praw_reddit.redditor(name=target_redditor)

        async for submission in redditor.stream.submissions():
            print("-------------")
            print(self.render_submission(submission, prefix="redditor"))
            print("-------------")
            await self.redditor_submission_to_event(
                redditor=redditor, reddit_submission=submission
            )

    @staticmethod
    def hash_submission(submission_comment: asyncpraw.reddit.Submission) -> str:
        """
        Take a comment and return a hash for it.
        This is pretty simple - just a str of a tuple of the comment_id and contents
        :param submission_comment:
        :return:
        """
        return str(
            (submission_comment.id, submission_comment.selftext, submission_comment.author)
        )

    async def redditor_submission_to_event(
        self, redditor: str, reddit_submission: asyncpraw.reddit.Submission
    ) -> None:
        """
        Takes a reddit submission and puts it on the wire as an event.
        :param redditor: In some edge cases we will need to know who the system thought posted the content.
        :param reddit_submission: A submission
        :return:
        """
        # "Detect" removed or deleted comments - a poor method, but the best that can be done atm
        # Note - there may be issues where this does not work for non-english language subreddits
        if reddit_submission.selftext == r"[removed]":

            # Per notes in reddit-dev-notes.md
            # Not sure if removed events are being broadcast by the API
            if reddit_submission.author == r"[deleted]":

                await self.process_redditor_removed_submission_in_subreddit(
                    redditor, reddit_submission
                )
                return

        if reddit_submission.selftext == r"[deleted]":

            await self.process_redditor_deleted_submission_in_subreddit(reddit_submission)
            return

        # Not sure if editing a submission produces a separate event in this stream
        # Or if it just happens to change the status of the observed event to edited
        # Given this is intended to be the backend for a _display_ system - it probably
        # DOES NOT produce a separate event

        # Note - depending on the cache size events will start falling out of it
        # So it's fairly certain that we won't be able to provide the pre-edit content

        # If a submission has been edited, then it needs to go on the wire as an edited event
        if reddit_submission.edited:

            await self.process_redditor_edited_submission_in_subreddit(reddit_submission)

            return

        # If a message is not declared as edited, deleted or removed, just put it on the wire
        await self.process_redditor_created_submission_in_subreddit(reddit_submission)

    async def process_redditor_created_submission_in_subreddit(
        self, reddit_submission: asyncpraw.reddit.Submission
    ) -> None:
        """
        A redditor is registered as having edited a submission.
        :param reddit_submission: The submission which is noted as having been edited
        :return:
        """
        submission_creation_input_event = RedditUserCreatedSubredditSubmissionInputEvent(
            user_id=str(reddit_submission.author),
            submission=reddit_submission,
            subreddit=reddit_submission.subreddit,
            author_str=str(reddit_submission.author),
            creation_timestamp=reddit_submission.created_utc,
            submission_content=reddit_submission.selftext,
            submission_id=reddit_submission.id,
            submission_image=reddit_submission.url,
            submission_title=reddit_submission.title,
        )

        await self.send(submission_creation_input_event)

    async def process_redditor_edited_submission_in_subreddit(
        self, reddit_submission: asyncpraw.reddit.Submission
    ):
        """
        A redditor is registered as having edited a submission.
        :param reddit_submission: The submission which is noted as having been edited
        :return:
        """

        message_id = reddit_submission.id

        # Check if we have an existing old message to assign to this message
        message_hash = self.hash_submission(reddit_submission)
        if message_hash in self.reddit_state.previous_submission_map:
            old_message = self.reddit_state.previous_submission_map[message_hash]
        else:
            old_message = self.reddit_state.seen_submission_contents.get(message_id, None)

        submission_edit_input_event = RedditUserEditedSubredditSubmissionInputEvent(
            user_id=str(reddit_submission.author),
            submission=reddit_submission,
            author_str=str(reddit_submission.author),
            submission_image=None,
            submission_title=reddit_submission.title,
            # If we have it in our internal cache
            pre_edit_submission=old_message,
            # This may be the best we can do - as the message doesn't seem to have a "last edited"
            # or similar field
            edit_timestamp=str(time.time()),
            subreddit=reddit_submission.subreddit,
            submission_content=reddit_submission.selftext,
            submission_id=reddit_submission.id,
        )
        await self.send(submission_edit_input_event)

        self.reddit_state.previous_submission_map[message_hash] = old_message
        # Store the current state of the message - in case it's edited again
        self.reddit_state.seen_submission_contents[message_id] = reddit_submission

    async def process_redditor_deleted_submission_in_subreddit(
        self, reddit_submission: asyncpraw.reddit.Submission
    ):
        """
        A redditor is registered as having deleted a submission.
        It is probable that they are the one who deleted the submission. But not certain.
        In the case that the submission is deleted - not removed - we can read the redditor's name
        out of the subreddit.
        :param redditor: Under other circumstances we'd read the submitter out of the submission.
                         But we might not be able to do that if the submission is gone.
                         So providing it here, manually.
        :param reddit_submission: The submissio which is noted as having been removed
        :return:
        """
        # Check to see if we have an old message
        submission_hash = self.hash_submission(reddit_submission)
        old_reddit_submission = self.reddit_state.previous_submission_map.get(
            submission_hash, None
        )

        # If we don't, try in the seen submissions
        if old_reddit_submission is None:
            old_reddit_submission = self.reddit_state.seen_submission_contents[
                reddit_submission.subreddit
            ].get(reddit_submission.id, None)

        # Update the cache - if a message has been removed it should never change again
        self.reddit_state.previous_submission_map[submission_hash] = None
        # Indicate that the submission is gone by setting the contents to None
        self.reddit_state.seen_submission_contents[reddit_submission.subreddit][
            reddit_submission.id
        ] = None

        deleted_message_event = RedditUserDeletedSubredditSubmissionInputEvent(
            submission=reddit_submission,
            subreddit=reddit_submission.subreddit,
            submission_title=reddit_submission.title,
            author_str=old_reddit_submission.author.id,
            del_timestamp=str(time.time()),
            submission_content=reddit_submission.selftext,
            submission_id=reddit_submission.id,
            submission_image=None,
            user_id=str(reddit_submission.author),
        )
        await self.send(deleted_message_event)

        return

    async def process_redditor_removed_submission_in_subreddit(
        self, redditor: str, reddit_submission: asyncpraw.reddit.Submission
    ):
        """
        A redditor is registered as having removed a submission.
        Probably the actual case is that someone has removed the submission _for_ them.
        :param redditor: Under other circumstances we'd read the submitter out of the submission.
                         But we might not be able to do that if the submission is gone.
                         So providing it here, manually.
        :param reddit_submission: The submissio which is noted as having been removed
        :return:
        """
        # Check to see if we have an old message
        submission_hash = self.hash_submission(reddit_submission)
        old_reddit_submission = self.reddit_state.previous_submission_map.get(
            submission_hash, None
        )

        # If we don't, try in the seen submissions
        if old_reddit_submission is None:
            old_reddit_submission = self.reddit_state.seen_submission_contents[
                reddit_submission.subreddit
            ].get(reddit_submission.id, None)

        # Update the cache - if a message has been removed it should never change again
        self.reddit_state.previous_submission_map[submission_hash] = None
        # Indicate that the submission is gone by setting the contents to None
        self.reddit_state.seen_submission_contents[reddit_submission.subreddit][
            reddit_submission.id
        ] = None

        # Without the old message there is no good way to know who the author was
        old_author_str = (
            "" if old_reddit_submission is None else str(old_reddit_submission.author.id)
        )

        removed_message_event = RedditUserRemovedSubredditSubmissionInputEvent(
            user_id=redditor,
            submission_id=reddit_submission.id,
            submission_title=reddit_submission.title,
            submission=reddit_submission,
            subreddit=reddit_submission.subreddit,
            author_str=old_author_str,
            remove_timestamp=str(time.time()),
            submission_content=reddit_submission.selftext,
            submission_image=reddit_submission.url,  # Not very sure how this is stored - working on it
        )

        await self.send(removed_message_event)

    # -------------------


class RedditOutput(Output):
    """
    Talk back to reddit.
    """

    @staticmethod
    def consumes_outputs() -> Set[Type[OutputEvent]]:
        return set()
