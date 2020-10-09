# Needed by pulseaudio, which is used by wine
%ifarch %{x86_64}
%bcond_without compat32
%endif

%define major 3
%define libname %mklibname %{name} %{major}
%define devname %mklibname -d %{name}
%define lib32name %mklib32name %{name} %{major}
%define dev32name %mklib32name -d %{name}

Name:		bluez
Summary:	Official Linux Bluetooth protocol stack
Version:	5.55
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

Patch1:		bluez-5.47-c++.patch
## Ubuntu patches
Patch2:		0001-work-around-Logitech-diNovo-Edge-keyboard-firmware-i.patch
# Non-upstream
Patch4:		0001-obex-Use-GLib-helper-function-to-manipulate-paths.patch
Patch7:		0004-agent-Assert-possible-infinite-loop.patch
# https://github.com/hadess/bluez/commits/systemd-hardening
Patch10:	0001-build-Always-define-confdir-and-statedir.patch
Patch11:	0002-systemd-Add-PrivateTmp-and-NoNewPrivileges-options.patch
Patch12:	0003-systemd-Add-more-filesystem-lockdown.patch
Patch13:	0004-systemd-More-lockdown.patch

BuildRequires:	flex
BuildRequires:	bison
BuildRequires:	pkgconfig(readline)
BuildRequires:	pkgconfig(expat)
BuildRequires:	cups-devel
BuildRequires:	pkgconfig(json-c)
BuildRequires:	pkgconfig(ell) >= 0.26
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(libcap-ng)
BuildRequires:	pkgconfig(libusb)
BuildRequires:	pkgconfig(libusb-1.0)
BuildRequires:	pkgconfig(libical)
BuildRequires:	pkgconfig(udev) >= 186
BuildRequires:	pkgconfig(systemd)
# For unitdir macros
BuildRequires:	systemd-macros
%if %{with compat32}
BuildRequires:	devel(libdbus-1)
BuildRequires:	devel(libglib-2.0)
BuildRequires:	devel(libpcre)
BuildRequires:	devel(libical)
BuildRequires:	devel(libudev)
BuildRequires:	devel(libsystemd)
BuildRequires:	devel(libreadline)
BuildRequires:	devel(libjson-c)
%endif

Obsoletes:	obex-data-server < 0.4.7
Provides:	obex-data-server = 0.4.7
Conflicts:	obex-data-server < 0.4.7
Obsoletes:	bluez-alsa < 5.0
Provides:	bluez-alsa = 5.0
Obsoletes:	bluez-gstreamer < 5.0
Provides:	bluez-gstreamer = 5.0

%description
These are the official Bluetooth communication libraries for Linux.

