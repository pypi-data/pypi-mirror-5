#!/usr/bin/env python

# http://ericholscher.com/blog/2009/jun/29/enable-setuppy-test-your-django-apps/
# http://www.travisswicegood.com/2010/01/17/django-virtualenv-pip-and-fabric/
# http://code.djangoproject.com/svn/django/trunk/tests/runtests.py
import os
from os.path import dirname
import sys

# fix sys path so we don't need to setup PYTHONPATH
ABS_PATH = os.path.abspath(__file__)
APP_DIR = dirname(dirname(dirname(ABS_PATH)))
sys.path.insert(0, APP_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'rest_framework_extensions.runtests.settings'

import django
from django.conf import settings
from django.test.utils import get_runner


def usage():
    return """
    Usage: python runtests.py [UnitTestClass].[method]

    You can pass the Class name of the `UnitTestClass` you want to test.

    Append a method name if you only want to test a specific method of that class.
    """


def main():
    TestRunner = get_runner(settings)

    monkeypatch_default_settings();

    test_runner = TestRunner()
    if len(sys.argv) == 2 and sys.argv[1] != 'test':
        test_case = '.' + sys.argv[1]
    else:
        test_case = ''
    test_module_name = 'rest_framework_extensions'

    failures = test_runner.run_tests([test_module_name + test_case])

    sys.exit(failures)

def monkeypatch_default_settings():
    from rest_framework import settings

    PATCH_REST_FRAMEWORK = {
        # Testing
        'TEST_REQUEST_RENDERER_CLASSES': (
            'rest_framework.renderers.MultiPartRenderer',
            'rest_framework.renderers.JSONRenderer'
        ),
        'TEST_REQUEST_DEFAULT_FORMAT': 'multipart',    
    }

    for key, value in PATCH_REST_FRAMEWORK.items():
        if key not in settings.DEFAULTS:
            settings.DEFAULTS[key] = value


if __name__ == '__main__':
    main()
