
=============
MovieList 1.4
=============

A utility application to catalogue, sort, filter, and play media files on local 
disk. The catalogue can be imported using csv text, and it can be maintained by 
adding, editing, and deleting records.

In addition to flat lists of media, support is provided to group the media into 
'series' in an arbitrarily deep tree structure. 

The latest addition for v1.4 is the ability to print out a list of the media.

Installation
============

For Versions up to 1.4 the only supported platform is Linux. It *should* work 
with Mac, but I do not have a Mac available for verifying the port. 

The port to Windows is not possible at present (July 2013) because the Python-gi 
libraries are not available for that platform (it *may* be possible to back-port 
to Python 2.7 and use PyGTK instead - I have not tried it and don't plan to 
anytime soon). 

System Requirements:
--------------------

    *   Python 3
    *   Gtk
    *   Python Gtk+ introspection bindings 3.4.2 (part of gi)
    *   lxml >3.0 (and supporting libraries)
    *   cairo (part of gi)
    *   WebKit (part of gi)

Installation (Linux):
---------------------

    1.  Unzip the tar.gz somewhere.

    2.  In a console window navigate to the MovieList-1.3 directory and run the
        following command as root (on Ubuntu/Debian use sudo):

            ``[sudo] python3 setup.py install``

    3.  On Ubuntu a desktop launcher is installed, which you should be able to
        find in the Dash and drag to the launcher bar.
        
Upgrades
========

Upgrading does not require removal of the older version. 

However, to avoid compatibility issues with the configuration file, any existing
configuration should be removed or renamed before running an update for the 
first time. Any configuration you want to recover can be copied into the new 
configuration from the saved one after the first run. 

On Linux, the user's configuration file can be found at 
~/.config/MovieList/MovieList.cfg

Design Notes and Plans
======================

MovieList allows storage of data in two formats, a Python 'pickle' file, or an 
xml file. The pickle has some advantages for a large database, but the xml 
version makes it easier to transport data between other packages and manually 
edit the data when required. 

Rather than use Python's own sax and dom parsers, the xml implementation is 
based on element trees, using lxml.

To print the movie data, the lxml element tree model of the data is used to 
generate html via an xslt transform. The html is fed into a WebView for parsing 
and rendering, and to administer the print interface. 

(It should be possible to use weasyprint to do the parsing and rendering, but
there seem to be incompatibilities between weasyprint and gnome introspection).

The playing of the media is delegated to VLC Media Player, which, of course, is 
assumed to be installed. A future version of MovieList may be able to choose the 
media player to use.

A simple import from csv text is available to facilitate creating a new file.
Future versions may enable importing to add to an existing database, possibly 
by using csv, but also possibly by extending the xml facilities.

Author:
=======

Bob Bowles <bobjohnbowles@gmail.com>
