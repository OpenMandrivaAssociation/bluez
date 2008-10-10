%define xinit_level 80

%define major   3
%define libname %mklibname %{name} %major
%define	devname	%mklibname -d %{name}

Name:		    bluez
Summary:	    Official Linux Bluetooth protocol stack
Version:	    4.11
Release:	    %mkrel 1
License:	    GPLv2+
Group:		    Communications
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
URL:		    http://bluez.sourceforge.net/
Source0:	    http://bluez.sourceforge.net/download/%{name}-%{version}.tar.gz
Source1:        bluetooth.init
Source2:        pand.init
Source3:        dund.init
Source4:        hidd.init
Source5:        bluetooth.conf
Source6:        pand.conf
Source7:        dund.conf
Source8:        hidd.conf
Source9:        rfcomm.conf
Source10:       hidd.hotplug
Source11:       hidd.udev.rules
Source12:       %{name}.bash-completion
# (fc) 2.8-2mdk change default configuration (Fedora)
Patch0:         bluez-defaultconf.patch
# (fc) 2.25-4mdk fix cups backend location for x86-64
Patch3:         bluez-2.25-fixcups.patch
# kmobiletools backport of standard auth by pin exec prog
# http://kmobiletools.org/files/bluez-pin-exec-patch-r2.diff.bz2
Patch4:         bluez-3.9-pin-exec.patch
BuildRequires:  dbus-devel 
BuildRequires:  flex 
BuildRequires:  bison 
BuildRequires:  libusb-devel
BuildRequires:  libalsa-devel 
BuildRequires:  udev-tools 
BuildRequires:  automake >= 1.9
BuildRequires:  libgstreamer0.10-plugins-base-devel 
BuildRequires:  gstreamer0.10-devel hal-devel
BuildRequires:  expat-devel
Requires:       python 
Requires:       bluez-pin 
Requires:       obex-data-server
Provides:       bluez-sdp 
Provides:       bluez-sdp
Provides:       bluez-pan 
Provides:       bluez-pan
Provides:       bluez-hciemu 
Provides:       bluez-hciemu
Suggests:       bluez-firmware

Obsoletes:      %name-utils

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

%_post_service bluetooth
%_post_service dund
%_post_service hidd
%_post_service pand

%preun
%_preun_service bluetooth
%_preun_service dund
%_preun_service hidd
%_preun_service pand

%postun
if [ "$1" = "0" ]; then
  update-alternatives --remove bluepin /usr/bin/bluepin
fi

%triggerpostun -- bluez-utils < 2.9-1mdk
/sbin/chkconfig bluetooth reset

%files
%defattr(-,root,root)
%{_bindir}/*
%{_sbindir}/*
/sbin/udev_bluetooth_helper
%{_mandir}/man?/*
%dir %{_sysconfdir}/bluetooth
%{_sysconfdir}/bluetooth/main.conf
%{_sysconfdir}/bluetooth/rfcomm.conf
%{_sysconfdir}/bluetooth/audio.conf
%{_sysconfdir}/bluetooth/pin
%{_sysconfdir}/bash_completion.d/bluez
%{_sysconfdir}/dbus-1/system.d/bluetooth.conf
/lib/udev/bluetooth_serial
/%_lib/bluetooth/plugins/*
%{_sysconfdir}/udev/rules.d/97-bluetooth-serial.rules
%{_sysconfdir}/udev/rules.d/60-bluetooth.rules
%{_sysconfdir}/X11/xinit.d/%{xinit_level}bluez

#--------------------------------------------------------------------

%package        cups
Summary:        CUPS printer backend for Bluetooth printers
Group:          System/Servers
Requires:       cups

%description    cups
This package contains the CUPS backend for Bluetooth printers.

%files cups
%defattr(-, root, root)
%{_prefix}/lib/cups/backend/bluetooth

#--------------------------------------------------------------------

%package gstreamer
Summary: Gstreamer support for SBC audio format
Group: Sound

%description gstreamer
This package contains gstreamer plugins for the Bluetooth SBC audio format

%files gstreamer
%defattr(-, root, root)
/%{_lib}/gstreamer-*/*.so

