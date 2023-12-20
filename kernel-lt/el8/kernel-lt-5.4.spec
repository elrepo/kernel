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
%define LKAver 5.4.265

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

# Do not package the source tarball.
NoSource: 0

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
%{__cp} -a --parents arch/x86/entry/syscalls/syscallhdr.sh $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%{__cp} -a --parents arch/x86/entry/syscalls/syscalltbl.sh $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
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
%{_mandir}/man7/bpf-helpers.7.gz
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
* Wed Dec 20 2023 S.Tindall <s10dal@elrepo.org> - 5.4.265-1
- Updated with the 5.4.265 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.265]

* Thu Dec 14 2023 S.Tindall <s10dal@elrepo.org> - 5.4.264-1
- Updated with the 5.4.264 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.264]

* Fri Dec 08 2023 S.Tindall <s10dal@elrepo.org> - 5.4.263-1
- Updated with the 5.4.263 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.263]

* Wed Nov 29 2023 S.Tindall <s10dal@elrepo.org> - 5.4.262-1
- Updated with the 5.4.262 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.262]

* Mon Nov 20 2023 S.Tindall <s10dal@elrepo.org> - 5.4.261-1
- Updated with the 5.4.261 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.261]

* Wed Nov 08 2023 S.Tindall <s10dal@elrepo.org> - 5.4.260-1
- Updated with the 5.4.260 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.260]

* Wed Oct 25 2023 Akemi Yagi <toracat@elrepo.org> - 5.4.259-1
- Updated with the 5.4.259 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.259]

* Tue Oct 10 2023 S.Tindall <s10dal@elrepo.org> - 5.4.258-1
- Updated with the 5.4.258 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.258]

* Sat Sep 23 2023 S.Tindall <s10dal@elrepo.org> - 5.4.257-1
- Updated with the 5.4.257 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.257]

* Sat Sep 02 2023 Akemi Yagi <toracat@elrepo.org> - 5.4.256-1
- Updated with the 5.4.256 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.256]

* Wed Aug 30 2023 Akemi Yagi <toracat@elrepo.org> - 5.4.255-1
- Updated with the 5.4.255 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.255]

* Wed Aug 16 2023 S.Tindall <s10dal@elrepo.org> - 5.4.254-1
- Updated with the 5.4.254 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.254]

* Fri Aug 11 2023 S.Tindall <s10dal@elrepo.org> - 5.4.253-1
- Updated with the 5.4.253 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.253]

* Tue Aug 08 2023 S.Tindall <s10dal@elrepo.org> - 5.4.252-1
- Updated with the 5.4.252 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.252]
- Added: CONFIG_ARCH_HAS_CPU_FINALIZE_INIT=y

* Thu Jul 27 2023 S.Tindall <s10dal@elrepo.org> - 5.4.251-1
- Updated with the 5.4.251 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.251]

* Mon Jul 24 2023 S.Tindall <s10dal@elrepo.org> - 5.4.250-1
- Updated with the 5.4.250 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.250]

* Wed Jun 28 2023 S.Tindall <s10dal@elrepo.org> - 5.4.249-1
- Updated with the 5.4.249 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.249]

* Wed Jun 21 2023 S.Tindall <s10dal@elrepo.org> - 5.4.248-1
- Updated with the 5.4.248 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.248]

* Wed Jun 14 2023 S.Tindall <s10dal@elrepo.org> - 5.4.247-1
- Updated with the 5.4.247 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.247]

* Fri Jun 09 2023 S.Tindall <s10dal@elrepo.org> - 5.4.246-1
- Updated with the 5.4.246 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.246]

* Wed Jun 07 2023 Akemi Yagi <toracat@elrepo.org> - 5.4.245-1.1
- Config file corrected.
  [https://elrepo.org/bugs/view.php?id=1357]

* Tue May 30 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.244-1
- Updated with the 5.4.244 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.244]

* Wed May 17 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.243-1
- Updated with the 5.4.243 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.243]

* Wed Apr 26 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.242-1
- Updated with the 5.4.242 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.242]

* Thu Apr 20 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.241-1
- Updated with the 5.4.241 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.241]
- CONFIG_EROFS_FS=m, CONFIG_EROFS_FS_XATTR=y,
- CONFIG_EROFS_FS_POSIX_ACL=y, CONFIG_EROFS_FS_SECURITY=y,
- CONFIG_EROFS_FS_ZIP=y and CONFIG_EROFS_FS_CLUSTER_PAGE_LIMIT=1
- [https://elrepo.org/bugs/view.php?id=1343]

* Wed Apr 05 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.240-1
- Updated with the 5.4.240 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.240]

* Thu Mar 30 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.239-1
- Updated with the 5.4.239 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.239]

* Wed Mar 22 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.238-1
- Updated with the 5.4.238 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.238]
- Enable the kernel-lt-tools package to provide the
- intel-speed-select binary file.
- [https://elrepo.org/bugs/view.php?id=1333]

* Fri Mar 17 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.237-1
- Updated with the 5.4.237 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.237]

* Tue Mar 14 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.236-1
- Updated with the 5.4.236 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.236]

* Sat Mar 11 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.235-1
- Updated with the 5.4.235 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.235]

* Fri Mar 03 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.234-1
- Updated with the 5.4.234 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.234]

* Sat Feb 25 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.233-1
- Updated with the 5.4.233 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.233]

* Wed Feb 22 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.232-1
- Updated with the 5.4.232 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.232]

* Sun Feb 05 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.231-1
- Updated with the 5.4.231 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.231]
- CONFIG_MEDIA_CONTROLLER_DVB=y, CONFIG_TTPCI_EEPROM=m,
- CONFIG_VIDEO_AU0828=m, CONFIG_VIDEO_AU0828_V4L2=y,
- CONFIG_VIDEO_CX231XX=m, CONFIG_VIDEO_CX231XX_ALSA=m,
- CONFIG_VIDEO_CX231XX_DVB=m, CONFIG_VIDEO_TM6000=m,
- CONFIG_VIDEO_TM6000_ALSA=m, CONFIG_VIDEO_TM6000_DVB=m,
- CONFIG_DVB_USB=m, CONFIG_DVB_USB_DIB3000MC=m, CONFIG_DVB_USB_A800=m,
- CONFIG_DVB_USB_DIBUSB_MB=m, CONFIG_DVB_USB_DIBUSB_MC=m,
- CONFIG_DVB_USB_DIB0700=m, CONFIG_DVB_USB_UMT_010=m,
- CONFIG_DVB_USB_CXUSB=m, CONFIG_DVB_USB_M920X=m,
- CONFIG_DVB_USB_DIGITV=m, CONFIG_DVB_USB_VP7045=m,
- CONFIG_DVB_USB_VP702X=m, CONFIG_DVB_USB_GP8PSK=m,
- CONFIG_DVB_USB_NOVA_T_USB2=m, CONFIG_DVB_USB_TTUSB2=m,
- CONFIG_DVB_USB_DTT200U=m, CONFIG_DVB_USB_OPERA1=m,
- CONFIG_DVB_USB_AF9005=m, CONFIG_DVB_USB_AF9005_REMOTE=m,
- CONFIG_DVB_USB_PCTV452E=m, CONFIG_DVB_USB_DW2102=m,
- CONFIG_DVB_USB_CINERGY_T2=m, CONFIG_DVB_USB_DTV5100=m,
- CONFIG_DVB_USB_AZ6027=m, CONFIG_DVB_USB_TECHNISAT_USB2=m,
- CONFIG_DVB_USB_V2=m, CONFIG_DVB_USB_AF9015=m, CONFIG_DVB_USB_AF9035=m,
- CONFIG_DVB_USB_ANYSEE=m, CONFIG_DVB_USB_AU6610=m,
- CONFIG_DVB_USB_AZ6007=m, CONFIG_DVB_USB_CE6230=m,
- CONFIG_DVB_USB_EC168=m, CONFIG_DVB_USB_GL861=m,
- CONFIG_DVB_USB_LME2510=m, CONFIG_DVB_USB_MXL111SF=m,
- CONFIG_DVB_USB_RTL28XXU=m, CONFIG_DVB_USB_DVBSKY=m,
- CONFIG_DVB_USB_ZD1301=m, CONFIG_DVB_TTUSB_BUDGET=m,
- CONFIG_DVB_TTUSB_DEC=m, CONFIG_SMS_USB_DRV=m,
- CONFIG_DVB_B2C2_FLEXCOP_USB=m, CONFIG_DVB_AS102=m,
- CONFIG_MEDIA_COMMON_OPTIONS=y, CONFIG_VIDEO_CX2341X=m,
- CONFIG_DVB_B2C2_FLEXCOP=m, CONFIG_SMS_SIANO_MDTV=m,
- CONFIG_VIDEO_CX25840=m, CONFIG_MEDIA_TUNER_TDA18250=m,
- CONFIG_MEDIA_TUNER_MT2063=m, CONFIG_MEDIA_TUNER_MT2266=m,
- CONFIG_MEDIA_TUNER_MXL5005S=m, CONFIG_MEDIA_TUNER_MXL5007T=m,
- CONFIG_MEDIA_TUNER_MAX2165=m, CONFIG_MEDIA_TUNER_TDA18218=m,
- CONFIG_MEDIA_TUNER_FC0011=m, CONFIG_MEDIA_TUNER_FC0012=m,
- CONFIG_MEDIA_TUNER_FC0013=m, CONFIG_MEDIA_TUNER_E4000=m,
- CONFIG_MEDIA_TUNER_FC2580=m, CONFIG_MEDIA_TUNER_TUA9001=m,
- CONFIG_MEDIA_TUNER_IT913X=m, CONFIG_MEDIA_TUNER_R820T=m,
- CONFIG_DVB_STB0899=m, CONFIG_DVB_STB6100=m, CONFIG_DVB_STV090x=m,
- CONFIG_DVB_STV6110x=m, CONFIG_DVB_SI2165=m, CONFIG_DVB_MN88472=m,
- CONFIG_DVB_MN88473=m, CONFIG_DVB_CX24123=m, CONFIG_DVB_MT312=m,
- CONFIG_DVB_ZL10039=m, CONFIG_DVB_S5H1420=m, CONFIG_DVB_STV0288=m,
- CONFIG_DVB_STB6000=m, CONFIG_DVB_STV0299=m, CONFIG_DVB_STV6110=m,
- CONFIG_DVB_STV0900=m, CONFIG_DVB_TDA8083=m, CONFIG_DVB_TDA10086=m,
- CONFIG_DVB_TUNER_ITD1000=m, CONFIG_DVB_TUNER_CX24113=m,
- CONFIG_DVB_TDA826X=m, CONFIG_DVB_CX24116=m, CONFIG_DVB_CX24120=m,
- CONFIG_DVB_SI21XX=m, CONFIG_DVB_DS3000=m, CONFIG_DVB_CX22700=m,
- CONFIG_DVB_CX22702=m, CONFIG_DVB_TDA1004X=m, CONFIG_DVB_NXT6000=m,
- CONFIG_DVB_DIB3000MB=m, CONFIG_DVB_DIB3000MC=m,
- CONFIG_DVB_DIB7000M=m, CONFIG_DVB_DIB7000P=m,
- CONFIG_DVB_TDA10048=m, CONFIG_DVB_AF9013=m, CONFIG_DVB_EC100=m,
- CONFIG_DVB_CXD2841ER=m, CONFIG_DVB_RTL2830=m, CONFIG_DVB_RTL2832=m,
- CONFIG_DVB_AS102_FE=m, CONFIG_DVB_ZD1301_DEMOD=m,
- CONFIG_DVB_GP8PSK_FE=m, CONFIG_DVB_VES1820=m, CONFIG_DVB_STV0297=m,
- CONFIG_DVB_NXT200X=m, CONFIG_DVB_BCM3510=m, CONFIG_DVB_LG2160=m,
- CONFIG_DVB_AU8522=m, CONFIG_DVB_AU8522_DTV=m,
- CONFIG_DVB_AU8522_V4L=m, CONFIG_DVB_S5H1411=m,
- CONFIG_DVB_DIB8000=m, CONFIG_DVB_PLL=m, CONFIG_DVB_TUNER_DIB0070=m,
- CONFIG_DVB_TUNER_DIB0090=m, CONFIG_DVB_LNBP21=m,
- CONFIG_DVB_LNBP22=m, CONFIG_DVB_ISL6421=m, CONFIG_DVB_ISL6423=m,
- CONFIG_DVB_LGS8GXX=m, CONFIG_DVB_ATBM8830=m, CONFIG_DVB_IX2505V=m,
- CONFIG_DVB_M88RS2000=m, CONFIG_DVB_AF9033=m and CONFIG_DVB_SP2=m
- [https://elrepo.org/bugs/view.php?id=1321]
- CONFIG_NTB_NETDEV=m, CONFIG_NTB=m, CONFIG_NTB_MSI=y, CONFIG_NTB_AMD=m,
- CONFIG_NTB_INTEL=m, CONFIG_NTB_PINGPONG=m, CONFIG_NTB_TOOL=m,
- CONFIG_NTB_PERF=m and CONFIG_NTB_TRANSPORT=m
- [https://elrepo.org/bugs/view.php?id=1322]

* Wed Jan 25 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.230-1
- Updated with the 5.4.230 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.230]

* Wed Jan 18 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.229-1
- Updated with the 5.4.229 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.229]

