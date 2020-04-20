Name: ripe.atlas.cousteau
Version: 1.4.2.td8
Release: 1
Summary: RIPE Atlas Cousteau
Group: Applications/Internet
License: GPLv3
URL: https://github.com/dreibh/ripe-atlas-cousteau
Source: https://packages.nntb.no/software/ripe.atlas.cousteau/%{name}-%{version}.tar.bz2

AutoReqProv: on
BuildRequires: gcc
BuildRequires: python3
BuildRequires: python3-coverage
BuildRequires: python3-dateutil
BuildRequires: python3-funcsigs
BuildRequires: python3-jsonschema
BuildRequires: python3-mock
BuildRequires: python3-nose
BuildRequires: python3-pip
BuildRequires: python3-requests
BuildRequires: python3-setuptools
# BuildRequires: python3-socketIO-client
# BuildRequires: python3-websocket-client
BuildRoot: %{_tmppath}/%{name}-%{version}-build


# This package does not generate debug information (no executables):
%global debug_package %{nil}

# TEST ONLY:
# define _unpackaged_files_terminate_build 0


%description
A python wrapper around the RIPE ATLAS API.
See https://ripe-atlas-cousteau.readthedocs.io/en/latest/ for details!

%prep
%setup -n %{name}-%{version} -n %{name}-%{version}

%build
python3 setup.py build

%install
python3 setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
