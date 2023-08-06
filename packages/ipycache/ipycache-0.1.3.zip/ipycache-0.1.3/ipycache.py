# -*- coding: utf-8 -*-
"""Defines a %%cache cell magic in the notebook to persistent-cache results of 
long-lasting computations.
"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
import inspect, os, sys, textwrap, cPickle

# Our own
from IPython.config.configurable import Configurable
from IPython.core import magic_arguments
from IPython.core.magic import Magics, magics_class, line_magic, cell_magic
from IPython.utils.traitlets import Unicode


#------------------------------------------------------------------------------
# Six utility functions for Python 2/3 compatibility
#------------------------------------------------------------------------------
# Author: "Benjamin Peterson <benjamin@python.org>"
    
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    _iteritems = "items"
    
    exec_ = getattr(moves.builtins, "exec")
else:
    _iteritems = "iteritems"
    
    def exec_(_code_, _globs_=None, _locs_=None):
        """Execute code in a namespace."""
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")
    
def iteritems(d, **kw):
    """Return an iterator over the (key, value) pairs of a dictionary."""
    return iter(getattr(d, _iteritems)(**kw))


#------------------------------------------------------------------------------
# Functions
#------------------------------------------------------------------------------
def clean_var(var):
    """Clean variable name, removing accidental commas, etc."""
    return var.strip().replace(',', '')

def clean_vars(vars):
    """Clean variable names, removing accidental commas, etc."""
    return sorted(map(clean_var, vars))

def do_save(path, force=False, read=False):
    """Return True or False whether the variables need to be saved or not."""
    if force and read:
        raise ValueError(("The 'force' and 'read' options are "
                          "mutually exclusive."))
         
    # Execute the cell and save the variables.
    return force or (not read and not os.path.exists(path))
    
def load_vars(path, vars):
    """Load variables from a cPickle file.
    
    Arguments:
    
      * path: the path to the pickle file.
      * vars: a list of variable names.
    
    Returns:
    
      * cache: a dictionary {var_name: var_value}.
    
    """
    with open(path, 'rb') as f:
        # Load the variables from the cache.
        try:
            cache = cPickle.load(f)
        except EOFError as e:
            raise IOError(e.message)
        
        # Check that all requested variables could be loaded successfully
        # from the cache.
        missing_vars = sorted(set(vars) - set(cache.keys()))
        if missing_vars:
            raise ValueError(("The following variables could not be loaded "
                "from the cache: {0:s}").format(
                ', '.join(["'{0:s}'".format(var) for var in missing_vars])))
        
        return cache

def save_vars(path, vars_d):
    """Save variables into a cPickle file.
    
    Arguments:
    
      * path: the path to the pickle file.
      * vars_d: a dictionary {var_name: var_value}.
    
    """
    with open(path, 'wb') as f:
        cPickle.dump(vars_d, f)
    
def cache(cell, path, vars=[],
          # HACK: this function implementing the magic's logic is testable
          # without IPython, by giving mock functions here instead of IPython
          # methods.
          ip_user_ns={}, ip_run_cell=None, ip_push=None,
          force=False, read=False, verbose=True):
    
    if not path:
        raise ValueError("The path needs to be specified as a first argument.")
        
    if do_save(path, force=force, read=read):
        ip_run_cell(cell)
        # Create the cache from the namespace.
        try:
            cache = {var: ip_user_ns[var] for var in vars}
        except KeyError:
            raise ValueError(("Variable '{0:s}' could not be found in the "
                              "interactive namespace").format(var))
        # Save the cache in the pickle file.
        save_vars(path, cache)
        if verbose:
            print("Saved variables {0:s} to file '{1:s}'.".format(
                ', '.join(vars), path))
        
    # If the cache file exists, and no --force mode, load the requested 
    # variables from the specified file into the interactive namespace.
    else:
        # Load the variables from cache in inject them in the namespace.
        ip_push(load_vars(path, vars))
        
        if verbose:
            print(("Skipped the cell's code and loaded variables {0:s} "
                   "from file '{1:s}'.").format(', '.join(vars), path))
        
    
#------------------------------------------------------------------------------
# Magics class
#------------------------------------------------------------------------------
@magics_class
class CacheMagics(Magics, Configurable):
    """Variable caching.

    Provides the %cache magic."""
    
    cachedir = Unicode('', config=True)
    
    @magic_arguments.magic_arguments()
    @magic_arguments.argument(
        'to', nargs=1, type=str,
        help="Path to the file containing the cached variables."
    )
    @magic_arguments.argument(
        'vars', nargs='*', type=str,
        help="Variables to save."
    )
    @magic_arguments.argument(
        '-v', '--verbose', action='store_true', default=True,
        help="Display information when loading/saving variables."
    )
    @magic_arguments.argument(
        '-d', '--cachedir',
        help="Cache directory as an absolute or relative path."
    )
    @magic_arguments.argument(
        '-f', '--force', action='store_true', default=False,
        help="Force the cell's execution and save the variables."
    )
    @magic_arguments.argument(
        '-r', '--read', action='store_true', default=False,
        help=("Always read from the file and prevent the cell's execution, "
              "raising an error if the file does not exist.")
    )
    @cell_magic
    def cache(self, line, cell):
        """Cache user variables in a file, and skip the cell if the cached
        variables exist.
        
        Usage:
        
            %%cache myfile.pkl var1 var2
            # If myfile.pkl doesn't exist, this cell is executed and 
            # var1 and var2 are saved in this file.
            # Otherwise, the cell is skipped and these variables are
            # injected from the file to the interactive namespace.
            var1 = ...
            var2 = ...
        
        """
        ip = self.shell
        args = magic_arguments.parse_argstring(self.cache, line)
        code = cell if cell.endswith('\n') else cell+'\n'
        vars = clean_vars(args.vars)
        path = args.to[0]
        # The cachedir can be specified with --cachedir or in
        # ipython_config.py
        try:
            cachedir_profile = ip.config.CacheMagics.cachedir
        except AttributeError:
            cachedir_profile = self.cachedir
        cachedir = args.cachedir or cachedir_profile
        # If path is relative, use the user-specified cache cachedir.
        if not os.path.isabs(path) and cachedir:
            # Try to create the cachedir if it does not already exist.
            if not os.path.exists(cachedir):
                try:
                    os.mkdir(cachedir)
                    print("Created cachedir '{0:s}'.".format(cachedir))
                except:
                    pass
            path = os.path.join(cachedir, path)
        cache(cell, path, vars=vars, 
              force=args.force, verbose=args.verbose, read=args.read,
              # IPython methods
              ip_user_ns=ip.user_ns, 
              ip_run_cell=ip.run_cell,
              ip_push=ip.push,
              )
        

def load_ipython_extension(ip):
    """Load the extension in IPython."""
    ip.register_magics(CacheMagics)
    