* Sat Dec 17 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.228-1
- Updated with the 5.4.228 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.228]

* Wed Dec 14 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.227-1
- Updated with the 5.4.227 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.227]
- CONFIG_LSM="lockdown,yama,integrity,selinux,bpf"
- [https://elrepo.org/bugs/view.php?id=1289]

* Wed Dec 07 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.226-1
- Updated with the 5.4.226 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.226]
- CONFIG_SECURITY_LOCKDOWN_LSM=y, CONFIG_SECURITY_LOCKDOWN_LSM_EARLY=y,
- CONFIG_LOCK_DOWN_KERNEL_FORCE_NONE=y and
- CONFIG_LSM="yama,integrity,selinux,bpf"
- [https://elrepo.org/bugs/view.php?id=1289]
- CONFIG_BPF_UNPRIV_DEFAULT_OFF=y, CONFIG_BPF_STREAM_PARSER=y,
- CONFIG_LWTUNNEL_BPF=y, CONFIG_BPF_KPROBE_OVERRIDE=y and
- CONFIG_TEST_BPF=m

* Fri Nov 25 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.225-1
- Updated with the 5.4.225 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.225]

* Thu Nov 10 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.224-1
- Updated with the 5.4.224 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.224]

* Fri Nov 04 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.223-1
- Updated with the 5.4.223 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.223]

* Tue Nov 01 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.222-1
- Updated with the 5.4.222 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.222]

* Sat Oct 29 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.221-1
- Updated with the 5.4.221 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.221]

* Wed Oct 26 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.220-1
- Updated with the 5.4.220 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.220]

* Tue Oct 18 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.219-1
- Updated with the 5.4.219 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.219]

* Sat Oct 15 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.218-1
- Updated with the 5.4.218 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.218]

* Fri Oct 07 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.217-1
- Updated with the 5.4.217 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.217]

* Wed Oct 05 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.216-1
- Updated with the 5.4.216 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.216]

* Wed Sep 28 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.215-1
- Updated with the 5.4.215 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.215]

* Sun Sep 18 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.214-1
- Updated with the 5.4.214 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.214]

* Thu Sep 15 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.213-1
- Updated with the 5.4.213 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.213]

* Sun Sep 04 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.212-1
- Updated with the 5.4.212 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.212]

* Thu Aug 25 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.211-1
- Updated with the 5.4.211 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.211]

* Thu Aug 11 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.210-1
- Updated with the 5.4.210 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.210]

* Wed Aug 03 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.209-1
- Updated with the 5.4.209 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.209]

* Fri Jul 29 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.208-1
- Updated with the 5.4.208 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.208]

* Thu Jul 21 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.207-1
- Updated with the 5.4.207 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.207]

* Fri Jul 15 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.206-1
- Updated with the 5.4.206 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.206]

* Wed Jul 13 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.205-1
- Updated with the 5.4.205 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.205]

* Thu Jul 07 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.204-1
- Updated with the 5.4.204 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.204]

* Sat Jul 02 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.203-1
- Updated with the 5.4.203 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.203]

* Wed Jun 29 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.202-1
- Updated with the 5.4.202 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.202]

* Sat Jun 25 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.201-1
- Updated with the 5.4.201 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.201]
- CONFIG_PSI=y and CONFIG_PSI_DEFAULT_DISABLED=y
- [https://elrepo.org/bugs/view.php?id=1239]

* Wed Jun 22 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.200-1
- Updated with the 5.4.200 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.200]

* Thu Jun 16 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.199-1
- Updated with the 5.4.199 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.199]

* Wed Jun 15 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.198-1
- Updated with the 5.4.198 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.198]

* Sun Jun 05 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.197-1
- Updated with the 5.4.197 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.197]

* Wed May 25 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.196-1
- Updated with the 5.4.196 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.196]

* Wed May 18 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.195-1
- Updated with the 5.4.195 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.195]

* Sun May 15 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.194-1
- Updated with the 5.4.194 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.194]

* Thu May 12 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.193-1
- Updated with the 5.4.193 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.193]

* Fri May 06 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.192-1
- Updated with the 5.4.192 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.192]

* Thu Apr 28 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.191-1
- Updated with the 5.4.191 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.191]

* Wed Apr 20 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.190-1
- Updated with the 5.4.190 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.190]

* Sat Apr 16 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.189-1
- Updated with the 5.4.189 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.189]

* Sun Mar 27 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.188-1
- Updated with the 5.4.188 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.188]

* Wed Mar 23 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.187-1
- Updated with the 5.4.187 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.187]

* Sat Mar 19 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.186-1
- Updated with the 5.4.186 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.186]

* Wed Mar 16 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.185-1
- Updated with the 5.4.185 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.185]

* Sat Mar 12 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.184-1
- Updated with the 5.4.184 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.184]

* Wed Mar 09 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.183-1
- Updated with the 5.4.183 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.183]

* Wed Mar 02 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.182-1
- Updated with the 5.4.182 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.182]

* Wed Feb 23 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.181-1
- Updated with the 5.4.181 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.181]

* Wed Feb 16 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.180-1
- Updated with the 5.4.180 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.180]

* Fri Feb 11 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.179-1
- Updated with the 5.4.179 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.179]

* Wed Feb 09 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.178-1
- Updated with the 5.4.178 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.178]

* Sun Feb 06 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.177-1
- Updated with the 5.4.177 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.177]

* Wed Feb 02 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.176-1
- Updated with the 5.4.176 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.176]

* Sat Jan 29 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.175-1
- Updated with the 5.4.175 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.175]

* Wed Jan 26 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.174-1
- Updated with the 5.4.174 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.174]
- CONFIG_DRM_VBOXVIDEO=m [https://elrepo.org/bugs/view.php?id=1190]
- CONFIG_DRM_XEN=y and CONFIG_DRM_XEN_FRONTEND=m
- [https://elrepo.org/bugs/view.php?id=1192]

* Thu Jan 20 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.173-1
- Updated with the 5.4.173 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.173]

* Sun Jan 16 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.172-1
- Updated with the 5.4.172 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.172]
- CONFIG_ORANGEFS_FS=m [https://elrepo.org/bugs/view.php?id=1184]

* Wed Jan 12 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.171-1
- Updated with the 5.4.171 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.171]

* Thu Jan 06 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.170-1
- Updated with the 5.4.170 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.170]

* Wed Dec 29 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.169-1
- Updated with the 5.4.169 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.169]

* Wed Dec 22 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.168-1
- Updated with the 5.4.168 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.168]

* Fri Dec 17 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.167-1
- Updated with the 5.4.167 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.167]

* Thu Dec 16 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.166-1
- Updated with the 5.4.166 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.166]

* Wed Dec 15 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.165-1
- Updated with the 5.4.165 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.165]

* Wed Dec 08 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.164-1
- Updated with the 5.4.164 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.164]

* Wed Dec 01 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.163-1
- Updated with the 5.4.163 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.163]

* Fri Nov 26 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.162-1
- Updated with the 5.4.162 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.162]

* Sun Nov 21 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.161-1
- Updated with the 5.4.161 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.161]

* Thu Nov 18 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.160-1
- Updated with the 5.4.160 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.160]

* Fri Nov 12 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.159-1
- Updated with the 5.4.159 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.159]

* Sat Nov 06 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.158-1
- Updated with the 5.4.158 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.158]

* Wed Nov 03 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.157-1
- Updated with the 5.4.157 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.157]

* Wed Oct 27 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.156-1
- Updated with the 5.4.156 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.156]

* Wed Oct 20 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.155-1
- Updated with the 5.4.155 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.155]

* Sat Oct 16 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.154-1
- Updated with the 5.4.154 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.154]

* Wed Oct 13 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.153-1
- Updated with the 5.4.153 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.153]

* Sun Oct 10 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.152-1
- Updated with the 5.4.152 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.152]

* Thu Oct 07 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.151-1
- Updated with the 5.4.151 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.151]

* Wed Sep 29 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.150-1
- Updated with the 5.4.150 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.150]

* Mon Sep 27 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.149-1
- Updated with the 5.4.149 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.149]

* Wed Sep 22 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.148-1
- Updated with the 5.4.148 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.148]

* Thu Sep 16 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.147-1
- Updated with the 5.4.147 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.147]

* Wed Sep 15 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.146-1
- Updated with the 5.4.146 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.146]

* Sun Sep 12 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.145-1
- Updated with the 5.4.145 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.145]

* Fri Sep 03 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.144-1
- Updated with the 5.4.144 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.144]
- CONFIG_MODULE_SIG_FORMAT=y, CONFIG_MODULE_SIG=y,
- CONFIG_MODULE_SIG_ALL=y, CONFIG_MODULE_SIG_SHA512=y,
- CONFIG_MODULE_SIG_HASH="sha512", CONFIG_IMA_DEFAULT_HASH_SHA512=y,
- CONFIG_IMA_DEFAULT_HASH="sha512", CONFIG_CRYPTO_FIPS=y,
- CONFIG_CRYPTO_SHA512=y and CONFIG_MODULE_SIG_KEY="certs/signing_key.pem"
- [https://elrepo.org/bugs/view.php?id=1127]
- [https://elrepo.org/bugs/view.php?id=1129]

* Thu Aug 26 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.143-1
- Updated with the 5.4.143 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.143]

* Wed Aug 18 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.142-1
- Updated with the 5.4.142 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.142]

* Sun Aug 15 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.141-1
- Updated with the 5.4.141 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.141]

* Thu Aug 12 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.140-1
- Updated with the 5.4.140 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.140]

* Sun Aug 08 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.139-1
- Updated with the 5.4.139 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.139]

* Wed Aug 04 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.138-1
- Updated with the 5.4.138 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.138]

* Sat Jul 31 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.137-1
- Updated with the 5.4.137 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.137]

* Wed Jul 28 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.136-1
- Updated with the 5.4.136 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.136]

* Sat Jul 24 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.135-1
- Updated with the 5.4.135 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.135]

* Wed Jul 21 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.134-1
- Updated with the 5.4.134 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.134]

* Wed Jul 21 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.133-1
- Updated with the 5.4.133 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.133]

* Wed Jul 14 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.132-1
- Updated with the 5.4.132 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.132]

* Sun Jul 11 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.131-1
- Updated with the 5.4.131 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.131]

* Wed Jul 07 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.130-1
- Updated with the 5.4.130 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.130]

* Wed Jun 30 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.129-1
- Updated with the 5.4.129 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.129]

* Wed Jun 23 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.128-1
- Updated with the 5.4.128 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.128]

* Fri Jun 18 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.127-1
- Updated with the 5.4.127 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.127]

* Wed Jun 16 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.126-1
- Updated with the 5.4.126 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.126]

* Thu Jun 10 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.125-1
- Updated with the 5.4.125 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.125]

* Wed Jun 02 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.124-1
- Updated with the 5.4.124 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.124]

* Sat May 29 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.123-1
- Updated with the 5.4.123 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.123]

* Wed May 26 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.122-1
- Updated with the 5.4.122 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.122]

* Sat May 22 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.121-1
- Updated with the 5.4.121 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.121]

* Wed May 19 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.120-1
- Updated with the 5.4.120 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.120]

* Fri May 14 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.119-1
- Updated with the 5.4.119 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.119]

* Wed May 12 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.118-1
- Updated with the 5.4.118 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.118]

* Fri May 07 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.117-1
- Updated with the 5.4.117 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.117]
- CONFIG_HSA_AMD=y [https://elrepo.org/bugs/view.php?id=1091]

* Sun May 02 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.116-1
- Updated with the 5.4.116 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.116]

* Wed Apr 28 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.115-1
- Updated with the 5.4.115 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.115]

* Wed Apr 21 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.114-1
- Updated with the 5.4.114 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.114]

* Fri Apr 16 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.113-1
- Updated with the 5.4.113 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.113]

* Wed Apr 14 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.112-1
- Updated with the 5.4.112 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.112]

