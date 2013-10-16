%define major	3
%define libname	%mklibname %{name} %{major}
%define	devname	%mklibname -d %{name}

%bcond_without	systemd

Name:		bluez
Summary:	Official Linux Bluetooth protocol stack
Version:	4.101
Release:	8
License:	GPLv2+
Group:		Communications
URL:		http://www.bluez.org/
Source0:	http://www.kernel.org/pub/linux/bluetooth/%{name}-%{version}.tar.xz
Source6:	pand.conf
Source7:	dund.conf
Source8:	hidd.conf
Source9:	rfcomm.conf
Source10:	bluez-uinput.modules

# http://thread.gmane.org/gmane.linux.bluez.kernel/8645
Patch0:		0002-systemd-unitdir-enable.patch
Patch1:		bluez-4.101-automake-1.13.patch
Patch4:		bluez-socket-mobile-cf-connection-kit.patch
# http://thread.gmane.org/gmane.linux.bluez.kernel/2396
Patch5:		0001-Add-sixaxis-cable-pairing-plugin.patch
# PS3 BD Remote patches
Patch6:		0001-input-Add-helper-function-to-request-disconnect.patch
Patch7:		0002-fakehid-Disconnect-from-PS3-remote-after-10-mins.patch
Patch8:		0003-fakehid-Use-the-same-constant-as-declared.patch
Patch9:		bluez-4.101-fix-c++11-compatibility.patch

BuildRequires:	flex
BuildRequires:	bison
BuildRequires:	systemd
BuildRequires:	readline-devel
BuildRequires:	expat-devel
BuildRequires:	pkgconfig(alsa)
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(gstreamer-plugins-base-0.10)
BuildRequires:	pkgconfig(gstreamer-0.10)
BuildRequires:	pkgconfig(libcap-ng)
BuildRequires:	pkgconfig(libusb)
BuildRequires:	pkgconfig(libusb-1.0)
BuildRequires:	pkgconfig(udev) >= 186

Requires:	bluez-pin
Suggests:	obex-data-server
Suggests:	bluez-firmware

%description
These are the official Bluetooth communication libraries for Linux.

%post
update-alternatives --install /bin/bluepin bluepin /usr/bin/bluepin 5
#migrate old configuration
if [ "$1" = "2" -a -d %{_var}/lib/lib/bluetooth ]; then
 mv -f %{_var}/lib/lib/bluetooth/* %{_var}/lib/bluetooth/ > /dev/null 2>&1 || exit 0
 rmdir %{_var}/lib/lib/bluetooth/ > /dev/null 2>&1 || exit 0
 rmdir %{_var}/lib/lib/ > /dev/null 2>&1 || exit 0
fi

if [ $1 -eq 1 ]; then
	/bin/systemctl enable bluetooth.service >/dev/null 2>&1 || :
fi

%postun
if [ "$1" = "0" ]; then
  update-alternatives --remove bluepin /usr/bin/bluepin
fi

/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
	/bin/systemctl try-restart bluetooth.service >/dev/null 2>&1 || :
fi

%triggerun -- bluez < 4.94-4
/bin/systemctl --no-reload enable bluetooth.service >/dev/null 2>&1 || :

%files
%{_bindir}/ciptool
%{_bindir}/dfutool
%{_bindir}/gatttool
%{_bindir}/hcitool
%{_bindir}/hidd
%{_bindir}/l2ping
%{_bindir}/rfcomm
%{_bindir}/sdptool
### compat
%{_bindir}/dund
%{_bindir}/pand
### 
%{_sbindir}/bccmd
%{_sbindir}/hciattach
%{_sbindir}/hciconfig
%{_sbindir}/bluetoothd
/bin/hidd
/sbin/bluetoothd
%if %{with systemd}
%{_unitdir}/*.service
%endif
%{_mandir}/man?/*
%config(noreplace) %{_sysconfdir}/sysconfig/*
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/*.conf
%config(noreplace) %{_sysconfdir}/bluetooth
%{_datadir}/dbus-1/system-services/org.bluez.service
/lib/udev/bluetooth_serial
/lib/udev/hid2hci
%{_sysconfdir}/udev/rules.d/97-bluetooth-serial.rules
%{_sysconfdir}/udev/rules.d/97-bluetooth-hid2hci.rules
%{_localstatedir}/lib/bluetooth

#--------------------------------------------------------------------

%package	cups
Summary:	CUPS printer backend for Bluetooth printers
Group:		System/Servers
Requires:	cups

%description	cups
This package contains the CUPS backend for Bluetooth printers.

%files		cups
%{_prefix}/lib/cups/backend/bluetooth

#--------------------------------------------------------------------

%package	gstreamer
Summary:	Gstreamer support for SBC audio format
Group:		Sound

%description	gstreamer
This package contains gstreamer plugins for the Bluetooth SBC audio format

%files		gstreamer
%{_libdir}/gstreamer-*/*.so

