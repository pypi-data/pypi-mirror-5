PNW
===

Latest version see `Bitbucket`_.

pnw is a text processing tool with a wide range of applications. It can
be used to compile chunks of text from various sources into a new text
file. The advantage over cut-and-paste techniques is that changes in the
source file are automatically followed. Secondly, we provide a thin
wrapper around the pandoc document converter. Therefore, chunks of text
can be converted from and to a wide range of lightweight markup
languages as well as html and tex/latex. Although literate programming
has become a little out of fashion, pnw can be used as a literate
programming tool, too. Not surprisingly, pnw itself and its
documentation is written using pnw. pnw is remotely inspired by noweb
and heavily inspired by (even borrowing part of the syntax from)
`antiweb <https://pypi.python.org/pypi/antiweb/0.2.2>`_. An important
feature of pnw, which is not present in antiweb, is the support of
namespaces. This allows to create reusable *block libraries* which can
be imported and addressed in a *dot-notation syntax* similar to python
modules.

A pnw file is a text file with tags defining named blocks of text. In a
way this is similar to an xml file. Tags may be hidden behind comment
characters, such that the file remains processable by another program.
The blocks of text from various pnw files can be processed and rendered
by another pnw file.


Documentation
-------------

The documentation is written in ``latex``. To compile the
pdf ``pnw-doc.pdf`` run::

    make doc

from the command line. You can also find pnw on the 
python package index. There pnw-doc.pdf is provided. I don't
put it under version control because it will unnecessarily 
inflate the repo.

Example
-------

Assuming that pnw is installed, from the main directory of the pnw
package open an interactive python session, I recommend to use
``ipython``, and write

::

    import pnw
    pnw.pnwimport('pnw.pnw','')

Now you can explore the pnw document tree of the ``pnw.pnw`` source file
by inspecting the dictionary

::

    pnw.chunks

To see the structure of a block, just print its repr

::

    pnw.chunks['moduledoc']

To render it, try

::

    print pnw.chunks['moduledoc'].render(indent=0,depth=2,toformat='rst')



The pnw source consists of one file ``pnw.pnw``. It is a working python
file containing pnw tags hidden behind the ``#`` comment character. To
produce a clean python file we invoke (compare the makefile in the main
directory)

::

    python ./pnw.pnw  -F pnw.pnw > pnw.py

The ``-F`` directive means that the whole file is treated as one block
named ``u''``. The previous command is used when installing pnw for the
first time.

The main driver file for the documentation is ``pnw-doc.pnw`` in the
``doc`` directory. Here is the head of this file

::

    #@chunk(main,format=latex)
    #@path(../..)
    #@path(..)
    #@import(latex-blocks.tex)
    #@import(md-blocks)
    #@import(pnw.pnw)
    #@include(ltxheader)

First the whole file is declared to be a block named *main* which is
``latex`` formatted. Then we add the first two parent directories to the
search path for imports. Then the files ``latex-blocks.tex``,
``md-blocks``, ``pnw.pnw`` are included into the main namespace ``u''``.
The block ``ltxheader``, which contains what its name says, and which
can be found in ``latex-blocks.tex`` is included.

``pnw-doc.pnw`` contains a little of the documentation written in
``latex``. Mostly, it includes blocks from other files. The bulk of the
documentation, written in ``markdown``, can be found in ``md-blocks``.

Finally, an executable ``latex`` file is produced by invoking

::

    pnw -Rmain pnw-doc.pnw > pnw-doc.tex



pnw is on `Bitbucket`_ and on `PyPi`_.

.. _Bitbucket: http://www.bitbucket.org/MLBN/2013-pnw
.. _PyPi: https://pypi.python.org/pypi/pnw
