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
%define LKAver 6.6.9

# Define the buildid, if required.
#define buildid .local

# The following build options are enabled by default.
# Use either --without <option> on your rpmbuild command line
# or force the values to 0, here, to disable them.

# kernel-ml
%define with_default      %{?_without_default:      0} %{?!_without_default:      1}
# kernel-ml-doc
%define with_doc          %{?_without_doc:          0} %{?!_without_doc:          1}
# kernel-ml-headers
%define with_headers      %{?_without_headers:      0} %{?!_without_headers:      1}
# perf
%define with_perf         %{?_without_perf:         0} %{?!_without_perf:         1}
# tools
%define with_tools        %{?_without_tools:        0} %{?!_without_tools:        1}
# bpf tool
%define with_bpftool      %{?_without_bpftool:      0} %{?!_without_bpftool:      1}
# vsdo install
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}

# Kernel-ml, devel, headers, perf, tools and bpftool.
%ifarch x86_64
%define with_doc 0
%define doc_build_fail true
%define zipmodules 1
### as of kernel-ml-6.5.4, no more bpftool -ay
%define with_bpftool 0
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

# Packages that need to be present before kernel-ml is installed
# because its %%post scripts make use of them.
%define kernel_prereq  coreutils, systemd >= 203-2, systemd-udev >= 203-2
%define initrd_prereq  dracut >= 027

Name: kernel-ml
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
BuildRequires: libtraceevent-devel
%endif
%if %{with_tools}
BuildRequires: asciidoc gettext libcap-devel libnl3-devel ncurses-devel pciutils-devel
%endif
%if %{with_bpftool}
BuildRequires: binutils-devel python3-docutils zlib-devel
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb

# Sources.
Source0: https://www.kernel.org/pub/linux/kernel/v6.x/linux-%{LKAver}.tar.xz
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
# and obsoletes for the kernel-ml package.
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
# isn't required for the kernel-ml proper to function.\
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
# This macro creates a kernel-ml-<subpackage>-devel package.
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
# This macro creates a kernel-ml-<subpackage>-modules-extra package.
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
# This macro creates a kernel-ml-<subpackage>-modules package.
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
# This macro creates a kernel-ml-<subpackage> meta package.
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
# This macro creates a kernel-ml-<subpackage>
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
# compression of the kernel-ml module files.
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

# Now ensure that the Makefile, version.h and auto.conf files have matching
# timestamps so that external modules can be built.
%{_bindir}/touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile \
    $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/uapi/linux/version.h \
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
# Generate the kernel-ml-core and kernel-ml-modules file lists.
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
# We use this for the directory lists in kernel-ml-core.
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

# Purge the kernel-ml-devel tree of leftover junk.
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
# Compute a content hash to export as Provides: kernel-ml-headers-checksum.
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
# This macro defines a %%post script for a kernel-ml package and its devel package.
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
# This macro defines a %%preun script for a kernel-ml package.
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
%{_libdir}/libcpupower.so.1
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
# This macro defines the %%files sections for the kernel-ml package
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
* Mon Jan 01 2024 S.Tindall <s10dal@elrepo.org> - 6.6.9-1
- Updated with the 6.6.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.9]

* Wed Dec 20 2023 S.Tindall <s10dal@elrepo.org> - 6.6.8-1
- Updated with the 6.6.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.8]

* Thu Dec 14 2023 S.Tindall <s10dal@elrepo.org> - 6.6.7-1
- Updated with the 6.6.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.7]

* Mon Dec 11 2023 S.Tindall <s10dal@elrepo.org> - 6.6.6-1
- Updated with the 6.6.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.6]

* Fri Dec 08 2023 S.Tindall <s10dal@elrepo.org> - 6.6.5-1
- Updated with the 6.6.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.5]

* Sun Dec 03 2023 S.Tindall <s10dal@elrepo.org> - 6.6.4-1
- Updated with the 6.6.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.4]

* Wed Nov 29 2023 S.Tindall <s10dal@elrepo.org> - 6.6.3-1
- Updated with the 6.6.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.3]

* Mon Nov 20 2023 S.Tindall <s10dal@elrepo.org> - 6.6.2-1
- Updated with the 6.6.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.2]
- CONFIG_CC_VERSION_TEXT="gcc (GCC) 8.5.0 20210514 (Red Hat 8.5.0-20)"

* Wed Nov 08 2023 S.Tindall <s10dal@elrepo.org> - 6.6.1-1
- Updated with the 6.6.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.1]

* Mon Oct 30 2023 Akemi Yagi <toracat@elrepo.org> - 6.6.0-1
- Updated with the 6.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6]

* Wed Oct 25 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.9-1
- Updated with the 6.5.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.9]

* Thu Oct 19 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.8-1
- Updated with the 6.5.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.8]

* Tue Oct 10 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.7-1
- Updated with the 6.5.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.7]

* Fri Oct 06 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.6-1
- Updated with the 6.5.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.6]
- Re-enable perf

* Sat Sep 23 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.5-1
- Updated with the 6.5.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.5]

* Tue Sep 19 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.4-1
- Updated with the 6.5.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.4]
- Disable perf (build error due to bison < 3.81)
- Disable bpftool (linker error)

* Wed Sep 13 2023 S.Tindall <s10dal@elrepo.org> - 6.5.3-1
- Updated with the 6.5.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.3]
- Removed: CONFIG_IMA_TRUSTED_KEYRING=y
- Added: CONFIG_VIDEO_CAMERA_SENSOR=y
- Added: CONFIG_VIDEO_V4L2_SUBDEV_API=y

* Wed Sep 06 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.2-1
- Updated with the 6.5.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.2]

* Sat Sep 02 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.1-1
- Updated with the 6.5.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.1]

* Sun Aug 27 2023 S.Tindall <s10dal@elrepo.org> - 6.5.0-1
- Updated with the 6.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5]
- CONFIG_CACHESTAT_SYSCALL=y
- CONFIG_CRYPTO_GENIV=y
- CONFIG_CRYPTO_SHA3=y
- CONFIG_CRYPTO_SIG2=y
- CONFIG_FB_IO_HELPERS=y
- CONFIG_FB_SYS_COPYAREA=y
- CONFIG_FB_SYS_FILLRECT=y
- CONFIG_FB_SYS_FOPS=y
- CONFIG_FB_SYS_HELPERS_DEFERRED=y
- CONFIG_FB_SYS_HELPERS=y
- CONFIG_FB_SYS_IMAGEBLIT=y
- CONFIG_GPIO_VX855=m
- CONFIG_HARDLOCKUP_DETECTOR_COUNTS_HRTIMER=y
- CONFIG_HARDLOCKUP_DETECTOR=y
- CONFIG_HAVE_FUNCTION_GRAPH_RETVAL=y
- CONFIG_HAVE_HARDLOCKUP_DETECTOR_BUDDY=y
- CONFIG_HOTPLUG_CORE_SYNC_DEAD=y
- CONFIG_HOTPLUG_CORE_SYNC_FULL=y
- CONFIG_HOTPLUG_CORE_SYNC=y
- CONFIG_HOTPLUG_PARALLEL=y
- CONFIG_HOTPLUG_SPLIT_STARTUP=y
- CONFIG_LEDS_SIEMENS_SIMATIC_IPC_APOLLOLAKE=m
- CONFIG_LEDS_SIEMENS_SIMATIC_IPC_F7188X=m
- CONFIG_LIQUIDIO_CORE=m
- CONFIG_MDIO_REGMAP=m
- CONFIG_NEED_SG_DMA_FLAGS=y
- CONFIG_PCS_LYNX=m
- CONFIG_PPPOE_HASH_BITS=4
- CONFIG_PPPOE_HASH_BITS_4=y
- CONFIG_UNACCEPTED_MEMORY=y
- CONFIG_X86_AMD_PSTATE_DEFAULT_MODE=3

* Wed Aug 23 2023 S.Tindall <s10dal@elrepo.org> - 6.4.12-1
- Updated with the 6.4.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.12]

* Wed Aug 16 2023 S.Tindall <s10dal@elrepo.org> - 6.4.11-1
- Updated with the 6.4.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.11]

* Fri Aug 11 2023 S.Tindall <s10dal@elrepo.org> - 6.4.10-1
- Updated with the 6.4.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.10]

* Tue Aug 08 2023 S.Tindall <s10dal@elrepo.org> - 6.4.9-1
- Updated with the 6.4.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.9]
- Added: CONFIG_ARCH_HAS_CPU_FINALIZE_INIT=y
- Added: CONFIG_CPU_SRSO=y

* Thu Aug 03 2023 S.Tindall <s10dal@elrepo.org> - 6.4.8-1
- Updated with the 6.4.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.8]

* Thu Jul 27 2023 S.Tindall <s10dal@elrepo.org> - 6.4.7-1
- Updated with the 6.4.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.7]

* Mon Jul 24 2023 S.Tindall <s10dal@elrepo.org> - 6.4.6-1
- Updated with the 6.4.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.6]

* Sun Jul 23 2023 S.Tindall <s10dal@elrepo.org> - 6.4.5-1
- Updated with the 6.4.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.5]

* Wed Jul 19 2023 S.Tindall <s10dal@elrepo.org> - 6.4.4-1
- Updated with the 6.4.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.4]

* Tue Jul 11 2023 S.Tindall <s10dal@elrepo.org> - 6.4.3-1
- Updated with the 6.4.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.3]
- Added: CONFIG_XEN_GRANT_DMA_OPS=y
- Added: CONFIG_XEN_VIRTIO_FORCE_GRANT=y
- Added: CONFIG_XEN_VIRTIO=y

* Wed Jul 05 2023 S.Tindall <s10dal@elrepo.org> - 6.4.2-1
- Updated with the 6.4.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.2]

* Sat Jul 01 2023 S.Tindall <s10dal@elrepo.org> - 6.4.1-1
- Updated with the 6.4.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.1]
- Added: CONFIG_LOCK_MM_AND_FIND_VMA=y

* Mon Jun 26 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.0-1
- Updated with the 6.4 source tarball.
- CONFIG_MMU_LAZY_TLB_REFCOUNT=y, CONFIG_BLK_CGROUP_PUNT_BIO=y,
- CONFIG_ARCH_WANT_OPTIMIZE_VMEMMAP=y, CONFIG_ARCH_SUPPORTS_PER_VMA_LOCK=y,
- CONFIG_PER_VMA_LOCK=y, CONFIG_NET_HANDSHAKE=y,
- CONFIG_NETFILTER_BPF_LINK=y, CONFIG_MAX_SKB_FRAGS=17,
- CONFIG_PAGE_POOL_STATS=y, CONFIG_FW_LOADER_DEBUG=y,
- CONFIG_BLKDEV_UBLK_LEGACY_OPCODES=y, CONFIG_NET_VENDOR_WANGXUN=y,
- CONFIG_LIBWX=m, CONFIG_NGBE=m, CONFIG_TXGBE=m,
- CONFIG_VIDEO_CMDLINE=y, CONFIG_DRM_SUBALLOC_HELPER=m,
- CONFIG_DRM_AMD_DC_FP=y, CONFIG_DRM_VIRTIO_GPU_KMS=y,
- CONFIG_SND_SOC_SOF_HDA_MLINK=m, CONFIG_USB_USS720=m,
- CONFIG_VHOST_TASK=y, CONFIG_XFS_SUPPORT_ASCII_CI=y,
- CONFIG_SMBFS=m, CONFIG_CRYPTO_DEV_NITROX=m and
- CONFIG_CRYPTO_DEV_NITROX_CNN55XX=m, CONFIG_HAS_IOPORT=y

* Wed Jun 21 2023 S.Tindall <s10dal@elrepo.org> - 6.3.9-1
- Updated with the 6.3.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.9]

* Wed Jun 14 2023 S.Tindall <s10dal@elrepo.org> - 6.3.8-1
- Updated with the 6.3.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.8]

* Fri Jun 09 2023 S.Tindall <s10dal@elrepo.org> - 6.3.7-1
- Updated with the 6.3.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.7]

* Mon Jun 05 2023 Akemi Yagi <toracat@elrepo.org> - 6.3.6-1
- Updated with the 6.3.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.6]

