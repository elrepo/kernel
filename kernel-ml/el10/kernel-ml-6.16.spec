# All global changes to build and install should follow this line.

# Disable LTO in userspace packages.
%global _lto_cflags %{nil}

# The libexec directory is not used by the linker, so the shared object there
# should not be exported to RPM provides.
%global __provides_exclude_from ^%{_libexecdir}/kselftests

# Disable the find-provides.ksyms script.
%global __provided_ksyms_provides %{nil}

# All global wide changes should be above this line otherwise
# the %%install section will not see them.
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
%global LKAver 6.16.6

# Define the buildid, if required.
#global buildid .local


# Determine the sublevel number and set pkg_version.
%define sublevel %(echo %{LKAver} | %{__awk} -F\. '{ print $3 }')
%if "%{sublevel}" == ""
%global pkg_version %{LKAver}.0
%else
%global pkg_version %{LKAver}
%endif

# Set pkg_release.
%global pkg_release 1%{?buildid}%{?dist}

### BCAT
# Further investigation is required before these features
# are enabled for the ELRepo Project kernels.
%global signkernel 0
%global signmodules 0
### BCAT

# Compress modules on all architectures that build modules.
%ifarch x86_64 || aarch64
%global zipmodules 1
%else
%global zipmodules 0
%endif

%if %{zipmodules}
%global zipsed -e 's/\.ko$/\.ko.xz/'
# For parallel xz processes. Replace with 1 to go back to single process.
%global zcpu `nproc --all`
%endif

# The following build options are enabled by default, but may become disabled
# by later architecture-specific checks. These can also be disabled by using
# --without <opt> in the rpmbuild command, or by forcing these values to 0.
#
# kernel-ml
%define with_std          %{?_without_std:          0} %{?!_without_std:          1}
#
# kernel-ml-headers
%define with_headers      %{?_without_headers:      0} %{?!_without_headers:      1}
%define with_cross_headers   %{?_without_cross_headers:   0} %{?!_without_cross_headers:   1}
#
# kernel-ml-doc
%define with_doc          %{?_without_doc:          0} %{?!_without_doc:          1}
#
# perf
%define with_perf         %{?_without_perf:         0} %{?!_without_perf:         1}
#
# tools
%define with_tools        %{?_without_tools:        0} %{?!_without_tools:        1}
#
# control whether to install the vdso directories
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}
#
# Additional option for toracat-friendly, one-off, kernel-ml building.
# Only build the base kernel-ml (--with baseonly):
%define with_baseonly     %{?_with_baseonly:        1} %{?!_with_baseonly:        0}

%global KVERREL %{pkg_version}-%{pkg_release}.%{_target_cpu}

# If requested, only build base kernel-ml package.
%if %{with_baseonly}
%define with_doc 0
%define with_perf 0
%define with_tools 0
%define with_vdso_install 0
%endif

%ifarch noarch
%define with_std 0
%define with_headers 0
%define with_cross_headers 0
%define with_perf 0
%define with_tools 0
%define with_vdso_install 0
%endif

%ifarch x86_64 || aarch64
%define with_doc 0
%endif

%ifarch x86_64
%define asmarch x86
%define bldarch x86_64
%define hdrarch x86_64
%define make_target bzImage
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch aarch64
%define asmarch arm64
%define bldarch arm64
%define hdrarch arm64
%define make_target Image.gz
%define kernel_image arch/arm64/boot/Image.gz
%endif

# Architectures we build tools/cpupower on
%define cpupowerarchs x86_64 aarch64

%if %{with_vdso_install}
%define use_vdso 1
%define _use_vdso 1
%else
%define _use_vdso 0
%endif

#
# Packages that need to be installed before the kernel is installed,
# as they will be used by the %%post scripts.
#
%define kernel_ml_prereq  coreutils, systemd >= 203-2, /usr/bin/kernel-install
%define initrd_prereq  dracut >= 027

Name: kernel-ml
Summary: The Linux kernel. (The core of any Linux kernel based operating system.)
License: ((GPL-2.0-only WITH Linux-syscall-note) OR BSD-2-Clause) AND ((GPL-2.0-only WITH Linux-syscall-note) OR BSD-3-Clause) AND ((GPL-2.0-only WITH Linux-syscall-note) OR CDDL-1.0) AND ((GPL-2.0-only WITH Linux-syscall-note) OR Linux-OpenIB) AND ((GPL-2.0-only WITH Linux-syscall-note) OR MIT) AND ((GPL-2.0-or-later WITH Linux-syscall-note) OR BSD-3-Clause) AND ((GPL-2.0-or-later WITH Linux-syscall-note) OR MIT) AND 0BSD AND BSD-2-Clause AND (BSD-2-Clause OR Apache-2.0) AND BSD-3-Clause AND BSD-3-Clause-Clear AND CC0-1.0 AND GFDL-1.1-no-invariants-or-later AND GPL-1.0-or-later AND (GPL-1.0-or-later OR BSD-3-Clause) AND (GPL-1.0-or-later WITH Linux-syscall-note) AND GPL-2.0-only AND (GPL-2.0-only OR Apache-2.0) AND (GPL-2.0-only OR BSD-2-Clause) AND (GPL-2.0-only OR BSD-3-Clause) AND (GPL-2.0-only OR CDDL-1.0) AND (GPL-2.0-only OR GFDL-1.1-no-invariants-or-later) AND (GPL-2.0-only OR GFDL-1.2-no-invariants-only) AND (GPL-2.0-only WITH Linux-syscall-note) AND GPL-2.0-or-later AND (GPL-2.0-or-later OR BSD-2-Clause) AND (GPL-2.0-or-later OR BSD-3-Clause) AND (GPL-2.0-or-later OR CC-BY-4.0) AND (GPL-2.0-or-later WITH GCC-exception-2.0) AND (GPL-2.0-or-later WITH Linux-syscall-note) AND ISC AND LGPL-2.0-or-later AND (LGPL-2.0-or-later OR BSD-2-Clause) AND (LGPL-2.0-or-later WITH Linux-syscall-note) AND LGPL-2.1-only AND (LGPL-2.1-only OR BSD-2-Clause) AND (LGPL-2.1-only WITH Linux-syscall-note) AND LGPL-2.1-or-later AND (LGPL-2.1-or-later WITH Linux-syscall-note) AND (Linux-OpenIB OR GPL-2.0-only) AND (Linux-OpenIB OR GPL-2.0-only OR BSD-2-Clause) AND Linux-man-pages-copyleft AND MIT AND (MIT OR Apache-2.0) AND (MIT OR GPL-2.0-only) AND (MIT OR GPL-2.0-or-later) AND (MIT OR LGPL-2.1-only) AND (MPL-1.1 OR GPL-2.0-only) AND (X11 OR GPL-2.0-only) AND (X11 OR GPL-2.0-or-later) AND Zlib AND (copyleft-next-0.3.1 OR GPL-2.0-or-later)
URL: https://www.kernel.org/
Version: %{pkg_version}
Release: %{pkg_release}
ExclusiveArch: x86_64 aarch64 noarch
ExclusiveOS: Linux
Provides: kernel = %{version}-%{release}
Provides: installonlypkg(kernel)
Requires: %{name}-core-uname-r = %{KVERREL}
Requires: %{name}-modules-uname-r = %{KVERREL}

#
# List the packages required for the kernel-ml build.
#
BuildRequires: bash, bc, binutils, bison, bzip2, coreutils, diffutils, dwarves, elfutils-devel
BuildRequires: findutils, flex, gawk, gcc, gcc-c++, gcc-plugin-devel, git-core, glibc-static
BuildRequires: gzip, hmaccalc, hostname, kernel-rpm-macros >= 185-9, kmod, m4, make, net-tools
BuildRequires: patch, perl-Carp, perl-devel, perl-generators, perl-interpreter, python3-devel
BuildRequires: redhat-rpm-config, tar, which, xz

BuildRequires: openssl-devel openssl
BuildRequires: zlib-devel binutils-devel newt-devel perl(ExtUtils::Embed) bison flex xz-devel
BuildRequires: audit-libs-devel python3-setuptools
BuildRequires: java-devel
BuildRequires: libbpf-devel
BuildRequires: libbabeltrace-devel
BuildRequires: numactl-devel
BuildRequires: asciidoc, python3-sphinx, python3-sphinx_rtd_theme, xmlto
BuildRequires: gettext, libcap-devel, libcap-ng-devel, libnl3-devel
BuildRequires: ncurses-devel, pciutils-devel
BuildRequires: rsync

# The following are rtla requirements
BuildRequires: python3-docutils
BuildRequires: libtraceevent-devel
BuildRequires: libtracefs-devel >= 1.6
%ifarch aarch64
BuildRequires: opencsd-devel >= 1.2.1
%endif

BuildConflicts: rhbuildsys(DiskFree) < 500Mb

###
### Sources
###
Source0: https://www.kernel.org/pub/linux/kernel/v6.x/linux-%{LKAver}.tar.xz

Source2: config-%{version}-x86_64

Source20: mod-denylist.sh
#Source21: mod-sign.sh
#Source23: x509.genkey
Source26: mod-extra.list

Source34: filter-x86_64.sh
#Source37: filter-aarch64.sh
Source40: filter-modules.sh

#Source100: rheldup3.x509
#Source101: rhelkpatch1.x509

Source2002: kvm_stat.logrotate

# Do not package the source tarball.
# To build .src.rpm, run with '--with src'
%if %{?_with_src:0}%{!?_with_src:1}
NoSource: 0
%endif

%description
The %{name} meta package.

#
# This macro does requires, provides, conflicts, obsoletes for a kernel-ml package.
#	%%kernel_ml_reqprovconf <subpackage>
# It uses any kernel_ml_<subpackage>_conflicts and kernel_ml_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_ml_reqprovconf \
Provides: %{name} = %{pkg_version}-%{pkg_release}\
Provides: %{name}-%{_target_cpu} = %{pkg_version}-%{pkg_release}%{?1:+%{1}}\
Provides: %{name}-drm-nouveau = 16\
Provides: %{name}-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires(pre): %{kernel_ml_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(pre): ((linux-firmware >= 20150904-56.git6ebf5d57) if linux-firmware)\
Recommends: linux-firmware\
Requires(preun): systemd >= 200\
Conflicts: xfsprogs < 4.3.0-1\
Conflicts: xorg-x11-drv-vmmouse < 13.0.99\
%{expand:%%{?kernel_ml%{?1:_%{1}}_conflicts:Conflicts: %%{%{name}%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel_ml%{?1:_%{1}}_obsoletes:Obsoletes: %%{%{name}%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel_ml%{?1:_%{1}}_provides:Provides: %%{%{name}%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatically because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function.\
AutoReq: no\
AutoProv: yes\
%{nil}

%package headers
Summary: Header files for the Linux kernel, used by glibc.
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%description headers
The Linux kernel headers includes the C header files that specify
the interface between the Linux kernel and userspace libraries and
programs. The header files define structures and constants that are
needed for building most standard programs and are also needed for
rebuilding the glibc package.

%package cross-headers
Summary: Header files for the Linux kernel for use by cross-glibc

%description cross-headers
Kernel-cross-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
cross-glibc package.

%package doc
Summary: Various documentation bits found in the Linux kernel source.
Group: Documentation
%description doc
This package contains documentation files from the Linux kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel.
Requires: bzip2
License: GPLv2
%description -n perf
This package contains the perf tool, which enables performance
monitoring of the Linux kernel.

%package -n python3-perf
Summary: Python bindings for apps which will manipulate perf events.
%description -n python3-perf
This package contains a module that permits applications written
in the Python programming language to use the interface to
manipulate perf events.

%package -n libperf
Summary: The perf library from kernel source

%description -n libperf
This package contains the kernel source perf library.


%package -n libperf-devel
Summary: Developement files for the perf library from kernel source
Requires: libperf = %{version}-%{release}

%description -n libperf-devel
This package includes libraries and header files needed for development
of applications which use perf library from kernel source.

# with_perf
%endif

%if %{with_tools}
%package -n %{name}-tools
Summary: Assortment of tools for the Linux kernel.
License: GPLv2
Obsoletes: kernel-tools < %{version}
Provides:  kernel-tools = %{version}-%{release}
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpuspeed < 1:1.5-16
Requires: %{name}-tools-libs = %{version}-%{release}
%if "%{name}" == "kernel-ml"
Conflicts: kernel-lt-tools
%else
# it's kernel-lt
Conflicts: kernel-ml-tools
%endif
%define __requires_exclude ^%{_bindir}/python
%description -n %{name}-tools
This package contains the tools/ directory from the Linux kernel
source and the supporting documentation.

%package -n %{name}-tools-libs
Summary: Libraries for the %{name}-tools.
License: GPLv2
Obsoletes: kernel-tools-libs < %{version}
Provides:  kernel-tools-libs = %{version}-%{release}
%if "%{name}" == "kernel-ml"
Conflicts: kernel-lt-tools-libs
%else
# it's kernel-lt
Conflicts: kernel-ml-tools-libs
%endif
%description -n %{name}-tools-libs
This package contains the libraries built from the tools/ directory
of the Linux kernel source.

%package -n %{name}-tools-libs-devel
Summary: Development files for the %{name}-tools libraries.
License: GPLv2
Obsoletes: kernel-tools-libs-devel < %{version}
Provides:  kernel-tools-libs-devel = %{version}-%{release}
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Provides: %{name}-tools-devel
Requires: %{name}-tools-libs = %{version}-%{release}
Requires: %{name}-tools = %{version}-%{release}
%if "%{name}" == "kernel-ml"
Conflicts: kernel-lt-tools-libs-devel
%else
# it's kernel-lt
Conflicts: kernel-ml-tools-libs-devel
%endif
%description -n %{name}-tools-libs-devel
This package contains the development files for the tools/ directory
of the Linux kernel source.

%package -n rtla
Summary: Real-Time Linux Analysis tools
Requires: libtraceevent
Requires: libtracefs
Requires: %{name}-tools-libs = %{version}-%{release}
%description -n rtla
The rtla meta-tool includes a set of commands that aims to analyze
the real-time properties of Linux. Instead of testing Linux as a black box,
rtla leverages kernel tracing capabilities to provide precise information
about the properties and root causes of unexpected results.

%package -n rv
Summary: RV: Runtime Verification
%description -n rv
Runtime Verification (RV) is a lightweight (yet rigorous) method that
complements classical exhaustive verification techniques (such as model
checking and theorem proving) with a more practical approach for
complex systems.
The rv tool is the interface for a collection of monitors that aim
analysing the logical and timing behavior of Linux.

# with_tools
%endif

#
# This macro creates a kernel-ml-<subpackage>-devel package.
#	%%kernel_ml_devel_package [-m] <subpackage> <pretty-name>
#
%define kernel_ml_devel_package(m) \
%package %{?1:%{1}-}devel\
Summary: Development package for building %{name} modules to match the %{?2:%{2} }%{name}.\
Provides: %{name}%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}-devel-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: %{name}-devel-uname-r = %{KVERREL}%{?1:+%{1}}\
Provides: kernel%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-devel-uname-r = %{KVERREL}%{?1:+%{1}}\
Provides: kernel-devel = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel)\
Provides: installonlypkg(kernel-ml)\
AutoReqProv: no\
Requires(pre): findutils\
Requires: findutils\
Requires: perl-interpreter\
Requires: openssl-devel\
Requires: elfutils-libelf-devel\
Requires: bison\
Requires: flex\
Requires: make\
Requires: gcc\
%if %{-m:1}%{!-m:0}\
Requires: %{name}-devel-uname-r = %{KVERREL}\
%endif\
%description %{?1:%{1}-}devel\
This package provides %{name} headers and makefiles sufficient to build modules\
against the %{?2:%{2} }%{name} package.\
%{nil}

#
# This macro creates an empty kernel-ml-<subpackage>-devel-matched package that
# requires both the core and devel packages locked on the same version.
#	%%kernel_ml_devel_matched_package [-m] <subpackage> <pretty-name>
#
%define kernel_ml_devel_matched_package(m) \
%package %{?1:%{1}-}devel-matched\
Summary: Meta package to install matching core and devel packages for a given %{?2:%{2} }%{name}.\
Requires: %{name}%{?1:-%{1}}-devel = %{version}-%{release}\
Requires: %{name}%{?1:-%{1}}-core = %{version}-%{release}\
%description %{?1:%{1}-}devel-matched\
This meta package is used to install matching core and devel packages for a given %{?2:%{2} }%{name}.\
%{nil}

#
# This macro creates a kernel-ml-<subpackage>-modules-extra package.
#	%%kernel_ml_modules_extra_package [-m] <subpackage> <pretty-name>
#
%define kernel_ml_modules_extra_package(m) \
%package %{?1:%{1}-}modules-extra\
Summary: Extra %{name} modules to match the %{?2:%{2} }%{name}.\
Provides: %{name}%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: %{name}%{?1:-%{1}}-modules-extra = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: installonlypkg(kernel-ml-module)\
Provides: %{name}%{?1:-%{1}}-modules-extra-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: %{name}-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: %{name}%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
%if %{-m:1}%{!-m:0}\
Requires: %{name}-modules-extra-uname-r = %{KVERREL}\
%endif\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules-extra\
This package provides less commonly used %{name} modules for the %{?2:%{2} }%{name} package.\
%{nil}

#
# This macro creates a kernel-ml-<subpackage>-modules package.
#	%%kernel_ml_modules_package [-m] <subpackage> <pretty-name>
#
%define kernel_ml_modules_package(m) \
%package %{?1:%{1}-}modules\
Summary: %{name} modules to match the %{?2:%{2}-}core %{name}.\
Provides: %{name}%{?1:-%{1}}-modules-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}-modules-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: %{name}-modules = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: installonlypkg(kernel-ml-module)\
Provides: %{name}%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: %{name}-uname-r = %{KVERREL}%{?1:+%{1}}\
%if %{-m:1}%{!-m:0}\
Requires: %{name}-modules-uname-r = %{KVERREL}\
%endif\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules\
This package provides commonly used %{name} modules for the %{?2:%{2}-}core %{name} package.\
%{nil}

#
# this macro creates a kernel-ml-<subpackage> meta package.
#	%%kernel_ml_meta_package <subpackage>
#
%define kernel_ml_meta_package() \
%package %{1}\
Summary: %{name} meta-package for the %{1} ${name}.\
Requires: %{name}-%{1}-core-uname-r = %{KVERREL}+%{1}\
Requires: %{name}-%{1}-modules-uname-r = %{KVERREL}+%{1}\
Provides: installonlypkg(kernel)\
Provides: installonlypkg(kernel-ml)\
%description %{1}\
The meta-package for the %{1} %{name}.\
%{nil}

#
# This macro creates a kernel-ml-<subpackage> and its -devel.
#	%%define variant_summary The Linux kernel-ml compiled for <configuration>
#	%%kernel_ml_variant_package [-n <pretty-name>] [-m] <subpackage>
#
%define kernel_ml_variant_package(n:m) \
%package %{?1:%{1}-}core\
Summary: %{variant_summary}.\
Provides: %{name}-%{?1:%{1}-}core-uname-r = %{KVERREL}%{?1:+%{1}}\
Provides: installonlypkg(kernel)\
Provides: installonlypkg(kernel-ml)\
%if %{-m:1}%{!-m:0}\
Requires: %{name}-core-uname-r = %{KVERREL}\
%endif\
%{expand:%%kernel_ml_reqprovconf}\
%if %{?1:1} %{!?1:0} \
%{expand:%%kernel_ml_meta_package %{?1:%{1}}}\
%endif\
%{expand:%%kernel_ml_devel_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}} %{-m:%{-m}}}\
%{expand:%%kernel_ml_devel_matched_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}} %{-m:%{-m}}}\
%{expand:%%kernel_ml_modules_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}} %{-m:%{-m}}}\
%{expand:%%kernel_ml_modules_extra_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}} %{-m:%{-m}}}\
%{nil}

