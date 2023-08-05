"""
Fast lxml-based XML plist reader/editor.
"""

import iso8601
import lxml.etree

__all__ = ['parse', 'factory', 'dumps']


def _elem(tag, text=None):
    """Create an lxml.xml.Element.
    """
    elem = lxml.etree.Element(tag)
    if text is not None:
        elem.text = text
    return elem


class PListArray(object):
    def __init__(self, elem):
        self.elem = elem

    def __len__(self):
        return len(self.elem)

    def __getitem__(self, idx):
        return factory(self.elem[idx])

    def __setitem__(self, idx, value):
        self.elem[idx] = collapse(value)

    def __iter__(self):
        return (factory(e) for e in self.elem)


class PListDict(object):
    def __init__(self, elem):
        self.elem = elem

    def __len__(self):
        return len(self.elem) / 2

    def _findValue(self, key):
        for child in self.elem:
            if child.tag == 'key' and child.text == key:
                return child.getnext()

    def __getitem__(self, key):
        elem = self._findValue(unicode(key))
        if elem is None:
            raise KeyError(key)
        return factory(elem)

    def __setitem__(self, key, value):
        elem = self._findValue(key)
        if elem:
            self.elem.remove(elem.getprevious())
            self.elem.remove(elem)
        collapsed = collapse(value)
        self.elem.append(_elem('key', unicode(key)))
        self.elem.append(collapsed)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __iter__(self):
        return (e.text for e in self.elem.findall('./key'))
    iterkeys = __iter__

    def keys(self):
        return list(self)

    def itervalues(self):
        return (factory(e) for e in self.elem if e.tag != 'key')

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        it = iter(self.elem)
        return ((elem.text, factory(it.next())) for elem in it)


def collapse(v):
    if isinstance(v, unicode):
        return _elem('string', v)
    elif isinstance(v, float):
        return _elem('real', unicode(v))
    elif isinstance(v, (int, long)):
        return _elem('integer', unicode(v))
    elif isinstance(v, datetime.datetime):
        return _elem('date', v.isoformat())
    elif isinstance(v, bool):
        return _elem(unicode(v).lower(), None)
    elif isinstance(v, str):
        return _elem('data', v.encode('base64'))
    elif isinstance(v, (list, PListArray)):
        parent = _elem('array')
        for subv in v:
            parent.append(collapse(subv))
        return parent
    elif isinstance(v, (dict, PListDict)):
        parent = _elem('dict')
        for key, value in v.iteritems():
            parent.append(_elem('key', unicode(key)))
            parent.append(collapse(value))
        return parent
    else:
        raise TypeError('%r is not supported.' % (type(v),))


TYPES = {
    'string':   lambda elem: elem.text,
    'real':     lambda elem: float(elem.text),
    'integer':  lambda elem: int(elem.text),
    'date':     lambda elem: iso8601.parse_date(elem.text),
    'true':     lambda elem: True,
    'false':    lambda elem: False,
    'data':     lambda elem: elem.text.decode('base64'),
    'array':    PListArray,
    'dict':     PListDict
}


def factory(elem):
    """Given a PList value element, return a Python representation of its
    value."""
    return TYPES[elem.tag](elem)


def parse(fp):
    root = lxml.etree.parse(fp).getroot()
    if root.tag != 'plist':
        raise ValueError('root element is not a <plist>')
    return factory(root[0])


def dumps(obj):
    return lxml.etree.tostring(obj.elem.getroottree().getroot(),
                               encoding='UTF-8')
