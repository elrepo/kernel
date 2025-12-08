# Explicity use python3 to avoid python byte compile errors.
%global __os_install_post    \
    /usr/lib/rpm/redhat/brp-compress \
    %{!?__debug_package:\
    /usr/lib/rpm/redhat/brp-strip %{__strip} \
    /usr/lib/rpm/redhat/brp-strip-comment-note %{__strip} %{__objdump} \
    } \
    /usr/lib/rpm/redhat/brp-strip-static-archive %{__strip} \
    /usr/lib/rpm/brp-python-bytecompile /usr/bin/python3 %{?_python_bytecompile_errors_terminate_build} \
    /usr/lib/rpm/redhat/brp-python-hardlink \
    %{!?__jar_repack:/usr/lib/rpm/redhat/brp-java-repack-jars} \
%{nil}

%global __spec_install_pre %{___build_pre}

# Define the version of the Linux Kernel Archive tarball.
%define LKAver 6.1.158

# Define the buildid, if required.
#define buildid .local

# The following build options are enabled by default.
# Use either --without <option> on your rpmbuild command line
# or force the values to 0, here, to disable them.

# kernel-lt
%define with_default %{?_without_default: 0} %{?!_without_default: 1}
# kernel-lt-doc
%define with_doc     %{?_without_doc:     0} %{?!_without_doc:     1}
# kernel-lt-headers
%define with_headers %{?_without_headers: 0} %{?!_without_headers: 1}
# perf
%define with_perf    %{?_without_perf:    0} %{?!_without_perf:    1}
# tools
%define with_tools   %{?_without_tools:   0} %{?!_without_tools:   1}
# gcc10
%define with_gcc10   %{?_without_gcc10:   0} %{?!_without_gcc10:   1}

# These architectures install vdso/ directories.
%define vdso_arches i686 x86_64

# Architecture defaults.
%define asmarch x86
%define buildarch %{_target_cpu}
%define hdrarch %{_target_cpu}

# Per-architecture tweaks.

%ifarch noarch
# Documentation only.
%define with_default 0
%define with_headers 0
%define with_perf 0
%define with_tools 0
%endif

%ifarch i686
# 32-bit kernel-lt, headers, perf and tools.
%define buildarch i386
%define hdrarch i386
%define with_doc 0
%endif

%ifarch x86_64
# 64-bit kernel-lt, headers, perf and tools.
%define with_doc 0
%endif

# Determine the sublevel number and set pkg_version.
%define sublevel %(echo %{LKAver} | %{__awk} -F\. '{ print $3 }')
%if "%{sublevel}" == ""
%define pkg_version %{LKAver}.0
%else
%define pkg_version %{LKAver}
%endif

# Set pkg_release.
%define pkg_release 3%{?buildid}%{?dist}

#
# Three sets of minimum package version requirements in the form of Conflicts.
#

#
# First the general kernel required versions, as per Documentation/Changes.
#
%define kernel_dot_org_conflicts ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2, device-mapper-libs < 1.02.63-2, mdadm < 3.2.1-5

#
# Then a series of requirements that are distribution specific, either because
# the older versions have problems with the newer kernel or lack certain things
# that make integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, ipw2200-firmware < 2.4, iwl4965-firmware < 228.57.2, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, wireless-tools < 29-3

#
# We moved the drm include files into kernel-headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
#
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel because the %%post scripts make use of them.
#
%define kernel_prereq fileutils, module-init-tools >= 3.16-2, initscripts >= 8.11.1-1, grubby >= 8.28-2
%define initrd_prereq dracut >= 001-7

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
Provides: kernel-%{_target_cpu} = %{version}-%{release}
Provides: kernel-uname-r = %{version}-%{release}.%{_target_cpu}
Provides: kernel-drm = 4.3.0
Provides: kernel-drm-nouveau = 16
Provides: kernel-modeset = 1
Provides: %{name} = %{version}-%{release}
Provides: %{name}-%{_target_cpu} = %{version}-%{release}
Provides: %{name}-uname-r = %{version}-%{release}.%{_target_cpu}
Provides: %{name}-drm = 4.3.0
Provides: %{name}-drm-nouveau = 16
Provides: %{name}-modeset = 1
Requires(pre): %{kernel_prereq}
Requires(pre): %{initrd_prereq}
Requires(pre): linux-firmware >= 20100806-2
Requires(post): %{_sbindir}/new-kernel-pkg
Requires(preun): %{_sbindir}/new-kernel-pkg
Conflicts: %{kernel_dot_org_conflicts}
Conflicts: %{package_conflicts}
# We can't let RPM do the dependencies automatically because it'll then pick up
# a correct but undesirable perl dependency from the module headers which
# isn't required for the kernel-lt proper to function.
AutoReq: no
AutoProv: yes

#
# List the packages used during the kernel-lt build.
#
%if %{with_gcc10}
BuildRequires: devtoolset-10, scl-utils
%endif
BuildRequires: asciidoc, bash >= 2.03, bc, bison, binutils >= 2.12, diffutils
BuildRequires: elfutils-libelf-devel, findutils, gawk, gcc >= 3.4.2, gzip
BuildRequires: hostname, m4, make >= 3.78, module-init-tools, net-tools
BuildRequires: newt-devel, openssl, openssl-devel, patch >= 2.5.4, perl
BuildRequires: redhat-rpm-config >= 9.1.0-55, rsync, sh-utils, tar, xmlto, xz
%if %{with_perf}
BuildRequires: audit-libs-devel, binutils-devel, elfutils-devel, git
BuildRequires: java-1.8.0-openjdk-devel, libcap-devel, numactl-devel
BuildRequires: perl(ExtUtils::Embed), python-devel, python3
BuildRequires: slang-devel, xz-devel, zlib-devel
%endif
%if %{with_tools}
BuildRequires: gettext, ncurses-devel, pciutils-devel
%endif

# Sources.
Source0: https://www.kernel.org/pub/linux/kernel/v5.x/linux-%{LKAver}.tar.xz
Source1: config-%{version}-x86_64
Source2: cpupower.service
Source3: cpupower.config

# To build .src.rpm, run with '--with src'
%if %{?_with_src:0}%{!?_with_src:1}
NoSource: 0
%endif

%description
This package provides the Linux kernel (vmlinuz), the core of any
Linux-based operating system. The kernel handles the basic functions
of the OS: memory allocation, process allocation, device I/O, etc.

%package devel
Summary: Development package for building kernel modules to match the kernel.
Group: System Environment/Kernel
Provides: kernel-devel = %{version}-%{release}
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}
Provides: kernel-devel-uname-r = %{version}-%{release}.%{_target_cpu}
Provides: %{name}-devel = %{version}-%{release}
Provides: %{name}-devel-%{_target_cpu} = %{version}-%{release}
Provides: %{name}-devel-uname-r = %{version}-%{release}.%{_target_cpu}
AutoReqProv: no
Requires(pre): %{_bindir}/find
Requires: perl
%description devel
This package provides the kernel header files and makefiles
sufficient to build modules against the kernel package.

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

%package -n python-perf
Summary: Python bindings for applications that will manipulate perf events.
Group: Development/Libraries
%description -n python-perf
This package provides a module that permits applications written in the
Python programming language to use the interface to manipulate perf events.

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
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
Obsoletes: cpuspeed < 1:2.0
Requires: %{name}-tools-libs = %{version}-%{release}
Conflicts: kernel-tools < %{version}-%{release}
%description -n %{name}-tools
This package contains the tools/ directory and its supporting
documentation, derived from the kernel source.

%package -n %{name}-tools-libs
Summary: Libraries for the kernel tools.
Group: Development/System
License: GPLv2
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
Provides: %{name}-tools-devel
Conflicts: kernel-tools-libs-devel < %{version}-%{release}
%description -n %{name}-tools-libs-devel
This package contains the development files for the tools/ directory
libraries, derived from the kernel source.
%endif

# Disable the building of the debug package(s).
%define debug_package %{nil}

%prep
%if %{with_gcc10}
. /opt/rh/devtoolset-10/enable
%endif

%setup -q -n %{name}-%{version} -c
%{__mv} linux-%{LKAver} linux-%{version}-%{release}.%{_target_cpu}

pushd linux-%{version}-%{release}.%{_target_cpu} > /dev/null

# Purge the source tree of all unrequired dot-files.
%{_bindir}/find -name '.*' -type f | %{_bindir}/xargs --no-run-if-empty %{__rm} -rf

%{__cp} %{SOURCE1} .

# Run make listnewconfig over all the configuration files.
%ifarch i686 || x86_64
for C in config-*-%{_target_cpu}*
do
    %{__cp} $C .config
    %{__make} -s ARCH=%{buildarch} listnewconfig | %{_bindir}/grep -E '^CONFIG_' > .newoptions || true
    if [ -s .newoptions ]; then
        cat .newoptions
        exit 1
    fi
    %{__rm} -f .newoptions
done
%endif

popd > /dev/null

%build
%if %{with_gcc10}
. /opt/rh/devtoolset-10/enable
%endif

BuildKernel() {
    Flavour=$1

    %{__make} -s distclean

    # Select the correct flavour configuration file.
    if [ -z "${Flavour}" ]; then
        %{__cp} config-%{version}-%{_target_cpu} .config
    else
        %{__cp} config-%{version}-%{_target_cpu}-${Flavour} .config
    fi

    %define KVRFA %{version}-%{release}${Flavour}.%{_target_cpu}

    # Set the EXTRAVERSION string in the top level Makefile.
    %{__sed} -i "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}${Flavour}.%{_target_cpu}/" Makefile

    %{__make} -s ARCH=%{buildarch} oldconfig

    %{__make} -s ARCH=%{buildarch} %{?_smp_mflags} bzImage

    %{__make} -s ARCH=%{buildarch} %{?_smp_mflags} modules

    # Install the results into the RPM_BUILD_ROOT directory.
    %{__mkdir_p} $RPM_BUILD_ROOT/boot
    %{__install} -m 644 .config $RPM_BUILD_ROOT/boot/config-%{KVRFA}
    %{__install} -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-%{KVRFA}

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-%{KVRFA}.img bs=1M count=20

    %{__cp} arch/x86/boot/bzImage $RPM_BUILD_ROOT/boot/vmlinuz-%{KVRFA}
    %{__chmod} 755 $RPM_BUILD_ROOT/boot/vmlinuz-%{KVRFA}

    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/kernel
    # Override $(mod-fw) because we don't want it to install any firmware.
    # We'll get it from the linux-firmware package and we don't want conflicts.
    %{__make} -s ARCH=%{buildarch} INSTALL_MOD_PATH=$RPM_BUILD_ROOT KERNELRELEASE=%{KVRFA} modules_install mod-fw=

%ifarch %{vdso_arches}
    %{__make} -s ARCH=%{buildarch} INSTALL_MOD_PATH=$RPM_BUILD_ROOT KERNELRELEASE=%{KVRFA} vdso_install
    %{_bindir}/find $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/vdso -name 'vdso*.so' -type f | \
        %{_bindir}/xargs --no-run-if-empty %{__strip}
    if %{_bindir}/grep -q '^CONFIG_XEN=y$' .config; then
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
    %{__install} -D -m 444 ldconfig-%{name}.conf $RPM_BUILD_ROOT/etc/ld.so.conf.d/%{name}-%{KVRFA}.conf
%endif

    # Save the headers/makefiles, etc, for building modules against.
    #
    # This looks scary but the end result is supposed to be:
    #
    # - all arch relevant include/ files
    # - all Makefile and Kconfig files
    # - all script/ files
    #
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/source
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    pushd $RPM_BUILD_ROOT/lib/modules/%{KVRFA} > /dev/null
    %{__ln_s} build source
    popd > /dev/null
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/extra
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/updates
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/weak-updates

    # First copy everything . . .
    %{__cp} --parents `%{_bindir}/find  -name 'Makefile*' -o -name 'Kconfig*' -type f` $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__cp} Module.symvers $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__cp} System.map $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    if [ -s Module.markers ]; then
        %{__cp} Module.markers $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    fi

    %{__gzip} -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-%{KVRFA}.gz

    # . . . then drop all but the needed Makefiles and Kconfig files.
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Documentation
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/scripts
    %{__rm} -rf $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include
    %{__cp} .config $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    %{__cp} -a scripts $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
    if [ -d arch/%{buildarch}/scripts ]; then
        %{__cp} -a arch/%{buildarch}/scripts $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/arch/%{_arch} || :
    fi
    if [ -f arch/%{buildarch}/*lds ]; then
        %{__cp} -a arch/%{buildarch}/*lds $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/arch/%{_arch}/ || :
    fi
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/scripts/*.o
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/scripts/*/*.o
    if [ -d arch/%{asmarch}/include ]; then
        %{__cp} -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/
    fi
    if [ -d arch/%{asmarch}/syscalls ]; then
        %{__cp} -a --parents arch/%{asmarch}/syscalls $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/
    fi
    %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include
    pushd include > /dev/null
    %{__cp} -a * $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/
    popd > /dev/null
    %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/Kbuild
    # Ensure that objtool is present if CONFIG_STACK_VALIDATION is set.
    if %{_bindir}/grep -q '^CONFIG_STACK_VALIDATION=y$' .config; then
        %{__mkdir_p} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/tools/objtool
        %{__cp} -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/tools/objtool
    fi
    # Copy the generated autoconf.h file to the include/linux/ directory.
    %{__cp} include/generated/autoconf.h $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/linux/
    # Copy .config to include/config/auto.conf so a "make prepare" is unnecessary.
    %{__cp} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/.config $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/config/auto.conf
    # Now ensure that the Makefile, .config, auto.conf, autoconf.h and version.h files
    # all have matching timestamps so that external modules can be built.
    %{_bindir}/touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/.config
    %{_bindir}/touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/config/auto.conf
    %{_bindir}/touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/linux/autoconf.h
    %{_bindir}/touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/generated/autoconf.h
    %{_bindir}/touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/generated/uapi/linux/version.h

    # Remove any 'left-over' .cmd files.
    %{_bindir}/find $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build -name '*.cmd' -type f | \
        %{_bindir}/xargs --no-run-if-empty %{__rm} -f

    %{_bindir}/find $RPM_BUILD_ROOT/lib/modules/%{KVRFA} -name '*.ko' -type f > modnames

    # Mark the modules executable, so that strip-to-file can strip them.
    %{_bindir}/xargs --no-run-if-empty %{__chmod} u+x < modnames

    # Generate a list of modules for block and networking.
    %{_bindir}/grep -F /drivers/ modnames | %{_bindir}/xargs --no-run-if-empty nm -upA \
        | sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
        sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef | LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/modules.$1
        if [ ! -z "$3" ]; then
            sed -r -e "/^($3)\$/d" -i $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/modules.$1
        fi
    }

    collect_modules_list networking \
        'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt2x00(pci|usb)_probe|register_netdevice'

    collect_modules_list block \
        'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size|pktcdvd.ko|dm-mod.ko'

    collect_modules_list drm \
        'drm_open|drm_init'

    collect_modules_list modesetting \
        'drm_crtc_init'

    # Detect any missing or incorrect license tags.
    %{__rm} -f modinfo

    while read i
    do
        echo -n "${i#$RPM_BUILD_ROOT/lib/modules/%{KVRFA}/} " >> modinfo
        %{_sbindir}/modinfo -l $i >> modinfo
    done < modnames

    %{_bindir}/grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' modinfo && exit 1

    %{__rm} -f modinfo modnames

    # Remove all the files that will be auto generated by depmod at the kernel install time.
    for i in alias alias.bin builtin.bin ccwmap dep dep.bin devname ieee1394map inputmap isapnpmap ofmap pcimap seriomap softdep symbols symbols.bin usbmap
    do
        %{__rm} -f $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/modules.$i
    done

    # Move the development files out of the /lib/modules/ file system.
    %{__mkdir_p} $RPM_BUILD_ROOT/usr/src/kernels
    %{__mv} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build $RPM_BUILD_ROOT/usr/src/kernels/%{KVRFA}
    %{__ln_s} -f %{_usrsrc}/kernels/%{KVRFA} $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build
}

# Prepare the directories.
%{__rm} -rf $RPM_BUILD_ROOT
%{__mkdir_p} $RPM_BUILD_ROOT/boot
%{__mkdir_p} $RPM_BUILD_ROOT%{_libexecdir}

pushd linux-%{version}-%{release}.%{_target_cpu} > /dev/null

%if %{with_default}
BuildKernel
%endif

%if %{with_perf}
%global perf_make \
    %{__make} -s -C tools/perf %{?_smp_mflags} prefix=%{_prefix} lib=%{_lib} WERROR=0 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_LIBBABELTRACE=1 NO_LIBUNWIND=1 NO_LIBZSTD=1 NO_PERF_READ_VDSO32=1 NO_PERF_READ_VDSOX32=1 NO_STRLCPY=1

%{perf_make} all
%{perf_make} man
%endif

%if %{with_tools}
%ifarch x86_64
# Make sure that version-gen.sh is executable.
%{__chmod} +x tools/power/cpupower/utils/version-gen.sh
pushd tools/power/cpupower > /dev/null
%{__make} -s CPUFREQ_BENCH=false
popd > /dev/null
pushd tools/power/cpupower/debug/x86_64 > /dev/null
%{__make} -s centrino-decode
%{__make} -s powernow-k8-decode
popd > /dev/null
pushd tools/power/x86/x86_energy_perf_policy > /dev/null
%{__make} -s
popd > /dev/null
pushd tools/power/x86/turbostat > /dev/null
%{__make} -s
popd > /dev/null
%endif
pushd tools/thermal/tmon > /dev/null
%{__make} -s
popd > /dev/null
%endif

popd > /dev/null

%install
%if %{with_gcc10}
. /opt/rh/devtoolset-10/enable
%endif

pushd linux-%{version}-%{release}.%{_target_cpu} > /dev/null

%if %{with_headers}
# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

# Install kernel headers.
%{__make} -s ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Remove the unrequired files.
%{_bindir}/find $RPM_BUILD_ROOT/usr/include ! -name '*.h' -type f | \
    %{_bindir}/xargs --no-run-if-empty %{__rm} -f
%endif

%if %{with_doc}
DOCDIR=$RPM_BUILD_ROOT%{_datadir}/doc/%{name}-doc-%{version}

# Sometimes non-world-readable files sneak into the kernel source tree.
%{__chmod} -Rf a+rX,u+w,go-w Documentation

# Copy the documentation over.
%{__mkdir_p} $DOCDIR
%{__tar} -f - --exclude=man --exclude='.*' -c Documentation | %{__tar} -xf - -C $DOCDIR
%endif

%if %{with_perf}
# perf tool binary and supporting scripts/binaries.
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install

# perf-python extension.
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

# perf man pages. (Note: implicit rpm magic compresses them later.)
%{perf_make} DESTDIR=$RPM_BUILD_ROOT try-install-man
%endif

%if %{with_tools}
%ifarch x86_64
%{__make} -s -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
%{__rm} -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
pushd tools/power/cpupower/debug/x86_64 > /dev/null
%{__install} -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
%{__install} -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
popd > /dev/null
%{__chmod} 0755 %{buildroot}%{_libdir}/libcpupower.so*
%{__mkdir_p} %{buildroot}%{_unitdir}
%{__install} -m644 %{SOURCE2} %{buildroot}%{_unitdir}/cpupower.service
%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m644 %{SOURCE3} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%{__mkdir_p} %{buildroot}%{_mandir}/man8
pushd tools/power/x86/x86_energy_perf_policy > /dev/null
%{__make} -s DESTDIR=%{buildroot} install
popd > /dev/null
pushd tools/power/x86/turbostat > /dev/null
%{__make} -s DESTDIR=%{buildroot} install
popd > /dev/null
%{_bindir}/find %{buildroot}%{_mandir} -type f -print0 | \
    %{_bindir}/xargs -0 --no-run-if-empty %{__chmod} 644
%endif
pushd tools/thermal/tmon > /dev/null
%{__install} -m755 tmon %{buildroot}%{_bindir}/tmon
popd > /dev/null
%endif

popd > /dev/null

%clean
%{__rm} -rf $RPM_BUILD_ROOT

# Scripts section.
%if %{with_default}
%triggerin -- microcode_ctl
KVERSION=%{version}-%{release}.%{_target_cpu}
if [ -e "/lib/modules/$KVERSION/modules.dep" ]; then
     %{_bindir}/dracut -f --kver $KVERSION
fi

%posttrans
%{_sbindir}/new-kernel-pkg --package %{name} --mkinitrd --dracut --depmod --update %{version}-%{release}.%{_target_cpu} || exit $?
%{_sbindir}/new-kernel-pkg --package %{name} --rpmposttrans %{version}-%{release}.%{_target_cpu} || exit $?
if [ -x %{_sbindir}/weak-modules ]; then
    %{_sbindir}/weak-modules --add-kernel %{version}-%{release}.%{_target_cpu} || exit $?
fi

%post
%{_sbindir}/new-kernel-pkg --package %{name} --install %{version}-%{release}.%{_target_cpu} || exit $?

%preun
%{_sbindir}/new-kernel-pkg --rminitrd --rmmoddep --remove %{version}-%{release}.%{_target_cpu} || exit $?
if [ -x %{_sbindir}/weak-modules ]; then
    %{_sbindir}/weak-modules --remove-kernel %{version}-%{release}.%{_target_cpu} || exit $?
fi

%postun
for i in `ls /boot/initramfs*kdump.img 2>/dev/null`; do
    KDVER=`echo $i | sed -e's/^.*initramfs-//' -e's/kdump.*$//'`
    if [ ! -e /boot/vmlinuz-$KDVER ]; then
        %{__rm} -f $i
    fi
done

%post devel
if [ -f /etc/sysconfig/kernel ]; then
    . /etc/sysconfig/kernel || exit $?
fi
if [ "$HARDLINK" != "no" -a -x %{_sbindir}/hardlink ]; then
    pushd %{_usrsrc}/kernels/%{version}-%{release}.%{_target_cpu} > /dev/null
    %{_bindir}/find . -type f | while read f; do
        %{_sbindir}/hardlink -c %{_usrsrc}/kernels/*.fc*.*/$f $f
    done
    popd > /dev/null
fi
%endif

%if %{with_tools}
%post -n %{name}-tools
%{_sbindir}/ldconfig || exit $?

%postun -n %{name}-tools
%{_sbindir}/ldconfig || exit $?
%endif

# Files section.
%if %{with_default}
%files
%defattr(-,root,root)
/boot/vmlinuz-%{version}-%{release}.%{_target_cpu}
%attr(600,root,root) /boot/System.map-%{version}-%{release}.%{_target_cpu}
/boot/symvers-%{version}-%{release}.%{_target_cpu}.gz
/boot/config-%{version}-%{release}.%{_target_cpu}
%dir /lib/modules/%{version}-%{release}.%{_target_cpu}
/lib/modules/%{version}-%{release}.%{_target_cpu}/kernel
/lib/modules/%{version}-%{release}.%{_target_cpu}/build
/lib/modules/%{version}-%{release}.%{_target_cpu}/source
/lib/modules/%{version}-%{release}.%{_target_cpu}/extra
/lib/modules/%{version}-%{release}.%{_target_cpu}/updates
/lib/modules/%{version}-%{release}.%{_target_cpu}/weak-updates
%ifarch %{vdso_arches}
/lib/modules/%{version}-%{release}.%{_target_cpu}/vdso
/etc/ld.so.conf.d/%{name}-%{version}-%{release}.%{_target_cpu}.conf
%endif
/lib/modules/%{version}-%{release}.%{_target_cpu}/modules.*
%ghost /boot/initramfs-%{version}-%{release}.%{_target_cpu}.img

%files devel
%defattr(-,root,root)
%dir %{_usrsrc}/kernels
%{_usrsrc}/kernels/%{version}-%{release}.%{_target_cpu}
%endif

