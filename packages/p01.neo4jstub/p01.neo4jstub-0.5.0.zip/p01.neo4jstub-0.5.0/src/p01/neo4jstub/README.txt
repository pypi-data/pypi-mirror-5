======
README
======

setup
-----

This test is using a neo4j server. The test setUp method used for this
test is calling our startNeo4jServer method which is starting a neo4j
server. The first time this test get called a new neo4j server will get
downloaded. The test setup looks like::

  def test_suite():
      return unittest.TestSuite((
          doctest.DocFileSuite('README.txt',
              setUp=testing.doctestSetUp, tearDown=testing.doctestTearDown,
              optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
              encoding='utf-8'),
          ))

Your setup with a custom conf folder could look like::

  def mySetUp(test):
      # setup neo4j server
      here = os.path.dirname(__file__)
      sandbox = os.path.join(here, 'sandbox')
      confSource = os.path.join(here, 'conf')
      startNeo4jServer(sandbox, confSource=confSource)
  
  
  def myTearDown(test):
      # tear down neo4j server
      here = os.path.dirname(__file__)
      sandbox = os.path.join(here, 'sandbox')
      stopNeo4jServer(sandbox)
      # do some custom teardown stuff here

Also see our test.py for a sample setup.


windows
-------

On windows a service with the name p01_neo4jstub_testing get installed and
removed during the test run. This is not nice but that's how neo4j can get
stopped after starting. If soemthing fails and the service dosn't get removed,
you can simply use the follwoingcommand for remove the service:

  sc delete p01_neo4jstub_testing


testing
-------

Let's setup a python httplib connection:

  >>> import httplib
  >>> conn = httplib.HTTPConnection('localhost', 47474)

and test the cluster state:

  >>> conn.request('GET', '/db/data')
  >>> response = conn.getresponse()
  >>> response.status
  302
