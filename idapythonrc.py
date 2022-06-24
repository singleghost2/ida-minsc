"""
Internal initialization script

This is an internal script that is executed when IDA starts. Things
such as meta_path hooks, replacing the namespace with the contents
of the __root__ module, and implementing a work-around for the hack
that IDAPython does with saving the contents of sys.modules. After
initializing everything, this script will then hand off execution
to the user's idapythonrc.py in their home directory.
"""

# output the IDAPython banner when IDA starts
print_banner()

# some general python modules that we use for meta_path
import sys, os, imp
import idaapi

# grab ida's user directory and remove from it from the path since we use
# python's meta_path to locate all of our modules. we also use this path
# to find out where our loader logic is actually located.
root = idaapi.get_user_idadir()
sys.path.remove(root)

# grab the loader, and then use it to seed python's meta_path.
loader = imp.load_source('__loader__', os.path.join(root, 'plugins', 'minsc.py'))
sys.meta_path.extend(loader.finders())

# now we can just load it into the globals() namespace. we don't need
# to delete it, because it gets popped out of existence during load.
loader.load(globals(), preserve={'_orig_stdout', '_orig_stderr'})

# try and execute our user's idapythonrc.py
try:
    import os
    path, filename = None, '.idapythonrc.py'

    try:
        # execute user's .pythonrc and .idapythonrc in one go
        if os.path.expanduser("~"):
            path = os.path.expanduser("~")
            exec(open(os.path.join(path, filename)).read())

    except ImportError:
        # otherwise try to figure it out without tainting the namespace
        if __import__('os').getenv('HOME', default=None) is not None:
            path = os.getenv('HOME')
            exec(open(os.path.join(path, filename)).read())
        elif __import__('os').getenv('USERPROFILE', default=None) is not None:
            path = os.getenv('USERPROFILE')
            exec(open(os.path.join(path, filename)).read())
        else:
            raise OSError("unable to determine the user's home directory.")
        pass

except IOError:
    __import__('logging').warning("No {:s} file found in the user's home directory ({!s}).".format(filename, path))

except Exception:
    __import__('logging').warning("Unexpected exception raised while trying to execute `{!s}`.".format(os.path.join(path or '~', filename)), exc_info=True)

finally:
    del(filename)
    del(path)
    del(os)

## stupid fucking idapython hax
# prevent idapython from trying to write its banner to the message window since we called it up above.
print_banner = lambda: None

# find the frame that fucks with our sys.modules, and save it for later
frame = __import__('sys')._getframe()
while frame.f_code.co_name != 'IDAPython_ExecScript':
    frame = frame.f_back

# inject our current sys.modules state into IDAPython_ExecScript's state if it's the broken version
if 'basemodules' in frame.f_locals:
    frame.f_locals['basemodules'].update(__import__('sys').modules)
del(frame)
