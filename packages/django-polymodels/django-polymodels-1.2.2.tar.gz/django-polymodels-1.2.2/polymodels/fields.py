from __future__ import unicode_literals

from inspect import isclass

from django.contrib.contenttypes.models import ContentType
from django.db.models import ForeignKey, Q
from django.db.models.fields import NOT_PROVIDED
from django.db.models.fields.related import add_lazy_relation, ManyToOneRel
from django.utils.translation import ugettext_lazy as _

from .models import BasePolymorphicModel
from .utils import get_content_type, string_types


class ManyToOneRel(ManyToOneRel):
    """
    Relationship that generates a `limit_choices_to` based on it's polymorphic
    type subclasses.
    """

    @property
    def limit_choices_to(self):
        subclasses_lookup = self.polymorphic_type.subclasses_lookup('pk')
        limit_choices_to = self._limit_choices_to
        if limit_choices_to is None:
            limit_choices_to = subclasses_lookup
        elif isinstance(limit_choices_to, dict):
            limit_choices_to = dict(limit_choices_to, **subclasses_lookup)
        elif isinstance(limit_choices_to, Q):
            limit_choices_to = limit_choices_to & Q(**subclasses_lookup)
        # Cache it
        self.__dict__['limit_choices_to'] = limit_choices_to
        return limit_choices_to

    @limit_choices_to.setter
    def limit_choices_to(self, value):
        self._limit_choices_to = value
        # Removed the cached value and return it
        return self.__dict__.pop('limit_choices_to', None)


class PolymorphicTypeField(ForeignKey):
    default_error_messages = {
        'invalid': _('Specified model is not a subclass of %(model)s.')
    }
    description = _(
        'Content type of a subclass of %(type)s'
    )

    def __init__(self, polymorphic_type, *args, **kwargs):
        if not isinstance(polymorphic_type, string_types):
            self.validate_polymorphic_type(polymorphic_type)
        defaults = {
            'to': ContentType, 'related_name': '+', 'rel_class': ManyToOneRel
        }
        defaults.update(kwargs)
        super(PolymorphicTypeField, self).__init__(*args, **defaults)
        self.rel.polymorphic_type = polymorphic_type

    def validate_polymorphic_type(self, model):
        if not isclass(model) or not issubclass(model, BasePolymorphicModel):
            raise AssertionError(
                "First parameter to `PolymorphicTypeField` must be "
                "a subclass of `BasePolymorphicModel`"
            )

    def contribute_to_class(self, cls, name):
        super(PolymorphicTypeField, self).contribute_to_class(cls, name)
        polymorphic_type = self.rel.polymorphic_type
        if (isinstance(polymorphic_type, string_types) or
            polymorphic_type._meta.pk is None):
            def resolve_polymorphic_type(field, model, cls):
                field.validate_polymorphic_type(model)
                field.rel.polymorphic_type = model
                field.do_polymorphic_type(model)
            add_lazy_relation(
                cls, self, polymorphic_type, resolve_polymorphic_type
            )
        else:
            self.do_polymorphic_type(polymorphic_type)

    def do_polymorphic_type(self, polymorphic_type):
        if self.default is NOT_PROVIDED and not self.null:
            self.default = lambda: get_content_type(polymorphic_type)
        self.type = polymorphic_type.__name__
        self.error_messages['invalid'] = (
            'Specified content type is not of a subclass of %s.' %
            polymorphic_type._meta.object_name
        )
