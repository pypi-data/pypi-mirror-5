This is a somewhat silly sample test that goes with the somewhat silly
test app.

It gives a simple example of using the testing infrastructure::

    >>> browser.get(server)
    >>> print browser.page_source # doctest: +ELLIPSIS
    <!DOCTYPE html>...
      <title>test title</title>
    <BLANKLINE>
      <link...href="/test.css"...
    <BLANKLINE>
    <BLANKLINE>
      <script type="text/javascript">
    <BLANKLINE>
                wsgidriver_x = 1;
    <BLANKLINE>
      </script>
    <BLANKLINE>
      <script src="/test.js"></script>
    <script type="text/javascript">
                wsgidriver_y = 2;
                </script>
    <BLANKLINE>
    </head><body>test content
    </body></html>

    js> [wsgidriver_x, wsgidriver_y, wsgidriver_z]
    [1, 2, 3]

Use js! when you don't want to return a value.  And when doing a block
of JS code::

    js! wsgidriver_f = function() {
    ...     return 4;
    ... }

Note that we defined a (global) variable here, rather than using a
function statement. This is due to some selenium details.

Now we can evaluate the function defined above::

    js> wsgidriver_f()
    4

We can also use ``browser.execute_script`` function to execute a block
of Javascript code from Python::

    wsgidriver_g = function() {
        return 5;
    }

.. -> src

With the above block in ``src``::

    >>> browser.execute_script(src)

    js> wsgidriver_g()
    5
