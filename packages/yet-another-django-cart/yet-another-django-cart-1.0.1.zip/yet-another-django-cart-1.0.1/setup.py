#coding: utf-8
#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
        name='yet-another-django-cart',
        version='1.0.1',
        description='Django simple shopping cart, tests and south migrations included',
        maintainer=u'Otávio Soares',
        maintainer_email='otaviokk@gmail.com',
        license="GNU v3",
        url='https://github.com/otaviosoares/django-cart',
        packages=['cart', 'cart.migrations'],
        classifiers=[
            "Development Status :: 5 - Production/Stable", 
            "Environment :: Web Environment",
            "Framework :: Django",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
     )
