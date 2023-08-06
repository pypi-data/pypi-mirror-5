# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='django-stdimage',
    version='0.2.3',
    description='Django Standarized Image Field',
    author='garcia.marc',
    url='https://github.com/humanfromearth/django-stdimage',
    author_email='garcia.marc@gmail.com',
    license='lgpl',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    packages=['stdimage'],
    include_package_data=True,
    requires=['django (>=1.0)',],
)
