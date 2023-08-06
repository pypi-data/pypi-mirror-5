============
Installation
============

Install dependencies first (\*buntu Linux)
------------------------------------------
Ts2mkv utilizes avconv, ProjectX and MKVToolNix via their command line interfaces. ProjectX is bundled with ts2mkv but it requires Java. Setup script requires Python Distutils Enhancements.

All the required packages can be installed as follows::

  [sudo] apt-get --yes --quiet install python-setuptools openjdk-7-jre libav-tools libavcodec-extra-53 mkvtoolnix

Installing ts2mkv as a Python module
------------------------------------
If you have Python installed, and you want to install ts2mkv as a Python module, then enter in ts2mkv source code root and say::

  [sudo] python setup.py install


Windows notes
-------------
Ts2mkv works perfectly in Windows but you have to download and install the required 3rd party software manually. See at least the following links:

  http://win32.libav.org/releases/
  
  https://www.bunkus.org/videotools/mkvtoolnix/downloads.html#windows

Install also Java from somewhere.

Note: The 3rd party executables must be found either from PATH **or** alternatively their directories must be defined in paths_win.ini file. Ts2mkv for Windows comes with the following default directory configuration::

  avconv=C:\utils\libav\win64\usr\bin
  java=C:\Program Files (x86)\Java\jre7\bin
  MKVToolNix=C:\Program Files (x86)\MKVToolNix

If you installed ts2mkv as a Python module you should make sure that python.exe, ts2mkv.cmd and mkvenc.cmd can be found from PATH. These files can be found for example in the following directories::

  C:\Python27
  C:\Python27\Scripts

It's also possible to create a py2exe distribution package::

  python setup.py py2exe
