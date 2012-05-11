%define major	3
%define libname	%mklibname %{name} %{major}
%define	devname	%mklibname -d %{name}

%define _with_systemd 1

Name:		bluez
Summary:	Official Linux Bluetooth protocol stack
Version:	4.99
Release:	2
License:	GPLv2+
Group:		Communications
Source0:	http://www.kernel.org/pub/linux/bluetooth/%{name}-%{version}.tar.xz
Source6:	pand.conf
Source7:	dund.conf
Source8:	hidd.conf
Source9:	rfcomm.conf

# (bor) also disable rule if systemd is active
Patch100:	bluez-4.79-fail_udev_event_on_error.patch
# (kazancas) patch from Fedora
# https://bugzilla.redhat.com/show_bug.cgi?id=498756
Patch4: bluez-socket-mobile-cf-connection-kit.patch
# http://thread.gmane.org/gmane.linux.bluez.kernel/2396
Patch5: 0001-Add-sixaxis-cable-pairing-plugin.patch
# http://thread.gmane.org/gmane.linux.bluez.kernel/8645
Patch6: 0001-systemd-install-systemd-unit-files.patch

BuildRequires:	flex
BuildRequires:	bison
BuildRequires:	udev
BuildRequires:	dbus-devel
BuildRequires:	libusb-devel
BuildRequires:	libalsa-devel
BuildRequires:	libgstreamer0.10-plugins-base-devel
BuildRequires:	gstreamer0.10-devel
BuildRequires:	expat-devel
BuildRequires:	udev-devel
BuildRequires:	libcap-ng-devel
# (kazancas)
Buildrequires:	systemd
BuildRequires:	readline

Requires:	bluez-pin
# MD I highly doubt this is true after looking around
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
%{_bindir}/hcitool
%{_bindir}/l2ping
%{_bindir}/rfcomm
%{_bindir}/sdptool
%{_bindir}/ciptool
%{_bindir}/dfutool
%{_bindir}/gatttool
%{_sbindir}/hciattach
%{_sbindir}/hciconfig
%{_sbindir}/bluetoothd
%{_sbindir}/bccmd
/bin/hidd
/sbin/bluetoothd
%if %{_with_systemd}
/lib/systemd/system/*.service
#/lib/systemd/system/bluetooth.target.wants/bluetooth.service
%endif
#/sbin/udev_bluetooth_helper
%{_mandir}/man?/*
%config(noreplace) %{_sysconfdir}/sysconfig/*
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/*.conf
%config(noreplace) %{_sysconfdir}/bluetooth
%{_datadir}/dbus-1/system-services/org.bluez.service
/lib/udev/bluetooth_serial
/lib/udev/hid2hci
%{_sysconfdir}/udev/rules.d/97-bluetooth-serial.rules
%{_sysconfdir}/udev/rules.d/97-bluetooth-hid2hci.rules
%{_sysconfdir}/udev/rules.d/97-bluetooth.rules
%{_localstatedir}/lib/bluetooth

#--------------------------------------------------------------------

%package        cups
Summary:        CUPS printer backend for Bluetooth printers
Group:          System/Servers
Requires:       cups
Obsoletes:      %name-utils-cups

%description    cups
This package contains the CUPS backend for Bluetooth printers.

%files cups
%{_prefix}/lib/cups/backend/bluetooth

#--------------------------------------------------------------------

%package gstreamer
Summary: Gstreamer support for SBC audio format
Group: Sound
Obsoletes:      %name-utils-gstreamer

%description gstreamer
This package contains gstreamer plugins for the Bluetooth SBC audio format

%files gstreamer
%{_libdir}/gstreamer-*/*.so

#--------------------------------------------------------------------

%package alsa
Summary: ALSA support for Bluetooth audio devices
Group: Sound
Obsoletes:      %name-utils-alsa

%description alsa
This package contains ALSA support for Bluetooth audio devices

%files alsa
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

%package test
Summary:	Tools for testing of various Bluetooth-functions
Group:		System/Servers
Requires:	python-dbus
Requires:	python-gobject

%description test
Contains a few tools for testing various bluetooth functions. The
BLUETOOTH trademarks are owned by Bluetooth SIG, Inc., U.S.A.

