pyupyun - Feature complete upyun REST client
===

.. code-block:: pycon

    >>> import upyun
    >>> client = upyun.UpYun(bucket='bucket', auth=('user', 'pass'), stype=upyun.const.SPACE_TYPE_FILE)
    >>> resp = client.put('/test/test.txt', open('/tmp/test.txt'))
    >>> print resp.success
    True
    >>> print resp.url
    http://bucket.b0.upaiyun.com/test/test.txt

Compatible with [upyun REST API v1.5](http://static.b0.upaiyun.com/upyun_api_doc.pdf)

Installation
------------

.. code-block:: bash

    $ pip install pyupyun

Documentation
-------------

https://pyupyun.readthedocs.org

Test
----

To run the tests, first install the dependencies

.. code-block:: bash

    $ pip install -r requirements.txt

Then fill in all the blank settings(documented) at the beginning part of
`UpYunTestCase` class, which is inside `test/test_upyun.py`

And run

.. code-block:: bash

    $ py.test
