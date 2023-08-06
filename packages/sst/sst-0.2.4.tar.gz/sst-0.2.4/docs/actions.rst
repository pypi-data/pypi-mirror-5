
=========================
 SST - Actions Reference
=========================

Actions to make Selenium tests simple.

Tests are comprised of Python scripts or test case classes.

Files whose names begin with an underscore will *not* be executed as tests.

Tests drive the browser with Selenium WebDriver by importing and using SST
actions.

The standard set of actions are imported by starting the test scripts with::

    from sst import actions


Actions that work on page elements take either an element id or an
element object as their first argument. If the element you are working with
doesn't have a specific id you can get the element object with the
`get_element` action. `get_element` allows you to find an element by its
id, tag, text, class or other attributes. See the `get_element` documentation.


----------------
    Actions:
----------------


accept_alert
------------

.. function :: accept_alert(expected_text=None, text_to_write=None)

    Accept a JavaScript alert, confirmation or prompt.

    Note that the action that opens the alert should not wait for a page with
    a body element. This means that you should call functions like
    `click_element` with the argument `wait=Fase`.

    :argument expected_text: The expected text of the alert. If `None`, the
        alert will not be checked.
    :argument text_to_write: The text to write in the alert prompt. If `None`,
        no text will be written.



add_cleanup
-----------

.. function :: add_cleanup(func, *args, **kwargs)

    Add a function to be called when the test is completed.

    Functions added are called on a LIFO basis and are called on test failure
    or success.

    They allow a test to clean up after itself.

    :argument func: The function to call.
    :argument args: The arguments to pass to `func`.
    :argument kwargs: The keyword arguments to pass to `func`.



assert_attribute
----------------

.. function :: assert_attribute(id_or_elem, attribute, value, regex=False)

    Assert an the value of an element's attribute.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument attribute: The name of the attribute to assert.
    :argument value: The expected value.
    :argument regex: If `True`, the `value` will be used as regular expression.
    :raise: AssertionError if the element doesn't exist, or if the value is not
        the expected.



assert_button
-------------

.. function :: assert_button(id_or_elem)

    Assert that an element is a button.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a button.
    :return: The element object.



assert_checkbox
---------------

.. function :: assert_checkbox(id_or_elem)

    Assert that an element is a checkbox.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a checkbox.
    :return: The element object.



assert_checkbox_value
---------------------

.. function :: assert_checkbox_value(id_or_elem, value)

    Assert the value of a checkbox.

    :argument id_or_elem: The identifier of the element, or an element object.
    :argument value: The expected value of the checkbox. Pass `True` if you
        want to assert that the checkbox is selected, `False` otherwise.
    :raise: AssertionError if the element doesn't exist, if it is not a
        checkbox, or if the checkbox value is not the expected.



assert_css_property
-------------------

.. function :: assert_css_property(id_or_elem, property, value, regex=False)

    Assert the value of an element's CSS property.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument property: The name of the CSS property to assert.
    :argument value: The expected value.
    :argument regex: If `True`, the `value` will be used as regular expression.
    :raise: AssertionError if the element doesn't exist, or if the value is not
        the expected.



assert_displayed
----------------

.. function :: assert_displayed(id_or_elem)

    Assert that an element is displayed.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't displayed.
    :return: The element object.



assert_dropdown
---------------

.. function :: assert_dropdown(id_or_elem)

    Assert that an element is a drop-down list.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a drop-down
        list.
    :return: The element object.



assert_dropdown_value
---------------------

.. function :: assert_dropdown_value(id_or_elem, text_in)

    Assert the selected option in a drop-list.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument text_in: The expected text of the selected option.
    :raise: AssertionError if the element doesn't exist, if it isn't a
        drop-down list or if the selected text is not the expected.



assert_element
--------------

.. function :: assert_element(tag=None, css_class=None, id=None, text=None, text_regex=None, **kwargs)

    Assert that an element exists.

    :argument tag: The HTML tag of the element.
    :argument css_class: The value of the class attribute of the element.
    :argument id: The value of the id attribute of the element.
    :argument text: The text of the element. If you pass the `text` argument,
        you shouldn't pass the `text_regex` too.
    :argument text_regex: A regular expression to look for in the text of the
        element. If you pass the `text_regex` argument, you shouldn't pass
        the `text` too.
    :argument kwargs: Keyword arguments to look for values of additional
        attributes. The key will be the attribute name.
    :raise: TypeError if you pass both `text` and `text_regex`. AssertionError
        if the element doesn't exist.