%files test
%{_bindir}/l2test
%{_bindir}/rctest
%{_bindir}/apitest
%{_bindir}/list-devices
%{_bindir}/simple-agent
%{_bindir}/simple-service
%{_bindir}/test-adapter
%{_bindir}/test-audio
%{_bindir}/test-device
%{_bindir}/test-discovery
%{_bindir}/test-input
%{_bindir}/test-manager
%{_bindir}/test-network
%{_bindir}/test-serial
%{_bindir}/test-service
%{_bindir}/test-telephony
%{_sbindir}/hciemu

#--------------------------------------------------------------------

%package -n	%{devname}
Summary:	Headers for developing programs that will use %name
Group:		Development/C++
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{devname}
This package contains the headers that programmers will need to develop
applications which will use libraries from %{name}.

%files -n %{devname}
%doc AUTHORS ChangeLog README
%dir %{_includedir}/bluetooth
%{_includedir}/bluetooth/*.h
/%{_lib}/*.so
%{_libdir}/pkgconfig/bluez.pc

#--------------------------------------------------------------------

%prep
%setup -q
%patch100 -p1 -b .fail_event
%patch4 -p1 -b .socket-mobile
%patch5 -p1 -b .cable-pairing
%patch6 -p1 -b .systemd

%build
# (bor) for P101
autoreconf -fi
# fix mdv bug 35444
%define _localstatedir %{_var}
%configure2_5x	\
	--libdir=/%{_lib} \
%if !%{_with_systemd}
	--without-systemdsystemunitdir \
%endif
	--enable-cups \
	--enable-dfutool \
	--enable-tools \
	--enable-bccmd \
	--enable-gstreamer \
	--enable-hidd \
	--enable-pand \
	--enable-dund \
	--enable-hid2hci \
	--enable-pcmcia \
	--enable-capng \
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

rm -f %{buildroot}/etc/default/bluetooth %{buildroot}/etc/init.d/bluetooth
install -D -c -m 0644 %SOURCE6 %buildroot%_sysconfdir/sysconfig/pand
install -D -c -m 0644 %SOURCE7 %buildroot%_sysconfdir/sysconfig/dund
install -D -c -m 0644 %SOURCE8 %buildroot%_sysconfdir/sysconfig/hidd
install -D -c -m 0644 %SOURCE9 %buildroot%_sysconfdir/sysconfig/rfcomm

rm -rf %{buildroot}/%{_lib}/pkgconfig
install -m644 bluez.pc -D  %{buildroot}%{_libdir}/pkgconfig/bluez.pc


# Remove the cups backend from libdir, and install it in /usr/lib whatever the install
if test -d %{buildroot}/%{_lib}/cups ; then
	install -D -m0755 %{buildroot}/%{_lib}/cups/backend/bluetooth %{buildroot}/usr/lib/cups/backend/bluetooth
	rm -rf %{buildroot}/%{_lib}/cups
fi 
	
mkdir -p %{buildroot}/{bin,sbin}
mv %{buildroot}%{_bindir}/hidd %{buildroot}/bin/
mv %{buildroot}%{_sbindir}/bluetoothd %{buildroot}/sbin/

cp test/test-* %{buildroot}%{_bindir}
cp test/simple-agent %{buildroot}%{_bindir}/simple-agent

#install more config files
install -m0644 audio/audio.conf %{buildroot}%{_sysconfdir}/bluetooth/
install -m0644 network/network.conf %{buildroot}%{_sysconfdir}/bluetooth/
install -m0644 input/input.conf %{buildroot}%{_sysconfdir}/bluetooth/
install -m0644 serial/serial.conf %{buildroot}%{_sysconfdir}/bluetooth/

mkdir -p %{buildroot}%{_libdir}/alsa-lib/
mv %{buildroot}/%{_lib}/alsa-lib/*.so %{buildroot}%{_libdir}/alsa-lib/

# remove unpackaged files
rm -f %{buildroot}/%{_libdir}/*/*.la
rm -f %{buildroot}/%{_lib}/*/*.la

install -d -m0755 %{buildroot}/%{_localstatedir}/lib/bluetooth

ln -s bluetooth.service %buildroot/lib/systemd/system/dbus-org.bluez.service