* Tue May 30 2023 Alan Bartlett <ajb@elrepo.org> - 6.3.5-1
- Updated with the 6.3.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.5]

* Wed May 24 2023 Alan Bartlett <ajb@elrepo.org> - 6.3.4-1
- Updated with the 6.3.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.4]

* Wed May 17 2023 Alan Bartlett <ajb@elrepo.org> - 6.3.3-1
- Updated with the 6.3.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.3]

* Wed May 10 2023 Alan Bartlett <ajb@elrepo.org> - 6.3.2-1
- Updated with the 6.3.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.2]

* Thu May 04 2023 Alan Bartlett <ajb@elrepo.org> - 6.3.1-2
- CONFIG_DEBUG_INFO_NONE=y
- Reverted all other configuration changes.
- [https://elrepo.org/bugs/view.php?id=1320]

* Sun Apr 30 2023 Alan Bartlett <ajb@elrepo.org> - 6.3.1-1
- Updated with the 6.3.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.1]
- CONFIG_DEBUG_INFO=y, CONFIG_DEBUG_INFO_DWARF4=y,
- CONFIG_DEBUG_INFO_COMPRESSED_NONE=y, CONFIG_DEBUG_INFO_BTF=y,
- CONFIG_PAHOLE_HAS_SPLIT_BTF=y, CONFIG_DEBUG_INFO_BTF_MODULES=y and
- CONFIG_MODULE_ALLOW_BTF_MISMATCH=y
- [https://elrepo.org/bugs/view.php?id=1320]

* Sun Apr 23 2023 Alan Bartlett <ajb@elrepo.org> - 6.3.0-1
- Updated with the 6.3 source tarball.
- CONFIG_SCHED_MM_CID=y, CONFIG_CPU_IDLE_GOV_HALTPOLL=y,
- CONFIG_KVM_GENERIC_HARDWARE_ENABLING=y, CONFIG_AS_GFNI=y,
- CONFIG_ZSMALLOC_CHAIN_SIZE=8, CONFIG_NF_CONNTRACK_OVS=y,
- CONFIG_NET_SCH_MQPRIO_LIB=m, CONFIG_NCN26000_PHY=m,
- CONFIG_ATH12K=m, CONFIG_SERIAL_8250_PCILIB=y,
- CONFIG_SERIAL_8250_PCI1XXXX=y, CONFIG_SENSORS_MC34VR500=m,
- CONFIG_SENSORS_LTC2978_REGULATOR=y,
- CONFIG_SENSORS_MPQ7932_REGULATOR=y, CONFIG_SENSORS_MPQ7932=m,
- CONFIG_SENSORS_TDA38640=m, CONFIG_SENSORS_TDA38640_REGULATOR=y,
- CONFIG_SENSORS_XDPE122_REGULATOR=y, CONFIG_THERMAL_ACPI=y,
- CONFIG_INTEL_TCC=y, CONFIG_REGULATOR_MAX20411=m,
- CONFIG_UVC_COMMON=m, CONFIG_BACKLIGHT_KTZ8866=m,
- CONFIG_SND_SOC_AW88395_LIB=m, CONFIG_SND_SOC_AW88395=m,
- CONFIG_SND_SOC_IDT821034=m, CONFIG_SND_SOC_PEB2466=m,
- CONFIG_SND_SOC_SMA1303=m, CONFIG_HID_SUPPORT=y,
- CONFIG_HID_EVISION=m, CONFIG_I2C_HID=y,
- CONFIG_TYPEC_MUX_GPIO_SBU=m, CONFIG_XILINX_XDMA=m,
- CONFIG_SNET_VDPA=m, CONFIG_INTEL_IOMMU_PERF_EVENTS=y,
- CONFIG_IDLE_INJECT=y, CONFIG_LEGACY_DIRECT_IO=y,
- CONFIG_EROFS_FS_PCPU_KTHREAD=y,
- CONFIG_RPCSEC_GSS_KRB5_CRYPTOSYSTEM=y,
- CONFIG_RPCSEC_GSS_KRB5_ENCTYPES_AES_SHA1=y,
- CONFIG_CRYPTO_ARIA_AESNI_AVX2_X86_64=m and
- CONFIG_CRYPTO_ARIA_GFNI_AVX512_X86_64=m

* Thu Apr 20 2023 Alan Bartlett <ajb@elrepo.org> - 6.2.12-1
- Updated with the 6.2.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.12]

* Fri Apr 14 2023 Alan Bartlett <ajb@elrepo.org> - 6.2.11-1
- Updated with the 6.2.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.11]
- CONFIG_EROFS_FS=m, CONFIG_EROFS_FS_XATTR=y,
- CONFIG_EROFS_FS_POSIX_ACL=y, CONFIG_EROFS_FS_SECURITY=y,
- CONFIG_EROFS_FS_ZIP=y and CONFIG_EROFS_FS_ZIP_LZMA=y
- [https://elrepo.org/bugs/view.php?id=1343]

* Wed Apr 05 2023 Alan Bartlett <ajb@elrepo.org> - 6.2.10-1
- Updated with the 6.2.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.10]

* Thu Mar 30 2023 Alan Bartlett <ajb@elrepo.org> - 6.2.9-1
- Updated with the 6.2.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.9]

* Wed Mar 22 2023 Alan Bartlett <ajb@elrepo.org> - 6.2.8-1
- Updated with the 6.2.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.8]
- Enable the kernel-ml-tools package to provide the
- intel-speed-select binary file.
- [https://elrepo.org/bugs/view.php?id=1333]

* Fri Mar 17 2023 Alan Bartlett <ajb@elrepo.org> - 6.2.7-1
- Updated with the 6.2.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.7]

* Tue Mar 14 2023 Alan Bartlett <ajb@elrepo.org> - 6.2.6-1
- Updated with the 6.2.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.6]

* Sat Mar 11 2023 Alan Bartlett <ajb@elrepo.org> - 6.2.5-1
- Updated with the 6.2.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.5]

* Sat Mar 11 2023 Alan Bartlett <ajb@elrepo.org> - 6.2.4-1
- Updated with the 6.2.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.4]

* Fri Mar 10 2023 Alan Bartlett <ajb@elrepo.org> - 6.2.3-1
- Updated with the 6.2.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.3]

* Fri Mar 03 2023 Alan Bartlett <ajb@elrepo.org> - 6.2.2-1
- Updated with the 6.2.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.2]

* Sat Feb 25 2023 Alan Bartlett <ajb@elrepo.org> - 6.2.1-1
- Updated with the 6.2.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.1]

* Sun Feb 19 2023 Alan Bartlett <ajb@elrepo.org> - 6.2.0-1
- Updated with the 6.2 source tarball.
- CONFIG_LD_ORPHAN_WARN_LEVEL="warn", CONFIG_EFI_HANDOVER_PROTOCOL=y,
- CONFIG_CC_HAS_ENTRY_PADDING=y, CONFIG_FUNCTION_PADDING_CFI=11,
- CONFIG_FUNCTION_PADDING_BYTES=16, CONFIG_CALL_PADDING=y,
- CONFIG_HAVE_CALL_THUNKS=y, CONFIG_CALL_THUNKS=y,
- CONFIG_PREFIX_SYMBOLS=y, CONFIG_CALL_DEPTH_TRACKING=y,
- CONFIG_KVM_SMM=y, CONFIG_ARCH_HAS_NMI_SAFE_THIS_CPU_OPS=y,
- CONFIG_FUNCTION_ALIGNMENT_4B=y, CONFIG_FUNCTION_ALIGNMENT_16B=y,
- CONFIG_FUNCTION_ALIGNMENT=16, CONFIG_NF_NAT_OVS=y,
- CONFIG_BT_LE_L2CAP_ECRED=y, CONFIG_BT_HCIBTUSB_POLL_SYNC=y,
- CONFIG_BT_HCIBCM4377=m, CONFIG_FW_CS_DSP=m, CONFIG_LIBWX=m,
- CONFIG_NFP_NET_IPSEC=y, CONFIG_MT7996E=m, CONFIG_RTW88_USB=m,
- CONFIG_RTW88_8822BU=m, CONFIG_RTW88_8822CU=m, CONFIG_RTW88_8723DU=m,
- CONFIG_RTW88_8821CU=m, CONFIG_RTW89_8852B=m, CONFIG_RTW89_8852BE=m,
- CONFIG_TOUCHSCREEN_CYTTSP5=m, CONFIG_TOUCHSCREEN_HYNITRON_CSTXXX=m,
- CONFIG_TOUCHSCREEN_HIMAX_HX83112B=m, CONFIG_LEGACY_TIOCSTI=y,
- CONFIG_GPIO_IDIO_16=m, CONFIG_SENSORS_OCC_P8_I2C=m,
- CONFIG_SENSORS_OCC=m, CONFIG_SENSORS_OXP=m,
- CONFIG_ADVANTECH_EC_WDT=m, CONFIG_MFD_SMPRO=m,
- CONFIG_REGULATOR_RT6190=m, CONFIG_MEDIA_ANALOG_TV_SUPPORT=y,
- CONFIG_MEDIA_RADIO_SUPPORT=y, CONFIG_MEDIA_SDR_SUPPORT=y,
- CONFIG_MEDIA_PLATFORM_SUPPORT=y, CONFIG_MEDIA_TEST_SUPPORT=y,
- CONFIG_VIDEO_GO7007=m, CONFIG_VIDEO_GO7007_USB=m,
- CONFIG_VIDEO_GO7007_LOADER=m, CONFIG_VIDEO_GO7007_USB_S2250_BOARD=m,
- CONFIG_VIDEO_HDPVR=m, CONFIG_VIDEO_PVRUSB2=m,
- CONFIG_VIDEO_PVRUSB2_SYSFS=y, CONFIG_VIDEO_PVRUSB2_DVB=y,
- CONFIG_VIDEO_STK1160_COMMON=m, CONFIG_VIDEO_STK1160=m,
- CONFIG_VIDEO_OV7640=m, CONFIG_VIDEO_CS53L32A=m,
- CONFIG_VIDEO_SONY_BTF_MPX=m, CONFIG_VIDEO_UDA1342=m,
- CONFIG_VIDEO_WM8775=m, CONFIG_VIDEO_TW2804=m, CONFIG_VIDEO_TW9903=m,
- CONFIG_VIDEO_TW9906=m, CONFIG_MEDIA_TUNER_TEA5761=m,
- CONFIG_MEDIA_TUNER_TEA5767=m, CONFIG_DVB_RTL2832_SDR=m,
- CONFIG_VIDEO_NOMODESET=y, CONFIG_DRM_I915_PREEMPT_TIMEOUT_COMPUTE=7500,
- CONFIG_SND_SOC_INTEL_AVS_MACH_MAX98927=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_PROBE=m, CONFIG_SND_SOC_WM8961=m,
- CONFIG_MANA_INFINIBAND=m, CONFIG_VFIO_CONTAINER=y, CONFIG_VFIO_VIRQFD=y,
- CONFIG_DELL_WMI_DDV=m, CONFIG_X86_PLATFORM_DRIVERS_HP=y,
- CONFIG_SQUASHFS_COMPILE_DECOMP_SINGLE=y, CONFIG_CRYPTO_LIB_GF128MUL=y,
- CONFIG_ARCH_HAS_CPU_CACHE_INVALIDATE_MEMREGION=y and
- CONFIG_HAVE_OBJTOOL_NOP_MCOUNT=y

* Wed Feb 15 2023 Alan Bartlett <ajb@elrepo.org> - 6.1.12-1
- Updated with the 6.1.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.12]

* Thu Feb 09 2023 Alan Bartlett <ajb@elrepo.org> - 6.1.11-1
- Updated with the 6.1.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.11]

