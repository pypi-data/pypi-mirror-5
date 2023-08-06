===============================
The gocept.jasmine distribution
===============================

Jasmine integration for selenium.


Usage
=====

You need two things to run jasmine tests with selenium:

* A test app which requires your resources and jasmine test files::

    class MyTestApp(gocept.jasmine.jasmine.TestApp):

        def need_resources(self):
            # Require your resources here
            my.package.resource.need()
            my.package.tests.jasmine_tests.need()

        @property
        def body(self):
            # HTML setup for your tests goes here
            return '<div id="my_container"></div>'

* A TestCase with the jasmine layer::

    class MyJasmineTestCase(gocept.jasmine.jasmine.TestCase):

        layer = gocept.jasmine.jasmine.get_layer(MyTestApp())

        def test_integration(self):
            self.run_jasmine()

The important things here are, that the `get_layer` function is given
your jasmine app and that the returned Layer is used on yout TestCase.

In your Test, simple run `run_jasmine`, which will open the TestApp in your
Browser. The TestApp renders your `body` and includes all needed resources and
then runs the jasmine tests. `run_jasmine` will wait for these tests to finish
and the report success or failure. Jasmine tracebacks and error details are
visible through the selenium error handling.


Debugging
---------

You can set the `debug` flag on your test case to get a pdb debugger right
after the start of the jasmine tests. This lets you debug your jasmine tests
within your browser::

    class MyJasmineTestCase(gocept.jasmine.jasmine.TestCase):

        layer = gocept.jasmine.jasmine.get_layer(MyTestApp())
        debug = True

        def test_integration(self):
            self.run_jasmine()
