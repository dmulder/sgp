import logging, os, sys
from samba.gpclass import apply_gp, GPOStorage
from samba.param import LoadParm
from samba.credentials import Credentials

def user_policy_apply(user, password):
    user = user.split('\\')[-1]

    logger = logging.getLogger('gpupdate')
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.CRITICAL)
    log_level = lp.log_level()
    if log_level == 1:
        logger.setLevel(logging.ERROR)
    elif log_level == 2:
        logger.setLevel(logging.WARNING)
    elif log_level == 3:
        logger.setLevel(logging.INFO)
    elif log_level >= 4:
        logger.setLevel(logging.DEBUG)
    lp = LoadParm()
    lp.load_default()
    creds = Credentials()
    creds.guess(lp)
    creds.set_username(user)
    creds.set_password(password)

    _, user_exts = get_gp_client_side_extensions(logger)
    gp_extensions = []
    for ext in user_exts:
        gp_extensions.append(ext(logger, lp, creds, store))

    cache_dir = lp.get('cache directory')
    store = GPOStorage(os.path.join(cache_dir, 'gpo.tdb'))
    try:
        apply_gp(lp, creds, logger, store, gp_extensions)
    except NTSTATUSError as e:
        logger.info(e.message)

