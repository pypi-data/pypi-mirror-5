
dotfigure: DOT graph directive for Docutils
===========================================

DotFigure -- a directive for creating graphs in DocUtils.

Requirements
------------

DocUtils.

Setuptools.

A working Graphviz installation (http://www.graphviz.org/).

Options
-------

The following options are recognized:

``format`` : an output format recognized by dot
    Most formats are accepted, except things like x11, xlib and gtk.
    The default format is "png".
    See http://www.graphviz.org/doc/info/output.html for available formats.

``layout`` : a layout algorithm
    Selects one of these layout algorithms: dot, neato, twopi, circo, fdp, sfdp.
    The default layout is "dot".

``datauri`` : a flag
    Enables conversion of output file to a datauri.

``inline`` : a flag
    Includes contents of output file inline.

``file`` : a file path
    Uses file as source for graph.

``url`` : a url
    Uses file at url as source for graph.

All options for Image directive:

``alt`` : alternative text
    Text for the image alt attribute.

``height`` : an length
    Image height attribute.

``width`` : an length or percentage
    Image width attribute.

``scale`` : a percentage
    Image scale attribute.

``align`` : left, center, rigth, top, middle, bottom
    Alignment of image.

``target`` : a target name
    Target for image link.

All options for the CodeBlock directive:

``line-numbers`` : an integer
    Toggle line numbering for code display (used for text output formats)

Common options:

``name`` : an anchor name
    A HTML anchor name. This option will also affect the name of the generated graph file.

``class`` : a class name
    A CSS class name.

Usage
-----

Applications
''''''''''''

.. code::

  from dotfigure import register
  register()
  from docutils.core import publish_cmdline
  publish_cmdline(writer='html')


