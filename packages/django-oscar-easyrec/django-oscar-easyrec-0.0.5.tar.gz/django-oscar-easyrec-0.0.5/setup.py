#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='django-oscar-easyrec',
      version='0.0.5',
      url='https://github.com/tangentlabs/django-oscar-easyrec',
      author="Jonathan Moss",
      author_email="jonathan.moss@tangentsnowball.com.au",
      description="easyrec recommendations module for django-oscar",
      long_description=open('README.rst').read(),
      keywords="Recommendation, easyrec",
      license='BSD',
      packages=find_packages(exclude=['tests','sandbox']),
      install_requires=[
            'django-oscar>=0.5,<0.6',
            'requests>=1.1.0,<1.2'
      ],
      classifiers=['Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python']
      )
