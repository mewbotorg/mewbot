#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2021 - 2023 Mewbot Developers <mewbot@quicksilver.london>
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Provides an IOConfig which can poll RSS feeds and produce InputEvents from them.

Currently, can only read from a list of RSS feeds which it regularly polls.
"""

from __future__ import annotations

from typing import (
    Any,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    SupportsInt,
    Type,
    Union,
)

import asyncio
import dataclasses
import logging
import pprint
from itertools import cycle

import aiohttp
import feedparser  # type: ignore

from mewbot.api.v1 import Input, InputEvent, IOConfig, Output

# rss input operates on a polling loop
# feed read attempts are spread out over the interval

# NOTE
# Input - is what you might expect - it parses rss feeds and puts them on the wire
# Output - RSS server running locally - this has various properties -
#          in particular, you can set the number of events to be served ... might be better to back
#          this with a persistent data source
#          when one exists
#          RSS is not a real time protocol - so the number of events to store is quite important.

TITLE_NOT_SET_STR = "TITLE NOT SET BY SOURCE"
LINK_NOT_SET_STR = "LINK NOT SET BY SOURCE"
DESCRIPTION_NOT_SET_STR = "DESCRIPTION NOT SET BY SOURCE"
AUTHOR_NOT_SET_STR = "AUTHOR NOT SET BY SOURCE"
CATEGORY_NOT_SET_STR = "CATEGORY NOT SET BY SOURCE"
COMMENTS_NOT_SET_STR = "COMMENTS (URL) NOT SET BY SOURCE"
ENCLOSURE_NOT_SET_STR = "ENCLOSURE (URL) NOT SET BY SOURCE"
PUBDATE_NOT_SET_STR = "PUBDATE NOT SET BY SOURCE"
SOURCE_NOT_SET_STR = "SRC NOT SET BY SOURCE"


@dataclasses.dataclass
class RSSInputEvent(InputEvent):
    """
    Should contain all the info from the original RSS message in a mewbot InputEvent.

    Some normalisation might be required, as not all RSS feeds seem to correspond to the standard.
    Spec from https://validator.w3.org/feed/docs/rss2.html#hrelementsOfLtitemgt
    """

    # pylint: disable=too-many-instance-attributes
    # Want to fully represent the core RSS standard

    title: str  # The title of the item.
    link: str  # The URL of the item.
    description: str  # The item synopsis.
    author: str  # Email address of the author of the item
    category: str  # Includes the item in one or more categories.
    comments: str  # URL of a page for comments relating to the item
    enclosure: str  # Optional URL of media associated with the file
    guid: str  # A unique identifier for the item
    pub_date: str  # Indicates when the item was published.
    source: str  # The RSS channel that the item came from.

    site_url: str  # The site according to us
    entry: feedparser.util.FeedParserDict  # raw entry for later processing

    startup: bool  # Was this feed read as part of first read for any given site?


class RSSIO(IOConfig):
    """
    IOConfig to read from RSS feeds.
    """

    _input: Optional[RSSInput] = None
    _output: None

    _sites: List[str]  # A list of sites to poll for RSS update events
    _polling_every: int  # How often to poll all the given sites (in seconds)

    def __init__(
        self,
        *args: Optional[Any],
        **kwargs: Optional[Any],
    ) -> None:
        """
        Configure the RSSIO.

        Most of the actual configuration is done after __init__ using information from the yaml
        that defines this class.
        :param args:
        :param kwargs:
        """
        self._logger = logging.getLogger(__name__ + "DesktopNotificationIO")

        # Not entirely sure why, but empty properties in the yaml errors
        self._logger.info("DesktopNotificationIO received args - %s", args)
        self._logger.info("DesktopNotificationIO received kwargs - %s", kwargs)

    @property
    def polling_every(self) -> int:
        """
        Number of seconds between each time a site in the polling list is polled.
        """
        return self._polling_every

    @polling_every.setter
    def polling_every(self, new_polling_every: SupportsInt) -> None:
        self._polling_every = int(new_polling_every)

    @property
    def sites(self) -> List[str]:
        """
        Get a list of the sites which are currently being polled.

        Note - changing the return of this function DOES NOT change which sites are being polled.
        :return:
        """
        return self._sites

    @sites.setter
    def sites(self, sites: List[str]) -> None:
        """
        Presented as a property because updating it requires updating the runner as well.
        """
        if not isinstance(sites, list):
            raise AttributeError("Please provide a list of sites.")

        self._sites = sites
        if not self._input:
            return
        self._input.sites = sites

    def get_inputs(self) -> Sequence[Input]:
        """
        Returns the inputs supported by the IOConfig - starting them if needed.
        """
        if not self._input:
            self._input = RSSInput(self._sites, self._polling_every)

        return [self._input]

    def get_outputs(self) -> Sequence[Output]:
        """
        We do not currently support RSS output, so this is an empty list.
        """
        return []


@dataclasses.dataclass
class RSSInputState:
    """
    State of the sites being monitored.

    Information stored includes
     - which sites are currently being polled
     - which sites have been started (historic entries retrieved and put on the wire)
     - which entries have been put on the wire in total
    """

    _sites: List[str]  # A list of sites to poll for RSS update events
    _sites_iter: Iterable[str]
    _sites_started: Set[str]  # sites which have undergone startup
    _sent_entries: Mapping[str, Set[str]]  # Entries which have been put on the wire

    def start(self) -> None:
        """
        Calculates all internal states based off _sites.
        """
        self._sites_iter = cycle(iter(self._sites))

        new_sent_entries = {}
        for new_site in self._sites:
            if new_site in self._sent_entries.keys():
                new_sent_entries[new_site] = self._sent_entries[new_site]
            else:
                new_sent_entries[new_site] = set()
        self._sent_entries = new_sent_entries

    @property
    def sites(self) -> List[str]:
        """
        Sites which are currently being polled.

        Note - changing the return of this _will not_ change the sites currently being polled.
        Please explicitly change the attribute for that.
        :return:
        """
        return self._sites

    @sites.setter
    def sites(self, new_sites: List[str]) -> None:
        if not isinstance(new_sites, list):
            raise AttributeError("Please provide a list of sites.")
        self._sites = new_sites
        self.start()

    @property
    def sites_iter(self) -> Iterable[str]:
        """
        Iterable of the sites currently being polled.

        Note - mutating this _will not_ change the sites currently being polled.
        :return:
        """
        return self._sites_iter

    @property
    def sites_started(self) -> Set[str]:
        """
        Sites which have been started (i.e. the initial number of entries read and sent).

        Note - changing the return of this _will_ change what sites are registered as having been
        started.
        :return:
        """
        return self._sites_started

    @property
    def sent_entries_size(self) -> int:
        """
        The number of entries which have been put on the wire.
        """
        return len(self._sent_entries)

    def note_site_started(self, site_started: str) -> None:
        """
        Record that a site has been successfully started.
        """
        self._sites_started.add(site_started)

    def note_event_transmitted(self, site_url: str, site_uid: str) -> None:
        """
        Record that an entry with a uid has been put on the wire.

        Now broken down by site so that we can more easily purge the old entries.
        When they have been superseded by new ones.
        Otherwise, they would just accumulate endlessly - a nasty memory leak.
        """
        self._sent_entries[site_url].add(site_uid)

    def check_for_event(self, site_url: str, site_uid: str) -> bool:
        """
        Check to see if an event is recorded as having been sent for the specified site.
        """
        return site_uid in self._sent_entries[site_url]


class RSSInput(Input):
    """
    Polling RSS Input source.

    Produces RSSInputEvents every time a new event is detected in an RSS feed.
    """

    _loop: Union[None, asyncio.events.AbstractEventLoop]

    _logger: logging.Logger

    _polling_every: int  # How often to poll all the given sites (in seconds)

    _rss_input_event_factory: RSSInputEventFactory

    state: RSSInputState

    def __init__(
        self, sites: List[str], polling_every: int, startup_queue_depth: int = 5
    ) -> None:
        """
        Start up the RSSInput.

        This class will contain an internal state which contains a summary of the state of the
        polling of the various RSS feeds.
        :param sites:
        :param polling_every:
        :param startup_queue_depth:
        """
        super().__init__()

        # Internal state variables
        self.state = RSSInputState(
            _sites=sites,
            _sites_iter=cycle(iter(sites)),
            _sites_started=set(),
            _sent_entries={},
        )
        self.state.start()

        # Generare a warning if the polling interval is less than this
        self.short_warning_interval = 60

        self._polling_every = polling_every  # The time taken to poll ever site in sites once

        self.startup_queue_depth = (
            startup_queue_depth  # How many RSS articles to retrieve for each site on start?
        )

        self._logger = logging.getLogger(__name__ + "RSSInput")

        # Used to note to the event loop when it's required to restart the monitor loop
        # self._restart_needed = asyncio.Event()

        # logging start
        self._logger.info(
            "RSSInput starting: \nsites\n%s\npolling_every: %s\nstartup_queue_depth: %s",
            pprint.pformat(self.state.sites),
            self._polling_every,
            self.startup_queue_depth,
        )

        self._rss_input_event_factory = RSSInputEventFactory()

        self._loop = None

    @property
    def polling_interval(self) -> Union[float, None]:
        """
        This is the time that the Input should wait between polling a new site.

        The total time between re-poll of each site is polling_every.
        """
        # If we have no sites to poll, then we shall do nothing
        if len(self.state.sites) == 0:
            return None
        return float(self._polling_every) / float(len(self.state.sites))

    @property
    def sites(self) -> List[str]:
        """
        List of sites currently being polled by this runner.

        Note - changing the return object for this _will_ change what sites are being polled.
        :return:
        """
        return self.state.sites

    @sites.setter
    def sites(self, new_sites: List[str]) -> None:
        self.state.sites = new_sites

    @staticmethod
    def produces_inputs() -> Set[Type[InputEvent]]:
        """
        Defines the set of input events this Input class can produce.
        """
        return {
            RSSInputEvent,
        }

    @property
    def polling_every(self) -> int:
        """
        Interval between polling each of the sites in the sites list.

        (Thus every site will be polled once each _this_ number of seconds).
        :return:
        """
        return self._polling_every

    @polling_every.setter
    def polling_every(self, new_polling_time: int) -> None:
        self._polling_every = new_polling_time

    @property
    def loop(self) -> asyncio.events.AbstractEventLoop:
        """
        Return the main event loop for this process.
        """
        if self._loop is not None:
            return self._loop
        self._loop = asyncio.get_running_loop()
        return self._loop

    def _get_entry_uid(self, entry: feedparser.util.FeedParserDict, site_url: str) -> str:
        """
        Returns a unique id (on a system level) for the given entry and site combination.

        Used to determine if entries have been put on the wire or not.
        As such, must always return some kind of semi-unique identifier.
        Even if the entry.guid of the FeedParserDict is malformed.
        """
        try:
            entry_in_feed_id = entry.guid
        except AttributeError:
            self._logger.warning(
                "entry %s did not possess a guid - %s might be producing malformed RSS entries",
                entry,
                site_url,
            )

            try:
                entry_pubdate = entry.pubDate
            except AttributeError:
                entry_pubdate = PUBDATE_NOT_SET_STR

            # This is not a fantastic fallback - but it should work most of the time
            entry_in_feed_id = f"{entry_pubdate}"

        return f"{entry_in_feed_id}:{site_url}"

    async def run(self) -> None:
        """
        Starts all sites, and then commences regular polling.
        """
        self._logger.info(
            "About to start RSS polling - %s will be polled every %s seconds",
            self.state.sites,
            self._polling_every,
        )
        if self._polling_every < self.short_warning_interval:
            self._logger.warning(
                "RSS polling interval is short %s (< %s seconds)",
                self._polling_every,
                self.short_warning_interval,
            )

        for target_site in self.state.sites_iter:
            if target_site not in self.state.sites_started:
                future = self.startup_site_feed(target_site)
            else:
                future = self.poll_site_feed(target_site)

            self.loop.create_task(future)

            # Delay to stagger site reads to prevent overwealming anything
            await asyncio.sleep(self.polling_every)

    async def fetch_feed(self, url: str) -> feedparser.FeedParserDict:
        """
        The actual action of fetch a feed - isolated here for easier replacement later.
        """
        # Need to add timeout and use etags to cut down on badnwidth use
        async with aiohttp.ClientSession(loop=self.loop) as session:
            async with session.get(url) as resp:
                resp_text = await resp.read()
                resp_headers = resp.headers

                site_newsfeed = feedparser.parse(
                    url_file_stream_or_string=resp_text, response_headers=resp_headers
                )

        return site_newsfeed

    async def startup_site_feed(self, site_url: str) -> None:
        """
        Preform the first read of a site.

        The requested number of events must be read and put on the wire.
        It must be noted that the site has been started.
        Regular polling of the site should commence after this method has been called.
        """
        self._logger.info(
            "Starting feed for site %s - %s entries will be retrieved",
            site_url,
            self.startup_queue_depth,
        )

        # Read the site feed
        site_newsfeed = await self.fetch_feed(site_url)

        site_entries = site_newsfeed.entries

        # Read the requested number of entries and put them on the wire
        for _ in range(0, self.startup_queue_depth):
            entry_internal_id = self._get_entry_uid(entry=site_entries[_], site_url=site_url)
            if self.state.check_for_event(site_url=site_url, site_uid=entry_internal_id):
                self._logger.warning(
                    "entry_internal_id - %s - for entry - %s - from site - %s - "
                    "has been seen before!",
                    entry_internal_id,
                    site_entries[_],
                    site_url,
                )
                continue

            try:
                await self._send_entry(entry=site_entries[_], site_url=site_url, startup=True)
            except IndexError:
                # Not enough entries in the retrieved feed to exhaust startup requirements?
                break

            self.state.note_event_transmitted(site_url=site_url, site_uid=entry_internal_id)

        self.state.note_site_started(site_url)

    async def poll_site_feed(self, site_url: str) -> None:
        """
        Preform a poll of an individual site's feed.

        :param site_url:
        :return:
        """
        self._logger.info("Reading from site %s", site_url)

        # Read the site feed
        site_newsfeed = await self.fetch_feed(site_url)
        site_entries = site_newsfeed.entries

        # Iterate backwards until we run into an entry which has already been sent
        transmitted_count = 0
        for entry in site_entries:
            entry_uid = self._get_entry_uid(entry, site_url)

            if self.state.check_for_event(site_url=site_url, site_uid=entry_uid):
                break

            await self._send_entry(entry=entry, site_url=site_url, startup=False)
            transmitted_count += 1

            self.state.note_event_transmitted(site_url=site_url, site_uid=entry_uid)

        self._logger.info("%s entries from %s transmitted", transmitted_count, site_url)

    async def _send_entry(
        self, entry: feedparser.util.FeedParserDict, site_url: str, startup: bool = False
    ) -> None:
        """
        Parse an RSS entry and put the OutputEvent representing it on the wire.
        """
        input_rss_event = self._rss_input_event_factory(entry, site_url, startup)

        # queue is not initialised - probably
        if not self.queue:
            return

        await self.queue.put(input_rss_event)


class RSSInputEventFactory:
    """
    Transforms a FeedParserDict into a RSSInputEvent to go on the wire.

    Class can be subclassed to provide finer control over feed entry to Input Event transformation.
    """

    _logger: logging.Logger

    def __init__(self) -> None:
        """
        Will start with independent logger.
        """
        self._logger = logging.getLogger(__name__ + "RSSInputEventFactory")

    def __call__(
        self, entry: feedparser.util.FeedParserDict, site_url: str, startup: bool = False
    ) -> RSSInputEvent:
        """
        Parse an RSS entry into a RSSInputEvent and return.
        """
        # Some RSS entries do not confirm to the spec - so some creative parsing might be required
        # Starting basic, and building up later

        problem_list: List[str] = []

        # guid - there are no rules for this syntax
        # THUS ONLY THE COMBINATION OF GUID AND SITE_URL SHOULD BE ASSUMED UNIQUE
        # This combination is used to determine if events have already been sent

        input_rss_event = RSSInputEvent(
            title=self.extract_field(
                entry=entry,
                attr_name="title",
                default=TITLE_NOT_SET_STR,
                problem_list=problem_list,
            ),
            link=self.extract_field(
                entry=entry,
                attr_name="link",
                default=LINK_NOT_SET_STR,
                problem_list=problem_list,
            ),
            description=self.extract_field(
                entry=entry,
                attr_name="description",
                default=DESCRIPTION_NOT_SET_STR,
                problem_list=problem_list,
            ),
            author=self.extract_field(
                entry=entry,
                attr_name="author",
                default=AUTHOR_NOT_SET_STR,
                problem_list=problem_list,
            ),
            category=self.extract_field(
                entry=entry,
                attr_name="category",
                default=CATEGORY_NOT_SET_STR,
                problem_list=problem_list,
            ),
            comments=self.extract_field(
                entry=entry,
                attr_name="comments",
                default=COMMENTS_NOT_SET_STR,
                problem_list=problem_list,
            ),
            enclosure=self.extract_field(
                entry=entry, attr_name="enclosure", default="", problem_list=[]
            ),  # enclosure is optional, so not bothering to log
            guid=self.extract_guid(entry=entry, site_url=site_url, problem_list=problem_list),
            pub_date=self.extract_pubdate(
                entry=entry, site_url=site_url, problem_list=problem_list
            ),
            source=self.extract_field(
                entry=entry,
                attr_name="source",
                default=SOURCE_NOT_SET_STR,
                problem_list=problem_list,
            ),
            site_url=site_url,
            startup=startup,
            entry=entry,
        )

        if problem_list:
            self._logger.info(
                "Bad parsing of entry \n%s\n \n%s", entry, "\n".join(problem_list)
            )

        return input_rss_event

    @staticmethod
    def extract_field(
        entry: feedparser.util.FeedParserDict,
        attr_name: str,
        default: str,
        problem_list: List[str],
    ) -> str:
        """
        Extract a named field from an RSS entry.
        """
        try:
            entry_attr = getattr(entry, attr_name)
        except AttributeError:
            problem_list.append(f"entry did not possess a {attr_name} attribute")
            entry_attr = default

        return str(entry_attr)

    @staticmethod
    def extract_enclosure(entry: feedparser.util.FeedParserDict) -> str:
        """
        Presented as an optional method because this is an optional attribute.

        As such, there is no logging if this method fails. It will just return the
        ENCLOSURE_NOT_SET_STR constant.
        :param entry:
        :return:
        """
        try:
            entry_enclosure = entry.enclosure
        except AttributeError:
            # No logging as this is an optional attribute
            entry_enclosure = ENCLOSURE_NOT_SET_STR

        return str(entry_enclosure)

    def extract_guid(
        self, entry: feedparser.util.FeedParserDict, site_url: str, problem_list: List[str]
    ) -> str:
        """
        Extract the guid from an RSS entry.

        We always need some form of guid - so using a method with a fallback which will always
        generate _something_ - hopefully - unique to the entry.
        :param entry:
        :param site_url:
        :param problem_list:
        :return:
        """

        # guid - there are no rules for this syntax
        # THUS ONLY THE COMBINATION OF GUID AND SITE_URL SHOULD BE ASSUMED UNIQUE
        # This combination is used to determine if events have already been sent
        try:
            entry_guid = entry.guid
        except AttributeError:
            problem_list.append(
                f"entry did not possess a guid - "
                f"{site_url} is producing malformed RSS entries"
            )

            entry_pubdate = self.extract_pubdate(
                entry=entry, site_url=site_url, problem_list=problem_list
            )

            # This is not a fantastic guid - but one needs to be set for internal tracking
            entry_guid = f"{site_url}:{entry_pubdate}"

        return str(entry_guid)

    def extract_pubdate(
        self, entry: feedparser.util.FeedParserDict, site_url: str, problem_list: List[str]
    ) -> str:
        """
        Extract the pubdate from an RSS entry.

        Presented as a separate method to allow higher level logging ("warning", not "info") if
        this fails.
        (This should _never_ fail - if it does, one of the sites being polled is producing
        malformed RSS).
        :param entry:
        :param site_url:
        :param problem_list:
        :return:
        """
        # pubDate - if this is not being set, something is badly wrong
        try:
            entry_pubdate = entry.pubDate
        except AttributeError:
            wrn_str = (
                f"entry did not possess a pubDate - "
                f"{site_url} might be producing malformed RSS entries"
            )
            self._logger.warning(wrn_str)
            problem_list.append(wrn_str)
            entry_pubdate = PUBDATE_NOT_SET_STR

        return str(entry_pubdate)
