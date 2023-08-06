#!/usr/bin/env python

from distutils.core import setup
import platform

def build_params():
    params = {
      'name':'copycat-clipboard',
      'version':'1.0',
      'description':'easy way let use clip on command line with system clip',
      'author':'Colin Su',
      'author_email':'littleq0903@gmail.com',
      'url':'https://github.com/littleq0903/copycat.git',
      'py_modules':['copycat'],
	  'license':'MIT',
      'install_requires': ['clime', 'pyclip-copycat'],
    }
    if platform.system() == 'Windows':
        params['scripts'] = ['copycat.bat']
    else:
        params['scripts'] = ['copycat']
    
    return params

setup(
    **build_params()
)

