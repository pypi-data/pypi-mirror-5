Eve
====
.. image:: https://secure.travis-ci.org/nicolaiarocci/eve.png?branch=master 
        :target: https://secure.travis-ci.org/nicolaiarocci/eve

Eve is an out-of-the-box, highly customizable and fully featured RESTful Web
API framework that you can use to effortlessly build and deploy your own APIs

Eve is Simple
-------------
.. code-block:: python

    from eve import Eve

    app = Eve()
    app.run()

The API is now live, ready to be consumed:

.. code-block:: console

    $ curl -i http://example.com/people/
    HTTP/1.1 200 OK

All you need to bring your API online is a database, a configuration file
(defaults to ``settings.py``) and a launch script.  Overall, you will find that
configuring and fine-tuning your API is a very simple process.

`Check out the Eve homepage <http://python-eve.org/>`_

License
-------
Eve is a `Nicola Iarocci`_ and `Gestionali Amica`_ open source project,
distributed under the `BSD license
<https://github.com/nicolaiarocci/eve/blob/master/LICENSE>`_. 

.. _`Nicola Iarocci`: http://nicolaiarocci.com
.. _`Gestionali Amica`: http://gestionaleamica.com
