AC_INIT([sgp], [0.1])

AM_INIT_AUTOMAKE

AM_PATH_PYTHON([2.7])
AX_PYTHON_DEVEL
PYTHON_CFLAGS=`${PYTHON}-config --cflags`
PYTHON_LDFLAGS=`${PYTHON}-config --libs`

AC_SUBST(PYTHON_CFLAGS)
AC_SUBST(PYTHON_LDFLAGS)

AC_PROG_CC
LT_INIT

AC_CONFIG_FILES([Makefile src/Makefile])

AC_ARG_WITH([libsecuritydir],
    [AS_HELP_STRING([--with-libsecuritydir],
        [Directory for PAM modules, pass /lib/security for live install])],
    [], [with_libsecuritydir='$(libdir)/security'])
AC_SUBST([libsecuritydir], [$with_libsecuritydir])

AC_OUTPUT
