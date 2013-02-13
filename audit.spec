%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

# Do we want systemd?
%define WITH_SYSTEMD 1

Summary: User space tools for 2.6 kernel auditing
Name: audit
Version: 2.2.2
Release: 5%{?dist}
License: GPLv2+
Group: System Environment/Daemons
URL: http://people.redhat.com/sgrubb/audit/
Source0: http://people.redhat.com/sgrubb/audit/%{name}-%{version}.tar.gz
Patch1: fix-srand.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: swig python-devel
BuildRequires: tcp_wrappers-devel krb5-devel libcap-ng-devel
BuildRequires: kernel-headers >= 2.6.29
Requires: %{name}-libs = %{version}-%{release}
%if %{WITH_SYSTEMD}
BuildRequires: systemd-units
Requires(post): systemd-units systemd-sysv chkconfig coreutils
Requires(preun): systemd-units
Requires(postun): systemd-units coreutils
%else
Requires: chkconfig
%endif

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
Summary: Header files for libaudit
License: LGPLv2+
Group: Development/Libraries
Requires: %{name}-libs = %{version}
Requires: kernel-headers >= 2.6.29

%description libs-devel
The audit-libs-devel package contains the header files needed for
developing applications that need to use the audit framework libraries.

%package libs-static
Summary: Static version of libaudit library
License: LGPLv2+
Group: Development/Libraries
Requires: kernel-headers >= 2.6.29

%description libs-static
The audit-libs-static package contains the static libraries
needed for developing applications that need to use static audit
framework libraries

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
BuildRequires: libprelude-devel >= 0.9.16
Requires: %{name} = %{version}-%{release}
Requires: %{name}-libs = %{version}-%{release}
Requires: openldap

%description -n audispd-plugins
The audispd-plugins package provides plugins for the real-time
interface to the audit system, audispd. These plugins can do things
like relay events to remote machines or analyze events for suspicious
behavior.

%prep
%setup -q
%patch1 -p1

%build
%configure --sbindir=/sbin --libdir=/%{_lib} --with-python=yes --with-prelude --with-libwrap --enable-gssapi-krb5=yes --with-libcap-ng=yes --with-armeb \
%if %{WITH_SYSTEMD}
	--enable-systemd
%endif

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/{sbin,etc/audispd/plugins.d}
%if !%{WITH_SYSTEMD}
mkdir -p $RPM_BUILD_ROOT/{etc/{sysconfig,rc.d/init.d}}
%endif
mkdir -p $RPM_BUILD_ROOT/%{_mandir}/{man5,man8}
mkdir -p $RPM_BUILD_ROOT/%{_lib}
mkdir -p $RPM_BUILD_ROOT/%{_libdir}/audit
mkdir -p $RPM_BUILD_ROOT/%{_var}/log/audit
mkdir -p $RPM_BUILD_ROOT/%{_var}/spool/audit
make DESTDIR=$RPM_BUILD_ROOT install

mkdir -p $RPM_BUILD_ROOT/%{_libdir}
# This winds up in the wrong place when libtool is involved
mv $RPM_BUILD_ROOT/%{_lib}/libaudit.a $RPM_BUILD_ROOT%{_libdir}
mv $RPM_BUILD_ROOT/%{_lib}/libauparse.a $RPM_BUILD_ROOT%{_libdir}
curdir=`pwd`
cd $RPM_BUILD_ROOT/%{_libdir}
LIBNAME=`basename \`ls $RPM_BUILD_ROOT/%{_lib}/libaudit.so.1.*.*\``
ln -s ../../%{_lib}/$LIBNAME libaudit.so
LIBNAME=`basename \`ls $RPM_BUILD_ROOT/%{_lib}/libauparse.so.0.*.*\``
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
rm -f $RPM_BUILD_ROOT/%{_libdir}/python?.?/site-packages/auparse.a
rm -f $RPM_BUILD_ROOT/%{_libdir}/python?.?/site-packages/auparse.la

