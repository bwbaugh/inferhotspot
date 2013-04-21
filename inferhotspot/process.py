# Copyright (C) 2013 Wesley Baugh
"""Functions to extract and process Twitter data."""
from __future__ import division
import bz2
import collections
import dateutil
import itertools
import json


def parse_archive(path):
    """Get tweets from a bz2 archive.

    Args:
        path: String of the path for the file.

    Yields:
        Dictionary representing a tweet, decoded from a JSON string.
    """
    with bz2.BZ2File(path) as archive:
        for line in archive:
            line = line.rstrip()
            try:
                tweet = json.loads(line)
            except ValueError:
                continue
            yield tweet


def extract_data(tweets):
    """Extract data to plot from tweets.

    Args:
        tweets: An iterable containing JSON decoded tweets.

    Yields:
        A tuple of the longitude and latitude coordinates, the
        created-at `datetime.datetime` object parsed from the tweet, and
        the tweet's user ID as a number.

        For example, if a tweet contained:
            tweet[created_at] = 'Tue Feb 12 06:33:37 +0000 2013'
        The datetime object yielded would be:
            datetime.datetime(2013, 2, 12, 6, 33, 37, tzinfo=tzutc())
    """
    for tweet in tweets:
        # Coordinates
        point = tweet['coordinates']['coordinates']
        longitude = point[0]
        latitude = point[1]
        # Created-at time
        created_at = tweet['created_at']
        created_at = dateutil.parser.parse(created_at)
        # User ID
        user_id = tweet['user']['id']
        yield longitude, latitude, created_at, user_id


def process_data(data):
    """Process the raw data and extract additional features.

    Datetime objects are converted to a float of the time of day.
    longitude, latitude, and user_id information is used to extract a
    dictionary of users that have each check-in made by each user.

    Args:
        data: List of the tuple outputs from `extract_data`.

    Retruns:
        Tuple of lists: longitude, latitude, time, users.
    """
    longitude, latitude, time, user_id = zip(*data)
    time = [(x.hour + (x.minute / 60)) for x in time]
    # Combine all points from same user.
    users = collections.defaultdict(list)
    for ulong, ulat, user in itertools.izip(longitude, latitude, user_id):
        users[user].append((ulong, ulat))
    return longitude, latitude, time, users
