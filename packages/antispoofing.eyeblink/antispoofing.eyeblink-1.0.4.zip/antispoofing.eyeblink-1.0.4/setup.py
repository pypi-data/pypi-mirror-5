#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='antispoofing.eyeblink',
    version='1.0.4',
    description='Eye-blinking counter-measures for the REPLAY-ATTACK database',
    url='http://pypi.python.org/pypi/antispoofing.eyeblink',
    license='GPLv3',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,

    namespace_packages=[
      "antispoofing",
      ],

    install_requires=[
      "setuptools",
      "bob >= 1.1.0",
      "xbob.db.replay",
    ],

    entry_points={

      'console_scripts': [
        'framediff.py = antispoofing.eyeblink.script.framediff:main',
        'make_scores.py = antispoofing.eyeblink.script.make_scores:main',
        'count_blinks.py = antispoofing.eyeblink.script.count_blinks:main',
        'merge_scores.py = antispoofing.eyeblink.script.merge_scores:main',
        'make_movie.py = antispoofing.eyeblink.script.make_movie:main',
        ],

      },

)
