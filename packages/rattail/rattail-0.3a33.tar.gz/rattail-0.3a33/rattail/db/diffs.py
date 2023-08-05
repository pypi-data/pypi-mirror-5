#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``rattail.db.diffs`` -- Data Diffs
"""

from rattail.db import Session
from rattail.db.sync import get_sync_engines

from sqlalchemy.orm import class_mapper


def instances_differ(local_instance, remote_instance, mapper):
    """
    Perform "shallow" comparison of data between two model instances.
    """

    for key in mapper.column_attrs.keys():
        if getattr(local_instance, key) != getattr(remote_instance, key):
            return True

    return False


def find_diffs(local_session, remote_session, class_, progress=None):
    """
    Find differences between local and remote database, for a given model.
    """

    diffs = {}
    local_query = local_session.query(class_)
    remote_query = remote_session.query(class_)
    mapper = class_mapper(class_)

    prog = None
    if progress:
        prog = progress("Finding diffs for {0}".format(class_.__name__), local_query.count())

    for i, local_instance in enumerate(local_query, 1):
        remote_instance = remote_query.get(local_instance.uuid)

        if remote_instance is None:
            diffs.setdefault('missing', [])
            diffs['missing'].append(local_instance)

        elif instances_differ(local_instance, remote_instance, mapper):
            diffs.setdefault('differs', [])
            diffs['differs'].append((local_instance, remote_instance))

        if prog:
            prog.update(i)

    if prog:
        prog.destroy()
    return diffs
