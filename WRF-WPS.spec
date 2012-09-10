# AltCCRPMS
%global _prefix /opt/%{name}/%{version}
%global _sysconfdir %{_prefix}/etc
%global _defaultdocdir %{_prefix}/share/doc
%global _infodir %{_prefix}/share/info
%global _mandir %{_prefix}/share/man

%global _cc_name intel
%global _cc_name_suffix -%{_cc_name}

#We don't want to be beholden to the proprietary libraries
%global    _use_internal_dependency_generator 0
%global    __find_requires %{nil}

# Non gcc compilers don't generate build ids
%undefine _missing_build_ids_terminate_build

%global shortname wrf

%global mpi_list openmpi

Name:           WRF-WPS341%{?_cc_name_suffix}
Version:        3.4.1
Release:        1%{?dist}
Summary:        WRF Model and WPS tools

Group:          Scientific
License:        Public Domain
URL:            http://www.wrf-model.org/
Source0:        http://www.mmm.ucar.edu/wrf/src/WRFV%{version}.TAR.gz
Source1:        http://www.mmm.ucar.edu/wrf/src/WPSV%{version}.TAR.gz
#This was created using the configure script and then modifying the 
#result to fix the netcdf locations $(WRF_SRC_ROOT_DIR)/netcdf_links
Source2:        configure.wrf
#This was created using the configure script and then modifying the
#result to fix the netcdf locations $(WRF_SRC_ROOT_DIR)/netcdf_links
Source3:        configure.wps
Source4:        setupwrf.in
Source5:        wrf.module.in
# Fix linking against netcdf
Patch0:         WRF-WPS-netcdf.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  tcsh
BuildRequires:  m4
#gfortran on EL5 fails
BuildRequires:  jasper-devel
BuildRequires:  libpng-devel
BuildRequires:  ncl%{?_cc_name_suffix}-static%{?_isa}
BuildRequires:  netcdf-fortran%{?_cc_name_suffix}-devel%{?_isa}
BuildRequires:  numactl-devel
#BuildRequires:  openmpi%{?_cc_name_suffix}-devel


%description
WRF/WPS build.  They need to be built together which is why we have one
srpm.


%package -n WRF341-openmpi%{?_cc_name_suffix}
Summary:        WRF Model
Group:          Scientific
Requires:       netcdf-fortran%{?_cc_name_suffix}-devel%{?_isa}
Provides:       WRF-openmpi-%{_cc_name} = %{version}-%{release}

%description -n WRF341-openmpi%{?_cc_name_suffix}
WRF Model.  DM parallel, simple nesting.


%package -n WPS341-openmpi%{?_cc_name_suffix}
Summary:        WPS Tools
Group:          Scientific
Requires:       netcdf-fortran%{?_cc_name_suffix}-devel%{?_isa}
Requires:       ncl%{?_cc_name_suffix}%{?_isa}
Provides:       WPS-openmpi-%{_cc_name} = %{version}-%{release}

%description -n WPS341-openmpi%{?_cc_name_suffix}
WPS Tools.  DM parallel.


%prep
%setup -q -c -a 1
%patch0 -p1 -b .netcdf
pushd WRFV3
cp %SOURCE2 configure.wrf
#openmpi mpif90 wrapper doesn't take the -f90,-cc options
sed -i.openmpi -r -e 's/ -(f90|cc)=.*//' arch/archive_configure.defaults \
                                         arch/configure_new.defaults
mkdir netcdf_links
ln -s %{_includedir} netcdf_links/include
ln -s %{_libdir} netcdf_links/lib
popd
pushd WPS
cp %SOURCE3 configure.wps
#openmpi mpif90 wrapper doesn't take the -f90,-cc options
sed -i.openmpi -r -e 's/ -(f90|cc)=.*//' arch/configure.defaults
mkdir netcdf_links
ln -s %{_includedir} netcdf_links/include
ln -s %{_libdir} netcdf_links/lib
popd


