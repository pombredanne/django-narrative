import multiprocessing
assert multiprocessing
import re
from setuptools import setup


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'narrative/version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))


setup(
    name='django-narrative',
    version=get_version(),
    description='Django narrative',
    long_description=open('README.md').read(),
    url='https://github.com/ambitioninc/django-narrative',
    author='Josh Marlow',
    author_email='opensource@ambition.com',
    packages=[
        'narrative',
        'narrative.batteries',
        'narrative.migrations',
        'narrative.south_migrations',
        'narrative.management',
        'narrative.management.commands',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
    ],
    license='MIT',
    install_requires=[
        'django>=1.6',
        'django-manager-utils>=0.7.2',
        'django-tastypie>=0.12.1',
        'pytz>=2012h',
    ],
    tests_require=[
        'coverage',
        'flake8',
        'psycopg2',
        'django-nose',
        'mock',
        'south>=1.0.2',
        'django_dynamic_fixture',
        'django-extensions',
    ],
    # test_suite='run_tests.run_tests',
    include_package_data=True,
    zip_safe=False,
)
