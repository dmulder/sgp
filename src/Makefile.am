
sgp: sgp.in
	sed -e 's;/usr/bin/python;$(PYTHON);g' < $(srcdir)/sgp.in > $(srcdir)/sgp
	chmod +x sgp

bin_SCRIPTS = sgp

CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = sgp.in

