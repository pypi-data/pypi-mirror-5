# -*- coding: utf-8 -*-
import datetime
from decimal import Decimal
import re
import types
from xml.sax.saxutils import quoteattr

try:
    from markupsafe import Markup
except ImportError:
    try:
        from jinja2 import Markup
    except ImportError:
        Markup = unicode


class FakeMultiDict(dict):
    """Adds a fake `getlist` method to a regular dict; or acts as a proxy to
    Webob's MultiDict `getall` method. 
    """
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError, error:
            raise AttributeError(error)

    def getlist(self, name):
        if hasattr(self, 'getall'):
            return self.getall(name)
        value = self.get(name)
        if value is None:
            return []
        return [value]



def get_html_attrs(kwargs=None):
    """Generate HTML attributes from the provided keyword arguments.

    The output value is sorted by the passed keys, to provide consistent
    output.  Because of the frequent use of the normally reserved keyword
    `class`, `classes` is used instead. Also, all underscores are translated
    to regular dashes.

    Set any property with a `True` value.

    >>> _get_html_attrs({'id': 'text1', 'classes': 'myclass',
        'data_id': 1, 'checked': True})
    u'class="myclass" data-id="1" id="text1" checked'

    """
    kwargs = kwargs or {}
    attrs = []
    props = []

    classes = kwargs.get('classes', '').strip()
    if classes:
        classes = ' '.join(re.split(r'\s+', classes))
        classes = to_unicode(quoteattr(classes))
        attrs.append('class=%s' % classes)
    try:
        del kwargs['classes']
    except KeyError:
        pass

    for key, value in kwargs.iteritems():
        key = key.replace('_', '-')
        key = to_unicode(key)
        if isinstance(value, bool):
            if value is True:
                props.append(key)
        else:
            value = quoteattr(to_unicode(value))
            attrs.append(u'%s=%s' % (key, value))

    attrs.sort()
    props.sort()
    attrs.extend(props)
    return u' '.join(attrs)


def is_protected_type(obj):
    """Determine if the object instance is of a protected type.

    Objects of protected types are preserved as-is when passed to
    to_unicode(strings_only=True).
    """
    return isinstance(obj, (
        types.NoneType,
        int, long,
        datetime.datetime, datetime.date, datetime.time,
        float, Decimal)
    )


def to_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """Returns a unicode object representing 's'. Treats bytestrings using the
    `encoding` codec.

    If strings_only is True, don't convert (some) non-string-like objects.

    ----
    Copyright © Django Software Foundation and individual contributors.
    Used under the modified BSD license.
    """
    # Handle the common case first, saves 30-40% in performance when s
    # is an instance of unicode.
    if isinstance(s, unicode):
        return s
    if strings_only and is_protected_type(s):
        return s
    encoding = encoding or 'utf-8'
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                try:
                    s = unicode(str(s), encoding, errors)
                except UnicodeEncodeError:
                    if not isinstance(s, Exception):
                        raise
                    # If we get to here, the caller has passed in an Exception
                    # subclass populated with non-ASCII data without special
                    # handling to display as a string. We need to handle this
                    # without raising a further exception. We do an
                    # approximation to what the Exception's standard str()
                    # output should be.
                    s = u' '.join([to_unicode(arg, encoding, strings_only,
                        errors) for arg in s])
        elif not isinstance(s, unicode):
            # Note: We use .decode() here, instead of unicode(s, encoding,
            # errors), so that if s is a SafeString, it ends up being a
            # SafeUnicode at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError, e:
        if not isinstance(s, Exception):
            raise UnicodeDecodeError(s, *e.args)
        else:
            # If we get to here, the caller has passed in an Exception
            # subclass populated with non-ASCII bytestring data without a
            # working unicode method. Try to handle this without raising a
            # further exception by individually forcing the exception args
            # to unicode.
            s = u' '.join([to_unicode(arg, encoding, strings_only,
                errors) for arg in s])
    return s

