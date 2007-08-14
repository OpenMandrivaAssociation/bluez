%define major   2
%define libname %mklibname %name %major
%define	devname	%mklibname -d %{name}
#we need libbluetooth before /usr is mounted
%define _libdir /%{_lib}

Name:		bluez
Summary:	Official Linux Bluetooth protocol stack
Version:	3.14
Release:	%mkrel 1
License:	GPL
Group:		Communications
URL:		http://bluez.sourceforge.net/
Source0:	http://bluez.sourceforge.net/download/%{name}-libs-%{version}.tar.lzma
#BuildRequires:  kernel-source

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

%description -n %{devname}
This package contains the headers that programmers will need to develop
applications which will use libraries from %{name}.

%prep
%setup -q -n bluez-libs-%{version}

%build
%configure2_5x	--libdir=/%{_lib} \
		--includedir=%{_includedir}/bluetooth
%make

%install
rm -rf %{buildroot}
%makeinstall_std %{buildroot}%{_libdir}/pkgconfig

%if 0
mkdir -p %{buildroot}/%_includedir/bluetooth
mv %{buildroot}/%_includedir/*.h %{buildroot}/%_includedir/bluetooth/

mkdir -p %{buildroot}%{_prefix}/%{_lib}
mv %{buildroot}/%{_lib}/pkgconfig %{buildroot}%{_prefix}/%{_lib}/
%endif
%clean
rm -rf %{buildroot}

%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/*.so.*

%files -n %{devname}
%defattr(-,root,root)
%doc AUTHORS ChangeLog README
%{_includedir}/bluetooth
%{_libdir}/*.so
%{_libdir}/*.la
%{_libdir}/*.a
%{_libdir}/pkgconfig/bluez.pc
%{_datadir}/aclocal/%{name}.m4