* Sun Feb 05 2023 Alan Bartlett <ajb@elrepo.org> - 6.1.10-1
- Updated with the 6.1.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.10]
- CONFIG_NTB_NETDEV=m, CONFIG_NTB=m, CONFIG_NTB_MSI=y,
- CONFIG_NTB_AMD=m, CONFIG_NTB_INTEL=m, CONFIG_NTB_PINGPONG=m,
- CONFIG_NTB_TOOL=m, CONFIG_NTB_PERF=m and CONFIG_NTB_TRANSPORT=m
- [https://elrepo.org/bugs/view.php?id=1322]

* Fri Feb 03 2023 Alan Bartlett <ajb@elrepo.org> - 6.1.9-2
- CONFIG_DEBUG_INFO=y, CONFIG_DEBUG_INFO_DWARF4=y,
- CONFIG_DEBUG_INFO_BTF=y, CONFIG_PAHOLE_HAS_SPLIT_BTF=y and
- CONFIG_DEBUG_INFO_BTF_MODULES=y -- All Reverted.
- CONFIG_DEBUG_INFO_NONE=y -- Set.
- [https://elrepo.org/bugs/view.php?id=1323]

* Wed Feb 01 2023 Alan Bartlett <ajb@elrepo.org> - 6.1.9-1
- Updated with the 6.1.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.9]
- CONFIG_DEBUG_INFO=y, CONFIG_DEBUG_INFO_DWARF4=y,
- CONFIG_DEBUG_INFO_BTF=y, CONFIG_PAHOLE_HAS_SPLIT_BTF=y and
- CONFIG_DEBUG_INFO_BTF_MODULES=y
- [https://elrepo.org/bugs/view.php?id=1320]
- CONFIG_MEDIA_CONTROLLER_DVB=y, CONFIG_VIDEO_AU0828=m,
- CONFIG_VIDEO_AU0828_V4L2=y, CONFIG_VIDEO_CX231XX=m,
- CONFIG_VIDEO_CX231XX_ALSA=m, CONFIG_VIDEO_CX231XX_DVB=m,
- CONFIG_DVB_AS102=m, CONFIG_DVB_B2C2_FLEXCOP_USB=m,
- CONFIG_DVB_USB_V2=m, CONFIG_DVB_USB_AF9015=m,
- CONFIG_DVB_USB_AF9035=m, CONFIG_DVB_USB_ANYSEE=m,
- CONFIG_DVB_USB_AU6610=m, CONFIG_DVB_USB_AZ6007=m,
- CONFIG_DVB_USB_CE6230=m, CONFIG_DVB_USB_DVBSKY=m,
- CONFIG_DVB_USB_EC168=m, CONFIG_DVB_USB_GL861=m,
- CONFIG_DVB_USB_LME2510=m, CONFIG_DVB_USB_MXL111SF=m,
- CONFIG_DVB_USB_RTL28XXU=m, CONFIG_DVB_USB_ZD1301=m,
- CONFIG_DVB_USB=m, CONFIG_DVB_USB_A800=m,
- CONFIG_DVB_USB_AF9005=m, CONFIG_DVB_USB_AF9005_REMOTE=m,
- CONFIG_DVB_USB_AZ6027=m, CONFIG_DVB_USB_CINERGY_T2=m,
- CONFIG_DVB_USB_CXUSB=m, CONFIG_DVB_USB_DIB0700=m,
- CONFIG_DVB_USB_DIB3000MC=m, CONFIG_DVB_USB_DIBUSB_MB=m,
- CONFIG_DVB_USB_DIBUSB_MC=m, CONFIG_DVB_USB_DIGITV=m,
- CONFIG_DVB_USB_DTT200U=m, CONFIG_DVB_USB_DTV5100=m,
- CONFIG_DVB_USB_DW2102=m, CONFIG_DVB_USB_GP8PSK=m,
- CONFIG_DVB_USB_M920X=m, CONFIG_DVB_USB_NOVA_T_USB2=m,
- CONFIG_DVB_USB_OPERA1=m, CONFIG_DVB_USB_PCTV452E=m,
- CONFIG_DVB_USB_TECHNISAT_USB2=m, CONFIG_DVB_USB_TTUSB2=m,
- CONFIG_DVB_USB_UMT_010=m, CONFIG_DVB_USB_VP702X=m,
- CONFIG_DVB_USB_VP7045=m, CONFIG_SMS_USB_DRV=m,
- CONFIG_DVB_TTUSB_BUDGET=m, CONFIG_DVB_TTUSB_DEC=m,
- CONFIG_MEDIA_COMMON_OPTIONS=y, CONFIG_CYPRESS_FIRMWARE=m,
- CONFIG_TTPCI_EEPROM=m, CONFIG_VIDEO_CX2341X=m,
- CONFIG_DVB_B2C2_FLEXCOP=m, CONFIG_SMS_SIANO_MDTV=m,
- CONFIG_VIDEO_CX25840=m, CONFIG_MEDIA_TUNER_E4000=m,
- CONFIG_MEDIA_TUNER_FC0011=m, CONFIG_MEDIA_TUNER_FC0012=m,
- CONFIG_MEDIA_TUNER_FC0013=m, CONFIG_MEDIA_TUNER_FC2580=m,
- CONFIG_MEDIA_TUNER_IT913X=m, CONFIG_MEDIA_TUNER_MAX2165=m,
- CONFIG_MEDIA_TUNER_MT2063=m, CONFIG_MEDIA_TUNER_MT2266=m,
- CONFIG_MEDIA_TUNER_MXL5005S=m, CONFIG_MEDIA_TUNER_MXL5007T=m,
- CONFIG_MEDIA_TUNER_R820T=m, CONFIG_MEDIA_TUNER_TDA18218=m,
- CONFIG_MEDIA_TUNER_TDA18250=m, CONFIG_MEDIA_TUNER_TUA9001=m,
- CONFIG_DVB_STB0899=m, CONFIG_DVB_STB6100=m,
- CONFIG_DVB_STV090x=m, CONFIG_DVB_STV6110x=m,
- CONFIG_DVB_MN88472=m, CONFIG_DVB_MN88473=m,
- CONFIG_DVB_SI2165=m, CONFIG_DVB_CX24116=m,
- CONFIG_DVB_CX24120=m, CONFIG_DVB_CX24123=m,
- CONFIG_DVB_DS3000=m, CONFIG_DVB_MT312=m,
- CONFIG_DVB_S5H1420=m, CONFIG_DVB_SI21XX=m,
- CONFIG_DVB_STB6000=m, CONFIG_DVB_STV0288=m,
- CONFIG_DVB_STV0299=m, CONFIG_DVB_STV0900=m,
- CONFIG_DVB_STV6110=m, CONFIG_DVB_TDA10086=m,
- CONFIG_DVB_TDA8083=m, CONFIG_DVB_TDA826X=m,
- CONFIG_DVB_TUNER_CX24113=m, CONFIG_DVB_TUNER_ITD1000=m,
- CONFIG_DVB_ZL10039=m, CONFIG_DVB_AF9013=m,
- CONFIG_DVB_AS102_FE=m, CONFIG_DVB_CX22700=m,
- CONFIG_DVB_CX22702=m, CONFIG_DVB_CXD2841ER=m,
- CONFIG_DVB_DIB3000MB=m, CONFIG_DVB_DIB3000MC=m,
- CONFIG_DVB_DIB7000M=m, CONFIG_DVB_DIB7000P=m,
- CONFIG_DVB_EC100=m, CONFIG_DVB_GP8PSK_FE=m,
- CONFIG_DVB_NXT6000=m, CONFIG_DVB_RTL2830=m,
- CONFIG_DVB_RTL2832=m, CONFIG_DVB_TDA10048=m,
- CONFIG_DVB_TDA1004X=m, CONFIG_DVB_ZD1301_DEMOD=m,
- CONFIG_DVB_STV0297=m, CONFIG_DVB_VES1820=m,
- CONFIG_DVB_AU8522=m, CONFIG_DVB_AU8522_DTV=m,
- CONFIG_DVB_AU8522_V4L=m, CONFIG_DVB_BCM3510=m,
- CONFIG_DVB_LG2160=m, CONFIG_DVB_NXT200X=m,
- CONFIG_DVB_S5H1411=m, CONFIG_DVB_DIB8000=m,
- CONFIG_DVB_PLL=m, CONFIG_DVB_TUNER_DIB0070=m,
- CONFIG_DVB_TUNER_DIB0090=m, CONFIG_DVB_AF9033=m,
- CONFIG_DVB_ATBM8830=m, CONFIG_DVB_ISL6421=m,
- CONFIG_DVB_ISL6423=m, CONFIG_DVB_IX2505V=m,
- CONFIG_DVB_LGS8GXX=m, CONFIG_DVB_LNBP21=m,
- CONFIG_DVB_LNBP22=m, CONFIG_DVB_M88RS2000=m and
- CONFIG_DVB_SP2=m
- [https://elrepo.org/bugs/view.php?id=1321]

* Wed Jan 25 2023 Alan Bartlett <ajb@elrepo.org> - 6.1.8-1
- Updated with the 6.1.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.8]

* Wed Jan 18 2023 Alan Bartlett <ajb@elrepo.org> - 6.1.7-1
- Updated with the 6.1.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.7]

* Sat Jan 14 2023 Alan Bartlett <ajb@elrepo.org> - 6.1.6-1
- Updated with the 6.1.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.6]

* Thu Jan 12 2023 Alan Bartlett <ajb@elrepo.org> - 6.1.5-1
- Updated with the 6.1.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.5]
- CONFIG_SECURITY_SELINUX_CHECKREQPROT_VALUE=0
- [https://elrepo.org/bugs/view.php?id=1310]

* Fri Jan 06 2023 Alan Bartlett <ajb@elrepo.org> - 6.1.4-1
- Updated with the 6.1.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.4]

* Wed Jan 04 2023 Alan Bartlett <ajb@elrepo.org> - 6.1.3-1
- Updated with the 6.1.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.3]

* Sat Dec 31 2022 Alan Bartlett <ajb@elrepo.org> - 6.1.2-1
- Updated with the 6.1.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.2]

* Wed Dec 21 2022 Alan Bartlett <ajb@elrepo.org> - 6.1.1-1
- Updated with the 6.1.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.1]
- CONFIG_BLK_DEV_UBLK=m [https://elrepo.org/bugs/view.php?id=1300]

* Sun Dec 11 2022 Alan Bartlett <ajb@elrepo.org> - 6.1.0-1
- Updated with the 6.1 source tarball.
- CONFIG_XEN_PV_MSR_SAFE=y, CONFIG_X86_PCC_CPUFREQ=m,
- CONFIG_X86_AMD_PSTATE=y, CONFIG_HAVE_KVM_DIRTY_RING_TSO=y,
- CONFIG_HAVE_KVM_DIRTY_RING_ACQ_REL=y, CONFIG_HAVE_RUST=y,
- CONFIG_ARCH_SUPPORTS_CFI_CLANG=y, CONFIG_ARCH_HAS_NONLEAF_PMD_YOUNG=y,
- CONFIG_COMPACT_UNEVICTABLE_DEFAULT=1, CONFIG_AHCI_DWC=m,
- CONFIG_NGBE=m, CONFIG_NET_VENDOR_ADI=y, CONFIG_ADIN1110=m,
- CONFIG_MLX5_EN_MACSEC=y, CONFIG_PCS_ALTERA_TSE=m,
- CONFIG_TOUCHSCREEN_COLIBRI_VF50=m, CONFIG_SENSORS_MAX31760=m,
- CONFIG_SENSORS_TPS546D24=m, CONFIG_SENSORS_EMC2305=m,
- CONFIG_EXAR_WDT=m, CONFIG_DRM_USE_DYNAMIC_DEBUG=y,
- CONFIG_DRM_GEM_DMA_HELPER=m, CONFIG_SND_SOC_AMD_PS=m,
- CONFIG_SND_SOC_AMD_PS_MACH=m, CONFIG_SND_SOC_SOF_AMD_REMBRANDT=m,
- CONFIG_SND_SOC_SOF_INTEL_SKL=m, CONFIG_SND_SOC_SOF_SKYLAKE=m,
- CONFIG_SND_SOC_SOF_KABYLAKE=m, CONFIG_SND_SOC_CS42L42_CORE=m,
- CONFIG_SND_SOC_CS42L83=m, CONFIG_SND_SOC_ES8326=m,
- CONFIG_SND_SOC_SRC4XXX_I2C=m, CONFIG_SND_SOC_SRC4XXX=m,
- CONFIG_HID_VRC2=m, CONFIG_HID_PXRC=m, CONFIG_AMD_PMF=m,
- CONFIG_RICHTEK_RTQ6056=m, CONFIG_LTRF216A=m,
- CONFIG_CRYPTO_ARIA_AESNI_AVX_X86_64=m, CONFIG_CRYPTO_LIB_UTILS=y,
- CONFIG_ZSTD_COMMON=y, CONFIG_HAVE_ARCH_KMSAN=y and
- CONFIG_HAVE_DYNAMIC_FTRACE_NO_PATCHABLE=y

* Thu Dec 08 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.12-1
- Updated with the 6.0.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.12]
- CONFIG_LSM="lockdown,yama,integrity,selinux,bpf"
- [https://elrepo.org/bugs/view.php?id=1289]

* Sat Dec 03 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.11-1
- Updated with the 6.0.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.11]
- CONFIG_SECURITY_LOCKDOWN_LSM=y, CONFIG_SECURITY_LOCKDOWN_LSM_EARLY=y,
- CONFIG_LOCK_DOWN_KERNEL_FORCE_NONE=y and
- CONFIG_LSM="yama,integrity,selinux,bpf"
- [https://elrepo.org/bugs/view.php?id=1289]
- CONFIG_BPF_UNPRIV_DEFAULT_OFF=y, CONFIG_BPF_LSM=y,
- CONFIG_BPF_STREAM_PARSER=y, CONFIG_LWTUNNEL_BPF=y,
- CONFIG_BPF_KPROBE_OVERRIDE=y, CONFIG_RUNTIME_TESTING_MENU=y and
- CONFIG_TEST_BPF=m

* Sun Nov 27 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.10-1
- Updated with the 6.0.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.10]

