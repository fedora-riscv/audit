%define sca_version 0.4.5
%define sca_release 1
%define selinux_variants mls strict targeted
%define selinux_policyver %(rpm -q selinux-policy | sed -e 's,^selinux-policy-\\([^/]*\\)$,\\1,')

Summary: User space tools for 2.6 kernel auditing
Name: audit
Version: 1.6.5
Release: 1%{?dist}
License: GPLv2+
Group: System Environment/Daemons
URL: http://people.redhat.com/sgrubb/audit/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: gettext-devel intltool libtool swig python-devel
BuildRequires: kernel-headers >= 2.6.18
BuildRequires: automake >= 1.9
BuildRequires: autoconf >= 2.59
Requires: %{name}-libs = %{version}-%{release}
Requires: chkconfig
Prereq: coreutils

%description
The audit package contains the user space utilities for
storing and searching the audit records generate by
the audit subsystem in the Linux 2.6 kernel.

%package libs
Summary: Dynamic library for libaudit
License: LGPLv2+
Group: Development/Libraries

%description libs
The audit-libs package contains the dynamic libraries needed for 
applications to use the audit framework.

%package libs-devel
Summary: Header files and static library for libaudit
License: LGPLv2+
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}
Requires: kernel-headers >= 2.6.18

%description libs-devel
The audit-libs-devel package contains the static libraries and header 
files needed for developing applications that need to use the audit 
framework libraries.

%package libs-python
Summary: Python bindings for libaudit
License: LGPLv2+
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}

%description libs-python
The audit-libs-python package contains the bindings so that libaudit
and libauparse can be used by python.

%package -n audispd-plugins
Summary: Plugins for the audit event dispatcher
License: GPLv2+
Group: System Environment/Daemons
BuildRequires: openldap-devel
BuildRequires: checkpolicy selinux-policy-devel
Requires: %{name} = %{version}-%{release}
Requires: %{name}-libs = %{version}-%{release}
Requires: openldap
%if "%{selinux_policyver}" != ""
Requires: selinux-policy >= %{selinux_policyver}
%endif
Requires(post): /usr/sbin/semodule /sbin/restorecon
Requires(postun): /usr/sbin/semodule

%description -n audispd-plugins
The audispd-plugins package provides plugins for the real-time
interface to the audit system, audispd. These plugins can do things
like relay events to remote machines or analyze events for suspicious
behavior.

%package -n system-config-audit
Summary: Utility for editing audit configuration
Version: %{sca_version}
Release: %{sca_release}%{?dist}
License: GPLv2+
Group: Applications/System
Requires: pygtk2-libglade usermode usermode-gtk

%description -n system-config-audit
A graphical utility for editing audit configuration.

%prep
%setup -q
mkdir zos-remote-policy
cp -p audisp/plugins/zos-remote/policy/audispd-zos-remote.* zos-remote-policy

%build
(cd system-config-audit; ./autogen.sh)
aclocal && autoconf && autoheader && automake
%configure --sbindir=/sbin --libdir=/%{_lib}
make
cd zos-remote-policy
for selinuxvariant in %{selinux_variants}
do
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
  mv audispd-zos-remote.pp audispd-zos-remote.pp.${selinuxvariant}
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
done
cd -

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/{sbin,etc/{sysconfig,audispd/plugins.d,rc.d/init.d}}
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/{man5,man8}
mkdir -p $RPM_BUILD_ROOT/%{_lib}
mkdir -p $RPM_BUILD_ROOT/%{_libdir}/audit
mkdir -p $RPM_BUILD_ROOT/%{_var}/log/audit
make DESTDIR=$RPM_BUILD_ROOT install
make -C system-config-audit DESTDIR=$RPM_BUILD_ROOT install-fedora
for selinuxvariant in %{selinux_variants}
do
  install -d $RPM_BUILD_ROOT/%{_datadir}/selinux/${selinuxvariant}
  install -p -m 644 zos-remote-policy/audispd-zos-remote.pp.${selinuxvariant} \
    $RPM_BUILD_ROOT/%{_datadir}/selinux/${selinuxvariant}/audispd-zos-remote.pp
done

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
rm -f $RPM_BUILD_ROOT/%{_libdir}/python?.?/site-packages/_audit.a
rm -f $RPM_BUILD_ROOT/%{_libdir}/python?.?/site-packages/_audit.la
rm -f $RPM_BUILD_ROOT/%{_libdir}/python?.?/site-packages/_auparse.a
rm -f $RPM_BUILD_ROOT/%{_libdir}/python?.?/site-packages/_auparse.la

# On platforms with 32 & 64 bit libs, we need to coordinate the timestamp
touch -r ./audit.spec $RPM_BUILD_ROOT/etc/libaudit.conf

%find_lang system-config-audit

#% check
#make check

