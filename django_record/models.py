from copy import deepcopy

from django.db import models
from django.db.models.signal import class_prepared
from django.db.models.signals import post_save

from django.db.models.fields import Field
from django.db.models.base import ModelBase
from django.db.models import Model


class TimeStampedModel(Model):
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class RecordModelMetaClass(ModelBase):
    def __new__(cls, name, bases, attrs):
        """
        Generates a RecordModel subclass.

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
        attrs['recording'] = models.ForeignKey(
            recording_model, related_name='records'
        )

        return super_new(cls, name, bases, attrs)

    def register_record_meta(cls):
        """
        Registers RecordMeta for the generated record model itself.

        """
        # Audit all relative fields if `RecordMeta`'s `audit_all_relatives` flag
        # is True.
        if cls.RecordMeta.audit_all_relatives:
            cls.auditing_relatives = [
                name for name in cls._meta.get_all_field_names() if
                getattr(cls, name).__module__ ==
                'django.db.models.fields.related'
            ]

    def register_recorders(cls, name, bases, attrs):
        """
        Registers recorders for the generated record model.

        """
        def recorder(sender, created, instance, **kwargs):
            # Ensure that the recorder audits and records only instances of the
            # `recording model`.
            if not sender == cls.recording_model:
                return

            if created or cls._recording_instance_changed(instance):
                cls.record(instance)

        def indirect_effect_recorder(sender, instance, **kwargs):
            # Ensure that only instances of relative models are audited and
            # have indirect effect on recording.
            if not sender in cls.relative_models:
                return

            # Get `recording_model` instances from the relative.
            instances = cls._get_recording_instances(instance)

            for instance in instances:
                if cls._recording_instance_changed(instance):
                    cls.record(instance)

        # Connect recorders to the signal.
        post_save.connect(recorder, weak=False)
        post_save.connect(indirect_effect_recorder, weak=False)

    def record(cls, instance):
        """
        Records an given instance.

        """
        ckwargs = {name: getattr(instance, name) for name in
                   cls.recording_fields}
        ckwargs['recording'] = instance
        cls.objects.create(**ckwargs)


    def identify_related_models(cls):
        """
        Identify all related models of the RecordModel subclass and register
        them as a set of models on the RecordModel subclass.

        """
        # Models of relatives defined from outside of the recorded model.
        foreign_relative_models = set([
            getattr(cls, name).related.model for name in cls.auditing_relatives
            if hasattr(getattr(cls, name), 'related') and not
            # Except RecordModel subclasses from auditing list.
            issubclass(getattr(cls, name).related.model, RecordModel)
        ])

        # Models of relatives defined inside of the recorded model.
        local_relative_models = set([
            getattr(cls, name).field.get_path_info()[0].to_opts.model for
            name in cls.auditing_relatives
            if hasattr(getattr(cls, name), 'field')
        ])

        cls.relative_models = foreign_relative_models | local_relative_models

    def _recording_instance_changed(cls, instance):
        # Consider a model instance has been changed if records doesn't exist.
        if not instance.records.exists():
            return True

        # Compare fields of the instance with the latest record.
        latest_record = instance.records.latest()
        for name in cls.recording_fields:
            if getattr(instance, name) != getattr(latest_record, name):
                return True
        return False

    def _get_recording_instances_in_relative(cls, relative):
        recording_instances = []

        for field in [getattr(relative, name) for name
                      in relative._meta.get_all_field_names()]:
            # If a field of a relative is an instance of the recording model,
            # it's an recording instance.
            if isinstance(field, cls.recording_model):
                recording_instances.append(field)

            # If a module attribute of a relative's field is 'django.db.models.
            # fields.related' and it's model attribute is recording model class,
            # it's an related manager or many related manager of recording
            # instances.
            elif field.__module__ == 'django.db.models.fields.related' and \
                field.model == cls.recording_model:
                recording_instances.append(field.all())

        return recording_instances



class RecordModel(TimeStampedModel):
    """
    Automatically create records when an audited Django model instance has been
    changed either directly or indirectly.

    RecordModel will detect any changes of 'recording_fields' in
    'recording_model' at it's post save() time or auditing relative's
    post ave() time and create an new record for it.

    You can access records via record manager 'records' in your recorded model
    instance. Also, you are able to access audited model via 'recording' in
    your records, which is in effect ForeignKey.

    Attributes:
        recording_model (class): A model class to be recorded. An extra record
            will be created on every changed save() calls of it's instance or
            auditing relative's save() calls.
        recording_fields (list): A List consists of either to-be-recoreded field
            names or tuples of a property name and it's field instance to
            be saved in database.
        auditing_relatives (list): A List of audited relatives. An extra record
            will be created on every save() calls of relative instances that
            affects recording instance, along with recording on recording-
            instance-changing save() calls.

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

            @property
            def user_name(self):
                return user.username


        class DebateRecord(RecordModel):
            recording_model = Debate
            recording_fields = [
                'title', 'num_of_pros', 'num_of_cons'
                ('pros_rate', models.FloatField()),
                ('cons_rate', models.FloatField()),
                ('user_name', models.CharField(max_length=100))
            ]

            auditing_relatives = ['user', ]

        ...
        >>> d =  Debate.objects.first()
        >>> r =  d.records.latest()
        >>> assert(d.title == r.title)
        >>> assert(d.pros_rate == r.pros_rate)
        ...
        >>> records_before_yesterday = d.records.filter(created__lte=yesterday)
        >>> records_of_today = d.records.filter(created__gte=today)
        ...
        >>> u = d.user
        >>> u.username = 'changed user name'
        >>> u.save()
        >>> r = d.records.latest()
        >>> assert(d.user_name == r.user_name)
        >> assert(d.user.username == r.user_name)

    Note:
        Only primitive types are supported for properties and you must
            offer appropriate field for them when you put a tuple of a property
            name and it's field in 'recording_fields' for expected recording.
        RecordModel is also a subclass of TimeStampedModel, so make sure that
            you don't record fields with either name 'created' or 'modified'.
    """
    # TODO: Python3 compatibility issue - use six module.
    __metaclass__ = RecordModelMetaClass

    recording_model = NotImplemented

    # List of model's fields or properties to be recorded.
    #
    # You should use tuples consist of property name and appropriate django
    # model field to record the model's property rather than ordinary model
    # field.
    #
    # If you want to monitor on ordinary django model field, then it's perfectly
    # ok to just simply put the field's name instead of the tuple.
    #
    # Example: recording_fields = [
    #                                 'first_name', 'last_name',
    #                                 ('liquidity', IntegerField()),
    #                                 ('liquidity_ratio', FloatField()),
    #                                 ('full_name', CharField(max_length=100))
    #                             ]
    recording_fields = NotImplemented

    # List of relatives to be audited for changes.
    #
    # You can audit relatives(foreign key or related instances) for their
    # changes to record their indirect effects on `recording_fields`.
    #
    # Example: auditing_relatives = [
    #                                   'father', 'mother',
    #                                   'interested_funds',
    #                                   'subscribed_funds',
    #                               ]
    auditing_relatives = []

    class Meta(TimeStampedModel.Meta):
        abstract = True
        get_latest_by = 'created'

    class RecordMeta:
        audit_all_relatives = False
