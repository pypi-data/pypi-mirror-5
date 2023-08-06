import sys
import os.path
import inspect

from .common import *


def _list_classes(module, type_filter):
    found = list()

    for name, module_obj in inspect.getmembers(module):
        if inspect.isclass(module_obj):
            append = not type_filter or type_filter(module_obj)
            if append:
                found.append(module_obj)
    return found


def _should_use_module(module):
    """
    Checks to make sure that the passed module has the correct hidden
    variables set.
    """
    return hasattr(module, PATH_ATTRUBITE) and len(module.__path__) > 0


def _scan_paths_for(mname, paths):
    mpath_part = mname.replace(MODULE_PATH_SEP, os.sep)
    for mpath in paths:
        scan_target = os.path.join(mpath, mpath_part)
        is_dir = os.path.isdir(scan_target)
        is_file = os.path.isfile('{}.py'.format(scan_target))
        if is_dir or is_file:
            return mpath


def _scan_dir(directory):
    found = list()
    module_py = os.path.join(directory, MODULE_INIT_FILE)
    if os.path.isfile(module_py):
        # Scan only if there's an __init__.py file
        for dir_entry in os.listdir(directory):
            if dir_entry != MODULE_INIT_FILE and dir_entry.endswith('.py'):
                found.append(dir_entry.rstrip('.py'))
    return found


def list_classes(mname, type_filter=None):
    """
    Attempts to list all of the classes within a specified module. This
    function works for modules located in the default path as well as
    extended paths via the sys.meta_path hooks.

    If a type filter is set, it will be called with each class as its
    parameter. This filter's return value must be interpretable as a
    boolean. Results that evaluate as True will include the type in the
    list of returned classes. Results that evaluate as False will exclude
    the type in the list of returned classes.
    """
    found = list()
    module = import_module(mname)
    if inspect.ismodule(module):
        [found.append(mod) for mod in _list_classes(module, type_filter)]
    return found


def discover_modules(mname):
    """
    Attempts to list all of the submodules under a module. This function
    works for modules located in the default path as well as extended paths
    via the sys.meta_path hooks.

    This function carries the expectation that the hidden module variable
    '__path__' has been set correctly.
    """
    found = list()
    module = import_module(mname)

    if module and _should_use_module(module):
        mpath = module.__path__[0]
    else:
        mpaths = sys.path
        mpath = _scan_paths_for(mname, mpaths)

    if mpath:
        for pmname in _scan_dir(mpath):
            found_mod = '{}{}{}'.format(mname, MODULE_PATH_SEP, pmname)
            found.append(found_mod)
    return found


def discover_classes(module, type_filter=None):
    """
    Attempts to list all of the classes within a given module namespace.
    This method, unlike list_classes, will recurse into discovered
    submodules.

    If a type filter is set, it will be called with each class as its
    parameter. This filter's return value must be interpretable as a
    boolean. Results that evaluate as True will include the type in the
    list of returned classes. Results that evaluate as False will exclude
    the type in the list of returned classes.
    """
    classes = list()
    mnames = discover_modules(module)
    for mname in mnames:
        [classes.append(c) for c in list_classes(mname, type_filter)]
    return classes
