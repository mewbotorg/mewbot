#!/usr/bin/env python3

from __future__ import annotations

from typing import Optional, Sequence, Union, Set, Type, List

import logging

import asyncpraw  # type: ignore

from mewbot.api.v1 import IOConfig, Input, Output, InputEvent, OutputEvent

from .inputs.subreddit import RedditSubredditInput
from .inputs.state import RedditState
from ..input_events import (
    # subreddit first events
    # - a submission has been manipulated in a subreddit
    SubRedditSubmissionCreationInputEvent,
    SubRedditSubmissionEditInputEvent,
    SubRedditSubmissionDeletedInputEvent,
    SubRedditSubmissionRemovedInputEvent,
    SubRedditSubmissionPinnedInputEvent,
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
    # RedditPersonaVoteInputEvent,
    # RedditPostVoteInputEvent,
)


SUBREDDIT_FOCUSSED_INPUT_EVENTS = (
    # - a user has interacted with the subreddit
    RedditUserJoinedSubredditInputEvent,
    RedditUserLeftSubredditInputEvent,
    RedditUserBannedFromSubredditInputEvent,
    # - a user has created a submission
    SubRedditSubmissionPinnedInputEvent,
    SubRedditSubmissionCreationInputEvent,
    SubRedditSubmissionDeletedInputEvent,
    SubRedditSubmissionRemovedInputEvent,
    SubRedditSubmissionEditInputEvent,
    # - a comment has been manipulated in the subreddit
    SubRedditCommentCreationInputEvent,
    SubRedditCommentEditInputEvent,
    SubRedditCommentDeletedInputEvent,
    SubRedditCommentRemovedInputEvent,
)


USER_FOSCUSSED_INPUT_EVENTS = (
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
    # RedditPersonaVoteInputEvent,
    # RedditPostVoteInputEvent,
)


USED_INPUT_EVENTS = SUBREDDIT_FOCUSSED_INPUT_EVENTS + USER_FOSCUSSED_INPUT_EVENTS


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
                praw_reddit=self.praw_reddit,
                redditors=self._redditors,
                reddit_state=self._subreddit_input.reddit_state,
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


