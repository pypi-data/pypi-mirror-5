%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

Name:    python-pcore
Version: 0.1
Release: 1%{?dist}
Summary: A Python package that provides various core tools

Group:   Development/Languages
License: GPLv3
URL:     http://github.com/KonishchevDmitry/pcore
Source:  http://pypi.python.org/packages/source/p/pcore/pcore-%{version}.tar.gz

BuildArch:     noarch
BuildRequires: python-setuptools

%description
A Python package that provides various core tools


%prep
%setup -n pcore-%version -q


%build
%{__python} setup.py build


%install
[ "%buildroot" = "/" ] || rm -rf "%buildroot"

%{__python} setup.py install -O1 --skip-build --root "%buildroot"


%files
%defattr(-,root,root,-)

%python_sitelib/pcore
%python_sitelib/pcore-*.egg-info


%clean
[ "%buildroot" = "/" ] || rm -rf "%buildroot"


%changelog
* Mon Nov 18 2013 Dmitry Konishchev <konishchev@gmail.com> - 0.1-1
- New package
