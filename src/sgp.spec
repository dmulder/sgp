#
# spec file for package sgp
#
# Copyright (c) 2018 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


Name:           sgp
Version:        0.1
Release:        0
Summary:        Group Policy client apply for Samba
License:        GPL-3.0
Group:          Productivity/Networking/Samba
Url:            http://www.github.com/dmulder/sgp
Source:         https://github.com/dmulder/sgp/archive/v%{version}.tar.gz
BuildArch:      noarch
Requires:       samba-winbind
Requires:       samba-python
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  python
BuildRequires:  python-devel
BuildRequires:  gcc

%description
Group Policy client apply for Samba

%prep
%setup -q

%build
autoreconf -if
%configure
make

%install
make DESTDIR=$RPM_BUILD_ROOT install

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_bindir}/sgp

%changelog
