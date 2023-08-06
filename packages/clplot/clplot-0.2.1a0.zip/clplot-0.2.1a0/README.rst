clplot
======

`clplot` is a command line utility to create plots and pages of plots from
csv-like files.

It is a thin wrapper over matplotlib with a few conveniences built in.

	
Rationale
=========

If you find yourself opening a csv file in a spreadsheet-like program to quickly plot and visualize your results, `clplot` may be a useful alternative for you. 

It allows you to get summary information about columns in your dataset, plot given variables, plot all variables, and specify the manner in which plots (or pages of plots) are formatted.


Installation
============

::

    $ pip install git+https://breisfeld@github.com/breisfeld/clplot.git

	
Dependencies
------------

-  numpy
-  matplotlib	
	
Usage
=====

	
Examples
--------

Assume that the data file is named `myfile.csv` and that it has a header
row with the names of the columns. Each subsequent row is assumed to
have numerical values corresponding to the header field names. For the
examples below, the header would have, at least, the field names (column
headers) `y1`, `y2`, `y3`, `y4`, `y5`, and `v1`.

*Show the help:*

::

    $ clplot-script.py -h

*Don't make any plots; just list all of the column names that are present in the data
file:*

::
  
    $ clplot-script.py -l myfile.csv

*Don't make any plots; just list some statistics and information about columns 'y1' and
'y2':*

::

    $ clplot-script.py -i -c y1 -c y2 myfile.csv

*Plot all of the columns in the file using the default independent variable (the one in the first column):*

::

    $ clplot-script.py myfile.csv

*Plot just the columns 'y1' and 'y2' and use 'v1' as the independent
variable:*

::

    $ clplot-script.py -c y1 -c y2 -x v1 myfile.csv

*Plot all of the columns except 'y3' and 'y4', put 12 plots on each
figure, and make the axis font size large:*

::

    $ clplot-script.py  -e y3 -e y4 -n 12 --fontsize=20.0 myfile.csv

*Plot columns matching the regular expression 'y.*\ (1\|5)' and put nine plots on each figure:\*

::

    $ clplot-script.py -n 9 -cr 'y.*(1|5)' myfile.csv

*(The regular expression may need different quoting, depending on the OS
or shell)*

*Plot all of the data columns using red, dashed, thick lines:*

::

    $ clplot-script.py --linecolor='red' --linestyle='--' --linewidth=5 myfile.csv

*Plot all of the data except those column names matching the regular
expression '.*\ y.\ *1', and assume that the entries in the file are
separated by tabs instead of commas:*

::

    $ clplot-script.py -er '.*y.*1' -d '\t' myfile.csv

	
On Windows, use `clplot.exe` instead of `clplot-script.py` in the
lines above.


License
=======

This program is freely available for anyone to use under an MIT license.
Please consult the MIT-LICENSE file.
