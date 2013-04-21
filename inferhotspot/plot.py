# Copyright (C) 2013 Wesley Baugh
"""Visually display geocded tweets."""
import json
import os

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1 import make_axes_locatable

from config import get_config
import process


def create_box(ax, box):
    """Create a colorbar object.

    Args:
        ax: Axes object to modify.
        box = A pair of longitude and latitude pairs, with the southwest
            corner of the bounding box coming first.
    """
    rect = Rectangle(xy=(box[0], box[1]),
                     width=box[2] - box[0],
                     height=box[3] - box[1],
                     facecolor='none')
    ax.add_patch(rect)


def create_colorbar(ax, mappable, cmap=None):
    """Create a colorbar object.

    Args:
        ax: Axes object to modify.
        mappable: The object to which the colorbar applies.
        cmap: The colormap to be used.

    Returns:
        The colorbar object created.
    """
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad='3%')
    colorbar = ax.figure.colorbar(mappable, cax=cax, cmap=cmap)
    colorbar.solids.set_edgecolor('face')
    # Make colorbar solid.
    # See: http://stackoverflow.com/a/4480124/1988505
    colorbar.set_alpha(1)
    colorbar.draw_all()
    return colorbar


def ax_coord_bounds(ax, longitude, latitude, box):
    """Set the x-axis and y-axis bounds based on longitude and latitude.

    Args:
        ax: Axes object to modify.
        longitude: List of longitude float values of length *N*.
        latitude: List of latitude float values of length *N*.
        box = A pair of longitude and latitude pairs, with the southwest
            corner of the bounding box coming first.
    """
    x_padding = (max(longitude) - min(longitude)) * 0.1
    y_padding = (max(latitude) - min(latitude)) * 0.1
    ax.set_xbound(box[0] - x_padding, box[2] + x_padding)
    ax.set_ybound(box[1] - y_padding, box[3] + y_padding)
    ax.set_aspect('equal')


def make_map(longitude, latitude, time, box, place):
    """Plot geocoded tweets on a scatter plot.

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

    create_box(ax, box)

    scatter = ax.scatter(x=longitude,
                         y=latitude,
                         c=time,
                         cmap=plt.cm.rainbow,
                         s=5,
                         alpha=0.5,
                         lw=0.5)

    colorbar = create_colorbar(ax, scatter, cmap=plt.cm.rainbow)
    colorbar.set_label('Hour (UTC)')
    colorbar.set_ticks(range(24))

    ax_coord_bounds(ax, longitude, latitude, box)

    figure.tight_layout(rect=(0.05, 0.05, 0.95, 0.95))

    return figure


def make_user_map(longitude, latitude, users, box, place):
    """Plot lines for each user using geocoded tweets.

    Args:
        longitude: List of longitude float values of length *N*.
        latitude: List of latitude float values of length *N*.
        users: Dictionary with keys being users and values being a list
            containing the ordered list of longitude-latitude points
            that are associated with that user.
        box = A pair of longitude and latitude pairs, with the southwest
            corner of the bounding box coming first.
        place = String for the place name of the bounding `box`.

    Returns:
        Figure object used to create the plot.
    """
    figure = plt.figure('user-map')
    figure.set_size_inches(12, 9, forward=True)
    figure.set_dpi(100)

    ax = figure.add_subplot(1, 1, 1)
    ax.set_title("Users' Geocoded Tweets in {0}".format(place))
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True)

    create_box(ax, box)

    for user in users:
        x, y = zip(*users[user])
        line, = ax.plot(x,
                        y,
                        linewidth=1,
                        marker='o',
                        markersize=2)
        line.set_alpha(0.2)

    # Display number of unique users.
    x, y = box[0], box[3]  # top-left of box.
    y += (box[3] - box[1]) * .01  # add a little margin
    ax.text(x,
            y,
            'Unique users: {0}'.format(len(users)),
            bbox=dict(facecolor='gray', alpha=0.25))

    ax_coord_bounds(ax, longitude, latitude, box)

    figure.tight_layout(rect=(0.05, 0.05, 0.95, 0.95))

    return figure


def make_user_checkins(users):
    """Plot a histogram of check-ins per user.

    Args:
        users: Dictionary with keys being users and values being a list
            containing the ordered list of longitude-latitude points
            that are associated with that user.

    Returns:
        Figure object used for the histogram.
    """
    figure = plt.figure('user-checkins')
    figure.set_dpi(100)

    ax = figure.add_subplot(1, 1, 1)
    ax.set_title('Check-ins per User')
    ax.set_xlabel('Number of check-ins')
    ax.set_ylabel('Number of users')
    ax.set_yscale('log')
    ax.grid(True)

    user_checkins = []
    for user in users:
        user_checkins.append(len(users[user]))

    n, bins, patches = ax.hist(user_checkins, bins=100)

    return figure


def make_heatmap(longitude, latitude, box, place):
    """Plot geocoded tweets on a heat map.

    Use matplotlib to produce a heat map (hexagonal binning plot) of the
    longitude and latitude data from a collection of tweets.

    Args:
        longitude: List of longitude float values of length *N*.
        latitude: List of latitude float values of length *N*.
        box = A pair of longitude and latitude pairs, with the southwest
            corner of the bounding box coming first.
        place = String for the place name of the bounding `box`.

    Returns:
        Figure object used to create the hexagonal binning plot.
    """
    figure = plt.figure('heatmap')
    figure.set_size_inches(12, 9, forward=True)
    figure.set_dpi(100)

    ax = figure.add_subplot(1, 1, 1)
    ax.set_title('Geocoded Tweets in {0}'.format(place))
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True)

    create_box(ax, box)

    heatmap = ax.hexbin(x=longitude,
                        y=latitude,
                        mincnt=1,
                        gridsize=128,
                        norm=LogNorm(),
                        cmap=plt.cm.rainbow)

    colorbar = create_colorbar(ax, heatmap, cmap=plt.cm.rainbow)
    colorbar.set_label('Number of Tweets')

    ax_coord_bounds(ax, longitude, latitude, box)

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
    print 'Extracting tweets ...',
    data = list(process.extract_data(tweets))
    print 'DONE'

    print 'Extracting census blocks ...',
    census_path = config.get('census', 'path')
    census_blocks = config.get('census', 'blocks')
    blocks = process.extract_blocks(os.path.join(census_path, census_blocks))
    print 'DONE'

    print 'Processing data ...',
    longitude, latitude, time, users = process.process_data(data)
    print 'DONE'

    print 'Computing census block interactions ...',
    interactions = process.compute_block_interactions(users, blocks)
    print 'DONE'

    print 'Saving census block interactions ...',
    with open('census-block-interactions.tsv', mode='w') as f:
        process.dump_interactions(interactions, f)
    print 'DONE'

    print 'Making figures ...',
    figures = []
    figures.append(make_map(longitude, latitude, time, box, place))
    figures.append(make_user_map(longitude, latitude, users, box, place))
    figures.append(make_user_checkins(users))
    figures.append(make_heatmap(longitude, latitude, box, place))
    figures.append(make_time(time))
    print 'DONE'

    print 'Saving figures ...',
    for figure in figures:
        figure.savefig('{0}.png'.format(figure.get_label()),
                       bbox_inches='tight',
                       pad_inches=0.1)
    print 'DONE'

    plt.show()


if __name__ == '__main__':
    config = get_config()
    path = config.get('plot', 'path')
    fname = config.get('plot', 'archive')
    box = json.loads(config.get('place', 'box'))
    place = config.get('place', 'name')

    tweets = process.parse_archive(os.path.join(path, fname))

    make_plots(tweets, box, place)
