# Copyright (C) 2013 Wesley Baugh
"""Web interface for displaying hotspot related information."""
from __future__ import division
import colorsys
import copy
import json
import logging
import os
import socket
import subprocess

import shapely
import tornado.ioloop
import tornado.web
import tornado.httpserver

import process
from config import get_config


class MainHandler(tornado.web.RequestHandler):
    """Handles requests for the query input page."""

    def initialize(self):
        self.git_version = self.application.settings.get('git_version')
        self.box = self.application.settings.get('box')
        self.blocks = self.application.settings.get('blocks')
        self.interactions = self.application.settings.get('interactions')

    def head(self, *args):
        """Handle HEAD requests by sending an identical GET response."""
        self.get(*args)

    def get(self):
        """Renders the query input page."""
        self.render('index.html',
                    box=self.box,
                    blocks=self.blocks,
                    git_version=self.git_version)


class InteractionHandler(MainHandler):
    """Handles the census block interaction query."""

    def get(self):
        """Renders the census block interactions result page.

        GET Parameters:
            latitude: Float of the latitude coordinate.
            longitude: Float of the longitude coordinate.
            edges: String, either 'directed' or 'undirected', indicating
                whether order of interactions matters.
        """
        latitude = float(self.get_argument('latitude'))
        longitude = float(self.get_argument('longitude'))
        edges = self.get_argument('edges')
        if edges == 'directed':
            directed = True
        elif edges == 'undirected':
            directed = False
        else:
            raise tornado.web.HTTPError(400)  # 400 Bad Request

        point = shapely.geometry.Point(longitude, latitude)
        block_id = process.point_to_block(point, self.blocks)
        if block_id in self.interactions:
            interactions = copy.deepcopy(self.interactions[block_id])
            if not directed:
                self._add_undirected(block_id, interactions)
            interactions = self._normalized_interaction_counts(interactions)
            blocks = self._prepare_blocks(interactions)
        else:
            blocks = []

        self.render('interaction.html',
                    box=self.box,
                    latitude=latitude,
                    longitude=longitude,
                    directed=directed,
                    source_id=block_id,
                    blocks=blocks,
                    color_code=self._color_code,
                    git_version=self.git_version)

    def _add_undirected(self, block_id, interactions):
        """Add counts for the reverse interaction edges.

        Args:
            block_id: The source block ID.
            interactions: Dictionary of the directed interactions for
                the `block_id`.

        Returns:
            The `interactions` dictionary updated with reverse counts.
        """
        for target_id in self.interactions:
            if (block_id not in self.interactions[target_id] or
                    target_id == block_id):
                continue
            if target_id not in interactions:
                interactions[target_id] = 0
            interactions[target_id] += self.interactions[target_id][block_id]

    def _normalized_interaction_counts(self, interactions):
        """Normalize the interaction value to between 0 and 1.

        Args:
            interactions: Dictionary of blocks with interaction value.

        Returns:
            Original dictionary with normalized values (0 <= x <= 1).
        """
        maximum = max(interactions.values())
        for block in interactions:
            interactions[block] /= maximum
        return interactions

    def _prepare_blocks(self, interactions):
        """Use interactions to prepare census blocks to be rendered.

        Args:
            interactions: Dictionary of blocks with interaction value.

        Returns:
            List of tuples: (target_block_id, shape, weight).
        """
        blocks = []
        for target_block_id in interactions:
            shape = self.blocks[target_block_id]
            weight = interactions[target_block_id]
            blocks.append((target_block_id, shape, weight))
        return blocks

    def _color_code(self, weight):
        """Converts float [0.0 - 1.0] to HTML color code."""
        weight = 1 - weight
        rgb = colorsys.hsv_to_rgb(weight / 2, 1, 0.75)
        code = '#' + ''.join([hex(int(x * 256))[2:].zfill(2) for x in rgb])
        return code


def start_server(config, blocks, interactions, git_version):
    application = tornado.web.Application(
        [(r'/', MainHandler),
         (r'/interaction/blocks', InteractionHandler)],
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        gzip=config.getboolean('web', 'gzip'),
        debug=config.getboolean('web', 'debug'),
        box=json.loads(config.get('place', 'box')),
        blocks=blocks,
        interactions=interactions,
        git_version=git_version)
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(config.getint('web', 'port'))

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass


def get_git_version():
    """Get the SHA of the current Git commit.

    Returns:
        String tuple of the `git_version` as returned by `git describe`,
        and the `git_commit`, which is the full SHA of the last commit.
        If there was an error retrieving the values then (None, None) is
        returned.
    """
    try:
        git_commit = subprocess.check_output([
            'git', 'rev-parse', '--verify', 'HEAD']).rstrip()
        git_version = subprocess.check_output(['git',
                                               'describe',
                                               '--always']).rstrip()
    except OSError, subprocess.CalledProcessError:
        git_version, git_commit = None, None
    return git_version, git_commit


def setup_logging(config):
    if config.getboolean('web', 'debug'):
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logger = logging.getLogger('')  # Root logger.
    logger.setLevel(log_level)

    console = logging.StreamHandler()
    console.setLevel(log_level)
    console_formatter = logging.Formatter(
        fmt='%(asctime)s|%(levelname)s|%(name)s|%(message)s',
        datefmt='%m-%d %H:%M:%S')
    console.setFormatter(console_formatter)
    logger.addHandler(console)

    web_query_log = config.get('web', 'web_query_log')
    # Add the system's hostname before the file extension.
    web_query_log = (web_query_log[:-3] + socket.gethostname() +
                     web_query_log[-4:])

    file_handler = logging.FileHandler(web_query_log)
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        fmt='%(asctime)s.%(msecs)d\t%(levelname)s\t%(name)s\t%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)


if __name__ == '__main__':
    config = get_config()

    setup_logging(config)

    logger = logging.getLogger('ui.web')

    git_version, git_commit = get_git_version()
    if git_version:
        logger.info('Version: {0} ({1})'.format(git_version, git_commit))
    else:
        logger.warning('Could not detect current Git commit.')

    print 'Extracting census blocks ...',
    census_path = config.get('census', 'path')
    census_blocks = config.get('census', 'blocks')
    blocks = process.extract_blocks(os.path.join(census_path, census_blocks))
    print 'DONE'

    print 'Loading census block interactions ...',
    with open('census-block-interactions.tsv') as f:
        interactions = process.load_interactions(f)
    print 'DONE'

    logger.info('Starting web server on port {}'.format(config.getint('web',
                                                                      'port')))
    start_server(config, blocks, interactions, (git_version, git_commit))
