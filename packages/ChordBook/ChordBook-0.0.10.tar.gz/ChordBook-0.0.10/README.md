ChordBook
=========

A tool to manage books of chords for bands.

Input
-----

Data is stored in JSON format.

There are two 'objects' - these become 'Book' and 'Tune' objects internally
as follows.

Book contains:

* band - a string containing the band name
* version - a string containing a version string for the book
* tunes - an array of Tunes

Tune contains:

* name - the name of the tune
* composer - the name of the composer (optional)
* credit - name of the original artist (for covers, optional))
* time - the time signature of the tune. 
* key - the key of the tune
* transpose - the key we display the tune in (optional)
* structure - an array of chord elements indicating the structure of the tune
* chord elements - arbitrarily named, containing chord elements

Chord elements are structured as follows:

* A series of chord names separated by the string " | "
* Chord names are currently free-form
* Eg "Ebmaj7 | Bb7 | Gmb5 | Fm"
* Repeat sections may be specified using '|:' and ':|'
* HTML output prettifies '#', 'b', repeats, 'pause', 'maj7' and 'm7b5'

For now you need to enter your JSON directly.

See examples/test.cbk for an example.

Something like http://www.jsoneditoronline.org/ may help.

Output
------

Output is designed to be pluggable, so users can easily create their
own output formats at will. For now there are only two, 'text', and
'html', which produce text and html output respectively.

Output currently goes directly to stdout rather than files.

Roadmap
-------

See TODO.

Issues
------

* Entering JSON by hand is no fun.
* Text output is a) useless, b) probably broken
* HTML output is hideous.
* Sorting not yet properly handled. Should be optional.
* No option to produce multi-page HTML output.
* Other bugs I have not yet spotted (many, no doubt).