%if %{with_headers}
%files headers
%defattr(-,root,root)
%{_includedir}/*
%endif

%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/%{name}-doc-%{version}/Documentation/*
%dir %{_datadir}/doc/%{name}-doc-%{version}/Documentation
%dir %{_datadir}/doc/%{name}-doc-%{version}
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf
%{_bindir}/trace
%{_libdir}/libperf-jvmti.so
%dir %{_usr}/lib/perf/examples/bpf
%{_usr}/lib/perf/examples/bpf/*
%dir %{_usr}/lib/perf/include/bpf
%{_usr}/lib/perf/include/bpf/*
%dir %{_libdir}/traceevent/plugins
%{_libdir}/traceevent/plugins/*
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_mandir}/man[1-8]/perf*
%config(noreplace) %{_sysconfdir}/bash_completion.d/perf
%dir %{_datadir}/perf-core/strace/groups
%{_datadir}/perf-core/strace/groups/*
%dir %{_datadir}/doc/perf-tip
%{_datadir}/doc/perf-tip/*
%doc linux-%{version}-%{release}.%{_target_cpu}/tools/perf/Documentation/examples.txt

%files -n python-perf
%defattr(-,root,root)
%{python_sitearch}
%endif

%if %{with_tools}
%files -n %{name}-tools -f cpupower.lang
%defattr(-,root,root)

%ifarch x86_64
%{_bindir}/cpupower
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%{_bindir}/x86_energy_perf_policy
%{_bindir}/turbostat
%{_bindir}/tmon
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%{_unitdir}/cpupower.service
%{_prefix}/share/bash-completion/completions/cpupower
%{_mandir}/man[1-8]/cpupower*
%{_mandir}/man8/x86_energy_perf_policy*
%{_mandir}/man8/turbostat*

%files -n %{name}-tools-libs
%defattr(-,root,root)
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.1

%files -n %{name}-tools-libs-devel
%defattr(-,root,root)
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%{_includedir}/cpuidle.h
%endif
%endif

%changelog
* Sun Dec 07 2025 S.Tindall <s10dal@elepo.org> - 6.1.158-3
- Updated with the 6.1.158 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-6.1.158]
- Enable devtoolset-10

* Fri Dec 05 2025 S.Tindall <s10dal@elepo.org> - 6.1.158-1
- Updated with the 6.1.158 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-6.1.158]
- Removed: CONFIG_64BIT_TIME=y
- Removed: CONFIG_88EU_AP_MODE=y
- Removed: CONFIG_ACER_WIRELESS=m
- Removed: CONFIG_ACER_WMI=m
- Removed: CONFIG_ACPI_CMPC=m
- Removed: CONFIG_ACPI_NUMA=y
- Removed: CONFIG_ACPI_TOSHIBA=m
- Removed: CONFIG_ACPI_WMI=m
- Removed: CONFIG_ADIN_PHY=m
- Removed: CONFIG_ALIENWARE_WMI=m
- Removed: CONFIG_AMILO_RFKILL=m
- Removed: CONFIG_APPLE_GMUX=m
- Removed: CONFIG_APPLE_PROPERTIES=y
- Removed: CONFIG_ARCH_CLOCKSOURCE_DATA=y
- Removed: CONFIG_ARCH_DEFCONFIG="arch/x86/configs/x86_64_defconfig"
- Removed: CONFIG_ARCH_ENABLE_HUGEPAGE_MIGRATION=y
- Removed: CONFIG_ARCH_ENABLE_MEMORY_HOTPLUG=y
- Removed: CONFIG_ARCH_ENABLE_MEMORY_HOTREMOVE=y
- Removed: CONFIG_ARCH_ENABLE_SPLIT_PMD_PTLOCK=y
- Removed: CONFIG_ARCH_ENABLE_THP_MIGRATION=y
- Removed: CONFIG_ARCH_HAS_ADD_PAGES=y
- Removed: CONFIG_ARCH_HAS_CACHE_LINE_SIZE=y
- Removed: CONFIG_ARCH_HAS_DEVMEM_IS_ALLOWED=y
- Removed: CONFIG_ARCH_HAS_FILTER_PGPROT=y
- Removed: CONFIG_ARCH_HAS_KCOV=y
- Removed: CONFIG_ARCH_HAS_UACCESS_MCSAFE=y
- Removed: CONFIG_ARCH_HAS_UBSAN_SANITIZE_ALL=y
- Removed: CONFIG_ARCH_RANDOM=y
- Removed: CONFIG_ARCH_SELECT_MEMORY_MODEL=y
- Removed: CONFIG_ARCH_SUPPORTS_DEBUG_PAGEALLOC=y
- Removed: CONFIG_ARCH_WANT_GENERAL_HUGETLB=y
- Removed: CONFIG_ARCH_WANTS_THP_SWAP=y
- Removed: CONFIG_ASUS_NB_WMI=m
- Removed: CONFIG_ASUS_WIRELESS=m
- Removed: CONFIG_ASUS_WMI=m
- Removed: CONFIG_ASYMMETRIC_TPM_KEY_SUBTYPE=m
- Removed: CONFIG_AT803X_PHY=m
- Removed: CONFIG_AURORA_NB8800=m
- Removed: CONFIG_BACKLIGHT_GENERIC=y
- Removed: CONFIG_BACKLIGHT_PM8941_WLED=m
- Removed: CONFIG_BIG_KEYS=y
- Removed: CONFIG_BLK_DEV_BSG=y
- Removed: CONFIG_BLK_DEV_RSXX=m
- Removed: CONFIG_BLK_DEV_SKD=m
- Removed: CONFIG_BLK_DEV_UMEM=m
- Removed: CONFIG_BLK_SCSI_REQUEST=y
- Removed: CONFIG_BLK_WBT_MQ=y
- Removed: CONFIG_BNA=m
- Removed: CONFIG_BOOTPARAM_HARDLOCKUP_PANIC_VALUE=1
- Removed: CONFIG_BOOTPARAM_HUNG_TASK_PANIC_VALUE=0
- Removed: CONFIG_BOOTPARAM_SOFTLOCKUP_PANIC_VALUE=0
- Removed: CONFIG_BOUNCE=y
- Removed: CONFIG_BPF_JIT=y
- Removed: CONFIG_BPF_SYSCALL=y
- Removed: CONFIG_BPF_UNPRIV_DEFAULT_OFF=y
- Removed: CONFIG_BPF=y
- Removed: CONFIG_BROADCOM_PHY=m
- Removed: CONFIG_BUG_ON_DATA_CORRUPTION=y
- Removed: CONFIG_BUILDTIME_EXTABLE_SORT=y
- Removed: CONFIG_CAN_8DEV_USB=m
- Removed: CONFIG_CAN_CALC_BITTIMING=y
- Removed: CONFIG_CAN_CC770_ISA=m
- Removed: CONFIG_CAN_CC770=m
- Removed: CONFIG_CAN_CC770_PLATFORM=m
- Removed: CONFIG_CAN_C_CAN=m
- Removed: CONFIG_CAN_C_CAN_PCI=m
- Removed: CONFIG_CAN_C_CAN_PLATFORM=m
- Removed: CONFIG_CAN_DEV=m
- Removed: CONFIG_CAN_EMS_PCI=m
- Removed: CONFIG_CAN_EMS_PCMCIA=m
- Removed: CONFIG_CAN_EMS_USB=m
- Removed: CONFIG_CAN_ESD_USB2=m
- Removed: CONFIG_CAN_F81601=m
- Removed: CONFIG_CAN_GS_USB=m
- Removed: CONFIG_CAN_HI311X=m
- Removed: CONFIG_CAN_IFI_CANFD=m
- Removed: CONFIG_CAN_JANZ_ICAN3=m
- Removed: CONFIG_CAN_KVASER_PCIEFD=m
- Removed: CONFIG_CAN_KVASER_PCI=m
- Removed: CONFIG_CAN_KVASER_USB=m
- Removed: CONFIG_CAN_M_CAN=m
- Removed: CONFIG_CAN_M_CAN_PLATFORM=m
- Removed: CONFIG_CAN_M_CAN_TCAN4X5X=m
- Removed: CONFIG_CAN_MCBA_USB=m
- Removed: CONFIG_CAN_MCP251X=m
- Removed: CONFIG_CAN_PEAK_PCIEC=y
- Removed: CONFIG_CAN_PEAK_PCIEFD=m
- Removed: CONFIG_CAN_PEAK_PCI=m
- Removed: CONFIG_CAN_PEAK_PCMCIA=m
- Removed: CONFIG_CAN_PEAK_USB=m
- Removed: CONFIG_CAN_PLX_PCI=m
- Removed: CONFIG_CAN_SJA1000_ISA=m
- Removed: CONFIG_CAN_SJA1000=m
- Removed: CONFIG_CAN_SJA1000_PLATFORM=m
- Removed: CONFIG_CAN_SLCAN=m
- Removed: CONFIG_CAN_SOFTING_CS=m
- Removed: CONFIG_CAN_SOFTING=m
- Removed: CONFIG_CAN_UCAN=m
- Removed: CONFIG_CAN_VCAN=m
- Removed: CONFIG_CAN_VXCAN=m
- Removed: CONFIG_CAPI_AVM=y
- Removed: CONFIG_CC_HAS_ASM_GOTO=y
- Removed: CONFIG_CC_HAS_SANCOV_TRACE_PC=y
- Removed: CONFIG_CC_HAS_STACKPROTECTOR_NONE=y
- Removed: CONFIG_CEC_CORE=m
- Removed: CONFIG_CEC_NOTIFIER=y
- Removed: CONFIG_CHELSIO_IPSEC_INLINE=y
- Removed: CONFIG_CHROMEOS_LAPTOP=m
- Removed: CONFIG_CHROMEOS_PSTORE=m
- Removed: CONFIG_CHROMEOS_TBMC=m
- Removed: CONFIG_CHROME_PLATFORMS=y
- Removed: CONFIG_CIFS_WEAK_PW_HASH=y
- Removed: CONFIG_CLEANCACHE=y
- Removed: CONFIG_CLKDEV_LOOKUP=y
- Removed: CONFIG_COMMON_CLK=y
- Removed: CONFIG_COMPAL_LAPTOP=m
- Removed: CONFIG_CONTEXT_TRACKING=y
- Removed: CONFIG_CPU_FREQ_DEFAULT_GOV_ONDEMAND=y
- Removed: CONFIG_CROS_KBD_LED_BACKLIGHT=m
- Removed: CONFIG_CRYPTO_ADIANTUM=m
- Removed: CONFIG_CRYPTO_AEGIS128_AESNI_SSE2=m
- Removed: CONFIG_CRYPTO_AEGIS128=m
- Removed: CONFIG_CRYPTO_AES_NI_INTEL=m
- Removed: CONFIG_CRYPTO_AES_TI=m
- Removed: CONFIG_CRYPTO_AES=y
- Removed: CONFIG_CRYPTO_ANUBIS=m
- Removed: CONFIG_CRYPTO_ARC4=m
- Removed: CONFIG_CRYPTO_BLKCIPHER2=y
- Removed: CONFIG_CRYPTO_BLKCIPHER=y
- Removed: CONFIG_CRYPTO_BLOWFISH_COMMON=m
- Removed: CONFIG_CRYPTO_BLOWFISH=m
- Removed: CONFIG_CRYPTO_BLOWFISH_X86_64=m
- Removed: CONFIG_CRYPTO_CAMELLIA_AESNI_AVX2_X86_64=m
- Removed: CONFIG_CRYPTO_CAMELLIA_AESNI_AVX_X86_64=m
- Removed: CONFIG_CRYPTO_CAMELLIA=m
- Removed: CONFIG_CRYPTO_CAMELLIA_X86_64=m
- Removed: CONFIG_CRYPTO_CAST5_AVX_X86_64=m
- Removed: CONFIG_CRYPTO_CAST5=m
- Removed: CONFIG_CRYPTO_CAST6_AVX_X86_64=m
- Removed: CONFIG_CRYPTO_CAST6=m
- Removed: CONFIG_CRYPTO_CAST_COMMON=m
- Removed: CONFIG_CRYPTO_CCM=m
- Removed: CONFIG_CRYPTO_CHACHA20=m
- Removed: CONFIG_CRYPTO_CHACHA20POLY1305=m
- Removed: CONFIG_CRYPTO_CHACHA20_X86_64=m
- Removed: CONFIG_CRYPTO_CMAC=m
- Removed: CONFIG_CRYPTO_CRC32C_INTEL=m
- Removed: CONFIG_CRYPTO_CRC32C=y
- Removed: CONFIG_CRYPTO_CRC32=m
- Removed: CONFIG_CRYPTO_CRC32_PCLMUL=m
- Removed: CONFIG_CRYPTO_CRCT10DIF_PCLMUL=m
- Removed: CONFIG_CRYPTO_CRCT10DIF=y
- Removed: CONFIG_CRYPTO_DES3_EDE_X86_64=m
- Removed: CONFIG_CRYPTO_DES=m
- Removed: CONFIG_CRYPTO_DEV_CHELSIO_TLS=m
- Removed: CONFIG_CRYPTO_ECHAINIV=m
- Removed: CONFIG_CRYPTO_ESSIV=m
- Removed: CONFIG_CRYPTO_FCRYPT=m
- Removed: CONFIG_CRYPTO_GCM=y
- Removed: CONFIG_CRYPTO_GHASH_CLMUL_NI_INTEL=m
- Removed: CONFIG_CRYPTO_GLUE_HELPER_X86=m
- Removed: CONFIG_CRYPTO_HMAC=y
- Removed: CONFIG_CRYPTO_KEYWRAP=m
- Removed: CONFIG_CRYPTO_KHAZAD=m
- Removed: CONFIG_CRYPTO_LIB_AES=y
- Removed: CONFIG_CRYPTO_LIB_ARC4=m
- Removed: CONFIG_CRYPTO_LIB_DES=m
- Removed: CONFIG_CRYPTO_LIB_SHA256=y
- Removed: CONFIG_CRYPTO_NHPOLY1305_AVX2=m
- Removed: CONFIG_CRYPTO_NHPOLY1305_SSE2=m
- Removed: CONFIG_CRYPTO_POLY1305=m
- Removed: CONFIG_CRYPTO_POLY1305_X86_64=m
- Removed: CONFIG_CRYPTO_RMD128=m
- Removed: CONFIG_CRYPTO_RMD256=m
- Removed: CONFIG_CRYPTO_RMD320=m
- Removed: CONFIG_CRYPTO_SALSA20=m
- Removed: CONFIG_CRYPTO_SEED=m
- Removed: CONFIG_CRYPTO_SEQIV=y
- Removed: CONFIG_CRYPTO_SERPENT_AVX2_X86_64=m
- Removed: CONFIG_CRYPTO_SERPENT_AVX_X86_64=m
- Removed: CONFIG_CRYPTO_SERPENT=m
- Removed: CONFIG_CRYPTO_SERPENT_SSE2_X86_64=m
- Removed: CONFIG_CRYPTO_SHA1_SSSE3=m
- Removed: CONFIG_CRYPTO_SHA256_SSSE3=m
- Removed: CONFIG_CRYPTO_SHA512_SSSE3=m
- Removed: CONFIG_CRYPTO_SM3=m
- Removed: CONFIG_CRYPTO_SM4=m
- Removed: CONFIG_CRYPTO_TEA=m
- Removed: CONFIG_CRYPTO_TGR192=m
- Removed: CONFIG_CRYPTO_TWOFISH_AVX_X86_64=m
- Removed: CONFIG_CRYPTO_TWOFISH_COMMON=m
- Removed: CONFIG_CRYPTO_TWOFISH=m
- Removed: CONFIG_CRYPTO_TWOFISH_X86_64_3WAY=m
- Removed: CONFIG_CRYPTO_TWOFISH_X86_64=m
- Removed: CONFIG_CRYPTO_VMAC=m
- Removed: CONFIG_CRYPTO_XCBC=m
- Removed: CONFIG_CRYPTO_XXHASH=m
- Removed: CONFIG_CX_ECAT=m
- Removed: CONFIG_CYCLADES=m
- Removed: CONFIG_CYPRESS_FIRMWARE=m
- Removed: CONFIG_DAX_DRIVER=y
- Removed: CONFIG_DCDBAS=m
- Removed: CONFIG_DE4X5=m
- Removed: CONFIG_DEBUG_BOOT_PARAMS=y
- Removed: CONFIG_DEBUG_BUGVERBOSE=y
- Removed: CONFIG_DEBUG_FS=y
- Removed: CONFIG_DEBUG_KERNEL=y
- Removed: CONFIG_DEBUG_MISC=y
- Removed: CONFIG_DELL_LAPTOP=m
- Removed: CONFIG_DELL_RBTN=m
- Removed: CONFIG_DELL_RBU=m
- Removed: CONFIG_DELL_SMBIOS=m
- Removed: CONFIG_DELL_SMBIOS_SMM=y
- Removed: CONFIG_DELL_SMBIOS_WMI=y
- Removed: CONFIG_DELL_SMO8800=m
- Removed: CONFIG_DELL_WMI_AIO=m
- Removed: CONFIG_DELL_WMI_DESCRIPTOR=m
- Removed: CONFIG_DELL_WMI_LED=m
- Removed: CONFIG_DELL_WMI=m
- Removed: CONFIG_DEV_DAX_PMEM_COMPAT=m
- Removed: CONFIG_DEVMEM=y
- Removed: CONFIG_DEV_PAGEMAP_OPS=y
- Removed: CONFIG_DEVPORT=y
- Removed: CONFIG_DLCI=m
- Removed: CONFIG_DLCI_MAX=8
- Removed: CONFIG_DMA_VIRT_OPS=y
- Removed: CONFIG_DMIID=y
- Removed: CONFIG_DMI_SCAN_MACHINE_NON_EFI_FALLBACK=y
- Removed: CONFIG_DMI_SYSFS=y
- Removed: CONFIG_DOUBLEFAULT=y
- Removed: CONFIG_DP83822_PHY=m
- Removed: CONFIG_DP83848_PHY=m
- Removed: CONFIG_DP83867_PHY=m
- Removed: CONFIG_DP83TC811_PHY=m
- Removed: CONFIG_DPTF_POWER=m
- Removed: CONFIG_DRM_AMD_DC_DCN1_0=y
- Removed: CONFIG_DRM_AMD_DC_DCN2_0=y
- Removed: CONFIG_DRM_AMD_DC_DSC_SUPPORT=y
- Removed: CONFIG_DRM_BOCHS=m
- Removed: CONFIG_DRM_CIRRUS_QEMU=m
- Removed: CONFIG_DRM_DP_AUX_CHARDEV=y
- Removed: CONFIG_DRM_GEM_CMA_HELPER=y
- Removed: CONFIG_DRM_GEM_SHMEM_HELPER=y
- Removed: CONFIG_DRM_GMA3600=y
- Removed: CONFIG_DRM_GMA600=y
- Removed: CONFIG_DRM_I915_SPIN_REQUEST=5
- Removed: CONFIG_DRM_KMS_CMA_HELPER=y
- Removed: CONFIG_DRM_KMS_FB_HELPER=y
- Removed: CONFIG_DRM_VMWGFX_FBCON=y
- Removed: CONFIG_DVB_A8293=m
- Removed: CONFIG_DVB_AF9013=m
- Removed: CONFIG_DVB_AF9033=m
- Removed: CONFIG_DVB_AS102_FE=m
- Removed: CONFIG_DVB_AS102=m
- Removed: CONFIG_DVB_ASCOT2E=m
- Removed: CONFIG_DVB_ATBM8830=m
- Removed: CONFIG_DVB_AU8522_DTV=m
- Removed: CONFIG_DVB_AU8522=m
- Removed: CONFIG_DVB_AU8522_V4L=m
- Removed: CONFIG_DVB_AV7110_IR=y
- Removed: CONFIG_DVB_AV7110=m
- Removed: CONFIG_DVB_AV7110_OSD=y
- Removed: CONFIG_DVB_B2C2_FLEXCOP=m
- Removed: CONFIG_DVB_B2C2_FLEXCOP_USB=m
- Removed: CONFIG_DVB_BT8XX=m
- Removed: CONFIG_DVB_BUDGET_AV=m
- Removed: CONFIG_DVB_BUDGET_CI=m
- Removed: CONFIG_DVB_BUDGET_CORE=m
- Removed: CONFIG_DVB_BUDGET=m
- Removed: CONFIG_DVB_BUDGET_PATCH=m
- Removed: CONFIG_DVB_CORE=m
- Removed: CONFIG_DVB_CX24116=m
- Removed: CONFIG_DVB_CX24117=m
- Removed: CONFIG_DVB_CX24120=m
- Removed: CONFIG_DVB_CXD2820R=m
- Removed: CONFIG_DVB_CXD2841ER=m
- Removed: CONFIG_DVB_DDBRIDGE=m
- Removed: CONFIG_DVB_DRX39XYJ=m
- Removed: CONFIG_DVB_DRXD=m
- Removed: CONFIG_DVB_DS3000=m
- Removed: CONFIG_DVB_GP8PSK_FE=m
- Removed: CONFIG_DVB_HELENE=m
- Removed: CONFIG_DVB_HORUS3A=m
- Removed: CONFIG_DVB_IX2505V=m
- Removed: CONFIG_DVB_L64781=m
- Removed: CONFIG_DVB_LG2160=m
- Removed: CONFIG_DVB_LGDT330X=m
- Removed: CONFIG_DVB_LNBH25=m
- Removed: CONFIG_DVB_LNBP21=m
- Removed: CONFIG_DVB_LNBP22=m
- Removed: CONFIG_DVB_M88DS3103=m
- Removed: CONFIG_DVB_MB86A16=m
- Removed: CONFIG_DVB_MT352=m
- Removed: CONFIG_DVB_MXL5XX=m
- Removed: CONFIG_DVB_NETUP_UNIDVB=m
- Removed: CONFIG_DVB_NXT200X=m
- Removed: CONFIG_DVB_NXT6000=m
- Removed: CONFIG_DVB_OR51132=m
- Removed: CONFIG_DVB_OR51211=m
- Removed: CONFIG_DVB_PLUTO2=m
- Removed: CONFIG_DVB_PT1=m
- Removed: CONFIG_DVB_PT3=m
- Removed: CONFIG_DVB_S921=m
- Removed: CONFIG_DVB_SI2165=m
- Removed: CONFIG_DVB_SI21XX=m
- Removed: CONFIG_DVB_SP8870=m
- Removed: CONFIG_DVB_SP887X=m
- Removed: CONFIG_DVB_STV0288=m
- Removed: CONFIG_DVB_STV0297=m
- Removed: CONFIG_DVB_STV0367=m
- Removed: CONFIG_DVB_STV6110=m
- Removed: CONFIG_DVB_TC90522=m
- Removed: CONFIG_DVB_TDA10048=m
- Removed: CONFIG_DVB_TDA1004X=m
- Removed: CONFIG_DVB_TDA10071=m
- Removed: CONFIG_DVB_TDA18271C2DD=m
- Removed: CONFIG_DVB_TDA665x=m
- Removed: CONFIG_DVB_TDA8083=m
- Removed: CONFIG_DVB_TUA6100=m
- Removed: CONFIG_DVB_TUNER_CX24113=m
- Removed: CONFIG_DVB_TUNER_ITD1000=m
- Removed: CONFIG_DVB_USB_A800=m
- Removed: CONFIG_DVB_USB_AF9005=m
- Removed: CONFIG_DVB_USB_AF9005_REMOTE=m
- Removed: CONFIG_DVB_USB_AZ6027=m
- Removed: CONFIG_DVB_USB_CINERGY_T2=m
- Removed: CONFIG_DVB_USB_CXUSB=m
- Removed: CONFIG_DVB_USB_DIB0700=m
- Removed: CONFIG_DVB_USB_DIB3000MC=m
- Removed: CONFIG_DVB_USB_DIBUSB_MB=m
- Removed: CONFIG_DVB_USB_DIBUSB_MC=m
- Removed: CONFIG_DVB_USB_DIGITV=m
- Removed: CONFIG_DVB_USB_DTT200U=m
- Removed: CONFIG_DVB_USB_DTV5100=m
- Removed: CONFIG_DVB_USB_DVBSKY=m
- Removed: CONFIG_DVB_USB_DW2102=m
- Removed: CONFIG_DVB_USB_GP8PSK=m
- Removed: CONFIG_DVB_USB=m
- Removed: CONFIG_DVB_USB_M920X=m
- Removed: CONFIG_DVB_USB_NOVA_T_USB2=m
- Removed: CONFIG_DVB_USB_OPERA1=m
- Removed: CONFIG_DVB_USB_PCTV452E=m
- Removed: CONFIG_DVB_USB_TECHNISAT_USB2=m
- Removed: CONFIG_DVB_USB_TTUSB2=m
- Removed: CONFIG_DVB_USB_UMT_010=m
- Removed: CONFIG_DVB_USB_VP702X=m
- Removed: CONFIG_DVB_USB_VP7045=m
- Removed: CONFIG_DVB_VES1820=m
- Removed: CONFIG_DVB_VES1X93=m
- Removed: CONFIG_DVB_ZL10036=m
- Removed: CONFIG_DVB_ZL10039=m
- Removed: CONFIG_DVB_ZL10353=m
- Removed: CONFIG_DYNAMIC_FTRACE_WITH_REGS=y
- Removed: CONFIG_DYNAMIC_FTRACE=y
- Removed: CONFIG_EARLY_PRINTK_DBGP=y
- Removed: CONFIG_EARLY_PRINTK_USB=y
- Removed: CONFIG_EARLY_PRINTK=y
- Removed: CONFIG_EDD=m
- Removed: CONFIG_EEEPC_LAPTOP=m
- Removed: CONFIG_EEEPC_WMI=m
- Removed: CONFIG_EFI_CUSTOM_SSDT_OVERLAYS=y
- Removed: CONFIG_EFI_DEV_PATH_PARSER=y
- Removed: CONFIG_EFI_EARLYCON=y
- Removed: CONFIG_EFI_ESRT=y
- Removed: CONFIG_EFI_RUNTIME_MAP=y
- Removed: CONFIG_EFI_RUNTIME_WRAPPERS=y
- Removed: CONFIG_EFI_VARS_PSTORE_DEFAULT_DISABLE=y
- Removed: CONFIG_EFI_VARS_PSTORE=y
- Removed: CONFIG_EFI_VARS=y
- Removed: CONFIG_ENABLE_MUST_CHECK=y
- Removed: CONFIG_EROFS_FS_CLUSTER_PAGE_LIMIT=1
- Removed: CONFIG_EXFAT_DEFAULT_CODEPAGE=437
- Removed: CONFIG_EXFAT_DEFAULT_IOCHARSET="utf8"
- Removed: CONFIG_EXFAT_DISCARD=y
- Removed: CONFIG_EXFAT_DONT_MOUNT_VFAT=y
- Removed: CONFIG_EXFAT_FS=m
- Removed: CONFIG_FB_BOOT_VESA_SUPPORT=y
- Removed: CONFIG_FIREWIRE_SERIAL=m
- Removed: CONFIG_FIRMWARE_MEMMAP=y
- Removed: CONFIG_FIXED_PHY=y
- Removed: CONFIG_FRAME_VECTOR=y
- Removed: CONFIG_FUNCTION_ERROR_INJECTION=y
- Removed: CONFIG_FUNCTION_PROFILER=y
- Removed: CONFIG_FW_CFG_SYSFS=m
- Removed: CONFIG_FWTTY_MAX_CARD_PORTS=32
- Removed: CONFIG_FWTTY_MAX_TOTAL_PORTS=64
- Removed: CONFIG_GENERIC_FIND_FIRST_BIT=y
- Removed: CONFIG_GIGASET_BASE=m
- Removed: CONFIG_GIGASET_CAPI=y
- Removed: CONFIG_GIGASET_M101=m
- Removed: CONFIG_GIGASET_M105=m
- Removed: CONFIG_GPIO_ADP5588=m
- Removed: CONFIG_GPIO_LYNXPOINT=m
- Removed: CONFIG_HARDENED_USERCOPY_FALLBACK=y
- Removed: CONFIG_HAVE_ARCH_KGDB=y
- Removed: CONFIG_HAVE_CLK_PREPARE=y
- Removed: CONFIG_HAVE_CLK=y
- Removed: CONFIG_HAVE_CONTEXT_TRACKING=y
- Removed: CONFIG_HAVE_COPY_THREAD_TLS=y
- Removed: CONFIG_HAVE_EBPF_JIT=y
- Removed: CONFIG_HAVE_IDE=y
- Removed: CONFIG_HAVE_MEMBLOCK_NODE_MAP=y
- Removed: CONFIG_HAVE_MEMORY_PRESENT=y
- Removed: CONFIG_HAVE_MMIOTRACE_SUPPORT=y
- Removed: CONFIG_HAVE_NET_DSA=y
- Removed: CONFIG_HAVE_OPROFILE=y
- Removed: CONFIG_HAVE_RCU_TABLE_FREE=y
- Removed: CONFIG_HAVE_SETUP_PER_CPU_AREA=y
- Removed: CONFIG_HP100=m
- Removed: CONFIG_HP_ACCEL=m
- Removed: CONFIG_HP_WIRELESS=m
- Removed: CONFIG_HP_WMI=m
- Removed: CONFIG_HUAWEI_WMI=m
- Removed: CONFIG_HVC_DRIVER=y
- Removed: CONFIG_HVC_IRQ=y
- Removed: CONFIG_HVC_XEN_FRONTEND=y
- Removed: CONFIG_HVC_XEN=y
- Removed: CONFIG_HYSDN_CAPI=y
- Removed: CONFIG_HYSDN=m
- Removed: CONFIG_I2C_DESIGNWARE_PCI=m
- Removed: CONFIG_I2C_DESIGNWARE_PLATFORM=m
- Removed: CONFIG_I2C_HID=m
- Removed: CONFIG_I2C_PARPORT_LIGHT=m
- Removed: CONFIG_I8K=m
- Removed: CONFIG_IBM_RTL=m
- Removed: CONFIG_INFINIBAND_BNXT_RE=m
- Removed: CONFIG_INFINIBAND_CXGB3=m
- Removed: CONFIG_INFINIBAND_I40IW=m
- Removed: CONFIG_INFINIBAND_MTHCA=m
- Removed: CONFIG_INFINIBAND_OCRDMA=m
- Removed: CONFIG_INFINIBAND_QIB_DCA=y
- Removed: CONFIG_INFINIBAND_QIB=m
- Removed: CONFIG_INFINIBAND_USNIC=m
- Removed: CONFIG_INFINIBAND_VMWARE_PVRDMA=m
- Removed: CONFIG_INLINE_READ_UNLOCK_IRQ=y
- Removed: CONFIG_INLINE_READ_UNLOCK=y
- Removed: CONFIG_INLINE_SPIN_UNLOCK_IRQ=y
- Removed: CONFIG_INLINE_WRITE_UNLOCK_IRQ=y
- Removed: CONFIG_INLINE_WRITE_UNLOCK=y
- Removed: CONFIG_INPUT_GP2A=m
- Removed: CONFIG_INPUT_KXTJ9_POLLED_MODE=y
- Removed: CONFIG_INPUT_POLLDEV=m
- Removed: CONFIG_INTEL_HID_EVENT=m
- Removed: CONFIG_INTEL_INT0002_VGPIO=m
- Removed: CONFIG_INTEL_IPS=m
- Removed: CONFIG_INTEL_MENLOW=m
- Removed: CONFIG_INTEL_OAKTRAIL=m
- Removed: CONFIG_INTEL_PMC_CORE=m
- Removed: CONFIG_INTEL_PMC_IPC=m
- Removed: CONFIG_INTEL_PUNIT_IPC=m
- Removed: CONFIG_INTEL_RST=m
- Removed: CONFIG_INTEL_SMARTCONNECT=m
- Removed: CONFIG_INTEL_VBTN=m
- Removed: CONFIG_INTEL_WMI_THUNDERBOLT=m
- Removed: CONFIG_IO_DELAY_0X80=y
- Removed: CONFIG_IR_FINTEK=m
- Removed: CONFIG_IR_IGORPLUGUSB=m
- Removed: CONFIG_IR_IGUANA=m
- Removed: CONFIG_IR_IMON_DECODER=m
- Removed: CONFIG_IR_JVC_DECODER=m
- Removed: CONFIG_IR_MCE_KBD_DECODER=m
- Removed: CONFIG_IR_MCEUSB=m
- Removed: CONFIG_IR_RCMM_DECODER=m
- Removed: CONFIG_IR_SERIAL=m
- Removed: CONFIG_IR_SERIAL_TRANSMITTER=y
- Removed: CONFIG_IR_SIR=m
- Removed: CONFIG_IR_SONY_DECODER=m
- Removed: CONFIG_IR_WINBOND_CIR=m
- Removed: CONFIG_ISCSI_IBFT_FIND=y
- Removed: CONFIG_ISCSI_IBFT=m
- Removed: CONFIG_ISDN_CAPI_CAPI20=m
- Removed: CONFIG_ISDN_DRV_AVMB1_AVM_CS=m
- Removed: CONFIG_ISDN_DRV_AVMB1_B1PCI=m
- Removed: CONFIG_ISDN_DRV_AVMB1_B1PCIV4=y
- Removed: CONFIG_ISDN_DRV_AVMB1_B1PCMCIA=m
- Removed: CONFIG_ISDN_DRV_AVMB1_C4=m
- Removed: CONFIG_ISDN_DRV_AVMB1_T1PCI=m
- Removed: CONFIG_ISDN_DRV_GIGASET=m
- Removed: CONFIG_ISI=m
- Removed: CONFIG_KASAN_STACK=1
- Removed: CONFIG_KDB_CONTINUE_CATASTROPHIC=0
- Removed: CONFIG_KDB_DEFAULT_ENABLE=0x1
- Removed: CONFIG_KDB_KEYBOARD=y
- Removed: CONFIG_KEYS_COMPAT=y
- Removed: CONFIG_KGDB_KDB=y
- Removed: CONFIG_KGDB_LOW_LEVEL_TRAP=y
- Removed: CONFIG_KGDB_SERIAL_CONSOLE=y
- Removed: CONFIG_KGDB_TESTS=y
- Removed: CONFIG_KGDB=y
- Removed: CONFIG_KVM_MMU_AUDIT=y
- Removed: CONFIG_LANMEDIA=m
- Removed: CONFIG_LEDS_CLEVO_MAIL=m
- Removed: CONFIG_LEDS_LP5521=m
- Removed: CONFIG_LEDS_LP5523=m
- Removed: CONFIG_LEDS_LP5562=m
- Removed: CONFIG_LEDS_LP55XX_COMMON=m
- Removed: CONFIG_LEDS_LP8501=m
- Removed: CONFIG_LEGACY_VSYSCALL_EMULATE=y
- Removed: CONFIG_LG_LAPTOP=m
- Removed: CONFIG_LXT_PHY=m
- Removed: CONFIG_MANDATORY_FILE_LOCKING=y
- Removed: CONFIG_MAX_RAW_DEVS=8192
- Removed: CONFIG_MDIO_BCM_UNIMAC=m
- Removed: CONFIG_MDIO_BITBANG=m
- Removed: CONFIG_MDIO_BUS=y
- Removed: CONFIG_MDIO_CAVIUM=m
- Removed: CONFIG_MDIO_DEVICE=y
- Removed: CONFIG_MDIO_GPIO=m
- Removed: CONFIG_MDIO_I2C=m
- Removed: CONFIG_MDIO_THUNDER=m
- Removed: CONFIG_MEDIA_CEC_RC=y
- Removed: CONFIG_MEDIA_CEC_SUPPORT=y
- Removed: CONFIG_MEDIA_CONTROLLER_DVB=y
- Removed: CONFIG_MEDIA_CONTROLLER=y
- Removed: CONFIG_MEDIA_SUBDRV_AUTOSELECT=y
- Removed: CONFIG_MEDIA_TUNER_E4000=m
- Removed: CONFIG_MEDIA_TUNER_FC0011=m
- Removed: CONFIG_MEDIA_TUNER_FC0012=m
- Removed: CONFIG_MEDIA_TUNER_FC0013=m
- Removed: CONFIG_MEDIA_TUNER_FC2580=m
- Removed: CONFIG_MEDIA_TUNER_IT913X=m
- Removed: CONFIG_MEDIA_TUNER_M88RS6000T=m
- Removed: CONFIG_MEDIA_TUNER_MAX2165=m
- Removed: CONFIG_MEDIA_TUNER_MC44S803=m
- Removed: CONFIG_MEDIA_TUNER_MT20XX=m
- Removed: CONFIG_MEDIA_TUNER_MT2266=m
- Removed: CONFIG_MEDIA_TUNER_MXL301RF=m
- Removed: CONFIG_MEDIA_TUNER_QM1D1B0004=m
- Removed: CONFIG_MEDIA_TUNER_QM1D1C0042=m
- Removed: CONFIG_MEDIA_TUNER_QT1010=m
- Removed: CONFIG_MEDIA_TUNER_R820T=m
- Removed: CONFIG_MEDIA_TUNER_SI2157=m
- Removed: CONFIG_MEDIA_TUNER_SIMPLE=m
- Removed: CONFIG_MEDIA_TUNER_TDA18218=m
- Removed: CONFIG_MEDIA_TUNER_TDA18250=m
- Removed: CONFIG_MEDIA_TUNER_TDA18271=m
- Removed: CONFIG_MEDIA_TUNER_TDA827X=m
- Removed: CONFIG_MEDIA_TUNER_TDA8290=m
- Removed: CONFIG_MEDIA_TUNER_TDA9887=m
- Removed: CONFIG_MEDIA_TUNER_TEA5761=m
- Removed: CONFIG_MEDIA_TUNER_TEA5767=m
- Removed: CONFIG_MEDIA_TUNER_XC2028=m
- Removed: CONFIG_MEDIA_TUNER_XC4000=m
- Removed: CONFIG_MEDIA_TUNER_XC5000=m
- Removed: CONFIG_MEMCG_SWAP_ENABLED=y
- Removed: CONFIG_MEMCG_SWAP=y
- Removed: CONFIG_MEMORY_HOTPLUG_SPARSE=y
- Removed: CONFIG_MICROCODE_OLD_INTERFACE=y
- Removed: CONFIG_MLX4_INFINIBAND=m
- Removed: CONFIG_MLX5_ACCEL=y
- Removed: CONFIG_MLX5_INFINIBAND=m
- Removed: CONFIG_MLX_PLATFORM=m
- Removed: CONFIG_MOXA_INTELLIO=m
- Removed: CONFIG_MOXA_SMARTIO=m
- Removed: CONFIG_MSI_LAPTOP=m
- Removed: CONFIG_MSI_WMI=m
- Removed: CONFIG_MXM_WMI=m
- Removed: CONFIG_ND_BLK=m
- Removed: CONFIG_NEED_MULTIPLE_NODES=y
- Removed: CONFIG_NEED_PER_CPU_EMBED_FIRST_CHUNK=y
- Removed: CONFIG_NEED_PER_CPU_PAGE_FIRST_CHUNK=y
- Removed: CONFIG_NET_VENDOR_AURORA=y
- Removed: CONFIG_NET_VENDOR_BROCADE=y
- Removed: CONFIG_NET_VENDOR_HP=y
- Removed: CONFIG_NET_VENDOR_NI=y
- Removed: CONFIG_NET_VENDOR_SILAN=y
- Removed: CONFIG_NET_VENDOR_SIS=y
- Removed: CONFIG_NF_FLOW_TABLE_IPV4=m
- Removed: CONFIG_NF_FLOW_TABLE_IPV6=m
- Removed: CONFIG_NF_LOG_BRIDGE=m
- Removed: CONFIG_NF_LOG_COMMON=m
- Removed: CONFIG_NF_LOG_NETDEV=m
- Removed: CONFIG_NFSD_V2_ACL=y
- Removed: CONFIG_NFSD_V3=y
- Removed: CONFIG_NF_TABLES_SET=m
- Removed: CONFIG_NFT_COUNTER=m
- Removed: CONFIG_N_GSM=m
- Removed: CONFIG_N_HDLC=m
- Removed: CONFIG_NI_XGE_MANAGEMENT_ENET=m
- Removed: CONFIG_NODES_SPAN_OTHER_NODES=y
- Removed: CONFIG_NOZOMI=m
- Removed: CONFIG_NVRAM=y
- Removed: CONFIG_OPROFILE_EVENT_MULTIPLEX=y
- Removed: CONFIG_OPROFILE=m
- Removed: CONFIG_OPROFILE_NMI_TIMER=y
- Removed: CONFIG_OPTIMIZE_INLINING=y
- Removed: CONFIG_PAGE_TABLE_ISOLATION=y
- Removed: CONFIG_PANASONIC_LAPTOP=m
- Removed: CONFIG_PANIC_ON_OOPS_VALUE=1
- Removed: CONFIG_PANIC_ON_OOPS=y
- Removed: CONFIG_PANIC_TIMEOUT=0
- Removed: CONFIG_PEAQ_WMI=m
- Removed: CONFIG_PINCTRL_AMD=m
- Removed: CONFIG_PINCTRL_INTEL=m
- Removed: CONFIG_PLUGIN_HOSTCC=""
- Removed: CONFIG_PMC_ATOM=y
- Removed: CONFIG_PRINTK_NMI=y
- Removed: CONFIG_PVPANIC=y
- Removed: CONFIG_QUOTACTL_COMPAT=y
- Removed: CONFIG_RADIO_ADAPTERS=y
- Removed: CONFIG_RADIO_MAXIRADIO=m
- Removed: CONFIG_RADIO_SAA7706H=m
- Removed: CONFIG_RADIO_SHARK2=m
- Removed: CONFIG_RADIO_SHARK=m
- Removed: CONFIG_RADIO_SI4713=m
- Removed: CONFIG_RADIO_TEA5764=m
- Removed: CONFIG_RADIO_TEF6862=m
- Removed: CONFIG_RADIO_WL1273=m
- Removed: CONFIG_RAW_DRIVER=y
- Removed: CONFIG_RC_ATI_REMOTE=m
- Removed: CONFIG_RC_MAP=m
- Removed: CONFIG_REGULATOR_ANATOP=m
- Removed: CONFIG_REGULATOR_PFUZE100=m
- Removed: CONFIG_RETPOLINE=y
- Removed: CONFIG_RING_BUFFER_ALLOW_SWAP=y
- Removed: CONFIG_ROCKETPORT=m
- Removed: CONFIG_RTC_DRV_RX6110=m
- Removed: CONFIG_RTW88_8822BE=y
- Removed: CONFIG_RTW88_8822CE=y
- Removed: CONFIG_SAMSUNG_LAPTOP=m
- Removed: CONFIG_SAMSUNG_Q10=m
- Removed: CONFIG_SBNI=m
- Removed: CONFIG_SC92031=m
- Removed: CONFIG_SCSI_DPT_I2O=m
- Removed: CONFIG_SCSI_GDTH=m
- Removed: CONFIG_SCSI_UFSHCD=m
- Removed: CONFIG_SCSI_UFSHCD_PCI=m
- Removed: CONFIG_SECCOMP=y
- Removed: CONFIG_SELECT_MEMORY_MODEL=y
- Removed: CONFIG_SENSORS_ADM1021=m
- Removed: CONFIG_SENSORS_ASPEED=m
- Removed: CONFIG_SENSORS_HDAPS=m
- Removed: CONFIG_SENSORS_MAX6642=m
- Removed: CONFIG_SERIAL_NONSTANDARD=y
- Removed: CONFIG_SFI=y
- Removed: CONFIG_SFP=m
- Removed: CONFIG_SIS190=m
- Removed: CONFIG_SIS900=m
- Removed: CONFIG_SLAB_MERGE_DEFAULT=y
- Removed: CONFIG_SLUB_CPU_PARTIAL=y
- Removed: CONFIG_SLUB_DEBUG=y
- Removed: CONFIG_SLUB=y
- Removed: CONFIG_SMS_SDIO_DRV=m
- Removed: CONFIG_SMS_SIANO_MDTV=m
- Removed: CONFIG_SMS_SIANO_RC=y
- Removed: CONFIG_SMS_USB_DRV=m
- Removed: CONFIG_SND_INTEL_NHLT=m
- Removed: CONFIG_SND_SOC_INTEL_HASWELL=m
- Removed: CONFIG_SND_SOC_INTEL_HASWELL_MACH=m
- Removed: CONFIG_SND_SOC_INTEL_SST_ACPI=m
- Removed: CONFIG_SND_SOC_INTEL_SST_FIRMWARE=m
- Removed: CONFIG_SND_SOC_SIRF_AUDIO_CODEC=m
- Removed: CONFIG_SND_SOC_SOF_APOLLOLAKE_SUPPORT=y
- Removed: CONFIG_SND_SOC_SOF_BAYTRAIL_SUPPORT=y
- Removed: CONFIG_SND_SOC_SOF_CANNONLAKE_SUPPORT=y
- Removed: CONFIG_SND_SOC_SOF_COFFEELAKE_SUPPORT=y
- Removed: CONFIG_SND_SOC_SOF_COMETLAKE_H=m
- Removed: CONFIG_SND_SOC_SOF_COMETLAKE_H_SUPPORT=y
- Removed: CONFIG_SND_SOC_SOF_COMETLAKE_LP=m
- Removed: CONFIG_SND_SOC_SOF_COMETLAKE_LP_SUPPORT=y
- Removed: CONFIG_SND_SOC_SOF_ELKHARTLAKE_SUPPORT=y
- Removed: CONFIG_SND_SOC_SOF_GEMINILAKE_SUPPORT=y
- Removed: CONFIG_SND_SOC_SOF_ICELAKE_SUPPORT=y
- Removed: CONFIG_SND_SOC_SOF_INTEL_ACPI=m
- Removed: CONFIG_SND_SOC_SOF_INTEL_PCI=m
- Removed: CONFIG_SND_SOC_SOF_MERRIFIELD_SUPPORT=y
- Removed: CONFIG_SND_SOC_SOF_OPTIONS=m
- Removed: CONFIG_SND_SOC_SOF_TIGERLAKE_SUPPORT=y
- Removed: CONFIG_SND_SOC_TLV320AIC3X=m
- Removed: CONFIG_SND_SOC_WM8731=m
- Removed: CONFIG_SND_SOC_ZX_AUD96P22=m
- Removed: CONFIG_SND_SST_IPC_ACPI=m
- Removed: CONFIG_SND_SST_IPC=m
- Removed: CONFIG_SND_SST_IPC_PCI=m
- Removed: CONFIG_SONY_LAPTOP=m
- Removed: CONFIG_SONYPI_COMPAT=y
- Removed: CONFIG_SPARSEMEM_MANUAL=y
- Removed: CONFIG_STACK_TRACER=y
- Removed: CONFIG_STRICT_DEVMEM=y
- Removed: CONFIG_SURFACE3_WMI=m
- Removed: CONFIG_SURFACE_PLATFORMS=y
- Removed: CONFIG_SURFACE_PRO3_BUTTON=m
- Removed: CONFIG_SWAP=y
- Removed: CONFIG_SYNCLINK_GT=m
- Removed: CONFIG_SYNCLINK=m
- Removed: CONFIG_SYNCLINKMP=m
- Removed: CONFIG_SYSVIPC_COMPAT=y
- Removed: CONFIG_TABLET_USB_GTCO=m
- Removed: CONFIG_THERMAL_GOV_POWER_ALLOCATOR=y
- Removed: CONFIG_THUNDERBOLT=m
- Removed: CONFIG_TOPSTAR_LAPTOP=m
- Removed: CONFIG_TOSHIBA_BT_RFKILL=m
- Removed: CONFIG_TOSHIBA_HAPS=m
- Removed: CONFIG_TOSHIBA_WMI=m
- Removed: CONFIG_TOUCHSCREEN_PROPERTIES=y
- Removed: CONFIG_TPM_KEY_PARSER=m
- Removed: CONFIG_TRACE_IRQFLAGS_SUPPORT=y
- Removed: CONFIG_TRANSPARENT_HUGE_PAGECACHE=y
- Removed: CONFIG_TTPCI_EEPROM=m
- Removed: CONFIG_UBSAN_ALIGNMENT=y
- Removed: CONFIG_UEFI_CPER_X86=y
- Removed: CONFIG_UEFI_CPER=y
- Removed: CONFIG_UNIX_SCM=y
- Removed: CONFIG_UNWINDER_FRAME_POINTER=y
- Removed: CONFIG_USB_CHIPIDEA_PCI=m
- Removed: CONFIG_USB_DSBR=m
- Removed: CONFIG_USB_GL860=m
- Removed: CONFIG_USB_GSPCA_SPCA1528=m
- Removed: CONFIG_USB_KEENE=m
- Removed: CONFIG_USB_M5602=m
- Removed: CONFIG_USB_MA901=m
- Removed: CONFIG_USB_MR800=m
- Removed: CONFIG_USB_PULSE8_CEC=m
- Removed: CONFIG_USB_RAINSHADOW_CEC=m
- Removed: CONFIG_USB_RAREMONO=m
- Removed: CONFIG_USB_SERIAL_XIRCOM=m
- Removed: CONFIG_USB_STKWEBCAM=m
- Removed: CONFIG_USB_STV06XX=m
- Removed: CONFIG_USB_VIDEO_CLASS_INPUT_EVDEV=y
- Removed: CONFIG_USB_VIDEO_CLASS=m
- Removed: CONFIG_USB_WUSB_CBAF=m
- Removed: CONFIG_USB_ZR364XX=m
- Removed: CONFIG_USE_PERCPU_NUMA_NODE_ID=y
- Removed: CONFIG_USERFAULTFD=y
- Removed: CONFIG_UWB_HWA=m
- Removed: CONFIG_UWB_I1480U=m
- Removed: CONFIG_UWB=m
- Removed: CONFIG_UWB_WHCI=m
- Removed: CONFIG_VFIO=m
- Removed: CONFIG_VFIO_PCI=m
- Removed: CONFIG_VGA_ARB_MAX_GPUS=64
- Removed: CONFIG_VGA_ARB=y
- Removed: CONFIG_VHOST=m
- Removed: CONFIG_VHOST_NET=m
- Removed: CONFIG_VHOST_SCSI=m
- Removed: CONFIG_VHOST_VSOCK=m
- Removed: CONFIG_VIDEO_BT848=m
- Removed: CONFIG_VIDEO_CPIA2=m
- Removed: CONFIG_VIDEO_CS3308=m
- Removed: CONFIG_VIDEO_CS5345=m
- Removed: CONFIG_VIDEO_CS53L32A=m
- Removed: CONFIG_VIDEO_DT3155=m
- Removed: CONFIG_VIDEO_GO7007_LOADER=m
- Removed: CONFIG_VIDEO_GO7007=m
- Removed: CONFIG_VIDEO_GO7007_USB=m
- Removed: CONFIG_VIDEO_GO7007_USB_S2250_BOARD=m
- Removed: CONFIG_VIDEO_HDPVR=m
- Removed: CONFIG_VIDEO_HEXIUM_GEMINI=m
- Removed: CONFIG_VIDEO_HEXIUM_ORION=m
- Removed: CONFIG_VIDEO_M52790=m
- Removed: CONFIG_VIDEO_MEYE=m
- Removed: CONFIG_VIDEO_MSP3400=m
- Removed: CONFIG_VIDEO_MT9V011=m
- Removed: CONFIG_VIDEO_MXB=m
- Removed: CONFIG_VIDEO_OV2640=m
- Removed: CONFIG_VIDEO_OV7640=m
- Removed: CONFIG_VIDEO_SAA7127=m
- Removed: CONFIG_VIDEO_SAA7146=m
- Removed: CONFIG_VIDEO_SAA7146_VV=m
- Removed: CONFIG_VIDEO_SONY_BTF_MPX=m
- Removed: CONFIG_VIDEO_TDA1997X=m
- Removed: CONFIG_VIDEO_TM6000_ALSA=m
- Removed: CONFIG_VIDEO_TM6000_DVB=m
- Removed: CONFIG_VIDEO_TM6000=m
- Removed: CONFIG_VIDEO_TVAUDIO=m
- Removed: CONFIG_VIDEO_USBVISION=m
- Removed: CONFIG_VIDEO_V4L2=m
- Removed: CONFIG_VIDEO_V4L2_SUBDEV_API=y
- Removed: CONFIG_VIDEO_WM8739=m
- Removed: CONFIG_VIDEO_WM8775=m
- Removed: CONFIG_VIRT_TO_BUS=y
- Removed: CONFIG_VM_EVENT_COUNTERS=y
- Removed: CONFIG_VXGE=m
- Removed: CONFIG_WMI_BMOF=m
- Removed: CONFIG_X86_DECODER_SELFTEST=y
- Removed: CONFIG_X86_DEV_DMA_OPS=y
- Removed: CONFIG_X86_INTEL_UMIP=y
- Removed: CONFIG_X86_RESERVE_LOW=64
- Removed: CONFIG_X86_SMAP=y
- Removed: CONFIG_X86_SYSFB=y
- Removed: CONFIG_X86_THERMAL_VECTOR=y
- Removed: CONFIG_XEN_512GB=y
- Removed: CONFIG_XEN_BALLOON_MEMORY_HOTPLUG_LIMIT=512
- Removed: CONFIG_XEN_DOM0=y
- Removed: CONFIG_XIAOMI_WMI=m
- Removed: CONFIG_ZBUD=y
- Removed: CONFIG_ZONE_DMA32=y
- Removed: CONFIG_ZONE_DMA=y
- Removed: CONFIG_ZPOOL=y
- Removed: CONFIG_ZSMALLOC=y
- Removed: CONFIG_ZSTD_DECOMPRESS=m
- Removed: CONFIG_ZSWAP=y
- Removed: CONFIG_ZX_TDM=m
- Added: CONFIG_ACER_WIRELESS=m
- Added: CONFIG_ACER_WMI=m
- Added: CONFIG_ACPI_CMPC=m
- Added: CONFIG_ACPI_MDIO=y
- Added: CONFIG_ACPI_NUMA=y
- Added: CONFIG_ACPI_PCC=y
- Added: CONFIG_ACPI_PLATFORM_PROFILE=m
- Added: CONFIG_ACPI_PRMT=y
- Added: CONFIG_ACPI_TOSHIBA=m
- Added: CONFIG_ACPI_WMI=m
- Added: CONFIG_ADIN_PHY=m
- Added: CONFIG_AF_UNIX_OOB=y
- Added: CONFIG_AMD_HSMP=m
- Added: CONFIG_AMD_PMC=m
- Added: CONFIG_AMD_PMF=m
- Added: CONFIG_AMILO_RFKILL=m
- Added: CONFIG_APERTURE_HELPERS=y
- Added: CONFIG_APPLE_GMUX=m
- Added: CONFIG_APPLE_PROPERTIES=y
- Added: CONFIG_ARCH_CONFIGURES_CPU_MITIGATIONS=y
- Added: CONFIG_ARCH_CORRECT_STACKTRACE_ON_KRETPROBE=y
- Added: CONFIG_ARCH_ENABLE_HUGEPAGE_MIGRATION=y
- Added: CONFIG_ARCH_ENABLE_MEMORY_HOTPLUG=y
- Added: CONFIG_ARCH_ENABLE_MEMORY_HOTREMOVE=y
- Added: CONFIG_ARCH_ENABLE_SPLIT_PMD_PTLOCK=y
- Added: CONFIG_ARCH_ENABLE_THP_MIGRATION=y
- Added: CONFIG_ARCH_HAS_ADD_PAGES=y
- Added: CONFIG_ARCH_HAS_CACHE_LINE_SIZE=y
- Added: CONFIG_ARCH_HAS_COPY_MC=y
- Added: CONFIG_ARCH_HAS_CURRENT_STACK_POINTER=y
- Added: CONFIG_ARCH_HAS_DEBUG_VM_PGTABLE=y
- Added: CONFIG_ARCH_HAS_DEBUG_WX=y
- Added: CONFIG_ARCH_HAS_DEVMEM_IS_ALLOWED=y
- Added: CONFIG_ARCH_HAS_EARLY_DEBUG=y
- Added: CONFIG_ARCH_HAS_ELFCORE_COMPAT=y
- Added: CONFIG_ARCH_HAS_KCOV=y
- Added: CONFIG_ARCH_HAS_NONLEAF_PMD_YOUNG=y
- Added: CONFIG_ARCH_HAS_NON_OVERLAPPING_ADDRESS_SPACE=y
- Added: CONFIG_ARCH_HAS_PARANOID_L1D_FLUSH=y
- Added: CONFIG_ARCH_HAS_UBSAN_SANITIZE_ALL=y
- Added: CONFIG_ARCH_HAS_ZONE_DMA_SET=y
- Added: CONFIG_ARCH_MHP_MEMMAP_ON_MEMORY_ENABLE=y
- Added: CONFIG_ARCH_NR_GPIO=1024
- Added: CONFIG_ARCH_SUPPORTS_CFI_CLANG=y
- Added: CONFIG_ARCH_SUPPORTS_DEBUG_PAGEALLOC=y
- Added: CONFIG_ARCH_SUPPORTS_LTO_CLANG_THIN=y
- Added: CONFIG_ARCH_SUPPORTS_LTO_CLANG=y
- Added: CONFIG_ARCH_SUPPORTS_PAGE_TABLE_CHECK=y
- Added: CONFIG_ARCH_USE_MEMTEST=y
- Added: CONFIG_ARCH_USE_SYM_ANNOTATIONS=y
- Added: CONFIG_ARCH_WANT_DEFAULT_BPF_JIT=y
- Added: CONFIG_ARCH_WANT_GENERAL_HUGETLB=y
- Added: CONFIG_ARCH_WANT_HUGETLB_PAGE_OPTIMIZE_VMEMMAP=y
- Added: CONFIG_ARCH_WANT_LD_ORPHAN_WARN=y
- Added: CONFIG_ARCH_WANTS_NO_INSTR=y
- Added: CONFIG_ARCH_WANTS_THP_SWAP=y
- Added: CONFIG_AS_AVX512=y
- Added: CONFIG_AS_HAS_NON_CONST_LEB128=y
- Added: CONFIG_AS_IS_GNU=y
- Added: CONFIG_ASN1_ENCODER=y
- Added: CONFIG_AS_SHA1_NI=y
- Added: CONFIG_AS_SHA256_NI=y
- Added: CONFIG_AS_TPAUSE=y
- Added: CONFIG_ASUS_NB_WMI=m
- Added: CONFIG_ASUS_WIRELESS=m
- Added: CONFIG_ASUS_WMI=m
- Added: CONFIG_AS_VERSION=23200
- Added: CONFIG_AT803X_PHY=m
- Added: CONFIG_ATA_FORCE=y
- Added: CONFIG_AUXILIARY_BUS=y
- Added: CONFIG_BCM_NET_PHYPTP=m
- Added: CONFIG_BLK_CGROUP_RWSTAT=y
- Added: CONFIG_BLK_DEV_BSG_COMMON=y
- Added: CONFIG_BLK_DEV_BSG=y
- Added: CONFIG_BLK_DEV_INTEGRITY_T10=m
- Added: CONFIG_BLK_ICQ=y
- Added: CONFIG_BLK_MQ_STACKING=y
- Added: CONFIG_BLK_WBT_MQ=y
- Added: CONFIG_BLOCK_HOLDER_DEPRECATED=y
- Added: CONFIG_BLOCK_LEGACY_AUTOLOAD=y
- Added: CONFIG_BNA=m
- Added: CONFIG_BOOT_VESA_SUPPORT=y
- Added: CONFIG_BPF_JIT_DEFAULT_ON=y
- Added: CONFIG_BPF_JIT=y
- Added: CONFIG_BPF_LSM=y
- Added: CONFIG_BPF_SYSCALL=y
- Added: CONFIG_BPF_UNPRIV_DEFAULT_OFF=y
- Added: CONFIG_BPF=y
- Added: CONFIG_BRCMSMAC_LEDS=y
- Added: CONFIG_BROADCOM_PHY=m
- Added: CONFIG_BT_MTK=m
- Added: CONFIG_BUG_ON_DATA_CORRUPTION=y
- Added: CONFIG_BUILDTIME_MCOUNT_SORT=y
- Added: CONFIG_BUILDTIME_TABLE_SORT=y
- Added: CONFIG_CAN_8DEV_USB=m
- Added: CONFIG_CAN_CALC_BITTIMING=y
- Added: CONFIG_CAN_CC770_ISA=m
- Added: CONFIG_CAN_CC770=m
- Added: CONFIG_CAN_CC770_PLATFORM=m
- Added: CONFIG_CAN_C_CAN=m
- Added: CONFIG_CAN_C_CAN_PCI=m
- Added: CONFIG_CAN_C_CAN_PLATFORM=m
- Added: CONFIG_CAN_DEV=m
- Added: CONFIG_CAN_EMS_PCI=m
- Added: CONFIG_CAN_EMS_PCMCIA=m
- Added: CONFIG_CAN_EMS_USB=m
- Added: CONFIG_CAN_F81601=m
- Added: CONFIG_CAN_GS_USB=m
- Added: CONFIG_CAN_HI311X=m
- Added: CONFIG_CAN_IFI_CANFD=m
- Added: CONFIG_CAN_JANZ_ICAN3=m
- Added: CONFIG_CAN_KVASER_PCIEFD=m
- Added: CONFIG_CAN_KVASER_PCI=m
- Added: CONFIG_CAN_KVASER_USB=m
- Added: CONFIG_CAN_M_CAN=m
- Added: CONFIG_CAN_M_CAN_PLATFORM=m
- Added: CONFIG_CAN_M_CAN_TCAN4X5X=m
- Added: CONFIG_CAN_MCBA_USB=m
- Added: CONFIG_CAN_MCP251X=m
- Added: CONFIG_CAN_NETLINK=y
- Added: CONFIG_CAN_PEAK_PCIEC=y
- Added: CONFIG_CAN_PEAK_PCIEFD=m
- Added: CONFIG_CAN_PEAK_PCI=m
- Added: CONFIG_CAN_PEAK_PCMCIA=m
- Added: CONFIG_CAN_PEAK_USB=m
- Added: CONFIG_CAN_PLX_PCI=m
- Added: CONFIG_CAN_RX_OFFLOAD=y
- Added: CONFIG_CAN_SJA1000_ISA=m
- Added: CONFIG_CAN_SJA1000=m
- Added: CONFIG_CAN_SJA1000_PLATFORM=m
- Added: CONFIG_CAN_SLCAN=m
- Added: CONFIG_CAN_SOFTING_CS=m
- Added: CONFIG_CAN_SOFTING=m
- Added: CONFIG_CAN_UCAN=m
- Added: CONFIG_CAN_VCAN=m
- Added: CONFIG_CAN_VXCAN=m
- Added: CONFIG_CC_HAS_IBT=y
- Added: CONFIG_CC_HAS_INT128=y
- Added: CONFIG_CC_HAS_NO_PROFILE_FN_ATTR=y
- Added: CONFIG_CC_HAS_RETURN_THUNK=y
- Added: CONFIG_CC_HAS_SANCOV_TRACE_PC=y
- Added: CONFIG_CC_HAS_WORKING_NOSANITIZE_ADDRESS=y
- Added: CONFIG_CC_IMPLICIT_FALLTHROUGH="-Wimplicit-fallthrough=5"
- Added: CONFIG_CC_VERSION_TEXT="gcc (GCC) 9.3.1 20200408 (Red Hat 9.3.1-2)"
- Added: CONFIG_CEC_CORE=m
- Added: CONFIG_CEC_NOTIFIER=y
- Added: CONFIG_CHELSIO_INLINE_CRYPTO=y
- Added: CONFIG_CHELSIO_IPSEC_INLINE=m
- Added: CONFIG_CHROMEOS_LAPTOP=m
- Added: CONFIG_CHROMEOS_PSTORE=m
- Added: CONFIG_CHROMEOS_TBMC=m
- Added: CONFIG_CHROME_PLATFORMS=y
- Added: CONFIG_CLOCKSOURCE_WATCHDOG_MAX_SKEW_US=100
- Added: CONFIG_COMMON_CLK=y
- Added: CONFIG_COMPACT_UNEVICTABLE_DEFAULT=1
- Added: CONFIG_COMPAL_LAPTOP=m
- Added: CONFIG_CONTEXT_TRACKING_IDLE=y
- Added: CONFIG_CONTEXT_TRACKING_USER=y
- Added: CONFIG_CONTEXT_TRACKING=y
- Added: CONFIG_CPU_FREQ_DEFAULT_GOV_SCHEDUTIL=y
- Added: CONFIG_CPU_IBPB_ENTRY=y
- Added: CONFIG_CPU_IBRS_ENTRY=y
- Added: CONFIG_CPU_MITIGATIONS=y
- Added: CONFIG_CPU_SRSO=y
- Added: CONFIG_CPU_UNRET_ENTRY=y
- Added: CONFIG_CRC64_ROCKSOFT=m
- Added: CONFIG_CROS_KBD_LED_BACKLIGHT=m
- Added: CONFIG_CRYPTO_ADIANTUM=m
- Added: CONFIG_CRYPTO_AEGIS128_AESNI_SSE2=m
- Added: CONFIG_CRYPTO_AEGIS128=m
- Added: CONFIG_CRYPTO_AES_NI_INTEL=m
- Added: CONFIG_CRYPTO_AES_TI=m
- Added: CONFIG_CRYPTO_AES=y
- Added: CONFIG_CRYPTO_ANUBIS=m
- Added: CONFIG_CRYPTO_ARC4=m
- Added: CONFIG_CRYPTO_ARCH_HAVE_LIB_CHACHA=m
- Added: CONFIG_CRYPTO_ARCH_HAVE_LIB_POLY1305=m
- Added: CONFIG_CRYPTO_BLAKE2B=m
- Added: CONFIG_CRYPTO_BLOWFISH_COMMON=m
- Added: CONFIG_CRYPTO_BLOWFISH=m
- Added: CONFIG_CRYPTO_BLOWFISH_X86_64=m
- Added: CONFIG_CRYPTO_CAMELLIA_AESNI_AVX2_X86_64=m
- Added: CONFIG_CRYPTO_CAMELLIA_AESNI_AVX_X86_64=m
- Added: CONFIG_CRYPTO_CAMELLIA=m
- Added: CONFIG_CRYPTO_CAMELLIA_X86_64=m
- Added: CONFIG_CRYPTO_CAST5_AVX_X86_64=m
- Added: CONFIG_CRYPTO_CAST5=m
- Added: CONFIG_CRYPTO_CAST6_AVX_X86_64=m
- Added: CONFIG_CRYPTO_CAST6=m
- Added: CONFIG_CRYPTO_CAST_COMMON=m
- Added: CONFIG_CRYPTO_CCM=m
- Added: CONFIG_CRYPTO_CHACHA20=m
- Added: CONFIG_CRYPTO_CHACHA20POLY1305=m
- Added: CONFIG_CRYPTO_CHACHA20_X86_64=m
- Added: CONFIG_CRYPTO_CMAC=m
- Added: CONFIG_CRYPTO_CRC32C_INTEL=m
- Added: CONFIG_CRYPTO_CRC32C=y
- Added: CONFIG_CRYPTO_CRC32=m
- Added: CONFIG_CRYPTO_CRC32_PCLMUL=m
- Added: CONFIG_CRYPTO_CRC64_ROCKSOFT=m
- Added: CONFIG_CRYPTO_CRCT10DIF_PCLMUL=m
- Added: CONFIG_CRYPTO_CRCT10DIF=y
- Added: CONFIG_CRYPTO_DES3_EDE_X86_64=m
- Added: CONFIG_CRYPTO_DES=m
- Added: CONFIG_CRYPTO_ECHAINIV=m
- Added: CONFIG_CRYPTO_ESSIV=m
- Added: CONFIG_CRYPTO_FCRYPT=m
- Added: CONFIG_CRYPTO_FIPS_NAME="Linux Kernel Cryptographic API"
- Added: CONFIG_CRYPTO_GCM=y
- Added: CONFIG_CRYPTO_GHASH_CLMUL_NI_INTEL=m
- Added: CONFIG_CRYPTO_HMAC=y
- Added: CONFIG_CRYPTO_KEYWRAP=m
- Added: CONFIG_CRYPTO_KHAZAD=m
- Added: CONFIG_CRYPTO_LIB_AES=y
- Added: CONFIG_CRYPTO_LIB_ARC4=m
- Added: CONFIG_CRYPTO_LIB_BLAKE2S_GENERIC=y
- Added: CONFIG_CRYPTO_LIB_CHACHA_GENERIC=m
- Added: CONFIG_CRYPTO_LIB_DES=m
- Added: CONFIG_CRYPTO_LIB_POLY1305_GENERIC=m
- Added: CONFIG_CRYPTO_LIB_POLY1305_RSIZE=11
- Added: CONFIG_CRYPTO_LIB_SHA1=y
- Added: CONFIG_CRYPTO_LIB_SHA256=y
- Added: CONFIG_CRYPTO_LIB_UTILS=y
- Added: CONFIG_CRYPTO_NHPOLY1305_AVX2=m
- Added: CONFIG_CRYPTO_NHPOLY1305_SSE2=m
- Added: CONFIG_CRYPTO_POLY1305=m
- Added: CONFIG_CRYPTO_POLY1305_X86_64=m
- Added: CONFIG_CRYPTO_SEED=m
- Added: CONFIG_CRYPTO_SEQIV=y
- Added: CONFIG_CRYPTO_SERPENT_AVX2_X86_64=m
- Added: CONFIG_CRYPTO_SERPENT_AVX_X86_64=m
- Added: CONFIG_CRYPTO_SERPENT=m
- Added: CONFIG_CRYPTO_SERPENT_SSE2_X86_64=m
- Added: CONFIG_CRYPTO_SHA1_SSSE3=m
- Added: CONFIG_CRYPTO_SHA256_SSSE3=m
- Added: CONFIG_CRYPTO_SHA512_SSSE3=m
- Added: CONFIG_CRYPTO_SKCIPHER2=y
- Added: CONFIG_CRYPTO_SKCIPHER=y
- Added: CONFIG_CRYPTO_TEA=m
- Added: CONFIG_CRYPTO_TWOFISH_AVX_X86_64=m
- Added: CONFIG_CRYPTO_TWOFISH_COMMON=m
- Added: CONFIG_CRYPTO_TWOFISH=m
- Added: CONFIG_CRYPTO_TWOFISH_X86_64_3WAY=m
- Added: CONFIG_CRYPTO_TWOFISH_X86_64=m
- Added: CONFIG_CRYPTO_USER_API_ENABLE_OBSOLETE=y
- Added: CONFIG_CRYPTO_VMAC=m
- Added: CONFIG_CRYPTO_XCBC=m
- Added: CONFIG_CRYPTO_XXHASH=m
- Added: CONFIG_CX_ECAT=m
- Added: CONFIG_CYPRESS_FIRMWARE=m
- Added: CONFIG_DEBUG_BOOT_PARAMS=y
- Added: CONFIG_DEBUG_BUGVERBOSE=y
- Added: CONFIG_DEBUG_FS_ALLOW_ALL=y
- Added: CONFIG_DEBUG_FS=y
- Added: CONFIG_DEBUG_INFO_DWARF5=y
- Added: CONFIG_DEBUG_KERNEL=y
- Added: CONFIG_DEBUG_MISC=y
- Added: CONFIG_DECOMPRESS_ZSTD=y
- Added: CONFIG_DEFAULT_INIT=""
- Added: CONFIG_DEVICE_MIGRATION=y
- Added: CONFIG_DEVMEM=y
- Added: CONFIG_DEVPORT=y
- Added: CONFIG_DMA_OPS=y
- Added: CONFIG_DM_AUDIT=y
- Added: CONFIG_DMIID=y
- Added: CONFIG_DMI_SCAN_MACHINE_NON_EFI_FALLBACK=y
- Added: CONFIG_DMI_SYSFS=y
- Added: CONFIG_DP83822_PHY=m
- Added: CONFIG_DP83848_PHY=m
- Added: CONFIG_DP83867_PHY=m
- Added: CONFIG_DP83TC811_PHY=m
- Added: CONFIG_DRM_AMD_DC_DCN=y
- Added: CONFIG_DRM_BOCHS=m
- Added: CONFIG_DRM_BUDDY=m
- Added: CONFIG_DRM_CIRRUS_QEMU=m
- Added: CONFIG_DRM_DISPLAY_DP_HELPER=y
- Added: CONFIG_DRM_DISPLAY_HDCP_HELPER=y
- Added: CONFIG_DRM_DISPLAY_HDMI_HELPER=y
- Added: CONFIG_DRM_DISPLAY_HELPER=m
- Added: CONFIG_DRM_DP_AUX_CHARDEV=y
- Added: CONFIG_DRM_GEM_DMA_HELPER=m
- Added: CONFIG_DRM_GEM_SHMEM_HELPER=m
- Added: CONFIG_DRM_I915_FENCE_TIMEOUT=10000
- Added: CONFIG_DRM_I915_HEARTBEAT_INTERVAL=2500
- Added: CONFIG_DRM_I915_MAX_REQUEST_BUSYWAIT=8000
- Added: CONFIG_DRM_I915_PREEMPT_TIMEOUT=640
- Added: CONFIG_DRM_I915_PXP=y
- Added: CONFIG_DRM_I915_REQUEST_TIMEOUT=20000
- Added: CONFIG_DRM_I915_STOP_TIMEOUT=100
- Added: CONFIG_DRM_I915_TIMESLICE_DURATION=1
- Added: CONFIG_DRM_NOMODESET=y
- Added: CONFIG_DRM_PRIVACY_SCREEN=y
- Added: CONFIG_DRM_TTM_HELPER=m
- Added: CONFIG_DVB_A8293=m
- Added: CONFIG_DVB_AF9013=m
- Added: CONFIG_DVB_AF9033=m
- Added: CONFIG_DVB_AS102_FE=m
- Added: CONFIG_DVB_AS102=m
- Added: CONFIG_DVB_ASCOT2E=m
- Added: CONFIG_DVB_ATBM8830=m
- Added: CONFIG_DVB_AU8522_DTV=m
- Added: CONFIG_DVB_AU8522=m
- Added: CONFIG_DVB_AU8522_V4L=m
- Added: CONFIG_DVB_B2C2_FLEXCOP=m
- Added: CONFIG_DVB_B2C2_FLEXCOP_USB=m
- Added: CONFIG_DVB_BT8XX=m
- Added: CONFIG_DVB_CORE=m
- Added: CONFIG_DVB_CX24116=m
- Added: CONFIG_DVB_CX24117=m
- Added: CONFIG_DVB_CX24120=m
- Added: CONFIG_DVB_CXD2820R=m
- Added: CONFIG_DVB_CXD2841ER=m
- Added: CONFIG_DVB_DDBRIDGE=m
- Added: CONFIG_DVB_DRX39XYJ=m
- Added: CONFIG_DVB_DRXD=m
- Added: CONFIG_DVB_DS3000=m
- Added: CONFIG_DVB_GP8PSK_FE=m
- Added: CONFIG_DVB_HELENE=m
- Added: CONFIG_DVB_HORUS3A=m
- Added: CONFIG_DVB_IX2505V=m
- Added: CONFIG_DVB_L64781=m
- Added: CONFIG_DVB_LG2160=m
- Added: CONFIG_DVB_LGDT330X=m
- Added: CONFIG_DVB_LNBH25=m
- Added: CONFIG_DVB_LNBP21=m
- Added: CONFIG_DVB_LNBP22=m
- Added: CONFIG_DVB_M88DS3103=m
- Added: CONFIG_DVB_MB86A16=m
- Added: CONFIG_DVB_MT352=m
- Added: CONFIG_DVB_MXL5XX=m
- Added: CONFIG_DVB_MXL692=m
- Added: CONFIG_DVB_NETUP_UNIDVB=m
- Added: CONFIG_DVB_NXT200X=m
- Added: CONFIG_DVB_NXT6000=m
- Added: CONFIG_DVB_OR51132=m
- Added: CONFIG_DVB_OR51211=m
- Added: CONFIG_DVB_PLUTO2=m
- Added: CONFIG_DVB_PT1=m
- Added: CONFIG_DVB_PT3=m
- Added: CONFIG_DVB_S921=m
- Added: CONFIG_DVB_SI2165=m
- Added: CONFIG_DVB_SI21XX=m
- Added: CONFIG_DVB_SP887X=m
- Added: CONFIG_DVB_STV0288=m
- Added: CONFIG_DVB_STV0297=m
- Added: CONFIG_DVB_STV0367=m
- Added: CONFIG_DVB_STV6110=m
- Added: CONFIG_DVB_TC90522=m
- Added: CONFIG_DVB_TDA10048=m
- Added: CONFIG_DVB_TDA1004X=m
- Added: CONFIG_DVB_TDA10071=m
- Added: CONFIG_DVB_TDA18271C2DD=m
- Added: CONFIG_DVB_TDA665x=m
- Added: CONFIG_DVB_TDA8083=m
- Added: CONFIG_DVB_TUA6100=m
- Added: CONFIG_DVB_TUNER_CX24113=m
- Added: CONFIG_DVB_TUNER_ITD1000=m
- Added: CONFIG_DVB_USB_A800=m
- Added: CONFIG_DVB_USB_AF9005=m
- Added: CONFIG_DVB_USB_AF9005_REMOTE=m
- Added: CONFIG_DVB_USB_AZ6027=m
- Added: CONFIG_DVB_USB_CINERGY_T2=m
- Added: CONFIG_DVB_USB_CXUSB=m
- Added: CONFIG_DVB_USB_DIB0700=m
- Added: CONFIG_DVB_USB_DIB3000MC=m
- Added: CONFIG_DVB_USB_DIBUSB_MB=m
- Added: CONFIG_DVB_USB_DIBUSB_MC=m
- Added: CONFIG_DVB_USB_DIGITV=m
- Added: CONFIG_DVB_USB_DTT200U=m
- Added: CONFIG_DVB_USB_DTV5100=m
- Added: CONFIG_DVB_USB_DVBSKY=m
- Added: CONFIG_DVB_USB_DW2102=m
- Added: CONFIG_DVB_USB_GP8PSK=m
- Added: CONFIG_DVB_USB=m
- Added: CONFIG_DVB_USB_M920X=m
- Added: CONFIG_DVB_USB_NOVA_T_USB2=m
- Added: CONFIG_DVB_USB_OPERA1=m
- Added: CONFIG_DVB_USB_PCTV452E=m
- Added: CONFIG_DVB_USB_TECHNISAT_USB2=m
- Added: CONFIG_DVB_USB_TTUSB2=m
- Added: CONFIG_DVB_USB_UMT_010=m
- Added: CONFIG_DVB_USB_VP702X=m
- Added: CONFIG_DVB_USB_VP7045=m
- Added: CONFIG_DVB_VES1820=m
- Added: CONFIG_DVB_VES1X93=m
- Added: CONFIG_DVB_ZL10036=m
- Added: CONFIG_DVB_ZL10039=m
- Added: CONFIG_DVB_ZL10353=m
- Added: CONFIG_DWMAC_INTEL=m
- Added: CONFIG_DYNAMIC_DEBUG_CORE=y
- Added: CONFIG_DYNAMIC_FTRACE_WITH_ARGS=y
- Added: CONFIG_DYNAMIC_FTRACE_WITH_DIRECT_CALLS=y
- Added: CONFIG_DYNAMIC_FTRACE_WITH_REGS=y
- Added: CONFIG_DYNAMIC_FTRACE=y
- Added: CONFIG_DYNAMIC_SIGFRAME=y
- Added: CONFIG_EARLY_PRINTK_DBGP=y
- Added: CONFIG_EARLY_PRINTK_USB=y
- Added: CONFIG_EARLY_PRINTK=y
- Added: CONFIG_EDD=m
- Added: CONFIG_EEEPC_LAPTOP=m
- Added: CONFIG_EEEPC_WMI=m
- Added: CONFIG_EFI_CUSTOM_SSDT_OVERLAYS=y
- Added: CONFIG_EFI_DEV_PATH_PARSER=y
- Added: CONFIG_EFI_DXE_MEM_ATTRIBUTES=y
- Added: CONFIG_EFI_EARLYCON=y
- Added: CONFIG_EFI_ESRT=y
- Added: CONFIG_EFI_GENERIC_STUB_INITRD_CMDLINE_LOADER=y
- Added: CONFIG_EFI_HANDOVER_PROTOCOL=y
- Added: CONFIG_EFI_RUNTIME_MAP=y
- Added: CONFIG_EFI_RUNTIME_WRAPPERS=y
- Added: CONFIG_EFI_VARS_PSTORE_DEFAULT_DISABLE=y
- Added: CONFIG_EFI_VARS_PSTORE=y
- Added: CONFIG_ETHTOOL_NETLINK=y
- Added: CONFIG_EXCLUSIVE_SYSTEM_RAM=y
- Added: CONFIG_EXFAT_DEFAULT_IOCHARSET="utf8"
- Added: CONFIG_EXFAT_FS=m
- Added: CONFIG_F2FS_IOSTAT=y
- Added: CONFIG_FIRMWARE_MEMMAP=y
- Added: CONFIG_FIXED_PHY=y
- Added: CONFIG_FTRACE_MCOUNT_USE_CC=y
- Added: CONFIG_FUNCTION_ERROR_INJECTION=y
- Added: CONFIG_FUNCTION_PROFILER=y
- Added: CONFIG_FUSE_DAX=y
- Added: CONFIG_FW_CACHE=y
- Added: CONFIG_FW_CFG_SYSFS=m
- Added: CONFIG_FW_LOADER_SYSFS=y
- Added: CONFIG_FWNODE_MDIO=y
- Added: CONFIG_GCC10_NO_ARRAY_BOUNDS=y
- Added: CONFIG_GDB_SCRIPTS=y
- Added: CONFIG_GENERIC_ENTRY=y
- Added: CONFIG_GENERIC_PTDUMP=y
- Added: CONFIG_GENERIC_VDSO_TIME_NS=y
- Added: CONFIG_GPIO_CDEV_V1=y
- Added: CONFIG_GPIO_CDEV=y
- Added: CONFIG_GUEST_PERF_EVENTS=y
- Added: CONFIG_HARDIRQS_SW_RESEND=y
- Added: CONFIG_HAVE_ARCH_HUGE_VMALLOC=y
- Added: CONFIG_HAVE_ARCH_KASAN_VMALLOC=y
- Added: CONFIG_HAVE_ARCH_KCSAN=y
- Added: CONFIG_HAVE_ARCH_KFENCE=y
- Added: CONFIG_HAVE_ARCH_KGDB=y
- Added: CONFIG_HAVE_ARCH_KMSAN=y
- Added: CONFIG_HAVE_ARCH_RANDOMIZE_KSTACK_OFFSET=y
- Added: CONFIG_HAVE_ARCH_SECCOMP=y
- Added: CONFIG_HAVE_ARCH_USERFAULTFD_MINOR=y
- Added: CONFIG_HAVE_ARCH_USERFAULTFD_WP=y
- Added: CONFIG_HAVE_BUILDTIME_MCOUNT_SORT=y
- Added: CONFIG_HAVE_CLK_PREPARE=y
- Added: CONFIG_HAVE_CLK=y
- Added: CONFIG_HAVE_CONTEXT_TRACKING_USER_OFFSTACK=y
- Added: CONFIG_HAVE_CONTEXT_TRACKING_USER=y
- Added: CONFIG_HAVE_DYNAMIC_FTRACE_NO_PATCHABLE=y
- Added: CONFIG_HAVE_DYNAMIC_FTRACE_WITH_ARGS=y
- Added: CONFIG_HAVE_DYNAMIC_FTRACE_WITH_DIRECT_CALLS=y
- Added: CONFIG_HAVE_EBPF_JIT=y
- Added: CONFIG_HAVE_JUMP_LABEL_HACK=y
- Added: CONFIG_HAVE_KERNEL_ZSTD=y
- Added: CONFIG_HAVE_KVM_DIRTY_RING_ACQ_REL=y
- Added: CONFIG_HAVE_KVM_DIRTY_RING_TSO=y
- Added: CONFIG_HAVE_KVM_DIRTY_RING=y
- Added: CONFIG_HAVE_KVM_PFNCACHE=y
- Added: CONFIG_HAVE_KVM_PM_NOTIFIER=y
- Added: CONFIG_HAVE_MMIOTRACE_SUPPORT=y
- Added: CONFIG_HAVE_MOVE_PUD=y
- Added: CONFIG_HAVE_NOINSTR_HACK=y
- Added: CONFIG_HAVE_NOINSTR_VALIDATION=y
- Added: CONFIG_HAVE_OBJTOOL_MCOUNT=y
- Added: CONFIG_HAVE_OBJTOOL=y
- Added: CONFIG_HAVE_POSIX_CPU_TIMERS_TASK_WORK=y
- Added: CONFIG_HAVE_PREEMPT_DYNAMIC_CALL=y
- Added: CONFIG_HAVE_PREEMPT_DYNAMIC=y
- Added: CONFIG_HAVE_RETHOOK=y
- Added: CONFIG_HAVE_RUST=y
- Added: CONFIG_HAVE_SAMPLE_FTRACE_DIRECT_MULTI=y
- Added: CONFIG_HAVE_SAMPLE_FTRACE_DIRECT=y
- Added: CONFIG_HAVE_SETUP_PER_CPU_AREA=y
- Added: CONFIG_HAVE_SOFTIRQ_ON_OWN_STACK=y
- Added: CONFIG_HAVE_STATIC_CALL_INLINE=y
- Added: CONFIG_HAVE_STATIC_CALL=y
- Added: CONFIG_HAVE_UACCESS_VALIDATION=y
- Added: CONFIG_HIBERNATION_SNAPSHOT_DEV=y
- Added: CONFIG_HUAWEI_WMI=m
- Added: CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP=y
- Added: CONFIG_HVC_DRIVER=y
- Added: CONFIG_HVC_IRQ=y
- Added: CONFIG_HVC_XEN_FRONTEND=y
- Added: CONFIG_HVC_XEN=y
- Added: CONFIG_I2C_CCGX_UCSI=m
- Added: CONFIG_I2C_DESIGNWARE_PCI=m
- Added: CONFIG_I2C_DESIGNWARE_PLATFORM=m
- Added: CONFIG_IA32_FEAT_CTL=y
- Added: CONFIG_IBM_RTL=m
- Added: CONFIG_ICE_HWTS=y
- Added: CONFIG_IMA_MEASURE_ASYMMETRIC_KEYS=y
- Added: CONFIG_IMA_QUEUE_EARLY_BOOT_KEYS=y
- Added: CONFIG_INFINIBAND_BNXT_RE=m
- Added: CONFIG_INFINIBAND_MTHCA=m
- Added: CONFIG_INFINIBAND_OCRDMA=m
- Added: CONFIG_INFINIBAND_QIB_DCA=y
- Added: CONFIG_INFINIBAND_QIB=m
- Added: CONFIG_INFINIBAND_USNIC=m
- Added: CONFIG_INFINIBAND_VMWARE_PVRDMA=m
- Added: CONFIG_INITRAMFS_PRESERVE_MTIME=y
- Added: CONFIG_INPUT_VIVALDIFMAP=y
- Added: CONFIG_INTEL_ATOMISP2_PDX86=y
- Added: CONFIG_INTEL_HID_EVENT=m
- Added: CONFIG_INTEL_INT0002_VGPIO=m
- Added: CONFIG_INTEL_IOMMU_SCALABLE_MODE_DEFAULT_ON=y
- Added: CONFIG_INTEL_IPS=m
- Added: CONFIG_INTEL_MEI_GSC=m
- Added: CONFIG_INTEL_MEI_PXP=m
- Added: CONFIG_INTEL_MENLOW=m
- Added: CONFIG_INTEL_OAKTRAIL=m
- Added: CONFIG_INTEL_PMC_CORE=m
- Added: CONFIG_INTEL_PUNIT_IPC=m
- Added: CONFIG_INTEL_RST=m
- Added: CONFIG_INTEL_SMARTCONNECT=m
- Added: CONFIG_INTEL_VBTN=m
- Added: CONFIG_INTEL_WMI_THUNDERBOLT=m
- Added: CONFIG_INTEL_WMI=y
- Added: CONFIG_IOASID=y
- Added: CONFIG_IO_DELAY_0X80=y
- Added: CONFIG_IOMMU_DEFAULT_DMA_LAZY=y
- Added: CONFIG_IOMMU_DMA=y
- Added: CONFIG_IOMMU_IO_PGTABLE=y
- Added: CONFIG_IOMMU_SVA=y
- Added: CONFIG_IO_WQ=y
- Added: CONFIG_IR_FINTEK=m
- Added: CONFIG_IR_IGORPLUGUSB=m
- Added: CONFIG_IR_IGUANA=m
- Added: CONFIG_IR_IMON_DECODER=m
- Added: CONFIG_IR_JVC_DECODER=m
- Added: CONFIG_IR_MCE_KBD_DECODER=m
- Added: CONFIG_IR_MCEUSB=m
- Added: CONFIG_IRQ_MSI_IOMMU=y
- Added: CONFIG_IR_RCMM_DECODER=m
- Added: CONFIG_IR_SERIAL=m
- Added: CONFIG_IR_SERIAL_TRANSMITTER=y
- Added: CONFIG_IR_SONY_DECODER=m
- Added: CONFIG_IR_WINBOND_CIR=m
- Added: CONFIG_ISCSI_IBFT_FIND=y
- Added: CONFIG_ISCSI_IBFT=m
- Added: CONFIG_KCMP=y
- Added: CONFIG_KDB_CONTINUE_CATASTROPHIC=0
- Added: CONFIG_KDB_DEFAULT_ENABLE=0x1
- Added: CONFIG_KDB_KEYBOARD=y
- Added: CONFIG_KGDB_HONOUR_BLOCKLIST=y
- Added: CONFIG_KGDB_KDB=y
- Added: CONFIG_KGDB_LOW_LEVEL_TRAP=y
- Added: CONFIG_KGDB_SERIAL_CONSOLE=y
- Added: CONFIG_KGDB_TESTS=y
- Added: CONFIG_KGDB=y
- Added: CONFIG_KRETPROBE_ON_RETHOOK=y
- Added: CONFIG_KVM_WERROR=y
- Added: CONFIG_KVM_XFER_TO_GUEST_WORK=y
- Added: CONFIG_LD_IS_BFD=y
- Added: CONFIG_LD_ORPHAN_WARN=y
- Added: CONFIG_LD_VERSION=23200
- Added: CONFIG_LEDS_TPS6105X=m
- Added: CONFIG_LEGACY_VSYSCALL_XONLY=y
- Added: CONFIG_LG_LAPTOP=m
- Added: CONFIG_LINEAR_RANGES=y
- Added: CONFIG_LLD_VERSION=0
- Added: CONFIG_LOCK_MM_AND_FIND_VMA=y
- Added: CONFIG_LTO_NONE=y
- Added: CONFIG_LXT_PHY=m
- Added: CONFIG_MAGIC_SYSRQ_SERIAL_SEQUENCE=""
- Added: CONFIG_MAPPING_DIRTY_HELPERS=y
- Added: CONFIG_MDIO_BCM_UNIMAC=m
- Added: CONFIG_MDIO_BITBANG=m
- Added: CONFIG_MDIO_BUS=y
- Added: CONFIG_MDIO_CAVIUM=m
- Added: CONFIG_MDIO_DEVICE=y
- Added: CONFIG_MDIO_DEVRES=y
- Added: CONFIG_MDIO_GPIO=m
- Added: CONFIG_MDIO_I2C=m
- Added: CONFIG_MDIO_THUNDER=m
- Added: CONFIG_MEDIA_CEC_RC=y
- Added: CONFIG_MEDIA_CEC_SUPPORT=y
- Added: CONFIG_MEDIA_CONTROLLER_DVB=y
- Added: CONFIG_MEDIA_CONTROLLER=y
- Added: CONFIG_MEDIA_PLATFORM_DRIVERS=y
- Added: CONFIG_MEDIA_PLATFORM_SUPPORT=y
- Added: CONFIG_MEDIA_SUBDRV_AUTOSELECT=y
- Added: CONFIG_MEDIA_TEST_SUPPORT=y
- Added: CONFIG_MEDIA_TUNER_E4000=m
- Added: CONFIG_MEDIA_TUNER_FC0011=m
- Added: CONFIG_MEDIA_TUNER_FC0012=m
- Added: CONFIG_MEDIA_TUNER_FC0013=m
- Added: CONFIG_MEDIA_TUNER_FC2580=m
- Added: CONFIG_MEDIA_TUNER_IT913X=m
- Added: CONFIG_MEDIA_TUNER_M88RS6000T=m
- Added: CONFIG_MEDIA_TUNER_MAX2165=m
- Added: CONFIG_MEDIA_TUNER_MC44S803=m
- Added: CONFIG_MEDIA_TUNER_MT20XX=m
- Added: CONFIG_MEDIA_TUNER_MT2266=m
- Added: CONFIG_MEDIA_TUNER_MXL301RF=m
- Added: CONFIG_MEDIA_TUNER_QM1D1B0004=m
- Added: CONFIG_MEDIA_TUNER_QM1D1C0042=m
- Added: CONFIG_MEDIA_TUNER_QT1010=m
- Added: CONFIG_MEDIA_TUNER_R820T=m
- Added: CONFIG_MEDIA_TUNER_SI2157=m
- Added: CONFIG_MEDIA_TUNER_SIMPLE=m
- Added: CONFIG_MEDIA_TUNER_TDA18218=m
- Added: CONFIG_MEDIA_TUNER_TDA18250=m
- Added: CONFIG_MEDIA_TUNER_TDA18271=m
- Added: CONFIG_MEDIA_TUNER_TDA827X=m
- Added: CONFIG_MEDIA_TUNER_TDA8290=m
- Added: CONFIG_MEDIA_TUNER_TDA9887=m
- Added: CONFIG_MEDIA_TUNER_TEA5761=m
- Added: CONFIG_MEDIA_TUNER_TEA5767=m
- Added: CONFIG_MEDIA_TUNER_XC2028=m
- Added: CONFIG_MEDIA_TUNER_XC4000=m
- Added: CONFIG_MEDIA_TUNER_XC5000=m
- Added: CONFIG_MEMREGION=y
- Added: CONFIG_MHP_MEMMAP_ON_MEMORY=y
- Added: CONFIG_MITIGATION_ITS=y
- Added: CONFIG_MITIGATION_RFDS=y
- Added: CONFIG_MITIGATION_SPECTRE_BHI=y
- Added: CONFIG_MITIGATION_TSA=y
- Added: CONFIG_MITIGATION_VMSCAPE=y
- Added: CONFIG_MLX4_INFINIBAND=m
- Added: CONFIG_MLX5_INFINIBAND=m
- Added: CONFIG_MLX_PLATFORM=m
- Added: CONFIG_MMU_GATHER_MERGE_VMAS=y
- Added: CONFIG_MMU_GATHER_RCU_TABLE_FREE=y
- Added: CONFIG_MMU_GATHER_TABLE_FREE=y
- Added: CONFIG_MODPROBE_PATH="/sbin/modprobe"
- Added: CONFIG_MODULE_COMPRESS_NONE=y
- Added: CONFIG_MODULE_SIG_KEY_TYPE_RSA=y
- Added: CONFIG_MOXA_INTELLIO=m
- Added: CONFIG_MOXA_SMARTIO=m
- Added: CONFIG_MSI_LAPTOP=m
- Added: CONFIG_MSI_WMI=m
- Added: CONFIG_MT7615_COMMON=m
- Added: CONFIG_MT76_CONNAC_LIB=m
- Added: CONFIG_MTD_SPI_NOR_SWP_DISABLE_ON_VOLATILE=y
- Added: CONFIG_MXM_WMI=m
- Added: CONFIG_NEED_PER_CPU_EMBED_FIRST_CHUNK=y
- Added: CONFIG_NEED_PER_CPU_PAGE_FIRST_CHUNK=y
- Added: CONFIG_NET_9P_FD=m
- Added: CONFIG_NETFILTER_EGRESS=y
- Added: CONFIG_NETFILTER_SKIP_EGRESS=y
- Added: CONFIG_NETFILTER_XTABLES_COMPAT=y
- Added: CONFIG_NETFS_STATS=y
- Added: CONFIG_NETFS_SUPPORT=m
- Added: CONFIG_NET_SELFTESTS=y
- Added: CONFIG_NET_VENDOR_ADI=y
- Added: CONFIG_NET_VENDOR_ASIX=y
- Added: CONFIG_NET_VENDOR_BROCADE=y
- Added: CONFIG_NET_VENDOR_DAVICOM=y
- Added: CONFIG_NET_VENDOR_ENGLEDER=y
- Added: CONFIG_NET_VENDOR_FUNGIBLE=y
- Added: CONFIG_NET_VENDOR_LITEX=y
- Added: CONFIG_NET_VENDOR_MICROSOFT=y
- Added: CONFIG_NET_VENDOR_NI=y
- Added: CONFIG_NET_VENDOR_SILAN=y
- Added: CONFIG_NET_VENDOR_SIS=y
- Added: CONFIG_NET_VENDOR_VERTEXCOM=y
- Added: CONFIG_NET_VENDOR_WANGXUN=y
- Added: CONFIG_NF_LOG_SYSLOG=m
- Added: CONFIG_NFS_DISABLE_UDP_SUPPORT=y
- Added: CONFIG_NFS_V4_2_SSC_HELPER=y
- Added: CONFIG_N_GSM=m
- Added: CONFIG_N_HDLC=m
- Added: CONFIG_NI_XGE_MANAGEMENT_ENET=m
- Added: CONFIG_NOZOMI=m
- Added: CONFIG_NUMA_KEEP_MEMINFO=y
- Added: CONFIG_NVRAM=y
- Added: CONFIG_OBJTOOL=y
- Added: CONFIG_P2SB=y
- Added: CONFIG_PAGE_REPORTING=y
- Added: CONFIG_PAGE_SIZE_LESS_THAN_256KB=y
- Added: CONFIG_PAGE_SIZE_LESS_THAN_64KB=y
- Added: CONFIG_PAGE_TABLE_ISOLATION=y
- Added: CONFIG_PAHOLE_VERSION=19
- Added: CONFIG_PANASONIC_LAPTOP=m
- Added: CONFIG_PANIC_ON_OOPS_VALUE=1
- Added: CONFIG_PANIC_ON_OOPS=y
- Added: CONFIG_PANIC_TIMEOUT=0
- Added: CONFIG_PATA_TIMINGS=y
- Added: CONFIG_PCIE_BUS_DEFAULT=y
- Added: CONFIG_PCP_BATCH_SCALE_MAX=5
- Added: CONFIG_PCPU_DEV_REFCNT=y
- Added: CONFIG_PCS_ALTERA_TSE=m
- Added: CONFIG_PCS_XPCS=m
- Added: CONFIG_PEAQ_WMI=m
- Added: CONFIG_PERF_EVENTS_AMD_UNCORE=y
- Added: CONFIG_PINCTRL_INTEL=y
- Added: CONFIG_PINCTRL_MCP23S08_I2C=m
- Added: CONFIG_PINCTRL_MCP23S08_SPI=m
- Added: CONFIG_PLDMFW=y
- Added: CONFIG_POSIX_CPU_TIMERS_TASK_WORK=y
- Added: CONFIG_PREEMPT_BUILD=y
- Added: CONFIG_PREEMPT_COUNT=y
- Added: CONFIG_PREEMPT_DYNAMIC=y
- Added: CONFIG_PREEMPTION=y
- Added: CONFIG_PREEMPT_RCU=y
- Added: CONFIG_PSTORE_DEFAULT_KMSG_BYTES=10240
- Added: CONFIG_PTE_MARKER_UFFD_WP=y
- Added: CONFIG_PTE_MARKER=y
- Added: CONFIG_PTP_1588_CLOCK_OCP=m
- Added: CONFIG_PTP_1588_CLOCK_OPTIONAL=m
- Added: CONFIG_PVPANIC=y
- Added: CONFIG_RADIO_ADAPTERS=m
- Added: CONFIG_RADIO_MAXIRADIO=m
- Added: CONFIG_RADIO_SAA7706H=m
- Added: CONFIG_RADIO_SHARK2=m
- Added: CONFIG_RADIO_SHARK=m
- Added: CONFIG_RADIO_SI4713=m
- Added: CONFIG_RADIO_TEA5764=m
- Added: CONFIG_RADIO_TEF6862=m
- Added: CONFIG_RADIO_WL1273=m
- Added: CONFIG_RANDOMIZE_KSTACK_OFFSET=y
- Added: CONFIG_RANDSTRUCT_NONE=y
- Added: CONFIG_RC_ATI_REMOTE=m
- Added: CONFIG_RC_MAP=m
- Added: CONFIG_RCU_EXP_CPU_STALL_TIMEOUT=0
- Added: CONFIG_RD_ZSTD=y
- Added: CONFIG_RETHOOK=y
- Added: CONFIG_RETHUNK=y
- Added: CONFIG_RETPOLINE=y
- Added: CONFIG_RTC_DRV_RX6110=m
- Added: CONFIG_RTW88_8822BE=m
- Added: CONFIG_RTW88_8822B=m
- Added: CONFIG_RTW88_8822CE=m
- Added: CONFIG_RTW88_8822C=m
- Added: CONFIG_SAMSUNG_LAPTOP=m
- Added: CONFIG_SAMSUNG_Q10=m
- Added: CONFIG_SATA_HOST=y
- Added: CONFIG_SC92031=m
- Added: CONFIG_SCHED_CLUSTER=y
- Added: CONFIG_SCSI_COMMON=y
- Added: CONFIG_SCSI_MPI3MR=m
- Added: CONFIG_SCSI_UFSHCD=m
- Added: CONFIG_SCSI_UFSHCD_PCI=m
- Added: CONFIG_SECCOMP=y
- Added: CONFIG_SECRETMEM=y
- Added: CONFIG_SECURITY_LANDLOCK=y
- Added: CONFIG_SECURITY_SELINUX_SID2STR_CACHE_SIZE=256
- Added: CONFIG_SECURITY_SELINUX_SIDTAB_HASH_BITS=9
- Added: CONFIG_SENSORS_HDAPS=m
- Added: CONFIG_SENSORS_NCT6775_CORE=m
- Added: CONFIG_SERIAL_8250_PERICOM=y
- Added: CONFIG_SERIAL_NONSTANDARD=y
- Added: CONFIG_SFP=m
- Added: CONFIG_SIS190=m
- Added: CONFIG_SIS900=m
- Added: CONFIG_SLAB_MERGE_DEFAULT=y
- Added: CONFIG_SLUB_CPU_PARTIAL=y
- Added: CONFIG_SLUB_DEBUG=y
- Added: CONFIG_SLUB=y
- Added: CONFIG_SMBFS=m
- Added: CONFIG_SMS_SDIO_DRV=m
- Added: CONFIG_SMS_SIANO_MDTV=m
- Added: CONFIG_SMS_SIANO_RC=y
- Added: CONFIG_SMS_USB_DRV=m
- Added: CONFIG_SND_CTL_FAST_LOOKUP=y
- Added: CONFIG_SND_CTL_LED=m
- Added: CONFIG_SND_HDA_GENERIC_LEDS=y
- Added: CONFIG_SND_INTEL_DSP_CONFIG=m
- Added: CONFIG_SND_INTEL_NHLT=y
- Added: CONFIG_SND_INTEL_SOUNDWIRE_ACPI=m
- Added: CONFIG_SND_SOC_CS42L42_CORE=m
- Added: CONFIG_SND_SOC_FSL_UTILS=m
- Added: CONFIG_SND_SOC_INTEL_BXT_DA7219_MAX98357A_COMMON=m
- Added: CONFIG_SND_SOC_INTEL_HDA_DSP_COMMON=m
- Added: CONFIG_SND_SOC_MAX98373_I2C=m
- Added: CONFIG_SND_SOC_MAX98390=m
- Added: CONFIG_SND_SOC_RT5682_I2C=m
- Added: CONFIG_SND_SOC_RT5682S=m
- Added: CONFIG_SND_SOC_SOF_ACPI_DEV=m
- Added: CONFIG_SND_SOC_SOF_ALDERLAKE=m
- Added: CONFIG_SND_SOC_SOF_BROADWELL=m
- Added: CONFIG_SND_SOC_SOF_CLIENT=m
- Added: CONFIG_SND_SOC_SOF_COMETLAKE=m
- Added: CONFIG_SND_SOC_SOF_DEBUG_PROBES=m
- Added: CONFIG_SND_SOC_SOF_HDA_PROBES=m
- Added: CONFIG_SND_SOC_SOF_INTEL_APL=m
- Added: CONFIG_SND_SOC_SOF_INTEL_CNL=m
- Added: CONFIG_SND_SOC_SOF_INTEL_ICL=m
- Added: CONFIG_SND_SOC_SOF_INTEL_IPC4=y
- Added: CONFIG_SND_SOC_SOF_INTEL_MTL=m
- Added: CONFIG_SND_SOC_SOF_INTEL_SKL=m
- Added: CONFIG_SND_SOC_SOF_INTEL_SOUNDWIRE_LINK_BASELINE=m
- Added: CONFIG_SND_SOC_SOF_INTEL_SOUNDWIRE=m
- Added: CONFIG_SND_SOC_SOF_INTEL_TGL=m
- Added: CONFIG_SND_SOC_SOF_IPC3=y
- Added: CONFIG_SND_SOC_SOF_JASPERLAKE=m
- Added: CONFIG_SND_SOC_SOF_KABYLAKE=m
- Added: CONFIG_SND_SOC_SOF_METEORLAKE=m
- Added: CONFIG_SND_SOC_SOF_PCI_DEV=m
- Added: CONFIG_SND_SOC_SOF_SKYLAKE=m
- Added: CONFIG_SOCK_RX_QUEUE_MAPPING=y
- Added: CONFIG_SOFTIRQ_ON_OWN_STACK=y
- Added: CONFIG_SONY_LAPTOP=m
- Added: CONFIG_SONYPI_COMPAT=y
- Added: CONFIG_SOUNDWIRE_CADENCE=m
- Added: CONFIG_SOUNDWIRE_GENERIC_ALLOCATION=m
- Added: CONFIG_SOUNDWIRE_INTEL=m
- Added: CONFIG_SPI_ALTERA_CORE=m
- Added: CONFIG_STACKDEPOT=y
- Added: CONFIG_STACK_TRACER=y
- Added: CONFIG_STRICT_DEVMEM=y
- Added: CONFIG_SURFACE3_WMI=m
- Added: CONFIG_SURFACE_PLATFORMS=y
- Added: CONFIG_SURFACE_PRO3_BUTTON=m
- Added: CONFIG_SWAP=y
- Added: CONFIG_SYMBOLIC_ERRNAME=y
- Added: CONFIG_SYNCLINK_GT=m
- Added: CONFIG_SYSFB=y
- Added: CONFIG_SYSVIPC_COMPAT=y
- Added: CONFIG_TASKS_RCU_GENERIC=y
- Added: CONFIG_TASKS_RCU=y
- Added: CONFIG_TASKS_RUDE_RCU=y
- Added: CONFIG_TASKS_TRACE_RCU=y
- Added: CONFIG_TIME_NS=y
- Added: CONFIG_TOPSTAR_LAPTOP=m
- Added: CONFIG_TOSHIBA_BT_RFKILL=m
- Added: CONFIG_TOSHIBA_HAPS=m
- Added: CONFIG_TOSHIBA_WMI=m
- Added: CONFIG_TRACE_IRQFLAGS_NMI_SUPPORT=y
- Added: CONFIG_TRACE_IRQFLAGS_SUPPORT=y
- Added: CONFIG_TRUSTED_KEYS_TPM=y
- Added: CONFIG_TTPCI_EEPROM=m
- Added: CONFIG_UEFI_CPER_X86=y
- Added: CONFIG_UEFI_CPER=y
- Added: CONFIG_UNINLINE_SPIN_UNLOCK=y
- Added: CONFIG_UNWINDER_FRAME_POINTER=y
- Added: CONFIG_USB_CHIPIDEA_GENERIC=m
- Added: CONFIG_USB_CHIPIDEA_MSM=m
- Added: CONFIG_USB_CHIPIDEA_PCI=m
- Added: CONFIG_USB_DSBR=m
- Added: CONFIG_USB_GL860=m
- Added: CONFIG_USB_GSPCA_SPCA1528=m
- Added: CONFIG_USB_KEENE=m
- Added: CONFIG_USB_M5602=m
- Added: CONFIG_USB_MA901=m
- Added: CONFIG_USB_MR800=m
- Added: CONFIG_USB_PULSE8_CEC=m
- Added: CONFIG_USB_RAINSHADOW_CEC=m
- Added: CONFIG_USB_RAREMONO=m
- Added: CONFIG_USB_RTL8153_ECM=m
- Added: CONFIG_USB_STV06XX=m
- Added: CONFIG_USB_VIDEO_CLASS_INPUT_EVDEV=y
- Added: CONFIG_USB_VIDEO_CLASS=m
- Added: CONFIG_USE_PERCPU_NUMA_NODE_ID=y
- Added: CONFIG_USERFAULTFD=y
- Added: CONFIG_V4L2_ASYNC=m
- Added: CONFIG_VFIO=m
- Added: CONFIG_VFIO_PCI_CORE=m
- Added: CONFIG_VFIO_PCI=m
- Added: CONFIG_VGA_ARB_MAX_GPUS=64
- Added: CONFIG_VGA_ARB=y
- Added: CONFIG_VHOST_IOTLB=m
- Added: CONFIG_VHOST=m
- Added: CONFIG_VHOST_MENU=y
- Added: CONFIG_VHOST_NET=m
- Added: CONFIG_VHOST_SCSI=m
- Added: CONFIG_VHOST_VSOCK=m
- Added: CONFIG_VIDEO_BT848=m
- Added: CONFIG_VIDEO_CAMERA_SENSOR=y
- Added: CONFIG_VIDEO_CS3308=m
- Added: CONFIG_VIDEO_CS5345=m
- Added: CONFIG_VIDEO_CS53L32A=m
- Added: CONFIG_VIDEO_DT3155=m
- Added: CONFIG_VIDEO_GO7007_LOADER=m
- Added: CONFIG_VIDEO_GO7007=m
- Added: CONFIG_VIDEO_GO7007_USB=m
- Added: CONFIG_VIDEO_GO7007_USB_S2250_BOARD=m
- Added: CONFIG_VIDEO_HDPVR=m
- Added: CONFIG_VIDEO_HI556=m
- Added: CONFIG_VIDEO_M52790=m
- Added: CONFIG_VIDEO_MSP3400=m
- Added: CONFIG_VIDEO_MT9V011=m
- Added: CONFIG_VIDEO_OV2640=m
- Added: CONFIG_VIDEO_OV2740=m
- Added: CONFIG_VIDEO_OV7640=m
- Added: CONFIG_VIDEO_SAA7127=m
- Added: CONFIG_VIDEO_SONY_BTF_MPX=m
- Added: CONFIG_VIDEO_TDA1997X=m
- Added: CONFIG_VIDEO_TVAUDIO=m
- Added: CONFIG_VIDEO_V4L2_SUBDEV_API=y
- Added: CONFIG_VIDEO_WM8739=m
- Added: CONFIG_VIDEO_WM8775=m
- Added: CONFIG_VIRTIO_ANCHOR=y
- Added: CONFIG_VIRTIO_DMA_SHARED_BUFFER=m
- Added: CONFIG_VIRTIO_PCI_LIB_LEGACY=m
- Added: CONFIG_VIRTIO_PCI_LIB=m
- Added: CONFIG_VMAP_PFN=y
- Added: CONFIG_VM_EVENT_COUNTERS=y
- Added: CONFIG_VMGENID=y
- Added: CONFIG_VSOCKETS_LOOPBACK=m
- Added: CONFIG_WLAN_VENDOR_MICROCHIP=y
- Added: CONFIG_WLAN_VENDOR_PURELIFI=y
- Added: CONFIG_WLAN_VENDOR_SILABS=y
- Added: CONFIG_WMI_BMOF=m
- Added: CONFIG_X86_DECODER_SELFTEST=y
- Added: CONFIG_X86_IOPL_IOPERM=y
- Added: CONFIG_X86_THERMAL_VECTOR=y
- Added: CONFIG_X86_UMIP=y
- Added: CONFIG_X86_VMX_FEATURE_NAMES=y
- Added: CONFIG_XEN_512GB=y
- Added: CONFIG_XEN_DOM0=y
- Added: CONFIG_XEN_MEMORY_HOTPLUG_LIMIT=512
- Added: CONFIG_XEN_PCI_STUB=y
- Added: CONFIG_XEN_PV_DOM0=y
- Added: CONFIG_XEN_PVHVM_GUEST=y
- Added: CONFIG_XEN_PV_MSR_SAFE=y
- Added: CONFIG_XEN_UNPOPULATED_ALLOC=y
- Added: CONFIG_XFRM_AH=m
- Added: CONFIG_XFRM_ESP=m
- Added: CONFIG_XFS_SUPPORT_V4=y
- Added: CONFIG_XIAOMI_WMI=m
- Added: CONFIG_ZBUD=y
- Added: CONFIG_ZONE_DMA32=y
- Added: CONFIG_ZONE_DMA=y
- Added: CONFIG_ZPOOL=y
- Added: CONFIG_ZRAM_DEF_COMP="lzo-rle"
- Added: CONFIG_ZRAM_DEF_COMP_LZORLE=y
- Added: CONFIG_ZSMALLOC=y
- Added: CONFIG_ZSTD_COMMON=y
- Added: CONFIG_ZSTD_DECOMPRESS=y
- Added: CONFIG_ZSWAP_COMPRESSOR_DEFAULT="lzo"
- Added: CONFIG_ZSWAP_COMPRESSOR_DEFAULT_LZO=y
- Added: CONFIG_ZSWAP=y
- Added: CONFIG_ZSWAP_ZPOOL_DEFAULT="zbud"
- Added: CONFIG_ZSWAP_ZPOOL_DEFAULT_ZBUD=y

* Wed Dec 03 2025 S.Tindall <s10dal@elepo.org> - 5.4.302-1
- Updated with the 5.4.302 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.302]

* Wed Oct 29 2025 S.Tindall <s10dal@elepo.org> - 5.4.301-1
- Updated with the 5.4.301 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.301]

* Thu Oct 02 2025 S.Tindall <s10dal@elepo.org> - 5.4.300-1
- Updated with the 5.4.300 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.300]

* Tue Sep 09 2025 S.Tindall <s10dal@elepo.org> - 5.4.299-1
- Updated with the 5.4.299 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.299]

* Thu Sep 04 2025 S.Tindall <s10dal@elepo.org> - 5.4.298-1
- Updated with the 5.4.298 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.298]

* Thu Aug 28 2025 S.Tindall <s10dal@elepo.org> - 5.4.297-1
- Updated with the 5.4.297 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.297]

* Thu Jul 17 2025 S.Tindall <s10dal@elepo.org> - 5.4.296-1
- Updated with the 5.4.296 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.296]
- Added: CONFIG_MAC80211_HWSIM=m

* Fri Jun 27 2025 S.Tindall <s10dal@elepo.org> - 5.4.295-1
- Updated with the 5.4.295 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.295]
- Added: CONFIG_SURFACE_PLATFORMS=y

* Wed Jun 04 2025 S.Tindall <s10dal@elepo.org> - 5.4.294-1
- Updated with the 5.4.294 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.294]

* Fri May 02 2025 S.Tindall <s10dal@elepo.org> - 5.4.293-1
- Updated with the 5.4.293 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.293]

* Thu Apr 10 2025 S.Tindall <s10dal@elepo.org> - 5.4.292-1
- Updated with the 5.4.292 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.292]
- Removed: CONFIG_HAVE_EISA=y

* Thu Mar 13 2025 S.Tindall <s10dal@elepo.org> - 5.4.291
- Updated with the 5.4.291 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.291]
- Added: CONFIG_BUG_ON_DATA_CORRUPTION=y
- Added: CONFIG_MEMTEST=y

* Sat Feb 01 2025 S.Tindall <s10dal@elepo.org> - 5.4.290-1
- Updated with the 5.4.290 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.290]
- Added: CONFIG_PCIE_PTM=y

* Thu Jan 09 2025 S.Tindall <s10dal@elepo.org> - 5.4.289-1
- Updated with the 5.4.289 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.289]

* Thu Dec 19 2024 S.Tindall <s10dal@elepo.org> - 5.4.288-1
- Updated with the 5.4.288 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.288]

* Sat Dec 14 2024 S.Tindall <s10dal@elepo.org> - 5.4.287-1
- Updated with the 5.4.287 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.287]

* Sun Nov 17 2024 S.Tindall <s10dal@elepo.org> - 5.4.286-1
- Updated with the 5.4.286 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.286]

* Fri Nov 08 2024 S.Tindall <s10dal@elepo.org> - 5.4.285-1
- Updated with the 5.4.285 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.285]
- Added: CONFIG_PROC_MEM_ALWAYS_FORCE=y

* Thu Sep 12 2024 S.Tindall <s10dal@elepo.org> - 5.4.284-1
- Updated with the 5.4.284 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.284]

* Wed Sep 04 2024 S.Tindall <s10dal@elepo.org> - 5.4.283-1
- Updated with the 5.4.283 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.283]

* Mon Aug 19 2024 S.Tindall <s10dal@elepo.org> - 5.4.282-1
- Updated with the 5.4.282 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.282]
- Added: CONFIG_SPI_XILINX=m

* Sat Jul 27 2024 S.Tindall <s10dal@elepo.org> - 5.4.281-1
- Updated with the 5.4.281 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.281]
- Added: CONFIG_INTEL_MEI_HDCP=m
- Added: CONFIG_INTEL_MEI_TXE=m

* Thu Jul 18 2024 S.Tindall <s10dal@elepo.org> - 5.4.280-1
- Updated with the 5.4.280 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.280]

* Fri Jul 05 2024 S.Tindall <s10dal@elepo.org> - 5.4.279-1
- Updated with the 5.4.279 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.279]
- Added: CONFIG_UNICODE=y

* Sun Jun 16 2024 S.Tindall <s10dal@elepo.org> - 5.4.278-1
- Updated with the 5.4.278 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.278]
- Added: CONFIG_ARCH_WANT_FRAME_POINTERS=y

* Sun May 26 2024 S.Tindall <s10dal@elepo.org> - 5.4.277-1
- Updated with the 5.4.277 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.277]
- Removed: CONFIG_REALTEK_PHY=m
- Added: CONFIG_REALTEK_PHY=y

* Fri May 17 2024 S.Tindall <s10dal@elepo.org> - 5.4.276-1
- Updated with the 5.4.276 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.276]

* Thu May 02 2024 S.Tindall <s10dal@elepo.org> - 5.4.275-1
- Updated with the 5.4.275 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.275]

* Sat Apr 13 2024 S.Tindall <s10dal@elepo.org> - 5.4.274-1
- Updated with the 5.4.274 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.274]

* Wed Mar 27 2024 S.Tindall <s10dal@elepo.org> - 5.4.273-1
- Updated with the 5.4.273 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.273]

* Fri Mar 15 2024 S.Tindall <s10dal@elepo.org> - 5.4.272-1
- Updated with the 5.4.272 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.272]

* Wed Mar 06 2024 S.Tindall <s10dal@elepo.org> - 5.4.271-1
- Updated with the 5.4.271 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.271]

* Fri Mar 01 2024 Akemi Yagi <toracat@elrepo.org> - 5.4.270-1
- Updated with the 5.4.270 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.270]

* Fri Feb 23 2024 S.Tindall <s10dal@elepo.org> - 5.4.269-1
- Updated with the 5.4.269 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.269]
- Removed: CONFIG_MFD_TI_AM335X_TSCADC=m
- Removed: CONFIG_TOUCHSCREEN_TI_AM335X_TSC=m
- Added: CONFIG_NFS_V2=m

* Thu Jan 25 2024 S.Tindall <s10dal@elepo.org> - 5.4.268-1
- Updated with the 5.4.268 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.268]
- Added: CONFIG_SOUNDWIRE=m

* Tue Jan 16 2024 S.Tindall <s10dal@elepo.org> - 5.4.267-1
- Updated with the 5.4.267 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.267]

* Mon Jan 08 2024 S.Tindall <s10dal@elepo.org> - 5.4.266-1
- Updated with the 5.4.266 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.266]

* Wed Dec 20 2023 S.Tindall <s10dal@elepo.org> - 5.4.265-1
- Updated with the 5.4.265 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.265]

* Thu Dec 14 2023 S.Tindall <s10dal@elepo.org> - 5.4.264-1
- Updated with the 5.4.264 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.264]

* Fri Dec 08 2023 S.Tindall <s10dal@elepo.org> - 5.4.263-1
- Updated with the 5.4.263 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.263]

* Wed Nov 29 2023 S.Tindall <s10dal@elepo.org> - 5.4.262-1
- Updated with the 5.4.262 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.262]

* Mon Nov 20 2023 S.Tindall <s10dal@elepo.org> - 5.4.261-1
- Updated with the 5.4.261 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.261]

* Wed Nov 08 2023 S.Tindall <s10dal@elepo.org> - 5.4.260-1
- Updated with the 5.4.260 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.260]

* Wed Oct 25 2023 Akemi Yagi <toracat@elrepo.org> - 5.4.259-1
- Updated with the 5.4.259 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.259]

* Tue Oct 10 2023 S.Tindall <s10dal@elepo.org> - 5.4.258-1
- Updated with the 5.4.258 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.258]

* Sat Sep 23 2023 S.Tindall <s10dal@elepo.org> - 5.4.257-1
- Updated with the 5.4.257 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.257]

* Wed Aug 30 2023 S.Tindall <s10dal@elepo.org> - 5.4.255-1
- Updated with the 5.4.255 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.255]

* Wed Aug 16 2023 S.Tindall <s10dal@elepo.org> - 5.4.254-1
- Updated with the 5.4.254 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.254]

* Fri Aug 11 2023 S.Tindall <s10dal@elepo.org> - 5.4.253-1
- Updated with the 5.4.253 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.253]

* Tue Aug 08 2023 S.Tindall <s10dal@elepo.org> - 5.4.252-1
- Updated with the 5.4.252 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.252]
- Added: CONFIG_ARCH_HAS_CPU_FINALIZE_INIT=y

* Thu Jul 27 2023 S.Tindall <s10dal@elepo.org> - 5.4.251-1
- Updated with the 5.4.251 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.251]

* Mon Jul 24 2023 S.Tindall <s10dal@elepo.org> - 5.4.250-1
- Updated with the 5.4.250 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.250]

* Wed Jun 28 2023 S.Tindall <s10dal@elepo.org> - 5.4.249-1
- Updated with the 5.4.249 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.249]

* Wed Jun 21 2023 S.Tindall <s10dal@elepo.org> - 5.4.248-1
- Updated with the 5.4.248 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.248]

* Wed Jun 14 2023 S.Tindall <s10dal@elepo.org> - 5.4.247-1
- Updated with the 5.4.247 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.247]

* Fri Jun 09 2023 S.Tindall <s10dal@elepo.org> - 5.4.246-1
- Updated with the 5.4.246 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.246]

* Mon Jun 05 2023 S.Tindall <s10dal@elepo.org> - 5.4.245-1
- Updated with the 5.4.245 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.245]

* Tue May 30 2023 Alan Bartlett <ajb@elrepo.org> - 5.4.244-1
- Updated with the 5.4.244 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.244]
- CONFIG_SECURITY_YAMA=y [https://elrepo.org/bugs/view.php?id=1351]

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
- CONFIG_NTB_PERF=m [https://elrepo.org/bugs/view.php?id=1322]

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

* Thu Dec 08 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.226-1
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
- CONFIG_SND_SOC_SOF_HDA=m, CONFIG_SND_SOC_SOF_XTENSA=m and
- CONFIG_SND_SOC_HDAC_HDA=m
- [https://elrepo.org/bugs/view.php?id=1259]

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

* Sat Jul 02 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.203-1
- Updated with the 5.4.203 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.203]

* Wed Jun 29 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.202-1
- Updated with the 5.4.202 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.202]

* Sat Jun 25 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.201-1
- Updated with the 5.4.201 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.201]

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
- CONFIG_DRM_VBOXVIDEO=m [https://elrepo.org/bugs/view.php?id=1189]
- CONFIG_DRM_XEN=y and CONFIG_DRM_XEN_FRONTEND=m
- [https://elrepo.org/bugs/view.php?id=1191]

* Thu Jan 20 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.173-1
- Updated with the 5.4.173 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.173]

* Sun Jan 16 2022 Alan Bartlett <ajb@elrepo.org> - 5.4.172-1
- Updated with the 5.4.172 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.172]

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
- CONFIG_XDP_SOCKETS=y and CONFIG_XDP_SOCKETS_DIAG=m
- [https://elrepo.org/bugs/view.php?id=1147]

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
- CONFIG_BRIDGE_NETFILTER=m [https://elrepo.org/bugs/view.php?id=1135]

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
- CONFIG_HSA_AMD=y https://elrepo.org/bugs/view.php?id=1091]

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
- CONFIG_RANDOMIZE_BASE=y, CONFIG_X86_NEED_RELOCS=y,
- CONFIG_DYNAMIC_MEMORY_LAYOUT=y, CONFIG_RANDOMIZE_MEMORY=y
- and CONFIG_RANDOMIZE_MEMORY_PHYSICAL_PADDING=0xa
- [https://elrepo.org/bugs/view.php?id=1068]

* Sun Jan 17 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.90-1
- Updated with the 5.4.90 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.90]

* Wed Jan 13 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.89-1
- Updated with the 5.4.89 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.89]

* Sat Jan 09 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.88-1
- Updated with the 5.4.88 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.88]

* Wed Jan 06 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.87-1
- Updated with the 5.4.87 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.87]

* Fri Jan 01 2021 Alan Bartlett <ajb@elrepo.org> - 5.4.86-1
- Updated with the 5.4.86 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.86]

* Wed Dec 30 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.249-1
- Updated with the 4.4.249 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.249]

* Sat Dec 12 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.248-1
- Updated with the 4.4.248 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.248]

* Thu Dec 03 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.247-1
- Updated with the 4.4.247 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.247]

* Tue Nov 24 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.246-1
- Updated with the 4.4.246 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.246]

* Sun Nov 22 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.245-1
- Updated with the 4.4.245 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.245]

* Thu Nov 19 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.244-1
- Updated with the 4.4.244 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.244]

* Wed Nov 11 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.243-1
- Updated with the 4.4.243 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.243]

* Tue Nov 10 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.242-1
- Updated with the 4.4.242 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.242]

* Thu Oct 29 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.241-1
- Updated with the 4.4.241 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.241]

* Sun Oct 18 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.240-1
- Updated with the 4.4.240 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.240]

* Wed Oct 14 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.239-1
- Updated with the 4.4.239 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.239]

* Thu Oct 01 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.238-1
- Updated with the 4.4.238 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.238]

* Wed Sep 23 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.237-1
- Updated with the 4.4.237 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.237]

* Sat Sep 12 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.236-1
- Updated with the 4.4.236 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.236]

* Fri Sep 04 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.235-1
- Updated with the 4.4.235 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.235]

* Wed Aug 26 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.234-1
- Updated with the 4.4.234 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.234]

* Sat Aug 22 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.233-1
- Updated with the 4.4.233 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.233]

* Fri Jul 31 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.232-1
- Updated with the 4.4.232 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.232]

* Wed Jul 22 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.231-1
- Updated with the 4.4.231 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.231]
 - CONFIG_USBIP_CORE=m, CONFIG_USBIP_VHCI_HCD=m and CONFIG_USBIP_HOST=m
- [https://elrepo.org/bugs/view.php?id=1019]
- Enhanced the specification file to allow the kernel-lt
- package set to be built, using an updated gcc version from
- the Red Hat devtoolset-9 package, following an upstream
- increase in the minimum gcc version requirement.
- [https://elrepo.org/bugs/view.php?id=1023]

* Wed Jul 08 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.230-1
- Updated with the 4.4.230 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.230]

* Wed Jul 01 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.229-1
- Updated with the 4.4.229 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.229]
- Added a triggerin scriptlet to rebuild the initramfs image
- when the system microcode package is updated.
- [https://elrepo.org/bugs/view.php?id=1012]

* Sun Jun 21 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.228-1
- Updated with the 4.4.228 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.228]

* Thu Jun 11 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.227-1
- Updated with the 4.4.227 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.227]

* Wed Jun 03 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.226-1
- Updated with the 4.4.226 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.226]

* Wed May 27 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.225-1
- Updated with the 4.4.225 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.225]

* Wed May 20 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.224-1
- Updated with the 4.4.224 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.224]

* Sun May 10 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.223-1
- Updated with the 4.4.223 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.223]

* Wed May 06 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.222-1
- Updated with the 4.4.222 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.222]

* Sat May 02 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.221-1
- Updated with the 4.4.221 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.221]

* Fri Apr 24 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.220-1
- Updated with the 4.4.220 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.220]
- CONFIG_SND_SOC_FSL_ASRC=m, CONFIG_SND_SOC_FSL_SAI=m,
- CONFIG_SND_SOC_FSL_SSI=m, CONFIG_SND_SOC_FSL_SPDIF=m,
- CONFIG_SND_SOC_FSL_ESAI=m and CONFIG_SND_SOC_IMX_AUDMUX=m

* Sun Apr 12 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.219-1
- Updated with the 4.4.219 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.219]

* Thu Apr 02 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.218-1
- Updated with the 4.4.218 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.218]

* Sat Mar 21 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.217-1
- Updated with the 4.4.217 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.217]

* Wed Mar 11 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.216-1
- Updated with the 4.4.216 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.216]

* Fri Feb 28 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.215-1
- Updated with the 4.4.215 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.215]

* Fri Feb 14 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.214-1
- Updated with the 4.4.214 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.214]

* Wed Feb 05 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.213-1
- Updated with the 4.4.213 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.213]

* Wed Jan 29 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.212-1
- Updated with the 4.4.212 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.212]

* Thu Jan 23 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.211-1
- Updated with the 4.4.211 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.211]

* Tue Jan 14 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.210-1
- Updated with the 4.4.210 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.210]

* Sun Jan 12 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.209-1
- Updated with the 4.4.209 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.209]

* Sat Jan 04 2020 Alan Bartlett <ajb@elrepo.org> - 4.4.208-1
- Updated with the 4.4.208 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.208]
- Apply a patch to allow the perf & python-perf packages to be built.

* Sat Dec 21 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.207-1
- Updated with the 4.4.207 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.207]

* Thu Dec 05 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.206-1
- Updated with the 4.4.206 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.206]

* Fri Nov 29 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.205-1
- Updated with the 4.4.205 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.205]

* Thu Nov 28 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.204-1
- Updated with the 4.4.204 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.204]

* Mon Nov 25 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.203-1
- Updated with the 4.4.203 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.203]

* Sat Nov 16 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.202-1
- Updated with the 4.4.202 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.202]
- CONFIG_X86_INTEL_TSX_MODE_OFF=y

* Tue Nov 12 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.201-1
- Updated with the 4.4.201 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.201]

* Sun Nov 10 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.200-1
- Updated with the 4.4.200 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.200]

* Wed Nov 06 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.199-1
- Updated with the 4.4.199 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.199]

* Tue Oct 29 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.198-1
- Updated with the 4.4.198 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.198]

* Thu Oct 17 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.197-1
- Updated with the 4.4.197 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.197]

* Mon Oct 07 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.196-1
- Updated with the 4.4.196 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.196]

* Sat Oct 05 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.195-1
- Updated with the 4.4.195 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.195]

* Sat Sep 21 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.194-1
- Updated with the 4.4.194 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.194]

* Mon Sep 16 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.193-1
- Updated with the 4.4.193 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.193]

* Tue Sep 10 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.192-1
- Updated with the 4.4.192 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.192]

* Fri Sep 06 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.191-1
- Updated with the 4.4.191 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.191]

* Sun Aug 25 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.190-1
- Updated with the 4.4.190 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.190]

* Sun Aug 11 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.189-1
- Updated with the 4.4.189 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.189]

* Tue Aug 06 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.188-1
- Updated with the 4.4.188 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.188]

* Sun Aug 04 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.187-1
- Updated with the 4.4.187 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.187]

* Sun Jul 21 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.186-1
- Updated with the 4.4.186 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.186]

* Wed Jul 10 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.185-1
- Updated with the 4.4.185 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.185]

* Thu Jun 27 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.184-1
- Updated with the 4.4.184 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.184]

* Sat Jun 22 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.183-1
- Updated with the 4.4.183 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.183]

* Mon Jun 17 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.182-1
- Updated with the 4.4.182 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.182]

* Tue Jun 11 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.181-1
- Updated with the 4.4.181 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.181]
- Added NO_LIBZSTD=1 directive to the %global perf_make line.

* Wed May 22 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.180-2
- Apply a patch to fix the build of the turbostat binary, part of
- the tools sub-package. [https://elrepo.org/bugs/view.php?id=914]

* Thu May 16 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.180-1
- Updated with the 4.4.180 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.180]
- Purge the source tree of all unrequired dot-files.
- [https://elrepo.org/bugs/view.php?id=912]

* Sat Apr 27 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.179-1
- Updated with the 4.4.179 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.179]

* Wed Apr 03 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.178-1
- Updated with the 4.4.178 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.178]

* Sat Mar 23 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.177-1
- Updated with the 4.4.177 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.177]
- CONFIG_SQUASHFS_LZ4=y [https://elrepo.org/bugs/view.php?id=908]

* Sat Feb 23 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.176-1
- Updated with the 4.4.176 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.176]

* Wed Feb 20 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.175-1
- Updated with the 4.4.175 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.175]
- CONFIG_SND_COMPRESS_OFFLOAD=m, CONFIG_SND_HDA_EXT_CORE=m,
- CONFIG_SND_SOC_AC97_BUS=y, CONFIG_SND_SOC_COMPRESS=y,
- CONFIG_SND_SOC_TOPOLOGY=y, CONFIG_SND_ATMEL_SOC=m,
- CONFIG_SND_SST_MFLD_PLATFORM=m, CONFIG_SND_SST_IPC=m,
- CONFIG_SND_SST_IPC_ACPI=m, CONFIG_SND_SOC_INTEL_SST=m,
- CONFIG_SND_SOC_INTEL_SST_ACPI=m, CONFIG_SND_SOC_INTEL_HASWELL=m,
- CONFIG_SND_SOC_INTEL_BAYTRAIL=m, CONFIG_SND_SOC_INTEL_HASWELL_MACH=m,
- CONFIG_SND_SOC_INTEL_BYT_RT5640_MACH=m,
- CONFIG_SND_SOC_INTEL_BYT_MAX98090_MACH=m,
- CONFIG_SND_SOC_INTEL_BROADWELL_MACH=m,
- CONFIG_SND_SOC_INTEL_BYTCR_RT5640_MACH=m,
- CONFIG_SND_SOC_INTEL_CHT_BSW_RT5672_MACH=m,
- CONFIG_SND_SOC_INTEL_CHT_BSW_RT5645_MACH=m,
- CONFIG_SND_SOC_INTEL_CHT_BSW_MAX98090_TI_MACH=m,
- CONFIG_SND_SOC_INTEL_SKYLAKE=m, CONFIG_SND_SOC_INTEL_SKL_RT286_MACH=m,
- CONFIG_SND_SUN4I_CODEC=m, CONFIG_SND_SOC_XTFPGA_I2S=m,
- CONFIG_SND_SOC_AC97_CODEC=m, CONFIG_SND_SOC_ADAU1701=m,
- CONFIG_SND_SOC_AK4104=m, CONFIG_SND_SOC_AK4554=m, CONFIG_SND_SOC_AK4613=m,
- CONFIG_SND_SOC_AK4642=m, CONFIG_SND_SOC_AK5386=m, CONFIG_SND_SOC_ALC5623=m,
- CONFIG_SND_SOC_CS35L32=m, CONFIG_SND_SOC_CS42L51=m,
- CONFIG_SND_SOC_CS42L51_I2C=m, CONFIG_SND_SOC_CS42L52=m,
- CONFIG_SND_SOC_CS42L56=m, CONFIG_SND_SOC_CS42L73=m, CONFIG_SND_SOC_CS4265=m,
- CONFIG_SND_SOC_CS4270=m, CONFIG_SND_SOC_CS4271=m,
- CONFIG_SND_SOC_CS4271_I2C=m, CONFIG_SND_SOC_CS4271_SPI=m,
- CONFIG_SND_SOC_CS42XX8=m, CONFIG_SND_SOC_CS42XX8_I2C=m,
- CONFIG_SND_SOC_CS4349=m, CONFIG_SND_SOC_DMIC=m, CONFIG_SND_SOC_ES8328=m,
- CONFIG_SND_SOC_GTM601=m, CONFIG_SND_SOC_MAX98090=m, CONFIG_SND_SOC_PCM1681=m,
- CONFIG_SND_SOC_PCM1792A=m, CONFIG_SND_SOC_PCM512x=m,
- CONFIG_SND_SOC_PCM512x_I2C=m, CONFIG_SND_SOC_PCM512x_SPI=m,
- CONFIG_SND_SOC_RL6231=m, CONFIG_SND_SOC_RL6347A=m, CONFIG_SND_SOC_RT286=m,
- CONFIG_SND_SOC_RT5631=m, CONFIG_SND_SOC_RT5640=m, CONFIG_SND_SOC_RT5645=m,
- CONFIG_SND_SOC_RT5670=m, CONFIG_SND_SOC_SGTL5000=m,
- CONFIG_SND_SOC_SIGMADSP=m, CONFIG_SND_SOC_SIGMADSP_I2C=m,
- CONFIG_SND_SOC_SIRF_AUDIO_CODEC=m, CONFIG_SND_SOC_SPDIF=m,
- CONFIG_SND_SOC_SSM2602=m, CONFIG_SND_SOC_SSM2602_SPI=m,
- CONFIG_SND_SOC_SSM2602_I2C=m, CONFIG_SND_SOC_SSM4567=m,
- CONFIG_SND_SOC_STA32X=m, CONFIG_SND_SOC_STA350=m, CONFIG_SND_SOC_STI_SAS=m,
- CONFIG_SND_SOC_TAS2552=m, CONFIG_SND_SOC_TAS5086=m, CONFIG_SND_SOC_TAS571X=m,
- CONFIG_SND_SOC_TFA9879=m, CONFIG_SND_SOC_TLV320AIC23=m,
- CONFIG_SND_SOC_TLV320AIC23_I2C=m, CONFIG_SND_SOC_TLV320AIC23_SPI=m,
- CONFIG_SND_SOC_TLV320AIC31XX=m, CONFIG_SND_SOC_TLV320AIC3X=m,
- CONFIG_SND_SOC_TS3A227E=m, CONFIG_SND_SOC_WM8510=m, CONFIG_SND_SOC_WM8523=m,
- CONFIG_SND_SOC_WM8580=m, CONFIG_SND_SOC_WM8711=m, CONFIG_SND_SOC_WM8728=m,
- CONFIG_SND_SOC_WM8731=m, CONFIG_SND_SOC_WM8737=m, CONFIG_SND_SOC_WM8741=m,
- CONFIG_SND_SOC_WM8750=m, CONFIG_SND_SOC_WM8753=m, CONFIG_SND_SOC_WM8770=m,
- CONFIG_SND_SOC_WM8776=m, CONFIG_SND_SOC_WM8804=m, CONFIG_SND_SOC_WM8804_I2C=m,
- CONFIG_SND_SOC_WM8804_SPI=m, CONFIG_SND_SOC_WM8903=m, CONFIG_SND_SOC_WM8962=m,
- CONFIG_SND_SOC_WM8978=m, CONFIG_SND_SOC_TPA6130A2=m and
- CONFIG_SND_SIMPLE_CARD=m [https://elrepo.org/bugs/view.php?id=900]

* Fri Feb 08 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.174-1
- Updated with the 4.4.174 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.174]

* Wed Feb 06 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.173-1
- Updated with the 4.4.173 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.173]

* Sat Jan 26 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.172-1
- Updated with the 4.4.172 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.172]

* Wed Jan 16 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.171-1
- Updated with the 4.4.171 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.171]

* Sun Jan 13 2019 Alan Bartlett <ajb@elrepo.org> - 4.4.170-1
- Updated with the 4.4.170 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.170]

* Fri Dec 21 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.169-1
- Updated with the 4.4.169 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.169]

* Mon Dec 17 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.168-1
- Updated with the 4.4.168 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.168]

* Thu Dec 13 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.167-1
- Updated with the 4.4.167 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.167]

* Sat Dec 01 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.166-1
- Updated with the 4.4.166 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.166]

* Tue Nov 27 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.165-1
- Updated with the 4.4.165 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.165]

* Wed Nov 21 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.164-1
- Updated with the 4.4.164 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.164]

* Sat Nov 10 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.163-1
- Updated with the 4.4.163 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.163]

* Sat Oct 20 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.162-1
- Updated with the 4.4.162 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.162]

* Sat Oct 13 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.161-1
- Updated with the 4.4.161 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.161]

* Wed Oct 10 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.160-1
- Updated with the 4.4.160 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.160]

* Sat Sep 29 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.159-1
- Updated with the 4.4.159 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.159]

* Wed Sep 26 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.158-1
- Updated with the 4.4.158 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.158]

* Wed Sep 19 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.157-1
- Updated with the 4.4.157 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.157]

* Sat Sep 15 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.156-1
- Updated with the 4.4.156 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.156]

* Sun Sep 09 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.155-1
- Updated with the 4.4.155 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.155]

* Wed Sep 05 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.154-1
- Updated with the 4.4.154 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.154]

* Tue Aug 28 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.153-1
- Updated with the 4.4.153 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.153]

* Fri Aug 24 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.152-1
- Updated with the 4.4.152 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.152]

* Wed Aug 22 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.151-1
- Updated with the 4.4.151 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.151]
- CONFIG_NET_FOU_IP_TUNNELS=y
- [https://elrepo.org/bugs/view.php?id=865]

* Sat Aug 18 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.150-1
- Updated with the 4.4.150 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.150]

* Sat Aug 18 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.149-1
- Updated with the 4.4.149 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.149]
- Not released due to a source code defect.

* Thu Aug 16 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.148-1
- Updated with the 4.4.148 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.148]

* Thu Aug 09 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.147-1
- Updated with the 4.4.147 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.147]

* Mon Aug 06 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.146-1
- Updated with the 4.4.146 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.146]

* Sat Jul 28 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.145-1
- Updated with the 4.4.145 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.145]

* Wed Jul 25 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.144-1
- Updated with the 4.4.144 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.144]

* Sun Jul 22 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.143-1
- Updated with the 4.4.143 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.143]
- Removed the redundant ELRepo Project patch for the perf subsystem.

* Thu Jul 19 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.142-1
- Updated with the 4.4.142 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.142]

* Tue Jul 17 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.141-1
- Updated with the 4.4.141 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.141]
- Not released due to a source code defect.

* Wed Jul 11 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.140-1
- Updated with the 4.4.140 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.140]

* Tue Jul 03 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.139-1
- Updated with the 4.4.139 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.139]

* Sat Jun 16 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.138-1
- Updated with the 4.4.138 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.138]

* Wed Jun 13 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.137-1
- Updated with the 4.4.137 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.137]

* Wed Jun 06 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.136-1
- Updated with the 4.4.136 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.136]
- CONFIG_EFI_MIXED=y [https://elrepo.org/bugs/view.php?id=858]

* Wed May 30 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.135-1
- Updated with the 4.4.135 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.135]

* Wed May 30 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.134-1
- Updated with the 4.4.134 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.134]

* Sat May 26 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.133-1
- Updated with the 4.4.133 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.133]

* Wed May 16 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.132-1
- Updated with the 4.4.132 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.132]
- CONFIG_MD_CLUSTER=m [https://elrepo.org/bugs/view.php?id=847]

* Wed May 02 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.131-1
- Updated with the 4.4.131 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.131]

* Sun Apr 29 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.130-1
- Updated with the 4.4.130 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.130]

* Tue Apr 24 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.129-1
- Updated with the 4.4.129 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.129]

* Fri Apr 13 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.128-1
- Updated with the 4.4.128 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.128]

* Sun Apr 08 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.127-1
- Updated with the 4.4.127 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.127]

* Sat Mar 31 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.126-1
- Updated with the 4.4.126 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.126]
- CONFIG_STAGING_RDMA=m and CONFIG_INFINIBAND_HFI1=m
- [https://elrepo.org/bugs/view.php?id=835]

* Wed Mar 28 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.125-1
- Updated with the 4.4.125 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.125]

* Sun Mar 25 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.124-1
- Updated with the 4.4.124 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.124]

* Thu Mar 22 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.123-1
- Updated with the 4.4.123 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.123]

* Sun Mar 18 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.122-1
- Updated with the 4.4.122 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.122]

* Sun Mar 11 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.121-1
- Updated with the 4.4.121 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.121]

* Sun Mar 04 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.120-1
- Updated with the 4.4.120 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.120]

* Wed Feb 28 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.119-1
- Updated with the 4.4.119 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.119]

* Sun Feb 25 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.118-1
- Updated with the 4.4.118 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.118]

* Fri Feb 23 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.117-1
- Updated with the 4.4.117 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.117]
- Reverted "libxfs: pack the agfl header structure so XFS_AGFL_SIZE 
- is correct" [https://elrepo.org/bugs/view.php?id=829]

* Sat Feb 17 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.116-1
- Updated with the 4.4.116 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.116]
- Ensure that objtool is present in the kernel-lt-devel package
- if CONFIG_STACK_VALIDATION is set.
- [https://elrepo.org/bugs/view.php?id=819]

* Sun Feb 04 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.115-1
- Updated with the 4.4.115 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.115]
- CONFIG_BPF_JIT_ALWAYS_ON=y

* Wed Jan 31 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.114-1
- Updated with the 4.4.114 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.114]

* Wed Jan 24 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.113-1
- Updated with the 4.4.113 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.113]
- CONFIG_RETPOLINE=y

* Wed Jan 17 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.112-1
- Updated with the 4.4.112 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.112]
- CONFIG_GENERIC_CPU_VULNERABILITIES=y

* Wed Jan 10 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.111-1
- Updated with the 4.4.111 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.111]

* Fri Jan 05 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.110-1
- Updated with the 4.4.110 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.110]
- CONFIG_PAGE_TABLE_ISOLATION=y

* Tue Jan 02 2018 Alan Bartlett <ajb@elrepo.org> - 4.4.109-1
- Updated with the 4.4.109 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.109]

* Mon Dec 25 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.108-1
- Updated with the 4.4.108 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.108]

* Wed Dec 20 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.107-1
- Updated with the 4.4.107 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.107]

* Sat Dec 16 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.106-1
- Updated with the 4.4.106 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.106]
- CONFIG_PINMUX=y, CONFIG_PINCONF=y, CONFIG_GENERIC_PINCONF=y,
- CONFIG_PINCTRL_AMD=y, CONFIG_PINCTRL_CHERRYVIEW=m,
- CONFIG_PINCTRL_INTEL=m, CONFIG_PINCTRL_BROXTON=m and
- CONFIG_PINCTRL_SUNRISEPOINT=m
- [https://elrepo.org/bugs/view.php?id=804]
- CONFIG_DRM_AMDGPU_CIK=Y
- [https://elrepo.org/bugs/view.php?id=805]

* Sat Dec 09 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.105-1
- Updated with the 4.4.105 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.105]
- Adjusted the list of files to be removed, as they will be
- created by depmod at the package installation time.
- [https://elrepo.org/bugs/view.php?id=803]

* Tue Dec 05 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.104-1
- Updated with the 4.4.104 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.104]

* Thu Nov 30 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.103-1
- Updated with the 4.4.103 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.103]

* Fri Nov 24 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.102-1
- Updated with the 4.4.102 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.102]

* Fri Nov 24 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.101-1
- Updated with the 4.4.101 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.101]

* Tue Nov 21 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.100-1
- Updated with the 4.4.100 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.100]
- Applied the ELRepo Project patch for the perf subsystem.
- [https://lkml.org/lkml/2017/11/11/194]

* Sat Nov 18 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.99-1
- Updated with the 4.4.99 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.99]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Wed Nov 15 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.98-1
- Updated with the 4.4.98 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.98]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Wed Nov 08 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.97-1
- Updated with the 4.4.97 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.97]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Thu Nov 02 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.96-1
- Updated with the 4.4.96 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.96]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Fri Oct 27 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.95-1
- Updated with the 4.4.95 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.95]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Sun Oct 22 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.94-1
- Updated with the 4.4.94 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.94]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Wed Oct 18 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.93-1
- Updated with the 4.4.93 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.93]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Thu Oct 12 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.92-1
- Updated with the 4.4.92 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.92]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Sun Oct 08 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.91-1
- Updated with the 4.4.91 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.91]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Thu Oct 05 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.90-1
- Updated with the 4.4.90 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.90]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Wed Sep 27 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.89-1
- Updated with the 4.4.89 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.89]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Wed Sep 13 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.88-1
- Updated with the 4.4.88 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.88]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Fri Sep 08 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.87-1
- Updated with the 4.4.87 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.87]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Sat Sep 02 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.86-1
- Updated with the 4.4.86 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.86]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Wed Aug 30 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.85-1
- Updated with the 4.4.85 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.85]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Fri Aug 25 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.84-1
- Updated with the 4.4.84 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.84]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Thu Aug 17 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.83-1
- Updated with the 4.4.83 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.83]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Mon Aug 14 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.82-1
- Updated with the 4.4.82 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.82]
- CONFIG_MOUSE_PS2_VMMOUSE=y [https://elrepo.org/bugs/view.php?id=767]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Fri Aug 11 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.81-1
- Updated with the 4.4.81 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.81]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Mon Aug 07 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.80-1
- Updated with the 4.4.80 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.80]
- Build of perf subsystem has been disabled due to upstream
- code errors.

* Fri Jul 28 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.79-1
- Updated with the 4.4.79 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.79]

* Fri Jul 21 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.78-1
- Updated with the 4.4.78 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.78]

* Sat Jul 15 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.77-1
- Updated with the 4.4.77 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.77]

* Wed Jul 05 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.76-1
- Updated with the 4.4.76 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.76]

* Thu Jun 29 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.75-1
- Updated with the 4.4.75 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.75]

* Tue Jun 27 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.74-1
- Updated with the 4.4.74 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.74]

* Sat Jun 17 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.73-1
- Updated with the 4.4.73 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.73]

* Wed Jun 14 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.72-1
- Updated with the 4.4.72 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.72]

* Wed Jun 07 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.71-1
- Updated with the 4.4.71 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.71]
- CONFIG_HAMRADIO=y, CONFIG_AX25=m, CONFIG_AX25_DAMA_SLAVE=y,
- CONFIG_NETROM=m, CONFIG_ROSE=m, CONFIG_MKISS=m,
- CONFIG_6PACK=m, CONFIG_BPQETHER=m, CONFIG_BAYCOM_SER_FDX=m,
- CONFIG_BAYCOM_SER_HDX=m, CONFIG_BAYCOM_PAR=m and CONFIG_YAM=m
- [https://elrepo.org/bugs/view.php?id=745]

* Fri May 26 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.70-1
- Updated with the 4.4.70 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.70]

* Sun May 21 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.69-1
- Updated with the 4.4.69 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.69]

* Sun May 14 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.68-1
- Updated with the 4.4.68 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.68]

* Mon May 08 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.67-1
- Updated with the 4.4.67 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.67]

* Thu May 04 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.66-1
- Updated with the 4.4.66 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.66]
- CONFIG_DETECT_HUNG_TASK=y, CONFIG_DEFAULT_HUNG_TASK_TIMEOUT=120
- and CONFIG_BOOTPARAM_HUNG_TASK_PANIC_VALUE=0
- [https://elrepo.org/bugs/view.php?id=733]

* Sun Apr 30 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.65-1
- Updated with the 4.4.65 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.65]

* Thu Apr 27 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.64-1
- Updated with the 4.4.64 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.64]
- CONFIG_MLX5_CORE_EN=y [https://elrepo.org/bugs/view.php?id=730]

* Fri Apr 21 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.63-1
- Updated with the 4.4.63 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.63]

* Tue Apr 18 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.62-1
- Updated with the 4.4.62 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.62]
- CONFIG_USERFAULTFD=y
- [https://lists.elrepo.org/pipermail/elrepo/2017-April/003540.html]

* Wed Apr 12 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.61-1
- Updated with the 4.4.61 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.61]

* Sat Apr 08 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.60-1
- Updated with the 4.4.60 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.60]

* Fri Mar 31 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.59-1
- Updated with the 4.4.59 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.59]

* Thu Mar 30 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.58-1
- Updated with the 4.4.58 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.58]

* Sun Mar 26 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.57-1
- Updated with the 4.4.57 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.57]

* Wed Mar 22 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.56-1
- Updated with the 4.4.56 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.56]

* Sat Mar 18 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.55-1
- Updated with the 4.4.55 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.55]

* Wed Mar 15 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.54-1
- Updated with the 4.4.54 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.54]

* Sun Mar 12 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.53-1
- Updated with the 4.4.53 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.53]

* Sun Feb 26 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.52-1
- Updated with the 4.4.52 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.52]
- Added NO_PERF_READ_VDSO32=1 and NO_PERF_READ_VDSOX32=1
- directives to the %global perf_make line.
- [https://elrepo.org/bugs/view.php?id=719]

* Thu Feb 23 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.51-1
- Updated with the 4.4.51 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.51]

* Sat Feb 18 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.50-1
- Updated with the 4.4.50 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.50]

* Wed Feb 15 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.49-1
- Updated with the 4.4.49 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.49]

* Thu Feb 09 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.48-1
- Updated with the 4.4.48 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.48]

* Sat Feb 04 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.47-1
- Updated with the 4.4.47 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.47]

* Wed Feb 01 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.46-1
- Updated with the 4.4.46 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.46]

* Thu Jan 26 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.45-1
- Updated with the 4.4.45 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.45]
- Remove any orphaned initramfs-xxxkdump.img file
- found post kernel uninstall. [Akemi Yagi]

* Fri Jan 20 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.44-1
- Updated with the 4.4.44 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.44]

* Mon Jan 16 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.43-1
- Updated with the 4.4.43 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.43]

* Thu Jan 12 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.42-1
- Updated with the 4.4.42 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.42]

* Tue Jan 10 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.41-1
- Updated with the 4.4.41 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.41]
- CONFIG_CAN=m, CONFIG_CAN_RAW=m, CONFIG_CAN_BCM=m, CONFIG_CAN_GW=m,
- CONFIG_CAN_VCAN=m, CONFIG_CAN_SLCAN=m, CONFIG_CAN_DEV=m,
- CONFIG_CAN_CALC_BITTIMING=y, CONFIG_CAN_LEDS=y, CONFIG_CAN_JANZ_ICAN3=m,
- CONFIG_CAN_C_CAN=m, CONFIG_CAN_C_CAN_PLATFORM=m, CONFIG_CAN_C_CAN_PCI=m,
- CONFIG_CAN_CC770=m, CONFIG_CAN_CC770_ISA=m, CONFIG_CAN_CC770_PLATFORM=m,
- CONFIG_CAN_M_CAN=m, CONFIG_CAN_SJA1000=m, CONFIG_CAN_SJA1000_ISA=m,
- CONFIG_CAN_SJA1000_PLATFORM=m, CONFIG_CAN_EMS_PCMCIA=m,
- CONFIG_CAN_EMS_PCI=m, CONFIG_CAN_PEAK_PCMCIA=m, CONFIG_CAN_PEAK_PCI=m,
- CONFIG_CAN_PEAK_PCIEC=y, CONFIG_CAN_KVASER_PCI=m, CONFIG_CAN_PLX_PCI=m,
- CONFIG_CAN_SOFTING=m, CONFIG_CAN_SOFTING_CS=m, CONFIG_CAN_MCP251X=m,
- CONFIG_CAN_EMS_USB=m, CONFIG_CAN_ESD_USB2=m, CONFIG_CAN_GS_USB=m,
- CONFIG_CAN_KVASER_USB=m, CONFIG_CAN_PEAK_USB=m and CONFIG_CAN_8DEV_USB=m
- [https://elrepo.org/bugs/view.php?id=707]

* Fri Jan 06 2017 Alan Bartlett <ajb@elrepo.org> - 4.4.40-1
- Updated with the 4.4.40 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.40]

* Thu Dec 15 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.39-1
- Updated with the 4.4.39 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.39]

* Sat Dec 10 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.38-1
- Updated with the 4.4.38 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.38]

* Fri Dec 09 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.37-1
- Updated with the 4.4.37 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.37]

* Fri Dec 02 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.36-1
- Updated with the 4.4.36 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.36]

* Sat Nov 26 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.35-1
- Updated with the 4.4.35 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.35]

* Mon Nov 21 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.34-1
- Updated with the 4.4.34 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.34]

* Sat Nov 19 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.33-1
- Updated with the 4.4.33 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.33]
- CONFIG_BPF_SYSCALL=y and CONFIG_BPF_EVENTS=y
- [https://elrepo.org/bugs/view.php?id=690]

* Tue Nov 15 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.32-1
- Updated with the 4.4.32 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.32]

* Thu Nov 10 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.31-1
- Updated with the 4.4.31 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.31]
- CONFIG_FMC=m, CONFIG_FMC_CHARDEV=m and CONFIG_FMC_WRITE_EEPROM=m
- [https://elrepo.org/bugs/view.php?id=680]

* Tue Nov 01 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.30-1
- Updated with the 4.4.30 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.30]

* Mon Oct 31 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.29-1
- Updated with the 4.4.29 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.29]

* Fri Oct 28 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.28-1
- Updated with the 4.4.28 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.28]

* Sat Oct 22 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.27-1
- Updated with the 4.4.27 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.27]

* Thu Oct 20 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.26-1
- Updated with the 4.4.26 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.26]

* Mon Oct 17 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.25-1
- Updated with the 4.4.25 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.25]

* Fri Oct 07 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.24-1
- Updated with the 4.4.24 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.24]

* Fri Sep 30 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.23-1
- Updated with the 4.4.23 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.23]

* Sat Sep 24 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.22-1
- Updated with the 4.4.22 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.22]

* Thu Sep 15 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.21-1
- Updated with the 4.4.21 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.21]

* Wed Sep 07 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.20-1
- Updated with the 4.4.20 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.20]
- Disabled CONFIG_FW_LOADER_USER_HELPER_FALLBACK
- [https://elrepo.org/bugs/view.php?id=671]

* Sat Aug 20 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.19-1
- Updated with the 4.4.19 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.19]

* Tue Aug 16 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.18-1
- Updated with the 4.4.18 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.18]

* Wed Aug 10 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.17-1
- Updated with the 4.4.17 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.17]

* Wed Jul 27 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.16-1
- Updated with the 4.4.16 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.16]

* Tue Jul 12 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.15-1
- Updated with the 4.4.15 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.15]

* Sat Jun 25 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.14-1
- Updated with the 4.4.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.14]

* Wed Jun 08 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.13-1
- Updated with the 4.4.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.13]

* Thu Jun 02 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.12-1
- Updated with the 4.4.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.12]

* Thu May 19 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.11-1
- Updated with the 4.4.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.11]

* Thu May 12 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.10-1
- Updated with the 4.4.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.10]

* Thu May 05 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.9-1
- Updated with the 4.4.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.9]

* Wed Apr 20 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.8-1
- Updated with the 4.4.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.8]

* Sat Apr 16 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.7-1
- Updated with the 4.4.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.7]

* Mon Mar 21 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.6-1
- Updated with the 4.4.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.6]
- Forked this specification file so as to create
- a kernel-lt package set for EL7.

* Thu Mar 10 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.5-1
- Updated with the 4.4.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.5]

* Fri Mar 04 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.4-1
- Updated with the 4.4.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.4]

* Thu Feb 25 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.3-1
- Updated with the 4.4.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.3]

* Thu Feb 18 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.2-1
- Updated with the 4.4.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.2]

* Sun Jan 31 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.1-1
- Updated with the 4.4.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.1]

* Tue Jan 26 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.0-2
- CONFIG_SCSI_MPT2SAS=m [https://elrepo.org/bugs/view.php?id=628]

* Mon Jan 11 2016 Alan Bartlett <ajb@elrepo.org> - 4.4.0-1
- Updated with the 4.4 source tarball.

* Tue Dec 15 2015 Alan Bartlett <ajb@elrepo.org> - 4.3.3-1
- Updated with the 4.3.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.3.3]

* Thu Dec 10 2015 Alan Bartlett <ajb@elrepo.org> - 4.3.2-1
- Updated with the 4.3.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.3.2]

* Thu Dec 10 2015 Alan Bartlett <ajb@elrepo.org> - 4.3.1-1
- Updated with the 4.3.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.3.1]
- CONFIG_VXFS_FS=m [https://elrepo.org/bugs/view.php?id=606]

* Mon Nov 02 2015 Alan Bartlett <ajb@elrepo.org> - 4.3.0-1
- Updated with the 4.3 source tarball.

* Tue Oct 27 2015 Alan Bartlett <ajb@elrepo.org> - 4.2.5-1
- Updated with the 4.2.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.2.5]
- CONFIG_SCHEDSTATS=y [https://elrepo.org/bugs/view.php?id=603]

* Fri Oct 23 2015 Alan Bartlett <ajb@elrepo.org> - 4.2.4-1
- Updated with the 4.2.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.2.4]

* Sat Oct 03 2015 Alan Bartlett <ajb@elrepo.org> - 4.2.3-1
- Updated with the 4.2.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.2.3]

* Wed Sep 30 2015 Alan Bartlett <ajb@elrepo.org> - 4.2.2-1
- Updated with the 4.2.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.2.2]

* Mon Sep 21 2015 Alan Bartlett <ajb@elrepo.org> - 4.2.1-1
- Updated with the 4.2.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.2.1]
- CONFIG_BACKLIGHT_GPIO=m, CONFIG_BCMA_DRIVER_GPIO=y, CONFIG_CHARGER_GPIO=m,
- CONFIG_CHARGER_MANAGER=y, CONFIG_CLKDEV_LOOKUP=y, CONFIG_COMMON_CLK=y,
- CONFIG_EXTCON=y, CONFIG_GENERIC_IRQ_CHIP=y, CONFIG_GPIO_ACPI=y,
- CONFIG_GPIO_ADP5588=m, CONFIG_GPIO_AMD8111=m, CONFIG_GPIO_DEVRES=y,
- CONFIG_GPIO_DWAPB=m, CONFIG_GPIO_F7188X=m, CONFIG_GPIO_GENERIC=m,
- CONFIG_GPIO_GENERIC_PLATFORM=m, CONFIG_GPIO_ICH=m, CONFIG_GPIO_INTEL_MID=y,
- CONFIG_GPIO_IT8761E=m, CONFIG_GPIO_JANZ_TTL=m, CONFIG_GPIO_KEMPLD=m,
- CONFIG_GPIOLIB_IRQCHIP=y, CONFIG_GPIOLIB=y, CONFIG_GPIO_LP3943=m,
- CONFIG_GPIO_LYNXPOINT=m, CONFIG_GPIO_MAX7300=m, CONFIG_GPIO_MAX7301=m,
- CONFIG_GPIO_MAX730X=m, CONFIG_GPIO_MAX732X=m, CONFIG_GPIO_MC33880=m,
- CONFIG_GPIO_MCP23S08=m, CONFIG_GPIO_ML_IOH=m, CONFIG_GPIO_PCA953X=m,
- CONFIG_GPIO_PCF857X=m, CONFIG_GPIO_RDC321X=m, CONFIG_GPIO_SCH311X=m,
- CONFIG_GPIO_SCH=m, CONFIG_GPIO_SX150X=y, CONFIG_GPIO_SYSFS=y,
- CONFIG_GPIO_VX855=m, CONFIG_HAVE_CLK_PREPARE=y, CONFIG_HAVE_CLK=y,
- CONFIG_I2C_CBUS_GPIO=m, CONFIG_I2C_DESIGNWARE_PLATFORM=m, CONFIG_I2C_GPIO=m,
- CONFIG_I2C_MUX_GPIO=m, CONFIG_I2C_MUX_PCA954x=m, CONFIG_I2C_MUX_PINCTRL=m,
- CONFIG_LEDS_GPIO=m, CONFIG_LEDS_PCA9532_GPIO=y, CONFIG_LEDS_TRIGGER_GPIO=m,
- CONFIG_MDIO_GPIO=m, CONFIG_MFD_INTEL_QUARK_I2C_GPIO=m, CONFIG_MFD_SM501_GPIO=y,
- CONFIG_PINCTRL_BAYTRAIL=y, CONFIG_PINCTRL=y, CONFIG_PM_CLK=y,
- CONFIG_REGULATOR_GPIO=m, CONFIG_SENSORS_GPIO_FAN=m, CONFIG_SENSORS_SHT15=m,
- CONFIG_SND_COMPRESS_OFFLOAD=m, CONFIG_SND_DESIGNWARE_I2S=m,
- CONFIG_SND_DMAENGINE_PCM=m, CONFIG_SND_SOC_GENERIC_DMAENGINE_PCM=y,
- CONFIG_SND_SOC_I2C_AND_SPI=m, CONFIG_SND_SOC=m, CONFIG_SPI_GPIO=m,
- CONFIG_SPI_PXA2XX_DMA=y, CONFIG_SPI_PXA2XX=m, CONFIG_SPI_PXA2XX_PCI=m,
- CONFIG_SSB_DRIVER_GPIO=y, CONFIG_USB_DWC3_DUAL_ROLE=y, CONFIG_USB_F_MASS_STORAGE=m,
- CONFIG_USB_GADGET=m, CONFIG_USB_GADGET_STORAGE_NUM_BUFFERS=2,
- CONFIG_USB_GADGET_VBUS_DRAW=2, CONFIG_USB_LIBCOMPOSITE=m,
- CONFIG_USB_MASS_STORAGE=m and CONFIG_X86_INTEL_LPSS=y
- [https://elrepo.org/bugs/view.php?id=592]

* Mon Aug 31 2015 Alan Bartlett <ajb@elrepo.org> - 4.2.0-1
- Updated with the 4.2 source tarball.

* Mon Aug 17 2015 Alan Bartlett <ajb@elrepo.org> - 4.1.6-1
- Updated with the 4.1.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.1.6]

* Tue Aug 11 2015 Alan Bartlett <ajb@elrepo.org> - 4.1.5-1
- Updated with the 4.1.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.1.5]

* Wed Aug 05 2015 Alan Bartlett <ajb@elrepo.org> - 4.1.4-1
- Updated with the 4.1.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.1.4]

* Wed Jul 22 2015 Alan Bartlett <ajb@elrepo.org> - 4.1.3-1
- Updated with the 4.1.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.1.3]

* Sat Jul 11 2015 Alan Bartlett <ajb@elrepo.org> - 4.1.2-1
- Updated with the 4.1.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.1.2]

* Mon Jun 29 2015 Alan Bartlett <ajb@elrepo.org> - 4.1.1-1
- Updated with the 4.1.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.1.1]
- CONFIG_BLK_DEV_DRBD=m [https://elrepo.org/bugs/view.php?id=575]

* Mon Jun 22 2015 Alan Bartlett <ajb@elrepo.org> - 4.1.0-1
- Updated with the 4.1 source tarball.
- CONFIG_BRIDGE_NETFILTER=y [https://elrepo.org/bugs/view.php?id=573]

* Sun Jun 07 2015 Alan Bartlett <ajb@elrepo.org> - 4.0.5-1
- Updated with the 4.0.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.0.5]

* Sun May 17 2015 Alan Bartlett <ajb@elrepo.org> - 4.0.4-1
- Updated with the 4.0.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.0.4]

* Wed May 13 2015 Alan Bartlett <ajb@elrepo.org> - 4.0.3-1
- Updated with the 4.0.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.0.3]

* Thu May 07 2015 Alan Bartlett <ajb@elrepo.org> - 4.0.2-1
- Updated with the 4.0.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.0.2]

* Thu Apr 30 2015 Alan Bartlett <ajb@elrepo.org> - 4.0.1-1
- Updated with the 4.0.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.0.1]

* Mon Apr 13 2015 Alan Bartlett <ajb@elrepo.org> - 4.0.0-1
- Updated with the 4.0 source tarball.

* Thu Mar 26 2015 Alan Bartlett <ajb@elrepo.org> - 3.19.3-1
- Updated with the 3.19.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.19.3]

* Wed Mar 18 2015 Alan Bartlett <ajb@elrepo.org> - 3.19.2-1
- Updated with the 3.19.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.19.2]

* Sat Mar 07 2015 Alan Bartlett <ajb@elrepo.org> - 3.19.1-1
- Updated with the 3.19.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.19.1]

* Mon Feb 09 2015 Alan Bartlett <ajb@elrepo.org> - 3.19.0-1
- Updated with the 3.19 source tarball.

* Fri Feb 06 2015 Alan Bartlett <ajb@elrepo.org> - 3.18.6-1
- Updated with the 3.18.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.18.6]

* Fri Jan 30 2015 Alan Bartlett <ajb@elrepo.org> - 3.18.5-1
- Updated with the 3.18.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.18.5]

* Wed Jan 28 2015 Alan Bartlett <ajb@elrepo.org> - 3.18.4-1
- Updated with the 3.18.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.18.4]
- CONFIG_THUNDERBOLT=m [https://lists.elrepo.org/pipermail/elrepo/2015-January/002516.html]
- CONFIG_OVERLAY_FS=m [https://elrepo.org/bugs/view.php?id=548]

* Fri Jan 16 2015 Alan Bartlett <ajb@elrepo.org> - 3.18.3-1
- Updated with the 3.18.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.18.3]

* Fri Jan 09 2015 Alan Bartlett <ajb@elrepo.org> - 3.18.2-1
- Updated with the 3.18.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.18.2]

* Tue Dec 16 2014 Alan Bartlett <ajb@elrepo.org> - 3.18.1-1
- Updated with the 3.18.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.18.1]

* Mon Dec 08 2014 Alan Bartlett <ajb@elrepo.org> - 3.18.0-1
- Updated with the 3.18 source tarball.

* Mon Dec 08 2014 Alan Bartlett <ajb@elrepo.org> - 3.17.6-1
- Updated with the 3.17.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.17.6]

* Sun Dec 07 2014 Alan Bartlett <ajb@elrepo.org> - 3.17.5-1
- Updated with the 3.17.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.17.5]

* Sun Nov 30 2014 Alan Bartlett <ajb@elrepo,org> - 3.17.4-2
- CONFIG_BLK_DEV_NBD=m [https://elrepo.org/bugs/view.php?id=538]

* Sat Nov 22 2014 Alan Bartlett <ajb@elrepo.org> - 3.17.4-1
- Updated with the 3.17.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.17.4]
- CONFIG_CHROME_PLATFORMS=y, CONFIG_CHROMEOS_LAPTOP=m and
- CONFIG_CHROMEOS_PSTORE=m [https://elrepo.org/bugs/view.php?id=532]

* Sat Nov 15 2014 Alan Bartlett <ajb@elrepo.org> - 3.17.3-1
- Updated with the 3.17.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.17.3]
- CONFIG_BLK_DEV_RBD=m [https://elrepo.org/bugs/view.php?id=521]

* Fri Oct 31 2014 Alan Bartlett <ajb@elrepo.org> - 3.17.2-1
- Updated with the 3.17.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.17.2]

* Wed Oct 15 2014 Alan Bartlett <ajb@elrepo.org> - 3.17.1-1
- Updated with the 3.17.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.17.1]

* Mon Oct 06 2014 Alan Bartlett <ajb@elrepo.org> - 3.17.0-1
- Updated with the 3.17 source tarball.
- CONFIG_9P_FS=m, CONFIG_9P_FSCACHE=y and CONFIG_9P_FS_POSIX_ACL=y
- [https://elrepo.org/bugs/view.php?id=510]

* Thu Sep 18 2014 Alan Bartlett <ajb@elrepo.org> - 3.16.3-1
- Updated with the 3.16.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.16.3]

* Sat Sep 06 2014 Alan Bartlett <ajb@elrepo.org> - 3.16.2-1
- Updated with the 3.16.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.16.2]

* Thu Aug 14 2014 Alan Bartlett <ajb@elrepo.org> - 3.16.1-1
- Updated with the 3.16.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.16.1]
- CONFIG_ATH9K_DEBUGFS=y, CONFIG_ATH9K_HTC_DEBUGFS=y and
- CONFIG_ATH10K_DEBUGFS=y [https://elrepo.org/bugs/view.php?id=501]

* Mon Aug 04 2014 Alan Bartlett <ajb@elrepo.org> - 3.16.0-1
- Updated with the 3.16 source tarball.
- CONFIG_XEN_PCIDEV_BACKEND=y and CONFIG_XEN_FBDEV_FRONTEND=m [Mark Pryor]

* Fri Aug 01 2014 Alan Bartlett <ajb@elrepo.org> - 3.15.8-1
- Updated with the 3.15.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.15.8]

* Mon Jul 28 2014 Alan Bartlett <ajb@elrepo.org> - 3.15.7-1
- Updated with the 3.15.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.15.7]

* Fri Jul 18 2014 Alan Bartlett <ajb@elrepo.org> - 3.15.6-1
- Updated with the 3.15.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.15.6]

* Thu Jul 10 2014 Alan Bartlett <ajb@elrepo.org> - 3.15.5-1
- Updated with the 3.15.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.15.5]

* Mon Jul 07 2014 Alan Bartlett <ajb@elrepo.org> - 3.15.4-1
- Updated with the 3.15.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.15.4]

* Tue Jul 01 2014 Alan Bartlett <ajb@elrepo.org> - 3.15.3-1
- Updated with the 3.15.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.15.3]

* Fri Jun 27 2014 Alan Bartlett <ajb@elrepo.org> - 3.15.2-1
- Updated with the 3.15.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.15.2]

* Tue Jun 17 2014 Alan Bartlett <ajb@elrepo.org> - 3.15.1-1
- Updated with the 3.15.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.15.1]

* Thu Jun 12 2014 Alan Bartlett <ajb@elrepo.org> - 3.15.0-1
- General availability.

* Sun Jun 08 2014 Alan Bartlett <ajb@elrepo.org> - 3.15.0-0.rc8
- Updated with the 3.15 source tarball.
- The eighth release candidate of a kernel-ml package set for EL7.

* Sun Jun 08 2014 Alan Bartlett <ajb@elrepo.org> - 3.14.6-0.rc7
- Updated with the 3.14.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.14.6]
- The seventh release candidate of a kernel-ml package set for EL7.

* Wed Jun 04 2014 Alan Bartlett <ajb@elrepo.org> - 3.14.5-0.rc6
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.14.5]
- The sixth release candidate of a kernel-ml package set for EL7.
- Added a "Conflicts:" line for the kernel-ml-doc package.

* Mon Jun 02 2014 Alan Bartlett <ajb@elrepo.org> - 3.14.5-0.rc5
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.14.5]
- The fifth release candidate of a kernel-ml package set for EL7.
- CONFIG_SECURITY_TOMOYO_ACTIVATION_TRIGGER="/usr/lib/systemd/systemd"
- Corrected the "Conflicts:" line for the kernel-ml-tools-libs-devel
- package. [Akemi Yagi]

* Sun Jun 01 2014 Alan Bartlett <ajb@elrepo.org> - 3.14.5-0.rc4
- Updated with the 3.14.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.14.5]
- The fourth release candidate of a kernel-ml package set for EL7.
- Added a "Conflicts:" line for the kernel-ml-tools,
- kernel-ml-tools-libs and kernel-ml-tools-devel packages.

* Wed May 28 2014 Alan Bartlett <ajb@elrepo.org> - 3.14.4-0.rc3
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.14.4]
- The third release candidate of a kernel-ml package set for EL7.
- Fix a problem with the symlink between the /usr/src/$(uname -r)/
- directory and the /lib/modules/$(uname -r)/build directory.

* Sat May 24 2014 Alan Bartlett <ajb@elrepo.org> - 3.14.4-0.rc2
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.14.4]
- The second release candidate of a kernel-ml package set for EL7.
- Add calls of weak-modules to the %posttrans and %preun scripts.

* Tue May 20 2014 Alan Bartlett <ajb@elrepo.org> - 3.14.4-0.rc1
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.14.4]
- Skip the beta phase.
- The first release candidate of a kernel-ml package set for EL7.

* Mon May 19 2014 Alan Bartlett <ajb@elrepo.org> - 3.14.4-0.alpha3
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.14.4]
- The third attempt to build a kernel-ml package set for EL7.

* Sun May 18 2014 Alan Bartlett <ajb@elrepo.org> - 3.14.4-0.alpha2
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.14.4]
- The second attempt to build a kernel-ml package set for EL7.

* Sat May 17 2014 Alan Bartlett <ajb@elrepo.org> - 3.14.4-0.alpha1
- [https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.14.4]
- The first attempt to build a kernel-ml package set for EL7.
