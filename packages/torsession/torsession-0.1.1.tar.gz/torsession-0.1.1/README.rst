==========
Torsession
==========

:Info: Torsession is an asynchronous session backend with mongodb for tornado.
:Author: Lime YH.Shi

.. image:: https://travis-ci.org/shiyanhui/monguo.png
        :target: https://travis-ci.org/shiyanhui/monguo

.. image:: https://pypip.in/v/monguo/badge.png
        :target: https://crate.io/packages/monguo

.. image:: https://pypip.in/d/monguo/badge.png
        :target: https://crate.io/packages/monguo


Installation
============
    
.. code-block:: bash

    $ pip install git+https://github.com/mongodb/motor.git
    $ pip install torsession
    
Dependencies
============

* tornado 3+
* motor 0.1+

Example
=======

1. Generate session after login::

    yield session.generate_session()

2. Clear session when logout::

    yield session.delete_session()

3. Get a value::

    yield session.get(key)

4. Set a value::

    yield session.set(key, value)

5. Delete a value::

    yield session.delete(key)

6. Refresh session id::

    yield session.refresh_session()

7. Get session id::

    session.session_id

8. Set session id::

    session.session_id = new_session_id
    