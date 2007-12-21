Appscript is packaged using the standard Python Distribution Utilities (a.k.a. Distutils). To install appscript, cd to the appscript-0.18.0 directory and run:

	python setup.py install

Setuptools will be used if available, otherwise the setup.py script will revert to distutils.

If setuptools and bdist_mpkg are both installed, appscript can be installed by running the following command:

	python setup.py bdist_mpkg --open

This will build and open a binary installer for the appscript packages, documentation and examples.

Building appscript from source requires the gcc compiler (supplied with Apple's Developer Tools). Setuptools and bdist_mpkg are available from <http://cheeseshop.python.org/pypi>.

Appscript requires MacPython 2.3 or later and Mac OS X 10.3 or later.


======================================================================
NOTES

- Appscript underwent several non-backwards-compatible API changes for the 0.17.0 release. If upgrading from appscript 0.16.3 or earlier, please read the 'IMPORTANT - APPSCRIPT 0.17.0 API CHANGES' file in the Documentation folder BEFORE installing appscript 0.18.0.

- ASDictionary 0.9.0 or later is now required to use appscript 0.18.0's built-in help() method. If ASDictionary isn't installed, interactive help won't be available but appscript will continue to operate as normal.

- The osadict command-line tool bundled with previous versions of appscript has been replaced by the asdict tool bundled with ASDictionary 0.9.0 and later. To delete an existing osadict installation:

	sudo rm /usr/local/bin/osadict

- Appscript is currently 32-bit-only; 64-bit Python support is planned for the 0.19.0 release.

- Documentation and examples are installed at /Developer/Python.

- Appscript and aem are now moving towards beta 1 status, so please report any problems you have either with the appscript bridge itself or with scripting individual applications. In particular, appscript is a bit more sensitive to application bugs and terminology flaws than AppleScript is, so will sometimes fail on tasks where AppleScript works; identifying these problem apps so that internal/external workarounds can be developed will be useful.


======================================================================
COPYRIGHT

(C) 2006 - 2007 HAS <hhas -at- users - sourceforge - net> <http://appscript.sourceforge.net>

