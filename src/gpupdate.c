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
    asprintf(&cmd, "import gp_exts\n"
                   "gp_exts.user_policy_apply('%s', '%s')\n",
             user, password
        );
	PyRun_SimpleString(cmd);
	free(cmd);


	return PAM_SUCCESS;
}
