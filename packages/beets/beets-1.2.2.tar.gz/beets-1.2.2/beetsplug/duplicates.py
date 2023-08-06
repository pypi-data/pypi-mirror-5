# This file is part of beets.
# Copyright 2013, Pedro Silva.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""List duplicate tracks or albums.
"""
import logging

from beets.plugins import BeetsPlugin
from beets.ui import decargs, print_obj, Subcommand

PLUGIN = 'duplicates'
log = logging.getLogger('beets')


def _group_by_id(objs):
    """Return a dictionary whose keys are MBIDs and whose values are
    lists of objects (Albums or Items) with that ID.
    """
    import collections
    counts = collections.defaultdict(list)
    for obj in objs:
        mbid = getattr(obj, 'mb_trackid', obj.mb_albumid)
        counts[mbid].append(obj)
    return counts


def _duplicates(objs, full):
    """Generate triples of MBIDs, duplicate counts, and constituent
    objects.
    """
    offset = 0 if full else 1
    for mbid, objs in _group_by_id(objs).iteritems():
        if len(objs) > 1:
            yield (mbid, len(objs) - offset, objs[offset:])


class DuplicatesPlugin(BeetsPlugin):
    """List duplicate tracks or albums
    """
    def __init__(self):
        super(DuplicatesPlugin, self).__init__()

        self.config.add({'format': ''})
        self.config.add({'count': False})
        self.config.add({'album': False})
        self.config.add({'full': False})

        self._command = Subcommand('duplicates',
                                   help=__doc__,
                                   aliases=['dup'])

        self._command.parser.add_option('-f', '--format', dest='format',
                                        action='store', type='string',
                                        help='print with custom FORMAT',
                                        metavar='FORMAT')

        self._command.parser.add_option('-c', '--count', dest='count',
                                        action='store_true',
                                        help='count duplicate tracks or\
                                        albums')

        self._command.parser.add_option('-a', '--album', dest='album',
                                        action='store_true',
                                        help='show duplicate albums instead\
                                        of tracks')

        self._command.parser.add_option('-F', '--full', dest='full',
                                        action='store_true',
                                        help='show all versions of duplicate\
                                        tracks or albums')

    def commands(self):
        def _dup(lib, opts, args):
            self.config.set_args(opts)
            fmt = self.config['format'].get()
            count = self.config['count'].get()
            album = self.config['album'].get()
            full = self.config['full'].get()

            if album:
                items = lib.albums(decargs(args))
            else:
                items = lib.items(decargs(args))

            # Default format string for count mode.
            if count and not fmt:
                if album:
                    fmt = '$albumartist - $album'
                else:
                    fmt = '$albumartist - $album - $title'
                fmt += ': {0}'

            for obj_id, obj_count, objs in _duplicates(items, full):
                if obj_id:  # Skip empty IDs.
                    for o in objs:
                        print_obj(o, lib, fmt=fmt.format(obj_count))

        self._command.func = _dup
        return [self._command]
