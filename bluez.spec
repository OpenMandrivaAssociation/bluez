%define major	3
%define libname	%mklibname %{name} %{major}
%define	devname	%mklibname -d %{name}

Name:		bluez
Summary:	Official Linux Bluetooth protocol stack
Version:	4.48
Release:	%mkrel 1
License:	GPLv2+
Group:		Communications
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
URL:		http://bluez.sourceforge.net/
Source0:	http://www.kernel.org/pub/linux/bluetooth/%{name}-%{version}.tar.gz
#Source1:	bluetooth.init
#Source2:	pand.init
#Source3:	dund.init
#Source4:	hidd.init
Source5:	bluetooth.conf
Source6:	pand.conf
Source7:	dund.conf
Source8:	hidd.conf
Source9:	rfcomm.conf
Source10:	hidd.hotplug
Source11:	hidd.udev.rules
# (fc) 2.25-4mdk fix cups backend location for x86-64
Patch3:		bluez-2.25-fixcups.patch
BuildRequires:	dbus-devel 
BuildRequires:	flex 
BuildRequires:	bison 
BuildRequires:	libusb-devel
BuildRequires:	libalsa-devel 
BuildRequires:	udev-tools 
BuildRequires:	libgstreamer0.10-plugins-base-devel 
BuildRequires:	gstreamer0.10-devel hal-devel
BuildRequires:	expat-devel
Requires:	python 
Requires:	bluez-pin 
Requires:	obex-data-server
Provides:	bluez-sdp
Obsoletes:	bluez-sdp < 4.0
Provides:	bluez-pan
Provides:	bluez-hciemu
Obsoletes:	bluez-hciemu
Provides:	bluez-utils
Obsoletes:	bluez-utils < 4.0
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

##%_post_service bluetooth
##%_post_service dund
##%_post_service hidd
##%_post_service pand

%preun
##%_preun_service bluetooth
##%_preun_service dund
##%_preun_service hidd
##%_preun_service pand

%postun
if [ "$1" = "0" ]; then
  update-alternatives --remove bluepin /usr/bin/bluepin
fi

%triggerin -- bluez < 4.46-4mdv
/sbin/chkconfig --del bluetooth
/sbin/chkconfig --del dund
/sbin/chkconfig --del hidd
/sbin/chkconfig --del pand

%files
%defattr(-,root,root)
%{_bindir}/*
%{_sbindir}/*
/sbin/hidd
/sbin/bluetoothd
/sbin/udev_bluetooth_helper
%{_mandir}/man?/*
%dir %{_sysconfdir}/bluetooth
##%config(noreplace) %{_sysconfdir}/rc.d/init.d/*
%config(noreplace) %{_sysconfdir}/sysconfig/*
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/*.conf
%config(noreplace) %{_sysconfdir}/bluetooth
%config(noreplace) %{_datadir}/dbus-1/system-services/org.bluez.service
/lib/udev/bluetooth_serial
#/%_lib/bluetooth/plugins/*
%{_sysconfdir}/udev/rules.d/97-bluetooth-serial.rules
%{_sysconfdir}/udev/rules.d/97-bluetooth-hid2hci.rules
%{_sysconfdir}/udev/rules.d/97-bluetooth.rules
%{_sysconfdir}/udev/rules.d/60-bluetooth.rules
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
%defattr(-, root, root)
%{_prefix}/lib/cups/backend/bluetooth

#--------------------------------------------------------------------

%package gstreamer
Summary: Gstreamer support for SBC audio format
Group: Sound
Obsoletes:      %name-utils-gstreamer

%description gstreamer
This package contains gstreamer plugins for the Bluetooth SBC audio format

%files gstreamer
%defattr(-, root, root)
%{_libdir}/gstreamer-*/*.so

#--------------------------------------------------------------------

%package alsa
Summary: ALSA support for Bluetooth audio devices
Group: Sound
Obsoletes:      %name-utils-alsa

%description alsa
This package contains ALSA support for Bluetooth audio devices