class RedditRedditorInput(RedditSubredditInput):
    """
    Receives input from reddit.
    In particular, watches for events generated by a monitored list of redditors.
    """

    def __init__(
        self,
        praw_reddit: asyncpraw.Reddit,
        redditors: Optional[List[str]] = None,
        reddit_state: Optional[RedditState] = None,
    ) -> None:
        """
        :param praw_reddit: There can only be one asyncpraw instance so it needs to be
                            passed in
        :param redditors: A list of the redditors to watch. They might be up to something.
        :param reddit_state: Allows passing in an override stored state of reddit
        """
        redditors = redditors if redditors is not None else []

        self._logger = logging.getLogger(__name__ + ":" + type(self).__name__)

        # The users profile seem to act like a subreddit.
        # Monitoring them using the existing subreddit monitor
        super().__init__(
            praw_reddit=praw_reddit,
            subreddits=self.get_redditor_profile_names(redditors),
            reddit_state=reddit_state,
        )

        self._logger.info("Monitoring redditors - %s", self.reddit_state.target_redditors)

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
        return self.reddit_state.target_redditors

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
        # Monitoring the redditor's profiles - which act like subreddits
        # Currently yielding the wrong type of events
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
            await self.redditor_comment_to_event(reddit_comment=comment)

    async def redditor_comment_to_event(
        self, reddit_comment: asyncpraw.reddit.Comment
    ) -> None:
        """
        Takes a comment made by a redditor posting in a subreddit (or a profile) a puts it on the
        wire as an event.
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
        await self.process_subreddit_created_comment_on_submission(
            subreddit=reddit_comment.subreddit,
            reddit_comment=reddit_comment,
            top_level=top_level,
        )

    async def process_redditor_edited_comment_on_submission(
        self, reddit_comment: asyncpraw.reddit.Comment, top_level: bool
    ) -> None:
        """
        Edits have been detected to a redditor's comment.
        :param reddit_comment:
        :param top_level:
        :return:
        """

        await self.process_subreddit_edited_comment_on_submission(
            subreddit=reddit_comment.subreddit,
            reddit_comment=reddit_comment,
            top_level=top_level,
        )

    async def process_redditor_deleted_comment_on_submission(
        self, reddit_comment: asyncpraw.reddit.Comment, top_level: bool
    ) -> None:
        """
        A redditor comment has been processed as deleted.
        :param reddit_comment:
        :param top_level:
        :return:
        """
        await self.process_subreddit_deleted_comment_on_submission(
            subreddit=str(reddit_comment.subreddit),
            reddit_comment=reddit_comment,
            top_level=top_level,
        )

    async def process_redditor_removed_comment_on_submission(
        self, reddit_comment: asyncpraw.reddit.Comment, top_level: bool
    ) -> None:
        """
        A redditor comment has been detected as removed.

        :param reddit_comment:
        :param top_level: Is the comment to be processed top level
        :return:
        """
        await self.process_subreddit_removed_comment_on_submission(
            subreddit=reddit_comment.subreddit,
            reddit_comment=reddit_comment,
            top_level=top_level,
        )

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
            await self.redditor_submission_to_event(reddit_submission=submission)

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
        self, reddit_submission: asyncpraw.reddit.Submission
    ) -> None:
        """
        Takes a reddit submission and puts it on the wire as an event.
        :param redditor: In some edge cases we will need to know who the system thought posted
                         the content.
        :param reddit_submission: A submission
        :return:
        """
        # "Detect" removed or deleted comments - a poor method, but the best that can be done atm
        # Note - there may be issues where this does not work for non-english language subreddits
        if reddit_submission.selftext == r"[removed]":

            # Per notes in reddit-dev-notes.md
            # Not sure if removed events are being broadcast by the API
            if reddit_submission.author == r"[deleted]":

                await self.process_redditor_removed_submission_in_subreddit(reddit_submission)
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
            subreddit=reddit_submission.subreddit,
            author_str=str(reddit_submission.author),
            creation_timestamp=reddit_submission.created_utc,
            submission=reddit_submission,
            submission_content=reddit_submission.selftext,
            submission_id=reddit_submission.id,
            submission_image=reddit_submission.url,
            submission_title=reddit_submission.title,
        )

        await self.send(submission_creation_input_event)

    async def process_redditor_edited_submission_in_subreddit(
        self, reddit_submission: asyncpraw.reddit.Submission
    ) -> None:
        """
        A redditor is registered as having edited a submission.
        :param reddit_submission: The submission which is noted as having been edited
        :return:
        """
        await self.process_subreddit_edited_submission(
            reddit_submission=reddit_submission, subreddit=str(reddit_submission.subreddit)
        )

    async def process_redditor_deleted_submission_in_subreddit(
        self, reddit_submission: asyncpraw.reddit.Submission
    ) -> None:
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
        await self.process_subreddit_deleted_submission(
            subreddit=str(reddit_submission.subreddit), reddit_submission=reddit_submission
        )

    async def process_redditor_removed_submission_in_subreddit(
        self, reddit_submission: asyncpraw.reddit.Submission
    ) -> None:
        """
        A redditor is registered as having removed a submission.
        Probably the actual case is that someone has removed the submission _for_ them.
        :param redditor: Under other circumstances we'd read the submitter out of the submission.
                         But we might not be able to do that if the submission is gone.
                         So providing it here, manually.
        :param reddit_submission: The submissio which is noted as having been removed
        :return:
        """
        await self.process_subreddit_removed_submission(
            subreddit=str(reddit_submission.subreddit), reddit_submission=reddit_submission
        )


class RedditOutput(Output):
    """
    Talk back to reddit.
    """

    @staticmethod
    def consumes_outputs() -> Set[Type[OutputEvent]]:
        return set()
