#!/usr/bin/env python
from __future__ import unicode_literals

from setuptools import setup, find_packages

from tenancy import __version__


setup(
    name='django-tenancy',
    version='.'.join(str(v) for v in __version__),
    description='Handle multi-tenancy in Django with no additional global state using schemas.',
    url='https://github.com/charettes/django-tenancy',
    author='Simon Charette',
    author_email='charette.s+pypi@gmail.com',
    install_requires=(
        'django>=1.5',
    ),
    packages=find_packages(exclude=['test_settings']),
    include_package_data=True,
    license='MIT License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    extras_require={
        'hosts': ['django-hosts'],
        'mutant': ['django-mutant>=0.1.0'],
    }
)
