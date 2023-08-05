clc (command line charts)
=========================

Simple charts on the commandline (bar charts only for now). Read from stdin or
from a file.

install
-------

`pip install clc`. Done.

usage
-----

Give `clc` data on stdin or a filename, and see a command line chart.

    > cat ./fixtures/sample1.dat | clc
         Paris  ******************************  12
         Tokyo  *******  3
        London  ***********************************  14
    Washington  *****************  7

Adjust the width of the chart, and the symbol for the bars:

    > clc ./fixtures/sample1.dat -w30 --tick='~'
         Paris  ~~~~~~~~~~~~  12
         Tokyo  ~~~  3
        London  ~~~~~~~~~~~~~~~  14
    Washington  ~~~~~~~  7

Data should be formatted as in ./fixtures:

    Paris 12
    Tokyo 3
    London 14
    Washington 7

help
----

Via `--help`:

usage: clc [-h] [--verbose] [--width WIDTH] [--tick TICK] [infile]

clc: simple charts on the command line.

positional arguments:
  infile                data file (or stdin)

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v
  --width WIDTH, -w WIDTH
  --tick TICK, -t TICK

future
------

- better handle non-integer values
- use csv.Sniffer()
- tests
- colors
- vertical bar charts
