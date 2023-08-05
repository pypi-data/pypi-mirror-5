m7pubpylibs (MARIMORE Open Source Python Libraries)
=====================================
A set of basic utilities, libraries and python code being used 
by other packages in MARIMORE Inc.

To install, run ``python setup.py install``.

For development, use ``make develop`` to create symlink from python ``site-packages` dir to the working directory so you don't have to reinstall to test changes.

To test packaging, run ``make install_dist`` which would generate the ``sdist`` tarball first and install from that tarball.

To uninstall, run ``make uninstall``.

This project is released under the OSI BSD license
Please read LICENSE for more information

Updates
=======
