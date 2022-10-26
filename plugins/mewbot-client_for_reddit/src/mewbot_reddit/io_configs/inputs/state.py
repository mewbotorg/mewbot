from typing import Set, List, Dict

import dataclasses

import asyncpraw  # type: ignore


@dataclasses.dataclass
class CommentContentsState:

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
    # In order to have the old message contents available we need to cache it before it's
    # overwritten in seen_comment_contents hence
    # Keyed with the hash of a comment and valued with the value of the previous message of that
    # hash
    previous_comment_map: Dict[str, asyncpraw.Reddit.comment]


@dataclasses.dataclass
class SubmissionContentState:

    # Likewise we have submissions
    seen_submissions: Dict[str, Set[str]]
    seen_submission_contents: Dict[str, asyncpraw.Reddit.submission]
    previous_submission_map: Dict[str, asyncpraw.Reddit.submission]


@dataclasses.dataclass
class RedditState(CommentContentsState, SubmissionContentState):
    """
    Contains cached comments and the state of the monitored subreddits.
    """

    # To provide services related to edited/deleted/remove comments (such as "what was the contents
    # of this before the event") it's necessary to cache the contents of some messages against
    # future need.
    # This is done with dicts - this will change later bcause it presents a severe memory leak

    target_subreddits: List[str]  # All the subreddits to be monitored by the bot
    started_subreddits: Set[str]  # The subreddits where monitoring has started

    target_redditors: List[str]  # All of the redditors to be monitored
    started_redditors: Set[str]  # The redditors where monitoring has started
