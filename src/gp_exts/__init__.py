import logging, os, sys
from samba.gpclass import apply_gp
from samba.param import LoadParm
from samba.credentials import Credentials

# Get a list of modules names
def list_modules(filename):
    from os import listdir
    from os.path import dirname, abspath, splitext
    module_names = []
    for f in listdir(dirname(abspath(filename))):
        split = splitext(f)
        if not '__init__' in f and (split[-1] == '.py' or split[-1] == '.pyc'):
            module_names.append(split[0])
    return list(set(module_names))

# Find the top base class of a class
# doesn't work with multiple base classes
def get_base(cls):
    base = None
    bases = cls.__bases__
    while len(bases) == 1 and bases[-1].__name__ != 'object':
        base = bases[0]
        bases = base.__bases__
    return base

def get_gp_exts_from_module(parent):
    import inspect
    parent_gp_exts = []
    for mod_name in parent.modules:
        mod = getattr(parent, mod_name)
        clses = inspect.getmembers(mod, inspect.isclass)
        for cls in clses:
            base = get_base(cls[-1])
            if base and base.__name__ == 'gp_ext' and cls[-1].__module__ == mod.__name__:
                parent_gp_exts.append(cls[-1])
    return parent_gp_exts

from gp_exts.gpmachine import *
machine_gp_exts = get_gp_exts_from_module(gpmachine)
from gp_exts.gpuser import *
user_gp_exts = get_gp_exts_from_module(gpuser)

def user_policy_apply(user, password):
    logger = logging.getLogger('gpupdate')
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.WARNING)
    lp = LoadParm()
    lp.load_default()
    creds = Credentials()
    creds.guess(lp)
    creds.set_username(user)
    creds.set_password(password)
    gp_extensions = []
    for ext in user_gp_exts:
        gp_extensions.append(ext(logger, creds))
    cache_dir = lp.get('cache directory')
    store = GPOStorage(os.path.join(cache_dir, 'gpo.tdb'))
    apply_gp(lp, creds, None, logger, store, gp_extensions)

