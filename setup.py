from setuptools import setup, find_packages


long_description = (
    open('README.md').read() + '\n\n' +
    open('CHANGES.rst').read() + '\n\n' +
    open('AUTHORS').read()
)

MAJOR = 0
MINOR = 1
MICRO = 1

VERSION = '%d.%d.%d'.format(MAJOR, MINOR, MICRO)

setup(
    name='django-record',
    packages=['django_record'],
    version=VERSION,
    description='Models and mixins for recording changes in Django models',
    long_description=long_description,
    author='Jun Soo Ha',
    author_email='kuc2477@gmail.com',
    url='https://github.com/kuc2477/django-record/',
    pakcages=find_packages(),
    install_requires=['django>=1.7'],
    tests_require=["django>=1.7", 'faker'],
    test_suite="runtests.runtests",
    classifiers=[
        'Development Status :: 0 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPLv2 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
    ]
)
