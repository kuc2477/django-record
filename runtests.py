#!/usr/bin/env python

import sys
import django
import unipath

from django.conf import settings


if not settings.configured:
    settings_dict = dict(
        INSTALLED_APPS=(
            'django_record',
            'django_record.tests',
        ),
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
            }
        },
        MIDDLEWARE_CLASSES = ()
    )

    settings.configure(**settings_dict)
    if django.VERSION >= (1, 7):
        django.setup()


def runtests():
    parent = unipath.Path(__file__).ancestor(2)
    sys.path.insert(0, parent)

    # test for django under 1.8
    try:
        from django.test.simple import DjangoTestSuiteRunner
        runner_class = DjangoTestSuiteRunner
        test_args = ['tests']

    # test for django 1.8+
    except ImportError:
        from django.test.runner import DiscoverRunner
        runner_class = DiscoverRunner
        test_args = ['django_record']

    failures = runner_class(
        verbosity=2, interactive=True, failfast=False).run_tests(test_args)

    sys.exit(failures)


if __name__ == '__main__':
    runtests()
