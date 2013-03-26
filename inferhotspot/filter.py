# Copyright 2013 Wesley Baugh
"""Filter and combine all bz2 files based on tweet attributes.

Because the tweets returned by the Twitter Streaming API don't always
match in a way that we would expect, sometimes an additional layer of
filtering is required.

As an example, sometimes we want only those tweets that have a specific
coordinates to be matches. However, the filter endpoint will try to use
the region defined in the `place` field if the `coordinates` field is
not populated, which will cause false positive matches.
"""
import bz2
import json
import glob
import os

from config import get_config


class FilterInBox(object):
    """Matches if a tweet has a geocoded point in a bounding box.

    Attributes:
        box = A pair of longitude and latitude pairs, with the southwest
            corner of the bounding box coming first.
    """

    def __init__(self, box):
        """Creates a new in-box filter.

        Args:
            box = A pair of longitude and latitude pairs, with the
                southwest corner of the bounding box coming first.
        """
        self.box = box

    def in_box(self, point):
        """Whether or not a point is within the bounding box.

        If the coordinates field is populated, the values there will be
        tested against the bounding box.

        Args:
            point: Coordinates to check. Note that this field uses
                geoJSON order (longitude, latitude)

        Returns:
            Boolean whether or not the point is within the bounding box.
        """
        return (self.box[0] < point[0] < self.box[2] and
                self.box[1] < point[1] < self.box[3])

    def __call__(self, tweet):
        """Whether or not a tweet is within the bounding box.

        If the coordinates field is populated, the values there will be
        tested against the bounding box.

        Args:
            tweet: JSON object representing the tweet to check.

        Returns:
            Boolean whether or not the tweet is within the bounding box.
        """
        coords = tweet['coordinates']
        if coords:
            point = coords['coordinates']
            if self.in_box(point):
                return True
        return False


def combine_filter(directory, output, filters, msginterval=10000):
    """Combine tweets that match a filter from bz2 files.

    Args:
        directory: The directory containing bz2-archive files. Each line
            of the uncompressed file must be a JSON encoded tweet.
        output: The filename of the uncompressed file to save the
            combined tweets.
        filters: Collection of callable objects that when given a JSON
            decoded tweet should return a boolean if the tweet matches
            the filter or not. The filters are evaluated using
            logical-OR, so if any filter matches the tweet is saved.
        msginterval: Number of tweets to process between displaying
            a status message to the user on stdout.
    """
    status = 'count: {0}\ttotal: {1}\terrors: {2}'
    count, total, errors = 0, 0, 0
    with open(output, mode='w') as out:
        pathname = os.path.join(directory, '*.bz2')
        for fname in glob.iglob(pathname):
            with bz2.BZ2File(fname) as archive:
                print 'Processing:', fname
                for line in archive:
                    line = line.rstrip()
                    try:
                        tweet = json.loads(line)
                    except ValueError:
                        errors += 1
                        continue
                    if any(check(tweet) for check in filters):
                        count += 1
                        out.write(line + '\n')
                    total += 1
                    if total % msginterval == 0:
                        print status.format(count, total, errors)
    if total % msginterval != 0:
        print status.format(count, total, errors)


if __name__ == '__main__':
    config = get_config()
    path = config.get('filter', 'process_directory')
    fname = config.get('filter', 'output')
    box = json.loads(config.get('place', 'box'))

    filters = [FilterInBox(box)]
    combine_filter(directory=path, output=fname, filters=filters)