%clean
rm -rf $RPM_BUILD_ROOT
rm -rf zos-remote-policy

%post libs -p /sbin/ldconfig

%post -n audispd-plugins
for selinuxvariant in %{selinux_variants}
do
  /usr/sbin/semodule -s $selinuxvariant \
    -i %{_datadir}/selinux/$selinuxvariant/audispd-zos-remote.pp \
    &> /dev/null || :
done
/sbin/restorecon -F /sbin/audispd-zos-remote /etc/audisp/zos-remote.conf

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
      sed 's|^#dispatcher|dispatcher|g' /etc/audit/auditd.conf > $tmp && \
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

%postun -n audispd-plugins
if [ $1 -eq 0 ]; then
 for selinuxvariant in %{selinux_variants}
 do
   /usr/sbin/semodule -s $selinuxvariant -r audispd-zos-remote &>/dev/null || :
 done
fi

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
%doc contrib/skeleton.c contrib/plugin
%{_libdir}/libaudit.a
%{_libdir}/libauparse.a
%{_libdir}/libaudit.so
%{_libdir}/libauparse.so
%{_includedir}/libaudit.h
%{_includedir}/auparse.h
%{_includedir}/auparse-defs.h
%{_mandir}/man3/*

%files libs-python
%defattr(-,root,root)
%{_libdir}/python?.?/site-packages/_audit.so
%{_libdir}/python?.?/site-packages/auparse.so
/usr/lib/python?.?/site-packages/audit.py*

%files
%defattr(-,root,root,-)
%doc  README COPYING ChangeLog contrib/capp.rules contrib/nispom.rules contrib/lspp.rules init.d/auditd.cron
%attr(644,root,root) %{_mandir}/man8/audispd.8.gz
%attr(644,root,root) %{_mandir}/man8/auditctl.8.gz
%attr(644,root,root) %{_mandir}/man8/auditd.8.gz
%attr(644,root,root) %{_mandir}/man8/aureport.8.gz
%attr(644,root,root) %{_mandir}/man8/ausearch.8.gz
%attr(644,root,root) %{_mandir}/man8/autrace.8.gz
%attr(644,root,root) %{_mandir}/man8/aulastlog.8.gz
%attr(644,root,root) %{_mandir}/man5/auditd.conf.5.gz
%attr(644,root,root) %{_mandir}/man5/audispd.conf.5.gz
%attr(750,root,root) /sbin/auditctl
%attr(750,root,root) /sbin/auditd
%attr(755,root,root) /sbin/ausearch
%attr(755,root,root) /sbin/aureport
%attr(750,root,root) /sbin/autrace
%attr(750,root,root) /sbin/audispd
%attr(750,root,root) /sbin/aulastlog
%attr(755,root,root) /etc/rc.d/init.d/auditd
%attr(750,root,root) %{_var}/log/audit
%attr(750,root,root) %dir /etc/audit
%attr(750,root,root) %dir /etc/audisp
%attr(750,root,root) %dir /etc/audisp/plugins.d
%attr(750,root,root) %dir %{_libdir}/audit
%config(noreplace) %attr(640,root,root) /etc/audit/auditd.conf
%config(noreplace) %attr(640,root,root) /etc/audit/audit.rules
%config(noreplace) %attr(640,root,root) /etc/sysconfig/auditd
%config(noreplace) %attr(640,root,root) /etc/audisp/audispd.conf
%attr(640,root,root) /etc/audisp/plugins.d/af_unix.conf

%files -n audispd-plugins
%defattr(-,root,root,-)
%attr(640,root,root) /etc/audisp/plugins.d/syslog.conf
%attr(644,root,root) %{_mandir}/man8/audispd-zos-remote.8.gz
%attr(644,root,root) %{_mandir}/man5/zos-remote.conf.5.gz
%config(noreplace) %attr(640,root,root) /etc/audisp/plugins.d/audispd-zos-remote.conf
%config(noreplace) %attr(640,root,root) /etc/audisp/zos-remote.conf
%attr(750,root,root) /sbin/audispd-zos-remote
%attr(755,root,root) %{_datadir}/selinux/*/audispd-zos-remote.pp

%files -n system-config-audit -f system-config-audit.lang
%defattr(-,root,root,-)
%doc system-config-audit/AUTHORS
%doc system-config-audit/COPYING
%doc system-config-audit/ChangeLog
%doc system-config-audit/NEWS
%doc system-config-audit/README
%{_bindir}/system-config-audit
%{_datadir}/applications/system-config-audit.desktop
%{_datadir}/system-config-audit
%{_libexecdir}/system-config-audit-server-real
%{_libexecdir}/system-config-audit-server
%config(noreplace) %{_sysconfdir}/pam.d/system-config-audit-server
%config(noreplace) %{_sysconfdir}/security/console.apps/system-config-audit-server

