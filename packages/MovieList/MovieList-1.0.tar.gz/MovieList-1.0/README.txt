
=============
MovieList 1.0
=============

A utility application to catalogue, sort, filter, and play media files on local 
disk. The catalogue can be imported using csv text, and it can be maintained by 
adding, editing, and deleting records.

In addition to flat lists of media, support is provided to group the media into 
'series' in a shallow tree structure. 

Installation
============

For Version 1.0 the only supported platform is Linux. It _should_ work with Mac, 
but I do not have a Mac available for verifying the port. The port to Windows 
is not possible at present (May 2013) because the Python-gi libraries are not 
available for that platform (it _may_ be possible to back-port to Python 2.7 and 
use PyGTK instead). 

System Requirements:
--------------------

    *   Python 3
    *   Gtk
    *   Python Gtk+ introspection bindings 3.4.2
    *   lxml >3.0 (and supporting libraries)

Installation (Linux):
---------------------

    1.  Unzip the tar.gz somewhere.

    2.  In a console window navigate to the UXBgtk-0.9 directory and run the
        following command as root (on Ubuntu/Debian use sudo):

            ``[sudo] python3 setup.py install``

    3.  On Ubuntu a desktop launcher is installed, which you should be able to
        find in the Dash and drag to the launcher bar.

Design Notes and Plans
======================

MediaList allows storage of data in two formats, a Python 'pickle' file, or an 
xml file. The pickle has some advantages for a large datadase, but the xml 
version makes it easier to transport data between other packages and manually 
edit the data when required.

Rather than use Python's own sax and dom parsers, the xml implementation is 
based on element trees, using lxml.

The playing of the media is delegated to VLC Media Player, which, of course, is 
assumed to be installed. A future version of MediaList may be able to choose the 
media player to use.

A simple import from csv text is available to facilitate creating a new file.
Future versions may enable importing to add to an existing database, possibly 
by using csv, but also possibly by extending the xml facilities.

Author:
=======

Bob Bowles <bobjohnbowles@gmail.com>

