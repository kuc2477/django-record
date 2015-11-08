from datetime import timedelta

from django.db.models import QuerySet
from django.utils.timezone import datetime

from .utils import resample_records


class RecordQuerySet(QuerySet):
    def resample(self, rule):
        return resample_records(self, rule)

    def created_in(self, delta):
        return self.filter(created__gte=datetime.now() - delta)

    def created_in_years(self, years=1):
        return self.created_in(timedelta(days=365))

    def created_in_months(self, months=1):
        return self.created_in(timedelta(weeks=4))

    def created_in_weeks(self, weeks=1):
        return self.created_in(timedelta(weeks=weeks))

    def created_in_days(self, days=1):
        return self.created_in(timedelta(days=days))

    def created_in_hours(self, hours=1):
        return self.created_in(timedelta(hours=hours))

    def created_in_minutes(self, minutes=1):
        return self.created_in(timedelta(minutes=minutes))

    def created_in_seconds(self, seconds=1):
        return self.created_in(timedelta(seconds=seconds))

    resample.queryset_only = False
    created_in.queryset_only = False
    created_in_years.queryset_only = False
    created_in_months.queryset_only = False
    created_in_weeks.queryset_only = False
    created_in_days.queryset_only = False
    created_in_hours.queryset_only = False
    created_in_minutes.queryset_only = False
    created_in_seconds.queryset_only = False
