Summary: Audit user space tools for 2.6 kernel auditing.
Name: audit
Version: 0.5
Release: 1
License: GPL
Group: system
URL: http://people.redhat.com/faith/audit/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description

Author: Rik Faith
Maintainer: Charlie Bennett (ccb@redhat.com)

The audit package contains the user space utilities for
storing and processing the audit records generate by
the audit subsystem in the Linux 2.6 kernel.

%prep
%setup -q

%build
./configure
make

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}/sbin
install -m 750 auditctl %{buildroot}/sbin/auditctl
install -m 750 auditd %{buildroot}/sbin/auditd


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%attr(750,root,root) /sbin/auditctl
%attr(750,root,root) /sbin/auditd
%doc


%changelog
* Wed Sep  1 2004 root <root@redhat.com> - 
- Initial build.

