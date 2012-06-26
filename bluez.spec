%define major	3
%define libname	%mklibname %{name} %{major}
%define	devname	%mklibname -d %{name}

%define _with_systemd 1

Name:		bluez
Summary:	Official Linux Bluetooth protocol stack
Version:	4.101
Release:	1
License:	GPLv2+
Group:		Communications
Source0:	http://www.kernel.org/pub/linux/bluetooth/%{name}-%{version}.tar.xz
Source6:	pand.conf
Source7:	dund.conf
Source8:	hidd.conf
Source9:	rfcomm.conf
Source10:	bluez-uinput.modules

# http://thread.gmane.org/gmane.linux.bluez.kernel/8645
Patch0:		0002-systemd-unitdir-enable.patch

Patch4:		bluez-socket-mobile-cf-connection-kit.patch
# http://thread.gmane.org/gmane.linux.bluez.kernel/2396
Patch5:		0001-Add-sixaxis-cable-pairing-plugin.patch
# PS3 BD Remote patches
Patch6:		0001-input-Add-helper-function-to-request-disconnect.patch
Patch7:		0002-fakehid-Disconnect-from-PS3-remote-after-10-mins.patch
Patch8:		0003-fakehid-Use-the-same-constant-as-declared.patch


BuildRequires:	flex
BuildRequires:	bison
Buildrequires:	systemd
BuildRequires:	readline
BuildRequires:	udev
BuildRequires:	expat-devel
BuildRequires:	pkgconfig(alsa)
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(gstreamer-plugins-base-0.10)
BuildRequires:	pkgconfig(gstreamer-0.10)
BuildRequires:	pkgconfig(libcap-ng)
BuildRequires:	pkgconfig(libusb)
BuildRequires:	usb1-devel
BuildRequires:	pkgconfig(udev)

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
%if %{_with_systemd}
/lib/systemd/system/*.service
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

%package        cups
Summary:        CUPS printer backend for Bluetooth printers
Group:          System/Servers
Requires:       cups

%description    cups
This package contains the CUPS backend for Bluetooth printers.

%files cups
%{_prefix}/lib/cups/backend/bluetooth

#--------------------------------------------------------------------

%package gstreamer
Summary: Gstreamer support for SBC audio format
Group: Sound

%description gstreamer
This package contains gstreamer plugins for the Bluetooth SBC audio format

%files gstreamer
%{_libdir}/gstreamer-*/*.so

#--------------------------------------------------------------------

%package alsa
Summary: ALSA support for Bluetooth audio devices
Group: Sound

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

%files -n %{devname}
%doc AUTHORS ChangeLog README
%dir %{_includedir}/bluetooth
%{_includedir}/bluetooth/*.h
/%{_lib}/*.so
%{_libdir}/pkgconfig/bluez.pc

#--------------------------------------------------------------------

%prep
%setup -q
%apply_patches

%build
libtoolize -f -c
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
	
cp test/test-* %{buildroot}%{_bindir}
cp test/simple-agent %{buildroot}%{_bindir}/simple-agent

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

# remove unpackaged files
rm -f %{buildroot}/%{_libdir}/*/*.la
rm -f %{buildroot}/%{_lib}/*/*.la

install -d -m0755 %{buildroot}/%{_localstatedir}/lib/bluetooth

ln -s bluetooth.service %buildroot/lib/systemd/system/dbus-org.bluez.service

