.. _Python Programming Language: http://www.python.org/
.. _How To Create Your Own Freaking Awesome Programming Language: http://createyourproglang.com/
.. _Marc-Andre Cournoye: http://macournoyer.com/
.. _PyPi Page: http://pypi.python.org/pypi/mio-lang
.. _Project Website: https://bitbucket.org/prologic/mio-lang/
.. _Downloads Page: https://bitbucket.org/prologic/mio-lang/downloads


mio is a minimalistic IO programming language written in the
`Python Programming Language`_ based on MIo (*a port from Ruby to Python*)
in the book `How To Create Your Own Freaking Awesome Programming Language`_ by
`Marc-Andre Cournoye`_.

This project is being developed for educational purposes only and should serve as
a teaching tool for others wanting to learn how to implement your own programming
language (*albeit in the style of Smalltalk, Io, etc*). Many thanks go to `Marc-Andre Cournoye`_
and his wonderful book which was a great refresher and overview of the overall processing
and techniques involved in programming language design and implementation. Thanks also go to the
guys in the ``#io`` channel on the FreeNode IRC Network specifically **jer** nad **locks**
for their many valuable tips and help.

The overall goal for this project is to create a fully useable and working programming language
implementation of a langauge quite similar to `Io <http://iolanguage.com>`_ with heavy influence
from `Python <http://python.org>`_ (*because Python is awesome!*). This has already largely been
achived in the current version. See the `RoadMap <http://mio-lang.readthedocs.org/en/latest/roadmap.html>`_
for what might be coming up next.


Examples
--------

Factorial::
    
    Number set("!", method(
        (self < 2) ifTrue(return self)
        return (self * ((self - 1) !))
    ))

Hello World::
    
    World = Object clone
    World hello = method("Hello World!" println)
    
    World hello


Features
--------

- Homoiconic
- Message Passing
- Higher Order Messages
- Higher Order Functions
- Full support for Traits
- Object Orienated Language
- Written in an easy to understand language
- Supports Imperative, Functional, Object Oriented and Behavior Driven Development styles.


Installation
------------

The simplest and recommended way to install mio is with pip.
You may install the latest stable release from PyPI with pip::

    > pip install mio

If you do not have pip, you may use easy_install::

    > easy_install mio

Alternatively, you may download the source package from the
`PyPI Page`_ or the `Downloads page`_ on the `Project Website`_;
extract it and install using::

    > python setup.py install

You can also install the
`latest-development version <https://bitbucket.org/prologic/mio-lang/get/tip.tar.gz#egg=mio-dev>`_ by using ``pip`` or ``easy_install``::
    
    > pip install mio==dev

or::
    
    > easy_install mio==dev


For further information see the `mio documentation <http://mio-lag.readthedocs.org/>`_.
