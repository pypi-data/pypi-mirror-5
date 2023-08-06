ExEmGel: Simple pythonic xml reader
===================================

ExEmGel is a wrapper around the standard ElementTree library.
It allow clean and simple access to xml.


.. code-block:: pycon
   >>> config = exemgel.parse("configuration.xml")
   >>> config.configuration.email.host
   'mail.example.com'
   >>> config.configuration.email.port
   25
   
Installation
------------

To install ExEmGel:, simply:

.. code-block:: bash
    
        $ pip install exemgel
         
    