* Sun Apr 11 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.111-1
- Updated with the 5.4.111 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.111]

* Wed Apr 07 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.110-1
- Updated with the 5.4.110 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.110]
- CONFIG_SND_SOC_INTEL_SOF_RT5682_MACH=m,
- CONFIG_SND_SOC_INTEL_CML_LP_DA7219_MAX98357A_MACH=m,
- CONFIG_SND_SOC_SOF_TOPLEVEL=y, CONFIG_SND_SOC_SOF_PCI=m,
- CONFIG_SND_SOC_SOF_ACPI=m, CONFIG_SND_SOC_SOF_OPTIONS=m,
- CONFIG_SND_SOC_SOF=m, CONFIG_SND_SOC_SOF_PROBE_WORK_QUEUE=y,
- CONFIG_SND_SOC_SOF_INTEL_TOPLEVEL=y, CONFIG_SND_SOC_SOF_INTEL_ACPI=m,
- CONFIG_SND_SOC_SOF_INTEL_PCI=m, CONFIG_SND_SOC_SOF_INTEL_HIFI_EP_IPC=m,
- CONFIG_SND_SOC_SOF_INTEL_ATOM_HIFI_EP=m, CONFIG_SND_SOC_SOF_INTEL_COMMON=m,
- CONFIG_SND_SOC_SOF_BAYTRAIL_SUPPORT=y, CONFIG_SND_SOC_SOF_BAYTRAIL=m,
- CONFIG_SND_SOC_SOF_MERRIFIELD_SUPPORT=y, CONFIG_SND_SOC_SOF_MERRIFIELD=m,
- CONFIG_SND_SOC_SOF_APOLLOLAKE_SUPPORT=y, CONFIG_SND_SOC_SOF_APOLLOLAKE=m,
- CONFIG_SND_SOC_SOF_GEMINILAKE_SUPPORT=y, CONFIG_SND_SOC_SOF_GEMINILAKE=m,
- CONFIG_SND_SOC_SOF_CANNONLAKE_SUPPORT=y, CONFIG_SND_SOC_SOF_CANNONLAKE=m,
- CONFIG_SND_SOC_SOF_COFFEELAKE_SUPPORT=y, CONFIG_SND_SOC_SOF_COFFEELAKE=m,
- CONFIG_SND_SOC_SOF_ICELAKE_SUPPORT=y, CONFIG_SND_SOC_SOF_ICELAKE=m,
- CONFIG_SND_SOC_SOF_COMETLAKE_LP=m, CONFIG_SND_SOC_SOF_COMETLAKE_LP_SUPPORT=y,
- CONFIG_SND_SOC_SOF_COMETLAKE_H=m, CONFIG_SND_SOC_SOF_COMETLAKE_H_SUPPORT=y,
- CONFIG_SND_SOC_SOF_TIGERLAKE_SUPPORT=y, CONFIG_SND_SOC_SOF_TIGERLAKE=m,
- CONFIG_SND_SOC_SOF_ELKHARTLAKE_SUPPORT=y, CONFIG_SND_SOC_SOF_ELKHARTLAKE=m,
- CONFIG_SND_SOC_SOF_HDA_COMMON=m, CONFIG_SND_SOC_SOF_HDA_LINK=y,
- CONFIG_SND_SOC_SOF_HDA_AUDIO_CODEC=y, CONFIG_SND_SOC_SOF_HDA_LINK_BASELINE=m,
- CONFIG_SND_SOC_SOF_HDA=m and CONFIG_SND_SOC_SOF_XTENSA=m
- [https://elrepo.org/bugs/view.php?id=1086]

* Wed Mar 31 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.109-1
- Updated with the 5.4.109 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.109]

* Wed Mar 24 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.108-1
- Updated with the 5.4.108 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.108]

* Sun Mar 21 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.107-1
- Updated with the 5.4.107 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.107]

* Fri Mar 19 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.106-1
- Updated with the 5.4.106 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.106]

* Fri Mar 12 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.105-1
- Updated with the 5.4.105 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.105]

* Wed Mar 10 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.104-1
- Updated with the 5.4.104 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.104]

* Sun Mar 07 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.103-1
- Updated with the 5.4.103 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.103]

* Thu Mar 04 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.102-1
- Updated with the 5.4.102 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.102]

* Sat Feb 27 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.101-1
- Updated with the 5.4.101 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.101]

* Wed Feb 24 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.100-1
- Updated with the 5.4.100 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.100]

* Wed Feb 17 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.99-1
- Updated with the 5.4.99 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.99]

* Sat Feb 13 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.98-1
- Updated with the 5.4.98 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.98]

* Wed Feb 10 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.97-1
- Updated with the 5.4.97 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.97]

* Sun Feb 07 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.96-1
- Updated with the 5.4.96 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.96]

* Thu Feb 04 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.95-1
- Updated with the 5.4.95 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.95]

* Sun Jan 31 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.94-1
- Updated with the 5.4.94 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.94]

* Thu Jan 28 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.93-1
- Updated with the 5.4.93 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.93]

* Sun Jan 24 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.92-1
- Updated with the 5.4.92 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.92]

* Wed Jan 20 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.91-1
- Updated with the 5.4.91 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.91]

* Sun Jan 17 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.90-1
- Updated with the 5.4.90 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.90]

* Wed Jan 13 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.89-1
- Updated with the 5.4.89 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.89]

* Sat Jan 09 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.88-1
- Updated with the 5.4.88 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.88]

- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.87]
* Wed Jan 06 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.87-1
- Updated with the 5.4.87 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.87]
- CONFIG_BRCMFMAC_SDIO=y, CONFIG_RSI_SDIO=m,
- CONFIG_SSB_SDIOHOST_POSSIBLE=y, CONFIG_MMC=m, CONFIG_MMC_BLOCK=m,
- CONFIG_MMC_BLOCK_MINORS=8, CONFIG_SDIO_UART=m, CONFIG_MMC_SDHCI=m,
- CONFIG_MMC_SDHCI_IO_ACCESSORS=y, CONFIG_MMC_SDHCI_PCI=m,
- CONFIG_MMC_RICOH_MMC=y, CONFIG_MMC_SDHCI_ACPI=m,
- CONFIG_MMC_SDHCI_PLTFM=m, CONFIG_MMC_SDHCI_F_SDH30=m,
- CONFIG_MMC_WBSD=m, CONFIG_MMC_TIFM_SD=m, CONFIG_MMC_SPI=m,
- CONFIG_MMC_CB710=m, CONFIG_MMC_VIA_SDMMC=m, CONFIG_MMC_VUB300=m,
- CONFIG_MMC_USHC=m, CONFIG_MMC_USDHI6ROL0=m, CONFIG_MMC_REALTEK_PCI=m,
- CONFIG_MMC_REALTEK_USB=m, CONFIG_MMC_CQHCI=m, CONFIG_MMC_TOSHIBA_PCI=m,
- CONFIG_MMC_MTK=m and CONFIG_MMC_SDHCI_XENON=m
- [https://elrepo.org/bugs/view.php?id=1067]

* Fri Jan 01 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.86-1
- Reverted to the 5.4.86 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.86]
- Forked this specification file so as to create
- a kernel-lt package set for EL8.

* Thu Dec 31 2020 Alan Bartlett <ajb@elrepo.org> - 5.10.4-1
- Updated with the 5.10.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.4]

* Fri Dec 25 2020 Alan Bartlett <ajb@elrepo.org> - 5.10.3-1
- Updated with the 5.10.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.3]

* Mon Dec 21 2020 Alan Bartlett <ajb@elrepo.org> - 5.10.2-1
- Updated with the 5.10.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.2]

* Mon Dec 14 2020 Alan Bartlett <ajb@elrepo.org> - 5.10.1-1
- Updated with the 5.10.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.1]

