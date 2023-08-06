===========
vizmdend
===========

vizmdend is an AMBER Molecular Dynamics mdend file Inspector.

A Command-line
===============

usage: vizmdend.py [-h] [--xfield XFIELD] mdendfile yfield

Plot a field from mdend AMBER file

positional arguments:
  mdendfile        mdend file name
  yfield           name of the field to plot

optional arguments:
  -h, --help       show this help message and exit
  --xfield XFIELD  optional field to be used as x-axis

B Graphical Interface
=====================

usage: vizmdend.pyw [-h] [--mdendfile MDENDFILE]

Plot a field from mdend AMBER file

optional arguments:
  -h, --help            show this help message and exit
  --mdendfile MDENDFILE
                        mdend file name

