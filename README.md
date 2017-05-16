RESTCoder
==========

A collection of tools to auto-generate documentation and client stubs for RESTful services.

Team Members
============

 * Hiranya Jayathilaka
 * Stratos Dimopoulos


Try It
============

This library is described in a video at:
https://www.youtube.com/watch?v=ejF5p76L9Bw&t=10m57s

Commands to generate HTML [10:57]

   cd java-lib/
   ./jsgen.sh ../java-src/input/starbucks.json

Command to generate Python docs [15:49]

   cd bin/
   ./docgen.py -h
   ./docgen.py -f samples/starbucks.json -o starbucks
   open index.html

Command to generate Python client [18:26]

   cd bin/
   ./codegen.py -f samples/youtube.json -o youtube.py
   emacs youtube.py
   cp samples/test_youtube.py .
   python test_youtube.py
