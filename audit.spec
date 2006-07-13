Summary: User space tools for 2.6 kernel auditing
Name: audit
Version: 1.2.5
Release: 1
License: GPL
Group: System Environment/Daemons
URL: http://people.redhat.com/sgrubb/audit/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: libtool swig python-devel
BuildRequires: kernel-headers >= 2.6.17
BuildRequires: automake >= 1.9
BuildRequires: autoconf >= 2.59
Requires: %{name}-libs = %{version}-%{release}
Requires: chkconfig

%description
The audit package contains the user space utilities for
storing and searching the audit records generate by
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
Requires: kernel-headers >= 2.6.17

%description libs-devel
The audit-libs-devel package contains the static libraries and header 
files needed for developing applications that need to use the audit 
framework libraries.

%package libs-python
Summary: Python bindings for libaudit
License: LGPL
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}
Requires: kernel-headers >= 2.6.17

%description libs-python
The audit-libs-python package contains the bindings so that libaudit
can be used by python.

%prep
%setup -q

%build
autoreconf -fv --install
export CFLAGS="$RPM_OPT_FLAGS"
%configure --sbindir=/sbin --libdir=/%{_lib}
make

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/{sbin,etc/{sysconfig,rc.d/init.d}}
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man8
mkdir -p $RPM_BUILD_ROOT/%{_lib}
mkdir -p $RPM_BUILD_ROOT/usr/{lib,lib32}/audit
mkdir -p $RPM_BUILD_ROOT/%{_var}/log/audit
make DESTDIR=$RPM_BUILD_ROOT install

mkdir -p $RPM_BUILD_ROOT/%{_libdir}
# This winds up in the wrong place when libtool is involved
mv $RPM_BUILD_ROOT/%{_lib}/libaudit.a $RPM_BUILD_ROOT%{_libdir}
mv $RPM_BUILD_ROOT/%{_lib}/libauparse.a $RPM_BUILD_ROOT%{_libdir}
curdir=`pwd`
cd $RPM_BUILD_ROOT/%{_libdir}
LIBNAME=`basename \`ls $RPM_BUILD_ROOT/%{_lib}/libaudit.so.*.*.*\``
ln -s ../../%{_lib}/$LIBNAME libaudit.so
LIBNAME=`basename \`ls $RPM_BUILD_ROOT/%{_lib}/libauparse.so.*.*.*\``
ln -s ../../%{_lib}/$LIBNAME libauparse.so
cd $curdir
# Remove these items so they don't get picked up.
rm -f $RPM_BUILD_ROOT/%{_lib}/libaudit.so
rm -f $RPM_BUILD_ROOT/%{_lib}/libauparse.so
rm -f $RPM_BUILD_ROOT/%{_lib}/libaudit.la
rm -f $RPM_BUILD_ROOT/%{_lib}/libauparse.la
rm -f $RPM_BUILD_ROOT/%{_libdir}/python2.4/site-packages/_audit.a
rm -f $RPM_BUILD_ROOT/%{_libdir}/python2.4/site-packages/_audit.la

%clean
rm -rf $RPM_BUILD_ROOT

%post libs -p /sbin/ldconfig

%post
/sbin/chkconfig --add auditd
if [ -f /etc/auditd.conf ]; then
   mv /etc/auditd.conf /etc/audit/auditd.conf
fi
if [ -f /etc/audit.rules ]; then
   mv /etc/audit.rules /etc/audit/audit.rules
fi
if [ -f /etc/audit/auditd.conf ]; then
   tmp=`mktemp /etc/audit/auditd-post.XXXXXX`
   if [ -n $tmp ]; then
      sed 's|#dispatcher|dispatcher|g' /etc/audit/auditd.conf > $tmp && \
      cat $tmp > /etc/audit/auditd.conf
      rm -f $tmp
   fi
fi

%preun
if [ $1 -eq 0 ]; then
   /sbin/service auditd stop > /dev/null 2>&1
   /sbin/chkconfig --del auditd
fi

%postun libs
/sbin/ldconfig 2>/dev/null

%postun
if [ $1 -ge 1 ]; then
   /sbin/service auditd condrestart > /dev/null 2>&1 || :
fi

%files libs
%defattr(-,root,root)
%attr(755,root,root) /%{_lib}/libaudit.*
%attr(755,root,root) /%{_lib}/libauparse.*
%config(noreplace) %attr(640,root,root) /etc/libaudit.conf