%files
%{_bindir}/avinfo
%{_bindir}/ciptool
%{_bindir}/hcitool
%{_bindir}/gatttool
%{_bindir}/l2ping
%{_bindir}/rfcomm
%{_bindir}/sdptool
%{_bindir}/bccmd
%{_bindir}/bluetoothctl
%{_bindir}/btmon
%{_bindir}/hciattach
%{_bindir}/hciconfig
%{_bindir}/hcidump
%{_bindir}/hex2hcd
%{_bindir}/bluemoon
%{_bindir}/mpris-proxy
%{_bindir}/meshctl
%{_bindir}/mesh-cfgclient
%{_bindir}/btattach
%{_libexecdir}/bluetooth/bluetoothd
%{_libexecdir}/bluetooth/obexd
%{_libexecdir}/bluetooth/bluetooth-meshd
%{_presetdir}/86-bluetooth.preset
%{_unitdir}/bluetooth.service
%{_unitdir}/bluetooth-mesh.service
%{_userunitdir}/obex.service
%{_userunitdir}/dbus-org.bluez.obex.service
%{_mandir}/man1/ciptool.1*
%{_mandir}/man1/hcitool.1*
%{_mandir}/man1/rfcomm.1*
%{_mandir}/man1/sdptool.1*
%{_mandir}/man1/bccmd.1*
%{_mandir}/man1/btattach.1*
%{_mandir}/man1/hciattach.1*
%{_mandir}/man1/hciconfig.1*
%{_mandir}/man1/hcidump.1*
%{_mandir}/man1/l2ping.1*
%{_mandir}/man1/rctest.1*
%{_mandir}/man8/*
%config(noreplace) %{_sysconfdir}/sysconfig/*
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/*.conf
%config(noreplace) %{_sysconfdir}/bluetooth
%{_datadir}/dbus-1/system-services/org.bluez.service
%{_datadir}/dbus-1/system-services/org.bluez.mesh.service
%{_datadir}/dbus-1/services/org.bluez.obex.service
%{_localstatedir}/lib/bluetooth
%dir %{_libdir}/bluetooth
%dir %{_libdir}/bluetooth/plugins
%{_libdir}/bluetooth/plugins/sixaxis.so
%{_datadir}/zsh/site-functions/_bluetoothctl

%post
%systemd_user_post obex.service

%preun
%systemd_user_preun obex.service


#--------------------------------------------------------------------

%package cups
Summary:	CUPS printer backend for Bluetooth printers
Group:		System/Servers
Requires:	cups

%description cups
This package contains the CUPS backend for Bluetooth printers.

%files cups
%{_prefix}/lib/cups/backend/bluetooth

#--------------------------------------------------------------------

%package -n %{libname}
Summary:	Official Linux Bluetooth protocol stack
Group:		System/Libraries

%description -n %{libname}
These are the official Bluetooth communication libraries for Linux.

%files -n %{libname}
%{_libdir}/libbluetooth.so.%{major}*

#--------------------------------------------------------------------

%package hid2hci
Summary:	Put HID proxying bluetooth HCI's into HCI mode
Group:		Communications

%description hid2hci
Most allinone PC's and bluetooth keyboard / mouse sets which include a
bluetooth dongle, ship with a so called HID proxying bluetooth HCI.
The HID proxying makes the keyboard / mouse show up as regular USB HID
devices (after connecting using the connect button on the device + keyboard),
which makes them work without requiring any manual configuration.

The bluez-hid2hci package contains the hid2hci utility and udev rules to
automatically switch supported Bluetooth devices into regular HCI mode.

Install this package if you want to use the bluetooth function of the HCI
with other bluetooth devices like for example a mobile phone.

Note that after installing this package you will first need to pair your
bluetooth keyboard and mouse with the bluetooth adapter before you can use
them again. Since you cannot use your bluetooth keyboard and mouse until
they are paired, this will require the use of a regular (wired) USB keyboard
and mouse.

%files hid2hci
/lib/udev/hid2hci
%{_mandir}/man1/hid2hci.1*
/lib/udev/rules.d/97-hid2hci.rules

%post hid2hci
%{_bindir}/udevadm trigger --subsystem-match=usb

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
%{_bindir}/l2test
%{_bindir}/rctest
%{_bindir}/test-*

#--------------------------------------------------------------------
%package -n %{devname}
Summary:	Headers for developing programs that will use %{name}
Group:		Development/C++
Requires:	%{libname} = %{version}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{devname}
This package contains the headers that programmers will need to develop
applications which will use libraries from %{name}.

%files -n %{devname}
%doc AUTHORS ChangeLog README
%dir %{_includedir}/bluetooth
%{_includedir}/bluetooth/*.h
%{_libdir}/*.so
%{_libdir}/pkgconfig/bluez.pc
#--------------------------------------------------------------------

%if %{with compat32}
%package -n %{lib32name}
Summary:	Official Linux Bluetooth protocol stack (32-bit)
Group:		System/Libraries

%description -n %{lib32name}
These are the official Bluetooth communication libraries for Linux.

%files -n %{lib32name}
%{_prefix}/lib/libbluetooth.so.%{major}*
%dir %{_prefix}/lib/bluetooth
%dir %{_prefix}/lib/bluetooth/plugins
%{_prefix}/lib/bluetooth/plugins/sixaxis.so

#--------------------------------------------------------------------
%package -n %{dev32name}
Summary:	Headers for developing programs that will use %{name} (32-bit)
Group:		Development/C++
Requires:	%{devname} = %{version}
Requires:	%{lib32name} = %{version}

%description -n %{dev32name}
This package contains the headers that programmers will need to develop
applications which will use libraries from %{name}.

%files -n %{dev32name}
%{_prefix}/lib/*.so
%{_prefix}/lib/pkgconfig/bluez.pc
%endif

%prep
%autosetup -p1

libtoolize -f -c
autoreconf -fi

export CONFIGURE_TOP="$(pwd)"

%if %{with compat32}
mkdir build32
cd build32
%configure32 \
	--enable-sixaxis \
	--enable-pie \
	--enable-health \
	--enable-nfc \
	--enable-tools \
	--enable-library \
	--enable-usb \
	--enable-threads \
	--enable-monitor \
	--enable-mesh \
	--enable-obex \
	--enable-client \
	--enable-systemd \
	--with-systemdsystemunitdir=%{_unitdir} \
	--with-systemduserunitdir=%{_userunitdir} \
	--with-udevdir=/lib/udev \
	--enable-datafiles \
	--enable-experimental \
	--enable-deprecated
cd ..
%endif

mkdir build
cd build
%configure \
	--enable-cups \
	--enable-sixaxis \
	--enable-pie \
	--enable-health \
	--enable-nfc \
	--enable-tools \
	--enable-library \
	--enable-usb \
	--enable-threads \
	--enable-monitor \
	--enable-mesh \
	--enable-obex \
	--enable-client \
	--enable-systemd \
	--with-systemdsystemunitdir=%{_unitdir} \
	--with-systemduserunitdir=%{_userunitdir} \
	--with-udevdir=/lib/udev \
	--enable-datafiles \
	--enable-hid2hci \
	--enable-experimental \
	--enable-deprecated

# --enable-deprecated enables tools like hciattach -- still required by lots
# of stuff...

%build
%if %{with compat32}
%make_build -C build32
%endif
%make_build -C build

%install
%if %{with compat32}
%make_install -C build32 rulesdir=%{_sysconfdir}/udev/rules.d udevdir=/lib/udev
%endif
%make_install -C build rulesdir=%{_sysconfdir}/udev/rules.d udevdir=/lib/udev

mkdir -p %{buildroot}%{_sysconfdir}/bluetooth
printf '%s\n' '1234' > %{buildroot}%{_sysconfdir}/bluetooth/pin

chmod 600 %{buildroot}%{_sysconfdir}/bluetooth/pin

install -m644 %{SOURCE6} -D %{buildroot}%{_sysconfdir}/sysconfig/pand
install -m644 %{SOURCE7} -D %{buildroot}%{_sysconfdir}/sysconfig/dund
install -m644 %{SOURCE8} -D %{buildroot}%{_sysconfdir}/sysconfig/hidd
install -m644 %{SOURCE9} -D %{buildroot}%{_sysconfdir}/sysconfig/rfcomm

# "make install" fails to install gatttool, necessary for Bluetooth Low Energy
# Red Hat Bugzilla bug #1141909
# Debian bug #720486
install -m0755 build/attrib/gatttool %{buildroot}%{_bindir}

# "make install" fails to install avinfo
# Red Hat Bugzilla bug #1699680
install -m0755 build/tools/avinfo %{buildroot}%{_bindir}

# Remove the cups backend from libdir, and install it in /usr/lib whatever the install
%if "%{_lib}" == "lib64"
rm -rf %{buildroot}%{_prefix}/lib/cups
install -d %{buildroot}%{_prefix}/lib
mv %{buildroot}%{_libdir}/cups %{buildroot}%{_prefix}/lib/cups
%endif

cp test/test-* %{buildroot}%{_bindir}
cp test/simple-agent %{buildroot}%{_bindir}/simple-agent

install -p -m644 tools/hid2hci.rules -D %{buildroot}/lib/udev/rules.d/97-hid2hci.rules

#install more config files
install -m0644 profiles/network/network.conf %{buildroot}%{_sysconfdir}/bluetooth/
install -m0644 src/main.conf %{buildroot}%{_sysconfdir}/bluetooth/
install -m0644 profiles/input/input.conf %{buildroot}%{_sysconfdir}/bluetooth/

install -d -m0755 %{buildroot}%{_localstatedir}/lib/bluetooth

# copy bluetooth config file and setup auto enable
sed -i 's/#\[Policy\]$/\[Policy\]/; s/#AutoEnable=false/AutoEnable=true/' %{buildroot}%{_sysconfdir}/bluetooth/main.conf

# (tpg) enable obex in userland
ln -sf %{_userunitdir}/obex.service %{buildroot}%{_userunitdir}/dbus-org.bluez.obex.service

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-bluetooth.preset << EOF
enable bluetooth.service
EOF
