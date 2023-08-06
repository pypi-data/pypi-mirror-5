JPype - Python 3
################

From the `original Website <http://jpype.sourceforge.net/index.html>`_:

    JPype is an effort to allow python programs full access to java
    class libraries. This is achieved not through re-implementing
    Python, as Jython/JPython has done, but rather through interfacing
    at the native level in both Virtual Machines. Eventually, it should
    be possible to replace Java with python in many, though not all,
    situations. JSP, Servlets, RMI servers and IDE plugins are good
    candidates.

    Once this integration is achieved, a second phase will be started to
    separate the Java logic from the Python logic, eventually allowing
    the bridging technology to be used in other environments, I.E. Ruby,
    Perl, COM, etc ...

This GitHub fork is a Python 3 version of jPype.
**It does not support Python 2**.

This is a fork of `originell/jpype <https://github.com/originell/jpype>`_,
which originally aims to simplify the installation of jPype on Linux and
MacOS X.


Known Bugs/Limitations
**********************

* Java classes outside of a package (in the ``<default>`` package) cannot be
  imported.
* Fields or methods conflicting with a python keyword can't be accessed.
* Because of lack of JVM support, you cannot shutdown the JVM and then restart
  it.
* Some methods rely on the "current" class/caller. Since calls coming directly
  from python code do not have a current class, these methods do not work.
  The User Manual lists all the known methods like that.


Road map
********

Future developments of this fork of jPype :

* Stay close to the Python 2 version (patches, issues, ...)
* Convert tests in Python 3
* Convert examples in Python 3
* Review the code (Python and C++): clean up, add comments, ...
* Separate Python 3 specific code (Python and C++)


Requirements
************

The Python 3 development files and either the Sun/Oracle JDK/JRE Variant
or OpenJDK.

Debian/Ubuntu
=============

Debian/Ubuntu users will have to install ``g++`` and ``python3-dev``
first:

.. code-block:: bash

    sudo apt-get install g++ python3-dev


Red Hat/Fedora
==============

Same thing with Fedora users :

.. code-block:: bash

    su -c 'yum install gcc-c++ python3-devel'


Installation
************

Should be easy as

.. code-block:: bash

    sudo python3 setup.py install


If it fails...
==============

This happens mostly due to the setup not being able to find your
``JAVA_HOME``. In case this happens, please do two things:

#. You can continue the installation by finding the ``JAVA_HOME`` on
   your own ( the place where the headers etc. are) and explicitly
   setting it for the installation:

   .. code-block:: bash

      JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk-amd64 python3 setup.py install

#. Please create an Issue
   `on GitHub <https://github.com/tcalmant/jpype-py3/issues?state=open>`_ and
   post all the information you have.


Tested on
*********

* Mac OS X 10.8.4, with Oracle JDK 1.6.0 and 1.7.0
* Ubuntu 12.04, with OpenJDK 6 and 7
* Fedora 18 and 19, with OpenJDK 6 and 7
