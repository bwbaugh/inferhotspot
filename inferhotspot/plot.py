# Copyright (C) 2013 Wesley Baugh
"""Visually display geocded tweets."""
from __future__ import division
import bz2
import dateutil
import json
import os

import matplotlib.pyplot as plt

from config import get_config


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
        A tuple of the longitude and latitude coordinates, and the
        created-at `datetime.datetime` object parsed from the tweet.

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
        yield longitude, latitude, created_at


def plot_map(tweets):
    """Plot geocoded tweets on a map.

    Use matplotlib to produce a scatter plot of the longitude and
    latitude data from a collection of tweets.

    Args:
        tweets: Iterable of tweets.
    """
    data = list(extract_data(tweets))
    longitude, latitude, time = zip(*data)
    time = [(x.hour + (x.minute / 60)) for x in time]

    figure = plt.figure('map')
    ax = figure.add_subplot(1, 1, 1)
    ax.set_title('Geocoded Tweets in Denton County')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True)

    scatter = ax.scatter(x=longitude,
                         y=latitude,
                         c=time,
                         cmap=plt.cm.rainbow,
                         s=5,
                         alpha=0.5,
                         lw=0.5)

    colorbar = figure.colorbar(scatter,
                               ax=ax,
                               cmap=plt.cm.rainbow,
                               ticks=range(24))
    colorbar.solids.set_edgecolor("face")
    # Make colorbar solid.
    # See: http://stackoverflow.com/a/4480124/1988505
    colorbar.set_alpha(1)
    colorbar.draw_all()

    figure.tight_layout()
    plt.show()


if __name__ == '__main__':
    config = get_config()
    path = config.get('plot', 'path')
    fname = config.get('plot', 'archive')
    tweets = parse_archive(os.path.join(path, fname))
    plot_map(tweets)
