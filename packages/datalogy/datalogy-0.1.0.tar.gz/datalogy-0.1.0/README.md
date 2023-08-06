# datalogy

[![Build Status](https://secure.travis-ci.org/michaeljoseph/datalogy.png)](http://travis-ci.org/michaeljoseph/datalogy)
[![Stories in Ready](https://badge.waffle.io/michaeljoseph/datalogy.png?label=ready)](https://waffle.io/michaeljoseph/datalogy)
[![pypi version](https://badge.fury.io/py/datalogy.png)](http://badge.fury.io/py/datalogy)
[![# of downloads](https://pypip.in/d/datalogy/badge.png)](https://crate.io/packages/datalogy?version=latest)
[![code coverage](https://coveralls.io/repos/michaeljoseph/datalogy/badge.png?branch=master)](https://coveralls.io/r/michaeljoseph/datalogy?branch=master)

![datalogy](https://github.com/michaeljoseph/datalogy/raw/master/resources/datalogy.jpg)


A collection of python tools that facilitate the obtaining, scrubbing
and exploring of data.

## scrape

Extract HTML elements using an XPath query or CSS3 selector.

### Example usage
 
     curl -s http://en.wikipedia.org/wiki/List_of_sovereign_states | \
             scrape -be 'table.wikitable > tr > td > b > a'


## random-sample

Output lines from stdin to stdout with a given probability, for a given 
duration, and with a given delay between lines.

### Example usage

    seq 100 | random-sample -r 20% -d 1000

## Testing

Install development requirements:

    pip install -r requirements.txt

Run the tests with:

    nosetests

Lint the project with:

    flake8 datalogy tests

## API documentation

To generate the documentation:

    cd docs && PYTHONPATH=.. make singlehtml