# And, finally, the main -core package.

%define variant_summary The Linux kernel.
%kernel_ml_variant_package
%description core
The %{name} package contains the Linux kernel (vmlinuz), the core of any
Linux kernel based operating system. The %{name} package handles the basic
functions of the operating system: memory allocation, process allocation,
device input and output, etc.

# Disable the building of the debug package(s).
%global debug_package %{nil}

# Disable the creation of build_id symbolic links.
%global _build_id_links none

# Set up our "big" %%{make} macro.
%global make %{__make} -s HOSTCFLAGS="%{?build_cflags}" HOSTLDFLAGS="%{?build_ldflags}"

%prep
%ifarch x86_64 || aarch64
%if %{with_baseonly}
%if !%{with_std}
echo "Cannot build --with baseonly as the standard build is currently disabled."
exit 1
%endif
%endif
%endif

%setup -q -n %{name}-%{version} -c
mv linux-%{LKAver} linux-%{KVERREL}

pushd linux-%{KVERREL} > /dev/null

# Purge the source tree of all unrequired dot-files.
find . -name '.*' -type f -delete

# Mangle all Python shebangs to be Python 3 explicitly.
# -i specifies the interpreter for the shebang
# -n prevents creating ~backup files
# -p preserves timestamps
# This fixes errors such as
# *** ERROR: ambiguous python shebang in /usr/bin/kvm_stat: #!/usr/bin/python. Change it to python3 (or python2) explicitly.

# We patch all sources below for which we got a report/error.
## %%{log_msg "Fixing Python shebangs..."}
%py3_shebang_fix \
        tools/kvm/kvm_stat/kvm_stat \
        scripts/show_delta \
        scripts/diffconfig \
        scripts/bloat-o-meter \
        scripts/jobserver-exec \
        tools \
        Documentation \
        scripts/clang-tools 2> /dev/null


mv COPYING COPYING-%{version}-%{release}

cp -a %{SOURCE2} .

# Set the EXTRAVERSION string in the top level Makefile.
sed -i "s@^EXTRAVERSION.*@EXTRAVERSION = -%{release}.%{_target_cpu}@" Makefile

%ifarch x86_64 || aarch64
cp config-%{version}-%{_target_cpu} .config
%{__make} -s ARCH=%{bldarch} listnewconfig | grep -E '^CONFIG_' > newoptions-el-%{_target_cpu}.txt || true
if [ -s newoptions-el10-%{_target_cpu}.txt ]; then
	cat newoptions-el10-%{_target_cpu}.txt
	exit 1
fi
rm -f newoptions-el10-%{_target_cpu}.txt
%endif

# Adjust the FIPS module name for RHEL9.
for i in config-%{version}-*; do
	sed -i 's@CONFIG_CRYPTO_FIPS_NAME=.*@CONFIG_CRYPTO_FIPS_NAME="Red Hat Enterprise Linux 9 - Kernel Cryptographic API"@' $i
done

%{__make} -s distclean

popd > /dev/null

%build
pushd linux-%{KVERREL} > /dev/null

%ifarch x86_64 || aarch64
cp config-%{version}-%{_target_cpu} .config

%{__make} -s ARCH=%{bldarch} oldconfig


%if %{with_std}
%{make} %{?_smp_mflags} ARCH=%{bldarch} %{make_target}

%{make} %{?_smp_mflags} ARCH=%{bldarch} modules || exit 1

%ifarch aarch64
%{make} %{?_smp_mflags} ARCH=%{bldarch} dtbs
%endif

%endif

%if %{with_perf}
%ifarch aarch64
%global perf_build_extra_opts CORESIGHT=1
%endif

%global perf_make \
	%{__make} -s EXTRA_CFLAGS="%{?build_cflags}" EXTRA_CXXFLAGS="%{?build_cxxflags}"  LDFLAGS="%{?build_ldflags} -Wl,-E" -C tools/perf V=1 NO_PERF_READ_VDSO32=1 NO_PERF_READ_VDSOX32=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_STRLCPY=1 NO_BIONIC=1 LIBBPF_DYNAMIC=1 LIBTRACEEVENT_DYNAMIC=1 %{?perf_build_extra_opts} prefix=%{_prefix} PYTHON=%{__python3}

# Make sure that check-headers.sh is executable.
chmod +x tools/perf/check-headers.sh

%{perf_make} all

%global libperf_make \
	%{make} EXTRA_CFLAGS="%{?build_cflags}" LDFLAGS="%{?build_ldflags}" -C tools/lib/perf

# with_perf
%endif

%global tools_make \
  CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}" EXTRA_CFLAGS="${RPM_OPT_FLAGS}" %{make} %{?make_opts}

# link against in-tree libcpupower for idle state support
%global rtla_make %{tools_make} LDFLAGS="%{__global_ldflags} -L../../power/cpupower" INCLUDES="-I../../power/cpupower/lib"

%if %{with_tools}
# Make sure that version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
%{tools_make} %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false DEBUG=false

%ifarch x86_64
   pushd tools/power/cpupower/debug/x86_64
   %{tools_make} centrino-decode powernow-k8-decode
   popd
   pushd tools/power/x86/x86_energy_perf_policy/
   %{tools_make}
   popd
   pushd tools/power/x86/turbostat
   %{tools_make}
   popd
   pushd tools/power/x86/intel-speed-select
   %{tools_make}
   popd
   pushd tools/arch/x86/intel_sdsi
   %{tools_make} CFLAGS="${RPM_OPT_FLAGS}"
   popd
%endif

pushd tools/thermal/tmon/
%{tools_make}
popd
pushd tools/bootconfig/
%{tools_make}
popd
pushd tools/iio/
%{tools_make}
popd
pushd tools/gpio/
%{tools_make}
popd

# build VM tools
pushd tools/mm/
%{tools_make} slabinfo page_owner_sort
popd
pushd tools/verification/rv/
%{tools_make}
popd
pushd tools/tracing/rtla
%{rtla_make}
popd

%endif

%endif

popd > /dev/null

%install
%define __modsign_install_post \
if [ "%{zipmodules}" -eq "1" ]; then \
	find %{buildroot}/lib/modules/ -name '*.ko' -type f | xargs --no-run-if-empty -P%{zcpu} xz \
fi \
%{nil}

#
# Ensure modules are signed *after* all invocations of
# strip have occured, which are in __os_install_post.
#
%define __spec_install_post \
	%{__arch_install_post}\
	%{__os_install_post}\
	%{__modsign_install_post}

pushd linux-%{KVERREL} > /dev/null

rm -fr %{buildroot}

%ifarch x86_64 || aarch64
mkdir -p %{buildroot}

%if %{with_std}
mkdir -p %{buildroot}/boot
mkdir -p %{buildroot}%{_libexecdir}
mkdir -p %{buildroot}/lib/modules/%{KVERREL}
mkdir -p %{buildroot}/lib/modules/%{KVERREL}/systemtap

%ifarch aarch64
%{make} ARCH=%{bldarch} dtbs_install INSTALL_DTBS_PATH=%{buildroot}/boot/dtb-%{KVERREL}
cp -r %{buildroot}/boot/dtb-%{KVERREL} %{buildroot}/lib/modules/%{KVERREL}/dtb
find arch/%{bldarch}/boot/dts -name '*.dtb' -type f -delete
%endif

# Install the results within the RPM_BUILD_ROOT directory.
%{__install} -m 644 .config %{buildroot}/boot/config-%{KVERREL}
%{__install} -m 644 .config %{buildroot}/lib/modules/%{KVERREL}/config
%{__install} -m 644 System.map %{buildroot}/boot/System.map-%{KVERREL}
%{__install} -m 644 System.map %{buildroot}/lib/modules/%{KVERREL}/System.map

# We estimate the size of the initramfs because rpm needs to take this size
# into consideration when performing disk space calculations. (See bz #530778)
dd if=/dev/zero of=%{buildroot}/boot/initramfs-%{KVERREL}.img bs=1M count=20


cp %{kernel_image} %{buildroot}/boot/vmlinuz-%{KVERREL}
chmod 755 %{buildroot}/boot/vmlinuz-%{KVERREL}
cp %{buildroot}/boot/vmlinuz-%{KVERREL} %{buildroot}/lib/modules/%{KVERREL}/vmlinuz

sha512hmac %{buildroot}/boot/vmlinuz-%{KVERREL} | sed -e "s,%{buildroot},," > %{buildroot}/boot/.vmlinuz-%{KVERREL}.hmac
cp %{buildroot}/boot/.vmlinuz-%{KVERREL}.hmac %{buildroot}/lib/modules/%{KVERREL}/.vmlinuz.hmac

# Override mod-fw because we don't want it to install any firmware.
# We'll get it from the linux-firmware package and we don't want conflicts.
%{make} %{?_smp_mflags} ARCH=%{bldarch} INSTALL_MOD_PATH=%{buildroot} modules_install KERNELRELEASE=%{KVERREL} mod-fw=
    
# Add a noop %%defattr statement because rpm doesn't like empty file list files.
echo '%%defattr(-,-,-)' > ../%{name}-ldsoconf.list

%if %{with_vdso_install}
%{make} %{?_smp_mflags} ARCH=%{bldarch} INSTALL_MOD_PATH=%{buildroot} vdso_install KERNELRELEASE=%{KVERREL}

if [ -s ldconfig-%{name}.conf ]; then
	install -D -m 444 ldconfig-%{name}.conf %{buildroot}/etc/ld.so.conf.d/%{name}-%{KVERREL}.conf
	echo /etc/ld.so.conf.d/%{name}-%{KVERREL}.conf >> ../%{name}-ldsoconf.list
fi
%endif

#
# This looks scary but the end result is supposed to be:
#
# - all arch relevant include/ files.
# - all Makefile and Kconfig files.
# - all script/ files.
#
rm -f %{buildroot}/lib/modules/%{KVERREL}/build
rm -f %{buildroot}/lib/modules/%{KVERREL}/source
mkdir -p %{buildroot}/lib/modules/%{KVERREL}/build

pushd %{buildroot}/lib/modules/%{KVERREL} > /dev/null
ln -s build source
popd > /dev/null

mkdir -p %{buildroot}/lib/modules/%{KVERREL}/updates
mkdir -p %{buildroot}/lib/modules/%{KVERREL}/weak-updates

# CONFIG_KERNEL_HEADER_TEST generates some extra files during testing so just delete them.
find . -name *.h.s -delete

