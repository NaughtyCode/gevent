#!/usr/bin/env python
from __future__ import print_function
import os
import glob
from os.path import join, dirname, abspath, basename
import gevent


# do not generate .rst for the following modules as they imported into gevent package
# and covered there
SKIP = ['hub', 'timeout', 'greenlet']


template = '''.. AUTOGENERATED -- will be overwritten (remove this comment to save changes)

%(title)s
%(title_underline)s

.. automodule:: gevent.%(module)s
    :members:
    :undoc-members:
'''

directory = dirname(abspath(gevent.__file__))
print('Imported gevent from %s' % (directory, ))
modules = glob.glob(join(directory, '*.py')) + glob.glob(join(directory, '*.pyc'))
modules = set(basename(filename).split('.')[0] for filename in modules)
modules = set(name for name in modules if not name.startswith('_'))

import warnings
warnings.simplefilter('ignore', DeprecationWarning)


def generate_rst_for_module(module, do=True):
    rst_filename = 'gevent.%s.rst' % module
    exists = os.path.exists(rst_filename)
    if exists:
        autogenerated = 'autogenerated' in open(rst_filename).read(200).lower()
        if not autogenerated:
            return
    m = __import__('gevent.%s' % module)
    m = getattr(m, module)
    title = getattr(m, '__doc__', None)
    if title:
        lines = title.strip().splitlines()
        for line in lines:
            # skip leading blanks. Support both styles of docstrings.
            if line:
                title = line
                break
        title = title.strip().split('\n')[0]
        title = title.strip(' .')
    prefix = ':mod:`gevent.%s`' % module
    if title:
        title = prefix + ' -- %s' % (title, )
    else:
        title = prefix
    title_underline = '=' * len(title)
    params = globals().copy()
    params.update(locals())
    result = template % params
    if exists:
        if open(rst_filename).read(len(result) + 1) == result:
            return  # already exists one which is the same
    if do:
        print('Generated %s from %s' % (rst_filename, m.__file__))
        open(rst_filename, 'w').write(result)
    else:
        print('Would generate %s from %s' % (rst_filename, m.__file__))


def generate_rst(do=True):
    assert os.path.exists('contents.rst'), 'Wrong directory, contents.rst not found'
    for module in modules:
        if module not in SKIP:
            generate_rst_for_module(module, do=do)


def iter_autogenerated():
    for module in modules:
        rst_filename = 'gevent.%s.rst' % module
        exists = os.path.exists(rst_filename)
        if exists:
            autogenerated = 'autogenerated' in open(rst_filename).read(200).lower()
            if autogenerated:
                yield rst_filename


if __name__ == '__main__':
    import sys
    if sys.argv[1:] == ['show']:
        for filename in iter_autogenerated():
            print(filename)
    elif sys.argv[1:] == ['delete']:
        for filename in iter_autogenerated():
            print('Removing', filename)
            os.unlink(filename)
    elif sys.argv[1:] == ['generate']:
        generate_rst()
    elif sys.argv[1:] == []:
        generate_rst(do=False)
    else:
        sys.exit('Invalid command line: %s' % (sys.argv[1:], ))