assert_equal
------------

.. function :: assert_equal(first, second)

    Assert that two objects are equal.

assert_link
-----------

.. function :: assert_link(id_or_elem)

    Assert that an element is a link.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a link.
    :return: The element object.



assert_not_equal
----------------

.. function :: assert_not_equal(first, second)

    Assert that two objects are not equal.

assert_radio
------------

.. function :: assert_radio(id_or_elem)

    Assert that an element is a radio button.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a radio
        button.
    :return: The element object.



assert_radio_value
------------------

.. function :: assert_radio_value(id_or_elem, value)

    Assert the value of a radio button.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument value: The expected valueof the radio button. Pass `True` if you
        want to assert that the radio button is selected, `False` otherwise.
    :raise: AssertionError if the element doesn't exist, isn't a radio button,
        or the value is not the expected.



assert_table_has_rows
---------------------

.. function :: assert_table_has_rows(id_or_elem, num_rows)

    Assert the number of rows of a table.

    The rows are the `<tr>` tags inside the `<tbody>`

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument num_rows: The expected number of rows.
    :raise: AssertionError if the element doesn't exist, it isn't a table, it
        doesn't have a tbody, or if its number of rows is not the expected.



assert_table_headers
--------------------

.. function :: assert_table_headers(id_or_elem, headers)

    Assert the headers of a table.

    The headers are the `<th>` tags.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument headers: A sequence of the expected headers.
    :raise: AssertionError if the element doesn't exist, or if its headers are
        not the expected.



assert_table_row_contains_text
------------------------------

.. function :: assert_table_row_contains_text(id_or_elem, row, contents, regex=False)

    Assert that a row of a table contains a text.

    The row will be looked for inside the <tbody>, to check headers use
    `assert_table_headers`.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument row: The row index, starting from 0.
    :argument contents: A sequence of strings. Each where string will should
        be the same as the text of the corresponding column.
    :argument regex: If `True`, the strings in `contents` will be used as
        regular expressions.
    :raise: AssertionError if the element doesn't exist, it isn't a table, it
        doesn't have a tbody, if the rows number if bigger than the number of
        rows in the table, or if the row texts doesn't match the expected.



assert_text
-----------

.. function :: assert_text(id_or_elem, text)

    Assert the text of an element.

    For text fields, it checks the value attribute instead of the text of the
    element.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument text: The expected text.
    :raise: AssertionError if the element doesn't exist or its text is not the
        expected.



assert_text_contains
--------------------

.. function :: assert_text_contains(id_or_elem, text, regex=False)

    Assert that the element contains a text.

    For text fields, it checks the value attribute instead of the text of the
    element.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument text: The expected text.
    :argument regex: If `True`, `text` will be used as a regex pattern.
    :raise: AssertionError if the element doesn't exist or its text doesn't
        contain the expected.



assert_textfield
----------------

.. function :: assert_textfield(id_or_elem)

    Assert that an element is a textfield, textarea or password box.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a text field.
    :return: The element object.



assert_title
------------

.. function :: assert_title(title)

    Assert the page title.

    :argument title: The expected title.
    :raise: AssertionError if the title is not the expected.



assert_title_contains
---------------------

.. function :: assert_title_contains(text, regex=False)

    Assert that the page title contains a text.

    :argument text: The expected text.
    :argument regex: If `True`, `text` will be used as a regex pattern.
    :raise: AssertionError if the title doesn't contain the expected text.



assert_url
----------

.. function :: assert_url(url)

    Assert the current URL.

    :argument url: The expected URL. It can be an absolute URL or relative to
        the base url.
    :raise: AssertionError if the URL is not the expected.



assert_url_contains
-------------------

