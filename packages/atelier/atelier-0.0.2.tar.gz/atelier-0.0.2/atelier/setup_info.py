"""
This module is being execfile'd from `setup.py`, `atelier/__init__.py`
and possibly some external tools, too.

:copyright: Copyright 2013 by Luc Saffre.
:license: BSD, see LICENSE for more details.
"""
SETUP_INFO = dict(
  name = 'atelier', 
  version = '0.0.2',
  install_requires = ['Sphinx','unipath','python_dateutil'],
  scripts = ['scripts/per_project'],
  description = "A collection of tools for software artists",
  license = 'Free BSD',
  test_suite = 'tests',
  author = 'Luc Saffre',
  author_email = 'luc.saffre@gmail.com',
  url = "http://atelier.lino-framework.org",
  long_description="""\
`atelier` is my collection of tools for people who write and 
maintain multiple Python software projects.
It is not yet well documented, and so far there is 
nobody except me who uses it.
Let me know if you like it.
""",
  classifiers="""\
  Programming Language :: Python
  Programming Language :: Python :: 2.6
  Programming Language :: Python :: 2.7
  Development Status :: 4 - Beta
  Intended Audience :: Developers
  License :: OSI Approved :: BSD License
  Natural Language :: English
  Operating System :: OS Independent""".splitlines())

SETUP_INFO.update(packages = [str(n) for n in """
atelier
atelier.sphinxconf
""".splitlines() if n])
  
