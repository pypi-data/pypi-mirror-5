AC.py - Python Autoconf
=======================

While trying to grasp autoconf for the first time, I realized that I
could do everything I wanted in Python, and so I started doing that
instead.

This is the earliest of the earliest of early stages, but for absolute
basic system testing functionality, it does work.

::

    #!/usr/bin/env python
    # Filename: configure
    import ac

    ac.test("testname, testfunc())
    ac.testlib("somelib")
    ac.testheader("someheader.h")

    $ ./configure --shell=bash --compiler=g++ --yes

AC.py also offers (well, plans to offer, but the syntax is supported
now), 'alternatives', which allows you to define how to handle failed
tests depending on your user's platform:

::

    ac.if_fail("testname", ("debian","ubuntu"), "sudo apt-get install somepkg")
    ac.if_fail("testname", ("rehat","centos","fedora"), "sudo yum install somepkg")

Future plans include variable substitution like autoconf has with .in
files.

It's nowhere near ready at this time, but I wanted to make sure that
'ac' could be the actual package name, because it's easy to remember and
looks familiar to anyone who is used to autoconf files.

For now, refer to ac.py docstrings for documentation. More will come
later!