.. function :: assert_url_contains(text, regex=False)

    Assert that the current URL contains a text.

    :argument text: The expected text.
    :argument regex: If `True`, `text` will be used as a regex pattern.
    :raise: AssertionError if the URL doesn't contain the expected text.



assert_url_network_location
---------------------------

.. function :: assert_url_network_location(netloc)

    Assert the current URL's network location.

    :argument netloc: The expected network location. It is a string containing
        `domain:port`. In the case of port 80, `netloc` may contain domain
        only.
    :raise: AssertionError if the network location is not the expected.



check_flags
-----------

.. function :: check_flags(*args)

    Skip a test if one of the flags wasn't supplied at the command line.

    Flags are case-insensitive.

    :argument args: A list of flags to check.



clear_cookies
-------------

.. function :: clear_cookies()

    Clear the cookies of the current session.

click_button
------------

.. function :: click_button(id_or_elem, wait=True)

    Click a button.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument wait: If `True`, this action will wait until a page with a body
        element is available. Otherwise, it will return immediately after the
        Selenium refresh action is completed.
    :raise: AssertionError if the element doesn't exist or isn't a button.



click_element
-------------

.. function :: click_element(id_or_elem, wait=True)

    Click on an element of any kind not specific to links or buttons.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument wait: If `True`, this action will wait until a page with a body
        element is available. Otherwise, it will return immediately after the
        Selenium refresh action is completed.



click_link
----------

.. function :: click_link(id_or_elem, check=False, wait=True)

    Click a link.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument check: If `True`, the resulting URL will be check to be the same
        as the one on the link. Default is `False` because some links do
        redirects.
    :argument wait: If `True`, this action will wait until a page with a body
        element is available. Otherwise, it will return immediately after the
        Selenium refresh action is completed.
    :raise: AssertionError if the element doesn't exist or isn't a link.



close_window
------------

.. function :: close_window()

    Closes the current window.

debug
-----

.. function :: debug()

    Start the debugger, a shortcut for `pdb.set_trace()`.

dismiss_alert
-------------

.. function :: dismiss_alert(expected_text=None, text_to_write=None)

    Dismiss a JavaScript alert.

    Note that the action that opens the alert should not wait for a page with
    a body element. This means that you should call functions like
    `click_element` with the argument `wait=Fase`.

    :argument expected_text: The expected text of the alert. If `None`, the
        alert will not be checked.
    :argument text_to_write: The text to write in the alert prompt. If `None`,
        no text will be written.



end_test
--------

.. function :: end_test()

    End the test.

    It can be used conditionally to exit a test under certain conditions.



execute_script
--------------

.. function :: execute_script(script, *args)

    Execute JavaScript in the currently selected frame or window.

    Within the script, use `document` to refer to the current document.

    For example::

        execute_script('document.title = "New Title"')

    :argument script: The script to execute.
    :argument args: A list of arguments to be made available to the script.
    :return: The return value of the script.



exists_element
--------------

.. function :: exists_element(tag=None, css_class=None, id=None, text=None, text_regex=None, **kwargs)

    Check if an element exists.

    :argument tag: The HTML tag of the element.
    :argument css_class: The value of the class attribute of the element.
    :argument id: The value of the id attribute of the element.
    :argument text: The text of the element. If you pass the `text` argument,
        you shouldn't pass the `text_regex` too.
    :argument text_regex: A regular expression to look for in the text of the
        element. If you pass the `text_regex` argument, you shouldn't pass
        the `text` too.
    :argument kwargs: Keyword arguments to look for values of additional
        attributes. The key will be the attribute name.
    :raise: TypeError if you pass both `text` and `text_regex`.
    :return: True if the element exists, False otherwise.



fails
-----

.. function :: fails(action, *args, **kwargs)

    Check that an action raises an AssertionError.

    If the action raises a different exception, it will be propagated normally.

    :argument action: A function to check.
    :argument args: The arguments to pass to the `action` function.
    :argument kwargs: The keyword arguments to pass to the `action` function.
    :raise: AssertionError if the `action` doesn't raise an AssertionError.



get_argument
------------