* Wed Nov 16 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.9-1
- Updated with the 6.0.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.9]

* Thu Nov 10 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.8-1
- Updated with the 6.0.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.8]

* Fri Nov 04 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.7-1
- Updated with the 6.0.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.7]
- Deselected the CONFIG_WERROR option.
- [https://elrepo.org/bugs/view.php?id=1281]

* Sat Oct 29 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.6-1
- Updated with the 6.0.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.6]

* Wed Oct 26 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.5-1
- Updated with the 6.0.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.5]

* Wed Oct 26 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.4-1
- Updated with the 6.0.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.4]
- CONFIG_MPTCP=y, CONFIG_INET_MPTCP_DIAG=m and CONFIG_MPTCP_IPV6=y
- [https://elrepo.org/bugs/view.php?id=1280]

* Fri Oct 21 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.3-1
- Updated with the 6.0.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.3]

* Sat Oct 15 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.2-1
- Updated with the 6.0.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.2]

* Wed Oct 12 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.1-1
- Updated with the 6.0.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.1]

* Sun Oct 02 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.0-1
- Updated with the 6.0 source tarball.
- CONFIG_CONTEXT_TRACKING_IDLE=y, CONFIG_CONTEXT_TRACKING_USER=y,
- CONFIG_HAVE_IMA_KEXEC=y, CONFIG_HAVE_CONTEXT_TRACKING_USER=y,
- CONFIG_HAVE_CONTEXT_TRACKING_USER_OFFSTACK=y,
- CONFIG_SOFTIRQ_ON_OWN_STACK=y, CONFIG_GET_FREE_REGION=y,
- CONFIG_CAVIUM_PTP=y, CONFIG_NET_VENDOR_WANGXUN=y,
- CONFIG_TXGBE=m, CONFIG_BCM84881_PHY=y, CONFIG_BCM_NET_PHYPTP=m,
- CONFIG_CAN_NETLINK=y, CONFIG_CAN_RX_OFFLOAD=y, CONFIG_CAN_CAN327=m,
- CONFIG_CAN_ESD_USB=m, CONFIG_IEEE802154_HWSIM=m,
- CONFIG_TCG_TIS_I2C=m, CONFIG_PINCTRL_METEORLAKE=m,
- CONFIG_SENSORS_LT7182S=m, CONFIG_APERTURE_HELPERS=y,
- CONFIG_SND_MIXER_OSS=m, CONFIG_SND_PCM_OSS=m,
- CONFIG_SND_PCM_OSS_PLUGINS=y, CONFIG_SND_CTL_FAST_LOOKUP=y,
- CONFIG_SND_MTS64=m, CONFIG_SND_SERIAL_U16550=m,
- CONFIG_SND_PORTMAN2X4=m, CONFIG_SND_HDA_CS_DSP_CONTROLS=m,
- CONFIG_SND_INTEL_BYT_PREFER_SOF=y, CONFIG_SND_SPI=y,
- CONFIG_SND_SOC_AMD_ST_ES8336_MACH=m, CONFIG_SND_AMD_ASOC_REMBRANDT=m,
- CONFIG_SND_SOC_AMD_RPL_ACP6x=m, CONFIG_SND_SOC_FSL_UTILS=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_DA7219=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_DMIC=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_HDAUDIO=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_I2S_TEST=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_MAX98357A=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_MAX98373=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_NAU8825=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_RT274=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_RT286=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_RT298=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_RT5682=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_SSM4567=m,
- CONFIG_SND_SOC_SOF_IPC3=y, CONFIG_SND_SOC_SOF_INTEL_IPC4=y,
- CONFIG_SND_SOC_SOF_INTEL_MTL=m, CONFIG_SND_SOC_SOF_METEORLAKE=m,
- CONFIG_SND_SOC_HDA=m, CONFIG_SND_SOC_RT274=m, CONFIG_SND_SOC_TAS2780=m,
- CONFIG_UCSI_STM32G0=m, CONFIG_TYPEC_ANX7411=m, CONFIG_LEDS_IS31FL319X=m,
- CONFIG_INFINIBAND_ERDMA=m, CONFIG_P2SB=y, CONFIG_PWM_CLK=m,
- CONFIG_CRYPTO_FIPS_NAME="Linux Kernel Cryptographic API",
- CONFIG_CRYPTO_XCTR=m, CONFIG_CRYPTO_HCTR2=m, CONFIG_CRYPTO_POLYVAL=m,
- CONFIG_CRYPTO_POLYVAL_CLMUL_NI=m, CONFIG_CRYPTO_ARIA=m,
- CONFIG_CRYPTO_LIB_SHA1=y and CONFIG_POLYNOMIAL=m

* Wed Sep 28 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.12-1
- Updated with the 5.19.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.12]

* Fri Sep 23 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.11-1
- Updated with the 5.19.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.11]

* Sun Sep 18 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.10-1
- Updated with the 5.19.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.10]

* Thu Sep 15 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.9-1
- Updated with the 5.19.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.9]

* Thu Sep 08 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.8-1
- Updated with the 5.19.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.8]

* Sun Sep 04 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.7-1
- Updated with the 5.19.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.7]

* Wed Aug 31 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.6-1
- Updated with the 5.19.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.6]
- CONFIG_INTEL_SPEED_SELECT_INTERFACE=m
- [https://elrepo.org/bugs/view.php?id=1256]

* Mon Aug 29 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.5-1
- Updated with the 5.19.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.5]

* Thu Aug 25 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.4-1
- Updated with the 5.19.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.4]

* Sun Aug 21 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.3-1
- Updated with the 5.19.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.3]

* Thu Aug 18 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.2-1
- Updated with the 5.19.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.2]

* Thu Aug 11 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.1-1
- Updated with the 5.19.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.1]

* Sun Jul 31 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.0-1
- Updated with the 5.19 source tarball.
- CONFIG_INITRAMFS_PRESERVE_MTIME=y, CONFIG_INTEL_TDX_GUEST=y,
- CONFIG_BOOT_VESA_SUPPORT=y, CONFIG_LEGACY_VSYSCALL_XONLY=y,
- CONFIG_MMU_GATHER_MERGE_VMAS=y, CONFIG_HAVE_OBJTOOL=y,
- CONFIG_HAVE_JUMP_LABEL_HACK=y, CONFIG_HAVE_NOINSTR_HACK=y,
- CONFIG_HAVE_NOINSTR_VALIDATION=y, CONFIG_HAVE_UACCESS_VALIDATION=y,
- CONFIG_ARCH_HAS_VM_GET_PAGE_PROT=y, CONFIG_PTE_MARKER=y,
- CONFIG_PTE_MARKER_UFFD_WP=y, CONFIG_CAN_CTUCANFD=m,
- CONFIG_CAN_CTUCANFD_PCI=m, CONFIG_FW_LOADER_SYSFS=y,
- CONFIG_MHI_BUS_EP=m, CONFIG_EFI_DXE_MEM_ATTRIBUTES=y,
- CONFIG_OCTEON_EP=m, CONFIG_SFC_SIENA=m, CONFIG_SFC_SIENA_MTD=y,
- CONFIG_SFC_SIENA_MCDI_MON=y, CONFIG_SFC_SIENA_MCDI_LOGGING=y,
- CONFIG_ADIN1100_PHY=m, CONFIG_DP83TD510_PHY=m,
- CONFIG_WLAN_VENDOR_PURELIFI=y, CONFIG_PLFXLC=m,
- CONFIG_RTW89_8852C=m, CONFIG_RTW89_8852CE=m,
- CONFIG_WLAN_VENDOR_SILABS=y, CONFIG_WFX=m, CONFIG_MTK_T7XX=m,
- CONFIG_JOYSTICK_SENSEHAT=m, CONFIG_PINCTRL_AMD=y,
- CONFIG_PINCTRL_MCP23S08_I2C=m, CONFIG_PINCTRL_MCP23S08_SPI=m,
- CONFIG_PINCTRL_MCP23S08=m, CONFIG_PINCTRL_SX150X=y,
- CONFIG_SENSORS_NCT6775_CORE=m, CONFIG_SENSORS_NCT6775_I2C=m,
- CONFIG_SENSORS_XDPE152=m, CONFIG_MFD_SIMPLE_MFD_I2C=m,
- CONFIG_REGULATOR_RT5759=m, CONFIG_DRM_DISPLAY_HELPER=m,
- CONFIG_DRM_DISPLAY_DP_HELPER=y, CONFIG_DRM_DISPLAY_HDCP_HELPER=y,
- CONFIG_DRM_DISPLAY_HDMI_HELPER=y, CONFIG_SND_SOC_SOF_HDA_PROBES=m,
- CONFIG_SND_SOC_CS35L45_TABLES=m, CONFIG_SND_SOC_CS35L45=m,
- CONFIG_SND_SOC_CS35L45_SPI=m, CONFIG_SND_SOC_CS35L45_I2C=m,
- CONFIG_SND_SOC_MAX98396=m, CONFIG_SND_SOC_WM8731_I2C=m,
- CONFIG_SND_SOC_WM8731_SPI=m, CONFIG_SND_SOC_WM8940=m,
- CONFIG_TYPEC_MUX_FSA4480=m, CONFIG_LEDS_PWM_MULTICOLOR=m,
- CONFIG_SEV_GUEST=m, CONFIG_CHROMEOS_ACPI=m, CONFIG_CM3605=m,
- CONFIG_MULTIPLEXER=m, CONFIG_ARCH_WANT_HUGETLB_PAGE_OPTIMIZE_VMEMMAP=y,
- CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP=y, CONFIG_TRUSTED_KEYS_TPM=y,
- CONFIG_RANDSTRUCT_NONE=y, CONFIG_CRYPTO_SM3_GENERIC=m,
- CONFIG_STACKDEPOT=y, CONFIG_STACK_HASH_ORDER=20,
- CONFIG_OBJTOOL=y and CONFIG_RCU_EXP_CPU_STALL_TIMEOUT=0

* Fri Jul 29 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.15-1
- Updated with the 5.18.15 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.15]

* Sun Jul 24 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.14-1
- Updated with the 5.18.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.14]

* Thu Jul 21 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.13-1
- Updated with the 5.18.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.13]

* Fri Jul 15 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.12-1
- Updated with the 5.18.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.12]
- CONFIG_CC_HAS_RETURN_THUNK=y, CONFIG_SPECULATION_MITIGATIONS=y,
- CONFIG_RETHUNK=y, CONFIG_CPU_UNRET_ENTRY=y, CONFIG_CPU_IBPB_ENTRY=y
- and CONFIG_CPU_IBRS_ENTRY=y

* Wed Jul 13 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.11-1
- Updated with the 5.18.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.11]

* Thu Jul 07 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.10-1
- Updated with the 5.18.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.10]

* Sat Jul 02 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.9-1
- Updated with the 5.18.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.9]

