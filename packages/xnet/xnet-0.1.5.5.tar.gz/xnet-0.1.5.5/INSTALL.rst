
============================================
Xnet install instructions
============================================

Debian 6
========

Development packages are needed to build a newer gevent
than what debian ships with.

    $ sudo apt-get install gcc
    $ sudo apt-get install libevent-dev
    $ sudo apt-get install python-dev
    $ sudo apt-get install python-pip
    $ sudo apt-get install python-openssl

Optionally, if you want to contain xnet in a local directory
instead of making a system installation:

    $ sudo apt-get install python-virtualenv
    $ virtualenv pyenv && cd pyenv && . bin/activate

Finally, install gevent and xnet:

    $ pip install gevent==0.13.8
    $ pip install xnet



Debian 7
========

The same procedure as for Debian 6 but we can use the python-gevent
package right away instead of compiling our own.

    $ sudo apt-get install python-pip
    $ sudo apt-get install python-openssl
    $ sudo apt-get install python-gevent

Optionally, if you want to contain xnet in a local directory
instead of making a system installation:

    $ sudo apt-get install python-virtualenv
    $ virtualenv pyenv && cd pyenv && . bin/activate

Finally, install xnet:

    $ pip install xnet



Backtrack 5R2
=============

    $ sudo apt-get install python-dev
    $ sudo apt-get install python-openssl
    $ sudo apt-get install python-pip
    $ sudo apt-get install libevent-dev

Optionally, if you want to contain xnet in a local directory
instead of making a system installation:

    $ sudo apt-get install python-virtualenv
    $ virtualenv pyenv && cd pyenv && . bin/activate

Finally, install gevent and xnet:

    $ pip install gevent==0.13.8
    $ pip install xnet



OSX
===

Gevent 0.13.8 misbehaves under OSX, but the development release 1.0rc2 works.
This must be compiled so Xcode is a requirement.  The list below may be incomplete.

Optional if you want to contain xnet in a local directory
instead of making a system installation.

    $ sudo port install py-virtualenv
    $ virtualenv pyenv && cd pyenv && . bin/activate

And then gevent.

    $ pip install cython -e git://github.com/surfly/gevent.git@1.0rc2#egg=gevent

