%global __spec_install_pre %{___build_pre}

# Kernel has several large (hundreds of mbytes) rpms, they take ~5 mins
# to compress by single-threaded xz. Switch to threaded compression,
# and from level 2 to 3 to keep compressed sizes close to "w2" results.
#
# NB: if default compression in /usr/lib/rpm/redhat/macros ever changes,
# this one might need tweaking (e.g. if default changes to w3.xzdio,
# change below to w4T.xzdio):
%global _binary_payload w3T.xzdio

# Define the version of the Linux Kernel Archive tarball.
%define LKAver 6.1.159

# Define the buildid, if required.
#define buildid .local

# The following build options are enabled by default.
# Use either --without <option> on your rpmbuild command line
# or force the values to 0, here, to disable them.

# kernel-lt
%define with_default      %{?_without_default:      0} %{?!_without_default:      1}
# kernel-lt-doc
%define with_doc          %{?_without_doc:          0} %{?!_without_doc:          1}
# kernel-lt-headers
%define with_headers      %{?_without_headers:      0} %{?!_without_headers:      1}
# perf
%define with_perf         %{?_without_perf:         0} %{?!_without_perf:         1}
# tools
%define with_tools        %{?_without_tools:        0} %{?!_without_tools:        1}
# bpf tool
%define with_bpftool      %{?_without_bpftool:      0} %{?!_without_bpftool:      1}
# vsdo install
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}
# gcc12
%define with_gcc12    %{?_without_gcc12:    0} %{?!_without_gcc12:    1}

# Kernel-lt, devel, headers, perf, tools and bpftool.
%ifarch x86_64
%define with_doc 0
%define doc_build_fail true
%define zipmodules 1
%endif

# Documentation.
%ifarch noarch
%define with_default 0
%define with_headers 0
%define with_perf 0
%define with_tools 0
%define with_bpftool 0
%define with_vdso_install 0
%define zipmodules 0
%endif

# Compressed modules.
%if %{zipmodules}
%global zipsed -e 's/\.ko$/\.ko.xz/'
# For parallel xz processes. Replace with 1 to go back to single process.
%global zcpu `nproc --all`
%endif

# Determine the sublevel number and set pkg_version.
%define sublevel %(echo %{LKAver} | %{__awk} -F\. '{ print $3 }')
%if "%{sublevel}" == ""
%define pkg_version %{LKAver}.0
%else
%define pkg_version %{LKAver}
%endif

# Set pkg_release.
%define pkg_release 1%{?dist}%{?buildid}

%define KVERREL %{pkg_version}-%{pkg_release}.%{_target_cpu}

# Packages that need to be present before kernel-lt is installed
# because its %%post scripts make use of them.
%define kernel_prereq  coreutils, systemd >= 203-2, systemd-udev >= 203-2
%define initrd_prereq  dracut >= 027

Name: kernel-lt
Summary: The Linux kernel. (The core of any Linux-based operating system.)
Group: System Environment/Kernel
License: GPLv2
URL: https://www.kernel.org/
Version: %{pkg_version}
Release: %{pkg_release}
ExclusiveArch: noarch x86_64
ExclusiveOS: Linux
Provides: kernel = %{version}-%{release}
Provides: installonlypkg(kernel)
Requires: %{name}-core-uname-r = %{KVERREL}
Requires: %{name}-modules-uname-r = %{KVERREL}

%if %{with_gcc12}
BuildRequires: gcc-toolset-12-annobin-plugin-gcc
%endif

BuildRequires: bash bc binutils bison bzip2 diffutils dwarves elfutils-devel
BuildRequires: findutils flex gawk gcc git gzip hmaccalc hostname kmod m4
BuildRequires: make net-tools openssl openssl-devel patch perl-Carp
BuildRequires: perl-devel perl-generators perl-interpreter python3-devel
BuildRequires: redhat-rpm-config rsync sh-utils tar xz
%if %{with_doc}
BuildRequires: asciidoc python3-sphinx xmlto
%endif
%if %{with_perf}
BuildRequires: asciidoc audit-libs-devel binutils-devel bison flex
BuildRequires: java-devel libcap-devel newt-devel numactl-devel
BuildRequires: perl(ExtUtils::Embed) xmlto xz-devel zlib-devel
%endif
%if %{with_tools}
BuildRequires: asciidoc gettext libcap-devel libnl3-devel ncurses-devel pciutils-devel
%endif
%if %{with_bpftool}
BuildRequires: binutils-devel python3-docutils zlib-devel
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb

# Sources.
Source0: https://www.kernel.org/pub/linux/kernel/v5.x/linux-%{LKAver}.tar.xz
Source1: config-%{version}-x86_64
Source2: cpupower.service
Source3: cpupower.config
Source4: mod-extra.sh
Source5: mod-extra.list
Source6: mod-extra-blacklist.sh
Source7: filter-x86_64.sh
Source8: filter-modules.sh
Source9: generate_bls_conf.sh

# To build .src.rpm, run with '--with src'
%if %{?_with_src:0}%{!?_with_src:1}
NoSource: 0
%endif

%description
The %{name} meta package.

