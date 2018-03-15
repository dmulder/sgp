#include <Python.h>
#include <security/pam_appl.h>
#include <security/pam_modules.h>
#include <stdio.h>

PAM_EXTERN int pam_sm_setcred( pam_handle_t *pamh, int flags, int argc, const char **argv)
{
	return PAM_SUCCESS;
}

PAM_EXTERN int pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc, const char **argv)
{
	return PAM_SUCCESS;
}

PAM_EXTERN int pam_sm_authenticate(pam_handle_t *pamh, int flags,int argc, const char **argv)
{
	int ret;
	const char *user, *password;
	char *cmd;

	ret = pam_get_item(pamh, PAM_USER, &user);
	if (ret != PAM_SUCCESS) return ret;

	ret = pam_get_item(pamh, PAM_AUTHTOK, &password);

	Py_Initialize();
	asprintf(&cmd, "import logging, os, sys\n"
                   "import gp_exts\n"
				   "from samba.gpclass import apply_gp\n"
				   "from samba.param import LoadParm\n"
				   "from samba.credentials import Credentials\n"
				   "import gp_exts\n"
				   "logger = logging.getLogger('gpupdate')\n"
				   "logger.addHandler(logging.StreamHandler(sys.stdout))\n"
				   "logger.setLevel(logging.WARNING)\n"
				   "lp = LoadParm()\n"
				   "lp.load_default()\n"
				   "creds = Credentials()\n"
				   "creds.guess(lp)\n"
				   "creds.set_username('%s')\n"
				   "creds.set_password('%s')\n"
				   "gp_extensions = []\n"
				   "for ext in gp_exts.user_gp_exts:\n"
				   "    gp_extensions.append(ext(logger, creds))\n"
				   "cache_dir = lp.get('cache directory')\n"
				   "store = GPOStorage(os.path.join(cache_dir, 'gpo.tdb'))\n"
				   "apply_gp(lp, creds, None, logger, store, gp_extensions)\n",
			 user, password
		);
	PyRun_SimpleString(cmd);
	free(cmd);


	return PAM_SUCCESS;
}
