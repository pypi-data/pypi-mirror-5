# -*- coding: utf-8 -*-
from ..utils import Markup, get_html_attrs
from .field import Field, ValidationError


class File(Field):
    """ An upload file field.

    **Does not actually upload the file. Use its ``clean`` method for that.**

    :param validate:
        An list of validators. This will evaluate the current `value` when
        the method `validate` is called.

    :param default:
        Default value.

    :param prepare:
        An optional function that takes the current value as a string
        and preprocess it before rendering.

    :param clean:
        An optional function that takes the value already converted to
        python and return a 'cleaned' version of it. If the value can't be
        cleaned `None` must be returned instead.

    """
    hide_value = True

    def __init__(self, **kwargs):
        super(File, self).__init__(**kwargs)

    def str_to_py(self, **kwargs):
        return self.str_value or self.file_data or self.obj_value

    def __call__(self, **kwargs):
        return self.as_input(**kwargs)

    def as_input(self, **kwargs):
        kwargs['type'] = 'file'
        kwargs['name'] = self.name
        if not self.optional:
            kwargs.setdefault('required', True)
        html = u'<input %s>' % get_html_attrs(kwargs)
        return Markup(html)

