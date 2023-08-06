ChordBook
=========

A tool to manage books of chords for bands.

Options
-------

*  -h, --help            show this help message and exit
*  -v, --version         show version and exit
*  -c, --currentdir      write to current directory instead of a subdirectory
                         named after the output format
*  -f FORMAT, --format=FORMAT
                         output format: 'text' or 'html' (default is html)
*  -i INFILE, --input=INFILE
                         location of JSON-formatted .cbk file with song data
*  -o OUTFILE, --output=OUTFILE
                         specify name of output file directly;
                         default is to change suffix of input file
*  -s, --stdout          send output to stdout instead of writing to file


Input
-----

Data is stored in JSON format, in files suffixed .cbk by convention.

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
own output plugins easily. For now there are only two, 'text', and
'html', which produce text and html output respectively.

See the chordbook/output directory for code. Outputters inherit from
the _base.py base class.

Default output format is html.

By default an input file foo.cbk will produce output written to html/foo.html

If the -s switch is given, output is sent to stdout instead.

If the -c switch is given, output is sent to the current directory instead of
a subdirectory named after the output format.

Using the -o OUTFILE switch, the name of the output file can be specified directly.

Roadmap
-------

See TODO.

Issues
------

* Entering JSON by hand is no fun.
* Text output is useless, 
* HTML output is hideous.
* Sorting not yet properly handled. Should be optional.
* No option to produce multi-page HTML output.
* Other bugs I have not yet spotted (many, no doubt).



