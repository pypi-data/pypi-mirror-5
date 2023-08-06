===========================
Nuclear Mass Table Toolkit
===========================

The Nuclear Mass Table Toolkit provides utilities to work with nuclear mass tables. At the moment the following tables are supported:

* **AME2003**: G. Audi, H. Wapstra, C. Thibault, *Nucl. Phys. A* **729** (2003) 337
* **AME2003all**: Same as above but including interpolated("#") values
* **AME2012**: G. Audi et al, *Chinese Physics C.*  **36**, No. 12(2012)
* **AME2012all**: Same as above but including interpolated("#") values
* **DUZU**: J. Duflo, A.P. Zuker, *Phys. Rev. C* **52** (1995)
* **FRDM95**: Moller, P. et al., *At. Data and Nuc. Data Tables* **59** (1995) 185
* **KTUY05**: H. Koura, T.Tachibana, M. Uno, M. Yamada, *Progr. Theor. Phys.* **113** (2005) 305
* **ETFSI12**: Y. Aboussir et al., *At. Data Nucl. Data Tables* **61** (1995) 127
* **HFB14**: S. Goriely, M. Samyn, J.M. Pearson, *Phys. Rev. C* **75** (2007) 064312

Usage:
---------

* Print first 5 elements from Audi 2003:

.. code-block:: python

	>>> from masstable import Table
	>>> Table('AME2003').head()
	Z  N
	0  1     8.07132
	1  0     7.28897
	   1    13.13570
	   2    14.94980
	   3    25.90150


* Calculate the root mean squared error of Moller, et al. *Atomic Data and Nuclear Data Tables*, **59** (1995), 185-351.

.. code-block:: python

	>>> Table('FRDM95').rmse(relative_to='AME2003')
	0.890859326191

* Calculate 2 neutron separation energies for even-even nuclei:

.. code-block:: python

	>>> table = Table('AME2012').even_even.s2n
	Z  N 
	2  2           NaN
	   4      0.975454
	   6      2.125034
	   8     -1.417666
	4  2           NaN
	       ...

* Select nuclei with Z,N > 28:

.. code-block:: python

	>>> condition = lambda Z,N: Z > 28 and N > 28
	>>> table.select(condition)
	30  30    28.016334
	    32    23.136434
	    34    20.978934
	    36    19.037934
	    38    17.250334
	    40    15.700534
	       ...

* Plot binding energies per nucleon:

.. code-block:: python

	>>> t = Table('AME2012')
	>>> (t.binding_energy/t.A).plot()

.. image:: http://i.imgur.com/eKX5S8M.png

Install
--------

Just do:

	pip install masstable


Requirements
-------------
	
* python >= 2.7
* pandas >= 0.11


Credits
--------
Yaser Martinez
