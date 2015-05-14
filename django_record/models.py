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


class RecordModelMetaClass(ModelBase):
    def __new__(cls, name, bases, attrs):
        """
        Generates RecordModel subclass.

        """
        super_new = super(RecordModelMetaClass, cls).__new__

        # Ensure that recording field registration is done only on
        # subclasses of RecordModel (not RecordModel itself).
        if name == 'RecordModel':
            return super_new(cls, name, bases, attrs)

        recording_model = attrs.get('recording_model')
        recording_fields = attrs.pop('recording_fields')

        # Replace 'recording_fields' with list of field names rather than
        # storing composite of field names and property tuples.
        attrs['recording_fields'] = []

        # Only django models are recordable.
        assert(issubclass(recording_model, Model))

        for field_entry in recording_fields:
            # recording field given in a tuple format (properties allowed).
            if isinstance(field_entry, tuple):
                field_name, field = field_entry
                assert(isinstance(field, Field))

            # recording field given in ordinary format (ordinary fields).
            else:
                field_name = field_entry
                field = deepcopy(recording_model._meta.get_field(field_name))

            # Register recording fields to the subclass of a
            # RecordModel and keep their names for later usage.
            attrs[field_name] = field
            attrs['recording_fields'].append(field_name)

        # Register foreign key to the RecordModel.
        attrs['recording'] = ForeignKey(recording_model, related_name='records')

        return super_new(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        """
        Register a recorder with post_save signal for the generated RecordModel
        subclass.

        """
        def recorder(sender, **kwargs):
            # Ensure that only instances of models that are explicitly told
            # to be audited are recorded.
            if not sender == cls.recording_model:
                return

            instance = kwargs['instance']
            created = kwargs['created']

            if created or cls._model_instance_changed(instance):
                ckwargs = {name: getattr(instance, name) for name
                           in cls.recording_fields}
                ckwargs['recording'] = instance
                cls.objects.create(**ckwargs)

        # Connect recorder to the signal.
        post_save.connect(recorder, weak=False)

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
    """
    Automatically create records when an audited Django model instance has been
    changed.

    RecordModel will detect any changes of 'recording_fields' in
    'recording_model' at it's post save() time and create an record for it.

    You can access records via record manager 'records' in your recorded model
    instance. Also, you are able to access audited model via 'recording' in
    your records, which is in effect ForeignKey.

    Attributes:
        recording_model (class): A model class to be audited and recorded.
            Record will be created on every changed save() calls of it's
            instance.
        recording_fields (list): A List of to-be-recoreded field names or
            tuples of property name and it's appropriate field.

    Example:
        from django.db import models
        from django.contrib.auth.models import User
        from django_record.models import TimeStampedModel
        from django_record.models import RecordModel


        class Debate(models.Model):
            user = models.ForeignKey(User)

            title = models.CharField(max_length=100)
            num_of_pros = models.IntegerField()
            num_of_cons = models.IntegerField()

            @property
            def pros_rate(self):
                return self.num_of_pros // (self.num_of_pros + self.num_of_cons)

            @property
            def cons_rate(self):
                return self.num_of_cons // (self.num_of_pros + self.num_of_cons)


        class DebateRecord(RecordModel):
            recording_model = Debate
            recording_fields = [
                'title', 'num_of_pros', 'num_of_cons'
                ('pros_rate', models.FloatField()),
                ('cons_rate', models.FloatField())
            ]

        .
        .
        >>> d =  Debate.objects.first()
        >>> r =  d.records.latest()
        >>> assert(d.title == r.title)
        >>> assert(d.pros_rate == r.pros_rate)
        .
        .
        >>> records_before_yesterday = d.records.filter(created__lte=yesterday)
        >>> records_of_today = d.records.filter(created__gte=today)

    Note:
        Relational fields(e.g. ForeignKey, ManyToManyField, ...) are not
            currently supported.
        Only primitive types are supported for properties and you must
            offer appropriate field for them when you put a tuple of a property
            name and it's field in 'recording_fields' for expected recording.
        RecordModel is also a subclass of TimeStampedModel, so make sure that
            you don't record fields with either name 'created' or 'modified'.
    """
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
