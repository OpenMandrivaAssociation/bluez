%define major   2
%define libname %mklibname %name %major

#we need libbluetooth before /usr is mounted
%define _libdir /%{_lib}

Name:           bluez
Summary:        Official Linux Bluetooth protocol stack
Version:        3.9
Release:        %mkrel 1

Source:         http://bluez.sourceforge.net/download/%{name}-libs-%{version}.tar.bz2
URL:            http://bluez.sourceforge.net
License:        GPL
Group:          Communications
BuildRoot:      %{_tmppath}/%{name}-%{version}-buildroot
BuildRequires:  kernel-source

%description
These are the official Bluetooth communication libraries for Linux.

%package -n %{libname}
Summary: Official Linux Bluetooth protocol stack
Group: System/Libraries
Provides: %{name} = %{version}-%{release}
Provides: %{name}-sdp
Obsoletes: %{name}-sdp
Provides: lib%{name}-sdp2
Obsoletes: lib%{name}-sdp2

%description -n %{libname}
These are the official Bluetooth communication libraries for Linux.

%package -n %{libname}-devel
Summary: Headers for developing programs that will use %name
Group: Development/C++
Requires: %{libname} = %{version}
Provides: lib%{name}-devel = %{version}-%{release}
Provides: %{name}-devel = %{version}-%{release}
Provides: lib%{name}-sdp-devel, lib%{name}-sdp2-devel
Obsoletes: lib%{name}-sdp-devel, lib%{name}-sdp2-devel
Provides: %{name}-sdp-devel
Obsoletes: %{name}-sdp-devel

%description -n %{libname}-devel
This package contains the headers that programmers will need to develop
applications which will use libraries from %name.

%prep
%setup -q -n bluez-libs-%version


%build
%configure2_5x 
%make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

mkdir -p $RPM_BUILD_ROOT/%_includedir/bluetooth
mv $RPM_BUILD_ROOT/%_includedir/*.h $RPM_BUILD_ROOT/%_includedir/bluetooth/

mkdir -p $RPM_BUILD_ROOT%{_prefix}/%{_lib}
mv $RPM_BUILD_ROOT/%{_lib}/pkgconfig $RPM_BUILD_ROOT%{_prefix}/%{_lib}/

%clean
rm -rf $RPM_BUILD_ROOT

%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*.so.*

%files -n %{libname}-devel
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog README
%{_includedir}/bluetooth
%{_libdir}/*.so
%{_libdir}/*.la
%{_libdir}/*.a
%{_prefix}/%{_lib}/pkgconfig/bluez.pc
%{_datadir}/aclocal/%name.m4