%files alsa
%defattr(-, root, root)
%{_libdir}/alsa-lib/*.so
%{_sysconfdir}/alsa/bluetooth.conf

#--------------------------------------------------------------------

%package -n	%{libname}
Summary:	Official Linux Bluetooth protocol stack
Group:		System/Libraries
Provides:	lib%{name}-sdp2
Obsoletes:	lib%{name}-sdp2

%description -n	%{libname}
These are the official Bluetooth communication libraries for Linux.

%files -n %{libname}
%defattr(-,root,root)
/%{_lib}/lib*.so.%{major}*

#--------------------------------------------------------------------

%package -n	%{devname}
Summary:	Headers for developing programs that will use %name
Group:		Development/C++
Requires:	%{libname} = %{version}
Provides:	lib%{name}-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-sdp-devel, lib%{name}-sdp2-devel
Obsoletes:	lib%{name}-sdp-devel, lib%{name}-sdp2-devel
Provides:	%{name}-sdp-devel
Obsoletes:	%{name}-sdp-devel
Obsoletes:	%{libname}-devel

%description -n	%{devname}
This package contains the headers that programmers will need to develop
applications which will use libraries from %{name}.

%files -n %{devname}
%defattr(-,root,root)
%doc AUTHORS ChangeLog README
%dir %{_includedir}/bluetooth
%{_includedir}/bluetooth/*.h
/%{_lib}/*.so
/%{_lib}/*.la
%{_libdir}/pkgconfig/bluez.pc

#--------------------------------------------------------------------

%prep
%setup -q -n %name-%{version}
%patch3 -p1 -b .fixcups

#needed by patch3
libtoolize --force
FORCE_AUTOCONF_2_5=1 AUTOMAKE="automake --add-missing" autoreconf

%build
# fix mdv bug 35444
%define _localstatedir %{_var}

%configure2_5x	--libdir=/%{_lib} --enable-cups \
                --enable-hid2hci \
                --enable-dfutool \
                --enable-tools \
                --enable-bccmd \
                --enable-gstreamer \
                --enable-hidd \
                --enable-pand \
                --enable-dund

%make

%install
rm -rf %{buildroot}
%makeinstall_std rulesdir=%{_sysconfdir}/udev/rules.d udevdir=/lib/udev 

mkdir -p %{buildroot}%{_libdir}
mv %{buildroot}/%{_lib}/gstreamer-0.10 %{buildroot}%{_libdir}


cat << EOF > %{buildroot}%{_sysconfdir}/bluetooth/pin
1234
EOF

chmod 600 %{buildroot}%{_sysconfdir}/bluetooth/pin

rm -f %{buildroot}/etc/default/bluetooth %{buildroot}/etc/init.d/bluetooth
for a in bluetooth dund hidd pand ; do
         install -D -m0644 $RPM_SOURCE_DIR/$a.conf %{buildroot}%{_sysconfdir}/sysconfig/$a
done

rm -rf %{buildroot}/%{_lib}/pkgconfig
install -m644 bluez.pc -D  %{buildroot}%{_libdir}/pkgconfig/bluez.pc

# Remove the cups backend from libdir, and install it in /usr/lib whatever the install
rm -rf %{buildroot}%{_libdir}/cups
install -D -m0755 cups/bluetooth %{buildroot}/usr/lib/cups/backend/bluetooth

install -D -m0644 scripts/bluetooth.rules %{buildroot}/%{_sysconfdir}/udev/rules.d/97-bluetooth-serial.rules
install -D -m0644 scripts/bluetooth.rules %{buildroot}/%{_sysconfdir}/udev/rules.d/97-bluetooth-hid2hci.rules
install -D -m0644 scripts/bluetooth.rules %{buildroot}/%{_sysconfdir}/udev/rules.d/97-bluetooth.rules
install -D -m0755 scripts/bluetooth_serial %{buildroot}/lib/udev/bluetooth_serial

mkdir -p %{buildroot}/sbin
cp %{buildroot}%{_bindir}/hidd %{buildroot}/sbin/
cp %{buildroot}%{_sbindir}/bluetoothd %{buildroot}/sbin/

cp test/test-* %{buildroot}%{_bindir}
cp test/simple-agent %{buildroot}%{_bindir}/simple-agent

install -D -m0755 %{SOURCE10} %{buildroot}/sbin/udev_bluetooth_helper
install -D -m0644 %{SOURCE11} %{buildroot}%{_sysconfdir}/udev/rules.d/60-bluetooth.rules

#install more config files
install -m0644 audio/audio.conf %{buildroot}%{_sysconfdir}/bluetooth/
install -m0644 network/network.conf %{buildroot}%{_sysconfdir}/bluetooth/
install -m0644 input/input.conf %{buildroot}%{_sysconfdir}/bluetooth/

mkdir -p %buildroot%{_datadir}/dbus-1/system-services/
install -D -m0644 src/bluetooth.conf %{buildroot}%{_datadir}/dbus-1/system-services/org.bluez.service

%__mkdir -p %{buildroot}%{_libdir}/alsa-lib/
%__mv %{buildroot}/%{_lib}/alsa-lib/*.so %{buildroot}%{_libdir}/alsa-lib/

# remove unpackaged files
rm -f %{buildroot}/%{_libdir}/*/*.la
rm -f %{buildroot}/%{_lib}/*/*.la

install -d -m0755 %{buildroot}/%{_localstatedir}/lib/bluetooth

%clean
rm -fr %{buildroot}
