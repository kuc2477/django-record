from datetime import timedelta

from django.db.models import QuerySet
from django.utils.timezone import datetime

from .utils import resample_records


class RecordQuerySet(QuerySet):
    """Queryset for RecordModel subclass models.

    Provides useful time filters including pandas resampling filter.

    Note that record manager is created from the queryset.
    """
    def resample(self, rule):
        """Resamples record queryset based on pandas resampling rules.

        :param rule: The pandas resampling rule to filter queryset
        :return: The queryset that has been resampled base on the given pandas
        :rtype: QuerySet
        """
        return resample_records(self, rule)

    def created_in(self, delta):
        """Filters queryset based on the past time from it's been created.

        :param delta: Delta threshold from now to filter the queryset.
        :type delta: datetime.timedelta
        """
        return self.filter(created__gte=datetime.now() - delta)

    def created_in_years(self, years=1):
        """Filters queryset based on past years from it's been created.

        :param years: Years threshold from now to filter the queryset
        :type years: int (optional), defaults to 1
        """
        return self.created_in(timedelta(days=365))

    def created_in_months(self, months=1):
        """Filters queryset based on past months from it's been created.

        Note that here we consider 1 month as equivalent of 30 days.

        :param months: Months threshold from now import to filter the queryset.
        :type months: int (optional), defaults to 1
        """
        return self.created_in(timedelta(weeks=4))

    def created_in_weeks(self, weeks=1):
        """Filters queryset based on past weeks from it's been created.

        :param weeks: Weeks threshold from now import to filter the queryset.
        :type weeks: int (optional), defaults to 1
        """
        return self.created_in(timedelta(weeks=weeks))

    def created_in_days(self, days=1):
        """Filters queryset based on past days from it's been created.

        :param days: Days threshold from now import to filter the queryset.
        :type days: int (optional), defaults to 1
        """
        return self.created_in(timedelta(days=days))

    def created_in_hours(self, hours=1):
        """Filters queryset based on past hours from it's been created.

        :param hours: Hours threshold from now import to filter the queryset.
        :type hours: int (optional), defaults to 1
        """
        return self.created_in(timedelta(hours=hours))

    def created_in_minutes(self, minutes=1):
        """Filters queryset based on past minutes from it's been created.

        :param minute: Minutes threshold from now import to filter the queryset.
        :type minute: int (optional), defaults to 1
        """
        return self.created_in(timedelta(minutes=minutes))

    def created_in_seconds(self, seconds=1):
        """Filters queryset based on past seconds from it's been created.

        :param second: Seconds threshold from now import to filter the queryset.
        :type second: int (optional), defaults to 1
        """
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