* Sun Dec 13 2020 Alan Bartlett <ajb@elrepo.org> - 5.10.0-1
- Updated with the 5.10 source tarball.
- CONFIG_LLD_VERSION=0, CONFIG_GENERIC_IRQ_CHIP=y, CONFIG_TASKS_TRACE_RCU=y,
- CONFIG_LD_ORPHAN_WARN=y, CONFIG_ACPI_DPTF=y, CONFIG_DPTF_PCH_FIVR=m,
- CONFIG_HAVE_ARCH_SECCOMP=y, CONFIG_ISA_BUS_API=y, CONFIG_HAVE_STATIC_CALL=y,
- CONFIG_HAVE_STATIC_CALL_INLINE=y, CONFIG_ARCH_WANT_LD_ORPHAN_WARN=y,
- CONFIG_VMAP_PFN=y, CONFIG_WANT_COMPAT_NETLINK_MESSAGES=y,
- CONFIG_XFRM_USER_COMPAT=m, CONFIG_NFT_SYNPROXY=m, CONFIG_QRTR=m,
- CONFIG_QRTR_MHI=m, CONFIG_CAN_MCP251XFD=m, CONFIG_MHI_BUS=m,
- CONFIG_CHELSIO_INLINE_CRYPTO=y, CONFIG_CHELSIO_IPSEC_INLINE=m,
- CONFIG_CHELSIO_TLS_DEVICE=m, CONFIG_PRESTERA=m, CONFIG_PRESTERA_PCI=m,
- CONFIG_PCS_XPCS=m, CONFIG_ATH11K=m, CONFIG_ATH11K_PCI=m,
- CONFIG_TOUCHSCREEN_ADS7846=m, CONFIG_TOUCHSCREEN_AD7877=m,
- CONFIG_TOUCHSCREEN_AD7879=m, CONFIG_TOUCHSCREEN_AD7879_I2C=m,
- CONFIG_TOUCHSCREEN_AD7879_SPI=m, CONFIG_TOUCHSCREEN_ADC=m,
- CONFIG_TOUCHSCREEN_ATMEL_MXT=m, CONFIG_TOUCHSCREEN_AUO_PIXCIR=m,
- CONFIG_TOUCHSCREEN_BU21013=m, CONFIG_TOUCHSCREEN_BU21029=m,
- CONFIG_TOUCHSCREEN_CHIPONE_ICN8505=m, CONFIG_TOUCHSCREEN_CY8CTMA140=m,
- CONFIG_TOUCHSCREEN_CY8CTMG110=m, CONFIG_TOUCHSCREEN_CYTTSP_CORE=m,
- CONFIG_TOUCHSCREEN_CYTTSP_I2C=m, CONFIG_TOUCHSCREEN_CYTTSP_SPI=m,
- CONFIG_TOUCHSCREEN_CYTTSP4_CORE=m, CONFIG_TOUCHSCREEN_CYTTSP4_I2C=m,
- CONFIG_TOUCHSCREEN_CYTTSP4_SPI=m, CONFIG_TOUCHSCREEN_DYNAPRO=m,
- CONFIG_TOUCHSCREEN_HAMPSHIRE=m, CONFIG_TOUCHSCREEN_EETI=m,
- CONFIG_TOUCHSCREEN_EGALAX_SERIAL=m, CONFIG_TOUCHSCREEN_EXC3000=m,
- CONFIG_TOUCHSCREEN_FUJITSU=m, CONFIG_TOUCHSCREEN_GOODIX=m,
- CONFIG_TOUCHSCREEN_HIDEEP=m, CONFIG_TOUCHSCREEN_ILI210X=m,
- CONFIG_TOUCHSCREEN_S6SY761=m, CONFIG_TOUCHSCREEN_GUNZE=m,
- CONFIG_TOUCHSCREEN_EKTF2127=m, CONFIG_TOUCHSCREEN_ELAN=m,
- CONFIG_TOUCHSCREEN_MAX11801=m, CONFIG_TOUCHSCREEN_MCS5000=m,
- CONFIG_TOUCHSCREEN_MMS114=m, CONFIG_TOUCHSCREEN_MELFAS_MIP4=m,
- CONFIG_TOUCHSCREEN_MTOUCH=m, CONFIG_TOUCHSCREEN_INEXIO=m,
- CONFIG_TOUCHSCREEN_MK712=m, CONFIG_TOUCHSCREEN_PENMOUNT=m,
- CONFIG_TOUCHSCREEN_EDT_FT5X06=m, CONFIG_TOUCHSCREEN_TOUCHRIGHT=m,
- CONFIG_TOUCHSCREEN_TOUCHWIN=m, CONFIG_TOUCHSCREEN_PIXCIR=m,
- CONFIG_TOUCHSCREEN_WDT87XX_I2C=m, CONFIG_TOUCHSCREEN_WM97XX=m,
- CONFIG_TOUCHSCREEN_WM9705=y, CONFIG_TOUCHSCREEN_WM9712=y,
- CONFIG_TOUCHSCREEN_WM9713=y, CONFIG_TOUCHSCREEN_USB_COMPOSITE=m,
- CONFIG_TOUCHSCREEN_USB_EGALAX=y, CONFIG_TOUCHSCREEN_USB_PANJIT=y,
- CONFIG_TOUCHSCREEN_USB_3M=y, CONFIG_TOUCHSCREEN_USB_ITM=y,
- CONFIG_TOUCHSCREEN_USB_ETURBO=y, CONFIG_TOUCHSCREEN_USB_GUNZE=y,
- CONFIG_TOUCHSCREEN_USB_DMC_TSC10=y, CONFIG_TOUCHSCREEN_USB_IRTOUCH=y,
- CONFIG_TOUCHSCREEN_USB_IDEALTEK=y, CONFIG_TOUCHSCREEN_USB_GENERAL_TOUCH=y,
- CONFIG_TOUCHSCREEN_USB_GOTOP=y, CONFIG_TOUCHSCREEN_USB_JASTEC=y,
- CONFIG_TOUCHSCREEN_USB_ELO=y, CONFIG_TOUCHSCREEN_USB_E2I=y,
- CONFIG_TOUCHSCREEN_USB_ZYTRONIC=y, CONFIG_TOUCHSCREEN_USB_ETT_TC45USB=y,
- CONFIG_TOUCHSCREEN_USB_NEXIO=y, CONFIG_TOUCHSCREEN_USB_EASYTOUCH=y,
- CONFIG_TOUCHSCREEN_TOUCHIT213=m, CONFIG_TOUCHSCREEN_TSC_SERIO=m,
- CONFIG_TOUCHSCREEN_TSC200X_CORE=m, CONFIG_TOUCHSCREEN_TSC2004=m,
- CONFIG_TOUCHSCREEN_TSC2005=m, CONFIG_TOUCHSCREEN_TSC2007=m,
- CONFIG_TOUCHSCREEN_RM_TS=m, CONFIG_TOUCHSCREEN_SILEAD=m,
- CONFIG_TOUCHSCREEN_SIS_I2C=m, CONFIG_TOUCHSCREEN_ST1232=m,
- CONFIG_TOUCHSCREEN_STMFTS=m, CONFIG_TOUCHSCREEN_SUR40=m,
- CONFIG_TOUCHSCREEN_SURFACE3_SPI=m, CONFIG_TOUCHSCREEN_SX8654=m,
- CONFIG_TOUCHSCREEN_TPS6507X=m, CONFIG_TOUCHSCREEN_ZET6223=m,
- CONFIG_TOUCHSCREEN_ZFORCE=m, CONFIG_TOUCHSCREEN_ROHM_BU21023=m,
- CONFIG_TOUCHSCREEN_IQS5XX=m, CONFIG_TOUCHSCREEN_ZINITIX=m,
- CONFIG_RMI4_F3A=y, CONFIG_SERIO_PCIPS2=m, CONFIG_SERIO_PS2MULT=m,
- CONFIG_SERIO_GPIO_PS2=m, CONFIG_USERIO=m, CONFIG_GAMEPORT=m,
- CONFIG_GAMEPORT_NS558=m, CONFIG_GAMEPORT_L4=m, CONFIG_GAMEPORT_EMU10K1=m,
- CONFIG_GAMEPORT_FM801=m, CONFIG_HW_RANDOM_XIPHERA=m, CONFIG_PINCTRL_INTEL=y,
- CONFIG_GPIO_CDEV=y, CONFIG_GPIO_CDEV_V1=y, CONFIG_GPIO_MAX730X=m,
- CONFIG_GPIO_DWAPB=m, CONFIG_GPIO_EXAR=m, CONFIG_GPIO_GENERIC_PLATFORM=m,
- CONFIG_GPIO_MB86S7X=m, CONFIG_GPIO_VX855=m, CONFIG_GPIO_XILINX=m,
- CONFIG_GPIO_AMD_FCH=m, CONFIG_GPIO_F7188X=m, CONFIG_GPIO_IT87=m,
- CONFIG_GPIO_SCH=m, CONFIG_GPIO_SCH311X=m, CONFIG_GPIO_WINBOND=m,
- CONFIG_GPIO_WS16C48=m, CONFIG_GPIO_ADP5588=m, CONFIG_GPIO_MAX7300=m,
- CONFIG_GPIO_MAX732X=m, CONFIG_GPIO_PCA953X=m, CONFIG_GPIO_PCA9570=m,
- CONFIG_GPIO_PCF857X=m, CONFIG_GPIO_TPIC2810=m, CONFIG_GPIO_AMD8111=m,
- CONFIG_GPIO_BT8XX=m, CONFIG_GPIO_ML_IOH=m, CONFIG_GPIO_PCI_IDIO_16=m,
- CONFIG_GPIO_PCIE_IDIO_24=m, CONFIG_GPIO_RDC321X=m, CONFIG_GPIO_MAX3191X=m,
- CONFIG_GPIO_MAX7301=m, CONFIG_GPIO_MC33880=m, CONFIG_GPIO_PISOSR=m,
- CONFIG_GPIO_XRA1403=m, CONFIG_GPIO_AGGREGATOR=m, CONFIG_SENSORS_HIH6130=m,
- CONFIG_SENSORS_IIO_HWMON=m, CONFIG_SENSORS_POWR1220=m, CONFIG_SENSORS_MR75203=m,
- CONFIG_SENSORS_ADM1266=m, CONFIG_SENSORS_MP2975=m, CONFIG_MFD_RDC321X=m,
- CONFIG_REGULATOR_FIXED_VOLTAGE=m, CONFIG_REGULATOR_VIRTUAL_CONSUMER=m,
- CONFIG_REGULATOR_USERSPACE_CONSUMER=m, CONFIG_REGULATOR_88PG86X=m,
- CONFIG_REGULATOR_ACT8865=m, CONFIG_REGULATOR_AD5398=m, CONFIG_REGULATOR_DA9210=m,
- CONFIG_REGULATOR_DA9211=m, CONFIG_REGULATOR_FAN53555=m, CONFIG_REGULATOR_GPIO=m,
- CONFIG_REGULATOR_ISL9305=m, CONFIG_REGULATOR_ISL6271A=m, CONFIG_REGULATOR_LP3971=m,
- CONFIG_REGULATOR_LP3972=m, CONFIG_REGULATOR_LP872X=m, CONFIG_REGULATOR_LP8755=m,
- CONFIG_REGULATOR_LTC3589=m, CONFIG_REGULATOR_LTC3676=m, CONFIG_REGULATOR_MAX1586=m,
- CONFIG_REGULATOR_MAX8649=m, CONFIG_REGULATOR_MAX8660=m, CONFIG_REGULATOR_MAX8952=m,
- CONFIG_REGULATOR_MAX77826=m, CONFIG_REGULATOR_MP8859=m, CONFIG_REGULATOR_MT6311=m,
- CONFIG_REGULATOR_PCA9450=m, CONFIG_REGULATOR_PFUZE100=m, CONFIG_REGULATOR_PV88060=m,
- CONFIG_REGULATOR_PV88080=m, CONFIG_REGULATOR_PV88090=m, CONFIG_REGULATOR_PWM=m,
- CONFIG_REGULATOR_RASPBERRYPI_TOUCHSCREEN_ATTINY=m, CONFIG_REGULATOR_RT4801=m,
- CONFIG_REGULATOR_RTMV20=m, CONFIG_REGULATOR_SLG51000=m, CONFIG_REGULATOR_TPS51632=m,
- CONFIG_REGULATOR_TPS62360=m, CONFIG_REGULATOR_TPS65023=m, CONFIG_REGULATOR_TPS6507X=m,
- CONFIG_REGULATOR_TPS65132=m, CONFIG_REGULATOR_TPS6524X=m, CONFIG_VIDEOBUF2_DMA_SG=m,
- CONFIG_DRM_AMD_DC_DCN3_0=y, CONFIG_DRM_AMD_DC_HDCP=y, CONFIG_DRM_AMD_DC_SI=y,
- CONFIG_BACKLIGHT_KTD253=m, CONFIG_SND_SOC_INTEL_CATPT=m,
- CONFIG_SND_SOC_INTEL_SKYLAKE_HDAUDIO_CODEC=y,
- CONFIG_SND_SOC_INTEL_SKL_HDA_DSP_GENERIC_MACH=m,
- CONFIG_SND_SOC_CS4234=m, CONFIG_SND_SOC_HDAC_HDA=m, CONFIG_SND_SOC_TAS2764=m,
- CONFIG_HID_ACCUTOUCH=m, CONFIG_HID_ACRUX=m, CONFIG_HID_ACRUX_FF=y, CONFIG_HID_ASUS=m,
- CONFIG_HID_BIGBEN_FF=m, CONFIG_HID_CP2112=m, CONFIG_HID_CREATIVE_SB0540=m,
- CONFIG_DRAGONRISE_FF=y, CONFIG_HID_EMS_FF=m, CONFIG_HID_GLORIOUS=m, CONFIG_HOLTEK_FF=y,
- CONFIG_HID_VIVALDI=m, CONFIG_HID_VIEWSONIC=m, CONFIG_LOGITECH_FF=y,
- CONFIG_LOGIRUMBLEPAD2_FF=y, CONFIG_LOGIG940_FF=y, CONFIG_LOGIWHEELS_FF=y,
- CONFIG_HID_MAYFLASH=m, CONFIG_PANTHERLORD_FF=y, CONFIG_HID_RETRODE=m,
- CONFIG_HID_SONY=m, CONFIG_SONY_FF=y, CONFIG_HID_STEAM=m, CONFIG_HID_STEELSERIES=m,
- CONFIG_HID_GREENASIA=m, CONFIG_GREENASIA_FF=y, CONFIG_HID_SMARTJOYPLUS=m,
- CONFIG_SMARTJOYPLUS_FF=y, CONFIG_HID_THRUSTMASTER=m, CONFIG_THRUSTMASTER_FF=y,
- CONFIG_HID_UDRAW_PS3=m, CONFIG_HID_U2FZERO=m, CONFIG_HID_WIIMOTE=m, CONFIG_HID_ZEROPLUS=m,
- CONFIG_ZEROPLUS_FF=y, CONFIG_HID_MCP2221=m, CONFIG_USB_PHY=y, CONFIG_TYPEC_TCPM=m,
- CONFIG_TYPEC_TCPCI=m, CONFIG_TYPEC_RT1711H=m, CONFIG_TYPEC_TCPCI_MAXIM=m,
- CONFIG_TYPEC_FUSB302=m, CONFIG_UCSI_CCG=m, CONFIG_TYPEC_HD3SS3220=m,
- CONFIG_TYPEC_TPS6598X=m, CONFIG_TYPEC_STUSB160X=m, CONFIG_TYPEC_MUX_PI3USB30532=m,
- CONFIG_TYPEC_MUX_INTEL_PMC=m, CONFIG_TYPEC_DP_ALTMODE=m, CONFIG_TYPEC_NVIDIA_ALTMODE=m,
- CONFIG_USB_ROLE_SWITCH=m, CONFIG_LEDS_CLASS_FLASH=m, CONFIG_LEDS_CLASS_MULTICOLOR=m,
- CONFIG_LEDS_APU=m, CONFIG_LEDS_AS3645A=m, CONFIG_LEDS_LM3532=m, CONFIG_LEDS_LM3642=m,
- CONFIG_LEDS_LM3601X=m, CONFIG_LEDS_PCA9532=m, CONFIG_LEDS_PCA9532_GPIO=y, CONFIG_LEDS_GPIO=m,
- CONFIG_LEDS_LP3952=m, CONFIG_LEDS_LP50XX=m, CONFIG_LEDS_PCA955X=m, CONFIG_LEDS_PCA955X_GPIO=y,
- CONFIG_LEDS_PCA963X=m, CONFIG_LEDS_DAC124S085=m, CONFIG_LEDS_PWM=m, CONFIG_LEDS_REGULATOR=m,
- CONFIG_LEDS_BD2802=m, CONFIG_LEDS_TCA6507=m, CONFIG_LEDS_TLC591XX=m, CONFIG_LEDS_LM355x=m,
- CONFIG_LEDS_MLXREG=m, CONFIG_LEDS_USER=m, CONFIG_LEDS_NIC78BX=m, CONFIG_LEDS_SGM3140=m,
- CONFIG_LEDS_TRIGGER_ACTIVITY=m, CONFIG_LEDS_TRIGGER_NETDEV=m, CONFIG_LEDS_TRIGGER_PATTERN=m,
- CONFIG_RTC_DRV_RV3032=m, CONFIG_RTC_DRV_FTRTC010=m, CONFIG_RTC_DRV_HID_SENSOR_TIME=m,
- CONFIG_VIRTIO_DMA_SHARED_BUFFER=m, CONFIG_QCOM_QMI_HELPERS=m, CONFIG_EXTCON=y,
- CONFIG_IIO_BUFFER_CB=m, CONFIG_IIO_BUFFER_DMA=m, CONFIG_IIO_BUFFER_DMAENGINE=m,
- CONFIG_IIO_BUFFER_HW_CONSUMER=m, CONFIG_IIO_CONFIGFS=m, CONFIG_IIO_SW_DEVICE=m,
- CONFIG_IIO_SW_TRIGGER=m, CONFIG_IIO_TRIGGERED_EVENT=m, CONFIG_ACPI_ALS=m, CONFIG_ADJD_S311=m,
- CONFIG_ADUX1020=m, CONFIG_AL3320A=m, CONFIG_APDS9300=m, CONFIG_APDS9960=m, CONFIG_AS73211=m,
- CONFIG_BH1750=m, CONFIG_BH1780=m, CONFIG_CM32181=m, CONFIG_CM3232=m, CONFIG_CM3323=m,
- CONFIG_CM36651=m, CONFIG_GP2AP002=m, CONFIG_GP2AP020A00F=m, CONFIG_SENSORS_ISL29018=m,
- CONFIG_SENSORS_ISL29028=m, CONFIG_ISL29125=m, CONFIG_JSA1212=m, CONFIG_RPR0521=m,
- CONFIG_LTR501=m, CONFIG_LV0104CS=m, CONFIG_MAX44000=m, CONFIG_MAX44009=m, CONFIG_NOA1305=m,
- CONFIG_OPT3001=m, CONFIG_PA12203001=m, CONFIG_SI1133=m, CONFIG_SI1145=m, CONFIG_STK3310=m,
- CONFIG_ST_UVIS25=m, CONFIG_ST_UVIS25_I2C=m, CONFIG_ST_UVIS25_SPI=m, CONFIG_TCS3414=m,
- CONFIG_TCS3472=m, CONFIG_SENSORS_TSL2563=m, CONFIG_TSL2583=m, CONFIG_TSL2772=m,
- CONFIG_TSL4531=m, CONFIG_US5182D=m, CONFIG_VCNL4000=m, CONFIG_VCNL4035=m, CONFIG_VEML6030=m,
- CONFIG_VEML6070=m, CONFIG_VL6180=m, CONFIG_ZOPT2201=m, CONFIG_USB_LGM_PHY=m,
- CONFIG_BCM_KONA_USB2_PHY=m, CONFIG_PHY_PXA_28NM_HSIC=m, CONFIG_PHY_PXA_28NM_USB2=m,
- CONFIG_PHY_CPCAP_USB=m, CONFIG_PHY_INTEL_LGM_EMMC=m, CONFIG_XFS_SUPPORT_V4=y,
- CONFIG_FUSE_DAX=y, CONFIG_CRYPTO_SM2=m, CONFIG_CRYPTO_USER_API_ENABLE_OBSOLETE=y and
- CONFIG_KGDB_HONOUR_BLOCKLIST=y

