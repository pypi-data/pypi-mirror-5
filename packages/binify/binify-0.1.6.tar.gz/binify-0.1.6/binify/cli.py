#!/usr/bin/env python

import argparse

class CLI(object):
    """
    Handles command-line interface options
    """

    def parse_arguments(self, args=None):
        """
        Implement command-line arguments
        """
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('infile', help='A point shapefile to create \
                bins from.')
        self.parser.add_argument('outfile', help='A shapefile to write to. \
                Will be created if it does not exist.')
        self.parser.add_argument('-n', '--num-across', type=int,
                dest='num_across', default=10, help='Number of hexagons for \
                the grid to have across (approximate)')
        self.parser.add_argument('-E', '--extent', nargs=4, type=float, \
                metavar=('EAST_LNG', 'WEST_LNG', 'SOUTH_LAT', 'NORTH_LAT'),
                help='Use a custom extent.')
        self.parser.add_argument('-e', '--exclude-empty', \
                dest='exclude_empty', action='store_true', \
                help='Exclude shapes that end up binning zero points.')
        self.parser.add_argument('-o', '--overwrite', action='store_true', \
                help='Overwrite output file.')
        self.parser.add_argument('--ignore-type', action='store_true', \
                dest='ignore_type', help='Ignore the geometry type of the \
                input shapefile.')
        self.parser.add_argument('--suppress-output', action='store_true', \
                dest='suppress_output', help='Supress console output \
                (excluding any warnings).')
        return self.parser.parse_args(args)