.. function :: get_argument(name, default=default)

    Get an argument from the one the test was called with.

    A test is called with arguments when it is executed by the `run_test`. You
    can optionally provide a default value that will be used if the argument
    is not set.

    :argument name: The name of the argument.
    :argument default: Value that will be used if the argument is not set.
    :raise: `LookupError` if you don't provide a default value and the
        argument is missing.
    :return: The argument value.



get_base_url
------------

.. function :: get_base_url()

    Return the base URL used by `go_to`.

get_cookies
-----------

.. function :: get_cookies()

    Get the cookies of the current session.

    :return: A set of dicts with the session cookies.



get_current_url
---------------

.. function :: get_current_url()

    Get the URL of the current page.

get_element
-----------

.. function :: get_element(tag=None, css_class=None, id=None, text=None, text_regex=None, **kwargs)

    Return an element object.

    This action will find and return one elements by any of several
     attributes.

    :argument tag: The HTML tag of the element.
    :argument css_class: The value of the class attribute of the element.
    :argument id: The value of the id attribute of the element.
    :argument text: The text of the element. If you pass the `text` argument,
        you shouldn't pass the `text_regex` too.
    :argument text_regex: A regular expression to look for in the text of the
        element. If you pass the `text_regex` argument, you shouldn't pass
        the `text` too.
    :argument kwargs: Keyword arguments to look for values of additional
        attributes. The key will be the attribute name.
    :raise: TypeError if you pass both `text` and `text_regex`. AssertionError
        if no element matches the attributes or if more than one element
        match.
    :return: The elements that matches.



get_element_by_css
------------------

.. function :: get_element_by_css(selector)

    Return the element that matches a CSS selector.

    :argument selector: The CSS selector that will be used to search for the
        element.
    :raise: AssertionError if no element matches the `selector` of if more
        than one match.
    :return: The elements that matches.



get_element_by_xpath
--------------------

.. function :: get_element_by_xpath(selector)

    Return the element that matches an XPath selector.

    :argument selector: The XPath selector that will be used to search for the
        element.
    :raise: AssertionError if no element matches the `selector` of if more
        than one match.
    :return: The elements that matches.



get_element_source
------------------

.. function :: get_element_source(id_or_elem)

    Get the innerHTML source of an element.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist



get_elements
------------

.. function :: get_elements(tag=None, css_class=None, id=None, text=None, text_regex=None, **kwargs)

    Return element objects.

    This action will find and return all matching elements by any of several
    attributes.

    :argument tag: The HTML tag of the element.
    :argument css_class: The value of the class attribute of the element.
    :argument id: The value of the id attribute of the element.
    :argument text: The text of the element. If you pass the `text` argument,
        you shouldn't pass the `text_regex` too.
    :argument text_regex: A regular expression to look for in the text of the
        element. If you pass the `text_regex` argument, you shouldn't pass
        the `text` too.
    :argument kwargs: Keyword arguments to look for values of additional
        attributes. The key will be the attribute name.
    :raise: TypeError if you pass both `text` and `text_regex`. AssertionError
        if no element matches the attributes.
    :return: A list with the elements that match.



get_elements_by_css
-------------------

.. function :: get_elements_by_css(selector)

    Return all the elements that match a CSS selector.

    :argument selector: The CSS selector that will be used to search for the
        elements.
    :raise: AssertionError if no element matches the `selector`.
    :return: A list with the elements that match.



get_elements_by_xpath
---------------------

.. function :: get_elements_by_xpath(selector)

    Return all the elements that match an XPath selector.

    :argument selector: The XPath selector that will be used to search for the
        elements.
    :raise: AssertionError if no element matches the `selector`.
    :return: A list with the elements that match.



get_link_url
------------

.. function :: get_link_url(id_or_elem)

    Return the URL from a link.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a link.



get_page_source
---------------

.. function :: get_page_source()

    Gets the source of the current page.

get_text
--------

.. function :: get_text(id_or_elem)

    Return the text of an element.

    :argument id_or_elem: The identifier of the element, or an element object.
    :raise: AssertionError if the element doesn't exist.



get_wait_timeout
----------------

.. function :: get_wait_timeout()

    Get the timeout, in seconds, used by `wait_for`.

get_window_size
---------------

