from copy import deepcopy

from django.db.models.signals import post_save

from django.db.models.fields import Field
from django.db.models.base import ModelBase
from django.db.models import Model

from django.db.models import ForeignKey
from django.db.models import DateTimeField


class TimeStampedModel(Model):
    created_time = DateTimeField(auto_now=True)
    modified_time = DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('created_time',)
        get_latest_by = 'created_time'


class RecordModelMetaClass(ModelBase):
    def __init__(cls, name, bases, attrs):
        # Ensure that record field registration is done only on
        # subclasses of RecordModel (not RecordModel itself).
        if name == 'RecordModel':
            return

        recording_model = attrs.get('recording_model')
        recording_fields = attrs.get('recording_fields')

        # Only subclasses of Django Models are recordable.
        assert(issubclass(recording_model, Model))

        # Register recording fields to the subclass of a RecordModel and keep
        # their names for later usage.
        field_names = []
        for field_entry in recording_fields:
            # recording field given in a tuple format (properties allowed).
            if isinstance(field_entry, tuple):
                field_name, field = field_entry

                assert(isinstance(field, Field))
                field.contribute_to_class(cls, field_name)

            # recording field given in ordinary format (ordinary fields).
            else:
                field_name = field_entry

                field = deepcopy(recording_model._meta.get_field(field_name))
                field.contribute_to_class(cls, field.name)

            field_names.append(field_name)

        # Register foreign key.
        ForeignKey(recording_model, related_name='records')\
            .contribute_to_class

        def recorder(sender, **kwargs):
            # Ensure that only models that are explicitly told to be
            # are recorded.
            if not sender == recording_model:
                return

            # NOT IMPLEMENTED YET

        post_save.connect(recorder)


class RecordModel(TimeStampedModel):
    __metaclass__ = RecordModelMetaClass

    recording_model = NotImplemented

    # List of model's fields or properties to be recorded.
    #
    # You should use tuples consist of property name and appropriate django
    # model field to record the model's property rather than ordinary model
    # field.
    #
    # If you are just recording ordinary django model field, then it's
    # ok to just simply put the field's name instead of a tuple.
    #
    # Example: [('full_name', CharField(max_length=100)), 'created_time', ...]
    recording_fields = NotImplemented

    class Meta(TimeStampedModel.Meta):
        abstract = True