#--------------------------------------------------------------------

%package alsa
Summary: ALSA support for Bluetooth audio devices
Group: Sound

%description alsa
This package contains ALSA support for Bluetooth audio devices

%files alsa
%defattr(-, root, root)
%doc audio/asound.conf
/%{_lib}/alsa-lib/*.so

#--------------------------------------------------------------------

%package -n	%{libname}
Summary:	Official Linux Bluetooth protocol stack
Group:		System/Libraries
Provides:	%{name} = %{version}-%{release}
Provides:	%{name}-sdp
Obsoletes:	%{name}-sdp
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

%description -n %{devname}
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
#%patch0 -p1 -b .defaultconf
%patch3 -p1 -b .fixcups
#%patch4 -p1 -b .auth

#needed by patch3
FORCE_AUTOCONF_2_5=1 AUTOMAKE="automake --add-missing" autoreconf

%build
# fix mdv bug 35444
%define _localstatedir %{_var}

%configure2_5x	--libdir=/%{_lib} --enable-cups --enable-hid2hci --enable-dfutool --enable-tools --enable-bccmd --enable-gstreamer --enable-hidd --enable-pand --enable-dund

%make

%install
rm -rf %{buildroot}
%makeinstall_std rulesdir=%{_sysconfdir}/udev/rules.d udevdir=/lib/udev

cat << EOF > %{buildroot}%{_sysconfdir}/bluetooth/pin
1234
EOF

chmod 600 %{buildroot}%{_sysconfdir}/bluetooth/pin

rm -rf %{buildroot}/%{_lib}/pkgconfig
install -m644 bluez.pc -D  %{buildroot}%{_libdir}/pkgconfig/bluez.pc

# Remove the cups backend from libdir, and install it in /usr/lib whatever the install
rm -rf ${RPM_BUILD_ROOT}%{_libdir}/cups
install -D -m0755 cups/bluetooth ${RPM_BUILD_ROOT}/usr/lib/cups/backend/bluetooth

install -D -m0755 scripts/bluetooth.rules ${RPM_BUILD_ROOT}/%{_sysconfdir}/udev/rules.d/97-bluetooth-serial.rules
install -D -m0755 scripts/bluetooth_serial ${RPM_BUILD_ROOT}/lib/udev/bluetooth_serial

mkdir -p  %{buildroot}%{_sysconfdir}/X11/xinit.d
cat << EOF > %{buildroot}%{_sysconfdir}/X11/xinit.d/%{xinit_level}%{name}
#!/bin/sh
SESSION=\$1
if [ "\${SESSION}" != "KDE" ]; then
    exec %{_bindir}/passkey-agent --default /bin/bluepin
fi
EOF
chmod 755 %{buildroot}%{_sysconfdir}/X11/xinit.d/%{xinit_level}%{name}

#mkdir -p %{buildroot}/sbin
#cp %{buildroot}%{_bindir}/hidd %{buildroot}/sbin/
#cp %{buildroot}%{_sbindir}/hcid %{buildroot}/sbin/
cp test/test-* %{buildroot}%{_bindir}
#cp hcid/dbus-test %{buildroot}%{_bindir}/bluez-dbus-test

install -D -m0755 %{SOURCE10} %{buildroot}/sbin/udev_bluetooth_helper
install -D -m0644 %{SOURCE11} %{buildroot}%{_sysconfdir}/udev/rules.d/60-bluetooth.rules

# bash completion
install -d -m 755 %{buildroot}%{_sysconfdir}/bash_completion.d
install -m 644 %{SOURCE12} %{buildroot}%{_sysconfdir}/bash_completion.d/%{name}

#install more config files
install -m0644 audio/audio.conf %{buildroot}%{_sysconfdir}/bluetooth/

# remove unpackaged files
rm -f $RPM_BUILD_ROOT/%{_libdir}/*/*.la
rm -f $RPM_BUILD_ROOT/%{_lib}/*/*.la

%clean
rm -fr %{buildroot}