* Sat Dec 12 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.14-1
- Updated with the 5.9.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.14]

* Tue Dec 08 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.13-1
- Updated with the 5.9.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.13]

* Thu Dec 03 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.12-1
- Updated with the 5.9.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.12]

* Tue Nov 24 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.11-1
- Updated with the 5.9.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.11]

* Sun Nov 22 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.10-1
- Updated with the 5.9.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.10]

* Thu Nov 19 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.9-1
- Updated with the 5.9.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.9]

* Wed Nov 11 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.8-1
- Updated with the 5.9.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.8]

* Tue Nov 10 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.7-1
- Updated with the 5.9.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.7]

* Thu Nov 05 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.6-1
- Updated with the 5.9.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.6]

* Thu Nov 05 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.5-1
- Updated with the 5.9.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.5]

* Wed Nov 04 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.4-1
- Updated with the 5.9.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.4]

* Mon Nov 02 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.3-1
- Updated with the 5.9.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.3]

* Thu Oct 29 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.2-1
- Updated with the 5.9.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.2]

* Sun Oct 18 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.1-1
- Updated with the 5.9.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.9.1]

* Sun Oct 11 2020 Alan Bartlett <ajb@elrepo.org> - 5.9.0-1
- Updated with the 5.9 source tarball.
- CONFIG_HAVE_KERNEL_ZSTD=y, CONFIG_HAVE_POSIX_CPU_TIMERS_TASK_WORK=y,
- CONFIG_POSIX_CPU_TIMERS_TASK_WORK=y, CONFIG_RD_ZSTD=y,
- CONFIG_KVM_XFER_TO_GUEST_WORK=y, CONFIG_GENERIC_ENTRY=y,
- CONFIG_MDIO_DEVRES=y, CONFIG_MT7663_USB_SDIO_COMMON=m,
- CONFIG_WLAN_VENDOR_MICROCHIP=y, CONFIG_RTW88_8821C=m,
- CONFIG_RTW88_8821CE=m, CONFIG_HW_RANDOM_BA431=m,
- CONFIG_PINCTRL_EMMITSBURG=m, CONFIG_SENSORS_CORSAIR_CPRO=m,
- CONFIG_THERMAL_NETLINK=y, CONFIG_IR_TOY=m, CONFIG_SND_HDA_GENERIC_LEDS=y,
- CONFIG_SND_SOC_MAX98373_I2C=m, CONFIG_XILINX_ZYNQMP_DPDMA=m,
- CONFIG_MLX5_VDPA=y, CONFIG_MLX5_VDPA_NET=m,
- CONFIG_XEN_UNPOPULATED_ALLOC=y, CONFIG_STAGING=y,
- CONFIG_RTL8192U=m, CONFIG_RTLLIB=m, CONFIG_RTLLIB_CRYPTO_CCMP=m,
- CONFIG_RTLLIB_CRYPTO_TKIP=m, CONFIG_RTLLIB_CRYPTO_WEP=m,
- CONFIG_RTL8192E=m, CONFIG_R8712U=m, CONFIG_R8188EU=m,
- CONFIG_88EU_AP_MODE=y, CONFIG_RTS5208=m, CONFIG_FIREWIRE_SERIAL=m,
- CONFIG_FWTTY_MAX_TOTAL_PORTS=64, CONFIG_FWTTY_MAX_CARD_PORTS=32,
- CONFIG_PI433=m, CONFIG_QLGE=m, CONFIG_DECOMPRESS_ZSTD=y,
- CONFIG_DMA_OPS=y, CONFIG_PLDMFW=y, CONFIG_DEBUG_FS_ALLOW_ALL=y and
- CONFIG_TRACE_IRQFLAGS_NMI_SUPPORT=y

* Wed Oct 07 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.14-1
- Updated with the 5.8.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.14]

* Thu Oct 01 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.13-1
- Updated with the 5.8.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.13]

* Sun Sep 27 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.12-1
- Updated with the 5.8.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.12]

* Wed Sep 23 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.11-1
- Updated with the 5.8.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.11]

* Thu Sep 17 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.10-1
- Updated with the 5.8.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.10]

* Sat Sep 12 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.9-1
- Updated with the 5.8.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.9]
- CONFIG_MLX4_CORE_GEN2=y [https://elrepo.org/bugs/view.php?id=1037]

* Wed Sep 09 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.8-1
- Updated with the 5.8.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.8]

* Sun Sep 06 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.7-1
- Updated with the 5.8.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.7]
- CONFIG_IEEE802154_AT86RF230=m, CONFIG_IEEE802154_MRF24J40=m,
- CONFIG_IEEE802154_CC2520=m, CONFIG_IEEE802154_ATUSB=m,
- CONFIG_IEEE802154_ADF7242=m, CONFIG_IEEE802154_CA8210=m,
- CONFIG_IEEE802154_MCR20A=m and CONFIG_IEEE802154_HWSIM=m
- [http://lists.elrepo.org/pipermail/elrepo/2020-September/005375.html]

* Fri Sep 04 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.6-1
- Updated with the 5.8.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.6]

* Fri Aug 28 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.5-1
- Updated with the 5.8.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.5]

* Wed Aug 26 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.4-1
- Updated with the 5.8.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.4]

* Sat Aug 22 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.3-1
- Updated with the 5.8.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.3]

* Wed Aug 19 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.2-1
- Updated with the 5.8.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.2]

* Tue Aug 11 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.1-1
- Updated with the 5.8.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.1]
- CONFIG_USB4_NET=m and CONFIG_USB4=m
- [https://elrepo.org/bugs/view.php?id=1029]

* Sun Aug 02 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.0-1
- Updated with the 5.8 source tarball.
- CONFIG_CC_VERSION_TEXT="gcc (GCC) 8.3.1 20191121 (Red Hat 8.3.1-5)",
- CONFIG_DEFAULT_INIT="", CONFIG_TASKS_RCU_GENERIC=y,
- CONFIG_TASKS_RUDE_RCU=y, CONFIG_HIBERNATION_SNAPSHOT_DEV=y,
- CONFIG_EFI_GENERIC_STUB_INITRD_CMDLINE_LOADER=y,
- CONFIG_BLK_DEV_ZONED=y, CONFIG_XFRM_AH=m, CONFIG_XFRM_ESP=m,
- CONFIG_NET_ACT_GATE=m, CONFIG_MLX5_CLS_ACT=y, CONFIG_BCM54140_PHY=m,
- CONFIG_AT803X_PHY=m, CONFIG_MT7615_COMMON=m, CONFIG_MT7663U=m,
- CONFIG_MT7915E=m, CONFIG_RTW88_8822B=m, CONFIG_RTW88_8822C=m,
- CONFIG_RTW88_8723D=m, CONFIG_RTW88_8822BE=m, CONFIG_RTW88_8822CE=m,
- CONFIG_RTW88_8723DE=m, CONFIG_PINCTRL_JASPERLAKE=m,
- CONFIG_SENSORS_AXI_FAN_CONTROL=m, CONFIG_SENSORS_AMD_ENERGY=m,
- CONFIG_SENSORS_MAX16601=m, CONFIG_MFD_INTEL_PMC_BXT=m,
- CONFIG_MEDIA_SUPPORT_FILTER=y, CONFIG_MEDIA_CONTROLLER=y,
- CONFIG_DRM_I915_FENCE_TIMEOUT=10000,
- CONFIG_SND_USB_AUDIO_USE_MEDIA_CONTROLLER=y,
- CONFIG_SND_SOC_AMD_RENOIR=m, CONFIG_SND_SOC_AMD_RENOIR_MACH=m,
- CONFIG_SND_SOC_FSL_EASRC=m, CONFIG_SND_SOC_MAX98390=m,
- CONFIG_SND_SOC_ZL38060=m, CONFIG_INFINIBAND_RTRS=m,
- CONFIG_INFINIBAND_RTRS_CLIENT=m, CONFIG_INFINIBAND_RTRS_SERVER=m,
- CONFIG_VIRTIO_MEM=m, CONFIG_HUAWEI_WMI=m,
- CONFIG_INTEL_WMI_SBL_FW_UPDATE=m, CONFIG_INTEL_SCU_IPC=y,
- CONFIG_NILFS2_FS=m, CONFIG_F2FS_FS=m, CONFIG_F2FS_STAT_FS=y,
- CONFIG_F2FS_FS_XATTR=y, CONFIG_F2FS_FS_POSIX_ACL=y,
- CONFIG_F2FS_FS_SECURITY=y, CONFIG_F2FS_FS_COMPRESSION=y,
- CONFIG_F2FS_FS_LZO=y, CONFIG_F2FS_FS_LZ4=y, CONFIG_F2FS_FS_ZSTD=y,
- CONFIG_F2FS_FS_LZORLE=y, CONFIG_ZONEFS_FS=m, CONFIG_LINEAR_RANGES=y,
- CONFIG_ARCH_USE_SYM_ANNOTATIONS=y, CONFIG_LZ4_COMPRESS=y,
- CONFIG_ZSTD_COMPRESS=y, CONFIG_ZSTD_DECOMPRESS=y,
- CONFIG_DMA_COHERENT_POOL=y, CONFIG_DYNAMIC_DEBUG_CORE=y,
- CONFIG_ARCH_HAS_EARLY_DEBUG=y, CONFIG_ARCH_HAS_DEBUG_WX=y,
- CONFIG_ARCH_HAS_DEBUG_VM_PGTABLE=y,
- CONFIG_CC_HAS_WORKING_NOSANITIZE_ADDRESS=y, CONFIG_SYNTH_EVENTS=y and
- CONFIG_HAVE_ARCH_KCSAN=y

* Fri Jul 31 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.12-1
- Updated with the 5.7.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.12]

