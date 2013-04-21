# Copyright (C) 2013 Wesley Baugh
"""Web interface for displaying hotspot related information."""
import os
import subprocess

import tornado.ioloop
import tornado.web
import tornado.httpserver

import process
from config import get_config


class MainHandler(tornado.web.RequestHandler):
    """Handles requests for the query input page."""

    def initialize(self):
        self.git_version = self.application.settings.get('git_version')
        self.blocks = self.application.settings.get('blocks')
        self.interactions = self.application.settings.get('interactions')

    def head(self, *args):
        """Handle HEAD requests by sending an identical GET response."""
        self.get(*args)

    def get(self):
        """Renders the query input page."""
        self.render('index.html',
                    blocks=self.blocks,
                    git_version=self.git_version)


def start_server(config, blocks, interactions, git_version):
    application = tornado.web.Application(
        [(r'/', MainHandler)],
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        gzip=config.getboolean('web', 'gzip'),
        debug=config.getboolean('web', 'debug'),
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


if __name__ == '__main__':
    config = get_config()
    git_version, git_commit = get_git_version()
    if git_version:
        print 'Version: {0} ({1})'.format(git_version, git_commit)
    else:
        print 'Could not detect current Git commit.'

    print 'Extracting census blocks ...',
    census_path = config.get('census', 'path')
    census_blocks = config.get('census', 'blocks')
    blocks = process.extract_blocks(os.path.join(census_path, census_blocks))
    print 'DONE'

    print 'Loading census block interactions ...',
    with open('census-block-interactions.tsv') as f:
        interactions = process.load_interactions(f)
    print 'DONE'

    print 'Starting web server (port {0}).'.format(config.getint('web', 'port'))
    start_server(config, blocks, interactions, (git_version, git_commit))