%build
. /etc/profile.d/modules.sh
module load netcdf-fortran/openmpi-%{_cc_name}
# This is set by the openmpi module and interferes with the build
unset MPI_LIB
module load ncl/%{_cc_name}
export JASPERINC=%{_includedir}/jasper
export JASPERLIB=%{_libdir}
export WRFIO_NCD_LARGE_FILE_SUPPORT=1 
pushd WRFV3
./compile em_real
popd
pushd WPS
./compile
popd


%install
rm -rf $RPM_BUILD_ROOT
pushd WRFV3
mkdir -p $RPM_BUILD_ROOT%{_bindir}
cp -a main/*.exe $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_datadir}/WRFV3/test
cp -a run $RPM_BUILD_ROOT%{_datadir}/WRFV3
rm $RPM_BUILD_ROOT%{_datadir}/WRFV3/run/*.exe \
   $RPM_BUILD_ROOT%{_datadir}/WRFV3/run/namelist.input
cp -a test/em_real $RPM_BUILD_ROOT%{_datadir}/WRFV3/test
rm $RPM_BUILD_ROOT%{_datadir}/WRFV3/test/em_real/*.exe
popd
pushd WPS
cp -a */src/*.exe $RPM_BUILD_ROOT%{_bindir}
popd
sed -e 's#@PREFIX@#%{_prefix}#' < %SOURCE4 > $RPM_BUILD_ROOT%{_bindir}/setupwrf
# AltCCRPMS
# Make the environment-modules file
#mkdir -p %{buildroot}/etc/modulefiles/%{shortname}/%{_cc_name}
# Since we're doing our own substitution here, use our own definitions.
#sed -e 's#@PREFIX@#'%{_prefix}'#' -e 's#@LIB@#%{_lib}#' -e 's#@ARCH@#%{_arch}#' -e 's#@CC@#%{_cc_name}#' \
#< %SOURCE5 > %{buildroot}/etc/modulefiles/%{shortname}/%{_cc_name}/%{version}-%{_arch}
for mpi in %{mpi_list}
do
mkdir -p %{buildroot}/etc/modulefiles/%{shortname}/${mpi}-%{_cc_name}
sed -e 's#@PREFIX@#'%{_prefix}'#' -e 's#@LIB@#%{_lib}#' -e 's#@ARCH@#%{_arch}#' -e 's#@CC@#%{_cc_name}#'  -e 's#@MPI@#'$mpi'#' \
    < %SOURCE5 > %{buildroot}/etc/modulefiles/%{shortname}/${mpi}-%{_cc_name}/%{version}-%{_arch}
done


%clean
rm -rf $RPM_BUILD_ROOT


%files -n WRF341-openmpi%{?_cc_name_suffix}
%doc
/etc/modulefiles/%{shortname}/openmpi-%{_cc_name}/%{version}-%{_arch}
%{_bindir}/ndown.exe
%{_bindir}/nup.exe
%{_bindir}/tc.exe
%{_bindir}/real.exe
%{_bindir}/wrf.exe
%{_bindir}/setupwrf
%{_datadir}/WRFV3

%files -n WPS341-openmpi%{?_cc_name_suffix}
%doc
%{_bindir}/avg_tsfc.exe
%{_bindir}/calc_ecmwf_p.exe
%{_bindir}/g1print.exe
%{_bindir}/g2print.exe
%{_bindir}/geogrid.exe
%{_bindir}/height_ukmo.exe
%{_bindir}/metgrid.exe
%{_bindir}/mod_levs.exe
%{_bindir}/plotfmt.exe
%{_bindir}/plotgrids.exe
%{_bindir}/rd_intermediate.exe
%{_bindir}/ungrib.exe


%changelog
* Thu Sep 6 2012 Orion Poplawski <orion@cora.nwra.com> 3.4.1-1
- Update to 3.4.1
- AltCCRPMs version

* Thu Dec 11 2008 Orion Poplawski <orion@cora.nwra.com> 3.0.1.1-2
- Move WRF install to %{_bindir} and %{_datadir}/WRFV3
- Add setupwrf

* Thu Nov 20 2008 Orion Poplawski <orion@cora.nwra.com> 3.0.1.1-1
- Combinded WRF/WPS