.. function :: get_window_size()

    Get the current window size.

    :return: A pair (width, height), in pixels.



go_back
-------

.. function :: go_back(wait=True)

    Go one step backward in the browser history.

    :argument wait: If `True`, this action will wait until a page with a body
        element is available. Otherwise, it will return immediately after the
        Selenium refresh action is completed.



go_to
-----

.. function :: go_to(url='', wait=True)

    Go to a URL.

    :arguement url: The URL to go to. If it is a relative URL it will be added
        to the base URL. You can change the base url for the test with
        `set_base_url`.
    :argument wait: If `True`, this action will wait until a page with a body
        element is available. Otherwise, it will return immediately after the
        Selenium refresh action is completed.



refresh
-------

.. function :: refresh(wait=True)

    Refresh the current page.

    :argument wait: If `True`, this action will wait until a page with a body
        element is available. Otherwise, it will return immediately after the
        Selenium refresh action is completed.



reset_base_url
--------------

.. function :: reset_base_url()

    Restore the base url to the default.

    This is called automatically for you when a test script completes.



retry_on_exception
------------------

.. function :: retry_on_exception(exception, retries=None)

    Decorate a function so an `exception` triggers a retry.

    :param exception: If this exception is raised, the decorated function
        will be retried.
    :param retries: The number of times that the function will be retried.
        If it is `None`, the function will be retried until the time out set by
        `set_wait_timeout` expires.



run_test
--------

.. function :: run_test(name, **kwargs)

    Execute a test, with the specified arguments.

    Tests are executed with the same browser (and browser session) as the
    test calling `run_test`. This includes whether or not Javascript is
    enabled.

    Before the test is called the timeout and base url are reset, but will be
    restored to their orginal value when `run_test` returns.

    :argument name: The name of the test to run. It is the test file name
        without the '.py'. You can specify tests in an alternative directory
        with relative path syntax. e.g.: `subdir/foo`.
    :argument kwargs: The arguments to pass to the test. Arguments can be
        retrieved by the test with `get_argument`.
    :return: The value of the `RESULT` variable, if set by the test being run.



save_page_source
----------------

.. function :: save_page_source(filename='pagedump.html', add_timestamp=True)

    Save the source of the currently opened page.

    It is called automatically on failures when running in `-s` mode.

    :argument filename: The name of the file where the page will be dumped.
    :argument add_timestamp: If `True`, a timestamp will be added to the
        `filename`.
    :return: The path to the saved file.



set_base_url
------------

.. function :: set_base_url(url)

    Set the URL used for relative arguments to the `go_to` action.

set_checkbox_value
------------------

.. function :: set_checkbox_value(id_or_elem, new_value)

    Set the value of a checkbox.

    :argument id_or_elem: The identifier of the element, or an element object.
    :argument new_value: The new value for the checkbox. Pass `True` if you
        want to select the checkbox, `False` otherwise.
    :raise: AssertionError if the element doesn't exist or if it is not a
        checkbox.



set_dropdown_value
------------------

.. function :: set_dropdown_value(id_or_elem, text=None, value=None)

    Set the value of a drop-down list.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument text: The text of the drop-down option that will be selected. If
        you pass the `text` argument, you shouldn't pass `value` too.
    :argument value: The value of the drop-down option that will be selected.
        If  you pass the `value` argument, you shouldn't pass `text` too.
    :raise: AssertionError if the element doesn't exist, if it isn't a
        drop-down list, if you passed both `text` and `value`, or if the option
        is not in the drop-down list.



set_radio_value
---------------

.. function :: set_radio_value(id_or_elem)

    Select a radio button.

    :argument id_or_elem: The identifier of the element, or its element object.
    :raise: AssertionError if the element doesn't exist or isn't a radio
        button.



set_wait_timeout
----------------

.. function :: set_wait_timeout(timeout, poll=None)

    Set the timeout and poll frequency used by `wait_for`.

    The default timeout at the start of a test is 10 seconds and the poll
    frequency is 0.1 seconds.

    :argument timeout: The new timeout in seconds.
    :argument poll: The poll frequency in seconds. It is how long `wait_for`
       should wait in between checking its condition.



set_window_size
---------------