* Wed Jun 29 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.8-1
- Updated with the 5.18.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.8]

* Sat Jun 25 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.7-1
- Updated with the 5.18.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.7]
- CONFIG_PSI=y and CONFIG_PSI_DEFAULT_DISABLED=y
- [https://elrepo.org/bugs/view.php?id=1239]

* Wed Jun 22 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.6-1
- Updated with the 5.18.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.6]

* Thu Jun 16 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.5-1
- Updated with the 5.18.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.5]

* Wed Jun 15 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.4-1
- Updated with the 5.18.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.4]

* Thu Jun 09 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.3-1
- Updated with the 5.18.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.3]

* Sun Jun 05 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.2-1
- Updated with the 5.18.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.2]

* Sun May 29 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.1-1
- Updated with the 5.18.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.18.1]

* Sun May 22 2022 Alan Bartlett <ajb@elrepo.org> - 5.18.0-1
- Updated with the 5.18 source tarball.
- CONFIG_PAHOLE_VERSION=122, CONFIG_CLOCKSOURCE_WATCHDOG_MAX_SKEW_US=100,
- CONFIG_CC_HAS_IBT=y, CONFIG_KRETPROBE_ON_RETHOOK=y,
- CONFIG_HAVE_ARCH_HUGE_VMALLOC=y, CONFIG_RANDOMIZE_KSTACK_OFFSET=y,
- CONFIG_HAVE_PREEMPT_DYNAMIC_CALL=y, CONFIG_BLOCK_LEGACY_AUTOLOAD=y,
- CONFIG_BLK_MQ_STACKING=y, CONFIG_DEVICE_MIGRATION=y,
- CONFIG_ARCH_HAS_CURRENT_STACK_POINTER=y, CONFIG_NET_VENDOR_DAVICOM=y,
- CONFIG_DM9051=m, CONFIG_NET_VENDOR_FUNGIBLE=y, CONFIG_FUN_CORE=m,
- CONFIG_FUN_ETH=m, CONFIG_MT7921U=m, CONFIG_RTW89_8852A=m,
- CONFIG_INPUT_VIVALDIFMAP=y, CONFIG_TOUCHSCREEN_IMAGIS=m, CONFIG_I8K=y,
- CONFIG_SENSORS_LM25066_REGULATOR=y, CONFIG_SENSORS_PLI1209BC=m,
- CONFIG_SENSORS_PLI1209BC_REGULATOR=y, CONFIG_SENSORS_SY7636A=m,
- CONFIG_SENSORS_TMP464=m, CONFIG_SENSORS_ASUS_EC=m,
- CONFIG_INTEL_HFI_THERMAL=y, CONFIG_REGULATOR_RT5190A=m,
- CONFIG_REGULATOR_SY7636A=m, CONFIG_DRM_DP_HELPER=m,
- CONFIG_DRM_BUDDY=m, CONFIG_SND_SOC_AMD_ACP_PDM=m,
- CONFIG_SND_SOC_AMD_ACP_PCI=m, CONFIG_SND_SOC_INTEL_AVS=m,
- CONFIG_SND_SOC_INTEL_SOF_REALTEK_COMMON=m,
- CONFIG_SND_SOC_INTEL_SOF_CIRRUS_COMMON=m,
- CONFIG_SND_SOC_INTEL_SOF_SSP_AMP_MACH=m,
- CONFIG_SND_SOC_SOF_DEBUG_PROBES=m, CONFIG_SND_SOC_SOF_CLIENT=m,
- CONFIG_SND_SOC_SOF_HDA_PROBES=y, CONFIG_SND_SOC_AW8738=m,
- CONFIG_SND_SOC_RT1308=m, CONFIG_SND_SOC_TAS5805M=m,
- CONFIG_SND_SOC_LPASS_MACRO_COMMON=m, CONFIG_HID_VIVALDI_COMMON=m,
- CONFIG_TYPEC_RT1719=m, CONFIG_TYPEC_WUSB3801=m, CONFIG_VIRT_DRIVERS=y,
- CONFIG_VMGENID=y, CONFIG_AMD_HSMP=m, CONFIG_INTEL_SDSI=m,
- CONFIG_SERIAL_MULTI_INSTANTIATE=m, CONFIG_CHROME_PLATFORMS=y,
- CONFIG_CHROMEOS_LAPTOP=m, CONFIG_CHROMEOS_PSTORE=m,
- CONFIG_CHROMEOS_TBMC=m, CONFIG_CROS_KBD_LED_BACKLIGHT=m,
- CONFIG_F2FS_UNFAIR_RWSEM=y, CONFIG_CRYPTO_DH_RFC7919_GROUPS=y,
- CONFIG_CRYPTO_CRC64_ROCKSOFT=m, CONFIG_CRYPTO_SM3_AVX_X86_64=m,
- CONFIG_CRYPTO_LIB_SM3=m, CONFIG_CRC64_ROCKSOFT=m, CONFIG_DEBUG_INFO_NONE=y,
- CONFIG_HAVE_RETHOOK=y and CONFIG_RETHOOK=y

* Wed May 18 2022 Alan Bartlett <ajb@elrepo.org> - 5.17.9-1
- Updated with the 5.17.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17.9]

* Sun May 15 2022 Alan Bartlett <ajb@elrepo.org> - 5.17.8-1
- Updated with the 5.17.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17.8]

* Thu May 12 2022 Alan Bartlett <ajb@elrepo.org> - 5.17.7-1
- Updated with the 5.17.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17.7]

* Fri May 06 2022 Alan Bartlett <ajb@elrepo.org> - 5.17.6-1
- Updated with the 5.17.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17.6]

* Thu Apr 28 2022 Alan Bartlett <ajb@elrepo.org> - 5.17.5-1
- Updated with the 5.17.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17.5]

* Wed Apr 20 2022 Alan Bartlett <ajb@elrepo.org> - 5.17.4-1
- Updated with the 5.17.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17.4]

* Thu Apr 14 2022 Alan Bartlett <ajb@elrepo.org> - 5.17.3-1
- Updated with the 5.17.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17.3]

* Thu Apr 07 2022 Alan Bartlett <ajb@elrepo.org> - 5.17.2-1
- Updated with the 5.17.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17.2]
- Updated this specification file to allow external modules to be
- built without error. [https://elrepo.org/bugs/view.php?id=1215]

* Sun Mar 27 2022 Alan Bartlett <ajb@elrepo.org> - 5.17.1-1
- Updated with the 5.17.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.17.1]

* Sun Mar 20 2022 Alan Bartlett <ajb@elrepo.org> - 5.17.0-1
- Updated with the 5.17 source tarball.
- CONFIG_GUEST_PERF_EVENTS=y, CONFIG_X86_MEM_ENCRYPT=y,
- CONFIG_ACPI_PCC=y, CONFIG_X86_AMD_PSTATE=m,
- CONFIG_HAVE_KVM_PFNCACHE=y, CONFIG_HAVE_KVM_DIRTY_RING=y,
- CONFIG_PAGE_SIZE_LESS_THAN_256KB=y,
- CONFIG_ARCH_SUPPORTS_PAGE_TABLE_CHECK=y, CONFIG_BLK_ICQ=y,
- CONFIG_BT_MTK=m, CONFIG_NET_9P_FD=m, CONFIG_CS_DSP=m,
- CONFIG_NET_VENDOR_ENGLEDER=y, CONFIG_TSNEP=m,
- CONFIG_ICE_HWTS=y, CONFIG_NET_VENDOR_VERTEXCOM=y,
- CONFIG_MSE102X=m, CONFIG_WWAN_DEBUGFS=y, CONFIG_MHI_WWAN_CTRL=m,
- CONFIG_MHI_WWAN_MBIM=m, CONFIG_IOSM=m,
- CONFIG_SERIAL_8250_PERICOM=y, CONFIG_SENSORS_NZXT_SMART2=m,
- CONFIG_SENSORS_DELTA_AHE50DC_FAN=m,
- CONFIG_SENSORS_IR38064_REGULATOR=y, CONFIG_SENSORS_MP5023=m,
- CONFIG_SENSORS_INA238=m, CONFIG_SENSORS_ASUS_WMI=m,
- CONFIG_SENSORS_ASUS_WMI_EC=m, CONFIG_SIEMENS_SIMATIC_IPC_WDT=m,
- CONFIG_REGULATOR_MAX20086=m, CONFIG_DRM_GEM_CMA_HELPER=m,
- CONFIG_DRM_GEM_SHMEM_HELPER=m, CONFIG_TINYDRM_ILI9163=m,
- CONFIG_DRM_NOMODESET=y, CONFIG_DRM_PRIVACY_SCREEN=y,
- CONFIG_SND_HDA_SCODEC_CS35L41=m,
- CONFIG_SND_HDA_SCODEC_CS35L41_I2C=m,
- CONFIG_SND_HDA_SCODEC_CS35L41_SPI=m,
- CONFIG_SND_AMD_ACP_CONFIG=m,
- CONFIG_SND_SOC_INTEL_SOF_NAU8825_MACH=m,
- CONFIG_SND_SOC_SOF_AMD_TOPLEVEL=m,
- CONFIG_SND_SOC_SOF_AMD_COMMON=m,
- CONFIG_SND_SOC_SOF_AMD_RENOIR=m, CONFIG_SND_SOC_WM_ADSP=m,
- CONFIG_SND_SOC_AK4375=m, CONFIG_SND_SOC_CS35L41_LIB=m,
- CONFIG_SND_SOC_CS35L41=m, CONFIG_SND_SOC_TLV320ADC3XXX=m,
- CONFIG_USB_XEN_HCD=m, CONFIG_LEDS_SIEMENS_SIMATIC_IPC=m,
- CONFIG_YOGABOOK_WMI=m, CONFIG_ASUS_TF103C_DOCK=m,
- CONFIG_INTEL_VSEC=m, CONFIG_SIEMENS_SIMATIC_IPC=m,
- CONFIG_CRYPTO_ARCH_HAVE_LIB_BLAKE2S=y,
- CONFIG_CRYPTO_LIB_BLAKE2S_GENERIC=y,
- CONFIG_HAVE_BUILDTIME_MCOUNT_SORT=y and
- CONFIG_BUILDTIME_MCOUNT_SORT=y

* Sat Mar 19 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.16-1
- Updated with the 5.16.16 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.16]

* Wed Mar 16 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.15-1
- Updated with the 5.16.15 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.15]

* Sat Mar 12 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.14-1
- Updated with the 5.16.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.14]

* Wed Mar 09 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.13-1
- Updated with the 5.16.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.13]

* Wed Mar 02 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.12-1
- Updated with the 5.16.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.12]

* Wed Feb 23 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.11-1
- Updated with the 5.16.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.11]

* Wed Feb 16 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.10-1
- Updated with the 5.16.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.10]

* Fri Feb 11 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.9-1
- Updated with the 5.16.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.9]

* Wed Feb 09 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.8-1
- Updated with the 5.16.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.8]

* Sun Feb 06 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.7-1
- Updated with the 5.16.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.7]

* Sat Feb 05 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.6-1
- Updated with the 5.16.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.6]

* Wed Feb 02 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.5-1
- Updated with the 5.16.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.5]

* Sat Jan 29 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.4-1
- Updated with the 5.16.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.4]

* Wed Jan 26 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.3-1
- Updated with the 5.16.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.3]
- CONFIG_DRM_VBOXVIDEO=m [https://elrepo.org/bugs/view.php?id=1190]

* Thu Jan 20 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.2-1
- Updated with the 5.16.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.2]

