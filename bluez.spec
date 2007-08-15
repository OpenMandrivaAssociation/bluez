%define major   2
%define libname %mklibname %name %major
%define	devname	%mklibname -d %{name}

Name:		bluez
Summary:	Official Linux Bluetooth protocol stack
Version:	3.14
Release:	%mkrel 3
License:	GPL
Group:		Communications
URL:		http://bluez.sourceforge.net/
Source0:	http://bluez.sourceforge.net/download/%{name}-libs-%{version}.tar.lzma

%description
These are the official Bluetooth communication libraries for Linux.

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

%prep
%setup -q -n bluez-libs-%{version}

%build
%configure2_5x	-includedir=%{_includedir}/bluetooth
%make

%install
rm -rf %{buildroot}
%makeinstall_std
rm -f %{buildroot}%{_libdir}/lib*.so.*
mkdir %{buildroot}/%{_lib}
mv src/.libs/libbluetooth.so.* %{buildroot}/%{_lib}

%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%files -n %{libname}
%defattr(-,root,root)
/%{_lib}/lib*.so.%{major}*

%files -n %{devname}
%defattr(-,root,root)
%doc AUTHORS ChangeLog README
%{_includedir}/bluetooth
%{_libdir}/*.so
%{_libdir}/*.la
%{_libdir}/*.a
%{_libdir}/pkgconfig/bluez.pc
%{_datadir}/aclocal/%{name}.m4
