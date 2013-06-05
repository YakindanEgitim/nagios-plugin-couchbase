%define name nagios-plugin-couchbase
%define version 1.0
%define unmangled_version 1.0
%define release 1

Summary: A simple nagios plugin to monitor Couchbase 2.0 servers/cluster.
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPLv3
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Ebru Akagunduz <ebru.akagunduz@gmail.com>

%description
Nagios plugin to monitoring Couchbase 

%prep
%setup -n %{name}-%{unmangled_version}

%build
python setup.py build

%install
python setup.py install -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog 
* Initial release
