confiskus
=========


Confiskus is ini-file parse helper with simple inheritance feature.


Install
-------

.. code:: bash

   $ pip install confiskus


Usage
-----

Inheritance is accomplished by ``extends`` option in ``default`` section.

Content of ``dev_conf.ini``.

:: 

   [default]
   extends = base.ini

   [webservice]
   url = https://localhost:6543


Content of ``base.ini``.

::

    [webservice]
    user = web_service_user
    password = papluhaogrcalmikrpce
    url = https://ws.otherserver.com


Now while reading ``dev_conf.ini`` confiskus will pick up also ``base.ini``.

.. code:: pycon

    >>> import confiskus
    >>> config = confiskus.Confiskus().read('dev_conf.ini')
    >>> config.get('webservice', 'url')
    'https://localhost:6543'
    >>> config.get('webservice', 'user')
    'web_service_user'
