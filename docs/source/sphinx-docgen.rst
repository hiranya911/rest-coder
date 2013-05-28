Sphinx API Doc Generator
========================

`Sphinx <http://sphinx-doc.org>`_ is an open source documentation generation tool. It was originally created for the new Python documentation, and it is the framework of choice when it comes to documenting Python based projects and APIs. However the flexibility and versatility of Sphinx makes it suitable for documenting a wide range of other projects and software APIs including RESTful web APIs.

To create documentation using Sphinx, one must first create the necessary documentation files in the `reStructuredText <http://sphinx-doc.org/rest.html>`_ format. This is a simple textual format which allows the author to specify text formatting and layout information using text annotations and markup. In many ways, reStructuredText is similar to the markup languages used by documentation wikis and LaTeX. Once the documentation is created in the reStructuredFormat, these files are fed to the Sphinx documentation compiler which is capable of generating intelligent and professional looking project documentation in a number of output formats including HTML and LaTeX. The documentation of REST Coder, which you are reading right now has also been created using reStructuredText and compiled into HTML using the Sphinx compiler.

The REST Coder's Sphinx API Doc Generator operates in two steps.

 * Given a REST API description (in JSON) as the input, auto generate API documentation in the reStructuredText format.
 * Execute Sphinx compiler on the reStructuredText files created in the previous step to generate the final HTML based output.

The next few sections describe how to use the Sphinx API Doc Generator and what to expect from it as the output.

Using the Doc Generator
-----------------------

REST Coder's Sphinx API Doc Generator requires Python 2.7 and the Sphinx documentation engine to be installed. If these tools are already available, simply head over to the ``bin`` directory of the REST Coder installation and execute the script named ``docgen.py`` as follows. ::

  ./docgen.py -f /path/to/api/description.json -o /path/to/output/directory

This will load the specified API description file and create the Sphinx documentation at the specified output directory. If the output directory does not exist, it will be created by the tool.

It is also possible to load the input API description from a HTTP/S URL. ::

  ./docgen.py -u http://example.com/description.json -o /path/to/output/directory

By default the HTTP ``OPTIONS`` method will be used to pull the API description from the input URL. To use a different method use the ``-m`` flag.

To see the full list of command line options supported by the Sphinx Doc Generator, run ``docgen.py`` with the ``-h`` flag. ::

  ./docgen.py -h

Output Format
-------------

The Sphinx API Doc Generator creates a collection of reStructuredText (RST) files in the output directory and compiles them into HTML by default. Generated HTML files will also be stored in the same output directory and therefore after a successful run the output directory will contain both RST files and HTML files. You may manually execute the ``sphinx-builder`` command-line utility on the generated RST files to export the API documentation into a different format (e.g. LaTeX). If you want REST Coder to directly export the API documentation into a different (non-HTML) format, use the ``-e`` flag on the ``docgen.py`` utility.

What to Expect in the Generated Output?
---------------------------------------

The output created by the Sphinx API Doc Generator consists of an index page (index.rst/index.html) and a collection of other pages. The index page provides a description of the API and lists all its resources, operations and data models. These list entries link to other pages which provide in-depth details regarding the resources, operations and data types used by the API. Finally the index page lists all the base URLs (endpoints) of the web API and its licensing information.

The Doc Generator creates one page per resource defined in the API. These resource pages have multiple sections, one per operation. Each of these sections describes the API operation, its input and output types, HTTP status codes and also provides a sample `Curl <http://curl.haxx.se>`_ command to invoke the operation. Information regarding request/response media types, possible error conditions and sample JSON responses are also given where appropriate.

This tool also generates one page per complex data type defined in the API. These pages describe the data type and lists all the fields in each complex type. Resource pages link to these data model pages where appropriate. A data model page may link to other data model pages where necessary.

Project Metadata
----------------

Sphinx embeds some project metadata entries in each of the generated pages. These include project name, version and copyright information. The REST Coder's Sphinx API Doc Generator uses API metadata values extracted from the input API description to fill these entries in.

=======================  =====================
Project Metadata Entry     API Metadata Entry
=======================  =====================
Project Name		 API Name
Project Version		 API Version
Copyright Owners	 API Owner
=======================  =====================

Sphinx Template
---------------

Sphinx uses a special template file to load various project metadata, global layout settings and other runtime options. The REST Coder's Sphinx Doc Generator is shipped with a default template file which control the look and feel of all the generated API docs. This file is named ``sphinx_template.py`` and it can be found in the ``python-lib`` directory of the RESTCoder distribution. You may modify this file manually to assert more control over the behavior and layout of the API docs generated by the Sphinx API Doc Generator tool.