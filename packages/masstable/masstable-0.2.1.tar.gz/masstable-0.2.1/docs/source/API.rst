API Reference
=================

.. automodule:: masstable.masstable


Table object creation
---------------------
.. autoclass:: Table
   :members: from_name, from_file, from_ZNM, to_file


Properties
----------
.. autoclass:: Table
   :members: Z, N, A, count, error, rmse, names


Derived quantities
------------------

.. autoclass:: Table
   :members: binding_energy, q_alpha, q_beta, s2n, s1n, s2p, s1p, ds2n, ds2p




Convenience methods
-------------------

.. autoclass:: Table
   :members:  __getitem__, select, not_in, odd_odd, odd_even, even_odd, at