* Sun Jan 16 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.1-1
- Updated with the 5.16.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.1]
- CONFIG_ORANGEFS_FS=m [https://elrepo.org/bugs/view.php?id=1184]

* Sun Jan 09 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.0-1
- Updated with the 5.16 source tarball.
- CONFIG_PREEMPT_BUILD=y, CONFIG_PREEMPT_COUNT=y, CONFIG_PREEMPTION=y,
- CONFIG_PREEMPT_DYNAMIC=y, CONFIG_PREEMPT_RCU=y, CONFIG_TASKS_RCU=y,
- CONFIG_CC_IMPLICIT_FALLTHROUGH="-Wimplicit-fallthrough=5",
- CONFIG_SCHED_CLUSTER=y, CONFIG_KVM_EXTERNAL_WRITE_TRACKING=y,
- CONFIG_ARCH_CORRECT_STACKTRACE_ON_KRETPROBE=y,
- CONFIG_PAGE_SIZE_LESS_THAN_64KB=y, CONFIG_DYNAMIC_SIGFRAME=y,
- CONFIG_UNINLINE_SPIN_UNLOCK=y, CONFIG_EXCLUSIVE_SYSTEM_RAM=y,
- CONFIG_NETFILTER_EGRESS=y, CONFIG_NETFILTER_SKIP_EGRESS=y,
- CONFIG_DM_AUDIT=y, CONFIG_AMT=m, CONFIG_NET_VENDOR_ASIX=y,
- CONFIG_SPI_AX88796C=m, CONFIG_SPI_AX88796C_COMPRESSION=y,
- CONFIG_ICE_SWITCHDEV=y, CONFIG_BRCMSMAC_LEDS=y,
- CONFIG_MT7921_COMMON=m, CONFIG_MT7921S=m, CONFIG_RTW89=m,
- CONFIG_RTW89_CORE=m, CONFIG_RTW89_PCI=m, CONFIG_RTW89_8852AE=m,
- CONFIG_SENSORS_MAX6620=m, CONFIG_SND_SOC_AMD_VANGOGH_MACH=m,
- CONFIG_SND_SOC_AMD_ACP6x=m, CONFIG_SND_SOC_AMD_YC_MACH=m,
- CONFIG_SND_SOC_AMD_ACP_COMMON=m, CONFIG_SND_SOC_AMD_ACP_I2S=m,
- CONFIG_SND_SOC_AMD_ACP_PCM=m, CONFIG_SND_AMD_ASOC_RENOIR=m,
- CONFIG_SND_SOC_AMD_MACH_COMMON=m, CONFIG_SND_SOC_AMD_LEGACY_MACH=m,
- CONFIG_SND_SOC_AMD_SOF_MACH=m, CONFIG_SND_SOC_INTEL_SOF_ES8336_MACH=m,
- CONFIG_SND_SOC_CS35L41_SPI=m, CONFIG_SND_SOC_CS35L41_I2C=m,
- CONFIG_SND_SOC_MAX98520=m, CONFIG_SND_SOC_RT1019=m,
- CONFIG_SND_SOC_RT5682S=m, CONFIG_SND_SOC_RT9120=m,
- CONFIG_SND_SOC_NAU8821=m, CONFIG_VIRTIO_PCI_LIB_LEGACY=y,
- CONFIG_ALIBABA_ENI_VDPA=m, CONFIG_XEN_PCI_STUB=y,
- CONFIG_NVIDIA_WMI_EC_BACKLIGHT=m, CONFIG_BARCO_P50_GPIO=m,
- CONFIG_XZ_DEC_MICROLZMA=y, CONFIG_HAVE_SAMPLE_FTRACE_DIRECT=y and
- CONFIG_HAVE_SAMPLE_FTRACE_DIRECT_MULTI=y

* Thu Jan 06 2022 Alan Bartlett <ajb@elrepo.org> - 5.15.13-1
- Updated with the 5.15.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.13]

* Wed Dec 29 2021 Alan Bartlett <ajb@elrepo.org> - 5.15.12-1
- Updated with the 5.15.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.12]

* Wed Dec 22 2021 Alan Bartlett <ajb@elrepo.org> - 5.15.11-1
- Updated with the 5.15.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.11]

* Fri Dec 17 2021 Alan Bartlett <ajb@elrepo.org> - 5.15.10-1
- Updated with the 5.15.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.10]

* Thu Dec 16 2021 Alan Bartlett <ajb@elrepo.org> - 5.15.9-1
- Updated with the 5.15.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.9]
- Not released.

* Wed Dec 15 2021 Alan Bartlett <ajb@elrepo.org> - 5.15.8-1
- Updated with the 5.15.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.8]

* Wed Dec 08 2021 Alan Bartlett <ajb@elrepo.org> - 5.15.7-1
- Updated with the 5.15.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.7]

* Wed Dec 01 2021 Alan Bartlett <ajb@elrepo.org> - 5.15.6-1
- Updated with the 5.15.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.6]
- CONFIG_SMB_SERVER=m and CONFIG_SMB_SERVER_CHECK_CAP_NET_ADMIN=y
- [https://elrepo.org/bugs/view.php?id=1168]

* Thu Nov 25 2021 Alan Bartlett <ajb@elrepo.org> - 5.15.5-1
- Updated with the 5.15.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.5]

* Sun Nov 21 2021 Alan Bartlett <ajb@elrepo.org> - 5.15.4-1
- Updated with the 5.15.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.4]

* Sat Nov 20 2021 Alan Bartlett <ajb@elrepo.org> - 5.15.3-1
- Updated with the 5.15.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.3]

* Fri Nov 12 2021 Alan Bartlett <ajb@elrepo.org> - 5.15.2-1
- Updated with the 5.15.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.2]

* Sat Nov 06 2021 Alan Bartlett <ajb@elrepo.org> - 5.15.1-1
- Updated with the 5.15.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.15.1]

* Sun Oct 31 2021 Alan Bartlett <ajb@elrepo.org> - 5.15.0-1
- Updated with the 5.15 source tarball.
- CONFIG_WERROR=y, CONFIG_ARCH_NR_GPIO=1024, CONFIG_XEN_PV_DOM0=y,
- CONFIG_PERF_EVENTS_AMD_UNCORE=m, CONFIG_ARCH_HAS_PARANOID_L1D_FLUSH=y,
- CONFIG_BLK_DEV_BSG_COMMON=y, CONFIG_BLOCK_HOLDER_DEPRECATED=y,
- CONFIG_PAGE_IDLE_FLAG=y, CONFIG_AF_UNIX_OOB=y, CONFIG_SYSFB=y,
- CONFIG_SYSFB_SIMPLEFB=y, CONFIG_SCSI_COMMON=y,
- CONFIG_NET_VENDOR_LITEX=y, CONFIG_MAXLINEAR_GPHY=m,
- CONFIG_I2C_VIRTIO=m, CONFIG_PTP_1588_CLOCK_OPTIONAL=y,
- CONFIG_GPIO_VIRTIO=m, CONFIG_SENSORS_AQUACOMPUTER_D5NEXT=m,
- CONFIG_SENSORS_SBRMI=m, CONFIG_REGULATOR_RTQ2134=m,
- CONFIG_REGULATOR_RTQ6752=m, CONFIG_SND_HDA_CODEC_CS8409=m,
- CONFIG_SND_SOC_AMD_ACP5x=m, CONFIG_SND_SOC_ICS43432=m,
- CONFIG_INTEL_IDXD_BUS=m, CONFIG_AMD_PTDMA=m, CONFIG_VFIO_PCI_CORE=m,
- CONFIG_VDPA_USER=m, CONFIG_VHOST_RING=m, CONFIG_MERAKI_MX100=m,
- CONFIG_INTEL_WMI=y, CONFIG_F2FS_IOSTAT=y, CONFIG_NETFS_STATS=y,
- CONFIG_SMBFS_COMMON=m, CONFIG_CRYPTO_LIB_SM4=m and
- CONFIG_MODULE_SIG_KEY_TYPE_RSA=y

* Wed Oct 27 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.15-1
- Updated with the 5.14.15 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.15]

* Thu Oct 21 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.14-1
- Updated with the 5.14.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.14]

* Sat Oct 16 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.13-1
- Updated with the 5.14.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.13]

* Wed Oct 13 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.12-1
- Updated with the 5.14.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.12]

* Sun Oct 10 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.11-1
- Updated with the 5.14.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.11]

* Fri Oct 08 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.10-1
- Updated with the 5.14.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.10]

* Wed Sep 29 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.9-1
- Updated with the 5.14.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.9]

* Mon Sep 27 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.8-1
- Updated with the 5.14.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.8]

* Wed Sep 22 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.7-1
- Updated with the 5.14.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.7]

* Sat Sep 18 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.6-1
- Updated with the 5.14.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.6]

* Thu Sep 16 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.5-1
- Updated with the 5.14.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.5]

* Wed Sep 15 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.4-1
- Updated with the 5.14.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.4]

* Sun Sep 12 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.3-1
- Updated with the 5.14.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.3]

* Wed Sep 08 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.2-1
- Updated with the 5.14.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.2]

* Fri Sep 03 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.1-1
- Updated with the 5.14.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.14.1]

* Sun Aug 29 2021 Alan Bartlett <ajb@elrepo.org> - 5.14.0-1
- Updated with the 5.14 source tarball.
- CONFIG_CC_HAS_NO_PROFILE_FN_ATTR=y, CONFIG_SCHED_CORE=y,
- CONFIG_ACPI_VIOT=y, CONFIG_ACPI_PRMT=y,
- CONFIG_HAVE_KVM_PM_NOTIFIER=y, CONFIG_ARCH_WANTS_NO_INSTR=y,
- CONFIG_MODULE_SIG_FORMAT=y, CONFIG_MODULE_SIG=y,
- CONFIG_MODULE_SIG_ALL=y, CONFIG_MODULE_SIG_SHA512=y,
- CONFIG_MODULE_SIG_HASH="sha512", CONFIG_SECRETMEM=y,
- CONFIG_NETFILTER_NETLINK_HOOK=m, CONFIG_MLX5_BRIDGE=y,
- CONFIG_MEDIATEK_GE_PHY=m, CONFIG_MOTORCOMM_PHY=m,
- CONFIG_FWNODE_MDIO=y, CONFIG_ACPI_MDIO=y,
- CONFIG_INPUT_JOYSTICK=y, CONFIG_JOYSTICK_ANALOG=m,
- CONFIG_JOYSTICK_A3D=m, CONFIG_JOYSTICK_ADC=m,
- CONFIG_JOYSTICK_ADI=m, CONFIG_JOYSTICK_COBRA=m,
- CONFIG_JOYSTICK_GF2K=m, CONFIG_JOYSTICK_GRIP=m,
- CONFIG_JOYSTICK_GRIP_MP=m, CONFIG_JOYSTICK_GUILLEMOT=m,
- CONFIG_JOYSTICK_INTERACT=m, CONFIG_JOYSTICK_SIDEWINDER=m,
- CONFIG_JOYSTICK_TMDC=m, CONFIG_JOYSTICK_IFORCE=m,
- CONFIG_JOYSTICK_IFORCE_USB=m, CONFIG_JOYSTICK_IFORCE_232=m,
- CONFIG_JOYSTICK_WARRIOR=m, CONFIG_JOYSTICK_MAGELLAN=m,
- CONFIG_JOYSTICK_SPACEORB=m, CONFIG_JOYSTICK_SPACEBALL=m,
- CONFIG_JOYSTICK_STINGER=m, CONFIG_JOYSTICK_TWIDJOY=m,
- CONFIG_JOYSTICK_ZHENHUA=m, CONFIG_JOYSTICK_DB9=m,
- CONFIG_JOYSTICK_GAMECON=m, CONFIG_JOYSTICK_TURBOGRAFX=m,
- CONFIG_JOYSTICK_AS5011=m, CONFIG_JOYSTICK_JOYDUMP=m,
- CONFIG_JOYSTICK_XPAD=m, CONFIG_JOYSTICK_XPAD_FF=y,
- CONFIG_JOYSTICK_XPAD_LEDS=y, CONFIG_JOYSTICK_WALKERA0701=m,
- CONFIG_JOYSTICK_PSXPAD_SPI=m, CONFIG_JOYSTICK_PSXPAD_SPI_FF=y,
- CONFIG_JOYSTICK_PXRC=m, CONFIG_JOYSTICK_QWIIC=m,
- CONFIG_JOYSTICK_FSIA6B=m, CONFIG_SENSORS_DPS920AB=m,
- CONFIG_SENSORS_MP2888=m, CONFIG_SENSORS_PIM4328=m,
- CONFIG_SENSORS_SHT4x=m, CONFIG_REGULATOR_MAX8893=m,
- CONFIG_REGULATOR_RT6160=m, CONFIG_REGULATOR_RT6245=m,
- CONFIG_V4L2_ASYNC=m, CONFIG_HSA_AMD_SVM=y,
- CONFIG_SND_SOC_INTEL_SOF_CS42L42_MACH=m,
- CONFIG_SND_SOC_SSM2518=m, CONFIG_SND_SOC_TFA989X=m,
- CONFIG_LEDS_LT3593=m, CONFIG_INFINIBAND_IRDMA=m,
- CONFIG_DELL_WMI_PRIVACY=y, CONFIG_WIRELESS_HOTKEY=m,
- CONFIG_THINKPAD_LMI=m, CONFIG_X86_PLATFORM_DRIVERS_INTEL=y,
- CONFIG_FW_ATTR_CLASS=m, CONFIG_VIRTIO_IOMMU=m,
- CONFIG_TSL2591=m, CONFIG_PHY_CAN_TRANSCEIVER=m,
- CONFIG_HUGETLB_PAGE_FREE_VMEMMAP=y,
- CONFIG_IMA_DEFAULT_HASH_SHA512=y, CONFIG_IMA_DEFAULT_HASH="sha512",
- CONFIG_CRYPTO_FIPS=y, CONFIG_CRYPTO_SHA512=y and
- CONFIG_MODULE_SIG_KEY="certs/signing_key.pem"

