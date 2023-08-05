# -*- coding: utf-8 -*-

from django.db import models
from django.utils import six
from django.utils.encoding import force_text
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


def _cast_to_unicode(data):
    if isinstance(data, (list, tuple)):
        return [_cast_to_unicode(x) for x in data]
    elif isinstance(data, str):
        return force_text(data)
    return data


class ArrayField(models.Field):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self._array_type = kwargs.pop('dbtype', 'int')
        self._dimension = kwargs.pop('dimension', 1)
        kwargs.setdefault('blank', True)
        kwargs.setdefault('null', True)
        kwargs.setdefault('default', None)
        super(ArrayField, self).__init__(*args, **kwargs)

    def formfield(self, **params):
        params['form_class'] = ArrayFormField
        return super(ArrayField, self).formfield(**params)

    def db_type(self, connection):
        return '{0}{1}'.format(self._array_type, "[]" * self._dimension)

    def get_db_prep_value(self, value, connection, prepared=False):
        value = value if prepared else self.get_prep_value(value)
        if not value or isinstance(value, six.string_types):
            return value

        return value

    def get_prep_value(self, value):
        return value

    def to_python(self, value):
        return _cast_to_unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

# South support
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([
        (
            [ArrayField], # class
            [],           # positional params
            {
                "dbtype": ["_array_type", {"default": "int"}],
                "dimension": ["_dimension", {"default": 1}],
            }
        )
    ], ['^djorm_pgarray\.fields\.ArrayField'])
except ImportError:
    pass


class ArrayFormField(forms.Field):

    error_messages = {
        'invalid': _('Enter a list of values, joined by commas.  E.g. "a,b,c".'),
    }

    def __init__(self, max_length=None, min_length=None, delim=None, *args, **kwargs):
        if delim is not None:
            self.delim = delim
        else:
            self.delim = ','
        super(ArrayFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        try:
            return value.split(self.delim)
        except:
            raise ValidationError(self.error_messages['invalid'])

    def prepare_value(self, value):
        return self.delim.join(value)

    def to_python(self, value):
        return value.split(self.delim)
