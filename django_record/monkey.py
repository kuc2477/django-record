"""
Conains shortcut properties that will be monkey-patched to `recording_model`

"""
# TODO: Refactor entire module into custom record manager.
from django.utils.timezone import datetime
from django.utils.timezone import timedelta

from .utils import resample_records


# =================================================
# Shortcut properties for retrieving recent records
# =================================================

def records_in_delta(self, delta):
    return self.records.filter(created__gte=datetime.now()-delta)

@property
def records_in_hour(self):
    return self.records\
        .filter(created__year=datetime.now().year)\
        .filter(created__month=datetime.now().month)\
        .filter(created__day=datetime.now().day)\
        .filter(created__hour=datetime.now().hour)


@property
def records_in_day(self):
    return self.records\
        .filter(created__year=datetime.now().year)\
        .filter(created__month=datetime.now().month)\
        .filter(created__day=datetime.now().day)


@property
def records_in_week(self):
    return self.records.filter(
        created__range=[datetime.now()-timedelta(weeks=1), datetime.now()])


@property
def records_in_month(self):
    return self.records\
        .filter(created__year=datetime.now().year)\
        .filter(created__month=datetime.now().month)


@property
def records_in_year(self):
    return self.records.filter(created__year=datetime.now().year)


# =========================================================================
# Shortcut properties for retrieving recent records within resampled format
# =========================================================================

def resampled_records_in_delta(self, delta, rule):
    return resampled_records(self.records_in_delta(delta), rule)

@property
def resampled_records_in_hour(self):
    return resample_records(self.records_in_hour, 'T')


@property
def resampled_records_in_day(self):
    return resample_records(self.records_in_day, 'H')


@property
def resampled_records_in_week(self):
    return resample_records(self.records_in_week, 'D')


@property
def resampled_records_in_month(self):
    return resample_records(self.records_in_month, 'D')


@property
def resampled_records_in_year(self):
    return resample_records(self.records_in_year, 'M')