* Wed Jul 29 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.11-1
- Updated with the 5.7.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.11]

* Wed Jul 22 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.10-1
- Updated with the 5.7.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.10]

* Thu Jul 16 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.9-1
- Updated with the 5.7.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.9]
- CONFIG_USBIP_CORE=m, CONFIG_USBIP_VHCI_HCD=m,
- CONFIG_USBIP_VHCI_HC_PORTS=8, CONFIG_USBIP_VHCI_NR_HCS=1 and
- CONFIG_USBIP_HOST=m
- [https://elrepo.org/bugs/view.php?id=1020]

* Wed Jul 08 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.8-1
- Updated with the 5.7.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.8]

* Wed Jul 01 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.7-1
- Updated with the 5.7.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.7]
- Added a triggerin scriptlet to rebuild the initramfs image
- when the system microcode package is updated.
- [https://elrepo.org/bugs/view.php?id=1013]

* Thu Jun 25 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.6-1
- Updated with the 5.7.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.6]

* Mon Jun 22 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.5-1
- Updated with the 5.7.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.5]

* Thu Jun 18 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.4-1
- Updated with the 5.7.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.4]

* Wed Jun 17 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.3-1
- Updated with the 5.7.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.3]

* Thu Jun 11 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.2-1
- Updated with the 5.7.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.2]

* Sat Jun 06 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.1-1
- Updated with the 5.7.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.1]

* Sun May 31 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.0-1
- Updated with the 5.7 source tarball.
- CONFIG_LD_VERSION=230000000, CONFIG_HARDIRQS_SW_RESEND=y,
- CONFIG_HAVE_ARCH_USERFAULTFD_WP=y,
- CONFIG_CPU_FREQ_GOV_SCHEDUTIL=y, CONFIG_AS_AVX512=y,
- CONFIG_AS_SHA1_NI=y, CONFIG_AS_SHA256_NI=y,
- CONFIG_NUMA_KEEP_MEMINFO=y, CONFIG_PAGE_REPORTING=y,
- CONFIG_ZSWAP_COMPRESSOR_DEFAULT_LZO=y,
- CONFIG_ZSWAP_COMPRESSOR_DEFAULT="lzo",
- CONFIG_ZSWAP_ZPOOL_DEFAULT_ZBUD=y,
- CONFIG_ZSWAP_ZPOOL_DEFAULT="zbud", CONFIG_SATA_HOST=y,
- CONFIG_PATA_TIMINGS=y, CONFIG_ATA_FORCE=y, CONFIG_BAREUDP=m,
- CONFIG_MLX5_TC_CT=y, CONFIG_DWMAC_INTEL=m,
- CONFIG_MDIO_XPCS=m, CONFIG_SERIAL_SPRD=m,
- CONFIG_DRM_I915_MAX_REQUEST_BUSYWAIT=8000,
- CONFIG_TINYDRM_ILI9486=m, CONFIG_SND_BCM63XX_I2S_WHISTLER=m,
- CONFIG_SND_SOC_TLV320ADCX140=m, CONFIG_APPLE_MFI_FASTCHARGE=m,
- CONFIG_MMC_HSQ=m, CONFIG_VIRTIO_VDPA=m, CONFIG_VDPA=m,
- CONFIG_IFCVF=m, CONFIG_VHOST_IOTLB=m, CONFIG_VHOST_DPN=y,
- CONFIG_VHOST_MENU=y, CONFIG_VHOST_VDPA=m,
- CONFIG_SURFACE_3_POWER_OPREGION=m, CONFIG_AL3010=m,
- CONFIG_EXFAT_FS=m, CONFIG_EXFAT_DEFAULT_IOCHARSET="utf8",
- CONFIG_CHELSIO_TLS_DEVICE=y and
- CONFIG_MAGIC_SYSRQ_SERIAL_SEQUENCE=""

* Wed May 27 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.15-1
- Updated with the 5.6.15 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.15]

* Wed May 20 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.14-1
- Updated with the 5.6.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.14]

* Thu May 14 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.13-1
- Updated with the 5.6.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.13]

* Sun May 10 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.12-1
- Updated with the 5.6.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.12]

* Wed May 06 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.11-1
- Updated with the 5.6.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.11]

* Sat May 02 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.10-1
- Updated with the 5.6.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.10]

* Sat May 02 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.9-1
- Updated with the 5.6.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.9]
- CONFIG_BLK_DEV_NBD=m [https://elrepo.org/bugs/view.php?id=1007]

* Wed Apr 29 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.8-1
- Updated with the 5.6.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.8]

* Thu Apr 23 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.7-1
- Updated with the 5.6.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.7]

* Wed Apr 22 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.6-1
- Updated with the 5.6.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.6]

* Fri Apr 17 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.5-1
- Updated with the 5.6.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.5]
- CONFIG_REGULATOR=y, CONFIG_SND_DMAENGINE_PCM=m,
- CONFIG_SND_SOC_AC97_BUS=y, CONFIG_SND_SOC_GENERIC_DMAENGINE_PCM=y,
- CONFIG_SND_SOC_AMD_ACP=m, CONFIG_SND_SOC_AMD_CZ_DA7219MX98357_MACH=m,
- CONFIG_SND_SOC_AMD_CZ_RT5645_MACH=m, CONFIG_SND_SOC_AMD_ACP3x=m,
- CONFIG_SND_ATMEL_SOC=m, CONFIG_SND_DESIGNWARE_I2S=m,
- CONFIG_SND_DESIGNWARE_PCM=y, CONFIG_SND_SOC_FSL_ASRC=m,
- CONFIG_SND_SOC_FSL_SAI=m, CONFIG_SND_SOC_FSL_MQS=m,
- CONFIG_SND_SOC_FSL_AUDMIX=m, CONFIG_SND_SOC_FSL_SSI=m,
- CONFIG_SND_SOC_FSL_SPDIF=m, CONFIG_SND_SOC_FSL_ESAI=m,
- CONFIG_SND_SOC_FSL_MICFIL=m, CONFIG_SND_SOC_IMX_AUDMUX=m,
- CONFIG_SND_I2S_HI6210_I2S=m, CONFIG_SND_SOC_IMG=y,
- CONFIG_SND_SOC_IMG_I2S_IN=m, CONFIG_SND_SOC_IMG_I2S_OUT=m,
- CONFIG_SND_SOC_IMG_PARALLEL_OUT=m, CONFIG_SND_SOC_IMG_SPDIF_IN=m,
- CONFIG_SND_SOC_IMG_SPDIF_OUT=m, CONFIG_SND_SOC_IMG_PISTACHIO_INTERNAL_DAC=m,
- CONFIG_SND_SST_IPC_PCI=m, CONFIG_SND_SST_ATOM_HIFI2_PLATFORM_PCI=m,
- CONFIG_SND_SOC_MTK_BTCVSD=m, CONFIG_SND_SOC_XILINX_I2S=m,
- CONFIG_SND_SOC_XILINX_AUDIO_FORMATTER=m, CONFIG_SND_SOC_XILINX_SPDIF=m,
- CONFIG_SND_SOC_XTFPGA_I2S=m, CONFIG_ZX_TDM=m, CONFIG_SND_SOC_AC97_CODEC=m,
- CONFIG_SND_SOC_ADAU_UTILS=m, CONFIG_SND_SOC_ADAU1701=m,
- CONFIG_SND_SOC_ADAU17X1=m, CONFIG_SND_SOC_ADAU1761=m,
- CONFIG_SND_SOC_ADAU1761_I2C=m, CONFIG_SND_SOC_ADAU1761_SPI=m,
- CONFIG_SND_SOC_ADAU7002=m, CONFIG_SND_SOC_ADAU7118=m,
- CONFIG_SND_SOC_ADAU7118_HW=m, CONFIG_SND_SOC_ADAU7118_I2C=m,
- CONFIG_SND_SOC_AK4104=m, CONFIG_SND_SOC_AK4118=m, CONFIG_SND_SOC_AK4458=m,
- CONFIG_SND_SOC_AK4554=m, CONFIG_SND_SOC_AK4613=m, CONFIG_SND_SOC_AK4642=m,
- CONFIG_SND_SOC_AK5386=m, CONFIG_SND_SOC_AK5558=m, CONFIG_SND_SOC_ALC5623=m,
- CONFIG_SND_SOC_BD28623=m, CONFIG_SND_SOC_BT_SCO=m, CONFIG_SND_SOC_CS35L32=m,
- CONFIG_SND_SOC_CS35L33=m, CONFIG_SND_SOC_CS35L34=m, CONFIG_SND_SOC_CS35L35=m,
- CONFIG_SND_SOC_CS35L36=m, CONFIG_SND_SOC_CS42L42=m, CONFIG_SND_SOC_CS42L51=m,
- CONFIG_SND_SOC_CS42L51_I2C=m, CONFIG_SND_SOC_CS42L52=m,
- CONFIG_SND_SOC_CS42L56=m, CONFIG_SND_SOC_CS42L73=m, CONFIG_SND_SOC_CS4265=m,
- CONFIG_SND_SOC_CS4270=m, CONFIG_SND_SOC_CS4271=m, CONFIG_SND_SOC_CS4271_I2C=m,
- CONFIG_SND_SOC_CS4271_SPI=m, CONFIG_SND_SOC_CS42XX8=m,
- CONFIG_SND_SOC_CS42XX8_I2C=m, CONFIG_SND_SOC_CS43130=m, CONFIG_SND_SOC_CS4341=m,
- CONFIG_SND_SOC_CS4349=m, CONFIG_SND_SOC_CS53L30=m, CONFIG_SND_SOC_ES7134=m,
- CONFIG_SND_SOC_ES7241=m, CONFIG_SND_SOC_ES8328=m, CONFIG_SND_SOC_ES8328_I2C=m,
- CONFIG_SND_SOC_ES8328_SPI=m, CONFIG_SND_SOC_GTM601=m,
- CONFIG_SND_SOC_INNO_RK3036=m, CONFIG_SND_SOC_MAX98088=m,
- CONFIG_SND_SOC_MAX98504=m, CONFIG_SND_SOC_MAX9867=m, CONFIG_SND_SOC_MAX9860=m,
- CONFIG_SND_SOC_MSM8916_WCD_DIGITAL=m, CONFIG_SND_SOC_PCM1681=m,
- CONFIG_SND_SOC_PCM1789=m, CONFIG_SND_SOC_PCM1789_I2C=m, CONFIG_SND_SOC_PCM179X=m,
- CONFIG_SND_SOC_PCM179X_I2C=m, CONFIG_SND_SOC_PCM179X_SPI=m,
- CONFIG_SND_SOC_PCM186X=m, CONFIG_SND_SOC_PCM186X_I2C=m,
- CONFIG_SND_SOC_PCM186X_SPI=m, CONFIG_SND_SOC_PCM3060=m,
- CONFIG_SND_SOC_PCM3060_I2C=m, CONFIG_SND_SOC_PCM3060_SPI=m,
- CONFIG_SND_SOC_PCM3168A=m, CONFIG_SND_SOC_PCM3168A_I2C=m,
- CONFIG_SND_SOC_PCM3168A_SPI=m, CONFIG_SND_SOC_PCM512x=m,
- CONFIG_SND_SOC_PCM512x_I2C=m, CONFIG_SND_SOC_PCM512x_SPI=m,
- CONFIG_SND_SOC_RK3328=m, CONFIG_SND_SOC_RT5616=m, CONFIG_SND_SOC_RT5631=m,
- CONFIG_SND_SOC_SGTL5000=m, CONFIG_SND_SOC_SIGMADSP=m,
- CONFIG_SND_SOC_SIGMADSP_I2C=m, CONFIG_SND_SOC_SIGMADSP_REGMAP=m,
- CONFIG_SND_SOC_SIMPLE_AMPLIFIER=m, CONFIG_SND_SOC_SIRF_AUDIO_CODEC=m,
- CONFIG_SND_SOC_SPDIF=m, CONFIG_SND_SOC_SSM2305=m, CONFIG_SND_SOC_SSM2602=m,
- CONFIG_SND_SOC_SSM2602_SPI=m, CONFIG_SND_SOC_SSM2602_I2C=m,
- CONFIG_SND_SOC_STA32X=m, CONFIG_SND_SOC_STA350=m, CONFIG_SND_SOC_STI_SAS=m,
- CONFIG_SND_SOC_TAS2552=m, CONFIG_SND_SOC_TAS2562=m, CONFIG_SND_SOC_TAS2770=m,
- CONFIG_SND_SOC_TAS5086=m, CONFIG_SND_SOC_TAS571X=m, CONFIG_SND_SOC_TAS5720=m,
- CONFIG_SND_SOC_TAS6424=m, CONFIG_SND_SOC_TDA7419=m, CONFIG_SND_SOC_TFA9879=m,
- CONFIG_SND_SOC_TLV320AIC23=m, CONFIG_SND_SOC_TLV320AIC23_I2C=m,
- CONFIG_SND_SOC_TLV320AIC23_SPI=m, CONFIG_SND_SOC_TLV320AIC31XX=m,
- CONFIG_SND_SOC_TLV320AIC32X4=m, CONFIG_SND_SOC_TLV320AIC32X4_I2C=m,
- CONFIG_SND_SOC_TLV320AIC32X4_SPI=m, CONFIG_SND_SOC_TLV320AIC3X=m,
- CONFIG_SND_SOC_TSCS42XX=m, CONFIG_SND_SOC_TSCS454=m, CONFIG_SND_SOC_UDA1334=m,
- CONFIG_SND_SOC_WM8510=m, CONFIG_SND_SOC_WM8523=m, CONFIG_SND_SOC_WM8524=m,
- CONFIG_SND_SOC_WM8580=m, CONFIG_SND_SOC_WM8711=m, CONFIG_SND_SOC_WM8728=m,
- CONFIG_SND_SOC_WM8731=m, CONFIG_SND_SOC_WM8737=m, CONFIG_SND_SOC_WM8741=m,
- CONFIG_SND_SOC_WM8750=m, CONFIG_SND_SOC_WM8753=m, CONFIG_SND_SOC_WM8770=m,
- CONFIG_SND_SOC_WM8776=m, CONFIG_SND_SOC_WM8782=m, CONFIG_SND_SOC_WM8804=m,
- CONFIG_SND_SOC_WM8804_I2C=m, CONFIG_SND_SOC_WM8804_SPI=m,
- CONFIG_SND_SOC_WM8903=m, CONFIG_SND_SOC_WM8904=m, CONFIG_SND_SOC_WM8960=m,
- CONFIG_SND_SOC_WM8962=m, CONFIG_SND_SOC_WM8974=m, CONFIG_SND_SOC_WM8978=m,
- CONFIG_SND_SOC_WM8985=m, CONFIG_SND_SOC_ZX_AUD96P22=m, CONFIG_SND_SOC_MAX9759=m,
- CONFIG_SND_SOC_MT6351=m, CONFIG_SND_SOC_MT6358=m, CONFIG_SND_SOC_MT6660=m,
- CONFIG_SND_SOC_NAU8540=m, CONFIG_SND_SOC_NAU8810=m, CONFIG_SND_SOC_NAU8822=m,
- CONFIG_SND_SOC_TPA6130A2=m, CONFIG_SND_SIMPLE_CARD_UTILS=m and
- CONFIG_SND_SIMPLE_CARD=m

