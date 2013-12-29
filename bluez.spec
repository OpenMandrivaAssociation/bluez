%define major	3
%define libname	%mklibname %{name} %{major}
%define	devname	%mklibname -d %{name}

%bcond_without	systemd

Name:		bluez
Summary:	Official Linux Bluetooth protocol stack
Version:	5.13
Release:	1
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
#Patch0:		0002-systemd-unitdir-enable.patch
#Patch1:		bluez-4.101-automake-1.13.patch
#Patch4:		bluez-socket-mobile-cf-connection-kit.patch
# http://thread.gmane.org/gmane.linux.bluez.kernel/2396
#Patch5:		0001-Add-sixaxis-cable-pairing-plugin.patch
# PS3 BD Remote patches
#Patch6:		0001-input-Add-helper-function-to-request-disconnect.patch
#Patch7:		0002-fakehid-Disconnect-from-PS3-remote-after-10-mins.patch
#Patch8:		0003-fakehid-Use-the-same-constant-as-declared.patch
#Patch9:		bluez-4.101-fix-c++11-compatibility.patch

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
BuildRequires:	pkgconfig(libical)
BuildRequires:	pkgconfig(systemd)

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
%{_bindir}/hcitool
%{_bindir}/l2ping
%{_bindir}/rfcomm
%{_bindir}/sdptool
%{_sysconfdir}/udev/rules.d/*hid2hci*
%{_bindir}/bccmd
%{_bindir}/bluetoothctl
%{_bindir}/btmon
%{_bindir}/hciattach
%{_bindir}/hciconfig
%{_bindir}/hcidump
%dir %{_libdir}/bluetooth
%{_libdir}/bluetooth/bluetoothd
%{_libdir}/bluetooth/obexd
%if %{with systemd}
%{_unitdir}/*.service
%{_prefix}/lib/systemd/user/*.service
%endif
%{_mandir}/man?/*
%config(noreplace) %{_sysconfdir}/sysconfig/*
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/*.conf
%config(noreplace) %{_sysconfdir}/bluetooth
%{_datadir}/dbus-1/system-services/org.bluez.service
%{_datadir}/dbus-1/services/org.bluez.obex.service
/lib/udev/hid2hci
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

%package -n	%{libname}
Summary:	Official Linux Bluetooth protocol stack
Group:		System/Libraries

%description -n	%{libname}
These are the official Bluetooth communication libraries for Linux.

%files -n %{libname}
/%{_lib}/libbluetooth.so.%{major}*

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
%{_bindir}/l2test
%{_bindir}/rctest
%{_bindir}/test-*

#--------------------------------------------------------------------
%package -n    %{devname}
Summary:       Headers for developing programs that will use %{name}
Group:         Development/C++
Requires:      %{libname} = %{version}
Provides:      %{name}-devel = %{version}-%{release}

%description -n        %{devname}
This package contains the headers that programmers will need to develop
applications which will use libraries from %{name}.

%files -n      %{devname}
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
	--enable-shared \
	--disable-hal \
	--enable-pnat \
	--enable-wiimote \
	--enable-tools \
	--enable-bccmd \
	--enable-hidd \
	--enable-pand \
	--enable-dund \
	--enable-hid2hci \
	--enable-library \
	--enable-pcmcia \
	--with-systemdsystemunitdir=/lib/systemd/system

%make

%install
%makeinstall_std rulesdir=%{_sysconfdir}/udev/rules.d udevdir=/lib/udev

mkdir -p %{buildroot}%{_sysconfdir}/bluetooth
cat << EOF > %{buildroot}%{_sysconfdir}/bluetooth/pin
1234
EOF

chmod 600 %{buildroot}%{_sysconfdir}/bluetooth/pin

rm -f %{buildroot}%{_sysconfdir}/default/bluetooth %{buildroot}%{_sysconfdir}/init.d/bluetooth
install -m644 %{SOURCE6} -D %{buildroot}%{_sysconfdir}/sysconfig/pand
install -m644 %{SOURCE7} -D %{buildroot}%{_sysconfdir}/sysconfig/dund
install -m644 %{SOURCE8} -D %{buildroot}%{_sysconfdir}/sysconfig/hidd
install -m644 %{SOURCE9} -D %{buildroot}%{_sysconfdir}/sysconfig/rfcomm

# Remove the cups backend from libdir, and install it in /usr/lib whatever the install
if test -d %{buildroot}/%{_lib}/cups ; then
	install -D -m0755 %{buildroot}/%{_lib}/cups/backend/bluetooth %{buildroot}%{_prefix}/lib/cups/backend/bluetooth
	rm -rf %{buildroot}/%{_lib}/cups
fi 
	
cp test/test-* %{buildroot}%{_bindir}
cp test/simple-agent %{buildroot}%{_bindir}/simple-agent
rm -f %{buildroot}%{_bindir}/test-*.c

mv %{buildroot}/%{_lib}/pkgconfig %{buildroot}%{_libdir}

#install more config files
install -m0644 profiles/network/network.conf %{buildroot}%{_sysconfdir}/bluetooth/
install -m0644 profiles/input/input.conf %{buildroot}%{_sysconfdir}/bluetooth/

install -d -m0755 %{buildroot}%{_localstatedir}/lib/bluetooth

ln -s bluetooth.service %{buildroot}%{_unitdir}/dbus-org.bluez.service
