from copy import deepcopy

from django.dispatch import receiver
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


class RecordModelMetaClass(ModelBase):
    def __init__(cls, name, bases, attrs):
        # Ensure that recording field registration is done only on
        # subclasses of RecordModel (not RecordModel itself).
        if name == 'RecordModel':
            return

        recording_model = attrs.get('recording_model')
        recording_fields = attrs.get('recording_fields')

        # Only subclasses of Django Models are recordable.
        assert(issubclass(recording_model, Model))

        # Register recording fields to the subclass of a
        # RecordModel and keep their names for later usage.
        cls.recording_fields = []
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

            cls.recording_fields.append(field_name)

        # Register foreign key to the RecordModel.
        foreign_key = ForeignKey(recording_model, related_name='records')
        foreign_key.contribute_to_class(cls, 'recording')
        foreign_key.contribute_to_related_class(cls, recording_model)

        @receiver(post_save)
        def recorder(sender, **kwargs):
            # Ensure that only instances of models that are explicitly told
            # to be audited are recorded.
            if not sender == recording_model:
                return

            instance = kwargs['instance']
            created = kwargs['instance']

            if created or cls._model_instance_changed(instance):
                cls.objects.create(
                    recording=instance,
                    {name: getattr(instance, name) for name in
                     cls.recording_fields}
                )

    def _model_instance_changed(cls, instance):
        # Consider a model instance has been changed if records doesn't exist.
        if not instance.records.exists():
            return True

        # Compare fields of the instance with the latest record.
        latest_record = instance.records.latest()
        for name in cls.recording_fields:
            if getattr(instance, name) != getattr(latest_record, name):
                return True
        return False


class RecordModel(TimeStampedModel):
    __metaclass__ = RecordModelMetaClass

    recording_model = NotImplemented

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
    recording_fields = NotImplemented

    class Meta(TimeStampedModel.Meta):
        abstract = True
        get_latest_by = 'created'