* Sun Apr 12 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.4-1
- Updated with the 5.6.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.4]

* Wed Apr 08 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.3-1
- Updated with the 5.6.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.3]

* Thu Apr 02 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.2-1
- Updated with the 5.6.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.2]

* Wed Apr 01 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.1-1
- Updated with the 5.6.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.1]

* Sun Mar 29 2020 Alan Bartlett <ajb@elrepo.org> - 5.6.0-1
- Updated with the 5.6.0 source tarball.
- CONFIG_BUILDTIME_TABLE_SORT=y, CONFIG_TIME_NS=y,
- CONFIG_ARCH_WANT_DEFAULT_BPF_JIT=y, CONFIG_BPF_JIT_DEFAULT_ON=y,
- CONFIG_IA32_FEAT_CTL=y, CONFIG_X86_VMX_FEATURE_NAMES=y,
- CONFIG_MMU_GATHER_TABLE_FREE=y, CONFIG_MMU_GATHER_RCU_TABLE_FREE=y,
- CONFIG_BLK_DEV_INTEGRITY_T10=m, CONFIG_NET_SCH_FQ_PIE=m,
- CONFIG_NET_SCH_ETS=m, CONFIG_VSOCKETS_LOOPBACK=m,
- CONFIG_ETHTOOL_NETLINK=y, CONFIG_WIREGUARD=m, CONFIG_BCM84881_PHY=y,
- CONFIG_ISDN_CAPI=y, CONFIG_CAPI_TRACE=y, CONFIG_SPI_PXA2XX=m,
- CONFIG_SPI_PXA2XX_PCI=m, CONFIG_PINCTRL_LYNXPOINT=m,
- CONFIG_SENSORS_ADM1177=m, CONFIG_SENSORS_DRIVETEMP=m,
- CONFIG_SENSORS_MAX31722=m, CONFIG_SENSORS_MAX31730=m,
- CONFIG_SENSORS_MAX20730=m, CONFIG_SENSORS_XDPE122=m,
- CONFIG_DRM_AMD_DC_DCN=y, CONFIG_SND_PCSP=m,
- CONFIG_SND_HDA_PREALLOC_SIZE=0,
- CONFIG_SND_SOC_INTEL_BDW_RT5650_MACH=m, CONFIG_INTEL_IDXD=m,
- CONFIG_PLX_DMA=m, CONFIG_EXTCON=m, CONFIG_NFS_DISABLE_UDP_SUPPORT=y,
- CONFIG_SECURITY_SELINUX_SIDTAB_HASH_BITS=9,
- CONFIG_SECURITY_SELINUX_SID2STR_CACHE_SIZE=256,
- CONFIG_IMA_MEASURE_ASYMMETRIC_KEYS=y, CONFIG_IMA_QUEUE_EARLY_BOOT_KEYS=y,
- CONFIG_CRYPTO_LIB_POLY1305_RSIZE=11, CONFIG_GENERIC_VDSO_TIME_NS=y and
- CONFIG_GENERIC_PTDUMP=y

* Wed Mar 25 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.13-1
- Updated with the 5.5.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.13]

* Wed Mar 25 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.12-1
- Updated with the 5.5.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.12]

* Sun Mar 22 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.11-1
- Updated with the 5.5.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.11]

* Wed Mar 18 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.10-1
- Updated with the 5.5.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.10]

* Thu Mar 12 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.9-1
- Updated with the 5.5.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.9]

* Wed Mar 04 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.8-1
- Updated with the 5.5.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.8]

* Fri Feb 28 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.7-1
- Updated with the 5.5.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.7]

* Sun Feb 23 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.6-1
- Updated with the 5.5.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.6]

* Wed Feb 19 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.5-1
- Updated with the 5.5.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.5]
- Adjustments to the PRCO lines for the kernel-ml-headers
- and kernel-ml-devel subpackages.
- [https://elrepo.org/bugs/view.php?id=991]

* Fri Feb 14 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.4-1
- Updated with the 5.5.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.4]

* Tue Feb 11 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.3-1
- Updated with the 5.5.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.3]

* Tue Feb 04 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.2-1
- Updated with the 5.5.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.2]

* Fri Jan 31 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.1-1
- Updated with the 5.5.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.1]

* Sun Jan 26 2020 Alan Bartlett <ajb@elrepo.org> - 5.5.0-1
- Updated with the 5.5.0 source tarball.
- CONFIG_IRQ_MSI_IOMMU=y, CONFIG_CC_HAS_INT128=y,
- CONFIG_X86_IOPL_IOPERM=y, CONFIG_X86_UMIP=y,
- CONFIG_BLK_CGROUP_RWSTAT=y, CONFIG_MAPPING_DIRTY_HELPERS=y,
- CONFIG_TIPC_CRYPTO=y, CONFIG_FW_CACHE=y, CONFIG_NVME_HWMON=y,
- CONFIG_DP83869_PHY=m, CONFIG_PINCTRL_TIGERLAKE=m,
- CONFIG_SENSORS_LTC2947=m, CONFIG_SENSORS_LTC2947_I2C=m,
- CONFIG_SENSORS_LTC2947_SPI=m, CONFIG_SENSORS_BEL_PFE=m,
- CONFIG_SENSORS_TMP513=m, CONFIG_DRM_TTM_DMA_PAGE_POOL=y,
- CONFIG_DRM_TTM_HELPER=m, CONFIG_DRM_I915_HEARTBEAT_INTERVAL=2500,
- CONFIG_DRM_I915_PREEMPT_TIMEOUT=640,
- CONFIG_DRM_I915_STOP_TIMEOUT=100,
- CONFIG_DRM_I915_TIMESLICE_DURATION=1, CONFIG_LCD_L4F00242T03=m,
- CONFIG_LCD_LMS283GF05=m, CONFIG_LCD_LTV350QV=m, CONFIG_LCD_ILI922X=m,
- CONFIG_LCD_ILI9320=m, CONFIG_LCD_TDO24M=m, CONFIG_LCD_VGG2432A4=m,
- CONFIG_LCD_AMS369FG06=m, CONFIG_LCD_LMS501KF03=m, CONFIG_LCD_HX8357=m,
- CONFIG_LCD_OTM3225A=m, CONFIG_BACKLIGHT_GENERIC=m,
- CONFIG_BACKLIGHT_QCOM_WLED=m, CONFIG_BACKLIGHT_SAHARA=m,
- CONFIG_BACKLIGHT_ADP8860=m, CONFIG_BACKLIGHT_ADP8870=m,
- CONFIG_BACKLIGHT_LM3630A=m, CONFIG_BACKLIGHT_LM3639=m,
- CONFIG_BACKLIGHT_LV5207LP=m, CONFIG_BACKLIGHT_BD6107=m,
- CONFIG_BACKLIGHT_ARCXCNN=m, CONFIG_SND_INTEL_NHLT=y,
- CONFIG_SND_INTEL_DSP_CONFIG=m,
- CONFIG_SND_SOC_INTEL_BXT_DA7219_MAX98357A_COMMON=m,
- CONFIG_SF_PDMA=m, CONFIG_SYSTEM76_ACPI=m, CONFIG_IOMMU_DMA=y,
- CONFIG_IO_WQ=y, CONFIG_CRYPTO_SKCIPHER=y, CONFIG_CRYPTO_SKCIPHER2=y,
- CONFIG_CRYPTO_CURVE25519=m, CONFIG_CRYPTO_CURVE25519_X86=m,
- CONFIG_CRYPTO_BLAKE2B=m, CONFIG_CRYPTO_BLAKE2S=m,
- CONFIG_CRYPTO_BLAKE2S_X86=m, CONFIG_CRYPTO_ARCH_HAVE_LIB_BLAKE2S=m,
- CONFIG_CRYPTO_LIB_BLAKE2S_GENERIC=m, CONFIG_CRYPTO_LIB_BLAKE2S=m,
- CONFIG_CRYPTO_ARCH_HAVE_LIB_CHACHA=m, CONFIG_CRYPTO_LIB_CHACHA_GENERIC=m,
- CONFIG_CRYPTO_LIB_CHACHA=m, CONFIG_CRYPTO_ARCH_HAVE_LIB_CURVE25519=m,
- CONFIG_CRYPTO_LIB_CURVE25519_GENERIC=m, CONFIG_CRYPTO_LIB_CURVE25519=m,
- CONFIG_CRYPTO_LIB_POLY1305_RSIZE=4, CONFIG_CRYPTO_ARCH_HAVE_LIB_POLY1305=m,
- CONFIG_CRYPTO_LIB_POLY1305_GENERIC=m, CONFIG_CRYPTO_LIB_POLY1305=m,
- CONFIG_CRYPTO_LIB_CHACHA20POLY1305=m, CONFIG_CRYPTO_DEV_AMLOGIC_GXL=m,
- CONFIG_MEMREGION=y, CONFIG_SYMBOLIC_ERRNAME=y,
- CONFIG_HAVE_ARCH_KASAN_VMALLOC=y,
- CONFIG_HAVE_DYNAMIC_FTRACE_WITH_DIRECT_CALLS=y and
- CONFIG_DYNAMIC_FTRACE_WITH_DIRECT_CALLS=y

* Sun Jan 26 2020 Alan Bartlett <ajb@elrepo.org> - 5.4.15-1
- Updated with the 5.4.15 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.15]

* Thu Jan 23 2020 Alan Bartlett <ajb@elrepo.org> - 5.4.14-1
- Updated with the 5.4.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.14]
- CONFIG_DVB_CORE=m, CONFIG_VIDEO_EM28XX=m, CONFIG_VIDEO_EM28XX_V4L2=m,
- CONFIG_VIDEO_EM28XX_ALSA=m, CONFIG_VIDEO_EM28XX_DVB=m and
- CONFIG_VIDEO_EM28XX_RC=m [https://elrepo.org/bugs/view.php?id=982]

* Fri Jan 17 2020 Alan Bartlett <ajb@elrepo.org> - 5.4.13-1
- Updated with the 5.4.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.13]

