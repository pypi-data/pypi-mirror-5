==============================================
Simple access to the reference genomes at UCSC
==============================================

The package allows to easily download and use genomic data at UCSC.
This is essentially a thin "caching" wrapper around the ``twobitreader`` library.

Installation
------------

The simplest way to install the package is via ``easy_install`` or ``pip``::

    $ easy_install ucscgenome

Dependencies
------------

- ``twobitreader``

Usage
-----
The primary usage example is the following::

   from ucscgenome import Genome
   g = Genome('sacCer2')
   print str(g['chrI'][0:100])

On the second line of the above example the following steps are performed:

* The local ``cache directory`` is searched for the pre-downloaded genome data. If the data is readily available, it is opened for reading.
* If there is not cached version of the ``sacCer2`` genome, it is downloaded from the UCSC site to the cache directory.
* The local data is downloaded and stored using the compact `2bit <http://www.its.caltech.edu/~alok/reviews/blatSpecs.html>`_ format.

You can configure the details of the procedure by providing additional options to the ``Genome`` constructor::

   g = Genome('hg19', cache_dir='my_genomes', use_web=False)
   
which means that the genome data is to be searched for in the ``./my_genomes`` directory and in no case should a download be attempted, or::

   g = Genome('hg19', source_url_pattern='http://my.site.com/genomes/%(id)s/%(id)s.2bit')

which means that the genomic data is to be downloaded from your own server rather than UCSD's.

See also
--------

* Report issues and submit fixes at Github: https://github.com/konstantint/ucscgenome

Related packages
----------------

* http://pyucsc.readthedocs.org/
* https://pypi.python.org/pypi/twobitreader
* https://pypi.python.org/pypi/pyfasta
* https://pypi.python.org/pypi/cruzdb
* https://pypi.python.org/pypi/pyliftover
