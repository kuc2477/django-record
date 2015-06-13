from setuptools import setup


long_description = (
    open('README.rst').read() + '\n\n' +
    open('CHANGES.rst').read()
)

MAJOR = 0
MINOR = 2
MICRO = 2

VERSION = '%s.%s.%s' % (MAJOR, MINOR, MICRO)

setup(
    name='django-record',
    packages=['django_record'],
    version=VERSION,
    description='Models and mixins for recording changes in Django models',
    long_description=long_description,
    author='Jun Soo Ha',
    author_email='kuc2477@gmail.com',
    url='https://github.com/kuc2477/django-record/',
    install_requires=['django', 'pandas'],
    tests_require=["django", 'pandas', 'unipath', 'faker'],
    test_suite="runtests.runtests",
    license='GNU General Public License v2 (GPLv2)',
    platforms=['OS Independent', ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Framework :: Django',
    ]
)
