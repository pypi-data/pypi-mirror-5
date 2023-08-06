===============================
 Python Service Locator v 0.1.3
===============================

- The service locator pattern is a very simple but useful pattern that helps you remove glue code from application code.
- Decoupling the wiring of dependencies (glue code) can reduce your lines of code significantly and encourages loose coupling.
- This allows you to depend on abstractions rather than on concretions, it makes adding additional
  functionality to your application much easier.
- Configuration xml files are not pythonic and are often overcomplicated, class decorators are used instead.
- Concrete service implementations should be placed in a services folder. All services subfolders will be discovered using
  discover_services function and all containing modules will be auto-loaded.
- All services will be instantiated by the service locator as a singleton.


Usage
-----

Please see test/integration/test.py for a sample project. Suppose you have an abstract service class that looks like this:

.. code-block:: python

    #mime_recognizer_service.py
    class MIMERecognizerService(object):
        def recognizes_extension(self, extension):
            pass

        def get_MIME_type(self):
            pass

Register a service like this:

.. code-block:: python

    #pdf_recognizer.py
    from servicelocator.service_discoverer import discover_services

    @service_provider(MIMERecognizerService)
    class PDFRecognizer(MIMERecognizerService):
        def recognizes_extension(self, extension):
            return extension == ".pdf"

        def get_MIME_type(self):
            return "application/pdf"
            

You can register as many services and service providers as you like. When you retrieve all MIMERecognizerServices using the 
lookup_all function, one of the results in the list will be a PDFRecognizer() instance.

In order for the service discovery process to find the PDFRecognizer, you need to place it in a services folder. Your 
directory structure might look something like this (__init__.py's removed for demo purposes):

::

    -root/
        -main.py
        -mime_recognizers/
           -mime_recognizer_service.py
           -services/
               -pdf_recognizer.py
        -file_openers/
           -file_opener_service.py
           -services/
               -pdf_opener.py
                   
You discover services like this:

.. code-block:: python

    from servicelocator.service_discoverer import discover_services

     discover_services()
     
And that's it. The discover_services will walk the project directory tree and import all python modules inside services folders.

To retrieve service providers for a service, use the lookup functions like this:

.. code-block:: python

    from servicelocator.lookup import global_lookup

    MIMERecognizers = global_lookup.lookup_all(MIMERecognizerService)

This will get all concrete implementations of the MIMERecognizerService but the we do not need to know about the
existence of any of these concrete implementations. Adding extra functionality is as simple as dropping a file inside a
services directory, no additional code is necessary. This makes adding new service providers in a loosely coupled way very easy .

And if you know there is only one implementation of the service:

.. code-block:: python

    from servicelocator.lookup import global_lookup

    MIMERecognizer = global_lookup.lookup(MIMERecognizerService)



