.. pywws - Python software for USB Wireless Weather Stations
   http://github.com/jim-easterbrook/pywws
   Copyright (C) 2008-13  Jim Easterbrook  jim@jim-easterbrook.me.uk

   This program is free software; you can redistribute it and/or
   modify it under the terms of the GNU General Public License
   as published by the Free Software Foundation; either version 2
   of the License, or (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program; if not, write to the Free Software
   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

pywws.WindRose
==============

Introduction
------------

This routine plots one or more "wind roses" (see `Wikipedia <http://en.wikipedia.org/wiki/Wind_rose>`_ for a description). Like Plot.py almost everything is controlled by an XML "recipe" / template file.

Before writing your own template files, it might be useful to look at some of the examples in the example_graph_templates directory. If (like I was) you are unfamiliar with XML, I suggest reading the `W3 Schools XML tutorial <http://www.w3schools.com/xml/>`_.

XML graph file syntax
---------------------

Here is the simplest useful wind rose template. It plots wind over the last 24 hours. ::

  <?xml version="1.0" encoding="ISO-8859-1"?>
  <graph>
    <windrose>
      <ycalc>data['wind_ave']</ycalc>
    </windrose>
  </graph>

In this example, the root element graph has one windrose element which contains nothing more than a ycalc element.

The complete element hierarchy is shown below. ::

    graph
        windrose
            xcalc
            ycalc
            threshold
            colour
            yrange
            points
            source
            title
        start
        stop
        duration
        layout
        size
        fileformat
        lmargin, rmargin, tmargin, bmargin
        title

graph
^^^^^

This is the root element of the graph XML file. It does not have to be called "graph", but there must be exactly one root element.

windrose
^^^^^^^^

A separate plot is drawn for each windrose element, but all share the same time period.

start
^^^^^

This element sets the date & time of the wind roses. It is used in the constructor of a Python datetime object. For example, to start at noon (local time) on Christmas day 2008: ``<start>year=2008, month=12, day=25, hour=12</start>``. The default value is (stop - duration).

stop
^^^^

This element sets the date & time of the end of the wind roses. It is used in the constructor of a Python datetime object. For example, to end at 10 am (local time) on new year's day 2009: ``<stop>year=2009, month=1, day=1, hour=10</stop>``. The default value is (start + duration), unless start is not defined in which case the timestamp of the latest weather station hourly reading is used.

duration
^^^^^^^^

This element sets the duration of wind roses, unless both start and stop are defined. It is used in the constructor of a Python timedelta object. For example, to plot one week: ``<duration>weeks=1</duration>``. The default value is hours=24.

layout
^^^^^^

Controls the layout of the plots. Default is a grid that is wider than it is tall. The layout element specifies rows and columns. For example: ``<layout>4, 2</layout>`` will use a grid of 4 rows and 2 columns.

size
^^^^

Sets the overall dimensions of the image file containing the graph. Default is a height of 600 pixels and a width that depends on the layout. Any size element must include both width and height. For example: ``<size>800, 600</size>`` will produce an image 800 pixels wide and 600 pixels high.

fileformat
^^^^^^^^^^

Sets the image format of the file containing the plots. Default is png. Any string recognised by your installation of gnuplot should do. For example: ``<fileformat>gif</fileformat>`` will produce a GIF image.

lmargin, rmargin, tmargin, bmargin
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Over-rides the automatically computed left, right, top or bottom margin. Supply any positive real number, for example ``<lmargin>1.3</lmargin>``. Some experimentation may be necessary to find the best values.

title
^^^^^

Sets the overall title of the plots. A single line of text, for example: ``<title>Today's weather</title>``. This title appears at the very top, outside any plot area.

xcalc
^^^^^

Selects if data is included in the wind rose. The value should be a valid Python logical expression. For example, to plot a rose for afternoon winds only: ``<xcalc>data['idx'].hour &gt;= 12</xcalc>``. This allows aggregation of afternoon wind data over several days. Remember that data is indexed in UTC, so you need to use an expression that takes account of your time zone. The default value is 'True'.

ycalc
^^^^^

Selects the data to be plotted. Any one line Python expression that returns a single float value can be used. At its simplest this just selects one value from the "data" dictionary, for example: ``<ycalc>data['wind_ave']</ycalc>``. To convert to mph use: ``<ycalc>data['wind_ave'] * 3.6 / 1.609344</ycalc>``. You are unlikely to want to use anything other than 'wind_ave' here.

threshold
^^^^^^^^^

Sets the thresholds for each colour on the rose petals. Defaults are based on the Wikipedia example. The values should be a correctly ordered list of real numbers, for example: ``<threshold>0.5, 3.5, 7.5, 12.5, 18.5, 24.5, 31.5</threshold>`` approximates to the Beaufort scale, if ycalc has been set to convert windspeeds to mph.

colour
^^^^^^

Sets the colours of the threshold petal segments. Any sequence of integer values is accepted. The mapping of colours to numbers is set by gnuplot. Default value is 0, 1, 2, 3, etc.

yrange
^^^^^^

Sets the upper limits of the axes. The rose shows what percentage of the time the wind came from a particular direction. For example, if you live somewhere with a very steady wind you might want to allow higher percentages than normal: ``<yrange>91</yrange>``. Auto-scaling is also possible, using an asterisk: ``<yrange>*</yrange>``

points
^^^^^^

Sets the text of the compass points. The defaults are 'N', 'S', 'E' & 'W'. For graphs in another language you can over-ride this, for example: ``<points>'No', 'Zu', 'Oo', 'We'</points>``. (The preferred way to do this is to create a language file, see Localisation.py.)

source
^^^^^^

Select the weather data to be plotted. Permitted values are ``<source>raw</source>``, ``<source>hourly</source>``, ``<source>daily</source>`` and ``<source>monthly</source>``. Default is raw. Note that the different sources have different data dictionaries, so this choice affects ycalc.

title
^^^^^

Sets the title of the plot. A single line of text, for example: ``<title>Morning winds</title>``. This title appears within the plot area, above the threshold colour key.

Detailed API
------------

.. automodule:: pywws.WindRose
   
   .. rubric:: Functions

   .. autosummary::
   
      main
   
   .. rubric:: Classes

   .. autosummary::
   
      RosePlotter
