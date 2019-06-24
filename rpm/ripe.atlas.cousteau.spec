%define version 1.4.2_td1.0
%define unmangled_version 1.4.2-td1.0

Name: ripe.atlas.cousteau
Version: %{version}
Release: 1
Summary: RIPE Atlas Cousteau
Group: Applications/Internet
License: GPLv3
URL: https://github.com/dreibh/ripe-atlas-cousteau
Source: https://packages.nntb.no/software/ripe.atlas.cousteau/%{name}-%{unmangled_version}.tar.bz2

AutoReqProv: on
BuildRequires: gcc
BuildRequires: python3
BuildRequires: python3-coverage
BuildRequires: python3-dateutil
BuildRequires: python3-funcsigs
BuildRequires: python3-jsonschema
BuildRequires: python3-mock
BuildRequires: python3-nose
BuildRequires: python3-requests
BuildRequires: python3-setuptools
BuildRequires: python3-socketIO-client
BuildRequires: python3-websocket-client
BuildRoot: %{_tmppath}/%{name}-%{version}-build


%description
A python wrapper around RIPE ATLAS API.
See https://ripe-atlas-cousteau.readthedocs.io/en/latest/ for details!

%prep
%setup -n %{name}-%{version} -n %{name}-%{version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