* Tue Jan 14 2020 Alan Bartlett <ajb@elrepo.org> - 5.4.12-1
- Updated with the 5.4.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.12]

* Sun Jan 12 2020 Alan Bartlett <ajb@elrepo.org> - 5.4.11-1
- Updated with the 5.4.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.11]

* Thu Jan 09 2020 Alan Bartlett <ajb@elrepo.org> - 5.4.10-1
- Updated with the 5.4.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.10]

* Thu Jan 09 2020 Alan Bartlett <ajb@elrepo.org> - 5.4.9-1
- Updated with the 5.4.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.9]
- CONFIG_9P_FSCACHE=y, CONFIG_9P_FS=m and CONFIG_9P_FS_POSIX_ACL=y 
- [https://elrepo.org/bugs/view.php?id=981]
- Not released due to a patch being missing from the upstream
- stable tree. [https://lkml.org/lkml/2020/1/9/363]

* Sat Jan 04 2020 Alan Bartlett <ajb@elrepo.org> - 5.4.8-1
- Updated with the 5.4.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.8]

* Tue Dec 31 2019 Alan Bartlett <ajb@elrepo.org> - 5.4.7-1
- Updated with the 5.4.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.7]

* Sat Dec 21 2019 Alan Bartlett <ajb@elrepo.org> - 5.4.6-1
- Updated with the 5.4.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.6]

* Wed Dec 18 2019 Alan Bartlett <ajb@elrepo.org> - 5.4.5-1
- Updated with the 5.4.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.5]

* Tue Dec 17 2019 Alan Bartlett <ajb@elrepo.org> - 5.4.4-1
- Updated with the 5.4.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.4]

* Fri Dec 13 2019 Alan Bartlett <ajb@elrepo.org> - 5.4.3-1
- Updated with the 5.4.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.3]

* Wed Dec 04 2019 Alan Bartlett <ajb@elrepo.org> - 5.4.2-1
- Updated with the 5.4.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.2]

* Fri Nov 29 2019 Alan Bartlett <ajb@elrepo.org> - 5.4.1-1
- Updated with the 5.4.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.1]
- CONFIG_AF_RXRPC=m, CONFIG_AF_RXRPC_IPV6=y,
- CONFIG_AF_RXRPC_DEBUG=y, CONFIG_RXKAD=y, CONFIG_AFS_FS=m,
- CONFIG_AFS_DEBUG=y, CONFIG_AFS_FSCACHE=y
- and CONFIG_AFS_DEBUG_CURSOR=y
- [https://elrepo.org/bugs/view.php?id=969]
- CONFIG_DM_CLONE=m
- [https://elrepo.org/bugs/view.php?id=970]
- CONFIG_HMM_MIRROR=y, CONFIG_DRM_AMDGPU_SI=y,
- CONFIG_DRM_AMDGPU_CIK=y and CONFIG_DRM_AMDGPU_USERPTR=y
- [https://elrepo.org/bugs/view.php?id=971]

* Mon Nov 25 2019 Alan Bartlett <ajb@elrepo.org> - 5.4.0-1
- Updated with the 5.4 source tarball.
- CONFIG_CC_HAS_ASM_INLINE=y, CONFIG_ARCH_CPUIDLE_HALTPOLL=y,
- CONFIG_HALTPOLL_CPUIDLE=y, CONFIG_HAVE_ASM_MODVERSIONS=y,
- CONFIG_ASM_MODVERSIONS=y, CONFIG_NET_TC_SKB_EXT=y,
- CONFIG_CAN_J1939=m, CONFIG_CAN_KVASER_PCIEFD=m,
- CONFIG_CAN_M_CAN_PLATFORM=m, CONFIG_CAN_M_CAN_TCAN4X5X=m,
- CONFIG_CAN_F81601=m, CONFIG_PCI_HYPERV_INTERFACE=m,
- CONFIG_MLX5_SW_STEERING=y, CONFIG_NET_VENDOR_PENSANDO=y,
- CONFIG_IONIC=m, CONFIG_ADIN_PHY=m,
- CONFIG_ATH9K_PCI_NO_EEPROM=m, CONFIG_SERIAL_8250_DWLIB=y,
- CONFIG_SENSORS_AS370=m, CONFIG_SENSORS_INSPUR_IPSPS=m,
- CONFIG_VIDEO_V4L2_I2C=y, CONFIG_MEDIA_HIDE_ANCILLARY_SUBDRV=y,
- CONFIG_DRM_MIPI_DBI=m, CONFIG_DRM_GEM_CMA_HELPER=y,
- CONFIG_DRM_KMS_CMA_HELPER=y, CONFIG_DRM_AMD_DC_DCN2_1=y,
- CONFIG_TINYDRM_HX8357D=m, CONFIG_TINYDRM_ILI9225=m,
- CONFIG_TINYDRM_ILI9341=m, CONFIG_TINYDRM_MI0283QT=m,
- CONFIG_TINYDRM_REPAPER=m, CONFIG_TINYDRM_ST7586=m,
- CONFIG_TINYDRM_ST7735R=m, CONFIG_SND_INTEL_NHLT=m,
- CONFIG_SND_SOC_INTEL_DA7219_MAX98357A_GENERIC=m,
- CONFIG_MMC_SDHCI_IO_ACCESSORS=y, CONFIG_VIRTIO_FS=m,
- CONFIG_CRYPTO_ESSIV=m, CONFIG_CRYPTO_LIB_SHA256=y,
- CONFIG_CRYPTO_LIB_AES=y, CONFIG_CRYPTO_LIB_DES=m
- and CONFIG_CRYPTO_DEV_SAFEXCEL=m

* Sun Nov 24 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.13-1
- Updated with the 5.3.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.13]

* Wed Nov 20 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.12-1
- Updated with the 5.3.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.12]
- CONFIG_BTRFS_FS=m and CONFIG_BTRFS_FS_POSIX_ACL=y
- [https://elrepo.org/bugs/view.php?id=967]

* Tue Nov 12 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.11-1
- Updated with the 5.3.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.11]
- CONFIG_X86_INTEL_TSX_MODE_OFF=y

* Sun Nov 10 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.10-1
- Updated with the 5.3.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.10]

* Wed Nov 06 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.9-1
- Updated with the 5.3.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.9]

* Tue Oct 29 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.8-1
- Updated with the 5.3.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.8]

* Thu Oct 17 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.7-1
- Updated with the 5.3.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.7]

* Fri Oct 11 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.6-1
- Updated with the 5.3.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.6]

* Tue Oct 08 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.5-1
- Updated with the 5.3.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.5]

* Sat Oct 05 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.4-1
- Updated with the 5.3.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.4]
- Note: There was no linux-5.3.3 release due to an upstream
- developer "mishap". Details can be seen via the following link:
- https://lore.kernel.org/lkml/20191001070738.GC2893807@kroah.com/
- CONFIG_XEN_BLKDEV_BACKEND=m, CONFIG_XEN_NETDEV_BACKEND=m,
- CONFIG_XEN_FBDEV_FRONTEND=m, CONFIG_XEN_BALLOON_MEMORY_HOTPLUG=y
- and CONFIG_XEN_BALLOON_MEMORY_HOTPLUG_LIMIT=512
- [https://elrepo.org/bugs/view.php?id=953]

* Tue Oct 01 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.2-1
- Updated with the 5.3.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.2]
- CONFIG_NVME_MULTIPATH=y [https://elrepo.org/bugs/view.php?id=945]

* Sat Sep 21 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.1-1
- Updated with the 5.3.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.1]

* Mon Sep 16 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.0-1
- Updated with the 5.3 source tarball.
- CONFIG_CC_CAN_LINK=y, CONFIG_X86_HV_CALLBACK_VECTOR=y,
- CONFIG_CPU_SUP_ZHAOXIN=y, CONFIG_HAVE_KVM_NO_POLL=y,
- CONFIG_HAVE_FAST_GUP=y, CONFIG_ARCH_HAS_PTE_DEVMAP=y,
- CONFIG_NFT_FLOW_OFFLOAD=m, CONFIG_NF_TABLES_BRIDGE=m,
- CONFIG_NFT_BRIDGE_META=m, CONFIG_NF_CONNTRACK_BRIDGE=m,
- CONFIG_NET_ACT_MPLS=m, CONFIG_NET_ACT_CTINFO=m,
- CONFIG_NET_ACT_CT=m, CONFIG_BT_HCIBTUSB_MTK=y,
- CONFIG_FW_LOADER_PAGED_BUF=y, CONFIG_NET_VENDOR_GOOGLE=y,
- CONFIG_GVE=m, CONFIG_XILINX_AXI_EMAC=m,
- CONFIG_MDIO_I2C=m, CONFIG_PHYLINK=m, CONFIG_SFP=m,
- CONFIG_NXP_TJA11XX_PHY=m, CONFIG_MISDN_HDLC=m,
- CONFIG_SERIAL_MCTRL_GPIO=y, CONFIG_POWER_SUPPLY_HWMON=y,
- CONFIG_SENSORS_IRPS5401=m, CONFIG_SENSORS_PXE1610=m,
- CONFIG_PROC_THERMAL_MMIO_RAPL=y, CONFIG_WATCHDOG_OPEN_TIMEOUT=0,
- CONFIG_DRM_VRAM_HELPER=m, CONFIG_DRM_AMD_DC_DCN2_0=y,
- CONFIG_DRM_AMD_DC_DSC_SUPPORT=y, CONFIG_DRM_I915_FORCE_PROBE="",
- CONFIG_DRM_I915_USERFAULT_AUTOSUSPEND=250,
- CONFIG_DRM_I915_SPIN_REQUEST=5, CONFIG_SND_SOC_INTEL_CML_H=m,
- CONFIG_SND_SOC_INTEL_CML_LP=m,
- CONFIG_SND_SOC_INTEL_BYT_CHT_CX2072X_MACH=m,
- CONFIG_SND_SOC_CX2072X=m, CONFIG_LEDS_TI_LMU_COMMON=m,
- CONFIG_RDMA_SIW=m, CONFIG_RTC_DRV_BD70528=m, CONFIG_DW_EDMA=m,
- CONFIG_DW_EDMA_PCIE=m, CONFIG_VIRTIO_PMEM=m, CONFIG_HYPERV_TIMER=y,
- CONFIG_XIAOMI_WMI=m, CONFIG_ACPI_CMPC=m, CONFIG_SAMSUNG_Q10=m,
- CONFIG_INTEL_RAPL_CORE=m, CONFIG_PROC_PID_ARCH_STATUS=y,
- CONFIG_KEYS_REQUEST_CACHE=y, CONFIG_CRYPTO_XXHASH=m,
- CONFIG_CRYPTO_LIB_ARC4=m, CONFIG_CRYPTO_DEV_ATMEL_I2C=m,
- CONFIG_CRYPTO_DEV_ATMEL_ECC=m, CONFIG_CRYPTO_DEV_ATMEL_SHA204A=m,
- CONFIG_ARCH_HAS_FORCE_DMA_UNENCRYPTED=y, CONFIG_DIMLIB=y,
- CONFIG_HAVE_GENERIC_VDSO=y and CONFIG_GENERIC_GETTIMEOFDAY=y

* Tue Sep 10 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.14-1
- Updated with the 5.2.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.14]

* Fri Sep 06 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.13-1
- Updated with the 5.2.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.13]

* Fri Sep 06 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.12-1
- Updated with the 5.2.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.12]

* Thu Aug 29 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.11-1
- Updated with the 5.2.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.11]

* Sun Aug 25 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.10-1
- Updated with the 5.2.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.10]

* Fri Aug 09 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.8-1
- Updated with the 5.2.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.8]

* Tue Aug 06 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.7-1
- Updated with the 5.2.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.7]

* Sun Aug 04 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.6-1
- Updated with the 5.2.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.6]

* Wed Jul 31 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.5-1
- Updated with the 5.2.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.5]

* Sun Jul 28 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.4-1
- Updated with the 5.2.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.4]

* Sat Jul 27 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.3-1
- Updated with the 5.2.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.3]

* Sun Jul 21 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.2-1
- Updated with the 5.2.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.2]
- General availability.

* Mon Jul 15 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.15-0.rc2
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.15]
- The second release candidate of a kernel-ml package set for EL8.

* Tue Jul 02 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.15-0.rc1
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.15]
- The first release candidate of a kernel-ml package set for EL8.
