About
=====

This script comes in support of the submitted paper:

*Low-bandwidth and non-compute intensive remote
identification of microbes from raw sequencing reads*.

- It requires:

    - Python 3.3 (note the ".3")

    - bowtie2 (parameter "-a", try "--help")

- It is self-documented (try "-h" or "--help").

- It is working on FASTQ or gzipped-FASTQ files, possibly on BAM files

Be gentle and please do not hammer the server like there is no tomorrow.

The latest released versions of the package will always be on Pypi.

Usage
=====

This installs as a regular Python package:

  python setup.py install

The module can be run directly:

  python -m dnasnout_client.console

Help is available with:

  python -m dnasnout_client.console --help


Oh, and here is a screenshot:

.. image:: http://cbs.dtu.dk/~laurent/dnasnout/static/screenshot.png
   :alt: Screenshot
   :align: center

 
