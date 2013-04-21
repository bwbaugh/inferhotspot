# Copyright (C) 2013 Wesley Baugh
"""Configuration file access and settings."""
import errno
import os
import sys
import ConfigParser


CONFIG_FNAME = 'inferhotspot.ini'


def create_default_config():
    """Create a default config file.

    Returns:
        An instance of ConfigParser populated with the default settings.
    """
    config = ConfigParser.SafeConfigParser()

    config.add_section('filter')
    config.set('filter', 'process_directory', 'PATH/TO/TWEET/ARCHIVE/FILES')
    config.set('filter', 'output', 'tweet-loc_denton-filtered.json')

    config.add_section('place')
    config.set('place', 'box', '[-97.399786, 32.989759, -96.834612, 33.413174]')
    config.set('place', 'name', 'Denton County')

    config.add_section('census')
    config.set('census', 'path', 'PATH/TO/CENSUS/DATA')
    config.set('census', 'blocks', 'census-blocks.tsv.bz2')

    config.add_section('plot')
    config.set('plot', 'path', 'PATH/TO/TWEET/ARCHIVE')
    config.set('plot', 'archive', 'tweet-loc_denton-filtered.json.bz2')

    return config


def get_config(fname=CONFIG_FNAME, create=True, exit=True):
    """Reads a configuration file from disk.

    Args:
        create: Boolean if the configuration file should be created if
            it does not already exist. (Default: True)
        exit: Boolean if the program should exit if the configuration
            file did not originally exist.

    Returns:
        An instance of ConfigParser. If the config file exists, then it
        is used for populating the settings. Otherwise, if `create` is
        True (and exit is False) then the settings will be populated
        with the default. Returns None if `create` is False.

    Raises:
        SystemExit if the configuration file does not exist and `create`
        is False.
    """
    config = ConfigParser.SafeConfigParser()
    try:
        with open(fname) as f:
            config.readfp(f)  # pragma: no branch
    except IOError as e:
        if e.errno != errno.ENOENT:
            raise  # pragma: no cover
        if create:
            print 'Configuration file not found! Creating one...'
            config = create_default_config()
            with open(fname, mode='w') as f:
                config.write(f)
            msg = 'Please edit the config file named "{0}" in directory "{1}"'
        else:
            msg = 'Configuration file "{0}" not found in directory "{1}"'
        print msg.format(CONFIG_FNAME, os.getcwd())
        if exit:
            sys.exit(errno.ENOENT)
        else:
            if not create:
                return None
    return config
