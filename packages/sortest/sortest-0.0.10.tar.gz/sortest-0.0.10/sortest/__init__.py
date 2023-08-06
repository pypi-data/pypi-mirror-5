import collections
import inspect
import itertools
import nose.importer
import nose.util
import re
import os
import os.path
import sys
import time
import traceback
import unittest


def find_python_files(rootdirs, excluded_dirs):
    for rootdir in rootdirs:
        for root, subdirs, files in os.walk(rootdir):
            for baddir in excluded_dirs:
                baddir = baddir.rstrip("/").lstrip("/")
                if baddir in subdirs:
                    subdirs.remove(baddir)
            for f in files:
                if f.endswith('.py'):
                    yield root, f


def find_python_update_times(excluded_dirs, pyfiles):
    for d, f in pyfiles:
        try:
            yield {"dir": d,
                   "file": f,
                   "path": os.path.join(d, f),
                   "saved": os.path.getmtime(os.path.join(d, f))}
        except OSError:
            pass  # Skip deleted file


def excluded_file(fname, excluded):
    return any(p for p in excluded if re.search(p, fname))


def wanted_files(excluded_files, excluded_dirs, filesgen):
    for d in filesgen:
        if (not excluded_file(d["file"], excluded_files) and
            d["dir"] not in excluded_dirs):
            yield d


def nuke_module_refs(module):
    """
    Delete all refs to e.g. functions in a module, which are NOT
    automagically cleaned out when module is reloaded; see
    http://stackoverflow.com/questions/11380328/\
    why-does-pythons-imp-reload-not-delete-old-classes-and-functions
    """
    for attr in dir(module):
        if attr not in ('__name__', '__file__'):
            delattr(module, attr)


def find_modules(dictgen):
    importer = nose.importer.Importer()
    for d in dictgen:
        modname = nose.util.getpackage(d["path"])
        module = importer.importFromPath(d["path"], modname)
        nuke_module_refs(module)
        reload(module)
        d["modname"] = modname
        d["module"] = module
        d["tests"] = []
        yield d


def is_a_test_function(func):
    return inspect.isfunction(func) and func.__name__.startswith("test")


def get_test_functions_for_modules(dictgen):
    for d in dictgen:
        
        module = d["module"]
        for itemname in dir(module):
            item = getattr(module, itemname, None)
            if is_a_test_function(item):
                d["tests"].append({"function": item,
                                   "testtype": "function",
                                   "funname": ":".join((d["modname"], itemname))})
        yield d


def get_unittest_functions(mods):
    tl = unittest.TestLoader()
    for module in mods:
        for itemname in dir(module["module"]):
            item = getattr(module["module"], itemname, None)
            if (item and
                nose.util.isclass(item) and
                issubclass(item, unittest.TestCase)):
                for t in tl.loadTestsFromTestCase(item):
                    funname = "%s:%s.%s" % (module["modname"],
                                            itemname,
                                            t._testMethodName)
                    module["tests"].append({"function": t,
                                            "testtype": "unittest",
                                            "funname": funname})
        yield module


def duration_and_success_status(frec, dry_run):
    test_result = unittest.TestResult()
    t = time.time()
    try:
        if not dry_run:
            if frec["testtype"] == "unittest":
                frec["function"](test_result)
            else:
                assert frec["testtype"] == "function"
                frec["function"]()
    except Exception, e:   # handle failing functions
        traceback.print_exc()
        return time.time() - t, False
    else:
        if not test_result.wasSuccessful():
            print
            print "\n".join([e[1] for e in test_result.failures + test_result.errors])
        return time.time() - t, test_result.wasSuccessful()


def unroll_into_functions(modules_gen):
    for m in modules_gen:
        for f in m["tests"]:
            f["modname"] = m["modname"]
            f["module"] = m["module"]
            f["dir"] = m["dir"]
            f["file"] = m["file"]
            f["saved"] = m["saved"]
            yield f


def get_all_wanted_files(rootdirs, excluded_files, excluded_dirs):
    pyfiles = find_python_files(rootdirs, excluded_dirs)
    py_updated = find_python_update_times(excluded_dirs, pyfiles)
    return wanted_files(excluded_files, excluded_dirs, py_updated)


def get_functions_from_files(files):
    with_modules = find_modules(files)
    unittest_funs = get_unittest_functions(with_modules)
    with_testfuns = get_test_functions_for_modules(unittest_funs)
    return unroll_into_functions(with_testfuns)


def pr(x):
    print x,
    sys.stdout.flush()
    

import pprint;
def pp(*args):
    pprint.PrettyPrinter().pprint(args)


# STATES
START = "S"
RUN = "R"
WAIT = "w"


def any_files_have_changed(filedict, last_check, verbose_level):
    for f in filedict:
        if f["saved"] > last_check:
            if verbose_level > 1:
                print "%s %s has changed" % ("." * 30, f["path"])
            return True


def run(frec, verbose_level, dry_run):
    if verbose_level > 1:
        print frec["funname"],
        sys.stdout.flush()
    duration, succeeded = duration_and_success_status(frec, dry_run)
    if verbose_level == 1 and succeeded:
        os.write(sys.stdout.fileno(), ".")
        sys.stdout.flush()
    elif verbose_level > 1 and succeeded:
        print "%.4fs" % duration
    return duration, succeeded


def continuously_test(rootdirs, excluded_files, excluded_dirs,
                      verbose_level=1, dry_run=False):
    file_t = time.time()
    last_timeout = time.time()
    state = START
    funcs = []
    constant_factory = lambda(value): itertools.repeat(value).next
    durations = collections.defaultdict(constant_factory(1E10))
    succeeded = collections.defaultdict(bool)
    while True:
    # for _ in range(100):   # For development with conttest
        if state == START:
            files = get_all_wanted_files(rootdirs, excluded_files, excluded_dirs)
            try:
                funcs = sorted(list(get_functions_from_files(files)),
                               key=lambda f: (succeeded[f["funname"]],
                                              durations[f["funname"]]))
            except (IndentationError, SyntaxError):
                traceback.print_exc()
                state = WAIT
                continue
            state = RUN

        if state == RUN:
            if not funcs:
                print "\nOK"
                state = WAIT
                continue
            f = funcs.pop(0)
            testtime, result = run(f, verbose_level, dry_run)
            durations[f["funname"]] = testtime
            succeeded[f["funname"]] = result
            if result == False:
                state = WAIT
                continue
            t = time.time()
            if t - last_timeout > 0.5:
                last_timeout = t
                files = get_all_wanted_files(rootdirs, excluded_files, excluded_dirs)
                if any_files_have_changed(files, file_t, verbose_level):
                    file_t = time.time()
                    state = START
                    continue

        if state == WAIT:
            files = get_all_wanted_files(rootdirs, excluded_files, excluded_dirs)
            if any_files_have_changed(files, file_t, verbose_level):
                file_t = time.time()
                state = START
            else:
                time.sleep(0.05)
    # print "XXXXX"    # For development with conttest