* Thu Aug 26 2021 Alan Bartlett <ajb@elrepo.org> - 5.13.13-1
- Updated with the 5.13.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.13]

* Wed Aug 18 2021 Alan Bartlett <ajb@elrepo.org> - 5.13.12-1
- Updated with the 5.13.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.12]

* Sun Aug 15 2021 Alan Bartlett <ajb@elrepo.org> - 5.13.11-1
- Updated with the 5.13.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.11]

* Thu Aug 12 2021 Alan Bartlett <ajb@elrepo.org> - 5.13.10-1
- Updated with the 5.13.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.10]

* Sun Aug 08 2021 Alan Bartlett <ajb@elrepo.org> - 5.13.9-1
- Updated with the 5.13.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.9]

* Wed Aug 04 2021 Alan Bartlett <ajb@elrepo.org> - 5.13.8-1
- Updated with the 5.13.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.8]

* Sat Jul 31 2021 Alan Bartlett <ajb@elrepo.org> - 5.13.7-1
- Updated with the 5.13.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.7]

* Wed Jul 28 2021 Alan Bartlett <ajb@elrepo.org> - 5.13.6-1
- Updated with the 5.13.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.6]
- CONFIG_I2C_HID_ACPI=m [https://elrepo.org/bugs/view.php?id=1123]

* Sat Jul 24 2021 Alan Bartlett <ajb@elrepo.org> - 5.13.5-1
- Updated with the 5.13.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.5]

* Wed Jul 21 2021 S.Tindall <s10dal@elrepo.org> - 5.13.4-1
- Updated with the 5.13.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.4]

* Wed Jul 21 2021 S.Tindall <s10dal@elrepo.org> - 5.13.3-1
- Updated with the 5.13.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.3]

* Wed Jul 14 2021 Alan Bartlett <ajb@elrepo.org> - 5.13.2-1
- Updated with the 5.13.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.2]

* Wed Jul 07 2021 Alan Bartlett <ajb@elrepo.org> - 5.13.1-1
- Updated with the 5.13.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.13.1]

* Sun Jun 27 2021 Alan Bartlett <ajb@elrepo.org> - 5.13.0-1
- Updated with the 5.13 source tarball.
- CONFIG_AS_IS_GNU=y, CONFIG_AS_VERSION=23000, CONFIG_CGROUP_MISC=y,
- CONFIG_HAVE_ARCH_USERFAULTFD_MINOR=y,
- CONFIG_ARCH_MHP_MEMMAP_ON_MEMORY_ENABLE=y,
- CONFIG_HAVE_ARCH_RANDOMIZE_KSTACK_OFFSET=y,
- CONFIG_MODULE_COMPRESS_NONE=y, CONFIG_MODPROBE_PATH="/sbin/modprobe",
- CONFIG_MHP_MEMMAP_ON_MEMORY=y, CONFIG_NF_LOG_SYSLOG=m,
- CONFIG_NETFILTER_XTABLES_COMPAT=y, CONFIG_PCPU_DEV_REFCNT=y,
- CONFIG_CAN_ETAS_ES58X=m, CONFIG_BT_HCIBTSDIO=m,
- CONFIG_BT_MRVL_SDIO=m, CONFIG_BT_MTKSDIO=m, CONFIG_BT_VIRTIO=m,
- CONFIG_NET_SELFTESTS=y, CONFIG_NET_VENDOR_MICROSOFT=y,
- CONFIG_MICROSOFT_MANA=m, CONFIG_MLX5_TC_SAMPLE=y,
- CONFIG_MARVELL_88X2222_PHY=m, CONFIG_NXP_C45_TJA11XX_PHY=m,
- CONFIG_TOUCHSCREEN_HYCON_HY46XX=m, CONFIG_TOUCHSCREEN_ILITEK=m,
- CONFIG_TOUCHSCREEN_MSG2638=m, CONFIG_I2C_CP2615=m,
- CONFIG_SENSORS_NZXT_KRAKEN2=m, CONFIG_SENSORS_BPA_RS600=m,
- CONFIG_SENSORS_FSP_3Y=m, CONFIG_SENSORS_IR36021=m,
- CONFIG_SENSORS_MAX15301=m, CONFIG_SENSORS_STPDDC60=m,
- CONFIG_INTEL_SOC_DTS_THERMAL=m, CONFIG_INTEL_PCH_THERMAL=m,
- CONFIG_INTEL_TCC_COOLING=m, CONFIG_DRM_I915_REQUEST_TIMEOUT=20000,
- CONFIG_DRM_XEN=y, CONFIG_DRM_XEN_FRONTEND=m, CONFIG_DRM_GUD=m,
- CONFIG_VIDEOMODE_HELPERS=y, CONFIG_SND_CTL_LED=m,
- CONFIG_SND_SOC_RT1015P=m, CONFIG_SND_SOC_TLV320AIC3X_I2C=m,
- CONFIG_SND_SOC_TLV320AIC3X_SPI=m, CONFIG_SND_VIRTIO=m,
- CONFIG_HID_FT260=m, CONFIG_RTC_DRV_GOLDFISH=m,
- CONFIG_ARCH_HAS_RESTRICTED_VIRTIO_MEMORY_ACCESS=y,
- CONFIG_VP_VDPA=m, CONFIG_GIGABYTE_WMI=m, CONFIG_ADV_SWBUTTON=m,
- CONFIG_NETFS_SUPPORT=m, CONFIG_NFS_V4_2_SSC_HELPER=y,
- CONFIG_CRYPTO_ECDSA=m, CONFIG_LZ4_COMPRESS=m,
- CONFIG_LZ4HC_COMPRESS=m, CONFIG_ZSTD_COMPRESS=m,
- CONFIG_ASN1_ENCODER=y and CONFIG_ARCH_USE_MEMTEST=y

* Wed Jun 23 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.13-1
- Updated with the 5.12.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.13]

* Fri Jun 18 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.12-1
- Updated with the 5.12.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.12]

* Wed Jun 16 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.11-1
- Updated with the 5.12.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.11]

* Thu Jun 10 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.10-1
- Updated with the 5.12.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.10]

* Wed Jun 02 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.9-1
- Updated with the 5.12.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.9]

* Sat May 29 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.8-1
- Updated with the 5.12.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.8]

* Wed May 26 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.7-1
- Updated with the 5.12.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.7]

* Sat May 22 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.6-1
- Updated with the 5.12.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.6]

* Wed May 19 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.5-1
- Updated with the 5.12.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.5]

* Fri May 14 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.4-1
- Updated with the 5.12.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.4]

* Wed May 12 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.3-1
- Updated with the 5.12.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.3]

* Fri May 07 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.2-1
- Updated with the 5.12.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.2]
- CONFIG_HSA_AMD=y [https://elrepo.org/bugs/view.php?id=1091]

* Sun May 02 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.1-1
- Updated with the 5.12.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.1]

* Sun Apr 25 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.0-1
- Updated with the 5.12 source tarball.
- CONFIG_LD_IS_BFD=y, CONFIG_LD_VERSION=23000, CONFIG_ACPI_PLATFORM_PROFILE=m,
- CONFIG_KVM_XEN=y, CONFIG_ARCH_SUPPORTS_LTO_CLANG=y,
- CONFIG_ARCH_SUPPORTS_LTO_CLANG_THIN=y, CONFIG_LTO_NONE=y,
- CONFIG_HAVE_IRQ_EXIT_ON_IRQ_STACK=y, CONFIG_HAVE_SOFTIRQ_ON_OWN_STACK=y,
- CONFIG_HAVE_PREEMPT_DYNAMIC=y, CONFIG_ARCH_HAS_ELFCORE_COMPAT=y,
- CONFIG_IP_VS_TWOS=m, CONFIG_SOCK_RX_QUEUE_MAPPING=y, CONFIG_XILINX_EMACLITE=m,
- CONFIG_MT76_SDIO=m, CONFIG_MT76_CONNAC_LIB=m, CONFIG_MT7663S=m,
- CONFIG_MT7921E=m, CONFIG_TCG_TIS_SPI=m, CONFIG_TCG_TIS_I2C_CR50=m,
- CONFIG_TCG_TIS_ST33ZP24_SPI=m, CONFIG_SENSORS_AHT10=m,
- CONFIG_SENSORS_TPS23861=m, CONFIG_DVB_MXL692=m,
- CONFIG_SND_INTEL_SOUNDWIRE_ACPI=m, CONFIG_SND_SOC_SOF_PCI_DEV=m,
- CONFIG_SND_SOC_SOF_ACPI_DEV=m, CONFIG_SND_SOC_SOF_INTEL_APL=m,
- CONFIG_SND_SOC_SOF_INTEL_CNL=m, CONFIG_SND_SOC_SOF_INTEL_ICL=m,
- CONFIG_SND_SOC_SOF_INTEL_TGL=m, CONFIG_SND_SOC_RT5659=m,
- CONFIG_SND_SOC_LPASS_RX_MACRO=m, CONFIG_SND_SOC_LPASS_TX_MACRO=m,
- CONFIG_USB_SERIAL_XR=m, CONFIG_TYPEC_UCSI=m, CONFIG_UCSI_ACPI=m,
- CONFIG_LEDS_TRIGGER_TTY=m, CONFIG_LEDS_BLINK=y, CONFIG_VIRTIO_PCI_LIB=y,
- CONFIG_X86_PLATFORM_DRIVERS_DELL=y, CONFIG_IOMMU_IO_PGTABLE=y,
- CONFIG_F2FS_FS_LZ4HC=y, CONFIG_NFS_V4_2_SSC_HELPER=m, CONFIG_LZ4HC_COMPRESS=y,
- CONFIG_HAVE_ARCH_KFENCE=y, CONFIG_HAVE_OBJTOOL_MCOUNT=y and
- CONFIG_FTRACE_MCOUNT_USE_CC=y

* Wed Apr 21 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.16-1
- Updated with the 5.11.16 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.16]

* Fri Apr 16 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.15-1
- Updated with the 5.11.15 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.15]

* Wed Apr 14 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.14-1
- Updated with the 5.11.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.14]

* Sun Apr 11 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.13-1
- Updated with the 5.11.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.13]

