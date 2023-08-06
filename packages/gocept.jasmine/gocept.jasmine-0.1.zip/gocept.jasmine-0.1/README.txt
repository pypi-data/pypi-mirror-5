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

* A TestCase with a proper layer setup::

    JASMINE_LAYER = gocept.jasmine.jasmine.Layer(
        application=MyTestApp(), name='JasmineLayer')

    HTTP_SERVER_LAYER = gocept.httpserverlayer.wsgi.Layer(
        name='HTTPServerLayer', bases=(WSGI_LAYER,))

    WEBDRIVER_LAYER = gocept.selenium.webdriver.Layer(
        name='WebdriverLayer', bases=(HTTP_SERVER_LAYER,))

    SELENESE_LAYER = gocept.selenium.webdriver.WebdriverSeleneseLayer(
        name='SeleneseLayer', bases=(WEBDRIVER_LAYER,))


    class MyJasmineTestCase(gocept.jasmine.jasmine.TestCase):

        layer = SELENESE_LAYER

        def test_integration(self):
            self.run_jasmine()

Please refer to the `gocept.selenium` documentation for information about the
layer setup. The important things here are, that the `JASMINE_LAYER` is given
your jasmine app and that this Layer is used on yout TestCase.

In your Test, simple run `run_jasmine`, which will open the TestApp in your
Browser. The TestApp renders your `body` and includes all needed resources and
then runs the jasmine tests. `run_jasmine` will wait for these tests to finish
and the report success or failure. Jasmine tracebacks and error details are
visible through the selenium error handling.