#--------------------------------------------------------------------

%package	alsa
Summary:	ALSA support for Bluetooth audio devices
Group:		Sound

%description	alsa
This package contains ALSA support for Bluetooth audio devices

%files		alsa
%{_libdir}/alsa-lib/*.so
%{_datadir}/alsa/bluetooth.conf

#--------------------------------------------------------------------

%package -n	%{libname}
Summary:	Official Linux Bluetooth protocol stack
Group:		System/Libraries

%description -n	%{libname}
These are the official Bluetooth communication libraries for Linux.

%files -n %{libname}
/%{_lib}/lib*.so.%{major}*

#--------------------------------------------------------------------

%package	test
Summary:	Tools for testing of various Bluetooth-functions
Group:		System/Servers
Requires:	python-dbus
Requires:	python-gobject

%description	test
Contains a few tools for testing various bluetooth functions. The
BLUETOOTH trademarks are owned by Bluetooth SIG, Inc., U.S.A.

%files		test
%{_bindir}/simple-agent
%{_bindir}/test-*

#--------------------------------------------------------------------

%package -n	%{devname}
Summary:	Headers for developing programs that will use %{name}
Group:		Development/C++
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{devname}
This package contains the headers that programmers will need to develop
applications which will use libraries from %{name}.

%files -n	%{devname}
%doc AUTHORS ChangeLog README
%dir %{_includedir}/bluetooth
%{_includedir}/bluetooth/*.h
/%{_lib}/*.so
%{_libdir}/pkgconfig/bluez.pc

#--------------------------------------------------------------------

%prep
%setup -q
%apply_patches

libtoolize -f -c
autoreconf -fi

%build
%configure2_5x	\
	--libdir=/%{_lib} \
%if !%{with systemd}
	--without-systemdsystemunitdir \
%endif
	--enable-cups \
	--enable-dfutool \
	--enable-audio \
	--enable-health \
	--disable-hal \
	--enable-pnat \
	--enable-wiimote \
	--enable-tools \
	--enable-bccmd \
	--enable-gstreamer \
	--enable-hidd \
	--enable-pand \
	--enable-dund \
	--enable-hid2hci \
	--enable-pcmcia \
	--with-systemdsystemunitdir=/lib/systemd/system

%make

%install
%makeinstall_std rulesdir=%{_sysconfdir}/udev/rules.d udevdir=/lib/udev

mkdir -p %{buildroot}%{_libdir}
mv %{buildroot}/%{_lib}/gstreamer-0.10 %{buildroot}%{_libdir}

cat << EOF > %{buildroot}%{_sysconfdir}/bluetooth/pin
1234
EOF

chmod 600 %{buildroot}%{_sysconfdir}/bluetooth/pin

rm -f %{buildroot}%{_sysconfdir}/default/bluetooth %{buildroot}%{_sysconfdir}/init.d/bluetooth
install -m644 %{SOURCE6} -D %{buildroot}%{_sysconfdir}/sysconfig/pand
install -m644 %{SOURCE7} -D %{buildroot}%{_sysconfdir}/sysconfig/dund
install -m644 %{SOURCE8} -D %{buildroot}%{_sysconfdir}/sysconfig/hidd
install -m644 %{SOURCE9} -D %{buildroot}%{_sysconfdir}/sysconfig/rfcomm

rm -rf %{buildroot}/%{_lib}/pkgconfig
install -m644 bluez.pc -D  %{buildroot}%{_libdir}/pkgconfig/bluez.pc

# Remove the cups backend from libdir, and install it in /usr/lib whatever the install
if test -d %{buildroot}/%{_lib}/cups ; then
	install -D -m0755 %{buildroot}/%{_lib}/cups/backend/bluetooth %{buildroot}%{_prefix}/lib/cups/backend/bluetooth
	rm -rf %{buildroot}/%{_lib}/cups
fi 
	
cp test/test-* %{buildroot}%{_bindir}
cp test/simple-agent %{buildroot}%{_bindir}/simple-agent
rm -f %{buildroot}%{_bindir}/test-*.c

mkdir -p %{buildroot}/{bin,sbin}
mv %{buildroot}%{_bindir}/hidd %{buildroot}/bin
mv %{buildroot}%{_sbindir}/bluetoothd %{buildroot}/sbin
# sym link just to be safe
pushd %{buildroot}
ln -s /bin/hidd %{buildroot}%{_bindir}/hidd
ln -s /sbin/bluetoothd %{buildroot}%{_sbindir}/bluetoothd
popd

#install more config files
install -m0644 audio/audio.conf %{buildroot}%{_sysconfdir}/bluetooth/
install -m0644 network/network.conf %{buildroot}%{_sysconfdir}/bluetooth/
install -m0644 input/input.conf %{buildroot}%{_sysconfdir}/bluetooth/
install -m0644 serial/serial.conf %{buildroot}%{_sysconfdir}/bluetooth/

mkdir -p %{buildroot}%{_libdir}/alsa-lib/
mv %{buildroot}/%{_lib}/alsa-lib/*.so %{buildroot}%{_libdir}/alsa-lib/

install -d -m0755 %{buildroot}%{_localstatedir}/lib/bluetooth

ln -s bluetooth.service %{buildroot}%{_unitdir}/dbus-org.bluez.service


%changelog
* Sun Jul 08 2012 Bernhard Rosenkraenzer <bero@bero.eu> 4.101-4
+ Revision: 808508
- Rebuild for libudev.so.1

* Fri Jun 29 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 4.101-3
+ Revision: 807491
- fix buildrequires
- get rid of /usr/bin/test-textfile.c that got packaged
- add url
- package gatttool
- move libtoolize & autoreconf to %%prep
- cleanups
- fix compatibility with ISO C++11 (P9)

* Tue Jun 26 2012 Alexander Khrukin <akhrukin@mandriva.org> 4.101-2
+ Revision: 807024
- rel up

* Tue Jun 26 2012 Alexander Khrukin <akhrukin@mandriva.org> 4.101-1
+ Revision: 806985
- removed unneeded file
- BR usb1-devel
- version update 4.10118

* Fri May 11 2012 Matthew Dawkins <mattydaw@mandriva.org> 4.99-2
+ Revision: 798165
- rebuild
- split out test package
- cleaned up spec
- made obex-data-server a suggests

  + Per Øyvind Karlsen <peroyvind@mandriva.org>
    - move hidd to /bin rather than /sbin
    - don't copy files within package to /sbin, move them in stead
    - drop dead --enable-udevrules option

* Fri Mar 09 2012 Götz Waschk <waschk@mandriva.org> 4.99-1
+ Revision: 783683
- new version
- rediff patch 5

* Fri Feb 24 2012 Bernhard Rosenkraenzer <bero@bero.eu> 4.98-1
+ Revision: 780214
- 4.98
- Remove RPM_SOURCE_DIR usage
- Fix dbus systemd startup
- Adapt sixaxis patch to 4.98

* Tue Oct 04 2011 Александр Казанцев <kazancas@mandriva.org> 4.96-1
+ Revision: 702844
- new version 4.96
- enable bluetoothd by default
- drop systemd patch rather upstream impliment
- add patches from Fedora
- remove obsoletes dating back to october 2008
- remove old obsoletes ( likely no longer needed )
- drop hal buildrequires. No longer needed
- br systemd, readline

  + Matthew Dawkins <mattydaw@mandriva.org>
    - removed unnecessary hal-devel BR

* Wed Jun 29 2011 Michael Scherer <misc@mandriva.org> 4.93-2
+ Revision: 688284
- fix requires

* Mon May 16 2011 Funda Wang <fwang@mandriva.org> 4.93-1
+ Revision: 675047
- rediff systemd patch
- update to new version 4.93

* Tue Apr 26 2011 Funda Wang <fwang@mandriva.org> 4.92-1
+ Revision: 659081
- update to new version 4.92

* Sun Feb 27 2011 Funda Wang <fwang@mandriva.org> 4.88-2
+ Revision: 640205
- rebuild to obsolete old packages

* Sun Feb 20 2011 Andrey Borzenkov <arvidjaar@mandriva.org> 4.88-1
+ Revision: 638875
- new version (mdv#62516)

* Sun Jan 30 2011 Andrey Borzenkov <arvidjaar@mandriva.org> 4.79-2
+ Revision: 634124
- enable systemd support
- update P100: skip rules if systemd is active
- update P101: let bluetooth.target pull bluetooth.service by default
- do not install bluetooth.conf as org.bluez.service
- P101: systemd support

* Tue Nov 23 2010 Eugeni Dodonov <eugeni@mandriva.com> 4.79-1mdv2011.0
+ Revision: 600266
- Updated to 4.79.

* Fri Sep 24 2010 Funda Wang <fwang@mandriva.org> 4.72-1mdv2011.0
+ Revision: 580826
- new version 4.72

* Thu Sep 23 2010 Funda Wang <fwang@mandriva.org> 4.71-1mdv2011.0
+ Revision: 580748
- new version 4.71

* Sun Jul 18 2010 Emmanuel Andry <eandry@mandriva.org> 4.69-1mdv2011.0
+ Revision: 554841
- New version 4.69

* Sun Jul 11 2010 Emmanuel Andry <eandry@mandriva.org> 4.67-1mdv2011.0
+ Revision: 550676
- New version 4.67

* Thu Apr 29 2010 Emmanuel Andry <eandry@mandriva.org> 4.64-1mdv2010.1
+ Revision: 540970
- New version 4.64

* Fri Mar 26 2010 Emmanuel Andry <eandry@mandriva.org> 4.63-1mdv2010.1
+ Revision: 527760
- New version 4.63

* Wed Mar 10 2010 Emmanuel Andry <eandry@mandriva.org> 4.62-1mdv2010.1
+ Revision: 517486
- New version 4.62

* Fri Feb 19 2010 Emmanuel Andry <eandry@mandriva.org> 4.61-2mdv2010.1
+ Revision: 508471
- BR libcap-ng-devel
- enable capng
- don't package cups backend build wrapper, but the binary (#51320)

* Sat Feb 13 2010 Emmanuel Andry <eandry@mandriva.org> 4.61-1mdv2010.1
+ Revision: 505525
- New version 4.61

* Tue Jan 12 2010 Emmanuel Andry <eandry@mandriva.org> 4.60-1mdv2010.1
+ Revision: 490296
- New version 4.60

* Sat Dec 26 2009 Emmanuel Andry <eandry@mandriva.org> 4.59-1mdv2010.1
+ Revision: 482487
- New version 4.59

* Thu Nov 12 2009 Frederik Himpe <fhimpe@mandriva.org> 4.57-1mdv2010.1
+ Revision: 465516
- update to new version 4.57

* Sat Nov 07 2009 Frederik Himpe <fhimpe@mandriva.org> 4.56-1mdv2010.1
+ Revision: 462594
- update to new version 4.56

  + Andrey Borzenkov <arvidjaar@mandriva.org>
    - no reason to install udev rules manually when Makefile does it
    - enable hid2hci
    - buildrequires udev-devel (for pkg-config)

* Fri Sep 25 2009 Frederik Himpe <fhimpe@mandriva.org> 4.54-1mdv2010.0
+ Revision: 449221
- update to new version 4.54

* Tue Sep 22 2009 Andrey Borzenkov <arvidjaar@mandriva.org> 4.53-3mdv2010.0
+ Revision: 447391
- do not install source11 as well - not needed now when source10 was removed
- fix udev rules install - all of them were copied from the same source file

* Sun Sep 20 2009 Andrey Borzenkov <arvidjaar@mandriva.org> 4.53-2mdv2010.0
+ Revision: 445609
- patch100: add {fail_event_on_error} to bluetoothd udev rule to make sure
  it is retried later
- disable source10 (udev_bluetooth_helper). There are no bluetooth services
  anymore; they are started from within udev rules

* Fri Sep 11 2009 Emmanuel Andry <eandry@mandriva.org> 4.53-1mdv2010.0
+ Revision: 438326
- New version 4.53

* Mon Sep 07 2009 Emmanuel Andry <eandry@mandriva.org> 4.52-1mdv2010.0
+ Revision: 432540
- New version 4.52

* Wed Aug 26 2009 Emmanuel Andry <eandry@mandriva.org> 4.50-1mdv2010.0
+ Revision: 421561
- New version 4.50
- drop P3 (not needed)

* Thu Aug 20 2009 Emmanuel Andry <eandry@mandriva.org> 4.48-2mdv2010.0
+ Revision: 418506
- Remove hid2hci calls, they're in udev now

* Wed Aug 19 2009 Emmanuel Andry <eandry@mandriva.org> 4.48-1mdv2010.0
+ Revision: 418001
- update files list

* Sun Aug 02 2009 Emmanuel Andry <eandry@mandriva.org> 4.47-1mdv2010.0
+ Revision: 407555
- New version 4.47

* Tue Jul 28 2009 Emmanuel Andry <eandry@mandriva.org> 4.46-3mdv2010.0
+ Revision: 402829
- fix init uninstallation

* Sun Jul 26 2009 Emmanuel Andry <eandry@mandriva.org> 4.46-2mdv2010.0
+ Revision: 400341
- remove init from previous version

* Sat Jul 25 2009 Emmanuel Andry <eandry@mandriva.org> 4.46-1mdv2010.0
+ Revision: 399809
- New version 4.46
- don't package initscripts, daemon is now handled with udev
- update files list

* Wed May 13 2009 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.39-2mdv2010.0
+ Revision: 375382
- Install alsa libs at the good place

* Wed May 13 2009 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.39-1mdv2010.0
+ Revision: 375351
- Update to version 4.39

* Wed Apr 22 2009 Frederic Crozat <fcrozat@mandriva.com> 4.33-3mdv2009.1
+ Revision: 368734
- Fix incorrect provides / requires which could prevent installation of main package

* Sun Apr 05 2009 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.33-2mdv2009.1
+ Revision: 364106
- Fix dbus file

  + Thierry Vignaud <tv@mandriva.org>
    - do not make udev rules executable, there's no reason for doing so

* Tue Mar 17 2009 Emmanuel Andry <eandry@mandriva.org> 4.33-1mdv2009.1
+ Revision: 356929
- New version 4.33

* Tue Mar 03 2009 Emmanuel Andry <eandry@mandriva.org> 4.32-1mdv2009.1
+ Revision: 347744
- New version 4.32

* Fri Feb 27 2009 Emmanuel Andry <eandry@mandriva.org> 4.31-1mdv2009.1
+ Revision: 345705
- New version 4.31

* Wed Feb 18 2009 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.30-4mdv2009.1
+ Revision: 342549
- Bump release
- remove my debugs :/

* Wed Feb 18 2009 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.30-3mdv2009.1
+ Revision: 342533
- Fix communication of bluez/dbus
- package simple-agent ( discussed on bluez irc channel )

* Mon Feb 16 2009 Frederic Crozat <fcrozat@mandriva.com> 4.30-2mdv2009.1
+ Revision: 340927
- Fix gstreamer plugin install when bootstrapping package
- Fix installation path for gstreamer plugin

* Fri Feb 13 2009 Guillaume Bedot <littletux@mandriva.org> 4.30-1mdv2009.1
+ Revision: 340046
- New version 4.30
- fix mixed-use-of-spaces-and-tabs

* Wed Feb 11 2009 Emmanuel Andry <eandry@mandriva.org> 4.29-1mdv2009.1
+ Revision: 339582
- New version 4.29

  + Nicolas Lécureuil <nlecureuil@mandriva.com>
    - Add more config files

* Wed Feb 04 2009 Guillaume Rousse <guillomovitch@mandriva.org> 4.28-2mdv2009.1
+ Revision: 337217
- fix build with new libtool
- keep bash completion in its own package

  + Nicolas Lécureuil <nlecureuil@mandriva.com>
    - New version 4.28

* Mon Jan 19 2009 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.27-1mdv2009.1
+ Revision: 331191
- update to new version 4.27

* Wed Jan 07 2009 Emmanuel Andry <eandry@mandriva.org> 4.25-1mdv2009.1
+ Revision: 326910
- New version 4.25

* Thu Dec 11 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.22-2mdv2009.1
+ Revision: 312872
- Rebuild for missing package

* Wed Dec 10 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.22-1mdv2009.1
+ Revision: 312464
- update to new version 4.22

* Mon Dec 01 2008 Frederic Crozat <fcrozat@mandriva.com> 4.17-3mdv2009.1
+ Revision: 308865
- Remove patch4, not needed anymore

* Mon Dec 01 2008 Frederic Crozat <fcrozat@mandriva.com> 4.17-2mdv2009.1
+ Revision: 308855
- No longer start passkey-agent when starting X session

  + Nicolas Lécureuil <nlecureuil@mandriva.com>
    - Own /var/lib/bluetooth

* Sun Oct 26 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.17-1mdv2009.1
+ Revision: 297440
- update to new version 4.17

* Wed Oct 22 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.16-1mdv2009.1
+ Revision: 296374
- update to new version 4.16

* Sun Oct 19 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.14-1mdv2009.1
+ Revision: 295366
- Update to 4.14
- Remove wrong -s arg

* Wed Oct 15 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.13-3mdv2009.1
+ Revision: 293903
- Fix File list
- Fix service files
- Provides bluez-utils as suggested  by Adam

* Wed Oct 15 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.13-2mdv2009.1
+ Revision: 293832
- More Obsoletes

* Fri Oct 10 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 4.13-1mdv2009.1
+ Revision: 291621
- clean configure
  Fix file list
  Fix hidd install path
- Update to bluez 4.13
- Update to Bluez 4.11
  Merge Bluez-utils ( + patches )
  Obsoletes Bluez-utils

* Sat Aug 02 2008 Emmanuel Andry <eandry@mandriva.org> 3.36-1mdv2009.0
+ Revision: 260785
- New version

* Thu Jul 03 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 3.35-1mdv2009.0
+ Revision: 231283
- New version

* Sun Jun 29 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 3.34-1mdv2009.0
+ Revision: 230082
- New version 3.34

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Tue Jun 03 2008 Funda Wang <fwang@mandriva.org> 3.32-1mdv2009.0
+ Revision: 214627
- update to new version 3.32

* Thu May 08 2008 Nicolas Lécureuil <nlecureuil@mandriva.com> 3.31-1mdv2009.0
+ Revision: 204512
- New version 3.31

* Thu Mar 06 2008 Frederic Crozat <fcrozat@mandriva.com> 3.28-1mdv2008.1
+ Revision: 180967
- Release 3.28

* Sun Feb 24 2008 Emmanuel Andry <eandry@mandriva.org> 3.27-1mdv2008.1
+ Revision: 174389
- New version

  + Thierry Vignaud <tv@mandriva.org>
    - fix no-buildroot-tag

* Mon Feb 11 2008 Frederic Crozat <fcrozat@mandriva.com> 3.26-1mdv2008.1
+ Revision: 165112
-Release 3.26

* Sun Feb 03 2008 Emmanuel Andry <eandry@mandriva.org> 3.25-1mdv2008.1
+ Revision: 161743
- New version

* Tue Dec 25 2007 Nicolas Lécureuil <nlecureuil@mandriva.com> 3.24-1mdv2008.1
+ Revision: 137802
- New bugfix release

* Thu Dec 20 2007 Adam Williamson <awilliamson@mandriva.org> 3.23-1mdv2008.1
+ Revision: 135962
- new license policy
- new release 3.23

* Sat Nov 10 2007 Jérôme Soyer <saispo@mandriva.org> 3.22-1mdv2008.1
+ Revision: 107312
- New release

* Wed Oct 10 2007 Nicolas Lécureuil <nlecureuil@mandriva.com> 3.20-1mdv2008.1
+ Revision: 96915
- New version 3.20

* Mon Aug 27 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.15-1mdv2008.0
+ Revision: 71793
- new release: 3.15

* Wed Aug 15 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.14-6mdv2008.0
+ Revision: 63901
- bah

* Wed Aug 15 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.14-5mdv2008.0
+ Revision: 63893
+ rebuild (emptylog)

* Wed Aug 15 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.14-4mdv2008.0
+ Revision: 63839
- bah, fix path headers

* Wed Aug 15 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.14-3mdv2008.0
+ Revision: 63827
- fix location of library

* Wed Aug 15 2007 Funda Wang <fwang@mandriva.org> 3.14-2mdv2008.0
+ Revision: 63671
- fix upgrading

* Wed Aug 15 2007 Per Øyvind Karlsen <peroyvind@mandriva.org> 3.14-1mdv2008.0
+ Revision: 63509
- new release: 3.14

* Thu Aug 02 2007 Olivier Blin <blino@mandriva.org> 3.13-1mdv2008.0
+ Revision: 58035
- drop pkgconfig buildrequires, it's required by rpm-mandriva-setup-build
- 3.13

* Fri May 25 2007 Guillaume Rousse <guillomovitch@mandriva.org> 3.11-1mdv2008.0
+ Revision: 31134
- new version

* Thu May 10 2007 Nicolas Lécureuil <nlecureuil@mandriva.com> 3.10-1mdv2008.0
+ Revision: 26147
- New version 3.10

* Wed May 02 2007 Guillaume Rousse <guillomovitch@mandriva.org> 3.9-2mdv2008.0
+ Revision: 20512
- build requires pkg-config for proper pkgconfig automatic dependencies computation

