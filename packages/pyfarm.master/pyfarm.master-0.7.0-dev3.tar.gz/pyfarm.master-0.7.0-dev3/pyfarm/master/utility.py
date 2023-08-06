# No shebang line, this module is meant to be imported
#
# Copyright 2013 Oliver Palmer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Utility
=======

General utility which are not view or tool specific
"""

try:
    from json import dumps as _dumps
except ImportError:
    from simplejson import dumps as _dumps

from sqlalchemy.schema import Table
from werkzeug.datastructures import ImmutableDict
from flask import Response
from pyfarm.master.application import app

PRETTY_JSON = app.config["PYFARM_JSON_PRETTY"]
COLUMN_CACHE = {}


def dumps(*args, **kwargs):
    """
    Wrapper around :func:`._dumps` which does some work to respect any
    application settings.
    """
    if PRETTY_JSON:
        kwargs.setdefault("indent", 4)
    return _dumps(*args, **kwargs)


class JSONResponse(Response):
    """
    Wrapper around :class:`.Response` which will set the proper content type
    and serialize any input
    """
    content_type = "application/json"

    def __init__(self, *args, **kwargs):
        # retrieve, reduce, then serialize the data to json
        data = kwargs.get("response", args[0])
        if isinstance(data, ReducibleDictionary):
            data.reduce()
        data = dumps(data)

        if "response" in kwargs:
            kwargs["response"] = data

        elif len(args) == 1:
            args = (data, )

        super(JSONResponse, self).__init__(*args, **kwargs)


class ReducibleDictionary(dict):
    """
    Adds a :meth:`.reduce` method to :class:`dict` class
    which will remove empty values from a dictionary.

    >>> data = ReducibleDictionary({"foo": True, "bar": None})
    >>> data.reduce()
    >>> print data
    {'foo': True}
    """
    def reduce(self):
        for key, value in self.copy().iteritems():
            if value is None:
                self.pop(key)


class TemplateDictionary(ImmutableDict):
    """
    Simple dictionary which subclasses werkzeug's :class:`.ImmutableDict`
    but allows for new instanced to be produced using :meth:`.__call__`.

    >>> template = TemplateDictionary({"foo": None})
    >>> data = template()
    >>> data["foo"] = True
    >>> data["bar"] = False
    >>> print data, template
    {'foo': True, 'bar': False} TemplateDictionary({'foo': None})

    This class is mainly meant for simple REST responses, other considerations
    should be taken for more complex structures.
    """
    def __call__(self, reducible=True):
        class_ = ReducibleDictionary if reducible else dict
        return class_(self.copy())
