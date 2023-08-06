import os
import shutil
import tempfile
import unittest
import pynsive


INIT_PY = """
from .test_classes import *
"""

TEST_CLASSES_PY = """
SUCCESS = True

class PynsiveTestingClass(object):
    pass


class OtherPynsiveTestingClass(PynsiveTestingClass):
    pass
"""


class WhenLoading(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        This crazy setUp method for the following unit tests creates a
        temporary plugin directory and then drops a Python module and related
        testing code into it. The method then spins up a plugin context via
        a pynsive.PluginManager instance.
        """

        cls.directory = tempfile.mkdtemp()
        cls.module_path = os.path.join(cls.directory, 'pynsive_test')
        os.mkdir(cls.module_path)
        with open(os.path.join(cls.module_path, '__init__.py'), 'w') as f:
            f.write(INIT_PY)
        with open(os.path.join(cls.module_path, 'test_classes.py'), 'w') as f:
            f.write(TEST_CLASSES_PY)
        cls.plugin_manager = pynsive.PluginManager()
        cls.plugin_manager.plug_into(cls.directory)

    @classmethod
    def tearDownClass(cls):
        cls.plugin_manager.destroy()
        if cls.directory:
            shutil.rmtree(cls.directory)

    def test_plugging_into_directory(self):
        """
        When plugging into a directory using a PluginManager, the manager
        will make the new directory available for search when importing
        modules. These modules must be available for import via the
        import_module function provided by pynsive.
        """

        test_module = pynsive.import_module('pynsive_test.test_classes')
        self.assertTrue(test_module.SUCCESS)

    def test_listing_classes(self):
        classes = pynsive.list_classes('pynsive_test')
        self.assertEqual(len(classes), 2)

    def test_listing_classes_with_filter(self):
        test_module = pynsive.import_module('pynsive_test.test_classes')

        def subclasses_only(test_type):
            same = test_type is not test_module.PynsiveTestingClass
            is_subclass = issubclass(
                test_type, test_module.PynsiveTestingClass)
            return not same and is_subclass

        classes = pynsive.list_classes('pynsive_test', subclasses_only)
        self.assertEqual(len(classes), 1)

    def test_discovering_modules(self):
        stock_path_packages = [
            'pynsive.plugin.loader',
            'pynsive.plugin.manager']
        plugin_path_packages = ['pynsive_test.test_classes']
        self.assertEqual(
            plugin_path_packages,
            pynsive.discover_modules('pynsive_test'))
        self.assertListEqual(stock_path_packages,
            pynsive.discover_modules('pynsive.plugin'))

    def test_discovering_classes(self):
        classes = pynsive.discover_classes('pynsive_test')
        self.assertEqual(2, len(classes))

    def test_discovering_classes_with_filter(self):
        test_module = pynsive.import_module('pynsive_test.test_classes')

        def subclasses_only(test_type):
            same = test_type is not test_module.PynsiveTestingClass
            is_subclass = issubclass(
                test_type, test_module.PynsiveTestingClass)
            return not same and is_subclass

        classes = pynsive.discover_classes('pynsive_test', subclasses_only)
        self.assertEqual(len(classes), 1)
