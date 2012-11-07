No Frills PDFScanner
====================

This application is a very simple scanning application. It only
supports PDF as the output format and you can only scan whole
pages. All pages scanned in between saves will be added to the same
multi-page PDF.

Running the program
-------------------
Make the file executable ("chmod 755 Scan.py") and run it from the
command line ("./Scan.py").

Alternatively, run it with the python interpreter ("python Scan.py")


Usage
-----

The scan button scans a page using the selected scanner
settings. Every page that is scanned gets added to the queue of pages
to be saved. 

The preview button performs a quick scan using the selected colour
mode. No pages gets saved to the queue.

The clear button removes all scanned pages from the queue.

The save button saves all queued pages into a multi-page PDF. 


Dependencies
------------
This program relies on:

 * python-reportlab
 * sane
 * python-imaging
 * python-imaging-sane
 * wxPython

These are the names of the relevant Fedora packages. They might vary
in your distribution.

Authors and Licensing
---------------------
This program has been written by Andreas Löf <andreas@alternating.net>
and is licensed under the GPLv3.

Limitations
-----------

The program only connects to the first scanner it detects. If you have
multiple scanners, this will cause trouble.

The program doesn't allow you to select a region of a page for
scanning, it only supports whole pages.

The program only outputs in A4. Adding support for other paper sizes
would be easy, and will be done if other users request it.

