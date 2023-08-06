Grid Map
-----------

A module to allow you to easily create jobs on the cluster directly from
Python. You can directly map Python functions onto the cluster without
needing to write any wrapper code yourself.

This is the ETS fork of an older project called Python Grid. It's a lot
simpler than the original version, because we use a Redis database for
storing the inputs/outputs for each job instead of the ZeroMQ-based
method they were using. The main benefit of this approach is you never
run into issues with exceeding the message length when you're
parallelizing a huge job.

For some examples of how to use it, check out map\_reduce.py
(for a simple example of how you can map a function onto the cluster)
and manual.py (for an example of how you can create list of
jobs yourself) in the examples folder.

For complete documentation go
`here <http://htmlpreview.github.io/?http://github.com/EducationalTestingService/gridmap/blob/master/doc/index.html>`__.

*NOTE*: You cannot use Grid Map on a machine that is not allowed to
submit jobs (e.g., slave nodes).

Requirements
~~~~~~~~~~~~

-  `redis-py <https://github.com/andymccurdy/redis-py>`__
-  `drmaa-python <http://drmaa-python.github.io/>`__
-  Python 2.6+

Recommended
~~~~~~~~~~~

-  `hiredis <https://pypi.python.org/pypi/hiredis>`__

License
~~~~~~~

GPLv3