%files libs-devel
%defattr(-,root,root)
%{_libdir}/libaudit.a
%{_libdir}/libauparse.a
%{_libdir}/libaudit.so
%{_libdir}/libauparse.so
%{_includedir}/libaudit.h
%{_mandir}/man3/*

%files libs-python
%defattr(-,root,root)
%{_libdir}/python2.4/site-packages/_audit.so
/usr/lib/python2.4/site-packages/audit.py*

%files
%defattr(-,root,root,-)
%doc  README COPYING ChangeLog sample.rules contrib/capp.rules contrib/lspp.rules contrib/skeleton.c init.d/auditd.cron
%attr(0644,root,root) %{_mandir}/man8/*
%attr(750,root,root) /sbin/auditctl
%attr(750,root,root) /sbin/auditd
%attr(750,root,root) /sbin/ausearch
%attr(750,root,root) /sbin/aureport
%attr(750,root,root) /sbin/autrace
%attr(750,root,root) /sbin/audispd
%attr(755,root,root) /etc/rc.d/init.d/auditd
%attr(750,root,root) %{_var}/log/audit
%attr(750,root,root) %dir /etc/audit
%attr(750,root,root) %dir /usr/lib/audit
%attr(750,root,root) %dir /usr/lib32/audit
%config(noreplace) %attr(640,root,root) /etc/audit/auditd.conf
%config(noreplace) %attr(640,root,root) /etc/audit/audit.rules
%config(noreplace) %attr(640,root,root) /etc/sysconfig/auditd
/usr/lib/python2.4/site-packages/AuditMsg.py*


%changelog
* Thu Jul 13 2006 Steve Grubb <sgrubb@redhat.com> 1.2.5-1
- Switch out dispatcher
- Fix bug upgrading rule types

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.2.4-1.1
- rebuild

* Fri Jun 30 2006 Steve Grubb <sgrubb@redhat.com> 1.2.4-1
- Add support for the new filter key
- Update syscall tables for 2.6.17
- Add audit failure query function
- Switch out gethostbyname call with getaddrinfo
- Add audit by obj capability for 2.6.18 kernel
- Ausearch & aureport now fail if no args to -te
- New auditd.conf option to choose blocking/non-blocking dispatcher comm
- Ausearch improved search by label

* Fri May 25 2006 Steve Grubb <sgrubb@redhat.com> 1.2.3-1
- Apply patch to ensure watches only associate with exit filter
- Apply patch to correctly show new operators when new listing format is used
- Apply patch to pull kernel's audit.h into python bindings
- Collect signal sender's context

* Tue May 16 2006 David Woodhouse <dwmw2@redhat.com> 1.2.2-2
- Require kernel-headers, not glibc-kernheaders. Again.

* Fri May 12 2006 Steve Grubb <sgrubb@redhat.com> 1.2.2-1
- Updates for new glibc-kernheaders
- Change auditctl to collect list of rules then delete them on -D
- Update capp.rules and lspp.rules to comment out rules for the possible list
- Add new message types
- Support sigusr1 sender identity of newer kernels
- Add support for ppid in auditctl and ausearch
- fix auditctl to trim the '/' from watches
- Move audit daemon config files to /etc/audit for better SE Linux protection

* Wed Apr 25 2006 David Woodhouse <dwmw2@redhat.com> 1.2.1-2
- Require kernel-headers, not glibc-kernheaders
- Fix redefinition of audit_rule_data with new kernel headers
- Remove abuse of __KERNEL__ in lookup_table.c

* Sun Apr 16 2006 Steve Grubb <sgrubb@redhat.com> 1.2.1-1
- New message type for trusted apps
- Add new keywords today, yesterday, now for ausearch and aureport
- Make audit_log_user_avc_message really send to syslog on error
- Updated syscall tables in auditctl
- Deprecated the 'possible' action for syscall rules in auditctl
- Update watch code to use file syscalls instead of 'all' in auditctl

* Fri Apr 7 2006 Steve Grubb <sgrubb@redhat.com> 1.2-1
- Add support for new file system auditing kernel subsystem

* Thu Apr 6 2006 Steve Grubb <sgrubb@redhat.com> 1.1.6-1
- New message types
- Support new rule format found in 2.6.17 and later kernels
- Add support for audit by role, clearance, type, sensitivity

* Wed Mar 6 2006 Steve Grubb <sgrubb@redhat.com> 1.1.5-1
- Changed audit_log_semanage_message to take new params
- In aureport, add class between syscall and permission in avc report
- Fix bug where fsync is called in debug mode
- Add optional support for tty in SYSCALL records for ausearch/aureport
- Reinstate legacy rule operator support
- Add man pages
- Auditd ignore most signals

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.1.4-5.1
- bump again for double-long bug on ppc(64)

* Fri Feb 10 2006 Steve Grubb <sgrubb@redhat.com> 1.1.4-5
- Change audit_log_semanage_message to check strlen as well as NULL.

* Thu Feb 9 2006 Steve Grubb <sgrubb@redhat.com> 1.1.4-3
- Change audit_log_semanage_message to take new params.

* Wed Feb 8 2006 Steve Grubb <sgrubb@redhat.com> 1.1.4-1
- Fix bug in autrace where it didn't run on kernels without file watch support
- Add syslog message to auditd saying what program was started for dispatcher
- Remove audit_send_user from public api
- Fix bug in USER_LOGIN messages where ausearch does not translate
  msg='uid=500: into acct name (#178102).
- Change comm with dispatcher to socketpair from pipe
- Change auditd to use custom daemonize to avoid race in init scripts
- Update error message when deleting a rule that doesn't exist (#176239)
- Call shutdown_dispatcher when auditd stops
- Add new logging function audit_log_semanage_message

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.1.3-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Thu Jan 5 2006 Steve Grubb <sgrubb@redhat.com> 1.1.3-1
- Add timestamp to daemon_config messages (#174865)
- Add error checking of year for aureport & ausearch
- Treat af_unix sockets as files for searching and reporting
- Update capp & lspp rules to combine syscalls for higher performance
- Adjusted the chkconfig line for auditd to start a little earlier
- Added skeleton program to docs for people to write their own dispatcher with
- Apply patch from Ulrich Drepper that optimizes resource utilization
- Change ausearch and aureport to unlocked IO

* Thu Dec 5 2005 Steve Grubb <sgrubb@redhat.com> 1.1.2-1
- Add more message types

* Wed Nov 30 2005 Steve Grubb <sgrubb@redhat.com> 1.1.1-1
- Add support for alpha processors
- Update the audisp code
- Add locale code in ausearch and aureport
- Add new rule operator patch
- Add exclude filter patch
- Cleanup make files
- Add python bindings

* Wed Nov 9 2005 Steve Grubb <sgrubb@redhat.com> 1.1-1
- Add initial version of audisp. Just a placeholder at this point
- Remove -t from auditctl

* Mon Nov 7 2005 Steve Grubb <sgrubb@redhat.com> 1.0.12-1
- Add 2 more summary reports
- Add 2 more message types

