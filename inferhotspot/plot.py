# Copyright (C) 2013 Wesley Baugh
"""Visually display geocded tweets."""
import bz2
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


def extract_points(tweets):
    """Extract the longitude and latitude data from tweets.

    Args:
        tweets: An iterable containing JSON decoded tweets.

    Yields:
        A tuple of the longitude and latitude coordinates extracted
        from the tweet.
    """
    for tweet in tweets:
        point = tweet['coordinates']['coordinates']
        longitude = point[0]
        latitude = point[1]
        yield longitude, latitude


def plot_map(tweets):
    """Plot geocoded tweets on a map.

    Use matplotlib to produce a scatter plot of the longitude and
    latitude data from a collection of tweets.

    Args:
        tweets: Iterable of tweets.
    """
    points = list(extract_points(tweets))
    longitude, latitude = zip(*points)

    figure = plt.figure('map')
    ax = figure.add_subplot(1, 1, 1)
    scatter = ax.scatter(x=longitude,
                         y=latitude,
                         c=latitude,
                         cmap=plt.cm.prism,
                         s=10,
                         alpha=0.25)
    plt.show()


if __name__ == '__main__':
    config = get_config()
    path = config.get('plot', 'path')
    fname = config.get('plot', 'archive')
    tweets = parse_archive(os.path.join(path, fname))
    plot_map(tweets)
