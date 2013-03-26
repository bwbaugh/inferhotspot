# Copyright (C) 2013 Wesley Baugh
"""Visually display geocded tweets."""
from __future__ import division
import bz2
import dateutil
import json
import os

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1 import make_axes_locatable

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


def make_map(longitude, latitude, time, box, place):
    """Plot geocoded tweets on a map.

    Use matplotlib to produce a scatter plot of the longitude and
    latitude data from a collection of tweets.

    Args:
        longitude: List of longitude float values of length *N*.
        latitude: List of latitude float values of length *N*.
        time: List of time of day float values length *N*.
        box = A pair of longitude and latitude pairs, with the southwest
            corner of the bounding box coming first.
        place = String for the place name of the bounding `box`.

    Returns:
        Figure object used to create the map scatter plot.
    """
    figure = plt.figure('map')
    figure.set_size_inches(12, 9, forward=True)
    figure.set_dpi(100)

    ax = figure.add_subplot(1, 1, 1)
    ax.set_title('Geocoded Tweets in {0}'.format(place))
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True)

    rect = Rectangle(xy=(box[0], box[1]),
                     width=box[2] - box[0],
                     height=box[3] - box[1],
                     facecolor='none')
    ax.add_patch(rect)

    scatter = ax.scatter(x=longitude,
                         y=latitude,
                         c=time,
                         cmap=plt.cm.rainbow,
                         s=5,
                         alpha=0.5,
                         lw=0.5)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad='3%')
    colorbar = figure.colorbar(scatter,
                               cax=cax,
                               cmap=plt.cm.rainbow,
                               ticks=range(24))
    colorbar.solids.set_edgecolor("face")
    # Make colorbar solid.
    # See: http://stackoverflow.com/a/4480124/1988505
    colorbar.set_alpha(1)
    colorbar.draw_all()

    x_padding = (max(longitude) - min(longitude)) * 0.1
    y_padding = (max(latitude) - min(latitude)) * 0.1
    ax.set_xbound(box[0] - x_padding, box[2] + x_padding)
    ax.set_ybound(box[1] - y_padding, box[3] + y_padding)
    ax.set_aspect('equal')

    figure.tight_layout(rect=(0.05, 0.05, 0.95, 0.95))

    return figure


def make_time(time):
    """Plot a histogram of time of day values.

    Args:
        time: List of time of day float values length *N*.

    Returns:
        Figure object used for the histogram.
    """
    figure = plt.figure('time')
    figure.set_dpi(100)

    ax = figure.add_subplot(1, 1, 1)
    ax.set_title('Created-at Times of Tweets')
    ax.set_xlabel('Hour (UTC)')
    ax.set_ylabel('Number of Tweets')
    ax.set_xlim(0, 24)
    ax.grid(True)

    n, bins, patches = ax.hist(time, bins=range(25))

    return figure


def make_plots(tweets, box, place):
    """Make plots from the extracted tweet data.

    Args:
        tweets: Iterable of tweets already filtered and within the
            bounding box.
        box = A pair of longitude and latitude pairs, with the southwest
            corner of the bounding box coming first.
        place = String for the place name of the bounding `box`.
    """
    data = list(extract_data(tweets))
    longitude, latitude, time = zip(*data)
    time = [(x.hour + (x.minute / 60)) for x in time]

    map_figure = make_map(longitude, latitude, time, box, place)
    time_histogram = make_time(time)

    plt.show()


if __name__ == '__main__':
    config = get_config()
    path = config.get('plot', 'path')
    fname = config.get('plot', 'archive')
    box = json.loads(config.get('plot', 'box'))
    place = config.get('plot', 'place')

    tweets = parse_archive(os.path.join(path, fname))

    make_plots(tweets, box, place)
