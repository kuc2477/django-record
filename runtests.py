from os import path
import sys

import django

from django.conf import settings


if not settings.configured:
    settings_dict = dict(
        INSTALLED_APPS=(
            'django_record',
            'django_record.tests'
        ),
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
            }
        },
    )

    # configure settings
    settings.configure(**settings_dict)
    if django.VERSION >= (1, 7):
        django.setup()


def runtests():
    sys.path.insert(0, path.dirname(path.abspath(__file__)))

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

    # run tests
    failures = runner_class(
        verbosity=2, interactive=True, failfast=False
    ).run_tests(test_args)

    # exit with errors
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
