Summary: User space tools for 2.6 kernel auditing.
Name: audit
Version: 0.5.1
Release: 1
License: GPL
Group: System Environment/Daemons
URL: http://people.redhat.com/faith/audit/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: pam-devel

%description

The audit package contains the user space utilities for
storing and processing the audit records generate by
the audit subsystem in the Linux 2.6 kernel.

%prep
%setup -q

%build
autoreconf -fv --install
./configure --sbindir=/sbin --mandir=%{_mandir}
make

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/{sbin,etc/{sysconfig,rc.d/init.d}}
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man8
mkdir -p $RPM_BUILD_ROOT/lib/security
make DESTDIR=$RPM_BUILD_ROOT install


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc ChangeLog
%attr(0644,root,root) %{_mandir}/man8/*
%attr(750,root,root) /sbin/auditctl
%attr(750,root,root) /sbin/auditd
#%attr(755,root,root) /lib/security/pam_audit.so
%attr(755,root,root) /etc/rc.d/init.d/auditd
%config(noreplace) %attr(640,root,root) /etc/sysconfig/auditd



%changelog
* Wed Nov 10 2004 Steve Grubb <sgrubb@redhat.com> 0.5.1-1
- Added initscript pieces
- New version

* Wed Sep  1 2004 Charlie Bennett (ccb@redhat.com) 0.5-1 
- Initial build.

