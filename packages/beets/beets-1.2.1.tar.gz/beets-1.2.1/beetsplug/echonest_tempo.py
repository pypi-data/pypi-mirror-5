# This file is part of beets.
# Copyright 2013, David Brenner <david.a.brenner gmail>
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

"""Gets tempo (bpm) for imported music from the EchoNest API. Requires
the pyechonest library (https://github.com/echonest/pyechonest).
"""
import time
import logging
from beets.plugins import BeetsPlugin
from beets import ui
from beets import config
import pyechonest.config
import pyechonest.song
import socket

# Global logger.
log = logging.getLogger('beets')

RETRY_INTERVAL = 10  # Seconds.
RETRIES = 10

def fetch_item_tempo(lib, loglevel, item, write):
    """Fetch and store tempo for a single item. If ``write``, then the
    tempo will also be written to the file itself in the bpm field. The 
    ``loglevel`` parameter controls the visibility of the function's 
    status log messages.
    """
    # Skip if the item already has the tempo field.
    if item.bpm:
        log.log(loglevel, u'bpm already present: %s - %s' %
                          (item.artist, item.title))
        return

    # Fetch tempo.
    tempo = get_tempo(item.artist, item.title)
    if not tempo:
        log.log(loglevel, u'tempo not found: %s - %s' %
                          (item.artist, item.title))
        return

    log.log(loglevel, u'fetched tempo: %s - %s' %
                      (item.artist, item.title))
    item.bpm = tempo
    if write:
        item.write()
    lib.store(item)

def get_tempo(artist, title):
    """Get the tempo for a song."""
    # We must have sufficient metadata for the lookup. Otherwise the API
    # will just complain.
    artist = artist.replace(u'\n', u' ').strip()
    title = title.replace(u'\n', u' ').strip()
    if not artist or not title:
        return None

    for i in range(RETRIES):
        try:
            # Unfortunately, all we can do is search by artist and title.
            # EchoNest supports foreign ids from MusicBrainz, but currently
            # only for artists, not individual tracks/recordings.
            results = pyechonest.song.search(
                artist=artist, title=title, results=1, buckets=['audio_summary']
            )
        except pyechonest.util.EchoNestAPIError as e:
            if e.code == 3:
                # Wait and try again.
                time.sleep(RETRY_INTERVAL)
            else:
                log.warn(u'echonest_tempo: {0}'.format(e.args[0][0]))
                return None
        except (pyechonest.util.EchoNestIOError, socket.error) as e:
            log.debug(u'echonest_tempo: IO error: {0}'.format(e))
            time.sleep(RETRY_INTERVAL)
        else:
            break
    else:
        # If we exited the loop without breaking, then we used up all
        # our allotted retries.
        log.debug(u'echonest_tempo: exceeded retries')
        return None

    if len(results) > 0:
        return results[0].audio_summary['tempo']
    else:
        return None

class EchoNestTempoPlugin(BeetsPlugin):
    def __init__(self):
        super(EchoNestTempoPlugin, self).__init__()
        self.import_stages = [self.imported]
        self.config.add({
            'apikey': u'NY2KTZHQ0QDSHBAP6',
            'auto': True,
        })

        pyechonest.config.ECHO_NEST_API_KEY = \
                self.config['apikey'].get(unicode)

    def commands(self):
        cmd = ui.Subcommand('tempo', help='fetch song tempo (bpm)')
        cmd.parser.add_option('-p', '--print', dest='printbpm',
                              action='store_true', default=False,
                              help='print tempo (bpm) to console')
        def func(lib, opts, args):
            # The "write to files" option corresponds to the
            # import_write config value.
            write = config['import']['write'].get(bool)

            for item in lib.items(ui.decargs(args)):
                fetch_item_tempo(lib, logging.INFO, item, write)
                if opts.printbpm and item.bpm:
                    ui.print_('{0} BPM'.format(item.bpm))
        cmd.func = func
        return [cmd]

    # Auto-fetch tempo on import.
    def imported(self, config, task):
        if self.config['auto']:
            for item in task.imported_items():
                fetch_item_tempo(config.lib, logging.DEBUG, item, False)
