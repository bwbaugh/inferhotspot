# Copyright (C) 2013 Wesley Baugh
"""Web interface for displaying hotspot related information."""
import os

import tornado.ioloop
import tornado.web
import tornado.httpserver

import process
from config import get_config


class MainHandler(tornado.web.RequestHandler):
    """Handles requests for the query input page."""

    def initialize(self):
        self.git_version = (None, None)

    def head(self, *args):
        """Handle HEAD requests by sending an identical GET response."""
        self.get(*args)

    def get(self):
        """Renders the query input page."""
        self.render('index.html', git_version=self.git_version)


def start_server(config, interactions):
    application = tornado.web.Application(
        [(r'/', MainHandler)],
        template_path=os.path.join(os.path.dirname(__file__), 'templates'),
        static_path=os.path.join(os.path.dirname(__file__), 'static'),
        gzip=config.getboolean('web', 'gzip'),
        debug=config.getboolean('web', 'debug'),
        interactions=interactions)
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(config.getint('web', 'port'))

    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    config = get_config()
    print 'Loading census block interactions ...',
    with open('census-block-interactions.tsv') as f:
        interactions = process.load_interactions(f)
    print 'DONE'
    print 'Starting web server (port {0}).'.format(config.getint('web', 'port'))
    start_server(config, interactions)