%changelog
* Mon Jan 07 2008 Steve Grubb <sgrubb@redhat.com> 1.6.5-1
- New upstream version
- Add RACF zos remote audispd plugin (Klaus Kiwi)
- Fix audit log permissions on rotate. If group is root 0400, otherwise 0440
- Update system-config-audit to version 0.4.5 (Miloslav Trmac)
- Fix keep_logs when num_logs option disabled (#325561)
- Allow use of errno strings for exit codes in audit rules
- If auditd logging was suspended, it can be resumed with SIGUSR2 (#251639)
- Updated CAPP, LSPP, and NISPOM rules for new capabilities
- Added aulastlog utility

* Wed Oct 17 2007 Steve Grubb <sgrubb@redhat.com> 1.6.2-4
- Fix race between threads accessing common data in auditd
- Fix double free in event dispatcher.

* Fri Oct 5 2007 Steve Grubb <sgrubb@redhat.com> 1.6.2-3
- Fix syscall name to number conversion in libaudit.

* Mon Oct 1 2007 Steve Grubb <sgrubb@redhat.com> 1.6.2-2
- Don't retry if the rt queue is full.

* Tue Sep 25 2007 Steve Grubb <sgrubb@redhat.com> 1.6.2-1
- Add support for searching by posix regular expressions in auparse
- Route DEAMON events into rt interface
- If event pipe is full, try again after doing local logging
- Optionally add node/machine name to records in audit daemon
- Update ausearch/aureport to specify nodes to search on
- Fix segfault interpretting saddr fields in avcs

* Thu Sep 6 2007 Steve Grubb <sgrubb@redhat.com> 1.6.1-2
- Fix uninitialized variable in auparse (John Dennis)

* Sun Sep 2 2007 Steve Grubb <sgrubb@redhat.com> 1.6.1-1
- External plugin support in place
- Fix reference counting in auparse python bindings (#263961)
- Moved default af_unix plugin socket to /var/run/audispd_events

* Wed Aug 29 2007 Steve Grubb <sgrubb@redhat.com> 1.6-3
- Add newline to audispd string formatted events

* Tue Aug 28 2007 Steve Grubb <sgrubb@redhat.com> 1.6-2
- spec file cleanups
- Update to s-c-audit 0.4.3

* Mon Aug 27 2007 Steve Grubb <sgrubb@redhat.com> 1.6-1
- Update Licence tags
- Adding perm field should not set syscall added flag in auditctl
- Fix segfault when aureport -if option is used
- Fix auditctl to better check keys on rule lines
- Add support for audit by TTY and other new event types
- Auditd config option for group permission of audit logs
- Swig messed up a variable in ppc's python bindings causing crashes. (#251327)
- New audit event dispatcher
- Update syscall tables for 2.6.23 kernel

* Wed Jul 25 2007 Steve Grubb <sgrubb@redhat.com> 1.5.6-1
- Fix potential buffer overflow in print clone flags of auparse
- Fix python traceback parsing watches without perm statement (Miloslav Trmac)
- Update auditctl to handle legacy kernels when putting a watch on a dir
- Fix acct interpretation in auparse

* Tue Jul 17 2007 Miloslav Trmač <mitr@redhat.com> - 1.5.5-5
- Fix a double free when auditd receives SIGHUP
- Move the system-config-audit menu entry to the Administration menu

* Tue Jul 10 2007 Steve Grubb <sgrubb@redhat.com> 1.5.5-1
- Add system-config-audit (Miloslav Trmac)
- Correct bug in audit_make_equivalent function (Al Viro)

* Tue Jun 26 2007 Steve Grubb <sgrubb@redhat.com> 1.5.4-1
- Add feed interface to auparse library (John Dennis)
- Apply patch to libauparse for unresolved symbols (#241178)
- Apply patch to add line numbers for file events in libauparse (John Dennis)
- Change seresults to seresult in libauparse (John Dennis)
- Add unit32_t definition to swig (#244210)
- Add support for directory auditing
- Update acct field to be escaped

* Tue May 01 2007 Steve Grubb <sgrubb@redhat.com> 1.5.3-1
- Change buffer size to prevent truncation of DAEMON events with large labels
- Fix memory leaks in auparse (John Dennis)
- Update syscall tables for 2.6.21 kernel
- Update capp & lspp rules
- New python bindings for libauparse (John Dennis)

* Thu Apr 04 2007 Steve Grubb <sgrubb@redhat.com> 1.5.2-1
- New event dispatcher (James Antill)
- Apply patches fixing man pages and Makefile.am (Philipp Hahn)
- Apply patch correcting python libs permissions (Philipp Hahn)
- Fix auditd segfault on reload
- Fix bug in auparse library for file pointers and descriptors
- Extract subject information out of daemon events for ausearch

* Thu Mar 29 2007 Steve Grubb <sgrubb@redhat.com> 1.5.1-2
- Remove requires kernel-headers for python-libs
- Apply patch to prevent segfaults on auditd reload

* Tue Mar 20 2007 Steve Grubb <sgrubb@redhat.com> 1.5.1-1
- Updated autrace to monitor *at syscalls
- Add support in libaudit for AUDIT_BIT_TEST(^) and AUDIT_MASK_TEST (&)
- Finish reworking auditd config parser
- In auparse, interpret open, fcntl, and clone flags
- In auparse, when interpreting execve record types, run args through unencode
- Add support for OBJ_PID message type
- Event dispatcher updates

* Fri Mar 2 2007 Steve Grubb <sgrubb@redhat.com> 1.5-2
- rebuild

* Fri Mar 2 2007 Steve Grubb <sgrubb@redhat.com> 1.5-1
- NEW audit dispatcher program & plugin framework
- Correct hidden variables in libauparse
- Added NISPOM sample rules
- Verify accessibility of files passed in auparse_init
- Fix bug in parser library interpreting socketcalls
- Add support for stdio FILE pointer in auparse_init
- Adjust init script to allow anyone to status auditd (#230626)

* Tue Feb 20 2007 Steve Grubb <sgrubb@redhat.com> 1.4.2-1
- Add man pages
- Reduce text relocations in parser library
- Add -n option to auditd for no fork
- Add exec option to space_left, admin_space_left, disk_full,
  and disk_error - eg EXEC /usr/local/script

* Fri Feb 16 2007 Steve Grubb <sgrubb@redhat.com> 1.4.1-1
- updated audit_rule_fieldpair_data to handle perm correctly (#226780)
- Finished search options for audit parsing library
- Fix ausearch -se to work correctly
- Fix auditd init script for /usr on netdev (#228528)
- Parse avc seperms better when there are more than one

* Sun Feb 04 2007 Steve Grubb <sgrubb@redhat.com> 1.4-1
- New report about authentication attempts
- Updates for python 2.5
- update autrace to have resource usage mode
- update auditctl to support immutable config
- added audit_log_user_command function to libaudit api
- interpret capabilities
- added audit event parsing library
- updates for 2.6.20 kernel

* Sun Dec 10 2006 Steve Grubb <sgrubb@redhat.com> 1.3.1-2
- Make more adjustments for python 2.5

* Sun Dec 10 2006 Steve Grubb <sgrubb@redhat.com> 1.3.1-1
- Fix a couple parsing problems (#217952)
- Add tgkill to S390* syscall tables (#218484)
- Fix error messages in ausearch/aureport

* Wed Dec  6 2006 Jeremy Katz <katzj@redhat.com> - 1.3-4
- rebuild against python 2.5

* Thu Nov 30 2006 Steve Grubb <sgrubb@redhat.com> 1.3-3
- Fix timestamp for libaudit.conf (#218053)

* Thu Nov 30 2006 Steve Grubb <sgrubb@redhat.com> 1.3-2
- Fix minor parsing problem and add new msg types

* Tue Nov 28 2006 Steve Grubb <sgrubb@redhat.com> 1.3-1
- ausearch & aureport implement uid/gid caching
- In ausearch & aureport, extract addr when hostname is unknown
- In ausearch & aureport, test audit log presence O_RDONLY
- New ausearch/aureport time keywords: recent, this-week, this-month, this-year
- Added --add & --delete option to aureport
- Update res parsing in config change events
- Increase the size on audit daemon buffers
- Parse avc_path records in ausearch/aureport
- ausearch has new output mode, raw, for extracting events
- ausearch/aureport can now read stdin
- Rework AVC processing in ausearch/aureport
- Added long options to ausearch and aureport

* Tue Oct 24 2006 Steve Grubb <sgrubb@redhat.com> 1.2.9-1
- In auditd if num_logs is zero, don't rotate on SIGUSR1 (#208834)
- Fix some defines in libaudit.h
- Some auditd config strings were not initialized in aureport (#211443)
- Updated man pages
- Add Netlabel event types to libaudit
- Update aureports to current audit event types
- Update autrace a little
- Deprecated all the old audit_rule functions from public API
- Drop auparse library for the moment

* Fri Sep 29 2006 Steve Grubb <sgrubb@redhat.com> 1.2.8-1
- Add dist tag and bump version (#208532)
- Make internal auditd buffers bigger for context info
- Correct address resolving of hostname in logging functions
- Do not allow multiple msgtypes in same audit rule in auditctl (#207666)
- Only =, != operators for arch & inode fields in auditctl (#206427)
- Updated audit message type table
- Remove watches from aureport since FS_WATCH is deprecated
- Add audit_log_avc back temporarily (#208152)
 
