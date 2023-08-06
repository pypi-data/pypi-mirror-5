from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.query_utils import Q

from ..fields import PolymorphicTypeField
from ..utils import get_content_type

from .base import TestCase
from .models import AcknowledgedTrait, HugeSnake, Snake, Trait


class PolymorphicTypeFieldTest(TestCase):
    def test_default_value(self):
        """
        Make sure fields defaults
        """
        trait = Trait.objects.create()
        self.assertIsNone(trait.trait_type)
        self.assertIsNone(trait.mammal_type)
        self.assertEqual(trait.snake_type.model_class(), Snake)

    def test_limit_choices_to(self):
        """
        Make sure existing `limit_choices_to` are taken into consideration
        """
        trait_type = Trait._meta.get_field('trait_type')

        # Make sure it's cached
        limit_choices_to = trait_type.rel.limit_choices_to
        self.assertIn('limit_choices_to', trait_type.rel.__dict__)

        extra_limit_choices_to = {'app_label': 'polymodels'}

        # Make sure it works with existing dict `limit_choices_to`
        trait_type.rel.limit_choices_to = extra_limit_choices_to
        # Cache should be cleared
        self.assertNotIn('limit_choices_to', trait_type.rel.__dict__)
        self.assertEqual(
            trait_type.rel.limit_choices_to,
            dict(extra_limit_choices_to, **limit_choices_to)
        )

        # Make sure it works with existing Q `limit_choices_to`
        trait_type.rel.limit_choices_to = Q(**extra_limit_choices_to)
        # Cache should be cleared
        self.assertNotIn('limit_choices_to', trait_type.rel.__dict__)
        self.assertEqual(
            str(trait_type.rel.limit_choices_to),
            str(Q(**extra_limit_choices_to) & Q(**limit_choices_to))
        )

        # Re-assign the original value
        trait_type.rel.limit_choices_to = None
        # Cache should be cleared
        self.assertNotIn('limit_choices_to', trait_type.rel.__dict__)

    def test_invalid_type(self):
        trait = Trait.objects.create()
        snake_type = get_content_type(Snake)
        trait.mammal_type = snake_type
        trait.snake_type = snake_type
        with self.assertRaisesMessage(
            ValidationError, 'Specified content type is not of a subclass of Mammal.'):
            trait.full_clean()

    def test_valid_subclass(self):
        trait = Trait.objects.create()
        trait.snake_type = get_content_type(HugeSnake)
        trait.full_clean()

    def test_valid_proxy_subclass(self):
        trait = Trait.objects.create()
        trait.trait_type = get_content_type(AcknowledgedTrait)
        trait_type = Trait._meta.get_field('trait_type')
        trait.full_clean()

    def test_description(self):
        trait_type = Trait._meta.get_field('trait_type')
        self.assertEqual(
            trait_type.description % trait_type.__dict__,
            'Content type of a subclass of Trait'
        )

    def test_invalid_polymorphic_model(self):
        with self.assertRaisesMessage(AssertionError,
            "First parameter to `PolymorphicTypeField` must be "
            "a subclass of `BasePolymorphicModel`"):
            PolymorphicTypeField(None)
        with self.assertRaisesMessage(AssertionError,
            "First parameter to `PolymorphicTypeField` must be "
            "a subclass of `BasePolymorphicModel`"):
            PolymorphicTypeField(models.Model)
