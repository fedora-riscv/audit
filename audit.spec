Summary: User space tools for 2.6 kernel auditing.
Name: audit
Version: 0.9.20
Release: 1
License: GPL
Group: System Environment/Daemons
URL: http://people.redhat.com/sgrubb/audit/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: libtool
BuildRequires: glibc-kernheaders >= 2.4-9.1.95
BuildRequires: automake >= 1.9
BuildRequires: autoconf >= 2.59
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
Requires: glibc-kernheaders >= 2.4-9.1.95

%description libs-devel
The audit-libs-devel package contains the static libraries and header 
files needed for developing applications that need to use the audit 
framework libraries.

%prep
%setup -q

%build
autoreconf -fv --install
export CFLAGS="$RPM_OPT_FLAGS"
./configure --sbindir=/sbin --mandir=%{_mandir} --libdir=/%{_lib}
make

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/{sbin,etc/{sysconfig,rc.d/init.d}}
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/man8
mkdir -p $RPM_BUILD_ROOT/%{_lib}
mkdir -p $RPM_BUILD_ROOT/%{_var}/log/audit
make DESTDIR=$RPM_BUILD_ROOT install

mkdir -p $RPM_BUILD_ROOT/%{_includedir}
mkdir -p $RPM_BUILD_ROOT/%{_libdir}
# We manually install this since Makefile doesn't
install -m 0644 lib/libaudit.h $RPM_BUILD_ROOT/%{_includedir}
# This winds up in the wrong place when libtool is involved
mv $RPM_BUILD_ROOT/%{_lib}/libaudit.a $RPM_BUILD_ROOT%{_libdir}
curdir=`pwd`
cd $RPM_BUILD_ROOT/%{_libdir}
LIBNAME=`basename \`ls $RPM_BUILD_ROOT/%{_lib}/libaudit.so.*.*.*\``
ln -s ../../%{_lib}/$LIBNAME libaudit.so
cd $curdir
# Remove these items so they don't get picked up.
rm -f $RPM_BUILD_ROOT/%{_lib}/libaudit.so
rm -f $RPM_BUILD_ROOT/%{_lib}/libaudit.la

%clean
rm -rf $RPM_BUILD_ROOT

%post libs -p /sbin/ldconfig

%post
/sbin/chkconfig --add auditd

%preun
if [ $1 -eq 0 ]; then
   /sbin/service auditd stop > /dev/null 2>&1
   /sbin/chkconfig --del auditd
fi

%postun libs
/sbin/ldconfig 2>/dev/null

%postun
if [ $1 -ge 1 ]; then
   /sbin/service auditd condrestart > /dev/null 2>&1
fi

%files libs
%defattr(-,root,root)
%attr(755,root,root) /%{_lib}/libaudit.*