.. function :: set_window_size(width, height)

    Resize the current window.

    :argument width: The new width for the window, in pixels.
    :argument height: The new height for the window, in pixels.



simulate_keys
-------------

.. function :: simulate_keys(id_or_elem, key_to_press)

    Simulate keys sent to an element.

    Available keys can be found in `selenium/webdriver/common/keys.py`

    e.g.::

        simulate_keys('text_1', 'BACK_SPACE')

    :argument id_or_elem: The identifier of the element, or an element object.
    :argument key_to_press: The name of the key to press.
    :raise: AssertionError if the element doesn't exist.



skip
----

.. function :: skip(reason='')

    Skip the test.

    Unlike `end_test` a skipped test will be reported as a skip rather than a
    pass.

    :argument reason: The reason to skip the test. It will be recorded in the
        test result.



sleep
-----

.. function :: sleep(seconds)

    Delay execution for the given number of seconds.

    :argument seconds: The number of seconds to sleep. It may be a floating
        point number for subsecond precision.



switch_to_frame
---------------

.. function :: switch_to_frame(index_or_name=None)

    Switch focus to a frame.

    :argument index_or_name: The index or the name of the frame that will be
        focused. If `None` focus will switch to the default frame.
    :raise: Assertion error if the frame couldn't be found.



switch_to_window
----------------

.. function :: switch_to_window(index_or_name=None)

    Switch focus to a window.

    :argument index_or_name: The index or the name of the window that will be
        focused. If `None` focus will switch to the default window.
    :raise: Assertion error if the index is greater than the available windows,
        or the window couldn't be found.



take_screenshot
---------------

.. function :: take_screenshot(filename='screenshot.png', add_timestamp=True)

    Take a screenshot of the browser window.

    It is called automatically on failures when running in `-s` mode.

    :argument filename: The name of the file where the screenshot will be
        saved.
    :argument add_timestamp: If `True`, a timestamp will be added to the
        `filename`.
    :return: The path to the saved screenshot.



toggle_checkbox
---------------

.. function :: toggle_checkbox(id_or_elem)

    Toggle the checkbox value.

    :argument id_or_elem: The identifier of the element, or an element object.
    :raise: AssertionError if the element doesn't exist or if it is not a
        checkbox.



wait_for
--------

.. function :: wait_for(*args, **kwargs)

    Wait for an action to succeed.

    It is Useful for checking the results of actions that may take some time
    to complete.

    e.g::

        wait_for(assert_title, 'Some page title')

    :argument condition: A function to wait for. It can either be an action or
        a function that returns False or throws an AssertionError for failure,
        and returns anything different from False (including not returning
        anything) for success.
    :argument args: The arguments to pass to the `condition` function.
    :argument kwargs: The keyword arguments to pass to the `condition`
        function.
    :raise: AssertionError if `condition` does not succeed within the timeout.
        You can set the timeout for `wait_for` by calling `set_wait_timeout`
    :return: The value returned by `condition`.



wait_for_and_refresh
--------------------

.. function :: wait_for_and_refresh(condition, *args, **kwargs)

    Wait for an action to succeed.

    It is Useful for checking the results of actions that may take some time
    to complete.

    The difference to `wait_for` is, that `wait_for_and_refresh()` will
    refresh the current page with after every condition check.

    :argument condition: A function to wait for. It can either be an action or
        a function that returns False or throws an AssertionError for failure,
        and returns anything different from False (including not returning
        anything) for success.
    :argument args: The arguments to pass to the `condition` function.
    :argument kwargs: The keyword arguments to pass to the `condition`
        function.
    :raise: AssertionError if `condition` does not succeed within the timeout.
        You can set the timeout for `wait_for` by calling `set_wait_timeout`
    :return: The value returned by `condition`.



write_textfield
---------------

.. function :: write_textfield(id_or_elem, new_text, check=True, clear=True)

    Write a text into a text field.

    :argument id_or_elem: The identifier of the element, or its element object.
    :argument new_text: The text to write.
    :argument check: If `True`, a check will be made to make sure that the
        text field contents after writing are the same as `new_text`.
    :argument clear: If `True`, the field will be cleared before writting into
        it.