* Wed Apr 07 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.12-1
- Updated with the 5.11.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.12]
- CONFIG_REGMAP_SOUNDWIRE=m, CONFIG_SND_SOC_INTEL_SOF_WM8804_MACH=m,
- CONFIG_SND_SOC_INTEL_GLK_DA7219_MAX98357A_MACH=m,
- CONFIG_SND_SOC_INTEL_GLK_RT5682_MAX98357A_MACH=m,
- CONFIG_SND_SOC_INTEL_SOF_RT5682_MACH=m,
- CONFIG_SND_SOC_INTEL_SOF_PCM512x_MACH=m,
- CONFIG_SND_SOC_INTEL_CML_LP_DA7219_MAX98357A_MACH=m,
- CONFIG_SND_SOC_INTEL_SOF_CML_RT1011_RT5682_MACH=m,
- CONFIG_SND_SOC_INTEL_SOF_DA7219_MAX98373_MACH=m,
- CONFIG_SND_SOC_INTEL_EHL_RT5660_MACH=m, CONFIG_SND_SOC_SOF_TOPLEVEL=y,
- CONFIG_SND_SOC_SOF_PCI=m, CONFIG_SND_SOC_SOF_ACPI=m,
- CONFIG_SND_SOC_SOF=m, CONFIG_SND_SOC_SOF_PROBE_WORK_QUEUE=y,
- CONFIG_SND_SOC_SOF_INTEL_TOPLEVEL=y, CONFIG_SND_SOC_SOF_INTEL_ACPI=m,
- CONFIG_SND_SOC_SOF_INTEL_PCI=m, CONFIG_SND_SOC_SOF_INTEL_HIFI_EP_IPC=m,
- CONFIG_SND_SOC_SOF_INTEL_ATOM_HIFI_EP=m, CONFIG_SND_SOC_SOF_INTEL_COMMON=m,
- CONFIG_SND_SOC_SOF_BAYTRAIL_SUPPORT=y, CONFIG_SND_SOC_SOF_BAYTRAIL=m,
- CONFIG_SND_SOC_SOF_BROADWELL_SUPPORT=y, CONFIG_SND_SOC_SOF_BROADWELL=m,
- CONFIG_SND_SOC_SOF_MERRIFIELD_SUPPORT=y, CONFIG_SND_SOC_SOF_MERRIFIELD=m,
- CONFIG_SND_SOC_SOF_APOLLOLAKE_SUPPORT=y, CONFIG_SND_SOC_SOF_APOLLOLAKE=m,
- CONFIG_SND_SOC_SOF_GEMINILAKE_SUPPORT=y, CONFIG_SND_SOC_SOF_GEMINILAKE=m,
- CONFIG_SND_SOC_SOF_CANNONLAKE_SUPPORT=y, CONFIG_SND_SOC_SOF_CANNONLAKE=m,
- CONFIG_SND_SOC_SOF_COFFEELAKE_SUPPORT=y, CONFIG_SND_SOC_SOF_COFFEELAKE=m,
- CONFIG_SND_SOC_SOF_ICELAKE_SUPPORT=y, CONFIG_SND_SOC_SOF_ICELAKE=m,
- CONFIG_SND_SOC_SOF_COMETLAKE=m, CONFIG_SND_SOC_SOF_COMETLAKE_SUPPORT=y,
- CONFIG_SND_SOC_SOF_COMETLAKE_LP_SUPPORT=y, CONFIG_SND_SOC_SOF_TIGERLAKE_SUPPORT=y,
- CONFIG_SND_SOC_SOF_TIGERLAKE=m, CONFIG_SND_SOC_SOF_ELKHARTLAKE_SUPPORT=y,
- CONFIG_SND_SOC_SOF_ELKHARTLAKE=m, CONFIG_SND_SOC_SOF_JASPERLAKE_SUPPORT=y,
- CONFIG_SND_SOC_SOF_JASPERLAKE=m, CONFIG_SND_SOC_SOF_ALDERLAKE_SUPPORT=y,
- CONFIG_SND_SOC_SOF_ALDERLAKE=m, CONFIG_SND_SOC_SOF_HDA_COMMON=m,
- CONFIG_SND_SOC_SOF_HDA_LINK=y, CONFIG_SND_SOC_SOF_HDA_AUDIO_CODEC=y,
- CONFIG_SND_SOC_SOF_HDA_LINK_BASELINE=m, CONFIG_SND_SOC_SOF_HDA=m,
- CONFIG_SND_SOC_SOF_INTEL_SOUNDWIRE_LINK=y,
- CONFIG_SND_SOC_SOF_INTEL_SOUNDWIRE_LINK_BASELINE=m,
- CONFIG_SND_SOC_SOF_INTEL_SOUNDWIRE=m, CONFIG_SND_SOC_SOF_XTENSA=m,
- CONFIG_SND_SOC_MAX98373_SDW=m, CONFIG_SND_SOC_RT1011=m,
- CONFIG_SND_SOC_RT1015=m, CONFIG_SND_SOC_RT1308_SDW=m,
- CONFIG_SND_SOC_RT5682=m, CONFIG_SND_SOC_RT5682_I2C=m,
- CONFIG_SND_SOC_RT5682_SDW=m, CONFIG_SND_SOC_RT700=m,
- CONFIG_SND_SOC_RT700_SDW=m, CONFIG_SND_SOC_RT711=m,
- CONFIG_SND_SOC_RT711_SDW=m, CONFIG_SND_SOC_RT715=m,
- CONFIG_SND_SOC_RT715_SDW=m, CONFIG_SND_SOC_WSA881X=m,
- CONFIG_SOUNDWIRE=m, CONFIG_SOUNDWIRE_CADENCE=m,
- CONFIG_SOUNDWIRE_INTEL=m and
- CONFIG_SOUNDWIRE_GENERIC_ALLOCATION=m
- [https://elrepo.org/bugs/view.php?id=1087]

* Wed Mar 31 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.11-1
- Updated with the 5.11.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.11]

* Thu Mar 25 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.10-1
- Updated with the 5.11.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.10]

* Wed Mar 24 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.9-1
- Updated with the 5.11.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.9]

* Sun Mar 21 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.8-1
- Updated with the 5.11.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.8]

* Fri Mar 19 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.7-1
- Updated with the 5.11.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.7]

* Fri Mar 12 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.6-1
- Updated with the 5.11.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.6]

* Wed Mar 10 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.5-1
- Updated with the 5.11.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.5]

* Sun Mar 07 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.4-1
- Updated with the 5.11.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.4]

* Thu Mar 04 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.3-1
- Updated with the 5.11.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.3]

* Sat Feb 27 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.2-1
- Updated with the 5.11.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.2]

* Wed Feb 24 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.1-1
- Updated with the 5.11.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.11.1]

* Sun Feb 14 2021 Alan Bartlett <ajb@elrepo.org> - 5.11.0-1
- Updated with the 5.11 source tarball.
- CONFIG_XEN_PVHVM_GUEST=y, CONFIG_HAVE_CONTEXT_TRACKING_OFFSTACK=y,
- CONFIG_HAVE_MOVE_PUD=y, CONFIG_NFT_REJECT_NETDEV=m,
- CONFIG_CAN_M_CAN_PCI=m, CONFIG_BT_LEDS=y, CONFIG_AUXILIARY_BUS=y,
- CONFIG_MHI_BUS_PCI_GENERIC=m, CONFIG_ZRAM_DEF_COMP_LZORLE=y,
- CONFIG_ZRAM_DEF_COMP="lzo-rle", CONFIG_MHI_NET=m,
- CONFIG_USB_RTL8153_ECM=m, CONFIG_PINCTRL_ALDERLAKE=m,
- CONFIG_PINCTRL_ELKHARTLAKE=m, CONFIG_PINCTRL_LAKEFIELD=m,
- CONFIG_SENSORS_CORSAIR_PSU=m, CONFIG_SENSORS_LTC2992=m,
- CONFIG_SENSORS_MAX127=m, CONFIG_SENSORS_PM6764TR=m,
- CONFIG_SENSORS_Q54SJ108A2=m, CONFIG_SENSORS_SBTSI=m,
- CONFIG_SENSORS_XGENE=m, CONFIG_PROC_THERMAL_MMIO_RAPL=m,
- CONFIG_SND_SOC_ADI=m, CONFIG_SND_SOC_ADI_AXI_I2S=m,
- CONFIG_SND_SOC_ADI_AXI_SPDIF=m, CONFIG_SND_SOC_FSL_XCVR=m,
- CONFIG_SND_SOC_ADAU1372=m, CONFIG_SND_SOC_ADAU1372_I2C=m,
- CONFIG_SND_SOC_ADAU1372_SPI=m, CONFIG_SND_SOC_PCM5102A=m,
- CONFIG_SND_SOC_SIMPLE_MUX=m, CONFIG_SND_SOC_NAU8315=m,
- CONFIG_SND_SOC_LPASS_WSA_MACRO=m, CONFIG_SND_SOC_LPASS_VA_MACRO=m,
- CONFIG_AMD_SFH_HID=m, CONFIG_LEDS_RT8515=m,
- CONFIG_LEDS_TRIGGER_PANIC=y, CONFIG_EDAC_IGEN6=m,
- CONFIG_AMD_PMC=m, CONFIG_DELL_WMI_SYSMAN=m,
- CONFIG_INTEL_PMT_CLASS=m, CONFIG_INTEL_PMT_TELEMETRY=m,
- CONFIG_INTEL_PMT_CRASHLOG=m, CONFIG_PWM_DWC=m,
- CONFIG_PSTORE_DEFAULT_KMSG_BYTES=10240,
- CONFIG_CIFS_SWN_UPCALL=y,
- CONFIG_CRYPTO_DEV_QAT_4XXX=m and
- CONFIG_HAVE_DYNAMIC_FTRACE_WITH_ARGS=y

* Sat Feb 13 2021 Alan Bartlett <ajb@elrepo.org> - 5.10.16-1
- Updated with the 5.10.16 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.16]

* Wed Feb 10 2021 Alan Bartlett <ajb@elrepo.org> - 5.10.15-1
- Updated with the 5.10.15 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.15]

* Sun Feb 07 2021 Alan Bartlett <ajb@elrepo.org> - 5.10.14-1
- Updated with the 5.10.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.14]

* Thu Feb 04 2021 Alan Bartlett <ajb@elrepo.org> - 5.10.13-1
- Updated with the 5.10.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.13]

* Sun Jan 31 2021 Alan Bartlett <ajb@elrepo.org> - 5.10.12-1
- Updated with the 5.10.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.12]

* Thu Jan 28 2021 Alan Bartlett <ajb@elrepo.org> - 5.10.11-1
- Updated with the 5.10.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.11]

* Sun Jan 24 2021 Alan Bartlett <ajb@elrepo.org> - 5.10.10-1
- Updated with the 5.10.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.10]

* Wed Jan 20 2021 Alan Bartlett <ajb@elrepo.org> - 5.10.9-1
- Updated with the 5.10.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.9]

* Sun Jan 17 2021 Alan Bartlett <ajb@elrepo.org> - 5.10.8-1
- Updated with the 5.10.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.8]

* Wed Jan 13 2021 Alan Bartlett <ajb@elrepo.org> - 5.10.7-1
- Updated with the 5.10.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.7]

* Sat Jan 09 2021 Alan Bartlett <ajb@elrepo.org> - 5.10.6-1
- Updated with the 5.10.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.6]

* Wed Jan 06 2021 Alan Bartlett <ajb@elrepo.org> - 5.10.5-1
- Updated with the 5.10.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.10.5]
- CONFIG_BRCMFMAC_SDIO=y, CONFIG_RSI_SDIO=m,
- CONFIG_SSB_SDIOHOST_POSSIBLE=y, CONFIG_MMC=m, CONFIG_MMC_BLOCK=m,
- CONFIG_MMC_BLOCK_MINORS=8, CONFIG_SDIO_UART=m, CONFIG_MMC_SDHCI=m,
- CONFIG_MMC_SDHCI_IO_ACCESSORS=y, CONFIG_MMC_SDHCI_PCI=m,
- CONFIG_MMC_RICOH_MMC=y, CONFIG_MMC_SDHCI_ACPI=m,
- CONFIG_MMC_SDHCI_PLTFM=m, CONFIG_MMC_SDHCI_F_SDH30=m,
- CONFIG_MMC_WBSD=m, CONFIG_MMC_TIFM_SD=m, CONFIG_MMC_SPI=m,
- CONFIG_MMC_CB710=m, CONFIG_MMC_VIA_SDMMC=m, CONFIG_MMC_VUB300=m,
- CONFIG_MMC_USHC=m, CONFIG_MMC_USDHI6ROL0=m, CONFIG_MMC_REALTEK_PCI=m,
- CONFIG_MMC_REALTEK_USB=m, CONFIG_MMC_CQHCI=m, CONFIG_MMC_HSQ=m,
- CONFIG_MMC_TOSHIBA_PCI=m, CONFIG_MMC_MTK=m and
- CONFIG_MMC_SDHCI_XENON=m
- [https://elrepo.org/bugs/view.php?id=1067]

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
