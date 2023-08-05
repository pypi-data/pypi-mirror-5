# -*- coding: utf-8 -*-
#
# Copyright 2012 Manuel Stocker <mensi@mensi.ch>
#
# This file is part of Cydra.
#
# Cydra is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cydra is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cydra.  If not, see http://www.gnu.org/licenses

# This file contains code from trac, see trac/loader.py

import os.path
import pkg_resources
from pkg_resources import working_set, DistributionNotFound, VersionConflict, UnknownExtra
import sys

__all__ = ['load_components']

import logging
logger = logging.getLogger(__name__)

def load_eggs(ch, entry_point, search_path, only_enabled=True):
    """Loader that loads any eggs on the search path and `sys.path`."""
    
    logger.debug("Loading eggs...")
    
    # Note that the following doesn't seem to support unicode search_path
    distributions, errors = working_set.find_plugins(
        pkg_resources.Environment(search_path)
    )

    logger.debug("Found distributions: %s", str(distributions))
    for dist in distributions:
        if dist not in working_set:
            logger.debug('Adding plugin %s from %s', dist, dist.location)
            working_set.add(dist)

    for dist, e in errors.iteritems():
        logger.error("Error in distribution %s: %s", str(dist), str(e))

    for entry in sorted(working_set.iter_entry_points(entry_point),
                        key=lambda entry: entry.name):
        logger.debug('Loading %s from %s', entry.name, entry.dist.location)
        
        # If we are only loading enabled components, consult the config and skip if
        # not found
        if only_enabled and not any(map(lambda x: x.startswith(entry.name), ch.config.get('components', {}))):
            logger.debug('Skipping component %s since it is not enabled' % entry.name)
            continue

        try:
            entry.load(require=True)
        except ImportError, e:
            logger.warn("Loading %s failed, probably because of unmet dependencies: %s", entry.name, str(e))
        except Exception, e:
            logger.exception("Error loading: %s", entry)
        else:
            logger.debug("Loaded module %s from %s", entry.module_name, entry.dist.location)


def load_components(ch, entrypoint='cydra.plugins', search_path=None, loaders=[load_eggs]):
    """Load all plugin components found on the given search path."""
    search_path = search_path or []

    for loadfunc in loaders:
        loadfunc(ch, entrypoint, search_path, entrypoint != 'cydra.config')
