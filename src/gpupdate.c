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
	PyObject *pName, *pModule, *pFunc;
	PyObject *pArgs, *pValue;

	ret = pam_get_item(pamh, PAM_USER, &user);
	if (ret != PAM_SUCCESS) return ret;

	ret = pam_get_item(pamh, PAM_AUTHTOK, &password);

	Py_Initialize();
	pName = PyUnicode_FromString("gp_exts");
	pModule = PyImport_Import(pName);
	Py_DECREF(pName);

	if (pModule != NULL) {
		pFunc = PyObject_GetAttrString(pModule, "user_policy_apply");
		if (pFunc && PyCallable_Check(pFunc)) {
			pArgs = PyTuple_New(2);
			pValue = PyUnicode_FromString(user);
			if (!pValue) {
				return PAM_ABORT;
			}
			PyTuple_SetItem(pArgs, 0, pValue);
			pValue = PyUnicode_FromString(password);
			if (!pValue) {
				return PAM_ABORT;
			}
			PyTuple_SetItem(pArgs, 1, pValue);
			PyObject_CallObject(pFunc, pArgs);
		} else {
			return PAM_ABORT;
		}
	} else {
		return PAM_ABORT;
	}

	return PAM_SUCCESS;
}
