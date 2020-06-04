%global shortname WRF-WPS 
%global ver 4.1.3
%?altcc_init

Name:           %{shortname}%{?altcc_pkg_suffix}
Version:        %{ver}
Release:        1%{?dist}
Summary:        WRF Model and WPS tools

License:        Public Domain
URL:            http://www.wrf-model.org/
Source0:        https://github.com/wrf-model/WRF/archive/v%{version}/WRF-%{version}.tar.gz
#This was created using the configure script and then modifying the 
#result
Source1:        configure.wrf-gfortran
Source2:        configure.wrf-pgf
Source3:        configure.wrf-intel
Source4:        wrf.module.in
Source10:       https://github.com/wrf-model/WPS/archive/v4.1/WPS-4.1.tar.gz
#This was created using the configure script and then modifying the
#result
Source11:       configure.wps-gfortran
Source12:       configure.wps-pgf
Source13:       configure.wps-intel
Source20:       setupwrf

BuildRequires:  tcsh
BuildRequires:  m4
%if !0%{?altcc}
BuildRequires:  gcc-gfortran
%endif
BuildRequires:  hdf%{?altcc_cc_dep_suffix}-devel
BuildRequires:  jasper-devel
BuildRequires:  libpng-devel
BuildRequires:  ncl%{?altcc_cc_dep_suffix}-devel
BuildRequires:  netcdf-fortran%{?altcc_dep_suffix}-devel
BuildRequires:  numactl-devel
BuildRequires:  time

%description
WRF/WPS build.  They need to be built together which is why we have one
srpm.


%package -n WRF%{?altcc_pkg_suffix}
Summary:        WRF Model
%{?altcc_reqmodules}
%{?altcc_provide:%altcc_provide -n WRF}

%description -n WRF%{?altcc_pkg_suffix}
WRF Model.


%package -n WPS%{?altcc_pkg_suffix}
Summary:        WPS Tools
%{?altcc_provide:%altcc_provide -n WPS}

%description -n WPS%{?altcc_pkg_suffix}
WPS Tools.


%prep
%setup -q -c -a 10
# WPS configure will look for WRF
mv WRF-%{version} WRF
pushd WRF
[ -z "${COMPILER_NAME}" ] && export COMPILER_NAME=gfortran
cp %{_sourcedir}/configure.wrf-${COMPILER_NAME} configure.wrf
%if 0%{?rhel} && 0%{?rhel} <= 7
# Need gcc >= 4.10 for ieee_intrinsic
[ -z "$FC" ]  &&
  sed -i -e '/^ARCH_LOCAL/s/$/ -DNO_IEEE_MODULE/' configure.wrf
%endif
popd
pushd WPS-4.1
cp %{_sourcedir}/configure.wps-${COMPILER_NAME} configure.wps
popd


%build
%{?altcc:module load hdf ncl netcdf}
# This is set by the openmpi module and interferes with the build
unset MPI_LIB
if [ -n "${NETCDF_HOME}" ]; then
  export NETCDF=${NETCDF_HOME}
else
  export NETCDF=/usr
fi
export JASPERINC=/usr/include/jasper
export JASPERLIB=/usr/%{_lib}
export J=$(echo %{?_smp_mflags} | sed 's/-j/-j /')
pushd WRF
./compile em_real
popd
pushd WPS-4.1
./compile
# To explicitly compile plotfmt and plotgrids
./compile util
popd


%install
pushd WRF
mkdir -p %{buildroot}%{_bindir}
cp -a main/*.exe %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/WRF/test
cp -a run %{buildroot}%{_datadir}/WRF
rm %{buildroot}%{_datadir}/WRF/run/*.exe \
   %{buildroot}%{_datadir}/WRF/run/namelist.input
cp -a test/em_real %{buildroot}%{_datadir}/WRF/test
rm %{buildroot}%{_datadir}/WRF/test/em_real/*.exe
popd
pushd WPS-4.1
cp -a *.exe util/*.exe %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/WRF/{geogrid,metgrid}
cp -a geogrid/*TBL* geogrid/gribmap.txt %{buildroot}%{_datadir}/WRF/geogrid
cp -a metgrid/*TBL* metgrid/gribmap.txt %{buildroot}%{_datadir}/WRF/metgrid
popd
sed -e s,@DATADIR@,%{_datadir},g < %SOURCE20 > %{buildroot}%{_bindir}/setupwrf
chmod +x %{buildroot}%{_bindir}/setupwrf

%{?altcc:%altcc_writemodule %SOURCE4}


%files -n WRF%{?altcc_pkg_suffix}
#doc
%{?altcc:%altcc_files -m %{_bindir} %{_datadir}}
%{_bindir}/ndown.exe
# Temporarily removed
#{_bindir}/nup.exe
%{_bindir}/tc.exe
%{_bindir}/real.exe
%{_bindir}/wrf.exe
%{_bindir}/setupwrf
%dir %{_datadir}/WRF
%{_datadir}/WRF/run/
%{_datadir}/WRF/test/


%files -n WPS%{?altcc_pkg_suffix}
#doc
%{?altcc:%altcc_files %{_bindir} %{_datadir}}
%{_bindir}/avg_tsfc.exe
%{_bindir}/calc_ecmwf_p.exe
%{_bindir}/g1print.exe
%{_bindir}/g2print.exe
%{_bindir}/geogrid.exe
%{_bindir}/height_ukmo.exe
%{_bindir}/int2nc.exe
%{_bindir}/metgrid.exe
%{_bindir}/mod_levs.exe
%{_bindir}/plotfmt.exe
%{_bindir}/plotgrids.exe
%{_bindir}/rd_intermediate.exe
%{_bindir}/ungrib.exe
%dir %{_datadir}/WRF
%{_datadir}/WRF/geogrid/
%{_datadir}/WRF/metgrid/


%changelog
* Thu Jan 30 2020 Orion Poplawski <orion@nwra.com> 4.1.3-1
- Update to 4.1.3

* Thu Apr 19 2018 Orion Poplawski <orion@nwra.com> 3.9.1.1-1
- Update to 3.9.1.1

* Thu Sep 29 2016 Orion Poplawski <orion@cora.nwra.com> 3.8.1-1
- Update to 3.8.1
- Compile with -ipo for Intel version
- Increase parallel build cpus
- Fixup some BuildRequires
- Use NETCDF_* module variables for paths
- Build with altcc ncl

* Tue May 31 2016 Orion Poplawski <orion@cora.nwra.com> 3.8-1
- Update to 3.8
- Altccrpms style

* Thu Dec 11 2008 Orion Poplawski <orion@cora.nwra.com> 3.0.1.1-2
- Move WRF install to %{_bindir} and %{_datadir}/WRFV3
- Add setupwrf

* Thu Nov 20 2008 Orion Poplawski <orion@cora.nwra.com> 3.0.1.1-1
- Combinded WRF/WPS
