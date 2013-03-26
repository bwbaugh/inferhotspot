inferhotspot
============

Infer information about local hotspots.

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

  [bwbaugh/twitter-corpus]: https://github.com/bwbaugh/twitter-corpus
  [map]: http://s23.postimg.org/9j63tpl7v/map.png
  [heat map]: http://s8.postimg.org/48vg5s1ed/heatmap.png
  [time]: http://s24.postimg.org/sluzx4jhx/time.png
