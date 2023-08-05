==================
infrae.testbrowser
==================

`infrae.testbrowser` is test browser for WSGI applications sharing the
same ideas than `zope.testbrowser`_. It only has lxml and
zope.interface as dependency.

A Selenium version of the same browser is available in this package as
well. It share the same API than the default one, and requires
Selenium 2 to work.

.. contents::

API
===

Browser
-------

``infrae.testbrowser.browser.Browser``
   Test browser. You instantiate a new one by giving your WSGI
   application to test as arguments to the constructor. The
   application will be available via ``localhost``.

Example::

  >>> browser = Browser(MyWSGIApplication)

On the browser you have the following methods:

``open(url, method='GET', query=None, form=None, form_enctype='application/x-www-form-urlencoded', data=None, data_type=None)``
   Open the given `url`, with the given `method`. If query is
   provided, it will be encoded in the URL. If form is provided, it
   will be set as payload depending of `form_enctype`
   (`application/x-www-form-urlencoded` or `multipart/form-data`). An
   authentication can be provided in the URL (via
   ``user:password@localhost``). As the host part doesn't really have
   any meaning, you can directly specify a path as URL. It return the
   HTTP status code returned by the application.  An alternative to `form` is
   the `data` and `data_type` parameters.  The param `data` is the pre-encoded
   body of the request, and `data_type` is the the content type of the body.
   These parameters are useful for http PUT.

``reload()``
   Reload the currently open URL (sending back any posting data).

``login(username, password=_marker)``
   Set an basic authorization header in the request to authenticate
   yourself with the given `username` and `password`. If `password` is
   not provided, `username` is used as password.

``set_request_header(key, value)``
   Add an header called `key` with the value `value` used while
   querying the application.
   Headers are set for all further queries.

``get_request_header(key)``
  Get the value of an header used while querying the
  application. Return None if there is no matching header.

``clear_request_headers()``
  Remove all sets headers used while querying the
  application. Authentication one included.

``get_link(content)``
  Return a link selected via content.

``get_form(name=None, id=None)``
  Return a form selected via its `name` or `id` attribute (at least
  one of them is required).

The following properties are helpful as well:

``url``
  Currently viewed URL, without the hostname part, but with query data
  and so.

``location``
  Currently viewed path. **It is recommanded** to use this in your
  test instead of ``url``. In case of Selenium testing, the URL will
  change depending of your local testing setup, meaning if your
  Selenium is not on the same computer than your test suite, the URL
  won't be localhost).

``history``
  Last previously viewed URLs.

``method``
  Method used to view the current page.

``status``
  HTTP status for the currently viewed page.

``status_code``
  HTTP status code as an integer for the currently viewed page.

``content_type``
  Content type of the currently viewed page.

``headers``
  Dictionary like access to response headers.

``cookies``
  Dictionary like object to access existing cookies.

``contents``
  Payload of the currently viewed page.

``html``
  If the response was an HTML document, this contains an LXML parsed
  tree of the document.

``xml``
  If the response was an XML response, this contains an LXML parsed
  tree of it.

``json``
  If the response was a JSON response, this contains the loaded JSON
  object.

``options``
  Access to browser options.


Browser cookies
---------------

You can access the currently set cookies with the dict-like object ``cookies``
available on the browser::

   >>> browser.cookies['mycookie']
   mycookie=myvalue

In addition to default dictionary methods, this object as the following methods:

``add(name, value)``
   Add a new cookie called ``name`` with the given value ``value``.

``clear``
   Clear all set cookies.


Browser options
---------------

The following options are attributes of the ``options`` object,
example::

   >>> browser.options.handle_errors = False

``server``
  Server name to use to query the WSGI application (default to
  ``localhost``).

``port``
  Port number to use to query the WSGI application (default to ``80``).

``protocol``
  HTTP protocol to use to query the WSGI application (default to
  ``HTTP/1.0``).

``follow_redirect``
  Boolean indicating if a redirect must be automatically
  followed. Default to True.

``follow_external_redirect``
  Boolean indicating if a redirect to a url that doesn't match the
  current server and port set in options should be automatically
  followed and handled by the current WSGI application. Activating it,
  will update the options ``server`` and ``port`` to the new value
  defined by the redirect URL. Default to False.

``handle_errors``
  Set the WSGI flag ``wsgi.handleErrors`` in the WSGI
  environment. Default to True.

``cookie_support``
  Boolean indicating if we must support cookie. By default to ``True``.

``default_wsgi_environ``
  Dictionnary that can be used to inject variable in the WSGI environment.


Inspect
-------

The browser as an ``inspect`` attribute. You can register an Xpath
expression with it, and query them after on HTML pages::

  >>> browser.inspect.add('feedback', '//div[@class="feedback"]/span')
  >>> self.assertEqual(browser.inspect.feedback, ['Everything ok'])

  >>> browser.inspect.add('feedback', css='div.feedback span')
  >>> self.assertEqual(browser.inspect.feedback, ['Everything ok'])


