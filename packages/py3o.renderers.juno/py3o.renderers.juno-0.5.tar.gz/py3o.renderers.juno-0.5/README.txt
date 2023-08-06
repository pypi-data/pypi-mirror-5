Juno for py3o
=============

py3o.renderers.juno is a Java driver for py3o to transform
an OpenOffice document into a PDF

It is intended to be used in conjunction with http://bitbucket.org/faide/py3o.renderserver
But can be used outside it if you wish.

Prerequisites
=============

Since this is a Java implementation you will need to install
jpype and to have a recent Java runtime on the rendering machine.
You will also need a running OpenOffice instance. (If you are on
windows this can be addressed by using the py3o.renderserver
Open Office service.)

This has been tested to build correctly with:

  - Oracle JDK 1.6 and OpenOffice 3.2.1 on Windows 7 and Windows server 2003
  - Oracle JDK 1.6 and LibreOffice 3.4 on Windows 7 64bit
  - OpenJDK 6 and LibreOffice 3.4 on Linux (Ubuntu and RHEL 5)
  - OpenJDK 7 and LibreOffice 4.0.4 on Linux (Ubuntu 13.04) with some deprecation warnings but it still works

For example if you are on Ubuntu you should run this command::

  $ sudo apt-get install default-jdk

Usage
=====

::

    from py3o.renderers.juno import start_jvm, Convertor, formats
    import datetime

    # first arg is the jvm.so or .dll
    # second arg is the basedir where we can find the basis3.3/program/classes/unoil.jar
    # third argument it the ure basedir where we can find ure/share/java/*.jar containing
    # java_uno.jar, juh.jar, jurt.jar, unoloader.jar
    # the fourth argument was the openoffice version but is no more used
    # fifth argument is the max memory you want to give to the JVM
    start_jvm(
            "/usr/lib/jvm/java-7-openjdk-amd64/jre/lib/amd64/server/libjvm.so",
            "/usr/lib/libreoffice",
            "/usr/lib",
            "",
            140)
    c = Convertor("127.0.0.1", "8997")

    t1 = datetime.datetime.now()
    c.convert("py3o_example.odt", "py3o_example.pdf", formats['PDF'])
    t2 = datetime.datetime.now()

For more information please read the example provided in the examples dir and read the API documentation.

Installation
============

Requirements
~~~~~~~~~~~~

Unfortunately a direct easy_install will not work because we require JPype and jpype is neither on PyPi nor easy_installable
from an URL.

On linux You'll need to download and unzip JPype on your machine and easy_install from the source dir after setting your JAVA_HOME::

  $ wget http://sourceforge.net/projects/jpype/files/JPype/0.5.4/JPype-0.5.4.2.zip/download
  $ unzip JPype-0.5.4.2.zip
  $ cd JPype-0.5.4.2/
  $ export JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64
  $ python setup.py build
  $ python setup.py install

The really important part is the export JAVA_HOME variable that you MUST set correctly for the compilation to work.
The JAVA_HOME variable is only important if you want to compile, you will not need this variable at runtime

On windows you can easy_install a binary release easily like this::

  $ easy_install -UZ http://sourceforge.net/projects/jpype/files/JPype/0.5.4/JPype-0.5.4.2.win32-py2.7.exe/download

Driver install
~~~~~~~~~~~~~~

Once JPype is correctly installed in your desired python you can proceed with a normal installation::

  $ easy_install -UZ py3o.renderers.juno

Driver compilation and installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

NOTE: this is optionnal and reserved for developpers who want to compile the jar file by themselves

If you want to install from source you'll need to clone our repository::

  $ hg clone http://bitbucket.org/faide/py3o.renderers.juno
  $ cd py3o.renderers.juno/java/py3oconvertor
  $ ./compilelibroffice.sh
  $ cd ../../
  $ python setup.py develop

Please note how you must first compile the jar file with our script (some more example scripts are available for windows and OpenOffice).
If something fails, first try to edit the script and find if all referenced jar files are present on your system.