%files libs-devel
%defattr(-,root,root)
%{_libdir}/libaudit.a
%{_libdir}/libaudit.so
%{_includedir}/libaudit.h
%{_mandir}/man3/*

%files
%defattr(-,root,root,-)
%doc README COPYING ChangeLog sample.rules contrib/capp.rules
%attr(0644,root,root) %{_mandir}/man8/*
%attr(750,root,root)  /sbin/auditctl
%attr(750,root,root)  /sbin/auditd
%attr(750,root,root) /sbin/ausearch
%attr(750,root,root) /sbin/autrace
%attr(755,root,root) /etc/rc.d/init.d/auditd
%attr(750,root,root) %{_var}/log/audit
%config(noreplace) %attr(640,root,root) /etc/auditd.conf
%config(noreplace) %attr(640,root,root) /etc/audit.rules
%config(noreplace) %attr(640,root,root) /etc/sysconfig/auditd


%changelog
* Thu Jul 29 2005 Steve Grubb <sgrubb@redhat.com> 0.9.20-1
- Fix ausearch to handle no audit log better
- Fix auditctl blank line handling
- Trim trailing '/' from file system watches in auditctl
- Catch cases where parameter was passed without option being given to auditctl
- Add CAPP sample configuration

* Thu Jul 14 2005 Steve Grubb <sgrubb@redhat.com> 0.9.19-1
- ausearch remove debug code

* Thu Jul 14 2005 Steve Grubb <sgrubb@redhat.com> 0.9.18-1
- auditd message formatter use MAX_AUDIT_MESSAGE_LENGTH to prevent clipping

* Tue Jul 12 2005 Steve Grubb <sgrubb@redhat.com> 0.9.17-1
- Fix ausearch buffers to hold long filenames
- Make a0 long long for 64 bit kernels & 32 bit ausearch.

* Thu Jul 07 2005 Steve Grubb <sgrubb@redhat.com> 0.9.16-1
- Adjust umask
- Adjust length of strings for file system watches to not include NUL
- Remove extra error message from audit_send

* Tue Jun 27 2005 Steve Grubb <sgrubb@redhat.com> 0.9.15-1
- Update log rotation handling to be more robust

* Fri Jun 24 2005 Steve Grubb <sgrubb@redhat.com> 0.9.14-1
- make auditctl -s work again
- make AUDITD_CLEAN_STOP test in init scripts case insensitive

* Thu Jun 23 2005 Steve Grubb <sgrubb@redhat.com> 0.9.13-1
- Remove /lib/libaudit.so & .la from audit-libs package
- In auditctl, if syscall not given, default to all

* Wed Jun 22 2005 Steve Grubb <sgrubb@redhat.com> 0.9.12-1
- Add some syslog messages for a couple exits
- Add some unlinks of the pid file in a couple error exits
- Make some options of auditctl not expect a reply
- Update support for user and watch filter lists

* Tue Jun 21 2005 Steve Grubb <sgrubb@redhat.com> 0.9.11-1
- Change packet draining to nonblocking
- Interpret id field in ausearch
- Add error message if not able to create log
- Ignore netlink acks when asking for rule & watch list

* Mon Jun 20 2005 Steve Grubb <sgrubb@redhat.com> 0.9.10-1
- Make sure the bad packet is drained when retrying user messages
- Add support for new user and watch filter lists
- Interpret flags field in ausearch

* Sun Jun 19 2005 Steve Grubb <sgrubb@redhat.com> 0.9.9-1
- Fix user messages for people with older kernels

* Fri Jun 17 2005 Steve Grubb <sgrubb@redhat.com> 0.9.8-1
- Added support for FS_INODE and USYS_CONFIG records
- More cleanup of user space message functions

* Thu Jun 16 2005 Steve Grubb <sgrubb@redhat.com> 0.9.7-1
- fixed bug in send_user_message which errored on pam logins
- Change nanosleeps over to select loops
- Change the 'e' option to auditctl -p to 'x'

* Thu Jun 16 2005 Steve Grubb <sgrubb@redhat.com> 0.9.6-1
- fix bug in incremental flush where is wrongly reported an error
- ausearch should not do uid check for -if option
- adjust ipc interpretation to not use ipc.h

* Tue Jun 14 2005 Steve Grubb <sgrubb@redhat.com> 0.9.5-1
- interpret socketcall & ipc based on a0 in ausearch
- change call sequence to make user space messages faster
- update return val for auditctl

* Sat Jun 11 2005 Steve Grubb <sgrubb@redhat.com> 0.9.4-1
- Rule and watch insert no longer automatically dumps list
- auditctl rules can now use auid instead of loginuid
- Add sighup support for daemon reconfiguration
- Move some functions into private.h

* Thu Jun 9 2005 Steve Grubb <sgrubb@redhat.com> 0.9.3-1
- Change filename handling to use linked list in ausearch
- Add man pages for audit_setloginuid & audit_getloginuid
- Fix problem where you couldn't set rule on unset loginuid's
- Adjust memory management for sighup needs
- Fix problem where netlink timeout counter wasn't being reset

* Thu Jun 2 2005 Steve Grubb <sgrubb@redhat.com> 0.9.2-1
- Step up to new glibc-kernheaders

* Thu Jun 2 2005 Steve Grubb <sgrubb@redhat.com> 0.9.1-1
- AUDITD_CLEAN_STOP config option in /etc/sysconfig/auditd
- When unknown, show raw record in ausearch.
- Add CWD message type support

* Wed May 25 2005 Steve Grubb <sgrubb@redhat.com> 0.9-1
- Translate numeric info to human readable for ausearch output
- add '-if' option to ausearch to select input file
- add '-c' option to ausearch to allow searching by comm field
- init script now deletes all rules when daemon stops
- Make auditctl display perms correctly in watch listings
- Make auditctl -D remove all watches

* Thu May 20 2005 Steve Grubb <sgrubb@redhat.com> 0.8.2-1
- Update documentation
- Handle user space audit events in more uniform way
- Update all parsers for more robustness with new kernel changes
- Create quiet mode for error messages
- Make rotated logs readonly

* Tue May 17 2005 Steve Grubb <sgrubb@redhat.com> 0.8.1-1
- Fix code to "or" uid  & gid checks for ausearch -ua & -ga
- Change msg() to audit_msg() to avoid conflicts
- Parse socket messages for hostname in ausearch

* Thu May 12 2005 Steve Grubb <sgrubb@redhat.com> 0.8-1
- ausearch fix bugs related to -f & -x
- Parse messages using new types
- Properly unescape filenames
- Update interface for sending userspace messages to use more types

* Sun May 08 2005 Steve Grubb <sgrubb@redhat.com> 0.7.4-1
- Make sure ausearch ts & te obey DST.
- Code cleanups to make file system watches work correctly

* Tue May 03 2005 Steve Grubb <sgrubb@redhat.com> 0.7.3-1
- Add code to get watch list to auditctl
- Get -f & -hn working in ausearch
- Added search by terminal, exe, and syscall to ausearch program
- Added -w parameter to match whole word in ausearch

* Wed Apr 27 2005 Steve Grubb <sgrubb@redhat.com> 0.7.2-1
- Allow ausearch uid & gid to be non-numeric (root, wheel, etc)
- Fix problems with changing run level
- Added new code for logging shutdown reason credentials
- Update DAEMON messages to use better timestamp

* Sun Apr 24 2005 Steve Grubb <sgrubb@redhat.com> 0.7.1-1
- Make sure time calc is done using localtime
- Raise rlimits for file size & cpu usage
- Added new disk_error_action config item to auditd.conf
- Rework memory management of event buffer
- Handled all errors in event logging thread

* Sat Apr 23 2005 Steve Grubb <sgrubb@redhat.com> 0.7-1
- In auditctl -l, loop until all rules are printed
- Update autrace not to run if rules are currently loaded
- Added code to switch to single user mode when disk is full
- Added the ausearch program

* Wed Apr 20 2005 Steve Grubb <sgrubb@redhat.com> 0.6.12-1
- Fixed bug where elf type wasn't being set when given numerically
- Added autrace program (similar to strace)
- Fixed bug when logs = 2 and ROTATE is the action, only 1 log resulted

* Mon Apr 18 2005 Steve Grubb <sgrubb@redhat.com> 0.6.11-1
- Check log file size on start up
- Added priority_boost config item
- Reworked arch support
- Reworked how run level is changed
- Make allowances for ECONNREFUSED

* Fri Apr  1 2005 Steve Grubb <sgrubb@redhat.com> 0.6.10-1
- Code cleanups
- Support the arch field for auditctl
- Add version to auditctl
- Documentation updates
- Moved default location of the audit log to /var/log/audit

* Thu Mar 17 2005 Steve Grubb <sgrubb@redhat.com> 0.6.9-1
- Added patch for filesystem watch
- Added version information to audit start message
- Change netlink code to use ack in order to get error notification

* Wed Mar 10 2005 Steve Grubb <sgrubb@redhat.com> 0.6.8-1
- removed the pam_loginuid library - its going to pam

* Wed Mar 9 2005 Steve Grubb <sgrubb@redhat.com> 0.6.7-1
- Fixed bug setting loginuid
- Added num_logs to configure number of logs when rotating
- Added code for rotating logs

* Tue Mar 8 2005 Steve Grubb <sgrubb@redhat.com> 0.6.6-1
- Fix audit_set_pid to try to read a reply, but its non-fatal if no reply.
- Remove the read status during init
- Change to using pthreads sync mechanism for stopping system
- Worker thread should ignore all signals
- Change main loop to use select for inbound event handling
- Gave pam_loginuid a "failok" option for testing

* Thu Mar 3 2005 Steve Grubb <sgrubb@redhat.com> 0.6.5-1
- Lots of code cleanups
- Added write_pid function to auditd
- Added audit_log to libaudit
- Don't check file length in foreground mode of auditd
- Added *if_enabled functions to send messages only if audit system is enabled
- If syscall name is unknown when printing rules, use the syscall number
- Rework the build system to produce singly threaded public libraries
- Create a multithreaded version of libaudit for the audit daemon's use

* Wed Feb 23 2005 Steve Grubb <sgrubb@redhat.com> 0.6.4-1
- Rename pam_audit to pam_loginuid to reflect what it does
- Fix bug in detecting space left on partition
- Fix bug in handling of suspended logging

* Wed Feb 23 2005 David Woodhouse <dwmw2@redhat.com> 0.6.3-3
- Include stdint.h in libaudit.h and require new glibc-kernheaders

* Sun Feb 20 2005 Steve Grubb <sgrubb@redhat.com> 0.6.3-2
- Another lib64 correction

* Sun Feb 20 2005 Steve Grubb <sgrubb@redhat.com> 0.6.3-1
- Change pam install from /lib/security to /%{_lib}/security
- Change pam_audit to write loginuid to /proc/pid/loginuid
- Add pam_session_close handle
- Update to newest kernel headers

* Fri Feb 11 2005 Steve Grubb <sgrubb@redhat.com> 0.6.2-1
- New version
- Add R option to auditctl to allow reading rules from file.
- Do not allow task creation list to have syscall auditing
- Add D option to allow deleting all rules with 1 command
- Added pam_audit man page & sample.rules
- Mod initscript to call auditctl to load rules at start-up
- Write message to log file for daemon start up
- Write message that daemon is shutting down
- Modify auditd shutdown to wait until logger thread is finished
- Add sample rule file to docs

* Sat Jan 08 2005 Steve Grubb <sgrubb@redhat.com> 0.6.1-1
- New version: rework auditctl and its man pages.
- Added admin_space_left config option as last chance before
  running out of disk space.

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