``add(name, xpath=None, type='link', css=None, unique=False)``
  Add an expression called `name` that can be used to inspect the HTML
  content of the browser using the `xpath` expression (or the `css`
  one). `type` can be:

  `text`
    The result would be a list containing the text of each matched
    element.

  `normalized-text`
    The result would be a list containing the text where whitespaces
    have been normalized for each matched element. (not available on
    Selenium, the text is normalized by default by the browser).

  `link`
    The result would be a list of links.

  `form`
    The result would be a list of forms.

  `form-actions`
    The result would be the actions of a form.

  `form-fields`
    The result would be the fields of a form.

  `clickable`
    Available only on selenium, that is a list of elements, that you
    can click on it (even if they are not links).

  If ``unique`` is true, no more than one item matching will be
  expected.  An error will be asserted if there are more items
  matching, and ``None`` will be returned if none matched.

Macros
------

Macros let you add listing of action to do on the browser. An example
will speak by itself::

  >>> def create_content(browser, identifier, title):
  ...    form = browser.get_form('addform')
  ...    form.get_control('identifier').value = identifier
  ...    form.get_control('title').value = title
  ...    assert form.inspect.actions['save'].click() == 200

  >>> browser.macros.add('create', create_content)

Now you can create content with your browser::

  >>> browser.macros.create('test', 'Test Content')
  >>> browser.macros.create('othertest', 'Other Test Content')


Links
-----

Links have some useful attributes and methods:

``click()``
  Follow this link in the browser, and return the HTTP status code
  returned by the application.

``url``
  Target URL of the link.

``text``
  Text of the link.

As result of an inspect, links are pretty useful:

  >>> browser.inspect.add('tabs', '//div[@class="tabs"]/a', type="link")
  >>> self.assertEqual(browser.inspect.tabs, ['View', 'Edit'])
  >>> self.assertEqual(browser.inspect.tabs['view'].click(), 200)


Forms
-----

Forms have the following methods and attributes:

``name``
  Name of the form.

``action``
  URL where to form is posted.

``method``
  Method to use to post the form.

``enctype``
  Form enctype to use to post the form.

``accept_charset``
  Charset to which the form data will be encoded before being posted.

``controls``
  Dictionary containing all the controls of the form.

``inspect``
  Inspect attribute, working like the one of the browser. By default,
  ``inspect.actions`` is registered to return all the submit-like
  controls of the form.

``get_control(name)``
  Return the given form control by its name.

``submit(name=None, value=None)``
  Submit the form, potentially add the control name and the given
  value to the submission. This return the HTTP status code returned
  by the application.

Calling ``str(form)`` will only return the HTML code of the form.

Forms support all the known HTTP controls.

Form controls
~~~~~~~~~~~~~

For consistency, all form controls share the attributes:

``name``
  Name of the control.

``type``
  Type of control, like value of type attribute for input and tag name
  in other cases.

``value``
  Value stored in the control.

``multiple``
  Boolean indicating if the control store multiple value.

``options``
  If the value have to be chosen in a list of possible values, those
  are the possibilities.

``checkable``
  Boolean indicating if the control can be checked (i.e. is it a checkbox).

``checked``
  Boolean indicating if the control is checked (and so if the value
  will be sent if the control is checkable).


In addition action controls (like submit buttons, button), have:

``submit()``
  Submit the form with this action. This return the HTTP status code
  returned by the application.

``click()``
  Alias to ``submit()``.

For file control, you have to set as value the filename (i.e path to)
of the file you want to upload.

Selenium browser
----------------

``infrae.testbrowser.browser.selenium.Browser``
   Test browser. You instantiate a new one by giving your WSGI
   application to test as arguments to the constructor.

   You have to use the browser as a context manager in order to start
   and stop the server that Selenium will use to access the
   application.

   The following environement variable are available in order to
   control the connection to the Selenium server:

   - ``TESTBROWSER_BROWSER`` (default to firefox)

   - ``TESTBROWSER_SELENIUM_PLATFORM`` (default to the local one)

   - ``TESTBROWSER_SELENIUM_HOST`` (default to localhost)

   - ``TESTBROWSER_SELENIUM_PORT`` (default to 4444)

   - ``TESTBROWSER_SERVER`` (default to localhost)

   - ``TESTBROWSER_PORT`` (default to 8000)

   If you set your testsuite to connect to a Selenium server that is
   not on your computer where you run your testsuite, please set the
   server and port options so that the Selenium knows how to connect
   to your application (it should be the network name of your
   computer).

   The API is the same than the default browser, except for:

   - you can't access HTTP status or headers,

   - you can't change hidden fields (you can only do what the user can
     do).

   Cookies do work however.


Selenium Browser options
------------------------

The following options are attributes of the options object, example::

    >>> browser.options.enable_javascript = False

They are on par with the possible configuration environment variables:

``enable_javascript``
   Enable or disable Javascript in Selenium.

``browser``
   String used to specify which browser you expect to use,
   i.e. 'firefox' or 'chrome' for instance.

``selenium_host``
  Network name of the computer where the Selenium server run.

``selenium_port``
  Port number where the Selenium server run.

``selenium_platform``
  Operating system where the Selenium should run the wanted browsers
  (for instance set it to 'win' if you wish Selenium to pick a browser
  on Windows).

``server``
   Network name of the computer where the testsuite will be
   running. This is the name that Selenium will use to access the
   tested application.

``port``
   Port on which the test application will be bound so Selenium can
   access it.


Code repository
===============

You can find the source code of this extensions in mercurial at
https://hg.infrae.com/infrae.testbrowser.

.. _zope.testbrowser: http://pypi.python.org/pypi/zope.testbrowser
