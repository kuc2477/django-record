from copy import deepcopy

from django.db import models
from django.db.models.signals import post_save
from django.db.models.signals import class_prepared

from django.db.models.fields import Field
from django.db.models.base import ModelBase
from django.db.models import Model

import monkey


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

        # Monkey-patch recording model with shortcut properties.
        cls.monkey_patch(recording_model)

        # Generate RecordModel subclass
        return super_new(cls, name, bases, attrs)

    @staticmethod
    def monkey_patch(recording_model):
        for name, prop in [
            (k, v) for k, v in monkey.__dict__.items() if not k.startswith('_')
        ]:
            setattr(recording_model, name, prop)


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
    recording_fields = []

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

    class RecordMeta:
        # All relatives will be audited by default.
        #
        # Note that turning this flag on can cause potential
        # performance issue in large scale database.
        audit_all_relatives = False

    class Meta(TimeStampedModel.Meta):
        abstract = True

        # Latest Records will be retrieved by `latest()` filter.
        get_latest_by = 'created'

    # ====================
    # RecordModel Methods
    # ====================

    @classmethod
    def record(cls, instance):
        """
        Records an given instance of the `recording_model`.

        """
        ckwargs = {name: getattr(instance, name) for name in
                   cls.recording_fields}
        ckwargs['recording'] = instance
        cls.objects.create(**ckwargs)

    @classmethod
    def recording_instance_changed(cls, instance):
        """
        Check whether if any of `recording_fields` of the recording instance has
        been changed.

        """
        # Consider a model instance has been changed if records doesn't exist.
        if not instance.records.exists():
            return True

        latest_record = instance.records.latest()

        # Compare fields of the instance with the latest record.
        for name in cls.recording_fields:
            if getattr(instance, name) != getattr(latest_record, name):
                return True

        return False

    # TODO: Can be potential performance bottleneck, implement in other ways
    #       rather than in a method.
    @classmethod
    def get_relative_models_to_audit(cls):
        """
        Returns a set of all models of `recording_relatives`.

        """
        meta = cls.recording_model._meta

        # Audit all relatives if RecordMeta's audit_all_relatives flag is
        # True.
        if cls.RecordMeta.audit_all_relatives:
            cls.auditing_relatives = [
                name for name in meta.get_all_field_names() if
                'related' in meta.get_field_by_name(name)[0].__module__
            ]

        relative_models = set()

        for name in cls.auditing_relatives:
            field = meta.get_field_by_name(name)[0]

            try:
                # Related models.
                model = field.get_path_info()[0].to_opts.model

            except AttributeError:
                # Reverse related models.
                model = field.get_reverse_path_info()[0].from_opts.model

            if not model == cls:
                relative_models.add(model)

        return relative_models

    @classmethod
    def get_related_recording_instances(cls, relative):
        """
        Get related instances of the `recording_model` from a relative.

        """
        recording_instances = []

        # Links to related objects.
        related_links = [rel.get_accessor_name() for rel in
                         relative._meta.get_all_related_objects()]

        # Links to many to many related objects.
        many_to_many_links = [rel.get_accessor_name() for rel in
                              relative._meta
                              .get_all_related_many_to_many_objects()]

        for link in related_links + many_to_many_links:
            try:
                instances = getattr(relative, link).all()
                if instances.model == cls.recording_model:
                    recording_instances.extend(instances)

            except AttributeError:
                instance = getattr(relative, link)
                recording_instances.append(instance)

        return recording_instances

    @classmethod
    def get_reverse_related_recording_instances(cls, relative):
        """
        Get reverse related instances of the `recording_model` from a relative.

        """
        recording_instances = []

        for field in relative._meta.fields:
            if hasattr(field, 'get_path_info') and \
                    field.get_path_info()[0].to_opts.model == \
                    cls.recording_model:
                try:
                    instances = getattr(relative, field.name).all()
                    recording_instances.extend(instances)

                except AttributeError:
                    instance = getattr(relative, field.name)
                    recording_instances.append(instance)

        return recording_instances

    @classmethod
    def _register_recorder(cls):
        """
        Registers a recorder.

        """
        # RECORDER
        def recorder(sender, created, instance, **kwargs):
            # Ensure that the recorder audits and records only instances of the
            # `recording model`.
            if sender != cls.recording_model:
                return

            if created or cls.recording_instance_changed(instance):
                cls.record(instance)

        post_save.connect(recorder, weak=False)

    @classmethod
    def _register_indirect_effect_recorder(cls):
        """
        Registers an indirect effect recorder.

        """
        # INDIRECT EFFECT RECORDER
        def indirect_effect_recorder(sender, instance, **kwargs):
            # Ensure that only instances of relative models are audited and
            # have indirect effect on recording.
            if sender not in cls.get_relative_models_to_audit():
                return

            # Set alias for readability.
            relative = instance

            # Get `recording_model` instances from the relative.
            recording_instances = \
                cls.get_related_recording_instances(relative) + \
                cls.get_reverse_related_recording_instances(relative)

            for recording in recording_instances:
                if cls.recording_instance_changed(recording):
                    cls.record(recording)

        post_save.connect(indirect_effect_recorder, weak=False)


# ================================================
# Listen for RecordModel subclass prepared signals
# ================================================

# Registers recorders for RecordModel subclasses on their `class_prepared`
# signals.
def register_recorders(sender, **kwargs):
    base_names = [base.__name__ for base in sender.__bases__]
    # Since the model has not been fully registered, we use 'RecordModel' rather
    # than `issubclass` function.
    if 'RecordModel' in base_names:
        sender._register_recorder()
        sender._register_indirect_effect_recorder()

class_prepared.connect(register_recorders, weak=False)
