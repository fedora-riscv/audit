Summary: User space tools for 2.6 kernel auditing.
Name: audit
Version: 0.6
Release: 1
License: GPL
Group: System Environment/Daemons
URL: http://people.redhat.com/sgrubb/audit/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: glibc-kernheaders pam-devel libtool
Requires: %{name}-libs = %{version}-%{release}
Requires: chkconfig

%description
The audit package contains the user space utilities for
storing and processing the audit records generate by
the audit subsystem in the Linux 2.6 kernel.

%package libs
Summary: Dynamic library for libaudit
License: LGPL
Group: Development/Libraries

%description libs
The audit-libs package contains the dynamic libraries needed for 
applications to use the audit framework.

%package libs-devel
Summary: Header files and static library for libaudit
License: LGPL
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}

%description libs-devel
The audit-libs-devel package contains the static libraries and header 
files needed for developing applications that need to use the audit 
framework libraries.

%prep
%setup -q

%build
autoreconf -fv --install
./configure --sbindir=/sbin --mandir=%{_mandir} --libdir=/lib --with-pam=yes
make

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/{sbin,etc/{sysconfig,rc.d/init.d}}
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man8
mkdir -p $RPM_BUILD_ROOT/lib/security
make DESTDIR=$RPM_BUILD_ROOT install

mkdir -p $RPM_BUILD_ROOT/%{_includedir}
mkdir -p $RPM_BUILD_ROOT/%{_libdir}
# We manually install this since Makefile doesn't
install -m 0644 lib/libaudit.h $RPM_BUILD_ROOT/%{_includedir}
# This winds up in the wrong place when libtool is involved
mv $RPM_BUILD_ROOT/lib/libaudit.a $RPM_BUILD_ROOT%{_libdir}
mv $RPM_BUILD_ROOT/lib/libaudit.la $RPM_BUILD_ROOT%{_libdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post libs
/sbin/ldconfig 2>/dev/null

%post
/sbin/ldconfig 2>/dev/null
if [ $1 = 1 ]; then
   /sbin/chkconfig --add auditd
fi

%preun
if [ $1 = 0 ]; then
   /sbin/service auditd stop > /dev/null 2>&1
   /sbin/chkconfig --del auditd
fi

%postun libs
/sbin/ldconfig 2>/dev/null

%postun
/sbin/ldconfig 2>/dev/null
if [ $1 -ge 1 ]; then
   /sbin/service auditd condrestart > /dev/null 2>&1
fi

%files libs
%defattr(-,root,root)
%attr(755,root,root) /lib/libaudit.*

%files libs-devel
%defattr(-,root,root)
%{_libdir}/libaudit.*
%{_includedir}/libaudit.h
%{_mandir}/man3/*

%files
%defattr(-,root,root,-)
%doc ChangeLog
%attr(0644,root,root) %{_mandir}/man8/*
%attr(750,root,root) /sbin/auditctl
%attr(750,root,root) /sbin/auditd
%attr(755,root,root) /lib/security/pam_audit.so
%attr(755,root,root) /etc/rc.d/init.d/auditd
%config(noreplace) %attr(640,root,root) /etc/auditd.conf
%config(noreplace) %attr(640,root,root) /etc/sysconfig/auditd


%changelog
* Wed Jan 05 2005 Steve Grubb <sgrubb@redhat.com> 0.6-1
- New version
- Split package up to libs, libs-devel, and audit.

* Mon Dec 13 2004 Steve Grubb <sgrubb@redhat.com> 0.5.6-1
- New version

* Fri Dec 10 2004 Steve Grubb <sgrubb@redhat.com> 0.5.5-1
- New version

* Fri Dec 03 2004 Steve Grubb <sgrubb@redhat.com> 0.5.4-1
- New version

* Mon Nov 22 2004 Steve Grubb <sgrubb@redhat.com> 0.5.3-1
- New version

* Mon Nov 15 2004 Steve Grubb <sgrubb@redhat.com> 0.5.2-1
- New version

* Wed Nov 10 2004 Steve Grubb <sgrubb@redhat.com> 0.5.1-1
- Added initscript pieces
- New version

* Wed Sep  1 2004 Charlie Bennett (ccb@redhat.com) 0.5-1 
- Initial build.