# On platforms with 32 & 64 bit libs, we need to coordinate the timestamp
touch -r ./audit.spec $RPM_BUILD_ROOT/etc/libaudit.conf
touch -r ./audit.spec $RPM_BUILD_ROOT/usr/share/man/man5/libaudit.conf.5.gz

%ifnarch ppc ppc64
%check
make check
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post libs -p /sbin/ldconfig

%post
%if %{WITH_SYSTEMD}
%systemd_post auditd.service
%else
/sbin/chkconfig --add auditd
%endif

%preun
%if %{WITH_SYSTEMD}
%systemd_preun auditd.service
%else
if [ $1 -eq 0 ]; then
   /sbin/service auditd stop > /dev/null 2>&1
   /sbin/chkconfig --del auditd
fi
%endif

%postun libs -p /sbin/ldconfig

%postun
%if %{WITH_SYSTEMD}
%systemd_postun_with_restart auditd.service
%else
if [ $1 -ge 1 ]; then
   /sbin/service auditd condrestart > /dev/null 2>&1 || :
fi
%endif

%files libs
%defattr(-,root,root,-)
%attr(755,root,root) /%{_lib}/libaudit.so.1*
%attr(755,root,root) /%{_lib}/libauparse.*
%config(noreplace) %attr(640,root,root) /etc/libaudit.conf
%{_mandir}/man5/libaudit.conf.5.gz

