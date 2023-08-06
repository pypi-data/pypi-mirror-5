#!/usr/bin/env python

from setuptools import setup

setup(
    name='django-auth-policy',
    version='0.3',
    description='Enforces a couple of common authentication policies for the '
                'Django web framework.',
    author='Fox-IT B.V.',
    author_email='fox@fox-it.com',
    maintainer='Rudolph Froger',
    maintainer_email='rudolphfroger@estrate.nl',
    url='https://github.com/rudolphfroger/django_auth_policy',
    license='BSD',
    packages=['django_auth_policy'],
    install_requires=['Django>=1.5'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Topic :: Security',
        'Topic :: Internet :: WWW/HTTP :: Session',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
