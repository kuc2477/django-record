from copy import deepcopy

from django.db.models.signals import post_save

from django.db.models.fields import Field
from django.db.models.base import ModelBase
from django.db.models import Model

from django.db.models import ForeignKey
from django.db.models import DateTimeField


class TimeStampedModel(Model):
    created = DateTimeField(auto_now=True)
    modified = DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ('created',)
        get_latest_by = 'created'


class RecordModelMetaClass(ModelBase):
    def __init__(cls, name, bases, attrs):
        # Ensure that monitored field registration is done only on
        # subclasses of RecordModel (not RecordModel itself).
        if name == 'RecordModel':
            return

        monitored_model = attrs.get('recording_model')
        monitored_fields = attrs.get('recording_fields')

        # Only subclasses of Django Models are recordable.
        assert(issubclass(monitored_model, Model))

        # Register monitored and recorded fields to the subclass of a
        # RecordModel and keep their names for later usage.
        field_names = []
        for field_entry in monitored_fields:
            # monitored field given in a tuple format (properties allowed).
            if isinstance(field_entry, tuple):
                field_name, field = field_entry

                assert(isinstance(field, Field))
                field.contribute_to_class(cls, field_name)

            # monitored field given in ordinary format (ordinary fields).
            else:
                field_name = field_entry

                field = deepcopy(monitored_model._meta.get_field(field_name))
                field.contribute_to_class(cls, field.name)

            field_names.append(field_name)

        # Register foreign key.
        foreign_key = ForeignKey(monitored_model, related_name='records')
        foreign_key.contribute_to_class(cls, )

        def recorder(sender, **kwargs):
            # Ensure that only models that are explicitly told to be
            # are recorded.
            if not sender == monitored_model:
                return

            # NOT IMPLEMENTED YET

        post_save.connect(recorder)


class RecordModel(TimeStampedModel):
    __metaclass__ = RecordModelMetaClass

    monitored_model = NotImplemented

    # List of model's fields or properties to be recorded.
    #
    # You should use tuples consist of property name and appropriate django
    # model field to record the model's property rather than ordinary model
    # field.
    #
    # If you want to monitor on ordinary django model field, then it's
    # ok to just simply put the field's name instead of a tuple.
    #
    # Example: [('full_name', CharField(max_length=100)), 'created_time', ...]
    monitored_fields = NotImplemented

    class Meta(TimeStampedModel.Meta):
        abstract = True
