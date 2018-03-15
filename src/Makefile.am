
all-local:
	(cd $(srcdir); $(PYTHON) ./setup.py build \
		--build-base $(shell readlink -f $(builddir))/build \
		--verbose)

install-exec-local:
	$(PYTHON) $(srcdir)/setup.py install \
		--prefix $(DESTDIR)$(prefix) \
		--record $(builddir)/install_files \
		--verbose

uninstall-local:
	cat $(builddir)/install_files | xargs rm -rf

clean-local:
	rm -rf $(builddir)/build
	rm -rf $(builddir)/gp_exts.egg-info

sgp: sgp.in
	sed -e 's;/usr/bin/python;$(PYTHON);g' < $(srcdir)/sgp.in > $(srcdir)/sgp
	chmod +x sgp

bin_SCRIPTS = sgp

pam_gpupdate_la_SOURCES = gpupdate.c
pam_gpupdate_la_LDFLAGS = -module ${PYTHON_LDFLAGS}
pam_gpupdate_la_CFLAGS = ${PYTHON_CFLAGS}
libsecurity_LTLIBRARIES = pam_gpupdate.la

CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = sgp.in

