### Import note

[The reddit api docs](https://www.reddit.com/wiki/api/)

As per the terms laid out on this page
 - This plugin is named mewbot-client_for_reddit (not mewbot-reddit, which would be the normal naming scheme)
 - This plugin is not developed by reddit.
 - This software is not officially endorsed or supported by reddit
 - The aim for this plugin is non-commercial. All source code is provided freely and is open source according to the terms of the licence. Which can be found in LICENSE.md

We're creating a script application. 
Which will thus use password flow to authenticate.

### Introduction

Note asyncpraw strongly discourages the use of multiple instances of it's major apis.
This should be fairly simple to accommodate in design - we'll never actually have two instances of the class active at any one time.
Instead, using one shared between Input and Output.

[The PRAW - Python Reddit Api Wrapper - docs are very helpful](https://asyncpraw.readthedocs.io/)

There appears to be two ways to interact with reddit.
1) A self-bot - which their terms and conditions seem fine with (unlike discord) - where you log in as yourself and interact with reddit as yourself
2) A bot-bot - examples abound - where you take and respond to the entire reddit event flow (better have a decent net connection and a fast box)

I suspect - but do not know - that these cases are sufficiently different that it makes sense to deal with them as separate IOConfigs.

Starting with the self-bot - and see how it goes.

As with discord - where it seemed to be a good idea to create a discord guild purely for bot testing purposes - it will probably be necessary to do the same with a subreddit
More to follow on this.

### Inputs

#### Input Events

Will depend on working through the reddit api and implementing what's useful.
As a minimal set

 - subreddits being created
 - subreddits being deleted
 - subreddits going private

 - Posts created on monitored subreddits
 - Posts edited on monitored subreddit
 - Posts deleted on monitored subreddit
 - Posts pinned on monitored subreddit

 - People joining monitored subreddits
 - People leaving monitored subreddits
 - People you follow making posts

 - Replies to posts you have created on reddit
 - Or posts made in any of the subreddits you are following (danger - likely to be quite a lot of data)
 - These replies being deleted or edited

 - Upvotes or downvotes being given to the user for posts
 - User being banned from a subreddit (hopefully rare)
 - Responses to replies to posts you have created on reddit

(There are a lot of different ways that kudos can be given and received - so it might well be that there ends up being a whole subclass of Kudos Input events - depending on where and how it was given)

Others may be added as needed.

As with discord - though to a greater extent - it might be necessary to institute some kind of loopback control of the input method
 - to update the subreddits being watched
 - to update the users being watched

While writing the input classes it became apparent that there were two real operational modes that might be of interest
 - following a list of subreddits
 - following a list of users
So it seemed to make sense, conceptually, to spit these down into two separate input classes.
Which also provides a chance to experiment with a IOConfig with multiple input classes. 
Which is also going to serve as an example for the plugin system...
Because why do one thing at once, well, when you can do three, badly.

Note - thinking is it makes sense for both of the inputs to, sometimes, produce the same type of events.
Though possibly with a flag to indicate the type of input which produced it...

#### Connecting to reddit

Trying for a password authentication flow app.

This requires four pieces of information.
 - client_id
 - client_secret
 - password
 - username - bots are always explicitly associated with an account

There are a number of complications we may get into later when it comes to actually authenticating "properly".
For the moment a password based app would seem to do.

(There is an alternative authorization flow - where you prompt the user to login to reddit via browser.
This provides a `refresh_token` which may not expire when e.g. the user changes password.
Working on this problem later...
)

#### read only

The default way to start reddit seems to be read only.
Which should do for many applicatons.

So creating a read only IOConfig - after all, no reason to declare an output if it's not going to be used.

#### Acquiring credentials

Turned out to be slightly harder than expected.

1) Be sure that you have validated your email. If you do not do this, reddit will silently fail to send you your client_id
2) Four pieces of information are needed to connect a bot to reddit
   1) your reddit username (username)
   2) your reddit password (password)
   3) Your app secret (client_secret in praw)
   4) Your app id (client_id in praw)
3) Note - these are not named consistently anywhere. This can make the process of gathering these credentials somewhat annoying.
4) Go to https://www.reddit.com/prefs/apps (ideally after logging in to reddit - if you don't, there's a nasty tendency to get stuck in an infinite login loop).
5) Here, create a new application. You probaly want a "script" type application, as that's the only one I've tested so far. Other options will be added later.
6) This new application will provide you with the client_secret in the panel for the new app - it's just called secret
7) Reddit will now send you your client id. They will not call it client_id. They will call it App ID. Or something like that. If you haven't validated your email  address, this wil not be sent and there seems to be no way to retrieve it after the fact.
8) With these four credentials you should be able to populate a full set of bot credentials as in examples/trivial_reddit_bot.yaml.


