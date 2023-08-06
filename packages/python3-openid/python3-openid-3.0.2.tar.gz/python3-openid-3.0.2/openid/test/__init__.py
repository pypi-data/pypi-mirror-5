import os.path
import sys
import warnings
import unittest

test_modules = [
    'cryptutil',
    'oidutil',
    'dh',
    ]


def fixpath():
    try:
        d = os.path.dirname(__file__)
    except NameError:
        d = os.path.dirname(sys.argv[0])
    parent = os.path.normpath(os.path.join(d, '..'))
    if parent not in sys.path:
        print(("putting %s in sys.path" % (parent,)))
        sys.path.insert(0, parent)


def otherTests():
    suite = unittest.TestSuite()
    for module_name in test_modules:
        module_name = 'openid.test.' + module_name
        try:
            test_mod = __import__(module_name, {}, {}, [None])
        except ImportError:
            print(('Failed to import test %r' % (module_name,)))
        else:
            suite.addTest(unittest.FunctionTestCase(test_mod.test))

    return suite


def pyUnitTests():
    pyunit_module_names = [
        'server',
        'consumer',
        'message',
        'symbol',
        'etxrd',
        'xri',
        'xrires',
        'association_response',
        'auth_request',
        'negotiation',
        'verifydisco',
        'sreg',
        'ax',
        'pape',
        'pape_draft2',
        'pape_draft5',
        'rpverify',
        'extension',
        'codecutil',
        ]

    pyunit_modules = [
        __import__('openid.test.test_%s' % (name,), {}, {}, ['unused'])
        for name in pyunit_module_names
        ]

    try:
        from openid.test import test_examples
    except ImportError:
        # This is very likely due to twill being unimportable, since it's
        # ancient and unmaintained. Until the examples are reimplemented using
        # something else, we just need to skip it
        warnings.warn("Could not import twill; skipping test_examples.")
    else:
        pyunit_modules.append(test_examples)

    # Some modules have data-driven tests, and they use custom methods
    # to build the test suite:
    custom_module_names = [
        'kvform',
        'linkparse',
        'oidutil',
        'storetest',
        'test_accept',
        'test_association',
        'test_discover',
        'test_fetchers',
        'test_htmldiscover',
        'test_nonce',
        'test_openidyadis',
        'test_parsehtml',
        'test_urinorm',
        'test_yadis_discover',
        'trustroot',
        ]

    loader = unittest.TestLoader()
    s = unittest.TestSuite()

    for m in pyunit_modules:
        s.addTest(loader.loadTestsFromModule(m))

    for name in custom_module_names:
        m = __import__('openid.test.%s' % (name,), {}, {}, ['unused'])
        try:
            s.addTest(m.pyUnitTests())
        except AttributeError:
            # because the AttributeError doesn't actually say which
            # object it was.
            print(("Error loading tests from %s:" % (name,)))
            raise

    return s


def _import_djopenid():
    """Import djopenid from examples/

    It's not in sys.path, and I don't really want to put it in sys.path.
    """
    import types
    parentDir = os.path.join(__file__, "..", "..")
    topDir = os.path.abspath(os.path.join(parentDir, ".."))
    djdir = os.path.join(topDir, 'examples', 'djopenid')

    djinit = os.path.join(djdir, '__init__.py')

    djopenid = types.ModuleType('djopenid')
    with open(djinit, 'r') as f:
        exec(compile(f.read(), "__init__.py", "exec"), {})

    djopenid.__file__ = djinit

    # __path__ is the magic that makes child modules of the djopenid package
    # importable.  New feature in python 2.3, see PEP 302.
    djopenid.__path__ = [djdir]
    sys.modules['djopenid'] = djopenid


def django_tests():
    """Runs tests from examples/djopenid.

    @returns: number of failed tests.
    """
    import os
    # Django uses this to find out where its settings are.
    os.environ['DJANGO_SETTINGS_MODULE'] = 'djopenid.settings'

    _import_djopenid()

    try:
        import django.test.simple
    except ImportError:
        warnings.warn("django.test.simple not found; "
                      "django examples not tested.")
        return 0

    import djopenid.server.models, djopenid.consumer.models
    print ("Testing Django examples:")

    # These tests do get put in to a pyunit test suite, so we could run them
    # with the other pyunit tests, but django also establishes a test database
    # for them, so we let it do that thing instead.
    return django.test.simple.run_tests([djopenid.server.models,
                                         djopenid.consumer.models])

try:
    bool
except NameError:
    def bool(x):
        return not not x


def test_suite():
    fixpath()
    all_suite = unittest.TestSuite()
    all_suite.addTests(otherTests())
    all_suite.addTests(pyUnitTests())
    all_suite.addTest(unittest.FunctionTestCase(django_tests))
    return all_suite
