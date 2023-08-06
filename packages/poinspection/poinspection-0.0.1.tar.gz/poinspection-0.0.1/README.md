Python oject inspection for ipython
===================================

ipython magic function %pi, print instance

Written and maintained by Luis Montiel <luismmontielg@gmail.com>

%pi, print instance
-------------------

    In [2]: obj_or_dict = {'akey': 'value', 'another': 'value2'}
    In [3]: %pi obj_or_dict
    dict
    akey           = 'value'
    another        = 'value2'

You can pass a pattern and a separator after the object:

    In [3]: %pi obj_or_dict anot
    dict
    another        = 'value2'

    In [4]: %pi obj_or_dict * '| '
    dict
    akey= 'value'| another= 'value2'

Installation
============

    pip install poinspection

Usage
=====

    %load_ext poinspection

To autoload when IPython starts:

- Create ipython profile config file, or skip if already present

      ipython profile create

   And you will have a default ipython_config.py in your IPython directory under profile_default

- Add/modify this ipython config file

      c.InteractiveShellApp.extensions = ['poinspection']

Information
===========

The IPython magic commands work for versions of IPython with the
decorators IPython.core.magic.magics_class and
IPython.core.magic.line_magic.

License
=======

Public domain. You can do whatever you want with this.