%files libs-devel
%defattr(-,root,root,-)
%doc contrib/skeleton.c contrib/plugin
%{_libdir}/libaudit.so
%{_libdir}/libauparse.so
%{_includedir}/libaudit.h
%{_includedir}/auparse.h
%{_includedir}/auparse-defs.h
%{_mandir}/man3/*

%files libs-static
%defattr(-,root,root,-)
%{_libdir}/libaudit.a
%{_libdir}/libauparse.a

%files libs-python
%defattr(-,root,root,-)
%attr(755,root,root) %{python_sitearch}/_audit.so
%attr(755,root,root) %{python_sitearch}/auparse.so
%{python_sitearch}/audit.py*

%files
%defattr(-,root,root,-)
%doc  README COPYING ChangeLog contrib/capp.rules contrib/nispom.rules contrib/lspp.rules contrib/stig.rules init.d/auditd.cron
%attr(644,root,root) %{_mandir}/man8/audispd.8.gz
%attr(644,root,root) %{_mandir}/man8/auditctl.8.gz
%attr(644,root,root) %{_mandir}/man8/auditd.8.gz
%attr(644,root,root) %{_mandir}/man8/aureport.8.gz
%attr(644,root,root) %{_mandir}/man8/ausearch.8.gz
%attr(644,root,root) %{_mandir}/man8/autrace.8.gz
%attr(644,root,root) %{_mandir}/man8/aulast.8.gz
%attr(644,root,root) %{_mandir}/man8/aulastlog.8.gz
%attr(644,root,root) %{_mandir}/man8/auvirt.8.gz
%attr(644,root,root) %{_mandir}/man8/ausyscall.8.gz
%attr(644,root,root) %{_mandir}/man7/audit.rules.7.gz
%attr(644,root,root) %{_mandir}/man5/auditd.conf.5.gz
%attr(644,root,root) %{_mandir}/man5/audispd.conf.5.gz
%attr(644,root,root) %{_mandir}/man5/ausearch-expression.5.gz
%attr(750,root,root) /sbin/auditctl
%attr(750,root,root) /sbin/auditd
%attr(755,root,root) /sbin/ausearch
%attr(755,root,root) /sbin/aureport
%attr(750,root,root) /sbin/autrace
%attr(750,root,root) /sbin/audispd
%attr(755,root,root) %{_bindir}/aulast
%attr(755,root,root) %{_bindir}/aulastlog
%attr(755,root,root) %{_bindir}/ausyscall
%attr(755,root,root) %{_bindir}/auvirt
%if %{WITH_SYSTEMD}
%attr(640,root,root) %{_unitdir}/auditd.service
%else
%attr(755,root,root) /etc/rc.d/init.d/auditd
%config(noreplace) %attr(640,root,root) /etc/sysconfig/auditd
%endif
%attr(750,root,root) %dir %{_var}/log/audit
%attr(750,root,root) %dir /etc/audit
%attr(750,root,root) %dir /etc/audisp
%attr(750,root,root) %dir /etc/audisp/plugins.d
%config(noreplace) %attr(640,root,root) /etc/audit/auditd.conf
%config(noreplace) %attr(640,root,root) /etc/audit/audit.rules
%config(noreplace) %attr(640,root,root) /etc/audisp/audispd.conf
%config(noreplace) %attr(640,root,root) /etc/audisp/plugins.d/af_unix.conf
%config(noreplace) %attr(640,root,root) /etc/audisp/plugins.d/syslog.conf

%files -n audispd-plugins
%defattr(-,root,root,-)
%attr(644,root,root) %{_mandir}/man8/audispd-zos-remote.8.gz
%attr(644,root,root) %{_mandir}/man5/zos-remote.conf.5.gz
%config(noreplace) %attr(640,root,root) /etc/audisp/plugins.d/audispd-zos-remote.conf
%config(noreplace) %attr(640,root,root) /etc/audisp/zos-remote.conf
%attr(750,root,root) /sbin/audispd-zos-remote
%config(noreplace) %attr(640,root,root) /etc/audisp/plugins.d/au-prelude.conf
%config(noreplace) %attr(640,root,root) /etc/audisp/audisp-prelude.conf
%attr(750,root,root) /sbin/audisp-prelude
%attr(644,root,root) %{_mandir}/man5/audisp-prelude.conf.5.gz
%attr(644,root,root) %{_mandir}/man8/audisp-prelude.8.gz
%config(noreplace) %attr(640,root,root) /etc/audisp/audisp-remote.conf
%config(noreplace) %attr(640,root,root) /etc/audisp/plugins.d/au-remote.conf
%attr(750,root,root) /sbin/audisp-remote
%attr(700,root,root) %dir %{_var}/spool/audit
%attr(644,root,root) %{_mandir}/man5/audisp-remote.conf.5.gz
%attr(644,root,root) %{_mandir}/man8/audisp-remote.8.gz

%changelog
* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan 16 2013 Steve Grubb <sgrubb@redhat.com> 2.2.2-4
- Don't make auditd.service file executable (#896113)

* Fri Jan 11 2013 Steve Grubb <sgrubb@redhat.com> 2.2.2-3
- Do not own /usr/lib64/audit

* Wed Dec 12 2012 Steve Grubb <sgrubb@redhat.com> 2.2.2-2
- New upstream release

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Mar 23 2012 Steve Grubb <sgrubb@redhat.com> 2.2.1-1
- New upstream release

* Thu Mar 1 2012 Steve Grubb <sgrubb@redhat.com> 2.2-1
- New upstream release

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Sep 15 2011 Adam Williamson <awilliam@redhat.com> 2.1.3-4
- add in some systemd scriptlets that were missed, including one which
  will cause auditd to be enabled on upgrade from pre-systemd builds

* Wed Sep 14 2011 Steve Grubb <sgrubb@redhat.com> 2.1.3-3
- Enable by default (#737060)

* Tue Aug 30 2011 Steve Grubb <sgrubb@redhat.com> 2.1.3-2
- Correct misplaced %ifnarch (#734359)

* Mon Aug 15 2011 Steve Grubb <sgrubb@redhat.com> 2.1.3-1
- New upstream release

* Thu Jul 26 2011 Jóhann B. Guðmundsson <johannbg@gmail.com> - 2.1.2-2
- Introduce systemd unit file, drop SysV support

* Sat Jun 11 2011 Steve Grubb <sgrubb@redhat.com> 2.1.2-1
- New upstream release

* Wed Apr 20 2011 Steve Grubb <sgrubb@redhat.com> 2.1.1-1
- New upstream release

* Tue Mar 29 2011 Steve Grubb <sgrubb@redhat.com> 2.1-1
- New upstream release

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Feb 04 2011 Steve Grubb <sgrubb@redhat.com> 2.0.6-1
- New upstream release

* Thu Jan 20 2011 Karsten Hopp <karsten@redhat.com> 2.0.5-2
- bump and rebuild as 2.0.5-1 was erroneously linked with python-2.6 on ppc

* Tue Nov 02 2010 Steve Grubb <sgrubb@redhat.com> 2.0.5-1
- New upstream release

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 2.0.4-4
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Tue Feb 16 2010 Adam Jackson <ajax@redhat.com> 2.0.4-3
- audit-2.0.4-add-needed.patch: Fix FTBFS for --no-add-needed

* Fri Jan 29 2010 Steve Grubb <sgrubb@redhat.com> 2.0.4-2
- Split out static libs (#556039)

* Tue Dec 08 2009 Steve Grubb <sgrubb@redhat.com> 2.0.4-1
- New upstream release

* Sat Oct 17 2009 Steve Grubb <sgrubb@redhat.com> 2.0.3-1
- New upstream release

* Fri Oct 16 2009 Steve Grubb <sgrubb@redhat.com> 2.0.2-1
- New upstream release

* Mon Sep 28 2009 Steve Grubb <sgrubb@redhat.com> 2.0.1-1
- New upstream release

* Fri Aug 21 2009 Steve Grubb <sgrubb@redhat.com> 2.0-3
- New upstream release

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.13-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Apr 21 2009 Steve Grubb <sgrubb@redhat.com> 1.7.13-1
- New upstream release
- Fix problem with negative uids in audit rules on 32 bit systems
- Update tty keystroke interpretations (Miloslav Trmač)

* Fri Apr 03 2009 Steve Grubb <sgrubb@redhat.com> 1.7.12-4
- Drop some debug code in libev

* Tue Mar 17 2009 Steve Grubb <sgrubb@redhat.com> 1.7.12-3
- Apply patch from dwalsh moving audit.py file to arch specific python dir

* Thu Feb 25 2009 Steve Grubb <sgrubb@redhat.com> 1.7.12-2
- Handle audit=0 boot option for 2.6.29 kernel (#487541)

* Tue Feb 24 2009 Steve Grubb <sgrubb@redhat.com> 1.7.12-1
- New upstream release

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.7.11-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Jan 13 2009 Steve Grubb <sgrubb@redhat.com> 1.7.11-2
- Add crypto event definitions

* Sat Jan 10 2009 Steve Grubb <sgrubb@redhat.com> 1.7.11-1
- New upstream release

* Wed Dec 17 2008 Steve Grubb <sgrubb@redhat.com> 1.7.10-2
- Fix bz 476798 -  "auditd -n" does not work

* Sat Dec 13 2008 Steve Grubb <sgrubb@redhat.com> 1.7.10-1
- New upstream release

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 1.7.9-1.1
- Rebuild for Python 2.6

* Wed Nov 05 2008 Steve Grubb <sgrubb@redhat.com> 1.7.9-1
- New upstream release

* Tue Oct 28 2008 Steve Grubb <sgrubb@redhat.com> 1.7.8-6
- Update specfile requires to include dist

* Mon Oct 27 2008 Steve Grubb <sgrubb@redhat.com> 1.7.8-5
- Fix ausearch/report recent and now time keyword lookups (#468668)

* Sat Oct 25 2008 Steve Grubb <sgrubb@redhat.com> 1.7.8-4
- If kernel is in immutable mode, auditd should not send enable command

* Fri Oct 24 2008 Steve Grubb <sgrubb@redhat.com> 1.7.8-3
- Fix ausearch interpretting i386 syscalls on x86_64 machine

* Thu Oct 23 2008 Steve Grubb <sgrubb@redhat.com> 1.7.8-2
- Fix segfault when using file input to aureport
- Quieten down messages about missing gssapi support

* Wed Oct 22 2008 Steve Grubb <sgrubb@redhat.com> 1.7.8-1
- Disable GSSAPI support until its reworked as plugin
- Interpret TTY audit data in auparse (Miloslav Trmač)
- Extract terminal from USER_AVC events for ausearch/report (Peng Haitao)
- Add USER_AVCs to aureport's avc reporting (Peng Haitao)
- Short circuit hostname resolution in libaudit if host is empty
- If log_group and user are not root, don't check dispatcher perms
- Fix a bug when executing "ausearch -te today PM"
- Add --exit search option to ausearch
- Fix parsing config file when kerberos is disabled

* Thu Oct 16 2008 Steve Grubb <sgrubb@redhat.com> 1.7.7-2
- Remove selinux policy for zos-remote

* Wed Sep 17 2008 Steve Grubb <sgrubb@redhat.com> 1.7.7-1
- Bug fixes for GSSAPI code in remote logging (DJ Delorie)
- Add watched syscall support to audisp-prelude
- Enable tcp_wrappers support in auditd

* Wed Sep 11 2008 Steve Grubb <sgrubb@redhat.com> 1.7.6-1
- Add subject to audit daemon events (Chu Li)
- Add tcp_wrappers support for auditd
- Updated syscall tables for 2.6.27 kernel
- Audit connect/disconnect of remote clients
- Add GSS/Kerberos encryption to the remote protocol (DJ Delorie)

* Mon Aug 25 2008 Steve Grubb <sgrubb@redhat.com> 1.7.5-1
- Update system-config-audit to 0.4.8
- Whole lot of bug fixes - see ChangeLog for details
- Reimplement auditd main loop using libev
- Add TCP listener to auditd to receive remote events
- Fix scheduler problem (#457061)

* Thu Jul 03 2008 Steve Grubb <sgrubb@redhat.com> 1.7.4-2
- Move ausearch-expression to main package (#453437)

* Mon May 19 2008 Steve Grubb <sgrubb@redhat.com> 1.7.4-1
- Fix interpreting of keys in syscall records
- Don't error on name=(null) PATH records in ausearch/report
- Add key report to aureport
- Update system-config-audit to 0.4.7 (Miloslav Trmac)
- Add support for the filetype field option in auditctl new to 2.6.26 kernels

* Fri May 09 2008 Steve Grubb <sgrubb@redhat.com> 1.7.3-1
- Fix output of keys in ausearch interpretted mode
- Fix ausearch/report --start now to not be reset to midnight
- audispd now has a priority boost config option
- Look for laddr in avcs reported via prelude
- Detect page 0 mmaps and alert via prelude

* Fri Apr 18 2008 Steve Grubb <sgrubb@redhat.com> 1.7.2-6
- Fix overflow in audit_log_user_command, better (#438840)
- ausearch was not matching path in avc records
- audisp-prelude attempt to reposition index after examining each type
- correct building of mls policy
- Fix auparse iterating in auparse_find_field and next_field
- Don't alert on USER_AVC's - they are not quite right

* Tue Apr 08 2008 Steve Grubb <sgrubb@redhat.com> 1.7.1-1
- Fix buffer overflow in audit_log_user_command, again (#438840)
- Fix memory leak in EOE code in auditd (#440075)
- In auditctl, don't use new operators in legacy rule format
- Made a couple corrections in alpha & x86_64 syscall tables (Miloslav Trmac)

* Fri Apr 04 2008 Steve Grubb <sgrubb@redhat.com> 1.7-3
- Fix memleak in auditd eoe code

* Tue Apr 01 2008 Steve Grubb <sgrubb@redhat.com> 1.7-2
- Remove LSB headers from init scripts
- Fix buffer overflow in audit_log_user_command again

* Sun Mar 30 2008 Steve Grubb <sgrubb@redhat.com> 1.7-1
- Handle user space avcs in prelude plugin
- Fix watched account login detection for some failed login attempts
- Couple fixups in audit logging functions (Miloslav Trmac)
- Add support in auditctl for virtual keys
- auparse_find_field_next was not iterating correctly, fixed it
- Add idmef alerts for access or execution of watched file
- Fix buffer overflow in audit_log_user_command
- Add basic remote logging plugin - only sends & no flow control
- Update ausearch with interpret fixes from auparse
