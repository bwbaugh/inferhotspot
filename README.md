inferhotspot
============

Infer information about local hotspots.

Plot examples
-------------

The examples below were created using a collection of 69,150 tweets
within Denton County from *Tue Feb 12* to *Mon Mar 18*. The data was
collected using [bwbaugh/twitter-corpus][].

### Map

![map][]

### Heat map

![heat map][]

### Time

![time][]

Usage
-----

Run using the command: `python -m inferhotspot.plot`

The first time you run the script it will create a configuration file
named `inferhotspot.ini`, and you will be asked to edit it. There you
will need to indicate the path and filename of the bz2-archive that
contains the already filtered geocoded tweets. Once updated, run the
command again to generate the plots, which will also display an
interactive plot and saves each figure to the current working directory.

If the data hasn't been preprocessed to include only those tweets that
are geocded with using a coordinates-point---and that point falls within
the bounding box---then you will need to use the `filter.py` script to
preprocess your data first.

Installation
------------

You do not need to install the package in order to use it, however if
you choose to install then use one of the options below. Otherwise your
current working directory must be the parent of the *inferhotspot*
package.

### Using distribute

#### Standard install

`python setup.py install`

#### Development install

To install in *development* mode, which creates a symlink to the current
directory so that the source can be modified or updated in-place, use:

`python setup.py develop`

And to remove the symlink:

`python setup.py develop -u`

### Using pip

`pip install .`

To uninstall:

`pip uninstall inferhotspot`

  [bwbaugh/twitter-corpus]: https://github.com/bwbaugh/twitter-corpus
  [map]: http://s23.postimg.org/9j63tpl7v/map.png
  [heat map]: http://s8.postimg.org/48vg5s1ed/heatmap.png
  [time]: http://s24.postimg.org/sluzx4jhx/time.png