#### Polling

Reddit doesn't seem to support streaming websockets - so just having to poll the api.

Note - subscribing to "all" as a subreddit does not seem to work as expected.
Or, in fact, at all.

##### Comments

Now the problem is retrieving events and getting them on the wire.
We can poll the subreddit every interval - and hash the returned comments to determine if they need to be put on the wire.
(If the hash check fails, then the comment might have been edited - and we need to pop an event for that).
Some caching to see if they have been seen before will be required.
Also allows use to (sometimes) give the original content of the message in with the edit event.


There's some efficiency issues - we don't seem (bafflingly) to be able to specify a time limit.

But there is something we _can_ do.

You can pass additional parameters to the underlying get request using syntax something like

```python
multireddit = await self.praw_reddit.subreddit(target_subreddit, fetch=True)
async for comment in multireddit.comments(limit=25, params={"count": "25"}):
    print(type(comment))
    print(comment.author)
```

(API ref from https://www.reddit.com/dev/api/)

No clue why it would be this way round and not a time window.
But there probably is a reason.

So some messing around with after should allow us to iterate back until we find a known value - when we can stop.

(To quote from the docs

"To page through a listing, start by fetching the first page without specifying values for after and count. The response will contain an after value which you can pass in the next request. It is a good idea, but not required, to send an updated value for count which should be the number of items already fetched."
)

The full attributes of a comment returned by PRAW are (from the PRAW source code)

    ================= ==================================================================
    Attribute         Description
    ================= ==================================================================
    ``author``        Provides an instance of :class:`.Redditor`.
    ``body``          The body of the comment, as Markdown.
    ``body_html``     The body of the comment, as HTML.
    ``created_utc``   Time the comment was created, represented in `Unix Time`_.
    ``distinguished`` Whether or not the comment is distinguished.
    ``edited``        Whether or not the comment has been edited.
    ``id``            The ID of the comment.
    ``is_submitter``  Whether or not the comment author is also the author of the
                      submission.
    ``link_id``       The submission ID that the comment belongs to.
    ``parent_id``     The ID of the parent comment (prefixed with ``t1_``). If it is a
                      top-level comment, this returns the submission ID instead
                      (prefixed with ``t3_``).
    ``permalink``     A permalink for the comment. Comment objects from the inbox have a
                      ``context`` attribute instead.
    ``replies``       Provides an instance of :class:`.CommentForest`.
    ``saved``         Whether or not the comment is saved.
    ``score``         The number of upvotes for the comment.
    ``stickied``      Whether or not the comment is stickied.
    ``submission``    Provides an instance of :class:`.Submission`. The submission that
                      the comment belongs to.
    ``subreddit``     Provides an instance of :class:`.Subreddit`. The subreddit that
                      the comment belongs to.
    ``subreddit_id``  The subreddit ID that the comment belongs to.
    ================= ==================================================================

    .. _unix time: https://en.wikipedia.org/wiki/Unix_time

So parsing the `parent_id` to determine if a comment is top level or not.

##### Submissions

... Gonna have to poll for posts separately...

After some time focusing on the comments, it turns out that will have to poll a number of properties individually.

Question - does removing a post entirely also remove all the comments?
Probably.
Should this trigger a bunch of "comment deleted" InputEvents.
Probably not.
There could be thousands of the things.
(But this might want to be a behavior which can be turned on or off).


TURNS OUT NONE OF THE BELOW IS NECESSARY - BECAUSE PRAW ALREADY OFFERS IT BUILT IN - AS A MEANS OF STREAMING COMMENTS AND POSTS OCCURING IN A SUBREDDIT.

Algorith - for comments (going to have to work something out for everything else)

For each of the subreddits
   Startup - poll for posts
   For each of the posts
      If we have seen this post id before
         Is the post edited?
            If yes, then 
               Is the post one we have an assigned hash for?
                  If yes - then retrieve the previous text value based on its hash and send
                  If no - send the stored text, store this keyed with a hash (post has been edited multiple times - storing the hash and current text in case we see if again in another subreddit)
            if no then
               Check to see if it's removed or deleted. Send appropriate event.
      If we have not seen this post id before
         Note we've seen it and store the current text
         If there is one, because it could be removed or deleted and this is the first we're hearing about it
         Regardless, continue
      If the post is edited, and is one we have a hash for (so we have seen this edit event before)
         Retrieve the old text using the hash and put it on the wire
         If we need to - if it's a new event then we don't need to do this step.
      If we do not have a hash for this event
         Just put it on the wire
         


   Run - poll for posts
      Gather the posts - then do the above

Turns out, none of this is necessary - because PRAW offers a comment stream... which is great.
Really simplifies things and can use their own infrastructure to get streams for other things.

#### Submission definitions


    **Typical Attributes**

    This table describes attributes that typically belong to objects of this class.
    Since attributes are dynamically provided (see
    :ref:`determine-available-attributes-of-an-object`), there is not a guarantee that
    these attributes will always be present, nor is this list necessarily complete.

    ========================== =========================================================
    Attribute                  Description
    ========================== =========================================================
    ``author``                 Provides an instance of :class:`.Redditor`.
    ``clicked``                Whether or not the submission has been clicked by the
                               client.
    ``comments``               Provides an instance of :class:`.CommentForest`.
    ``created_utc``            Time the submission was created, represented in `Unix
                               Time`_.
    ``distinguished``          Whether or not the submission is distinguished.
    ``edited``                 Whether or not the submission has been edited.
    ``id``                     ID of the submission.
    ``is_original_content``    Whether or not the submission has been set as original
                               content.
    ``is_self``                Whether or not the submission is a selfpost (text-only).
    ``link_flair_template_id`` The link flair's ID.
    ``link_flair_text``        The link flair's text content, or None if not flaired.
    ``locked``                 Whether or not the submission has been locked.
    ``name``                   Fullname of the submission.
    ``num_comments``           The number of comments on the submission.
    ``over_18``                Whether or not the submission has been marked as NSFW.
    ``permalink``              A permalink for the submission.
    ``poll_data``              A :class:`.PollData` object representing the data of this
                               submission, if it is a poll submission.
    ``saved``                  Whether or not the submission is saved.
    ``score``                  The number of upvotes for the submission.
    ``selftext``               The submissions' selftext - an empty string if a link
                               post.
    ``spoiler``                Whether or not the submission has been marked as a
                               spoiler.
    ``stickied``               Whether or not the submission is stickied.
    ``subreddit``              Provides an instance of :class:`.Subreddit`.
    ``title``                  The title of the submission.
    ``upvote_ratio``           The percentage of upvotes from all votes on the
                               submission.
    ``url``                    The URL the submission links to, or the permalink if a
                               selfpost.
    ========================== =========================================================

    .. _unix time: https://en.wikipedia.org/wiki/Unix_time



### User forward outputs

To this point we've been watching subreddits.
Now watching redditors as well.
There are good ways to watch people's comments and submissions.
Less good ways to watch other properties - but these can be worked on.

#### How to post in a user profile using PRAW

Probably?

https://www.reddit.com/r/redditdev/comments/6cfu55/is_there_a_way_to_post_to_your_user_profile_using/

So - to monitor a profile - use a subreddit monitor.
However, will probably have to filter for all the comments which end up there which are _not_ in the profile - as it's also an agregate of all the content someone posts.



### Outputs

Turns out you can create entire new subreddits through the api.
Which is sort of a terrifying capability, it has to be said.
But might e quite useful for testing purposes.


### Other notes

praw uses aiohttp as a backend - so it's probably possibly to reuse the same aiohttp instance EVEN MORE.

Spent some time chasing my tail trying to use removed_by_category on a comment object.
Turns out, that's only for posts.
The best I've been able to do is check if the body has been replaced with \[removed\] or \[deleted\].
Clearly this isn't great (if nothing else, you can fool it by just setting the contents of your actual post to \[removed\] or \[deleted\]) but it's the best I've been able to do for the moment.
Not sure the difference matters that much.
See https://www.reddit.com/r/redditdev/comments/jl6xqp/praw_best_way_to_check_if_a_commenta_post_you/ ).

If a comment has been genuinely removed, we expect to see the body set to \[removed\] and the author field set to \[deleted\]
See https://www.reddit.com/r/redditdev/comments/cgsnpz/how_can_i_use_the_reddit_api_or_praw_to_check_if/
            




ACTUALLY - Plugins should provide the name of the plugin and the types of input for that plugin that it offers.
This is the way.

Todo: Not currently sure how it appears if a user makes a submission to another user's profile - might want a seperate event for it?
Todo: RSS comments can be edited. Would be good to implement edit detection there as well 
Todo: It'd be a good idea to error if we try and set an attribute which does not exist when creating a component from YAML



### Needed features

1) A means of setting up a new plugin quickly and easily
2) A function to validate your plugin before publishing it
3) An official plugin list - with a warning if you try and load something which is not on the list.
4) Or it just doesn't - but you can override it
5) The ability to include docs in with the main program as well
6) Cannot currently detect when submissions are pinned and unpinned - might need a poll for it
7) Currently the version of the subreddit monitor pointed at a user's profile yield the wrong type of events
8) A general means, in the YAML, to negate conditions
