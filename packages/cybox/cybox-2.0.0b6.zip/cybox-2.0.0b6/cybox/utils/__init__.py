# Copyright (c) 2013, The MITRE Corporation. All rights reserved.
# See LICENSE.txt for complete terms.

"""Common utility methods"""

from .caches import *
from .idgen import *
from .nsparser import *

import xml.sax.saxutils


def get_class_for_object_type(object_type):
    return META.get_class_for_object_type(object_type)


ESCAPE_DICT = {',': '&comma;'}
UNESCAPE_DICT = {'&comma;': ','}


def denormalize_from_xml(value):
    # This is probably not necessary since the parser will have removed
    # the CDATA already.
    value = unwrap_cdata(value)

    if ',' in value:
        return [unescape(x).strip() for x in value.split(',')]
    else:
        return unescape(value)


def normalize_to_xml(value):
    if isinstance(value, list):
        value = ",".join([escape(x) for x in value])
    else:
        value = escape(unicode(value))

    if '&comma;' in value:
        value = wrap_cdata(value)
    return value


def escape(value):
    return xml.sax.saxutils.escape(value, ESCAPE_DICT)


def unescape(value):
    return xml.sax.saxutils.unescape(value, UNESCAPE_DICT)


def wrap_cdata(value):
    return "<![CDATA[" + value + "]]>"


def unwrap_cdata(value):
    """Remove CDATA wrapping from `value` if present"""
    if value.startswith("<![CDATA[") and value.endswith("]]>"):
        return value[9:-3]
    else:
        return value


def test_value(value):
    """
    Test if an input string value is not None and has a length grater than 0 or
    if a dictionary contains a "value" key whose value is not None and has
    a length greater than 0.

    We explicitly want to return True even if the value is False or 0, since
    some parts of the standards are boolean or allow a 0 value, and we want to
    distinguish the case where the "value" key is omitted entirely.
    """
    if isinstance(value, dict):
        v = value.get('value', None)
    elif isinstance(value, str):
        v = value
    elif isinstance(value, unicode):
        v = value
    elif isinstance(value, int):
        v = value
    elif isinstance(value, float):
        v = value
    else:
        v = None
    return (v is not None) and (len(str(v)) > 0)
