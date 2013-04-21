# Copyright (C) 2013 Wesley Baugh
"""Functions to extract and process Twitter data."""
from __future__ import division
import bz2
import collections
import dateutil
import itertools
import json

import shapely.wkb


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


def extract_blocks(fname):
    """Get tweets from a bz2 archive.

    Args:
        fname: String of the full path the archive.

    Returns:
        Dictionary of census block geometry objects with census block ID
        as the key.
    """
    blocks = dict()
    with bz2.BZ2File(fname) as archive:
        for line in archive:
            block_id, geometry = line.rstrip().split('\t')
            geometry = shapely.wkb.loads(geometry.decode('hex'))
            blocks[block_id] = geometry
    return blocks


def bigrams(iterable):
    """Return all item bigrams of an iterable.

    Args:
        iterable: Any iterable object.

    Yields:
        Tuple containing two elements. For example:

        >>> list(bigrams([1, 2, 3, 4]))
        [(1, 2), (2, 3), (3, 4)]
    """
    prev = None
    for item in iterable:
        if prev:
            yield (prev, item)
        prev = item


def point_to_block(point, blocks):
    """Find the census block ID that holds the given point.

    Args:
        point: A shapely.geometry.Point object.
        blocks: A dictionary of block IDs mapping to the associated
            shapely geometry object representing the censsu block.

    Returns:
        The block ID that contains the point, otherwise None.
    """
    for block in blocks:
        if blocks[block].contains(point):
            return block
    return None


def compute_block_interactions(users, blocks):
    """Compute census block interactions using Twitter data.

    Args:
        users:
        blocks: Dictionary of census block geometry objects with census
        block ID as the key.

    Returns:
        Dictionary of block IDs with a dictionary that stores how many
        times the source block interacted with the target block.
    """
    interactions = collections.defaultdict(collections.Counter)

    for index, user in enumerate(users, start=1):
        cache = dict()
        for bigram in bigrams(users[user]):
            source, target = bigram
            source_long, source_lat = source
            target_long, target_lat = target

            if source in cache:
                source = cache[source]
            else:
                block = source
                source = shapely.geometry.Point(source_long, source_lat)
                source = point_to_block(source, blocks)
                cache[block] = source

            if target in cache:
                target = cache[target]
            else:
                block = target
                target = shapely.geometry.Point(target_long, target_lat)
                target = point_to_block(target, blocks)
                cache[block] = target

            if source is None or target is None:
                continue

            interactions[source][target] += 1

    return dict(interactions)


def dump_interactions(interactions, fileobj):
    """Save the census block interactions to a file.

    Args:
        interactions: Dictionary of block IDs with a dictionary that
            stores how many times the source block interacted with the
            target block.
        fileobj: File object to write the data to.
    """
    for source in sorted(interactions):
        interaction = json.dumps(interactions[source])
        fileobj.write('\t'.join([str(source), interaction]) + '\n')


def load_interactions(fileobj):
    """Load the census block interactions from a file.

    Args:
        fileobj: File object to load the data from.

    Returns:
        Dictionary of block IDs with a dictionary that stores how many
        times the source block interacted with the target block.
    """
    interactions = dict()
    for line in fileobj:
        source, interaction = line.rstrip().split('\t')
        interactions[source] = json.loads(interaction)
    return interactions
