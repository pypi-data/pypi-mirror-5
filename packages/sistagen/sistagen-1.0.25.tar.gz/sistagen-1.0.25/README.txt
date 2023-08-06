=====================
Simple Stat Generator
=====================


What's this?
============

Sistagen (Simple Stat Generator) is console tool that simplifies graph
plotting. It's main job is to parse configuration and call rrdtool to generate
desired graphs.

This app is kind of higher layer on rrdtool, allowing anything rrdtool allows,
but in easier to manage form.


Why?
====

RRDTool itself is great tool, but it's quite time consuming task to prepare
graph with it directly. On the other side, there are many bigger or lesser
(often all-in-one, and mostly web-oriented) applications, but they're
enforcing theirs philosophy, and having annoying "features".


How it works?
=============

At first, take a look on graph definition:

::

   echo "include templates.conf
   Graph test
      use disk-usage
      input-dir df-root" | sistagen

That would output file graph_400x100.png in current directory, containing
disk space utilization graph. Of course, you have to have df-root/ directory
with rrd files (generated with collectd - df plugin).

In this example, sistagen reads configuration from stdin. Thats because
no input files was given. You can pass as many files as you want, just by
giving they names of absolute path (TODO: describe more about pathes).

sistagen config1.conf config2.conf [...]


Configuration
=============

Sistagen configuration consists of list of declarations and attributes.

Declarations list:
 - include ARG - load and parse configuration from another file, given
                 as ARG
 - template NAME - create new template (named NAME) declaration
 - graph NAME - create new graph

Both graph and template means almost the same, with one difference:
template isn't graphed, it's only 'virtual' declaration, while all graph
declarations causes sistagen to plot them out.

Graph (and template) declarations should have some attributes. An attribute
in sistagen configuration is line, starting with at last one whitespace and 
beginning with keyword, followed by number of named values.
It's important that attribute must always refer to declaration, so:
1. all attributes that follows a declaration, belongs to that declaration
2. it's an error to pass attributes before any declaration

In its simplest case it looks like following:

::

   GRAPH|TEMPLATE name
      attribute1 name=val ...
      attribute2 ...
      ...

Most of attributes should have named values (except of 'use' and 'size').
Each value should be in form: "name value" or "name=value" (the equation 
symbol is optional).
      
      
List of allowed attributes:
 - use template-name - use template as current declaration base

 - input NAME FRRDFILE DS CF - create new input named NAME from file RRDFILE using DS and CF
 - input-file NAME RRDFILE - define file path to be used in input NAME
 - input-dir NAME PATH - define a directory that rrd file will be get from for input named NAME
 - input-ds NAME DS - define a datasource for input NAME
 - input-cf NAME CF - define a consolidation function for input NAME
   There could be as many inputs as needed.

 - output-dir PATH - define directory for output file
 - output-file FILE - define output file name or full path
 - output-prefix PREFIX - prefix for output file
 - output-suffix SUFFIX - suffix for output file
 - output-format FORMAT - output file format
   output file: OUTPUT-DIR + OUTPUT-PREFIX + SIZE + OUTPUT-SUFFIX + OUTPUT-FORMAT


 - option option-name option-value
 - option ...
 - ...
   any option that may be passed into rrdtool graph,
   for example: lower-limit, zoom, start, etc..


 - size SIZE [SIZE, ...]
   any number of dimensions of graphs to be generated
   each size would be used in output file name


 - line1|line2|line3|area (with EXPR | use NAME) [color COLOR] [text LEGEND] [stack]
 - gprint text TEXT (with EXPR | use NAME) get AGGR
   currently supported graphing methods
   for lines and areas there should be at last one of 'with' or 'use'
   keyword with corresponding value
   EXPR means any rpn expression (http://oss.oetiker.ch/rrdtool/doc/rrdgraph_rpn.en.html)
   NAME means any input name defined earlier
   AGGR means an aggregation function (one of CF)
 - comment text TEXT 
 

Graph and template declarations may be inherited. It means that when
one declaration inherits another then all attributes of parent would
be copied into child.

Example:
::

   Template A:
      attribute a

   Template B:
      use A # use A as base
      # attribue a is defined already


Templates
=========

There are some templates already prepared and shipped with applications, that 
lets fast and easy graph creation. 
Right now they are mostly focused on rrd files created by collectd, so with 
those files you may just create graph with only input-dir attribute.

Templates dir and current dir are added to config path (-C) by default.


Note
====

Please send me any reports and opinions as well. It would be nice to know
if this tool is useful for someone, so I may still work on this.