#
# This macro supplies the requires, provides, conflicts
# and obsoletes for the kernel-lt package.
#	%%kernel_reqprovconf <subpackage>
#
%define kernel_reqprovconf \
Provides: %{name} = %{version}-%{release}\
Provides: %{name}-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: %{name}-drm-nouveau = 16\
Provides: %{name}-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(pre): linux-firmware >= 20150904-56.git6ebf5d57\
Requires(preun): systemd >= 200\
Conflicts: xfsprogs < 4.3.0-1\
Conflicts: xorg-x11-drv-vmmouse < 13.0.99\
%{expand:%%{?%{name}%{?1:_%{1}}_provides:Provides: %%{%{name}%{?1:_%{1}}_provides}}}\
%{expand:%%{?%{name}%{?1:_%{1}}_conflicts:Conflicts: %%{%{name}%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?%{name}%{?1:_%{1}}_obsoletes:Obsoletes: %%{%{name}%{?1:_%{1}}_obsoletes}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel-lt proper to function.\
AutoReq: no\
AutoProv: yes\
%{nil}

%if %{with_doc}
%package doc
Summary: Various bits of documentation found in the kernel sources.
Group: Documentation
Provides: %{name}-doc = %{version}-%{release}
Provides: kernel-doc = %{version}-%{release}
Conflicts: kernel-doc < %{version}-%{release}
%description doc
This package provides documentation files from the kernel sources.
Various bits of information about the Linux kernel and the device
drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to the kernel modules at load time.
%endif

%if %{with_headers}
%package headers
Summary: Header files of the kernel, for use by glibc.
Group: Development/System
Provides: glibc-kernheaders = 3.0-46
Obsoletes: glibc-kernheaders < 3.0-46
Provides: %{name}-headers = %{version}-%{release}
Obsoletes: %{name}-headers < %{version}-%{release}
Provides: kernel-headers = %{version}-%{release}
Conflicts: kernel-headers < %{version}-%{release}
%description headers
This package provides the C header files that specify the interface
between the Linux kernel and userspace libraries and programs. The
header files define structures and constants that are needed when
building most standard programs. They are also required when
rebuilding the glibc package.
%endif

%if %{with_perf}
%package -n perf
Summary: Performance monitoring of the kernel.
Group: Development/System
License: GPLv2
%description -n perf
This package provides the perf tool and the supporting documentation
for performance monitoring of the Linux kernel.

%package -n python3-perf
Summary: Python bindings for applications that will manipulate perf events.
Group: Development/Libraries
%description -n python3-perf
This package provides a module that permits applications written in the
Python programming language to use the interface to manipulate perf events.
%endif

%if %{with_tools}
%package -n %{name}-tools
Summary: Assortment of tools for the kernel.
Group: Development/System
License: GPLv2
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:1.5-16
Provides:  kernel-tools = %{version}-%{release}
Conflicts: kernel-tools < %{version}-%{release}
Requires: %{name}-tools-libs = %{version}-%{release}
%define __requires_exclude ^%{_bindir}/python
%description -n %{name}-tools
This package contains the tools/ directory and its supporting
documentation, derived from the kernel source.

%package -n %{name}-tools-libs
Summary: Libraries for the kernel tools.
Group: Development/System
License: GPLv2
Provides:  kernel-tools-libs = %{version}-%{release}
Conflicts: kernel-tools-libs < %{version}-%{release}
%description -n %{name}-tools-libs
This package contains the libraries built from the
tools/ directory, derived from the kernel source.

%package -n %{name}-tools-libs-devel
Summary: Development package for the kernel tools libraries.
Group: Development/System
License: GPLv2
Requires: %{name}-tools = %{version}-%{release}
Requires: %{name}-tools-libs = %{version}-%{release}
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
Provides:  kernel-tools-libs-devel = %{version}-%{release}
Conflicts: kernel-tools-libs-devel < %{version}-%{release}
%description -n %{name}-tools-libs-devel
This package contains the development files for the tools/ directory
libraries, derived from the kernel source.
%endif

%if %{with_bpftool}
%package -n bpftool
Summary: Inspection and simple manipulation of eBPF programs and maps.
License: GPLv2
%description -n bpftool
This package provides the bpftool which allows inspection and simple
manipulation of eBPF programs and maps.
%endif

#
# This macro creates a kernel-lt-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package %{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: %{name}%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}-devel-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: %{name}-devel-uname-r = %{KVERREL}%{?1:+%{1}}\
Provides: kernel%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-devel-uname-r = %{KVERREL}%{?1:+%{1}}\
Provides: kernel-devel = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(%{name})\
Provides: installonlypkg(kernel)\
AutoReqProv: no\
Requires(pre): findutils\
Requires: findutils\
Requires: perl-interpreter\
%description %{?1:%{1}-}devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-lt-<subpackage>-modules-extra package.
#	%%kernel_modules_extra_package <subpackage> <pretty-name>
#
%define kernel_modules_extra_package() \
%package %{?1:%{1}-}modules-extra\
Summary: Extra kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: %{name}%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: %{name}%{?1:-%{1}}-modules-extra = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(%{name}-module)\
Provides: installonlypkg(kernel-module)\
Provides: %{name}%{?1:-%{1}}-modules-extra-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: %{name}-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: %{name}%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules-extra\
This package provides less commonly used kernel modules for the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-lt-<subpackage>-modules package.
#	%%kernel_modules_package <subpackage> <pretty-name>
#
%define kernel_modules_package() \
%package %{?1:%{1}-}modules\
Summary: Kernel modules to match the %{?2:%{2}-}core kernel\
Group: System Environment/Kernel\
Provides: %{name}%{?1:-%{1}}-modules-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}-modules-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: %{name}-modules = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(%{name}-module)\
Provides: installonlypkg(kernel-module)\
Provides: %{name}%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: %{name}-uname-r = %{KVERREL}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules\
This package provides commonly used kernel modules for the %{?2:%{2}-}core kernel package.\
%{nil}

#
# This macro creates a kernel-lt-<subpackage> meta package.
#	%%kernel_meta_package <subpackage>
#
%define kernel_meta_package() \
%package %{1}\
summary: kernel meta-package for the %{1} kernel\
group: system environment/kernel\
Provides: installonlypkg(%{name})\
Provides: installonlypkg(kernel)\
Requires: %{name}-%{1}-core-uname-r = %{KVERREL}+%{1}\
Requires: %{name}-%{1}-modules-uname-r = %{KVERREL}+%{1}\
%description %{1}\
The meta-package for the %{1} kernel\
%{nil}

#
# This macro creates a kernel-lt-<subpackage>
# and its corresponding devel package.
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package %{?1:%{1}-}core\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
Provides: %{name}-%{?1:%{1}-}core-uname-r = %{KVERREL}%{?1:+%{1}}\
Provides: installonlypkg(%{name})\
Provides: installonlypkg(kernel)\
%{expand:%%kernel_reqprovconf}\
%if %{?1:1} %{!?1:0} \
%{expand:%%kernel_meta_package %{?1:%{1}}}\
%endif\
%{expand:%%kernel_devel_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_extra_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{nil}

%define variant_summary The Linux kernel
%kernel_variant_package
%description core
This package provides the Linux kernel (vmlinuz), the core of any
Linux-based operating system. The kernel handles the basic functions
of the OS: memory allocation, process allocation, device I/O, etc.

# Disable the building of the debug package(s).
%define debug_package %{nil}

# Disable the creation of build_id symbolic links.
%define _build_id_links none

%prep
%if %{with_gcc12}
. /opt/rh/gcc-toolset-12/enable
%endif

%setup -q -n %{name}-%{version} -c
%{__mv} linux-%{LKAver} linux-%{version}-%{release}.%{_target_cpu}

pushd linux-%{KVERREL} > /dev/null

# Purge the source tree of all unrequired dot-files.
%{_bindir}/find -name '.*' -type f | %{_bindir}/xargs --no-run-if-empty %{__rm} -rf

%{__cp} %{SOURCE1} .

# Set the EXTRAVERSION string in the top level Makefile.
%{__sed} -i "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}/" Makefile

%ifarch x86_64
%{__cp} config-%{version}-%{_target_cpu} .config
%{__make} -s ARCH=%{_target_cpu} listnewconfig | %{__grep} -E '^CONFIG_' > newoptions-el8-%{_target_cpu}.txt || true
if [ -s newoptions-el8-%{_target_cpu}.txt ]; then
    %{__cat} newoptions-el8-%{_target_cpu}.txt
    exit 1
fi
%{__rm} -f newoptions-el8-%{_target_cpu}.txt
%endif

%{__mv} COPYING COPYING-%{version}

# Do not use ambiguous python shebangs. RHEL 8 now has a new script
# (/usr/lib/rpm/redhat/brp-mangle-shebangs) which forces us to specify a
# non-ambiguous python shebang for scripts that we ship in the buildroot.
#
# That script will throw an error like:
#
# *** ERROR: ambiguous python shebang in /usr/bin/kvm_stat: #!/usr/bin/python. Change it to python3 (or python2) explicitly.
#
for Dir in Documentation scripts tools; do
    %{_bindir}/find $Dir -type f
done | %{_bindir}/xargs --no-run-if-empty pathfix.py -i %{__python3} -p -n | \
    %{__grep} -E -v 'no change' 2> /dev/null

%{__make} -s distclean

popd > /dev/null

%build
%if %{with_gcc12}
. /opt/rh/gcc-toolset-12/enable
%endif

pushd linux-%{KVERREL} > /dev/null

%ifarch x86_64
%if %{with_default}
%{__cp} config-%{version}-%{_target_cpu} .config

%{__make} -s ARCH=%{_target_cpu} oldconfig

%{__make} -s ARCH=%{_target_cpu} %{?_smp_mflags} bzImage

%{__make} -s ARCH=%{_target_cpu} %{?_smp_mflags} modules || exit 1
%endif

%if %{with_headers}
%{__make} -s ARCH=%{_target_cpu} headers
%endif

%global perf_make \
    %{__make} -s -C tools/perf prefix=%{_prefix} EXTRA_CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}" PYTHON=%{__python3} WERROR=0 HAVE_CPLUS_DEMANGLE=1 NO_BIONIC=1 NO_GTK2=1 NO_LIBBABELTRACE=1 NO_LIBUNWIND=1 NO_LIBZSTD=1 NO_PERF_READ_VDSO32=1 NO_PERF_READ_VDSOX32=1 NO_STRLCPY=1

%if %{with_perf}
# Make sure that check-headers.sh is executable.
%{__chmod} +x tools/perf/check-headers.sh

%{perf_make} DESTDIR=$RPM_BUILD_ROOT all
%endif

%global tools_make \
    %{__make} -s CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}"

%if %{with_tools}
# Make sure that version-gen.sh is executable.
%{__chmod} +x tools/power/cpupower/utils/version-gen.sh

pushd tools/power/cpupower > /dev/null
%{tools_make} CPUFREQ_BENCH=false DEBUG=false
popd > /dev/null

pushd tools/power/cpupower/debug/x86_64 > /dev/null
%{tools_make} centrino-decode
%{tools_make} powernow-k8-decode
popd > /dev/null

pushd tools/power/x86/x86_energy_perf_policy > /dev/null
%{__make} -s
popd > /dev/null

pushd tools/power/x86/turbostat > /dev/null
%{__make} -s
popd > /dev/null

pushd tools/power/x86/intel-speed-select > /dev/null
%{__make} -s
popd > /dev/null

pushd tools/thermal/tmon > /dev/null
%{__make} -s
popd > /dev/null

pushd tools/iio > /dev/null
%{__make} -s
popd > /dev/null

pushd tools/gpio > /dev/null
%{__make} -s
popd > /dev/null
%endif

%global bpftool_make \
    %{__make} -s EXTRA_CFLAGS="${RPM_OPT_FLAGS}" EXTRA_LDFLAGS="%{__global_ldflags}" DESTDIR=$RPM_BUILD_ROOT

%if %{with_bpftool} && %{with_default}
pushd tools/bpf/bpftool > /dev/null
%{bpftool_make}
popd > /dev/null
%endif
%endif

%ifarch noarch
%if %{with_doc}
# Sometimes non-world-readable files sneak into the kernel sources.
%{__chmod} -Rf a+rX,ug+w,o-w Documentation
%endif
%endif

popd > /dev/null

%install
%if %{with_gcc12}
. /opt/rh/gcc-toolset-12/enable
%endif

pushd linux-%{KVERREL} > /dev/null

%{__rm} -rf $RPM_BUILD_ROOT

%ifarch x86_64
KernelVer=%{version}-%{release}.%{_target_cpu}

%{__mkdir_p} $RPM_BUILD_ROOT/boot
%{__mkdir_p} $RPM_BUILD_ROOT%{_libexecdir}
%{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/$KernelVer

%if %{with_default}
#
# This macro is to allow the (conditional)
# compression of the kernel-lt module files.
#
%define __spec_install_post \
    %{__arch_install_post} \
    %{__os_install_post} \
    if [ "%{zipmodules}" -eq "1" ]; then \
        %{_bindir}/find $RPM_BUILD_ROOT/lib/modules/ -name '*.ko' -type f | \
            %{_bindir}/xargs --no-run-if-empty -P%{zcpu} %{__xz} \
    fi \
%{nil}

# Install the results into the RPM_BUILD_ROOT directory.
%{__install} -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
%{__install} -m 644 .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/config
%{__install} -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer
%{__install} -m 644 System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/System.map

# We estimate the size of the initramfs because rpm needs to take this size
# into consideration when performing disk space calculations. (See bz #530778)
dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20

%{__cp} arch/x86/boot/bzImage $RPM_BUILD_ROOT/boot/vmlinuz-$KernelVer
%{__chmod} 755 $RPM_BUILD_ROOT/boot/vmlinuz-$KernelVer
%{__cp} $RPM_BUILD_ROOT/boot/vmlinuz-$KernelVer $RPM_BUILD_ROOT/lib/modules/$KernelVer/vmlinuz

# Override mod-fw because we don't want it to install any firmware.
# We'll get it from the linux-firmware package and we don't want conflicts.
%{__make} -s ARCH=%{_target_cpu} INSTALL_MOD_PATH=$RPM_BUILD_ROOT KERNELRELEASE=$KernelVer modules_install mod-fw=

%if %{with_vdso_install}
%{__make} -s ARCH=%{_target_cpu} INSTALL_MOD_PATH=$RPM_BUILD_ROOT KERNELRELEASE=$KernelVer vdso_install
%{_bindir}/find $RPM_BUILD_ROOT/lib/modules/$KernelVer/vdso -name 'vdso*.so' -type f | \
    %{_bindir}/xargs --no-run-if-empty %{__strip}
%if 0
if %{__grep} -q '^CONFIG_XEN=y$' .config; then
    echo > ldconfig-%{name}.conf "\
# This directive teaches ldconfig to search in nosegneg subdirectories
# and cache the DSOs there with extra bit 1 set in their hwcap match
# fields.  In Xen guest kernels, the vDSO tells the dynamic linker to
# search in nosegneg subdirectories and to match this extra hwcap bit
# in the ld.so.cache file.
hwcap 1 nosegneg"
fi
if [ ! -s ldconfig-%{name}.conf ]; then
    echo > ldconfig-%{name}.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
fi
%{__install} -D -m 444 ldconfig-%{name}.conf $RPM_BUILD_ROOT/etc/ld.so.conf.d/%{name}-$KernelVer.conf
%endif
%{__rm} -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/vdso/.build-id
%endif

#
# This looks scary but the end result is supposed to be:
#
# - all arch relevant include/ files.
# - all Makefile and Kconfig files.
# - all script/ files.
#
%{__rm} -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
%{__rm} -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
%{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer > /dev/null
%{__ln_s} build source
popd > /dev/null
%{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/$KernelVer/extra
%{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
%{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/$KernelVer/weak-updates

# First copy everything . . .
%{__cp} --parents $(%{_bindir}/find  -type f -name 'Makefile*' -o -name 'Kconfig*') $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
%{__cp} Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
%{__cp} System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
if [ -s Module.markers ]; then
    %{__cp} Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
fi
%{__gzip} -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz
%{__cp} $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz $RPM_BUILD_ROOT/lib/modules/$KernelVer/symvers.gz

# . . . then drop all but the needed Makefiles and Kconfig files.
%{__rm} -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
%{__rm} -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
%{__rm} -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
%{__cp} .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
%{__cp} -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
%{__rm} -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/tracing
%{__rm} -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/spdxcheck.py
if [ -f tools/objtool/objtool ]; then
    %{__cp} -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool/ || :
fi
if [ -f arch/x86/*lds ]; then
    %{__cp} -a arch/x86/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
fi
if [ -f arch/x86/kernel/module.lds ]; then
    %{__cp} -a --parents arch/x86/kernel/module.lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
fi
%{__rm} -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
%{__rm} -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
if [ -d arch/x86/include ]; then
    %{__cp} -a --parents arch/x86/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
fi
%{__cp} -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
%{__cp} -a --parents arch/x86/boot/compressed/string.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/boot/ctype.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/boot/string.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/boot/string.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/entry/syscalls/syscall_32.tbl $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/entry/syscalls/syscall_64.tbl $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/purgatory/entry64.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/purgatory/purgatory.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/purgatory/setup-x86_64.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/purgatory/stack.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/tools/relocs_32.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/tools/relocs_64.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/tools/relocs.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/tools/relocs_common.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/tools/relocs.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents tools/include/tools/le_byteshift.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/

# Now ensure that the Makefile and version.h files have matching
# timestamps so that external modules can be built.
%{_bindir}/touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile \
    $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/uapi/linux/version.h

# Copy .config to include/config/auto.conf so a "make prepare" is unnecessary.
%{__cp} $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config \
    $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%{_bindir}/find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name '*.ko' -type f > modnames

# Mark the modules executable, so that strip-to-file can strip them.
%{_bindir}/xargs --no-run-if-empty %{__chmod} u+x < modnames

# Generate a list of modules for block and networking.
%{__grep} -F /drivers/ modnames | %{_bindir}/xargs --no-run-if-empty %{__nm} -upA | \
    %{__sed} -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

collect_modules_list()
{
    %{__sed} -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef | \
        LC_ALL=C %{_bindir}/sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
    if [ ! -z "$3" ]; then
        %{__sed} -r -e "/^($3)\$/d" -i $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
    fi
}

collect_modules_list networking \
    'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt(l_|2x00)(pci|usb)_probe|register_netdevice'

collect_modules_list block \
    'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size' 'pktcdvd.ko|dm-mod.ko'

collect_modules_list drm \
    'drm_open|drm_init'

collect_modules_list modesetting \
    'drm_crtc_init'

# Detect any missing or incorrect license tags.
(%{_bindir}/find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name '*.ko' | %{_bindir}/xargs %{_sbindir}/modinfo -l | \
    %{__grep} -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$') && exit 1

# Remove all the files that will be auto generated by depmod at the kernel install time.
pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer > /dev/null
%{__rm} -f modules.{alias*,builtin.bin,dep*,*map,symbols*,devname,softdep}
popd > /dev/null

#
# Generate the kernel-lt-core and kernel-lt-modules file lists.
#

# Make a copy the System.map file for depmod to use.
%{__cp} System.map $RPM_BUILD_ROOT/

pushd $RPM_BUILD_ROOT > /dev/null

# Create a backup of the full module tree so it can be
# restored after the filtering has been completed.
%{__mkdir} restore
%{__cp} -r lib/modules/$KernelVer/* restore/

# Call the modules-extra script to move things around. Note the cleanup, below.
%{SOURCE4} $RPM_BUILD_ROOT /lib/modules/$KernelVer %{SOURCE5}

# Blacklist net autoloadable modules in modules-extra.
%{SOURCE6} $RPM_BUILD_ROOT/modules-extra.list

%{__cat} $RPM_BUILD_ROOT/modules-extra.list | %{_bindir}/xargs %{__rm} -f

# Find all the module files and filter them out into the core and modules lists.
%{_bindir}/find lib/modules/$KernelVer/kernel -name '*.ko' -type f | \
    %{_bindir}/sort -n > modules.list

%{__cp} %{SOURCE7} .
%{SOURCE8} modules.list %{_target_cpu}
%{__rm} -f filter-*.sh

### BCAT
%if 0
# Run depmod on the resulting tree to make sure that it isn't broken.
%{_sbindir}/depmod -b . -aeF ./System.map $KernelVer &> depmod.out
if [ -s depmod.out ]; then
    echo "Depmod failure"
    %{__cat} depmod.out
    exit 1
else
    %{__rm} -f depmod.out
fi

# As depmod has just been executed the following needs to be repeated.
# Remove all the files that will be auto generated by depmod at the kernel-lt install time.
pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer > /dev/null
%{__rm} -f modules.{alias*,builtin.bin,dep*,*map,symbols*,devname,softdep}
popd > /dev/null
%endif
### BCAT

# Go back and find all of the various directories in the tree.
# We use this for the directory lists in kernel-lt-core.
%{_bindir}/find lib/modules/$KernelVer/kernel -mindepth 1 -type d | \
    %{_bindir}/sort -n > module-dirs.list

# Cleanup.
%{__rm} -f System.map
%{__cp} -r restore/* lib/modules/$KernelVer/
%{__rm} -rf restore

popd > /dev/null

# Make sure that the file lists start with absolute paths or the rpmbuild fails.
# Also add in the directory entries.
%{__sed} -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/k-d.list > ../%{name}-modules.list
%{__sed} -e 's/^lib*/%dir \/lib/' %{?zipsed} $RPM_BUILD_ROOT/module-dirs.list > ../%{name}-core.list
%{__sed} -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/modules.list >> ../%{name}-core.list
%{__sed} -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/modules-extra.list >> ../%{name}-modules-extra.list

# Cleanup.
%{__rm} -f $RPM_BUILD_ROOT/k-d.list
%{__rm} -f $RPM_BUILD_ROOT/modules.list
%{__rm} -f $RPM_BUILD_ROOT/module-dirs.list
%{__rm} -f $RPM_BUILD_ROOT/modules-extra.list

# Move the development files out of the root of the /lib/modules/ file system.
%{__mkdir_p} $RPM_BUILD_ROOT/usr/src/kernels
%{__mv} $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/usr/src/kernels/$KernelVer
%{__ln_s} -f %{_usrsrc}/kernels/$KernelVer $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

# Purge the kernel-lt-devel tree of leftover junk.
%{_bindir}/find $RPM_BUILD_ROOT/usr/src/kernels -name '.*.cmd' -type f | \
    %{_bindir}/xargs --no-run-if-empty %{__rm} -f

# Create a boot loader script configuration file for this kernel.
%{SOURCE9} $KernelVer $RPM_BUILD_ROOT ""
%endif

%if %{with_headers}
# Install the kernel headers before installing any tools.
%{__make} -s ARCH=%{_target_cpu} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

%{_bindir}/find $RPM_BUILD_ROOT/usr/include ! -name '*.h' -type f | \
    %{_bindir}/xargs --no-run-if-empty %{__rm} -f
%endif

%if %{with_perf}
%{perf_make} DESTDIR=$RPM_BUILD_ROOT lib=%{_lib} install-bin
%{perf_make} DESTDIR=$RPM_BUILD_ROOT lib=%{_lib} install-traceevent-plugins

# Remove the trace link.
%{__rm} -f $RPM_BUILD_ROOT%{_bindir}/trace

# Remove the perf-tip directory.
%{__rm} -rf $RPM_BUILD_ROOT%{_docdir}/perf-tip

# Remove the examples directory.
%{__rm} -rf $RPM_BUILD_ROOT/usr/lib/perf/examples

# Remove the bpf directory.
%{__rm} -rf $RPM_BUILD_ROOT/usr/lib/perf/include/bpf

%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

%{__mkdir_p} $RPM_BUILD_ROOT%{_mandir}/man1
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-man
%endif

%if %{with_tools}
%{__mkdir_p} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
%{__mkdir_p} $RPM_BUILD_ROOT%{_unitdir}
%{__mkdir_p} $RPM_BUILD_ROOT%{_mandir}/man1
%{__mkdir_p} $RPM_BUILD_ROOT%{_mandir}/man8

pushd tools/power/cpupower > /dev/null
%{__make} -s DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
popd > /dev/null

%{__rm} -f $RPM_BUILD_ROOT%{_libdir}/*.{a,la}
%find_lang cpupower
%{__mv} cpupower.lang ../

pushd tools/power/cpupower/debug/x86_64 > /dev/null
%{__install} -m 755 centrino-decode $RPM_BUILD_ROOT%{_bindir}/centrino-decode
%{__install} -m 755 powernow-k8-decode $RPM_BUILD_ROOT%{_bindir}/powernow-k8-decode
popd > /dev/null

%{__chmod} 0755 $RPM_BUILD_ROOT%{_libdir}/libcpupower.so*

%{__install} -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_unitdir}/cpupower.service
%{__install} -m 644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/cpupower

pushd tools/power/x86/x86_energy_perf_policy > /dev/null
%{__make} -s DESTDIR=$RPM_BUILD_ROOT install
popd > /dev/null

pushd tools/power/x86/turbostat > /dev/null
%{__make} -s DESTDIR=$RPM_BUILD_ROOT install
popd > /dev/null

pushd tools/power/x86/intel-speed-select > /dev/null
%{__make} -s DESTDIR=$RPM_BUILD_ROOT install
popd > /dev/null

pushd tools/thermal/tmon > /dev/null
%{__make} -s INSTALL_ROOT=$RPM_BUILD_ROOT install
popd > /dev/null

pushd tools/iio > /dev/null
%{__make} -s DESTDIR=$RPM_BUILD_ROOT install
popd > /dev/null

pushd tools/gpio > /dev/null
%{__make} -s DESTDIR=$RPM_BUILD_ROOT install
popd > /dev/null

pushd tools/kvm/kvm_stat > /dev/null
%{__make} -s INSTALL_ROOT=$RPM_BUILD_ROOT install-tools
%{__make} -s INSTALL_ROOT=$RPM_BUILD_ROOT install-man
popd > /dev/null
%endif

%if %{with_bpftool} && %{with_default}
pushd tools/bpf/bpftool > /dev/null
%{bpftool_make} prefix=%{_prefix} bash_compdir=%{_sysconfdir}/bash_completion.d/ mandir=%{_mandir} install
%{bpftool_make} prefix=%{_prefix} bash_compdir=%{_sysconfdir}/bash_completion.d/ mandir=%{_mandir} doc-install
popd > /dev/null
%endif

%if %{with_headers}
# We calculate the headers checksum after all the tools have been installed
# because they might also install their own set of header files.
# Compute a content hash to export as Provides: kernel-lt-headers-checksum.
HEADERS_CHKSUM=$(export LC_ALL=C; %{_bindir}/find $RPM_BUILD_ROOT/usr/include -name '*.h' -type f \
			! -path $RPM_BUILD_ROOT/usr/include/linux/version.h | \
			%{_bindir}/sort | %{_bindir}/xargs %{__cat} | %{_bindir}/sha1sum - | \
			%{_bindir}/cut -f1 -d' ');
# Export the checksum via the usr/include/linux/version.h file so the dynamic
# find-provides can obtain the hash to update it accordingly.
echo "#define KERNEL_HEADERS_CHECKSUM \"$HEADERS_CHKSUM\"" >> $RPM_BUILD_ROOT/usr/include/linux/version.h
%endif
%endif

%ifarch noarch
DocDir=$RPM_BUILD_ROOT%{_datadir}/doc/%{name}-doc-%{version}

%{__mkdir_p} $DocDir

%if %{with_doc}
%{__tar} -h -f - --exclude=man --exclude='.*' -c Documentation | %{__tar} -xf - -C $DocDir
%endif
%endif

popd > /dev/null

%clean
%{__rm} -rf $RPM_BUILD_ROOT

# Scripts section.
%if %{with_default}
%triggerin -n %{name}-core -- microcode_ctl
KVERSION=%{pkg_version}-%{pkg_release}.%{_target_cpu}
if [ -e "/lib/modules/$KVERSION/modules.dep" ]; then
    %{_bindir}/dracut -f --kver $KVERSION
fi
%endif

%if %{with_tools}
%post -n %{name}-tools-libs
%{_sbindir}/ldconfig || exit $?

%postun -n %{name}-tools-libs
%{_sbindir}/ldconfig || exit $?
%endif

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
#
%define kernel_devel_post() \
%{expand:%%post %{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]; then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x %{_sbindir}/hardlink ]; then\
    (cd %{_usrsrc}/kernels/%{KVERREL}%{?1:+%{1}} &&\
        %{_bindir}/find . -type f | while read f; do\
        %{_sbindir}/hardlink -c %{_usrsrc}/kernels/*%{?dist}.*/$f $f\
        done)\
fi\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules-extra package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_extra_post [<subpackage>]
#
%define kernel_modules_extra_post() \
%{expand:%%post %{?1:%{1}-}modules-extra}\
%{_sbindir}/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules-extra}\
%{_sbindir}/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_post [<subpackage>]
#
%define kernel_modules_post() \
%{expand:%%post %{?1:%{1}-}modules}\
%{_sbindir}/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules}\
%{_sbindir}/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans %{?1:%{1}-}core}\
if [ -x %{_sbindir}/weak-modules ]; then\
    %{_sbindir}/weak-modules --add-kernel %{KVERREL}%{?1:+%{1}} || exit $?\
fi\
%{_bindir}/kernel-install add %{KVERREL}%{?1:+%{1}} /lib/modules/%{KVERREL}%{?1:+%{1}}/vmlinuz || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel-lt package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_modules_post %{?-v*}}\
%{expand:%%kernel_modules_extra_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post %{?-v*:%{-v*}-}core}\
%{-r:\
if [ `%{_bindir}/uname -i` == "x86_64" ] && [ -f /etc/sysconfig/kernel ]; then\
    %{_bindir}/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=%{name}%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{nil}

#
# This macro defines a %%preun script for a kernel-lt package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1:%{1}-}core}\
%{_bindir}/kernel-install remove %{KVERREL}%{?1:+%{1}} /lib/modules/%{KVERREL}%{?1:+%{1}}/vmlinuz || exit $?\
if [ -x %{_sbindir}/weak-modules ]; then\
    %{_sbindir}/weak-modules --remove-kernel %{KVERREL}%{?1:+%{1}} || exit $?\
fi\
%{nil}

%kernel_variant_preun
%kernel_variant_post

if [ -x %{_sbindir}/ldconfig ]; then
    %{_sbindir}/ldconfig || exit $?
fi

# Files section.
%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/%{name}-doc-%{version}/Documentation/*
%dir %{_datadir}/doc/%{name}-doc-%{version}/Documentation
%dir %{_datadir}/doc/%{name}-doc-%{version}
%endif

%if %{with_headers}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf
%{_libdir}/libperf-jvmti.so
%dir %{_libdir}/traceevent/plugins
%{_libdir}/traceevent/plugins/*
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_datadir}/perf-core/*
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf

%files -n python3-perf
%defattr(-,root,root)
%{python3_sitearch}/*
%endif

%if %{with_tools}
%defattr(-,root,root)
%files -n %{name}-tools -f cpupower.lang
%{_bindir}/cpupower
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%{_bindir}/x86_energy_perf_policy
%{_bindir}/turbostat
%{_bindir}/intel-speed-select
%{_bindir}/tmon
%{_bindir}/iio_event_monitor
%{_bindir}/iio_generic_buffer
%{_bindir}/lsiio
%{_bindir}/lsgpio
%{_bindir}/gpio-hammer
%{_bindir}/gpio-event-mon
%{_bindir}/gpio-watch
%{_bindir}/kvm_stat
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%{_unitdir}/cpupower.service
%{_datadir}/bash-completion/completions/cpupower
%{_mandir}/man[1-8]/cpupower*
%{_mandir}/man1/kvm_stat*
%{_mandir}/man8/turbostat*
%{_mandir}/man8/x86_energy_perf_policy*

%files -n %{name}-tools-libs
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.1

%files -n %{name}-tools-libs-devel
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%{_includedir}/cpuidle.h
%endif

%if %{with_bpftool} && %{with_default}
%files -n bpftool
%{_sbindir}/bpftool
%{_sysconfdir}/bash_completion.d/bpftool
%{_mandir}/man8/bpftool*
%endif

%if %{with_default}
# Empty meta-package.
%files
%defattr(-,root,root)
%endif

#
# This macro defines the %%files sections for the kernel-lt package
# and its corresponding devel package.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{2}\
%{expand:%%files -f %{name}-%{?3:%{3}-}core.list %{?3:%{3}-}core}\
%defattr(-,root,root)\
%{!?_licensedir:%global license %%doc}\
%license linux-%{KVERREL}/COPYING-%{version}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/%{?-k:%{-k*}}%{!?-k:vmlinuz}\
%ghost /boot/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?3:+%{3}}\
%attr(600,root,root) /lib/modules/%{KVERREL}%{?3:+%{3}}/System.map\
%ghost /boot/System.map-%{KVERREL}%{?3:+%{3}}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/symvers.gz\
/lib/modules/%{KVERREL}%{?3:+%{3}}/config\
%ghost /boot/symvers-%{KVERREL}%{?3:+%{3}}.gz\
%ghost /boot/config-%{KVERREL}%{?3:+%{3}}\
%ghost /boot/initramfs-%{KVERREL}%{?3:+%{3}}.img\
%dir /lib/modules\
%dir /lib/modules/%{KVERREL}%{?3:+%{3}}\
%dir /lib/modules/%{KVERREL}%{?3:+%{3}}/kernel\
/lib/modules/%{KVERREL}%{?3:+%{3}}/build\
/lib/modules/%{KVERREL}%{?3:+%{3}}/source\
/lib/modules/%{KVERREL}%{?3:+%{3}}/updates\
/lib/modules/%{KVERREL}%{?3:+%{3}}/weak-updates\
/lib/modules/%{KVERREL}%{?3:+%{3}}/bls.conf\
%if %{1}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/vdso\
%if 0\
/etc/ld.so.conf.d/%{name}-%{KVERREL}%{?3:+%{3}}.conf\
%endif\
%endif\
/lib/modules/%{KVERREL}%{?3:+%{3}}/modules.*\
%{expand:%%files -f %{name}-%{?3:%{3}-}modules.list %{?3:%{3}-}modules}\
%defattr(-,root,root)\
%{expand:%%files %{?3:%{3}-}devel}\
%defattr(-,root,root)\
%defverify(not mtime)\
%{_usrsrc}/kernels/%{KVERREL}%{?3:+%{3}}\
%{expand:%%files -f %{name}-%{?3:%{3}-}modules-extra.list %{?3:%{3}-}modules-extra}\
%defattr(-,root,root)\
%config(noreplace) /etc/modprobe.d/*-blacklist.conf\
/lib/modules/%{KVERREL}%{?3:+%{3}}/extra\
%if %{?3:1} %{!?3:0}\
%{expand:%%files %{3}}\
%defattr(-,root,root)\
%endif\
%endif\
%{nil}

%kernel_variant_files %{with_vdso_install} %{with_default}

%changelog
* Wed Dec 10 2025 Akemi Yagi <toracat@elrepo.org> - 6.1.159-1
- The first release of a kernel-lt package set with the 6.1.159 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-6.1.159]