# First copy everything . . .
cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` %{buildroot}/lib/modules/%{KVERREL}/build

if [ ! -e Module.symvers ]; then
	touch Module.symvers
fi

cp Module.symvers %{buildroot}/lib/modules/%{KVERREL}/build
cp System.map %{buildroot}/lib/modules/%{KVERREL}/build

if [ -s Module.markers ]; then
	cp Module.markers %{buildroot}/lib/modules/%{KVERREL}/build
fi

gzip -c9 < Module.symvers > %{buildroot}/boot/symvers-%{KVERREL}.gz
cp %{buildroot}/boot/symvers-%{KVERREL}.gz %{buildroot}/lib/modules/%{KVERREL}/symvers.gz

# . . . then drop all but the needed Makefiles and Kconfig files.
rm -fr %{buildroot}/lib/modules/%{KVERREL}/build/scripts
rm -fr %{buildroot}/lib/modules/%{KVERREL}/build/include
cp .config %{buildroot}/lib/modules/%{KVERREL}/build
cp -a scripts %{buildroot}/lib/modules/%{KVERREL}/build
rm -fr %{buildroot}/lib/modules/%{KVERREL}/build/scripts/tracing
rm -f %{buildroot}/lib/modules/%{KVERREL}/build/scripts/spdxcheck.py

# Files for 'make scripts' to succeed with kernel-ml-devel.
mkdir -p %{buildroot}/lib/modules/%{KVERREL}/build/security/selinux/include
cp -a --parents security/selinux/include/classmap.h %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents security/selinux/include/initial_sid_to_string.h %{buildroot}/lib/modules/%{KVERREL}/build
mkdir -p %{buildroot}/lib/modules/%{KVERREL}/build/tools/include/tools
cp -a --parents tools/include/tools/be_byteshift.h %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/include/tools/le_byteshift.h %{buildroot}/lib/modules/%{KVERREL}/build

# Files for 'make prepare' to succeed with kernel-ml-devel.
cp -a --parents tools/include/linux/compiler* %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/include/linux/types.h %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/build/Build.include %{buildroot}/lib/modules/%{KVERREL}/build
# cp --parents tools/build/Build %{buildroot}/lib/modules/%{KVERREL}/build
cp --parents tools/build/fixdep.c %{buildroot}/lib/modules/%{KVERREL}/build
cp --parents tools/objtool/sync-check.sh %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/bpf/resolve_btfids %{buildroot}/lib/modules/%{KVERREL}/build

cp --parents security/selinux/include/policycap_names.h %{buildroot}/lib/modules/%{KVERREL}/build
cp --parents security/selinux/include/policycap.h %{buildroot}/lib/modules/%{KVERREL}/build

cp -a --parents tools/include/asm-generic %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/include/linux %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/include/uapi/asm %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/include/uapi/asm-generic %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/include/uapi/linux %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/include/vdso %{buildroot}/lib/modules/%{KVERREL}/build
cp --parents tools/scripts/utilities.mak %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/lib/subcmd %{buildroot}/lib/modules/%{KVERREL}/build
cp --parents tools/lib/*.c %{buildroot}/lib/modules/%{KVERREL}/build
cp --parents tools/objtool/*.[ch] %{buildroot}/lib/modules/%{KVERREL}/build
cp --parents tools/objtool/Build %{buildroot}/lib/modules/%{KVERREL}/build
cp --parents tools/objtool/include/objtool/*.h %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/lib/bpf %{buildroot}/lib/modules/%{KVERREL}/build
cp --parents tools/lib/bpf/Build %{buildroot}/lib/modules/%{KVERREL}/build

if [ -f tools/objtool/objtool ]; then
	cp -a tools/objtool/objtool %{buildroot}/lib/modules/%{KVERREL}/build/tools/objtool/ || :
fi
if [ -f tools/objtool/fixdep ]; then
	cp -a tools/objtool/fixdep %{buildroot}/lib/modules/%{KVERREL}/build/tools/objtool/ || :
fi
if [ -d arch/%{bldarch}/scripts ]; then
	cp -a arch/%{bldarch}/scripts %{buildroot}/lib/modules/%{KVERREL}/build/arch/%{_arch} || :
fi
if [ -f arch/%{bldarch}/*lds ]; then
	cp -a arch/%{bldarch}/*lds %{buildroot}/lib/modules/%{KVERREL}/build/arch/%{_arch}/ || :
fi
if [ -f arch/%{asmarch}/kernel/module.lds ]; then
	cp -a --parents arch/%{asmarch}/kernel/module.lds %{buildroot}/lib/modules/%{KVERREL}/build/
fi

find %{buildroot}/lib/modules/%{KVERREL}/build/scripts \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +

if [ -d arch/%{asmarch}/include ]; then
	cp -a --parents arch/%{asmarch}/include %{buildroot}/lib/modules/%{KVERREL}/build/
fi

%ifarch aarch64
# arch/arm64/include/asm/xen references arch/arm
cp -a --parents arch/arm/include/asm/xen %{buildroot}/lib/modules/%{KVERREL}/build/
# arch/arm64/include/asm/opcodes.h references arch/arm
cp -a --parents arch/arm/include/asm/opcodes.h %{buildroot}/lib/modules/%{KVERREL}/build/
%endif

cp -a include %{buildroot}/lib/modules/%{KVERREL}/build/include

%ifarch x86_64
# Files required for 'make prepare' to succeed with kernel-ml-devel.
cp -a --parents arch/x86/entry/syscalls/syscall_32.tbl %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents arch/x86/entry/syscalls/syscall_64.tbl %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents arch/x86/tools/relocs_32.c %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents arch/x86/tools/relocs_64.c %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents arch/x86/tools/relocs.c %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents arch/x86/tools/relocs_common.c %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents arch/x86/tools/relocs.h %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents arch/x86/purgatory/purgatory.c %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents arch/x86/purgatory/stack.S %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents arch/x86/purgatory/setup-x86_64.S %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents arch/x86/purgatory/entry64.S %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents arch/x86/boot/string.h %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents arch/x86/boot/string.c %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents arch/x86/boot/ctype.h %{buildroot}/lib/modules/%{KVERREL}/build/

cp -a --parents scripts/syscalltbl.sh %{buildroot}/lib/modules/%{KVERREL}/build/
cp -a --parents scripts/syscallhdr.sh %{buildroot}/lib/modules/%{KVERREL}/build/

cp -a --parents tools/arch/x86/include/asm %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/arch/x86/include/uapi/asm %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/objtool/arch/x86/lib %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/arch/x86/lib/ %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/arch/x86/tools/gen-insn-attr-x86.awk %{buildroot}/lib/modules/%{KVERREL}/build
cp -a --parents tools/objtool/arch/x86/ %{buildroot}/lib/modules/%{KVERREL}/build
%endif

# Clean up the intermediate tools files.
find %{buildroot}/lib/modules/%{KVERREL}/build/tools \( -iname "*.o" -o -iname "*.cmd" \) -exec rm -f {} +

# Make sure that the Makefile and the version.h file have a matching timestamp
# so that external modules can be built.
touch -r %{buildroot}/lib/modules/%{KVERREL}/build/Makefile \
	%{buildroot}/lib/modules/%{KVERREL}/build/include/generated/uapi/linux/version.h

find %{buildroot}/lib/modules/%{KVERREL} -name "*.ko" -type f > modnames

# Mark the modules executable, so that strip-to-file can strip them.
xargs --no-run-if-empty chmod u+x < modnames

# Generate a list of modules for block and networking.
grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA | \
	sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

collect_modules_list()
{
	sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef | \
		LC_ALL=C sort -u > %{buildroot}/lib/modules/%{KVERREL}/modules.$1

	if [ ! -z "$3" ]; then
		sed -r -e "/^($3)\$/d" -i %{buildroot}/lib/modules/%{KVERREL}/modules.$1
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
( find %{buildroot}/lib/modules/%{KVERREL} -name '*.ko' -type f | xargs --no-run-if-empty /sbin/modinfo -l | \
	grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' ) && exit 1

remove_depmod_files()
{
	# Remove all the files that will be auto generated by depmod at the kernel install time.
	pushd %{buildroot}/lib/modules/%{KVERREL} > /dev/null
	rm -f modules.{alias,alias.bin,builtin.alias.bin,builtin.bin} \
		modules.{dep,dep.bin,devname,softdep,symbols,symbols.bin}
	popd > /dev/null
}

remove_depmod_files

# Identify modules in the kernel-ml-modules-extras package
%{SOURCE20} %{buildroot} lib/modules/%{KVERREL} %{SOURCE26}

#
# Generate the kernel-ml-core and kernel-ml-modules file lists.
#

# Make a copy of the System.map file for depmod to use.
cp System.map %{buildroot}/

pushd %{buildroot} > /dev/null

# Create a backup of the full module tree so it can be
# restored after the filtering has been completed.
mkdir restore
cp -r lib/modules/%{KVERREL}/* restore/

# Don't include anything going into kernel-ml-modules-extra in the file lists.
xargs rm -fr < mod-extra.list

# Find all the module files and filter them out into the core and modules lists.
# This actually removes anything going into kernel-ml-modules from the directory.
find lib/modules/%{KVERREL}/kernel -name *.ko -type f | sort -n > modules.list
cp $RPM_SOURCE_DIR/filter-*.sh .
./filter-modules.sh modules.list %{_target_cpu}
rm -f filter-*.sh

# Go back and find all of the various directories in the tree.
# We use this for the directory lists in kernel-ml-core.
find lib/modules/%{KVERREL}/kernel -mindepth 1 -type d | sort -n > module-dirs.list

# Cleanup.
rm -f System.map
cp -r restore/* lib/modules/%{KVERREL}/
rm -fr restore

popd > /dev/null

# Make sure that the files lists start with absolute paths or rpmbuild fails.
# Also add in the directory entries.
sed -e 's/^lib*/\/lib/' %{?zipsed} %{buildroot}/k-d.list > ../%{name}-modules.list
sed -e 's/^lib*/%dir \/lib/' %{?zipsed} %{buildroot}/module-dirs.list > ../%{name}-core.list
sed -e 's/^lib*/\/lib/' %{?zipsed} %{buildroot}/modules.list >> ../%{name}-core.list
sed -e 's/^lib*/\/lib/' %{?zipsed} %{buildroot}/mod-extra.list >> ../%{name}-modules-extra.list

# Cleanup.
rm -f %{buildroot}/k-d.list
rm -f %{buildroot}/module-dirs.list
rm -f %{buildroot}/modules.list
rm -f %{buildroot}/mod-extra.list

# Move the development files out of the /lib/modules/ file system.
mkdir -p %{buildroot}/usr/src/kernels
mv %{buildroot}/lib/modules/%{KVERREL}/build %{buildroot}/usr/src/kernels/%{KVERREL}

# This is going to create a broken link during the build but we don't use
# it after this point. We need the link to actually point to something
# for when the kernel-ml-devel package is installed.
ln -sf /usr/src/kernels/%{KVERREL} %{buildroot}/lib/modules/%{KVERREL}/build

# Move the generated vmlinux.h file into the kernel-ml-devel directory structure.
### if [ -f tools/bpf/bpftool/vmlinux.h ]; then
###	mv tools/bpf/bpftool/vmlinux.h %{buildroot}/usr/src/kernels/%{KVERREL}/
### fi

# Purge the kernel-ml-devel tree of leftover junk.
find %{buildroot}/usr/src/kernels -name ".*.cmd" -type f -delete

%endif

# We have to do the headers install before the tools install because the
# kernel-ml headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}
# Install kernel-ml headers
%{__make} -s ARCH=%{hdrarch} INSTALL_HDR_PATH=%{buildroot}/usr headers_install

find %{buildroot}/usr/include \
  \( -name .install -o -name .check -o \
     -name ..install.cmd -o -name ..check.cmd \) -delete
%endif

%if %{with_cross_headers}
HDR_ARCH_LIST='arm64 powerpc s390 x86 riscv'
mkdir -p %{buildroot}/usr/tmp-headers

for arch in $HDR_ARCH_LIST; do
	mkdir %{buildroot}/usr/tmp-headers/arch-${arch}
	%{__make} ARCH=${arch} INSTALL_HDR_PATH=%{buildroot}/usr/tmp-headers/arch-${arch} headers_install
done

find %{buildroot}/usr/tmp-headers \
     \( -name .install -o -name .check -o \
        -name ..install.cmd -o -name ..check.cmd \) -delete

# Copy all the architectures we care about to their respective asm directories
for arch in $HDR_ARCH_LIST ; do
	mkdir -p %{buildroot}/usr/${arch}-linux-gnu/include
	mv %{buildroot}/usr/tmp-headers/arch-${arch}/include/* %{buildroot}/usr/${arch}-linux-gnu/include/
done

rm -rf %{buildroot}/usr/tmp-headers
%endif

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=%{buildroot} lib=%{_lib} install-bin
%{__install} -m 644 -D -t %{buildroot}/%{_docdir}/perf tools/perf/Documentation/examples.txt
# Remove the 'trace' symlink.
rm -f %{buildroot}%{_bindir}/trace

# For both of the below, yes, this should be using a macro but right now
# it's hard coded and we don't actually want it anyway.
# Remove examples.
rm -fr %{buildroot}/usr/lib/perf/examples
rm -fr %{buildroot}/usr/lib/perf/include

# python-perf extension
%{perf_make} DESTDIR=%{buildroot} install-python_ext

# perf man pages (note: implicit rpm magic compresses them later)
mkdir -p %{buildroot}%{_mandir}/man1
%{perf_make} DESTDIR=%{buildroot} install-man

# Remove any tracevent files, eg. its plugins still gets built and installed,
# even if we build against system's libtracevent during perf build (by setting
# LIBTRACEEVENT_DYNAMIC=1 above in perf_make macro). Those files should already
# ship with libtraceevent package.
rm -fr %{buildroot}%{_libdir}/traceevent

# libperf
%{libperf_make} -j 1 DESTDIR=%{buildroot} prefix=%{_prefix} libdir=%{_libdir} install install_headers

%endif

%if %{with_tools}
%{__make} -s -C tools/power/cpupower DESTDIR=%{buildroot} libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install

%{__rm} -f $RPM_BUILD_ROOT%{_libdir}/*.{a,la}
%{__rm} -f $RPM_BUILD_ROOT%{_sysconfdir}/cpupower-service.conf
%{__rm} -f $RPM_BUILD_ROOT%{_libexecdir}/cpupower
%{__rm} -f $RPM_BUILD_ROOT%{_unitdir}/cpupower.service

%find_lang cpupower
mv cpupower.lang ../

%ifarch x86_64
pushd tools/power/cpupower/debug/x86_64 > /dev/null
%{__install} -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
%{__install} -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
popd > /dev/null
%endif

chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig

%ifarch x86_64
mkdir -p %{buildroot}%{_mandir}/man8
pushd tools/power/x86/x86_energy_perf_policy > /dev/null
%{__make} -s %{?_smp_mflags} DESTDIR=%{buildroot} install
popd > /dev/null

pushd tools/power/x86/turbostat > /dev/null
%{__make} -s %{?_smp_mflags} DESTDIR=%{buildroot} install
popd > /dev/null

pushd tools/power/x86/intel-speed-select > /dev/null
%{__make} -s %{?_smp_mflags} DESTDIR=%{buildroot} install
popd > /dev/null
%endif

pushd tools/thermal/tmon > /dev/null
%{__make} -s %{?_smp_mflags} INSTALL_ROOT=%{buildroot} install
popd > /dev/null

pushd tools/iio > /dev/null
%{__make} -s %{?_smp_mflags} DESTDIR=%{buildroot} install
popd > /dev/null

pushd tools/gpio > /dev/null
%{__make} -s %{?_smp_mflags} DESTDIR=%{buildroot} install
popd > /dev/null

%{__install} -m644 -D %{SOURCE2002} %{buildroot}%{_sysconfdir}/logrotate.d/kvm_stat

pushd tools/kvm/kvm_stat > /dev/null
%{__make} -s INSTALL_ROOT=%{buildroot} install-tools
%{__make} -s INSTALL_ROOT=%{buildroot} install-man
%{__install} -m644 -D kvm_stat.service %{buildroot}%{_unitdir}/kvm_stat.service
popd > /dev/null

# install VM tools
pushd tools/mm/
%{__install} -m755 slabinfo %{buildroot}%{_bindir}/slabinfo
%{__install} -m755 page_owner_sort %{buildroot}%{_bindir}/page_owner_sort
popd
pushd tools/verification/rv/
%{tools_make} DESTDIR=%{buildroot} install
popd
pushd tools/tracing/rtla/
%{tools_make} DESTDIR=%{buildroot} install
rm -f %{buildroot}%{_bindir}/hwnoise
rm -f %{buildroot}%{_bindir}/osnoise
rm -f %{buildroot}%{_bindir}/timerlat
(cd %{buildroot}

        ln -sf rtla ./%{_bindir}/hwnoise
        ln -sf rtla ./%{_bindir}/osnoise
        ln -sf rtla ./%{_bindir}/timerlat
)
popd

%endif

%endif

%ifarch noarch
mkdir -p %{buildroot}

%if %{with_doc}
# Sometimes non-world-readable files sneak into the kernel source tree.
chmod -R a=rX Documentation
find Documentation -type d | xargs --no-run-if-empty chmod u+w

DocDir=%{buildroot}%{_datadir}/doc/%{name}-doc-%{version}-%{release}

# Copy the source over.
mkdir -p $DocDir
tar -h -f - --exclude=man --exclude='.*' -c Documentation | tar xf - -C $DocDir
%endif
%endif

popd > /dev/null

###
### Scripts.
###
%if %{with_tools}
%post -n %{name}-tools-libs
/sbin/ldconfig

%postun -n %{name}-tools-libs
/sbin/ldconfig
%endif

#
# This macro defines a %%post script for a kernel-ml*-devel package.
#	%%kernel_ml_devel_post [<subpackage>]
# Note we don't run hardlink if ostree is in use, as ostree is
# a far more sophisticated hardlink implementation.
# https://github.com/projectatomic/rpm-ostree/commit/58a79056a889be8814aa51f507b2c7a4dccee526
#
%define kernel_ml_devel_post() \
%{expand:%%post %{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/bin/hardlink -a ! -e /run/ostree-booted ] \
then\
    (cd /usr/src/kernels/%{KVERREL}%{?1:+%{1}} &&\
        /usr/bin/find . -type f | while read f; do\
          hardlink -c /usr/src/kernels/*%{?dist}.*/$f $f > /dev/null\
        done)\
fi\
%{nil}

#
# This macro defines a %%post script for a kernel-ml*-modules-extra package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_ml_modules_extra_post [<subpackage>]
#
%define kernel_ml_modules_extra_post() \
%{expand:%%post %{?1:%{1}-}modules-extra}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules-extra}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

#
# This macro defines a %%post script for a kernel-ml*-modules package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_ml_modules_post [<subpackage>]
#
%define kernel_ml_modules_post() \
%{expand:%%post %{?1:%{1}-}modules}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
if [ ! -f %{_localstatedir}/lib/rpm-state/%{name}/installing_core_%{KVERREL}%{?1:+%{1}} ]; then\
	mkdir -p %{_localstatedir}/lib/rpm-state/%{name}\
	touch %{_localstatedir}/lib/rpm-state/%{name}/need_to_run_dracut_%{KVERREL}%{?1:+%{1}}\
fi\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%posttrans %{?1:%{1}-}modules}\
if [ -f %{_localstatedir}/lib/rpm-state/%{name}/need_to_run_dracut_%{KVERREL}%{?1:+%{1}} ]; then\
	rm -f %{_localstatedir}/lib/rpm-state/%{name}/need_to_run_dracut_%{KVERREL}%{?1:+%{1}}\
	echo "Running: dracut -f --kver %{KVERREL}%{?1:+%{1}}"\
	dracut -f --kver "%{KVERREL}%{?1:+%{1}}" || exit $?\
fi\
%{nil}

# This macro defines a %%posttrans script for a kernel-ml package.
#	%%kernel_ml_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_ml_variant_posttrans() \
%{expand:%%posttrans %{?1:%{1}-}core}\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --add-kernel %{KVERREL}%{?1:+%{1}} || exit $?\
fi\
rm -f %{_localstatedir}/lib/rpm-state/%{name}/installing_core_%{KVERREL}%{?-v:+%{-v*}}\
/bin/kernel-install add %{KVERREL}%{?1:+%{1}} /lib/modules/%{KVERREL}%{?1:+%{1}}/vmlinuz || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel-ml package and its devel package.
#	%%kernel_ml_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_ml_variant_post(v:r:) \
%{expand:%%kernel_ml_devel_post %{?-v*}}\
%{expand:%%kernel_ml_modules_post %{?-v*}}\
%{expand:%%kernel_ml_modules_extra_post %{?-v*}}\
%{expand:%%kernel_ml_variant_posttrans %{?-v*}}\
%{expand:%%post %{?-v*:%{-v*}-}core}\
%{-r:\
if [ `uname -i` == "x86_64" ] &&\
    [ -f /etc/sysconfig/kernel ]; then\
    /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=%{name}%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
mkdir -p %{_localstatedir}/lib/rpm-state/%{name}\
touch %{_localstatedir}/lib/rpm-state/%{name}/installing_core_%{KVERREL}%{?-v:+%{-v*}}\
%{nil}

#
# This macro defines a %%preun script for a kernel-ml package.
#	%%kernel_ml_variant_preun <subpackage>
#
%define kernel_ml_variant_preun() \
%{expand:%%preun %{?1:%{1}-}core}\
/bin/kernel-install remove %{KVERREL}%{?1:+%{1}} /lib/modules/%{KVERREL}%{?1:+%{1}}/vmlinuz || exit $?\
if [ -x %{_sbindir}/weak-modules ]\
then\
    %{_sbindir}/weak-modules --remove-kernel %{KVERREL}%{?1:+%{1}} || exit $?\
fi\
%{nil}

%kernel_ml_variant_preun
%kernel_ml_variant_post -r kernel-smp

if [ -x /sbin/ldconfig ]
then
    /sbin/ldconfig -X || exit $?
fi

###
### File lists.
###
%if %{with_headers}
%files headers
%{_includedir}/*
%exclude %{_includedir}/cpufreq.h
%endif

%if %{with_cross_headers}
%files cross-headers
%{_prefix}/*-linux-gnu/include/*
%endif

%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/%{name}-doc-%{version}-%{release}/Documentation/*
%dir %{_datadir}/doc/%{name}-doc-%{version}-%{release}/Documentation
%dir %{_datadir}/doc/%{name}-doc-%{version}-%{release}
%endif

%if %{with_perf}
%files -n perf
%{_bindir}/perf
%{_docdir}/perf*
%{_includedir}/perf/perf_dlfilter.h
%{_libdir}/libperf-jvmti.so
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf

%files -n python3-perf
%{python3_sitearch}/*

%files -n libperf
%{_libdir}/libperf.so.0
%{_libdir}/libperf.so.0.0.1

%files -n libperf-devel
%{_docdir}/libperf
%{_includedir}/internal/*.h
%{_includedir}/perf/bpf_perf.h
%{_includedir}/perf/core.h
%{_includedir}/perf/cpumap.h
%{_includedir}/perf/event.h
%{_includedir}/perf/evlist.h
%{_includedir}/perf/evsel.h
%{_includedir}/perf/mmap.h
%{_includedir}/perf/threadmap.h
%{_libdir}/libperf.so
%{_libdir}/pkgconfig/libperf.pc
%{_mandir}/man*/libperf*

%endif

%if %{with_tools}
%files -n %{name}-tools -f cpupower.lang
%{_bindir}/cpupower
%{_datadir}/bash-completion/completions/cpupower
%ifarch x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_mandir}/man[1-8]/cpupower*
%ifarch x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%{_bindir}/intel-speed-select
%endif
%{_bindir}/tmon
%{_bindir}/iio_event_monitor
%{_bindir}/iio_generic_buffer
%{_bindir}/lsiio
%{_bindir}/lsgpio
%{_bindir}/gpio-hammer
%{_bindir}/gpio-event-mon
%{_bindir}/gpio-watch
%{_mandir}/man1/kvm_stat*
%{_bindir}/kvm_stat
%{_unitdir}/kvm_stat.service
%config(noreplace) %{_sysconfdir}/logrotate.d/kvm_stat
%{_bindir}/page_owner_sort
%{_bindir}/slabinfo

%files -n %{name}-tools-libs
%{_libdir}/libcpupower.so.1
%{_libdir}/libcpupower.so.1.0.1

%files -n %{name}-tools-libs-devel
%{_includedir}/cpufreq.h
%{_includedir}/cpuidle.h
%{_includedir}/powercap.h
%{_libdir}/libcpupower.so

%files -n rtla
%{_bindir}/rtla
%{_bindir}/hwnoise
%{_bindir}/osnoise
%{_bindir}/timerlat
%{_mandir}/man1/rtla-hwnoise.1.gz
%{_mandir}/man1/rtla-osnoise-hist.1.gz
%{_mandir}/man1/rtla-osnoise-top.1.gz
%{_mandir}/man1/rtla-osnoise.1.gz
%{_mandir}/man1/rtla-timerlat-hist.1.gz
%{_mandir}/man1/rtla-timerlat-top.1.gz
%{_mandir}/man1/rtla-timerlat.1.gz
%{_mandir}/man1/rtla.1.gz

%files -n rv
%{_bindir}/rv
%{_mandir}/man1/rv-list.1.gz
%{_mandir}/man1/rv-mon-wip.1.gz
%{_mandir}/man1/rv-mon-wwnr.1.gz
%{_mandir}/man1/rv-mon.1.gz
%{_mandir}/man1/rv.1.gz
%{_mandir}/man1/rv-mon-sched.1.gz

# with_tools
%endif

# Empty meta-package.
%ifarch x86_64 || aarch64
%files
%endif

#
# This macro defines the %%files sections for a kernel-ml package
# and its devel package.
#	%%kernel_ml_variant_files [-k vmlinux] <use_vdso> <condition> <subpackage>
#
%define kernel_ml_variant_files(k:) \
%if %{2}\
%{expand:%%files -f %{name}-%{?3:%{3}-}core.list %{?1:-f %{name}-%{?3:%{3}-}ldsoconf.list} %{?3:%{3}-}core}\
%{!?_licensedir:%global license %%doc}\
%license linux-%{KVERREL}/COPYING-%{version}-%{release}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/%{?-k:%{-k*}}%{!?-k:vmlinuz}\
%ghost /boot/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?3:+%{3}}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/.vmlinuz.hmac \
%ghost /boot/.vmlinuz-%{KVERREL}%{?3:+%{3}}.hmac \
%ifarch aarch64\
/lib/modules/%{KVERREL}%{?3:+%{3}}/dtb \
%ghost /boot/dtb-%{KVERREL}%{?3:+%{3}} \
%endif\
%attr(0600, root, root) /lib/modules/%{KVERREL}%{?3:+%{3}}/System.map\
%ghost %attr(0600, root, root) /boot/System.map-%{KVERREL}%{?3:+%{3}}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/symvers.gz\
/lib/modules/%{KVERREL}%{?3:+%{3}}/config\
%ghost %attr(0600, root, root) /boot/symvers-%{KVERREL}%{?3:+%{3}}.gz\
%ghost %attr(0600, root, root) /boot/initramfs-%{KVERREL}%{?3:+%{3}}.img\
%ghost %attr(0644, root, root) /boot/config-%{KVERREL}%{?3:+%{3}}\
%dir /lib/modules\
%dir /lib/modules/%{KVERREL}%{?3:+%{3}}\
%dir /lib/modules/%{KVERREL}%{?3:+%{3}}/kernel\
/lib/modules/%{KVERREL}%{?3:+%{3}}/build\
/lib/modules/%{KVERREL}%{?3:+%{3}}/source\
/lib/modules/%{KVERREL}%{?3:+%{3}}/updates\
/lib/modules/%{KVERREL}%{?3:+%{3}}/weak-updates\
/lib/modules/%{KVERREL}%{?3:+%{3}}/systemtap\
%if %{1}\
/lib/modules/%{KVERREL}%{?3:+%{3}}/vdso\
%endif\
/lib/modules/%{KVERREL}%{?3:+%{3}}/modules.*\
%{expand:%%files -f %{name}-%{?3:%{3}-}modules.list %{?3:%{3}-}modules}\
%{expand:%%files %{?3:%{3}-}devel}\
%defverify(not mtime)\
/usr/src/kernels/%{KVERREL}%{?3:+%{3}}\
%{expand:%%files %{?3:%{3}-}devel-matched}\
%{expand:%%files -f %{name}-%{?3:%{3}-}modules-extra.list %{?3:%{3}-}modules-extra}\
%config(noreplace) /etc/modprobe.d/*-blacklist.conf\
%if %{?3:1} %{!?3:0}\
%{expand:%%files %{3}}\
%endif\
%endif\
%{nil}

%kernel_ml_variant_files %{_use_vdso} %{with_std}

%changelog
* Tue Sep 09 2025 Akemi Yagi <toracat@elrepo.org> - 6.16.6-1
- Updated with the 6.16.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.16.6]

* Thu Sep 04 2025 Akemi Yagi <toracat@elrepo.org> - 6.16.5-1
- Updated with the 6.16.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.16.5]

* Fri Aug 29 2025 Akemi Yagi <toracat@elrepo.org> - 6.16.4-1.1
- Config reverted to 6.16.3

* Thu Aug 28 2025 Akemi Yagi <toracat@elrepo.org> - 6.16.4-1
- Updated with the 6.16.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.16.4]

* Sat Aug 23 2025 Akemi Yagi <toracat@elrepo.org> - 6.16.3-1
- Updated with the 6.16.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.16.3]

* Wed Aug 20 2025 Akemi Yagi <toracat@elrepo.org> - 6.16.2-1
- Updated with the 6.16.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.16.2]
- Enable SND_SOC_SOF_AMD_ACP63 etc.
  [https://elrepo.org/bugs/view.php?id=1557]

* Fri Aug 15 2025 Akemi Yagi <toracat@elrepo.org> - 6.16.1-1
- Updated with the 6.16.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.16.1]

* Sun Jul 27 2025 Akemi Yagi <toracat@elrepo.org> - 6.16.0-1
- Updated with the 6.16 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.16]

* Thu Jul 24 2025 Akemi Yagi <toracat@elrepo.org> - 6.15.8-1
- Updated with the 6.15.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.15.8]

* Thu Jul 17 2025 Akemi Yagi <toracat@elrepo.org> - 6.15.7-1
- Updated with the 6.15.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.15.7]

* Thu Jul 10 2025 Akemi Yagi <toracat@elrepo.org> - 6.15.6-1
- Updated with the 6.15.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.15.6]

* Sun Jul 06 2025 Akemi Yagi <toracat@elrepo.org> - 6.15.5-1
- Updated with the 6.15.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.15.5]

* Fri Jun 27 2025 Akemi Yagi <toracat@elrepo.org> - 6.15.4-1
- Updated with the 6.15.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.15.4]

* Thu Jun 19 2025 Akemi Yagi <toracat@elrepo.org> - 6.15.3-1
- Updated with the 6.15.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.15.3]

* Tue Jun 10 2025 Akemi Yagi <toracat@elrepo.org> - 6.15.2-1
- Updated with the 6.15.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.15.2]

* Thu Jun 05 2025 Akemi Yagi <toracat@elrepo.org> - 6.15.1-1
- Updated with the 6.15.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.15.1]

* Tue Jun 03 2025 Akemi Yagi <toracat@elrepo.org> - 6.14.9-1
- Updated with the 6.14.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.14.9]

* Thu May 22 2025 Akemi Yagi <toracat@elrepo.org> - 6.14.8-1
- Updated with the 6.14.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.14.8]

* Sun May 18 2025 Akemi Yagi <toracat@elrepo.org> - 6.14.7-1
- Updated with the 6.14.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.14.7]

* Fri May 09 2025 Akemi Yagi <toracat@elrepo.org> - 6.14.6-1
- Updated with the 6.14.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.14.6]

* Fri May 02 2025 Akemi Yagi <toracat@elrepo.org> - 6.14.5-1
- Updated with the 6.14.5 source tarball.
- Revert libxslt to the current version.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.14.5]

* Fri Apr 25 2025 Akemi Yagi <toracat@elrepo.org> - 6.14.4-1
- Updated with the 6.14.4 source tarball.
- Use a lower version of libxslt.
  https://access.redhat.com/solutions/7117163
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.14.4]

* Sun Apr 20 2025 Akemi Yagi <toracat@elrepo.org> - 6.14.3-1
- Updated with the 6.14.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.14.3]

* Wed Apr 16 2025 Akemi Yagi <toracat@elrepo.org> - 6.14.2-2
- Upgraded from el9 to el10

* Thu Apr 10 2025 Akemi Yagi <toracat@elrepo.org> - 6.14.2-1
- Updated with the 6.14.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.14.2]

* Mon Apr 07 2025 Akemi Yagi <toracat@elrepo.org> - 6.14.1-1
- Updated with the 6.14.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.14.1]

* Mon Mar 24 2025 Akemi Yagi <toracat@elrepo.org> - 6.14.0-1
- Updated with the 6.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.14]

* Sat Mar 22 2025 Akemi Yagi <toracat@elrepo.org> - 6.13.8-1
- Updated with the 6.13.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.13.8]

* Thu Mar 13 2025 Akemi Yagi <toracat@elrepo.org> - 6.13.7-1
- Updated with the 6.13.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.13.7]

* Fri Mar 07 2025 Akemi Yagi <toracat@elrepo.org> - 6.13.6-1
- Updated with the 6.13.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.13.6]

* Thu Feb 27 2025 Akemi Yagi <toracat@elrepo.org> - 6.13.5-1
- Updated with the 6.13.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.13.5]

* Fri Feb 21 2025 Akemi Yagi <toracat@elrepo.org> - 6.13.4-1
- Updated with the 6.13.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.13.4]

* Mon Feb 17 2025 Akemi Yagi <toracat@elrepo.org> - 6.13.3-1
- Updated with the 6.13.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.13.3]

* Sat Feb 08 2025 Akemi Yagi <toracat@elrepo.org> - 6.13.2-1
- Updated with the 6.13.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.13.2]

* Sat Feb 01 2025 Akemi Yagi <toracat@elrepo.org> - 6.13.1-1
- Updated with the 6.13.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.13.1]

* Thu Jan 23 2025 Akemi Yagi <toracat@elrepo.org> - 6.12.11-1
- Updated with the 6.12.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.12.11]

* Fri Jan 17 2025 Akemi Yagi <toracat@elrepo.org> - 6.12.10-1
- Updated with the 6.12.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.12.10]

* Thu Jan 09 2025 Akemi Yagi <toracat@elrepo.org> - 6.12.9-1
- Updated with the 6.12.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.12.9]

* Thu Jan 02 2025 Akemi Yagi <toracat@elrepo.org> - 6.12.8-1
- Updated with the 6.12.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.12.8]

* Fri Dec 27 2024 Akemi Yagi <toracat@elrepo.org> - 6.12.7-1
- Updated with the 6.12.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.12.7]

* Thu Dec 19 2024 Akemi Yagi <toracat@elrepo.org> - 6.12.6-1
- Updated with the 6.12.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.12.6]

* Sat Dec 14 2024 Akemi Yagi <toracat@elrepo.org> - 6.12.5-1
- Updated with the 6.12.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.12.5]

* Mon Dec 09 2024 Akemi Yagi <toracat@elrepo.org> - 6.12.4-1
- Updated with the 6.12.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.12.4]

* Fri Dec 06 2024 Akemi Yagi <toracat@elrepo.org> - 6.12.3-1
- Updated with the 6.12.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.12.3]

* Thu Dec 05 2024 Akemi Yagi <toracat@elrepo.org> - 6.12.2-1
- Updated with the 6.12.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.12.2]

* Fri Nov 22 2024 Akemi Yagi <toracat@elrepo.org> - 6.12.1-1
- Updated with the 6.12.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.12.1]
- Enabled DRBD
  [https://elrepo.org/bugs/view.php?id=1492]

* Sun Nov 17 2024 Akemi Yagi <toracat@elrepo.org> - 6.12.0-1
- Updated with the 6.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.12]

* Sun Nov 17 2024 Akemi Yagi <toracat@elrepo.org> - 6.11.9-1
- Updated with the 6.11.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.11.9]

* Thu Nov 14 2024 Akemi Yagi <toracat@elrepo.org> - 6.11.8-1
- Updated with the 6.11.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.11.8]

* Fri Nov 08 2024 Akemi Yagi <toracat@elrepo.org> - 6.11.7-1
- Updated with the 6.11.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.11.7]

* Thu Oct 31 2024 Akemi Yagi <toracat@elrepo.org> - 6.11.6-1
- Updated with the 6.11.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.11.6]

* Tue Oct 22 2024 Akemi Yagi <toracat@elrepo.org> - 6.11.5-1
- Updated with the 6.11.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.11.5]

* Thu Oct 17 2024 Akemi Yagi <toracat@elrepo.org> - 6.11.4-1
- Updated with the 6.11.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.11.4]

* Thu Oct 10 2024 Akemi Yagi <toracat@elrepo.org> - 6.11.3-1
- Updated with the 6.11.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.11.3]

* Fri Oct 04 2024 Akemi Yagi <toracat@elrepo.org> - 6.11.2-1
- Updated with the 6.11.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.11.2]

* Mon Sep 30 2024 Akemi Yagi <toracat@elrepo.org> - 6.11.1-1
- Updated with the 6.11.1 source tarball.
- Config mods as requested
  [https://elrepo.org/bugs/view.php?id=1483]  x86_64 only
  [https://elrepo.org/bugs/view.php?id=1484]  aarch64 only
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.11.1]

* Sun Sep 15 2024 Akemi Yagi <toracat@elrepo.org> - 6.11.0-1
- Updated with the 6.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.11]

* Thu Sep 12 2024 Akemi Yagi <toracat@elrepo.org> - 6.10.10-1
- Updated with the 6.10.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.10.10]

* Sun Sep 08 2024 Akemi Yagi <toracat@elrepo.org> - 6.10.9-1
- Updated with the 6.10.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.10.9]
- Add conflicts to -tools sections

* Wed Sep 04 2024 Akemi Yagi <toracat@elrepo.org> - 6.10.8-1
- Updated with the 6.10.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.10.8]

* Thu Aug 29 2024 Akemi Yagi <toracat@elrepo.org> - 6.10.7-1
- Updated with the 6.10.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.10.7]

* Sun Aug 18 2024 Akemi Yagi <toracat@elrepo.org> - 6.10.6-1
- Updated with the 6.10.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.10.6]
- Add OCP TimeCard driver support
  [https://elrepo.org/bugs/view.php?id=1475]

* Wed Aug 14 2024 Akemi Yagi <toracat@elrepo.org> - 6.10.5-1
- Updated with the 6.10.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.10.5]

* Sun Aug 11 2024 Akemi Yagi <toracat@elrepo.org> - 6.10.4-1
- Updated with the 6.10.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.10.4]

* Sat Aug 03 2024 Akemi Yagi <toracat@elrepo.org> - 6.10.3-1
- Updated with the 6.10.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.10.3]

* Sat Jul 27 2024 Akemi Yagi <toracat@elrepo.org> - 6.10.2-1
- Updated with the 6.10.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.10.2]

* Wed Jul 24 2024 Akemi Yagi <toracat@elrepo.org> - 6.10.1-1
- Updated with the 6.10.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.10.1]
- Enable MEI modules
  [https://elrepo.org/bugs/view.php?id=1470]

* Sun Jul 14 2024 Akemi Yagi <toracat@elrepo.org> - 6.10.0-1
- Updated with the 6.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.10]

* Thu Jul 11 2024 Akemi Yagi <toracat@elrepo.org> - 6.9.9-1
- Updated with the 6.9.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.9.9]

* Fri Jul 05 2024 Akemi Yagi <toracat@elrepo.org> - 6.9.8-1
- Updated with the 6.9.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.9.8]
- Enabled CONFIG_UNICODE
  [https://elrepo.org/bugs/view.php?id=1467]

* Thu Jun 27 2024 Akemi Yagi <toracat@elrepo.org> - 6.9.7-1
- Updated with the 6.9.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.9.7]

* Fri Jun 21 2024 Akemi Yagi <toracat@elrepo.org> - 6.9.6-1
- Updated with the 6.9.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.9.6]

* Sun Jun 16 2024 Akemi Yagi <toracat@elrepo.org> - 6.9.5-1
- Updated with the 6.9.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.9.5]

* Wed Jun 12 2024 Akemi Yagi <toracat@elrepo.org> - 6.9.4-1
- Updated with the 6.9.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.9.4]

* Thu May 30 2024 Akemi Yagi <toracat@elrepo.org> - 6.9.3-1
- Updated with the 6.9.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.9.3]

* Sat May 25 2024 Akemi Yagi <toracat@elrepo.org> - 6.9.2-1
- Updated with the 6.9.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.9.2]

* Sun May 19 2024 Akemi Yagi <toracat@elrepo.org> - 6.9.1-3
- Enable CONFIG_CORESIGHT=m

* Sat May 18 2024 Akemi Yagi <toracat@elrepo.org> - 6.9.1-2
- Config corrected [https://elrepo.org/bugs/view.php?id=1452]

* Fri May 17 2024 Akemi Yagi <toracat@elrepo.org> - 6.9.1-1
- Updated with the 6.9.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.9.1]

* Mon May 13 2024 Akemi Yagi <toracat@elrepo.org> - 6.9.0-1
- Updated with the 6.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.9]

* Thu May 02 2024 Akemi Yagi <toracat@elrepo.org> - 6.8.9-1
- Updated with the 6.8.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.8.9]

* Sat Apr 27 2024 Akemi Yagi <toracat@elrepo.org> - 6.8.8-1
- Updated with the 6.8.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.8.8]

* Wed Apr 17 2024 Akemi Yagi <toracat@elrepo.org> - 6.8.7-1
- Updated with the 6.8.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.8.7]

* Sat Apr 13 2024 Akemi Yagi <toracat@elrepo.org> - 6.8.6-1
- Updated with the 6.8.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.8.6]

* Wed Apr 10 2024 Akemi Yagi <toracat@elrepo.org> - 6.8.5-1
- Updated with the 6.8.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.8.5]

* Thu Apr 04 2024 Akemi Yagi <toracat@elrepo.org> - 6.8.4-1
- Updated with the 6.8.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.8.4]

* Wed Apr 03 2024 Akemi Yagi <toracat@elrepo.org> - 6.8.3-1
- Updated with the 6.8.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.8.3]

* Tue Mar 26 2024 Akemi Yagi <toracat@elrepo.org> - 6.8.2-1]
- Updated with the 6.8.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.8.2]

* Fri Mar 15 2024 Akemi Yagi <toracat@elrepo.org> - 6.8.1-1]
- Updated with the 6.8.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.8.1]

* Sun Mar 10 2024 Akemi Yagi <toracat@elrepo.org> - 6.8.0-1]
- Updated with the 6.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.8]

* Wed Mar 06 2024 Akemi Yagi <toracat@elrepo.org> - 6.7.9-1
- Updated with the 6.7.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.7.9]

* Sat Mar 02 2024 Akemi Yagi <toracat@elrepo.org> - 6.7.8-1
- Updated with the 6.7.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.7.8]

* Fri Mar 01 2024 Akemi Yagi <toracat@elrepo.org> - 6.7.7-1
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.7.7]

* Fri Feb 23 2024 Akemi Yagi <toracat@elrepo.org> - 6.7.6-1
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.7.6]
- Enable CONFIG_NFS_V2
  [https://elrepo.org/bugs/view.php?id=1431]

* Fri Feb 16 2024 Akemi Yagi <toracat@elrepo.org> - 6.7.5-1
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.7.5]

* Mon Feb 05 2024 Akemi Yagi <toracat@elrepo.org> - 6.7.4-1
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.7.4]

* Wed Jan 31 2024 Akemi Yagi <toracat@elrepo.org> - 6.7.3-1
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.7.3]

* Thu Jan 25 2024 Akemi Yagi <toracat@elrepo.org> - 6.7.2-1
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.7.2]

* Mon Jan 22 2024 Akemi Yagi <toracat@elrepo.org> - 6.7.1-2
- Enable SND_SOC_INTEL_SOUNDWIRE_SOF_MACH (x86_64)
  [https://elrepo.org/bugs/view.php?id=1421]

* Sat Jan 20 2024 Akemi Yagi <toracat@elrepo.org> - 6.7.1-1
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.7.1]

* Thu Jan 11 2024 Akemi Yagi <toracat@elrepo.org> - 6.7.0-3
- Enable UDMABUF
  [https://elrepo.org/bugs/view.php?id=1415]

* Tue Jan 09 2024 Akemi Yagi <toracat@elrepo.org> - 6.7.0-2
- Enable bcachefs filesystem support
  [https://elrepo.org/bugs/view.php?id=1414]

* Sun Jan 07 2024 Akemi Yagi <toracat@elrepo.org> - 6.7.0-1
- Updated with the 6.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.7]

* Fri Jan 05 2024 Akemi Yagi <toracat@elrepo.org> - 6.6.10-1
- Updated with the 6.6.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.10]

* Mon Jan 01 2024 Akemi Yagi <toracat@elrepo.org> - 6.6.9-1
- Updated with the 6.6.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.9]

* Wed Dec 20 2023 Akemi Yagi <toracat@elrepo.org> - 6.6.8-1
- Updated with the 6.6.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.8]

* Wed Dec 13 2023 Akemi Yagi <toracat@elrepo.org> - 6.6.7-1
- Updated with the 6.6.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.7]

* Mon Dec 11 2023 Akemi Yagi <toracat@elrepo.org> - 6.6.6-1
- Updated with the 6.6.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.6]

* Fri Dec 08 2023 Akemi Yagi <toracat@elrepo.org> - 6.6.5-1
- Updated with the 6.6.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.5]

* Sun Dec 03 2023 Akemi Yagi <toracat@elrepo.org> - 6.6.4-1
- Updated with the 6.6.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.4]

* Tue Nov 28 2023 Akemi Yagi <toracat@elrepo.org> - 6.6.3-1
- Updated with the 6.6.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.3]

* Mon Nov 20 2023 Akemi Yagi <toracat@elrepo.org> - 6.6.2-1
- Updated with the 6.6.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.2]

* Wed Nov 08 2023 Akemi Yagi <toracat@elrepo.org> - 6.6.1-1
- Updated with the 6.6.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.1]

* Mon Oct 30 2023 Akemi Yagi <toracat@elrepo.org> - 6.6.0-1
- Updated with the 6.6 source tarball.
- Provides: add distro kernel to kernel-devel.
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

* Wed Sep 13 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.3-1
- Updated with the 6.5.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.3]
- CONFIG_VIDEO_V4L2_SUBDEV_API=y
- CONFIG_VIDEO_CAMERA_SENSOR=y

* Wed Sep 06 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.2-1
- Updated with the 6.5.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.2]

* Sat Sep 02 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.1-1
- Updated with the 6.5.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.1]

* Sun Aug 27 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.0-1
- Updated with the 6.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5]
- CONFIG_DMA_BOUNCE_UNALIGNED_KMALLOC=y,  CONFIG_HAVE_HARDLOCKUP_DETECTOR_PERF=y,
- CONFIG_HAVE_PERF_EVENTS_NMI=y,  CONFIG_HAVE_SAMPLE_FTRACE_DIRECT_MULTI=y,
- CONFIG_HAVE_SAMPLE_FTRACE_DIRECT=y, CONFIG_HW_RANDOM_HISTB=y,
- CONFIG_INTERCONNECT_CLK=m,
- For aarch64 only.
- CONFIG_HARDLOCKUP_DETECTOR_COUNTS_HRTIMER=y, CONFIG_HOTPLUG_CORE_SYNC_FULL=y,
- CONFIG_X86_AMD_PSTATE_DEFAULT_MODE=3, CONFIG_HOTPLUG_PARALLEL=y,
- CONFIG_HOTPLUG_SPLIT_STARTUP=y,
- For x86_64 only.
- CONFIG_CACHESTAT_SYSCALL=y, CONFIG_CHECKSUM_KUNIT=m,
- CONFIG_CRYPTO_GENIV=y, CONFIG_CRYPTO_SIG2=y,
- CONFIG_CXL_PMU=y, CONFIG_FB_IO_HELPERS=y,
- CONFIG_FB_SYS_HELPERS_DEFERRED=y, CONFIG_FB_SYS_HELPERS=y,
- CONFIG_FW_UPLOAD=y, CONFIG_HAVE_FUNCTION_GRAPH_RETVAL=y,
- CONFIG_HAVE_HARDLOCKUP_DETECTOR_BUDDY=y, CONFIG_HOTPLUG_CORE_SYNC_DEAD=y,
- CONFIG_HOTPLUG_CORE_SYNC=y, CONFIG_LAN966X_DCB=y,
- CONFIG_LIQUIDIO_CORE=m, CONFIG_MDIO_REGMAP=m,
- CONFIG_NEED_SG_DMA_FLAGS=y, CONFIG_PCS_LYNX=m,
- CONFIG_PPPOE_HASH_BITS=4, CONFIG_PPPOE_HASH_BITS_4=y,
- CONFIG_PROBE_EVENTS_BTF_ARGS=y, CONFIG_STRCAT_KUNIT_TEST=m,
- For both x86_64 and aarch64.

* Wed Aug 23 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.12-1
- Updated with the 6.4.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.12]

* Wed Aug 16 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.11-1
- Updated with the 6.4.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.11]

* Fri Aug 11 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.10-1
- Updated with the 6.4.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.10]

* Tue Aug 08 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.9-1
- Updated with the 6.4.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.9]
- CONFIG_CPU_SRSO=y, CONFIG_ARCH_HAS_CPU_FINALIZE_INIT=y
- For x86_64 only.

* Thu Aug 03 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.8-1
- Updated with the 6.4.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.8]

* Thu Jul 27 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.7-1
- Updated with the 6.4.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.7]

* Mon Jul 24 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.6-1
- Updated with the 6.4.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.6]

* Sun Jul 23 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.5-1
- Updated with the 6.4.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.5]
- CONFIG_AMPERE_ERRATUM_AC03_CPU_38=y,
- For aarch64 only.

* Wed Jul 19 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.4-1
- Updated with the 6.4.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.4]
- CONFIG_INPUT_KUNIT_TEST=m, CONFIG_HID_KUNIT_TEST=m

* Tue Jul 11 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.3-1
- Updated with the 6.4.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.3]

* Wed Jul 05 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.2-1
- Updated with the 6.4.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.2]

* Sat Jul 01 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.1-1
- Updated with the 6.4.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.1]
- Added: CONFIG_LOCK_MM_AND_FIND_VMA=y

* Sun Jun 25 2023 Akemi Yagi <toracat@elrepo.org> - 6.4.0-1
- Updated with the 6.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4]
- CONFIG_AIRO=m, CONFIG_ARCH_FORCE_MAX_ORDER=10,
- CONFIG_ARM_PMUV3=y, CONFIG_BUILTIN_RETURN_ADDRESS_STRIPS_PAC=y,
- CONFIG_CAVIUM_CPT=m, CONFIG_CRYPTO_DEV_CPT=m,
- CONFIG_CRYPTO_DEV_HISTB_TRNG=m, CONFIG_CRYPTO_DEV_MARVELL=m,
- CONFIG_CRYPTO_DEV_OCTEONTX2_CPT=m, CONFIG_CRYPTO_DEV_OCTEONTX_CPT=m,
- CONFIG_DYNAMIC_FTRACE_WITH_DIRECT_CALLS=y, CONFIG_HAVE_DYNAMIC_FTRACE_WITH_DIRECT_CALLS=y,
- CONFIG_IPQ_GCC_5332=m, CONFIG_IPQ_GCC_9574=m,
- CONFIG_MSM_GCC_8917=m, CONFIG_PCIE_ALTERA=m,
- CONFIG_PCIE_ALTERA_MSI=m, CONFIG_PCIE_AL=y,
- CONFIG_PCIE_BRCMSTB=y, CONFIG_PCIE_CADENCE_HOST=y,
- CONFIG_PCIE_CADENCE_PLAT=y, CONFIG_PCIE_CADENCE=y, 
- CONFIG_PCIE_HISI_ERR=y, CONFIG_PCIE_MICROCHIP_HOST=y, 
- CONFIG_PCIE_QCOM=y, CONFIG_PCIE_ROCKCHIP_DW_HOST=y, 
- CONFIG_PCIE_XILINX=y, CONFIG_PCI_FTPCI100=y, 
- CONFIG_PCI_HOST_COMMON=y, CONFIG_PCI_HOST_GENERIC=y, 
- CONFIG_PCI_J721E_HOST=y, CONFIG_PCI_J721E=y, 
- CONFIG_PCI_TEGRA=y, CONFIG_PCI_XGENE_MSI=y, 
- CONFIG_PCI_XGENE=y, CONFIG_PINCTRL_MLXBF3=m, 
- CONFIG_ROCKCHIP_ERRATUM_3588001=y, CONFIG_SA_GPUCC_8775P=m, 
- CONFIG_SM_GCC_7150=m, CONFIG_SM_GPUCC_6115=m, 
- CONFIG_SM_GPUCC_6125=m, CONFIG_SM_GPUCC_6375=m,
- For aarch64 only.
- CONFIG_ARCH_WANT_OPTIMIZE_VMEMMAP=y, CONFIG_DMA_DECLARE_COHERENT=y,
- CONFIG_DTC=y, CONFIG_GPIO_ELKHARTLAKE=m,
- CONFIG_GPIO_TANGIER=m, CONFIG_LENOVO_YMC=m,
- CONFIG_LIBFDT=y, CONFIG_MSI_EC=m,
- CONFIG_OF_EARLY_FLATTREE=y, CONFIG_OF_FLATTREE=y,
- CONFIG_OF_RESERVED_MEM=y, CONFIG_PCIE_DW_HOST=y,
- CONFIG_PCIE_DW=y, CONFIG_SND_SOC_SOF_HDA_MLINK=m
- For x86_64 only.
- CONFIG_ARCH_SUPPORTS_PER_VMA_LOCK=y, CONFIG_BLK_CGROUP_PUNT_BIO=y,
- CONFIG_BLKDEV_UBLK_LEGACY_OPCODES=y, CONFIG_COMMON_CLK_SI521XX=m,
- CONFIG_CRYPTO_DEV_NITROX_CNN55XX=m, CONFIG_CRYPTO_DEV_NITROX=m,
- CONFIG_DRM_AMD_DC_FP=y, CONFIG_DRM_SUBALLOC_HELPER=m,
- CONFIG_DRM_VIRTIO_GPU_KMS=y, CONFIG_GPIO_FXL6408=m,
- CONFIG_GPIO_REGMAP=m, CONFIG_HAS_IOPORT=y,
- CONFIG_IIO_GTS_HELPER=m, CONFIG_LEDS_BD2606MVV=m,
- CONFIG_LIBWX=m, CONFIG_MAX_SKB_FRAGS=17,
- CONFIG_MICROCHIP_T1S_PHY=m, CONFIG_MMU_LAZY_TLB_REFCOUNT=y,
- CONFIG_NETFILTER_BPF_LINK=y, CONFIG_NET_HANDSHAKE_KUNIT_TEST=m,
- CONFIG_NET_HANDSHAKE=y, CONFIG_NET_VENDOR_WANGXUN=y,
- CONFIG_NGBE=m	, CONFIG_NXP_CBTX_PHY=m,
- CONFIG_PCI_HYPERV_INTERFACE=m, CONFIG_PCI_MESON=m,
- CONFIG_PDS_CORE=m, CONFIG_PER_VMA_LOCK=y,
- CONFIG_PHYLIB_LEDS=y, CONFIG_REGMAP_KUNIT=m,
- CONFIG_REGMAP_RAM=m, CONFIG_REGULATOR_RT4803=m,
- CONFIG_REGULATOR_RT5739=m, CONFIG_ROHM_BU27034=m,
- CONFIG_RTW88_8821CS=m, CONFIG_RTW88_8822BS=m,
- CONFIG_RTW88_8822CS=m, CONFIG_RTW88_SDIO=m,
- CONFIG_SENSORS_ACBEL_FSG032=m, CONFIG_SMBFS=m,
- CONFIG_SND_SOC_CS35L56_I2C=m, CONFIG_SND_SOC_CS35L56=m,
- CONFIG_SND_SOC_CS35L56_SHARED=m, CONFIG_SND_SOC_CS35L56_SPI=m,
- CONFIG_TOUCHSCREEN_NOVATEK_NVT_TS=m, CONFIG_TXGBE=m,
- CONFIG_USB_USS720=m, CONFIG_VHOST_TASK=y,
- CONFIG_VIDEO_CMDLINE=y, CONFIG_XFS_DRAIN_INTENTS=y,
- CONFIG_XFS_SUPPORT_ASCII_CI=y,
- For both aarch64 and x86_64.

* Wed Jun 21 2023 Akemi Yagi <toracat@elrepo.org> - 6.3.9-1
- Updated with the 6.3.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.9]

* Wed Jun 14 2023 Akemi Yagi <toracat@elrepo.org> - 6.3.8-1
- Updated with the 6.3.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.8]

* Fri Jun 09 2023 Akemi Yagi <toracat@elrepo.org> - 6.3.7-1
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
- CONFIG_ARCH_ROCKCHIP=y, CONFIG_PCIE_ROCKCHIP=y,
- CONFIG_PCIE_ROCKCHIP_HOST=m, CONFIG_PCIE_ROCKCHIP_DW_HOST=y,
- CONFIG_MTD_NAND_CORE=m, CONFIG_MTD_RAW_NAND=m,
- CONFIG_MTD_NAND_ROCKCHIP=m, CONFIG_MTD_NAND_ECC=y,
- CONFIG_ARC_EMAC_CORE=m, CONFIG_EMAC_ROCKCHIP=m,
- CONFIG_DWMAC_ROCKCHIP=m, CONFIG_SPI_ROCKCHIP=m,
- CONFIG_SPI_ROCKCHIP_SFC=m, CONFIG_PINCTRL_ROCKCHIP=m,
- CONFIG_GPIO_ROCKCHIP=m, CONFIG_ROCKCHIP_THERMAL=m,
- CONFIG_DRM_ROCKCHIP=m, CONFIG_ROCKCHIP_VOP=y,
- CONFIG_ROCKCHIP_VOP2=y, CONFIG_ROCKCHIP_ANALOGIX_DP=y,
- CONFIG_ROCKCHIP_CDN_DP=y, CONFIG_ROCKCHIP_DW_HDMI=y,
- CONFIG_ROCKCHIP_DW_MIPI_DSI=y, CONFIG_ROCKCHIP_INNO_HDMI=y,
- CONFIG_ROCKCHIP_LVDS=y, CONFIG_ROCKCHIP_RGB=y,
- CONFIG_ROCKCHIP_RK3066_HDMI=y, CONFIG_DRM_ANALOGIX_DP=m,
- CONFIG_DRM_DW_HDMI=m, CONFIG_DRM_DW_HDMI_I2S_AUDIO=m,
- CONFIG_DRM_DW_MIPI_DSI=m, CONFIG_SND_SOC_ROCKCHIP=m,
- CONFIG_SND_SOC_ROCKCHIP_I2S=m, CONFIG_SND_SOC_ROCKCHIP_I2S_TDM=m,
- CONFIG_SND_SOC_ROCKCHIP_PDM=m, CONFIG_SND_SOC_ROCKCHIP_SPDIF=m,
- CONFIG_SND_SOC_ROCKCHIP_MAX98090=m, CONFIG_SND_SOC_ROCKCHIP_RT5645=m,
- CONFIG_SND_SOC_RK3288_HDMI_ANALOG=m, CONFIG_SND_SOC_RK3399_GRU_SOUND=m,
- CONFIG_SND_SOC_MAX98090=m, CONFIG_SND_SOC_RT5514=m,
- CONFIG_SND_SOC_RT5514_SPI=m, CONFIG_MMC_DW_ROCKCHIP=m,
- CONFIG_COMMON_CLK_ROCKCHIP=y, CONFIG_CLK_PX30=y, CONFIG_CLK_RK3308=y,
- CONFIG_CLK_RK3328=y, CONFIG_CLK_RK3368=y, CONFIG_CLK_RK3399=y,
- CONFIG_CLK_RK3568=y, CONFIG_CLK_RK3588=y, CONFIG_ROCKCHIP_TIMER=y,
- CONFIG_ROCKCHIP_MBOX=y, CONFIG_ROCKCHIP_IOMMU=y, CONFIG_ROCKCHIP_GRF=y,
- CONFIG_ROCKCHIP_IODOMAIN=m, CONFIG_ROCKCHIP_PM_DOMAINS=y,
- CONFIG_ARM_RK3399_DMC_DEVFREQ=m, CONFIG_PM_DEVFREQ_EVENT=y,
- CONFIG_DEVFREQ_EVENT_ROCKCHIP_DFI=m, CONFIG_ROCKCHIP_SARADC=m,
- CONFIG_PWM_ROCKCHIP=m, CONFIG_PHY_ROCKCHIP_DP=m,
- CONFIG_PHY_ROCKCHIP_DPHY_RX0=m, CONFIG_PHY_ROCKCHIP_EMMC=m,
- CONFIG_PHY_ROCKCHIP_INNO_HDMI=m, CONFIG_PHY_ROCKCHIP_INNO_USB2=m,
- CONFIG_PHY_ROCKCHIP_INNO_CSIDPHY=m, CONFIG_PHY_ROCKCHIP_INNO_DSIDPHY=m,
- CONFIG_PHY_ROCKCHIP_NANENG_COMBO_PHY=m, CONFIG_PHY_ROCKCHIP_PCIE=m,
- CONFIG_PHY_ROCKCHIP_SNPS_PCIE3=m, CONFIG_PHY_ROCKCHIP_TYPEC=m,
- CONFIG_PHY_ROCKCHIP_USB=m, CONFIG_NVMEM_ROCKCHIP_EFUSE=m,
- CONFIG_NVMEM_ROCKCHIP_OTP=m and CONFIG_CRYPTO_DEV_ROCKCHIP=m
- For aarch64 only. [https://elrepo.org/bugs/view.php?id=1345]

* Sun Apr 30 2023 Alan Bartlett <ajb@elrepo.org> - 6.3.1-1
- Updated with the 6.3.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.1]

* Sun Apr 23 2023 Alan Bartlett <ajb@elrepo.org> - 6.3.0-1
- Updated with the 6.3 source tarball.
- CONFIG_AS_HAS_ARMV8_3=y, CONFIG_FUNCTION_ALIGNMENT_4B=y,
- CONFIG_FUNCTION_ALIGNMENT_8B=y, CONFIG_FUNCTION_ALIGNMENT=8,
- CONFIG_SENSORS_SMPRO=m, CONFIG_SENSORS_IIO_HWMON=m,
- CONFIG_SENSORS_NTC_THERMISTOR=m, CONFIG_REGULATOR_CROS_EC=m,
- CONFIG_SA_GCC_8775P=m, CONFIG_QDU_GCC_1000=m, CONFIG_SM_CAMCC_6350=m,
- CONFIG_SM_DISPCC_8550=m, CONFIG_SM_TCSRCC_8550=m, CONFIG_PHY_QCOM_QMP_COMBO=m,
- CONFIG_PHY_QCOM_QMP_PCIE=m, CONFIG_PHY_QCOM_QMP_PCIE_8996=m,
- CONFIG_PHY_QCOM_QMP_UFS=m, CONFIG_PHY_QCOM_QMP_USB=m,
- CONFIG_PHY_QCOM_SNPS_EUSB2=m, CONFIG_PHY_QCOM_EUSB2_REPEATER=m,
- CONFIG_HAVE_DYNAMIC_FTRACE_WITH_CALL_OPS=y, CONFIG_DYNAMIC_FTRACE_WITH_CALL_OPS=y,
- CONFIG_ULTRASOC_SMB=m, CONFIG_CORESIGHT_TPDM=m and CONFIG_CORESIGHT_TPDA=m
- For aarch64 only.
- CONFIG_AS_GFNI=y, CONFIG_THERMAL_ACPI=y, CONFIG_INTEL_TCC=y,
- CONFIG_INTEL_IOMMU_PERF_EVENTS=y, CONFIG_IDLE_INJECT=y,
- CONFIG_CRYPTO_ARIA_AESNI_AVX2_X86_64=m and CONFIG_CRYPTO_ARIA_GFNI_AVX512_X86_64=m
- For x86_64 only.
- CONFIG_SCHED_MM_CID=y, CONFIG_KVM_GENERIC_HARDWARE_ENABLING=y,
- CONFIG_ZSMALLOC_CHAIN_SIZE=8, CONFIG_NF_CONNTRACK_OVS=y,
- CONFIG_NET_SCH_MQPRIO_LIB=m, CONFIG_NCN26000_PHY=m, CONFIG_AT803X_PHY=m,
- CONFIG_ATH12K=m, CONFIG_SERIAL_8250_PCILIB=y, CONFIG_SERIAL_8250_PCI1XXXX=y,
- CONFIG_SENSORS_MC34VR500=m, CONFIG_SENSORS_IR38064_REGULATOR=y,
- CONFIG_SENSORS_LM25066_REGULATOR=y, CONFIG_SENSORS_LTC2978_REGULATOR=y,
- CONFIG_SENSORS_MPQ7932_REGULATOR=y, CONFIG_SENSORS_MPQ7932=m,
- CONFIG_SENSORS_PLI1209BC_REGULATOR=y, CONFIG_SENSORS_TDA38640=m,
- CONFIG_SENSORS_TDA38640_REGULATOR=y, CONFIG_SENSORS_XDPE122_REGULATOR=y,
- CONFIG_REGULATOR_MAX20411=m, CONFIG_UVC_COMMON=m, CONFIG_BACKLIGHT_KTZ8866=m,
- CONFIG_SND_SOC_AW88395_LIB=m, CONFIG_SND_SOC_AW88395=m, CONFIG_SND_SOC_IDT821034=m,
- CONFIG_SND_SOC_PEB2466=m, CONFIG_SND_SOC_SMA1303=m, CONFIG_HID_SUPPORT=y,
- CONFIG_HID_EVISION=m, CONFIG_I2C_HID=y, CONFIG_TYPEC_MUX_GPIO_SBU=m,
- CONFIG_XILINX_XDMA=m, CONFIG_SNET_VDPA=m, CONFIG_DEV_DAX_CXL=m,
- CONFIG_LEGACY_DIRECT_IO=y, CONFIG_EROFS_FS_PCPU_KTHREAD=y,
- CONFIG_RPCSEC_GSS_KRB5_CRYPTOSYSTEM=y, CONFIG_RPCSEC_GSS_KRB5_ENCTYPES_AES_SHA1=y and
- CONFIG_HASHTABLE_KUNIT_TEST=m
- For both aarch64 and x86_64.

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
- CONFIG_GCC_SUPPORTS_DYNAMIC_FTRACE_WITH_ARGS=y,
- CONFIG_ARM64_ERRATUM_2645198=y, CONFIG_ACPI_APMT=y,
- CONFIG_HAVE_KVM_DIRTY_RING=y, CONFIG_HAVE_KVM_DIRTY_RING_ACQ_REL=y,
- CONFIG_NEED_KVM_DIRTY_RING_WITH_BITMAP=y, CONFIG_FUNCTION_ALIGNMENT=0,
- CONFIG_ARCH_USES_PG_ARCH_X=y, CONFIG_MTD_BRCM_U_BOOT=m,
- CONFIG_DWMAC_TEGRA=m, CONFIG_TOUCHSCREEN_WM97XX=m,
- CONFIG_TOUCHSCREEN_WM9705=y, CONFIG_TOUCHSCREEN_WM9712=y,
- CONFIG_TOUCHSCREEN_WM9713=y, CONFIG_TOUCHSCREEN_SUR40=m,
- CONFIG_TOUCHSCREEN_COLIBRI_VF50=m, CONFIG_VIDEOBUF2_DMA_SG=m,
- CONFIG_DRM_AMD_DC_DCN=y, CONFIG_SC_DISPCC_8280XP=m,
- CONFIG_SM_DISPCC_6375=m, CONFIG_SM_GCC_8550=m, CONFIG_NTB_IDT=m,
- CONFIG_NTB_EPF=m, CONFIG_NTB_SWITCHTEC=m, CONFIG_ARM_SCMI_POWERCAP=m,
- CONFIG_ARM_CORESIGHT_PMU_ARCH_SYSTEM_PMU=m,
- CONFIG_CRYPTO_SM4_ARM64_CE_CCM=m, CONFIG_CRYPTO_SM4_ARM64_CE_GCM=m,
- CONFIG_HAVE_DYNAMIC_FTRACE_WITH_ARGS=y and
- CONFIG_DYNAMIC_FTRACE_WITH_ARGS=y
- For aarch64 only.
- CONFIG_EFI_HANDOVER_PROTOCOL=y, CONFIG_CC_HAS_ENTRY_PADDING=y,
- CONFIG_FUNCTION_PADDING_CFI=11, CONFIG_FUNCTION_PADDING_BYTES=16,
- CONFIG_CALL_PADDING=y, CONFIG_HAVE_CALL_THUNKS=y, CONFIG_CALL_THUNKS=y,
- CONFIG_PREFIX_SYMBOLS=y, CONFIG_CALL_DEPTH_TRACKING=y, CONFIG_KVM_SMM=y,
- CONFIG_FUNCTION_ALIGNMENT_4B=y, CONFIG_FUNCTION_ALIGNMENT_16B=y,
- CONFIG_FUNCTION_ALIGNMENT=16, CONFIG_SENSORS_OCC_P8_I2C=m,
- CONFIG_SENSORS_OCC=m, CONFIG_SENSORS_OXP=m, CONFIG_ADVANTECH_EC_WDT=m,
- CONFIG_REGULATOR_CROS_EC=m, CONFIG_REGULATOR_TPS68470=m,
- CONFIG_DRM_I915_PREEMPT_TIMEOUT_COMPUTE=7500,
- CONFIG_SND_SOC_INTEL_AVS_MACH_MAX98927=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_MAX98373=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_PROBE=m, CONFIG_MANA_INFINIBAND=m,
- CONFIG_DELL_WMI_DDV=m, CONFIG_X86_PLATFORM_DRIVERS_HP=y,
- CONFIG_INTEL_IFS=m,
- CONFIG_ARCH_HAS_CPU_CACHE_INVALIDATE_MEMREGION=y and
- CONFIG_HAVE_OBJTOOL_NOP_MCOUNT=y
- For x86_64 only.
- CONFIG_LD_ORPHAN_WARN_LEVEL="warn", CONFIG_ARCH_HAS_NMI_SAFE_THIS_CPU_OPS=y,
- CONFIG_NF_NAT_OVS=y, CONFIG_BT_LE_L2CAP_ECRED=y,
- CONFIG_BT_HCIBTUSB_POLL_SYNC=y, CONFIG_BT_HCIBCM4377=m, CONFIG_FW_CS_DSP=m,
- CONFIG_LIBWX=m, CONFIG_VCAP=y, CONFIG_NFP_NET_IPSEC=y, CONFIG_MT7996E=m,
- CONFIG_RTW88_USB=m, CONFIG_RTW88_8822BU=m, CONFIG_RTW88_8822CU=m,
- CONFIG_RTW88_8723DU=m, CONFIG_RTW88_8821CU=m, CONFIG_RTW89_8852B=m,
- CONFIG_RTW89_8852BE=m, CONFIG_TOUCHSCREEN_CYTTSP5=m,
- CONFIG_TOUCHSCREEN_HYNITRON_CSTXXX=m, CONFIG_TOUCHSCREEN_HIMAX_HX83112B=m,
- CONFIG_LEGACY_TIOCSTI=y, CONFIG_SSIF_IPMI_BMC=m, CONFIG_GPIO_IDIO_16=m,
- CONFIG_MFD_SMPRO=m, CONFIG_REGULATOR_RT6190=m, CONFIG_VIDEO_NOMODESET=y,
- CONFIG_SND_SOC_WM8961=m, CONFIG_VFIO_CONTAINER=y, CONFIG_VFIO_VIRQFD=y,
- CONFIG_CROS_HPS_I2C=m, CONFIG_IOMMUFD=m, CONFIG_SQUASHFS_DECOMP_SINGLE=y,
- CONFIG_SQUASHFS_COMPILE_DECOMP_SINGLE=y, CONFIG_CRYPTO_LIB_GF128MUL=y,
- CONFIG_INTERVAL_TREE_SPAN_ITER=y, CONFIG_DEBUG_INFO_COMPRESSED_NONE=y,
- CONFIG_MEMCPY_SLOW_KUNIT_TEST=y, CONFIG_STRSCPY_KUNIT_TEST=m and
- CONFIG_SIPHASH_KUNIT_TEST=m
- For both aarch64 and x86_64.

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
- CONFIG_NTB_PINGPONG=m, CONFIG_NTB_TOOL=m, CONFIG_NTB_PERF=m,
- CONFIG_NTB_MSI_TEST=m and CONFIG_NTB_TRANSPORT=m
- For aarch64 only. [https://elrepo.org/bugs/view.php?id=1322]

* Wed Feb 01 2023 Alan Bartlett <ajb@elrepo.org> - 6.1.9-1
- Updated with the 6.1.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.9]
- CONFIG_MEDIA_CONTROLLER_DVB=y, CONFIG_VIDEO_USBTV=m,
- CONFIG_VIDEO_AU0828=m, CONFIG_VIDEO_AU0828_V4L2=y,
- CONFIG_VIDEO_CX231XX=m, CONFIG_VIDEO_CX231XX_ALSA=m,
- CONFIG_VIDEO_CX231XX_DVB=m, CONFIG_DVB_AS102=m,
- CONFIG_DVB_B2C2_FLEXCOP_USB=m, CONFIG_DVB_USB_V2=m,
- CONFIG_DVB_USB_AF9015=m, CONFIG_DVB_USB_AF9035=m,
- CONFIG_DVB_USB_ANYSEE=m, CONFIG_DVB_USB_AU6610=m,
- CONFIG_DVB_USB_AZ6007=m, CONFIG_DVB_USB_CE6230=m,
- CONFIG_DVB_USB_DVBSKY=m, CONFIG_DVB_USB_EC168=m,
- CONFIG_DVB_USB_GL861=m, CONFIG_DVB_USB_LME2510=m,
- CONFIG_DVB_USB_MXL111SF=m, CONFIG_DVB_USB_RTL28XXU=m,
- CONFIG_DVB_USB_ZD1301=m, CONFIG_DVB_USB=m,
- CONFIG_DVB_USB_A800=m, CONFIG_DVB_USB_AF9005=m,
- CONFIG_DVB_USB_AF9005_REMOTE=m, CONFIG_DVB_USB_AZ6027=m,
- CONFIG_DVB_USB_CINERGY_T2=m, CONFIG_DVB_USB_CXUSB=m,
- CONFIG_DVB_USB_DIB0700=m, CONFIG_DVB_USB_DIB3000MC=m,
- CONFIG_DVB_USB_DIBUSB_MB=m, CONFIG_DVB_USB_DIBUSB_MC=m,
- CONFIG_DVB_USB_DIGITV=m, CONFIG_DVB_USB_DTT200U=m,
- CONFIG_DVB_USB_DTV5100=m, CONFIG_DVB_USB_DW2102=m,
- CONFIG_DVB_USB_GP8PSK=m, CONFIG_DVB_USB_M920X=m,
- CONFIG_DVB_USB_NOVA_T_USB2=m, CONFIG_DVB_USB_OPERA1=m,
- CONFIG_DVB_USB_PCTV452E=m, CONFIG_DVB_USB_TECHNISAT_USB2=m,
- CONFIG_DVB_USB_TTUSB2=m, CONFIG_DVB_USB_UMT_010=m,
- CONFIG_DVB_USB_VP702X=m, CONFIG_DVB_USB_VP7045=m,
- CONFIG_SMS_USB_DRV=m, CONFIG_DVB_TTUSB_BUDGET=m,
- CONFIG_DVB_TTUSB_DEC=m, CONFIG_MEDIA_COMMON_OPTIONS=y,
- CONFIG_CYPRESS_FIRMWARE=m, CONFIG_TTPCI_EEPROM=m,
- CONFIG_VIDEO_CX2341X=m, CONFIG_DVB_B2C2_FLEXCOP=m,
- CONFIG_SMS_SIANO_MDTV=m, CONFIG_SMS_SIANO_RC=y,
- CONFIG_VIDEO_CX25840=m, CONFIG_MEDIA_TUNER_E4000=m,
- CONFIG_MEDIA_TUNER_FC0011=m, CONFIG_MEDIA_TUNER_FC0012=m,
- CONFIG_MEDIA_TUNER_FC0013=m, CONFIG_MEDIA_TUNER_FC2580=m,
- CONFIG_MEDIA_TUNER_IT913X=m, CONFIG_MEDIA_TUNER_MAX2165=m,
- CONFIG_MEDIA_TUNER_MT2063=m, CONFIG_MEDIA_TUNER_MT2266=m,
- CONFIG_MEDIA_TUNER_MXL5005S=m, CONFIG_MEDIA_TUNER_MXL5007T=m,
- CONFIG_MEDIA_TUNER_R820T=m, CONFIG_MEDIA_TUNER_TDA18218=m,
- CONFIG_MEDIA_TUNER_TDA18250=m, CONFIG_MEDIA_TUNER_TUA9001=m,
- CONFIG_DVB_STB0899=m, CONFIG_DVB_STB6100=m, CONFIG_DVB_STV090x=m,
- CONFIG_DVB_STV6110x=m, CONFIG_DVB_MN88472=m, CONFIG_DVB_MN88473=m,
- CONFIG_DVB_SI2165=m, CONFIG_DVB_CX24116=m, CONFIG_DVB_CX24120=m,
- CONFIG_DVB_CX24123=m, CONFIG_DVB_DS3000=m, CONFIG_DVB_MT312=m,
- CONFIG_DVB_S5H1420=m, CONFIG_DVB_SI21XX=m, CONFIG_DVB_STB6000=m,
- CONFIG_DVB_STV0288=m, CONFIG_DVB_STV0299=m, CONFIG_DVB_STV0900=m,
- CONFIG_DVB_STV6110=m, CONFIG_DVB_TDA10086=m, CONFIG_DVB_TDA8083=m,
- CONFIG_DVB_TDA826X=m, CONFIG_DVB_TUNER_CX24113=m,
- CONFIG_DVB_TUNER_ITD1000=m, CONFIG_DVB_ZL10039=m,
- CONFIG_DVB_AF9013=m, CONFIG_DVB_AS102_FE=m, CONFIG_DVB_CX22700=m,
- CONFIG_DVB_CX22702=m, CONFIG_DVB_CXD2841ER=m,
- CONFIG_DVB_DIB3000MB=m, CONFIG_DVB_DIB3000MC=m,
- CONFIG_DVB_DIB7000M=m, CONFIG_DVB_DIB7000P=m, CONFIG_DVB_EC100=m,
- CONFIG_DVB_GP8PSK_FE=m, CONFIG_DVB_NXT6000=m, CONFIG_DVB_RTL2830=m,
- CONFIG_DVB_RTL2832=m, CONFIG_DVB_TDA10048=m, CONFIG_DVB_TDA1004X=m,
- CONFIG_DVB_ZD1301_DEMOD=m, CONFIG_DVB_STV0297=m,
- CONFIG_DVB_VES1820=m, CONFIG_DVB_AU8522=m, CONFIG_DVB_AU8522_DTV=m,
- CONFIG_DVB_AU8522_V4L=m, CONFIG_DVB_BCM3510=m, CONFIG_DVB_LG2160=m,
- CONFIG_DVB_NXT200X=m, CONFIG_DVB_S5H1411=m, CONFIG_DVB_DIB8000=m,
- CONFIG_DVB_PLL=m, CONFIG_DVB_TUNER_DIB0070=m,
- CONFIG_DVB_TUNER_DIB0090=m, CONFIG_DVB_AF9033=m,
- CONFIG_DVB_ATBM8830=m, CONFIG_DVB_ISL6421=m, CONFIG_DVB_ISL6423=m,
- CONFIG_DVB_IX2505V=m, CONFIG_DVB_LGS8GXX=m, CONFIG_DVB_LNBP21=m,
- CONFIG_DVB_LNBP22=m, CONFIG_DVB_M88RS2000=m and CONFIG_DVB_SP2=m
- For both aarch64 and x86_64. [https://elrepo.org/bugs/view.php?id=1321]

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
- CONFIG_BLK_DEV_FD=m
- For x86_64 only. [https://elrepo.org/bugs/view.php?id=1308]

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
- CONFIG_GENERIC_IRQ_CHIP=y, CONFIG_ARCH_BCM=y, CONFIG_ARCH_BCM2835=y,
- CONFIG_ARCH_BCM_IPROC=y, CONFIG_ARCH_BCMBCA=y, CONFIG_ARCH_BRCMSTB=y,
- CONFIG_ARM_BRCMSTB_AVS_CPUFREQ=y, CONFIG_ARM_RASPBERRYPI_CPUFREQ=m,
- CONFIG_PCIE_IPROC=y, CONFIG_PCIE_IPROC_PLATFORM=y,
- CONFIG_PCIE_IPROC_MSI=y, CONFIG_PCIE_BRCMSTB=y,
- CONFIG_RASPBERRYPI_FIRMWARE=m, CONFIG_MTD_OF_PARTS_BCM4908=y,
- CONFIG_MTD_OF_PARTS_LINKSYS_NS=y, CONFIG_BLK_DEV_UBLK=m,
- CONFIG_AHCI_BRCM=m, CONFIG_BCM4908_ENET=y, CONFIG_BGMAC=y,
- CONFIG_BGMAC_PLATFORM=y, CONFIG_BCM_CYGNUS_PHY=m,
- CONFIG_MDIO_BCM_IPROC=y, CONFIG_MDIO_BUS_MUX=y,
- CONFIG_MDIO_BUS_MUX_BCM_IPROC=y, CONFIG_TOUCHSCREEN_IPROC=m,
- CONFIG_TOUCHSCREEN_RASPBERRYPI_FW=m, CONFIG_SERIAL_8250_BCM2835AUX=m,
- CONFIG_SERIAL_8250_BCM7271=y, CONFIG_SERIAL_BCM63XX=y,
- CONFIG_SERIAL_BCM63XX_CONSOLE=y, CONFIG_HW_RANDOM_BCM2835=y,
- CONFIG_HW_RANDOM_IPROC_RNG200=y, CONFIG_I2C_BCM2835=m,
- CONFIG_I2C_BCM_IPROC=y, CONFIG_I2C_BRCMSTB=y, CONFIG_SPI_BCM2835=m,
- CONFIG_SPI_BCM2835AUX=m, CONFIG_SPI_BCM63XX_HSSPI=m,
- CONFIG_SPI_BCM_QSPI=y, CONFIG_PTP_1588_CLOCK_DTE=y,
- CONFIG_GENERIC_PINCTRL_GROUPS=y, CONFIG_GENERIC_PINMUX_FUNCTIONS=y,
- CONFIG_PINCTRL_BCM2835=y, CONFIG_PINCTRL_BCM4908=y,
- CONFIG_PINCTRL_IPROC_GPIO=y, CONFIG_PINCTRL_NS2_MUX=y,
- CONFIG_GPIO_GENERIC=y, CONFIG_GPIO_RASPBERRYPI_EXP=m,
- CONFIG_GPIO_BCM_XGS_IPROC=y, CONFIG_GPIO_BRCMSTB=y,
- CONFIG_SENSORS_RASPBERRYPI_HWMON=m, CONFIG_BCM2711_THERMAL=y,
- CONFIG_BCM2835_THERMAL=y, CONFIG_BRCMSTB_THERMAL=y,
- CONFIG_BCM_NS_THERMAL=y, CONFIG_BCM_SR_THERMAL=y,
- CONFIG_BCM2835_WDT=m, CONFIG_BCM7038_WDT=m, CONFIG_DRM_V3D=m,
- CONFIG_DRM_VC4=m, CONFIG_DRM_VC4_HDMI_CEC=y,
- CONFIG_SND_BCM2835_SOC_I2S=m, CONFIG_USB_EHCI_BRCMSTB=m,
- CONFIG_USB_BRCMSTB=m, CONFIG_USB_OHCI_HCD_PLATFORM=m,
- CONFIG_BRCM_USB_PINMAP=y, CONFIG_MMC_SDHCI_IPROC=m,
- CONFIG_MMC_BCM2835=m, CONFIG_MMC_SDHCI_BRCMSTB=m,
- CONFIG_RTC_DRV_BRCMSTB=y, CONFIG_DMA_BCM2835=m,
- CONFIG_BCM_VIDEOCORE=m, CONFIG_BCM2835_VCHIQ=m, CONFIG_VCHIQ_CDEV=y,
- CONFIG_SND_BCM2835=m, CONFIG_VIDEO_BCM2835=m,
- CONFIG_BCM2835_VCHIQ_MMAL=m, CONFIG_CLK_BCM2711_DVP=y,
- CONFIG_CLK_BCM2835=y, CONFIG_CLK_BCM_63XX=y, CONFIG_COMMON_CLK_IPROC=y,
- CONFIG_CLK_BCM_NS2=y, CONFIG_CLK_BCM_SR=y, CONFIG_CLK_RASPBERRYPI=m,
- CONFIG_BCM2835_MBOX=m, CONFIG_BCM_FLEXRM_MBOX=m, CONFIG_BCM2835_POWER=y,
- CONFIG_SOC_BRCMSTB=y, CONFIG_BCM_PMB=y, CONFIG_BRCMSTB_PM=y,
- CONFIG_BCM_IPROC_ADC=m, CONFIG_PWM_BCM_IPROC=y, CONFIG_PWM_BCM2835=m,
- CONFIG_PWM_BRCMSTB=m, CONFIG_PWM_RASPBERRYPI_POE=m,
- CONFIG_BCM7038_L1_IRQ=y, CONFIG_BCM7120_L2_IRQ=y,
- CONFIG_BRCMSTB_L2_IRQ=y, CONFIG_RESET_BRCMSTB=y,
- CONFIG_RESET_BRCMSTB_RESCAL=y, CONFIG_RESET_RASPBERRYPI=m,
- CONFIG_RESET_SIMPLE=y, CONFIG_PHY_BCM_SR_USB=y,
- CONFIG_PHY_BCM_NS_USB2=y, CONFIG_PHY_BCM_NS_USB3=y, CONFIG_PHY_NS2_PCIE=y,
- CONFIG_PHY_NS2_USB_DRD=y, CONFIG_PHY_BRCM_SATA=y, CONFIG_PHY_BRCM_USB=y,
- CONFIG_PHY_BCM_SR_PCIE=y, CONFIG_NVMEM_BCM_OCOTP=y and
- CONFIG_CRYPTO_DEV_BCM_SPU=m
- For aarch64 only. [https://elrepo.org/bugs/view.php?id=1299]
- CONFIG_BLK_DEV_UBLK=m
- For both aarch64 and x86_64. [https://elrepo.org/bugs/view.php?id=1300]

* Sun Dec 11 2022 Alan Bartlett <ajb@elrepo.org> - 6.1.0-1
- Updated with the 6.1 source tarball.
- CONFIG_ARM64_ERRATUM_2658417=y, CONFIG_ARCH_FORCE_MAX_ORDER=11,
- CONFIG_HAVE_ARCH_HUGE_VMALLOC=y, CONFIG_HAVE_SOFTIRQ_ON_OWN_STACK=y,
- CONFIG_SOFTIRQ_ON_OWN_STACK=y, CONFIG_XEN_PV_MSR_SAFE=y,
- CONFIG_X86_AMD_PSTATE=y, CONFIG_HAVE_KVM_DIRTY_RING_TSO=y,
- CONFIG_HAVE_KVM_DIRTY_RING_ACQ_REL=y, CONFIG_HAVE_RUST=y,
- CONFIG_ARCH_SUPPORTS_CFI_CLANG=y, CONFIG_ARCH_HAS_NONLEAF_PMD_YOUNG=y,
- CONFIG_COMPACT_UNEVICTABLE_DEFAULT=1, CONFIG_AHCI_DWC=m,
- CONFIG_NGBE=m, CONFIG_NET_VENDOR_ADI=y, CONFIG_ADIN1110=m,
- CONFIG_MLX5_EN_MACSEC=y, CONFIG_PCS_ALTERA_TSE=m, CONFIG_IOSM=m,
- CONFIG_TOUCHSCREEN_COLIBRI_VF50=m, CONFIG_SENSORS_MAX31760=m,
- CONFIG_SENSORS_TPS546D24=m, CONFIG_SENSORS_EMC2305=m,
- CONFIG_HP_WATCHDOG=m, CONFIG_EXAR_WDT=m,
- CONFIG_DRM_USE_DYNAMIC_DEBUG=y, CONFIG_DRM_GEM_DMA_HELPER=m,
- CONFIG_SND_SOC_AMD_PS=m, CONFIG_SND_SOC_AMD_PS_MACH=m,
- CONFIG_SND_SOC_SOF_AMD_REMBRANDT=m, CONFIG_SND_SOC_SOF_INTEL_SKL=m,
- CONFIG_SND_SOC_SOF_SKYLAKE=m, CONFIG_SND_SOC_SOF_KABYLAKE=m,
- CONFIG_SND_SOC_CROS_EC_CODEC=m, CONFIG_SND_SOC_CS42L42_CORE=m,
- CONFIG_SND_SOC_CS42L83=m, CONFIG_SND_SOC_ES8326=m,
- CONFIG_SND_SOC_SRC4XXX_I2C=m, CONFIG_SND_SOC_SRC4XXX=m,
- CONFIG_HID_VRC2=m, CONFIG_HID_PXRC=m, CONFIG_CROS_TYPEC_SWITCH=m,
- CONFIG_QCOM_CLK_APCS_MSM8916=m, CONFIG_QCOM_CLK_APCS_SDX55=m,
- CONFIG_AMD_PMF=m, CONFIG_COMMON_CLK_VC7=m, CONFIG_IPQ_APSS_6018=m,
- CONFIG_MSM_GCC_8909=m, CONFIG_SC_GPUCC_8280XP=m,
- CONFIG_SM_DISPCC_6115=m, CONFIG_SM_DISPCC_8450=m,
- CONFIG_SM_GCC_6375=m, CONFIG_LTRF216A=m,
- CONFIG_ALIBABA_UNCORE_DRW_PMU=m, CONFIG_CRYPTO_ARIA_AESNI_AVX_X86_64=m,
- CONFIG_HISI_PTT=m, CONFIG_CRYPTO_LIB_UTILS=y, CONFIG_ZSTD_COMMON=y,
- CONFIG_HAVE_ARCH_KMSAN=y, CONFIG_HAVE_DYNAMIC_FTRACE_NO_PATCHABLE=y,
- CONFIG_KUNIT_DEFAULT_ENABLED=y, CONFIG_IS_SIGNED_TYPE_KUNIT_TEST=m and
- CONFIG_FORTIFY_KUNIT_TEST=m

* Thu Dec 08 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.12-1
- Updated with the 6.0.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.12]

* Sat Dec 03 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.11-1
- Updated with the 6.0.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.11]

* Fri Nov 25 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.10-1
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

* Sat Oct 29 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.6-1
- Updated with the 6.0.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.6]

* Wed Oct 26 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.5-1
- Updated with the 6.0.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.5]

* Wed Oct 26 2022 Alan Bartlett <ajb@elrepo.org> - 6.0.4-1
- Updated with the 6.0.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.0.4]

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
- CONFIG_HAVE_IMA_KEXEC=y, CONFIG_ACPI_VIDEO=y, CONFIG_ACPI_PRMT=y,
- CONFIG_CRYPTO_POLYVAL_ARM64_CE=m, CONFIG_HAVE_IOREMAP_PROT=y,
- CONFIG_HAVE_CONTEXT_TRACKING_USER=y,
- CONFIG_HAVE_CONTEXT_TRACKING_USER_OFFSTACK=y,
- CONFIG_SOFTIRQ_ON_OWN_STACK=y,
- CONFIG_ARCH_HAVE_TRACE_MMIO_ACCESS=y, CONFIG_ARCH_WANTS_THP_SWAP=y,
- CONFIG_THP_SWAP=y, CONFIG_GET_FREE_REGION=y,
- CONFIG_NF_FLOW_TABLE_PROCFS=y, CONFIG_PCI_DOE=y,
- CONFIG_CXL_REGION=y, CONFIG_ARM_SCMI_POWER_CONTROL=m,
- CONFIG_SCSI_BUSLOGIC=m, CONFIG_NET_VENDOR_WANGXUN=y,
- CONFIG_TXGBE=m, CONFIG_BCM_NET_PHYPTP=m, CONFIG_CAN_NETLINK=y,
- CONFIG_CAN_RX_OFFLOAD=y, CONFIG_CAN_CAN327=m, CONFIG_CAN_FLEXCAN=m,
- CONFIG_CAN_GRCAN=m, CONFIG_CAN_CTUCANFD_PLATFORM=m,
- CONFIG_CAN_ESD_USB=m, CONFIG_TCG_TIS_I2C=m,
- CONFIG_PINCTRL_METEORLAKE=m, CONFIG_SENSORS_LT7182S=m,
- CONFIG_APERTURE_HELPERS=y, CONFIG_DRM_BUDDY=m,
- CONFIG_SND_CTL_FAST_LOOKUP=y, CONFIG_SND_HDA_CS_DSP_CONTROLS=m,
- CONFIG_SND_HDA_EXT_CORE=m, CONFIG_SND_SOC_AMD_ST_ES8336_MACH=m,
- CONFIG_SND_AMD_ASOC_REMBRANDT=m, CONFIG_SND_SOC_AMD_RPL_ACP6x=m,
- CONFIG_SND_SOC_FSL_UTILS=m, CONFIG_SND_SOC_INTEL_AVS_MACH_DA7219=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_DMIC=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_HDAUDIO=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_MAX98357A=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_NAU8825=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_RT274=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_RT286=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_RT298=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_RT5682=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_SSM4567=m,
- CONFIG_SND_SOC_SOF_IPC3=y, CONFIG_SND_SOC_SOF_INTEL_IPC4=y,
- CONFIG_SND_SOC_SOF_INTEL_MTL=m, CONFIG_SND_SOC_SOF_METEORLAKE=m,
- CONFIG_SND_SOC_HDA=m, CONFIG_SND_SOC_RT274=m,
- CONFIG_SND_SOC_TAS2780=m, CONFIG_I2C_HID_OF_ELAN=m,
- CONFIG_USB_ONBOARD_HUB=m, CONFIG_UCSI_STM32G0=m,
- CONFIG_TYPEC_ANX7411=m, CONFIG_INFINIBAND_ERDMA=m,
- CONFIG_RTC_DRV_NCT3018Y=m, CONFIG_CROS_KUNIT=m, CONFIG_P2SB=y,
- CONFIG_SM_CAMCC_8450=m, CONFIG_SM_GPUCC_8350=m,
- CONFIG_IIO_FORMAT_KUNIT_TEST=m, CONFIG_PWM_CLK=m, CONFIG_HNS3_PMU=m,
- CONFIG_CRYPTO_FIPS_NAME="Red Hat Enterprise Linux 9 - Kernel Cryptographic API",
- CONFIG_CRYPTO_XCTR=m, CONFIG_CRYPTO_HCTR2=m, CONFIG_CRYPTO_POLYVAL=m,
- CONFIG_CRYPTO_POLYVAL_CLMUL_NI=m, CONFIG_CRYPTO_ARIA=m, CONFIG_CRYPTO_DEV_QAT=m,
- CONFIG_CRYPTO_DEV_QAT_DH895xCC=m, CONFIG_CRYPTO_DEV_QAT_C3XXX=m,
- CONFIG_CRYPTO_DEV_QAT_C62X=m, CONFIG_CRYPTO_DEV_QAT_4XXX=m,
- CONFIG_CRYPTO_DEV_QAT_DH895xCCVF=m, CONFIG_CRYPTO_DEV_QAT_C3XXXVF=m,
- CONFIG_CRYPTO_DEV_QAT_C62XVF=m, CONFIG_CRYPTO_LIB_SHA1=y,
- CONFIG_GENERIC_IOREMAP=y, CONFIG_POLYNOMIAL=m and
- CONFIG_CPUMASK_KUNIT_TEST=m

* Wed Sep 28 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.12-0.rc4
- Updated with the 5.19.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.12]
- The fourth release candidate of a kernel-ml package set for el9.

* Sat Sep 24 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.11-0.rc3
- Updated with the 5.19.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.11]
- The third release candidate of a kernel-ml package set for el9.

* Tue Sep 20 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.10-0.rc2
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.10]
- The second release candidate of a kernel-ml package set for el9.

* Sun Sep 18 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.10-0.rc1
- Updated with the 5.19.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.10]
- The first release candidate of a kernel-ml package set for el9.

* Sat Aug 13 2022 Alan Bartlett <ajb@elrepo.org>
- Forked this specification file to create a kernel-ml package set for the ELRepo Project.

* Tue Aug 02 2022 Herton R. Krzesinski <herton@redhat.com> [5.14.0-70.22.1.el9_0]
- PCI: vmd: Revert 2565e5b69c44 ("PCI: vmd: Do not disable MSI-X remapping if interrupt
- remapping is enabled by IOMMU.") (Myron Stowe) [2109974 2084146]
- PCI: vmd: Assign VMD IRQ domain before enumeration (Myron Stowe) [2109974 2084146]
- rhel config: Set DMAR_UNITS_SUPPORTED (Jerry Snitselaar) [2105326 2094984]
- iommu/vt-d: Make DMAR_UNITS_SUPPORTED a config setting (Jerry Snitselaar) [2105326 2094984]
