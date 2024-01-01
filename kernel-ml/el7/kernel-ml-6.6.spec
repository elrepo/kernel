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
%define LKAver 6.6.9

# Define the buildid, if required.
#define buildid .local

# The following build options are enabled by default.
# Use either --without <option> on your rpmbuild command line
# or force the values to 0, here, to disable them.

# kernel-ml
%define with_default %{?_without_default: 0} %{?!_without_default: 1}
# kernel-ml-doc
%define with_doc     %{?_without_doc:     0} %{?!_without_doc:     1}
# kernel-ml-headers
%define with_headers %{?_without_headers: 0} %{?!_without_headers: 1}
# perf
%define with_perf    %{?_without_perf:    0} %{?!_without_perf:    1}
%define with_perf    0
# tools
%define with_tools   %{?_without_tools:   0} %{?!_without_tools:   1}
# gcc9
%define with_gcc9    %{?_without_gcc9:    0} %{?!_without_gcc9:    1}

# These architectures install vdso/ directories.
%define vdso_arches x86_64

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

%ifarch x86_64
# 64-bit kernel-ml, headers, perf and tools.
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
%define pkg_release 1%{?dist}%{?buildid}

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
# isn't required for the kernel-ml proper to function.
AutoReq: no
AutoProv: yes

#
# List the packages used during the kernel-ml build.
#
%if %{with_gcc9}
BuildRequires: devtoolset-9-gcc, devtoolset-9-binutils, devtoolset-9-runtime, scl-utils
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
BuildRequires: gettext, libcap-devel, ncurses-devel, pciutils-devel
%endif

# Sources.
Source0: https://www.kernel.org/pub/linux/kernel/v6.x/linux-%{LKAver}.tar.xz
Source1: config-%{version}-x86_64
Source2: cpupower.service
Source3: cpupower.config

# Do not package the source tarball.
NoSource: 0

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
%if %{with_gcc9}
. /opt/rh/devtoolset-9/enable
%endif

%setup -q -n %{name}-%{version} -c
%{__mv} linux-%{LKAver} linux-%{version}-%{release}.%{_target_cpu}

pushd linux-%{version}-%{release}.%{_target_cpu} > /dev/null

# Purge the source tree of all unrequired dot-files.
%{_bindir}/find -name '.*' -type f | %{_bindir}/xargs --no-run-if-empty %{__rm} -rf

%{__cp} %{SOURCE1} .

# Run make listnewconfig over all the configuration files.
%ifarch x86_64
for C in config-*-%{_target_cpu}*
do
    %{__cp} $C .config
    %{__make} -s ARCH=%{buildarch} listnewconfig | %{_bindir}/grep -E '^CONFIG_' > newoptions-el7-%{_target_cpu}.txt || true
    if [ -s newoptions-el7-%{_target_cpu}.txt ]; then
        cat newoptions-el7-%{_target_cpu}.txt
        exit 1
    fi
    %{__rm} -f newoptions-el7-%{_target_cpu}.txt
done
%endif

popd > /dev/null

%build
%if %{with_gcc9}
. /opt/rh/devtoolset-9/enable
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

    # Now ensure that the Makefile, .config, auto.conf, autoconf.h and version.h files
    # all have matching timestamps so that external modules can be built.
    %{_bindir}/touch -r $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/Makefile \
        $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/.config \
        $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/config/auto.conf \
        $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/linux/autoconf.h \
        $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/generated/autoconf.h \
        $RPM_BUILD_ROOT/lib/modules/%{KVRFA}/build/include/generated/uapi/linux/version.h

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
%if %{with_gcc9}
. /opt/rh/devtoolset-9/enable
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
#dir #{_includedir}/perf
#{_includedir}/perf/perf_dlfilter.h
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
%{_libdir}/libcpupower.so.1
%{_libdir}/libcpupower.so.0.0.1

%files -n %{name}-tools-libs-devel
%defattr(-,root,root)
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%{_includedir}/cpuidle.h
%endif
%endif

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

* Wed Nov 08 2023 S.Tindall <s10dal@elrepo.org> - 6.6.1-1
- Updated with the 6.6.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.1]

* Mon Oct 30 2023 Akemi Yagi <toracat@elrepo.org> - 6.6.0-1
- Updated with the 6.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6]

* Wed Oct 25 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.9-1
- Updated with the 6.5.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.9]

* Thu Oct 19 2023 S.Tindall <s10dal@elrepo.org> - 6.5.8-1
- Updated with the 6.5.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.8]

* Tue Oct 10 2023 S.Tindall <s10dal@elrepo.org> - 6.5.7-1
- Updated with the 6.5.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.7]

* Fri Oct 06 2023 S.Tindall <s10dal@elrepo.org> - 6.5.6-1
- Updated with the 6.5.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.6]

* Sat Sep 23 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.5-1
- Updated with the 6.5.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.5]

* Tue Sep 19 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.4-1
- Updated with the 6.5.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.4]

* Wed Sep 13 2023 S.Tindall <s10dal@elrepo.org> - 6.5.3-1
- Updated with the 6.5.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.3]
- Removed: CONFIG_IMA_TRUSTED_KEYRING=y
- Added: CONFIG_VIDEO_CAMERA_SENSOR=y

* Wed Sep 06 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.2-1
- Updated with the 6.5.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.2]

* Sat Sep 02 2023 Akemi Yagi <toracat@elrepo.org> - 6.5.1-1
- Updated with the 6.5.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.5.1]
- CONFIG_PAHOLE_VERSION=19

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

* Fri Jul 07 2023 S.Tindall <s10dal@elrepo.org> - 6.4.2-2
- Updated with the 6.4.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.2]
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

* Mon Jun 26 2023 S.Tindall <s10dal@elrepo.org> - 6.4.0-1
- Updated with the 6.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.0]
- CONFIG_ARCH_SUPPORTS_PER_VMA_LOCK=y
- CONFIG_ARCH_WANT_OPTIMIZE_VMEMMAP=y
- CONFIG_BLK_CGROUP_PUNT_BIO=y
- CONFIG_BLKDEV_UBLK_LEGACY_OPCODES=y
- CONFIG_CRYPTO_DEV_NITROX_CNN55XX=m
- CONFIG_CRYPTO_DEV_NITROX=m
- CONFIG_DRM_AMD_DC_FP=y
- CONFIG_DRM_SUBALLOC_HELPER=m
- CONFIG_DRM_VIRTIO_GPU_KMS=y
- CONFIG_FW_LOADER_DEBUG=y
- CONFIG_HAS_IOPORT=y
- CONFIG_IPWIRELESS=m
- CONFIG_LIBWX=m
- CONFIG_MAX_SKB_FRAGS=17
- CONFIG_MMU_LAZY_TLB_REFCOUNT=y
- CONFIG_NETFILTER_BPF_LINK=y
- CONFIG_NET_HANDSHAKE=y
- CONFIG_NET_VENDOR_WANGXUN=y
- CONFIG_NGBE=m
- CONFIG_PAGE_POOL_STATS=y
- CONFIG_PER_VMA_LOCK=y
- CONFIG_SMBFS=m
- CONFIG_SND_SOC_SOF_HDA_MLINK=m
- CONFIG_TXGBE=m
- CONFIG_USB_USS720=m
- CONFIG_VHOST_TASK=y
- CONFIG_VIDEO_CMDLINE=y
- CONFIG_XFS_SUPPORT_ASCII_CI=y

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
- CONFIG_SECURITY_YAMA=y [https://elrepo.org/bugs/view.php?id=1351]

* Wed May 17 2023 Alan Bartlett <ajb@elrepo.org> - 6.3.3-1
- Updated with the 6.3.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.3]

* Wed May 10 2023 Alan Bartlett <ajb@elrepo.org> - 6.3.2-1
- Updated with the 6.3.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.2]

* Sun Apr 23 2023 Alan Bartlett <ajb@elrepo.org> - 6.3.1-1
- Updated with the 6.3.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.3.1]

* Sun Apr 23 2023 Alan Bartlett <ajb@elrepo.org> - 6.3.0-1
- Updated with the 6.3 source tarball.
- CONFIG_SCHED_MM_CID=y, CONFIG_CPU_IDLE_GOV_HALTPOLL=y,
- CONFIG_KVM_GENERIC_HARDWARE_ENABLING=y, CONFIG_AS_GFNI=y,
- CONFIG_ZSMALLOC_CHAIN_SIZE=8, CONFIG_NF_CONNTRACK_OVS=y,
- CONFIG_NET_SCH_MQPRIO_LIB=m, CONFIG_NCN26000_PHY=m,
- CONFIG_ATH12K=m, CONFIG_SERIAL_8250_PCILIB=y,
- CONFIG_SERIAL_8250_PCI1XXXX=y, CONFIG_SENSORS_MC34VR500=m,
- CONFIG_SENSORS_MPQ7932_REGULATOR=y, CONFIG_SENSORS_MPQ7932=m,
- CONFIG_SENSORS_TDA38640=m, CONFIG_SENSORS_TDA38640_REGULATOR=y,
- CONFIG_SENSORS_XDPE122_REGULATOR=y, CONFIG_THERMAL_ACPI=y,
- CONFIG_INTEL_TCC=y, CONFIG_PROC_THERMAL_MMIO_RAPL=m,
- CONFIG_REGULATOR_MAX20411=m, CONFIG_VIDEO_HEXIUM_GEMINI=m,
- CONFIG_VIDEO_HEXIUM_ORION=m, CONFIG_VIDEO_MXB=m,
- CONFIG_DVB_BUDGET_CORE=m, CONFIG_DVB_BUDGET=m,
- CONFIG_DVB_BUDGET_CI=m, CONFIG_DVB_BUDGET_AV=m,
- CONFIG_UVC_COMMON=m, CONFIG_VIDEO_SAA7146=m,
- CONFIG_VIDEO_SAA7146_VV=m, CONFIG_BACKLIGHT_KTZ8866=m,
- CONFIG_SND_SOC_AW88395_LIB=m, CONFIG_SND_SOC_AW88395=m,
- CONFIG_SND_SOC_IDT821034=m, CONFIG_SND_SOC_PEB2466=m,
- CONFIG_SND_SOC_SMA1303=m, CONFIG_HID_SUPPORT=y,
- CONFIG_HID_EVISION=m, CONFIG_I2C_HID=y, CONFIG_XILINX_XDMA=m,
- CONFIG_SNET_VDPA=m, CONFIG_INTEL_IOMMU_PERF_EVENTS=y,
- CONFIG_POWERCAP=y, CONFIG_INTEL_RAPL_CORE=m, CONFIG_IDLE_INJECT=y,
- CONFIG_LEGACY_DIRECT_IO=y, CONFIG_EROFS_FS_PCPU_KTHREAD=y,
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
- CONFIG_SENSORS_OCC_P8_I2C=m, CONFIG_SENSORS_OCC=m,
- CONFIG_SENSORS_OXP=m, CONFIG_ADVANTECH_EC_WDT=m, CONFIG_MFD_SMPRO=m,
- CONFIG_REGULATOR_RT6190=m, CONFIG_VIDEO_TC358746=m,
- CONFIG_VIDEO_NOMODESET=y, CONFIG_DRM_I915_PREEMPT_TIMEOUT_COMPUTE=7500,
- CONFIG_SND_SOC_INTEL_AVS_MACH_MAX98927=m,
- CONFIG_SND_SOC_INTEL_AVS_MACH_PROBE=m, CONFIG_SND_SOC_WM8961=m,
- CONFIG_MANA_INFINIBAND=m, CONFIG_VFIO_CONTAINER=y, CONFIG_VFIO_VIRQFD=y,
- CONFIG_DELL_WMI_DDV=m, CONFIG_X86_PLATFORM_DRIVERS_HP=y,
- CONFIG_GENERIC_PHY_MIPI_DPHY=y, CONFIG_FPGA_MGR_LATTICE_SYSCONFIG=m,
- CONFIG_FPGA_MGR_LATTICE_SYSCONFIG_SPI=m,
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
- CONFIG_NTB_NETDEV=m, CONFIG_NTB=m, CONFIG_NTB_AMD=m,
- CONFIG_NTB_INTEL=m, CONFIG_NTB_EPF=m, CONFIG_NTB_PERF=m and
- CONFIG_NTB_TRANSPORT=m [https://elrepo.org/bugs/view.php?id=1322]

* Wed Feb 01 2023 Alan Bartlett <ajb@elrepo.org> - 6.1.9-1
- Updated with the 6.1.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.1.9]

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
- CONFIG_XEN_PV_MSR_SAFE=y, CONFIG_X86_AMD_PSTATE=y,
- CONFIG_HAVE_KVM_DIRTY_RING_TSO=y, CONFIG_HAVE_KVM_DIRTY_RING_ACQ_REL=y,
- CONFIG_HAVE_RUST=y, CONFIG_ARCH_SUPPORTS_CFI_CLANG=y,
- CONFIG_ARCH_HAS_NONLEAF_PMD_YOUNG=y, CONFIG_COMPACT_UNEVICTABLE_DEFAULT=1,
- CONFIG_AHCI_DWC=m, CONFIG_NGBE=m, CONFIG_NET_VENDOR_ADI=y,
- CONFIG_MLX5_EN_MACSEC=y, CONFIG_PCS_ALTERA_TSE=m,
- CONFIG_TOUCHSCREEN_COLIBRI_VF50=m, CONFIG_SENSORS_MAX31760=m,
- CONFIG_SENSORS_TPS546D24=m, CONFIG_SENSORS_EMC2305=m, CONFIG_EXAR_WDT=m,
- CONFIG_DRM_USE_DYNAMIC_DEBUG=y, CONFIG_DRM_GEM_DMA_HELPER=m,
- CONFIG_SND_SOC_AMD_PS=m, CONFIG_SND_SOC_AMD_PS_MACH=m,
- CONFIG_SND_SOC_SOF_AMD_REMBRANDT=m, CONFIG_SND_SOC_SOF_INTEL_SKL=m,
- CONFIG_SND_SOC_SOF_SKYLAKE=m, CONFIG_SND_SOC_SOF_KABYLAKE=m,
- CONFIG_SND_SOC_CS42L42_CORE=m, CONFIG_SND_SOC_CS42L83=m,
- CONFIG_SND_SOC_ES8326=m, CONFIG_SND_SOC_SRC4XXX_I2C=m,
- CONFIG_SND_SOC_SRC4XXX=m, CONFIG_HID_VRC2=m, CONFIG_HID_PXRC=m,
- CONFIG_HID_UDRAW_PS3=m, CONFIG_AMD_PMF=m, CONFIG_LTRF216A=m,
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
- CONFIG_INET_TABLE_PERTURB_ORDER=16, CONFIG_BPF_STREAM_PARSER=y and
- CONFIG_BPF_KPROBE_OVERRIDE=y

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
- CONFIG_HAVE_CONTEXT_TRACKING_USER=y,
- CONFIG_HAVE_CONTEXT_TRACKING_USER_OFFSTACK=y,
- CONFIG_SOFTIRQ_ON_OWN_STACK=y, CONFIG_NET_VENDOR_WANGXUN=y,
- CONFIG_TXGBE=m, CONFIG_BCM_NET_PHYPTP=m, CONFIG_CAN_NETLINK=y,
- CONFIG_CAN_RX_OFFLOAD=y, CONFIG_CAN_CAN327=m, CONFIG_CAN_ESD_USB=m,
- CONFIG_TCG_TIS_I2C=m, CONFIG_PINCTRL_METEORLAKE=m,
- CONFIG_SENSORS_LT7182S=m, CONFIG_APERTURE_HELPERS=y,
- CONFIG_SND_CTL_FAST_LOOKUP=y, CONFIG_SND_HDA_CS_DSP_CONTROLS=m,
- CONFIG_SND_INTEL_BYT_PREFER_SOF=y,
- CONFIG_SND_SOC_AMD_ST_ES8336_MACH=m,
- CONFIG_SND_AMD_ASOC_REMBRANDT=m, CONFIG_SND_SOC_AMD_RPL_ACP6x=m,
- CONFIG_SND_SOC_FSL_UTILS=m,
- CONFIG_SND_SOC_INTEL_SKYLAKE_HDAUDIO_CODEC=y,
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
- CONFIG_SND_SOC_INTEL_SOF_MAXIM_COMMON=m,
- CONFIG_SND_SOC_INTEL_SOF_REALTEK_COMMON=m,
- CONFIG_SND_SOC_INTEL_SOF_CIRRUS_COMMON=m,
- CONFIG_SND_SOC_INTEL_SOF_WM8804_MACH=m,
- CONFIG_SND_SOC_INTEL_GLK_DA7219_MAX98357A_MACH=m,
- CONFIG_SND_SOC_INTEL_GLK_RT5682_MAX98357A_MACH=m,
- CONFIG_SND_SOC_INTEL_SKL_HDA_DSP_GENERIC_MACH=m,
- CONFIG_SND_SOC_INTEL_SOF_RT5682_MACH=m,
- CONFIG_SND_SOC_INTEL_SOF_CS42L42_MACH=m,
- CONFIG_SND_SOC_INTEL_SOF_PCM512x_MACH=m,
- CONFIG_SND_SOC_INTEL_SOF_ES8336_MACH=m,
- CONFIG_SND_SOC_INTEL_SOF_NAU8825_MACH=m,
- CONFIG_SND_SOC_INTEL_CML_LP_DA7219_MAX98357A_MACH=m,
- CONFIG_SND_SOC_INTEL_SOF_CML_RT1011_RT5682_MACH=m,
- CONFIG_SND_SOC_INTEL_SOF_DA7219_MAX98373_MACH=m,
- CONFIG_SND_SOC_INTEL_SOF_SSP_AMP_MACH=m,
- CONFIG_SND_SOC_INTEL_EHL_RT5660_MACH=m,
- CONFIG_SND_SOC_SOF_IPC3=y, CONFIG_SND_SOC_SOF_INTEL_IPC4=y,
- CONFIG_SND_SOC_SOF_INTEL_MTL=m, CONFIG_SND_SOC_SOF_METEORLAKE=m,
- CONFIG_SND_SOC_HDA=m, CONFIG_SND_SOC_RT274=m,
- CONFIG_SND_SOC_RT1011=m, CONFIG_SND_SOC_RT1015=m,
- CONFIG_SND_SOC_RT1015P=m, CONFIG_SND_SOC_RT1308=m,
- CONFIG_SND_SOC_TAS2780=m, CONFIG_SND_VIRTIO=m,
- CONFIG_LEDS_IS31FL319X=m, CONFIG_INFINIBAND_ERDMA=m,
- CONFIG_P2SB=y, CONFIG_FPGA_MGR_MICROCHIP_SPI=m,
- CONFIG_CRYPTO_FIPS_NAME="Linux Kernel Cryptographic API",
- CONFIG_CRYPTO_XCTR=m, CONFIG_CRYPTO_HCTR2=m,
- CONFIG_CRYPTO_POLYVAL=m, CONFIG_CRYPTO_POLYVAL_CLMUL_NI=m,
- CONFIG_CRYPTO_ARIA=m, CONFIG_CRYPTO_LIB_SHA1=y and
- CONFIG_POLYNOMIAL=m

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
- CONFIG_SND_SOC_SOF_TOPLEVEL=y, CONFIG_SND_SOC_SOF_PCI_DEV=m,
- CONFIG_SND_SOC_SOF_PCI=m, CONFIG_SND_SOC_SOF_ACPI=m,
- CONFIG_SND_SOC_SOF_ACPI_DEV=m, CONFIG_SND_SOC_SOF_DEBUG_PROBES=m,
- CONFIG_SND_SOC_SOF_CLIENT=m, CONFIG_SND_SOC_SOF=m,
- CONFIG_SND_SOC_SOF_PROBE_WORK_QUEUE=y, CONFIG_SND_SOC_SOF_AMD_TOPLEVEL=m,
- CONFIG_SND_SOC_SOF_AMD_COMMON=m, CONFIG_SND_SOC_SOF_AMD_RENOIR=m,
- CONFIG_SND_SOC_SOF_INTEL_TOPLEVEL=y, CONFIG_SND_SOC_SOF_INTEL_HIFI_EP_IPC=m,
- CONFIG_SND_SOC_SOF_INTEL_ATOM_HIFI_EP=m, CONFIG_SND_SOC_SOF_INTEL_COMMON=m,
- CONFIG_SND_SOC_SOF_BAYTRAIL=m, CONFIG_SND_SOC_SOF_BROADWELL=m,
- CONFIG_SND_SOC_SOF_MERRIFIELD=m, CONFIG_SND_SOC_SOF_INTEL_APL=m,
- CONFIG_SND_SOC_SOF_APOLLOLAKE=m, CONFIG_SND_SOC_SOF_GEMINILAKE=m,
- CONFIG_SND_SOC_SOF_INTEL_CNL=m, CONFIG_SND_SOC_SOF_CANNONLAKE=m,
- CONFIG_SND_SOC_SOF_COFFEELAKE=m, CONFIG_SND_SOC_SOF_COMETLAKE=m,
- CONFIG_SND_SOC_SOF_INTEL_ICL=m, CONFIG_SND_SOC_SOF_ICELAKE=m,
- CONFIG_SND_SOC_SOF_JASPERLAKE=m, CONFIG_SND_SOC_SOF_INTEL_TGL=m,
- CONFIG_SND_SOC_SOF_TIGERLAKE=m, CONFIG_SND_SOC_SOF_ELKHARTLAKE=m,
- CONFIG_SND_SOC_SOF_ALDERLAKE=m, CONFIG_SND_SOC_SOF_HDA_COMMON=m,
- CONFIG_SND_SOC_SOF_HDA_LINK=y, CONFIG_SND_SOC_SOF_HDA_AUDIO_CODEC=y,
- CONFIG_SND_SOC_SOF_HDA_LINK_BASELINE=m, CONFIG_SND_SOC_SOF_HDA=m,
- CONFIG_SND_SOC_SOF_HDA_PROBES=m,
- CONFIG_SND_SOC_SOF_INTEL_SOUNDWIRE_LINK_BASELINE=m,
- CONFIG_SND_SOC_SOF_XTENSA=m and CONFIG_SND_SOC_HDAC_HDA=m
- [https://elrepo.org/bugs/view.php?id=1259]

* Wed Aug 31 2022 Alan Bartlett <ajb@elrepo.org> - 5.19.6-1
- Updated with the 5.19.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.19.6]

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
- CONFIG_INITRAMFS_PRESERVE_MTIME=y, CONFIG_DYNAMIC_PHYSICAL_MASK=y,
- CONFIG_INTEL_TDX_GUEST=y, CONFIG_BOOT_VESA_SUPPORT=y,
- CONFIG_X86_MEM_ENCRYPT=y, CONFIG_LEGACY_VSYSCALL_XONLY=y,
- CONFIG_MMU_GATHER_MERGE_VMAS=y, CONFIG_HAVE_OBJTOOL=y,
- CONFIG_HAVE_JUMP_LABEL_HACK=y, CONFIG_HAVE_NOINSTR_HACK=y,
- CONFIG_HAVE_NOINSTR_VALIDATION=y, CONFIG_HAVE_UACCESS_VALIDATION=y,
- CONFIG_ARCH_HAS_CC_PLATFORM=y, CONFIG_ARCH_HAS_VM_GET_PAGE_PROT=y,
- CONFIG_PTE_MARKER=y, CONFIG_PTE_MARKER_UFFD_WP=y,
- CONFIG_CAN_CTUCANFD=m, CONFIG_CAN_CTUCANFD_PCI=m,
- CONFIG_FW_LOADER_SYSFS=y, CONFIG_MHI_BUS_EP=m,
- CONFIG_EFI_DXE_MEM_ATTRIBUTES=y, CONFIG_OCTEON_EP=m,
- CONFIG_SFC_SIENA=m, CONFIG_SFC_SIENA_MTD=y,
- CONFIG_SFC_SIENA_MCDI_MON=y, CONFIG_SFC_SIENA_MCDI_LOGGING=y,
- CONFIG_ADIN1100_PHY=m, CONFIG_DP83TD510_PHY=m,
- CONFIG_WLAN_VENDOR_PURELIFI=y, CONFIG_PLFXLC=m,
- CONFIG_RTW89_8852C=m, CONFIG_RTW89_8852CE=m,
- CONFIG_WLAN_VENDOR_SILABS=y, CONFIG_WFX=m, CONFIG_MTK_T7XX=m,
- CONFIG_JOYSTICK_SENSEHAT=m, CONFIG_PINCTRL_AMD=y,
- CONFIG_SENSORS_NCT6775_CORE=m, CONFIG_SENSORS_NCT6775_I2C=m,
- CONFIG_SENSORS_XDPE152=m, CONFIG_MFD_SIMPLE_MFD_I2C=m,
- CONFIG_REGULATOR_RT5759=m, CONFIG_DRM_DISPLAY_HELPER=m,
- CONFIG_DRM_DISPLAY_DP_HELPER=y, CONFIG_DRM_DISPLAY_HDCP_HELPER=y,
- CONFIG_DRM_DISPLAY_HDMI_HELPER=y, CONFIG_SND_SOC_CS35L45_TABLES=m,
- CONFIG_SND_SOC_CS35L45=m, CONFIG_SND_SOC_CS35L45_SPI=m,
- CONFIG_SND_SOC_CS35L45_I2C=m, CONFIG_SND_SOC_MAX98396=m,
- CONFIG_SND_SOC_WM8731_I2C=m, CONFIG_SND_SOC_WM8731_SPI=m,
- CONFIG_SND_SOC_WM8940=m, CONFIG_CHROMEOS_ACPI=m,
- CONFIG_MULTIPLEXER=m, CONFIG_ARCH_WANT_HUGETLB_PAGE_OPTIMIZE_VMEMMAP=y,
- CONFIG_HUGETLB_PAGE_OPTIMIZE_VMEMMAP=y, CONFIG_TRUSTED_KEYS_TPM=y,
- CONFIG_RANDSTRUCT_NONE=y, CONFIG_CRYPTO_SM3_GENERIC=m,
- CONFIG_ARCH_HAS_FORCE_DMA_UNENCRYPTED=y, CONFIG_STACKDEPOT=y,
- CONFIG_STACK_HASH_ORDER=20, CONFIG_OBJTOOL=y and
- CONFIG_RCU_EXP_CPU_STALL_TIMEOUT=0

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
- CONFIG_PAHOLE_VERSION=0, CONFIG_CLOCKSOURCE_WATCHDOG_MAX_SKEW_US=100,
- CONFIG_CC_HAS_IBT=y, CONFIG_KRETPROBE_ON_RETHOOK=y,
- CONFIG_HAVE_ARCH_HUGE_VMALLOC=y, CONFIG_RANDOMIZE_KSTACK_OFFSET=y,
- CONFIG_HAVE_PREEMPT_DYNAMIC_CALL=y, CONFIG_BLOCK_LEGACY_AUTOLOAD=y,
- CONFIG_BLK_MQ_STACKING=y, CONFIG_DEVICE_MIGRATION=y,
- CONFIG_ARCH_HAS_CURRENT_STACK_POINTER=y, CONFIG_NET_VENDOR_DAVICOM=y,
- CONFIG_DM9051=m, CONFIG_NET_VENDOR_FUNGIBLE=y, CONFIG_FUN_CORE=m,
- CONFIG_FUN_ETH=m, CONFIG_MT7921U=m, CONFIG_RTW89_8852A=m,
- CONFIG_INPUT_VIVALDIFMAP=y, CONFIG_TOUCHSCREEN_IMAGIS=m,
- CONFIG_I2C_CCGX_UCSI=m, CONFIG_I8K=y,
- CONFIG_SENSORS_LM25066_REGULATOR=y, CONFIG_SENSORS_PLI1209BC=m,
- CONFIG_SENSORS_PLI1209BC_REGULATOR=y, CONFIG_SENSORS_SY7636A=m,
- CONFIG_SENSORS_TMP464=m, CONFIG_SENSORS_ASUS_EC=m,
- CONFIG_INTEL_HFI_THERMAL=y, CONFIG_REGULATOR_RT5190A=m,
- CONFIG_REGULATOR_SY7636A=m, CONFIG_DRM_DP_HELPER=m, CONFIG_DRM_BUDDY=m,
- CONFIG_SND_SOC_AMD_ACP_PDM=m, CONFIG_SND_SOC_AMD_ACP_PCI=m,
- CONFIG_SND_SOC_INTEL_AVS=m, CONFIG_SND_SOC_AW8738=m,
- CONFIG_SND_SOC_TAS5805M=m, CONFIG_SND_SOC_LPASS_MACRO_COMMON=m,
- CONFIG_HID_VIVALDI_COMMON=m, CONFIG_VMGENID=y, CONFIG_AMD_HSMP=m,
- CONFIG_INTEL_SDSI=m, CONFIG_SERIAL_MULTI_INSTANTIATE=m,
- CONFIG_IOMMU_SVA=y, CONFIG_F2FS_UNFAIR_RWSEM=y,
- CONFIG_CRYPTO_DH_RFC7919_GROUPS=y, CONFIG_CRYPTO_CRC64_ROCKSOFT=m,
- CONFIG_CRYPTO_SM3_AVX_X86_64=m, CONFIG_CRYPTO_LIB_SM3=m,
- CONFIG_CRC64_ROCKSOFT=m, CONFIG_DEBUG_INFO_NONE=y,
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
- CONFIG_GUEST_PERF_EVENTS=y, CONFIG_ACPI_PCC=y,
- CONFIG_X86_AMD_PSTATE=m, CONFIG_HAVE_KVM_PFNCACHE=y,
- CONFIG_HAVE_KVM_DIRTY_RING=y, CONFIG_PAGE_SIZE_LESS_THAN_256KB=y,
- CONFIG_ARCH_SUPPORTS_PAGE_TABLE_CHECK=y, CONFIG_BLK_ICQ=y,
- CONFIG_BT_MTK=m, CONFIG_NET_9P_FD=m, CONFIG_CS_DSP=m,
- CONFIG_NET_VENDOR_ENGLEDER=y, CONFIG_TSNEP=m, CONFIG_ICE_HWTS=y,
- CONFIG_NET_VENDOR_VERTEXCOM=y, CONFIG_MSE102X=m,
- CONFIG_WWAN_DEBUGFS=y, CONFIG_MHI_WWAN_CTRL=m,
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
- CONFIG_SND_AMD_ACP_CONFIG=m, CONFIG_SND_SOC_WM_ADSP=m,
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
- CONFIG_DRM_VBOXVIDEO=m [https://elrepo.org/bugs/view.php?id=1189]

* Thu Jan 20 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.2-1
- Updated with the 5.16.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.2]

* Sun Jan 16 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.1-1
- Updated with the 5.16.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.1]

* Sun Jan 09 2022 Alan Bartlett <ajb@elrepo.org> - 5.16.0-1
- Updated with the 5.16 source tarball.
- CONFIG_PREEMPT_BUILD=y, CONFIG_PREEMPT_COUNT=y, CONFIG_PREEMPTION=y,
- CONFIG_PREEMPT_DYNAMIC=y, CONFIG_PREEMPT_RCU=y, CONFIG_TASKS_RCU=y,
- CONFIG_CC_IMPLICIT_FALLTHROUGH="-Wimplicit-fallthrough=5",
- CONFIG_SCHED_CLUSTER=y, CONFIG_ARCH_CORRECT_STACKTRACE_ON_KRETPROBE=y,
- CONFIG_PAGE_SIZE_LESS_THAN_64KB=y, CONFIG_DYNAMIC_SIGFRAME=y,
- CONFIG_UNINLINE_SPIN_UNLOCK=y, CONFIG_EXCLUSIVE_SYSTEM_RAM=y,
- CONFIG_NETFILTER_EGRESS=y, CONFIG_NETFILTER_SKIP_EGRESS=y,
- CONFIG_DM_AUDIT=y, CONFIG_AMT=m, CONFIG_NET_VENDOR_ASIX=y,
- CONFIG_SPI_AX88796C=m, CONFIG_SPI_AX88796C_COMPRESSION=y,
- CONFIG_BRCMSMAC_LEDS=y, CONFIG_MT7921_COMMON=m, CONFIG_MT7921S=m,
- CONFIG_RTW89=m, CONFIG_RTW89_CORE=m, CONFIG_RTW89_PCI=m,
- CONFIG_RTW89_8852AE=m, CONFIG_SENSORS_MAX6620=m, CONFIG_CEC_PIN=y,
- CONFIG_CEC_GPIO=m, CONFIG_SND_SOC_AMD_VANGOGH_MACH=m,
- CONFIG_SND_SOC_AMD_ACP6x=m, CONFIG_SND_SOC_AMD_YC_MACH=m,
- CONFIG_SND_SOC_AMD_ACP_COMMON=m, CONFIG_SND_SOC_AMD_ACP_I2S=m,
- CONFIG_SND_SOC_AMD_ACP_PCM=m, CONFIG_SND_AMD_ASOC_RENOIR=m,
- CONFIG_SND_SOC_AMD_MACH_COMMON=m, CONFIG_SND_SOC_AMD_LEGACY_MACH=m,
- CONFIG_SND_SOC_AMD_SOF_MACH=m, CONFIG_SND_SOC_CS35L41_SPI=m,
- CONFIG_SND_SOC_CS35L41_I2C=m, CONFIG_SND_SOC_MAX98520=m,
- CONFIG_SND_SOC_RT1019=m, CONFIG_SND_SOC_RT5682S=m,
- CONFIG_SND_SOC_RT9120=m, CONFIG_SND_SOC_NAU8821=m,
- CONFIG_VIRTIO_PCI_LIB_LEGACY=m, CONFIG_ALIBABA_ENI_VDPA=m,
- CONFIG_XEN_PCI_STUB=y, CONFIG_NVIDIA_WMI_EC_BACKLIGHT=m,
- CONFIG_BARCO_P50_GPIO=m, CONFIG_XZ_DEC_MICROLZMA=y,
- CONFIG_HAVE_SAMPLE_FTRACE_DIRECT=y and
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
- CONFIG_PERF_EVENTS_AMD_UNCORE=y, CONFIG_ARCH_HAS_PARANOID_L1D_FLUSH=y,
- CONFIG_BLK_DEV_BSG_COMMON=y, CONFIG_BLOCK_HOLDER_DEPRECATED=y,
- CONFIG_AF_UNIX_OOB=y, CONFIG_SYSFB=y, CONFIG_SYSFB_SIMPLEFB=y,
- CONFIG_SCSI_COMMON=y, CONFIG_NET_VENDOR_LITEX=y,
- CONFIG_MAXLINEAR_GPHY=m, CONFIG_I2C_VIRTIO=m,
- CONFIG_PTP_1588_CLOCK_OPTIONAL=m, CONFIG_GPIO_AGGREGATOR=m,
- CONFIG_GPIO_VIRTIO=m, CONFIG_SENSORS_AQUACOMPUTER_D5NEXT=m,
- CONFIG_SENSORS_SBRMI=m, CONFIG_REGULATOR_RTQ2134=m,
- CONFIG_REGULATOR_RTQ6752=m, CONFIG_SND_HDA_CODEC_CS8409=m,
- CONFIG_SND_SOC_AMD_ACP5x=m, CONFIG_SND_SOC_ICS43432=m,
- CONFIG_INTEL_IDXD_BUS=m, CONFIG_AMD_PTDMA=m, CONFIG_VFIO_PCI_CORE=m,
- CONFIG_VDPA_USER=m, CONFIG_VHOST_RING=m, CONFIG_MERAKI_MX100=m,
- CONFIG_INTEL_ATOMISP2_PDX86=y, CONFIG_INTEL_WMI=y,
- CONFIG_IOMMU_DEFAULT_DMA_LAZY=y, CONFIG_F2FS_IOSTAT=y,
- CONFIG_NETFS_STATS=y, CONFIG_SMBFS_COMMON=m,
- CONFIG_CRYPTO_LIB_SM4=m and CONFIG_MODULE_SIG_KEY_TYPE_RSA=y

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
- CONFIG_XDP_SOCKETS=y and CONFIG_XDP_SOCKETS_DIAG=m
- [https://elrepo.org/bugs/view.php?id=1147]

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
- CONFIG_BRIDGE_NETFILTER=m [https://elrepo.org/bugs/view.php?id=1135]

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
- CONFIG_MODULE_SIG_HASH="sha512", CONFIG_ARCH_HAS_ZONE_DMA_SET=y,
- CONFIG_SECRETMEM=y, CONFIG_NETFILTER_NETLINK_HOOK=m,
- CONFIG_MEDIATEK_GE_PHY=m, CONFIG_MOTORCOMM_PHY=m,
- CONFIG_FWNODE_MDIO=y, CONFIG_ACPI_MDIO=y, CONFIG_JOYSTICK_QWIIC=m,
- CONFIG_SENSORS_DPS920AB=m, CONFIG_SENSORS_MP2888=m,
- CONFIG_SENSORS_PIM4328=m, CONFIG_SENSORS_SHT4x=m,
- CONFIG_REGULATOR_MAX8893=m, CONFIG_REGULATOR_RT6160=m,
- CONFIG_REGULATOR_RT6245=m, CONFIG_V4L2_ASYNC=m,
- CONFIG_SND_SOC_SSM2518=m, CONFIG_SND_SOC_TFA989X=m,
- CONFIG_LEDS_LT3593=m, CONFIG_INFINIBAND_IRDMA=m,
- CONFIG_DELL_WMI_PRIVACY=y, CONFIG_WIRELESS_HOTKEY=m,
- CONFIG_THINKPAD_LMI=m, CONFIG_X86_PLATFORM_DRIVERS_INTEL=y,
- CONFIG_FW_ATTR_CLASS=m, CONFIG_INTEL_SPEED_SELECT_INTERFACE=m,
- CONFIG_IOMMU_SVA_LIB=y, CONFIG_VIRTIO_IOMMU=m,
- CONFIG_PHY_CAN_TRANSCEIVER=m, CONFIG_HUGETLB_PAGE_FREE_VMEMMAP=y,
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
- CONFIG_AS_IS_GNU=y, CONFIG_AS_VERSION=23200, CONFIG_CGROUP_MISC=y,
- CONFIG_HAVE_ARCH_USERFAULTFD_MINOR=y,
- CONFIG_ARCH_MHP_MEMMAP_ON_MEMORY_ENABLE=y,
- CONFIG_HAVE_ARCH_RANDOMIZE_KSTACK_OFFSET=y,
- CONFIG_MODULE_COMPRESS_NONE=y,
- CONFIG_MODPROBE_PATH="/sbin/modprobe", CONFIG_MHP_MEMMAP_ON_MEMORY=y,
- CONFIG_NF_LOG_SYSLOG=m, CONFIG_NETFILTER_XTABLES_COMPAT=y,
- CONFIG_PCPU_DEV_REFCNT=y, CONFIG_CAN_ETAS_ES58X=m,
- CONFIG_BT_VIRTIO=m, CONFIG_NET_SELFTESTS=y,
- CONFIG_NET_VENDOR_MICROSOFT=y, CONFIG_MICROSOFT_MANA=m,
- CONFIG_MARVELL_88X2222_PHY=m, CONFIG_NXP_C45_TJA11XX_PHY=m,
- CONFIG_TOUCHSCREEN_HYCON_HY46XX=m, CONFIG_TOUCHSCREEN_ILITEK=m,
- CONFIG_TOUCHSCREEN_MSG2638=m, CONFIG_I2C_CP2615=m,
- CONFIG_SPI_ALTERA_CORE=m, CONFIG_SENSORS_NZXT_KRAKEN2=m,
- CONFIG_SENSORS_BPA_RS600=m, CONFIG_SENSORS_FSP_3Y=m,
- CONFIG_SENSORS_IR36021=m, CONFIG_SENSORS_MAX15301=m,
- CONFIG_SENSORS_STPDDC60=m, CONFIG_INTEL_SOC_DTS_THERMAL=m,
- CONFIG_INT3406_THERMAL=m, CONFIG_INTEL_TCC_COOLING=m,
- CONFIG_DRM_I915_REQUEST_TIMEOUT=20000, CONFIG_DRM_XEN=y,
- CONFIG_DRM_XEN_FRONTEND=m, CONFIG_DRM_GUD=m,
- CONFIG_VIDEOMODE_HELPERS=y, CONFIG_SND_CTL_LED=m,
- CONFIG_SND_SOC_RT5682=m, CONFIG_SND_SOC_RT5682_I2C=m,
- CONFIG_SND_SOC_TLV320AIC3X_I2C=m, CONFIG_SND_SOC_TLV320AIC3X_SPI=m,
- CONFIG_RTC_DRV_GOLDFISH=m, CONFIG_UIO_DFL=m, CONFIG_VP_VDPA=m,
- CONFIG_GIGABYTE_WMI=m, CONFIG_ADV_SWBUTTON=m, CONFIG_NETFS_SUPPORT=m,
- CONFIG_NFS_V4_2_SSC_HELPER=y, CONFIG_CRYPTO_ECDSA=m,
- CONFIG_LZ4_COMPRESS=m, CONFIG_LZ4HC_COMPRESS=m, CONFIG_ZSTD_COMPRESS=m,
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
- CONFIG_HSA_AMD=y https://elrepo.org/bugs/view.php?id=1091]

* Sun May 02 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.1-1
- Updated with the 5.12.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.12.1]

* Sun Apr 25 2021 Alan Bartlett <ajb@elrepo.org> - 5.12.0-1
- Updated with the 5.12 source tarball.
- CONFIG_LD_IS_BFD=y, CONFIG_LD_VERSION=23200, CONFIG_ACPI_PLATFORM_PROFILE=m,
- CONFIG_KVM_XEN=y, CONFIG_ARCH_SUPPORTS_LTO_CLANG=y,
- CONFIG_ARCH_SUPPORTS_LTO_CLANG_THIN=y, CONFIG_LTO_NONE=y,
- CONFIG_HAVE_IRQ_EXIT_ON_IRQ_STACK=y, CONFIG_HAVE_SOFTIRQ_ON_OWN_STACK=y,
- CONFIG_HAVE_PREEMPT_DYNAMIC=y, CONFIG_ARCH_HAS_ELFCORE_COMPAT=y,
- CONFIG_IP_VS_TWOS=m, CONFIG_SOCK_RX_QUEUE_MAPPING=y, CONFIG_XILINX_EMACLITE=m,
- CONFIG_MT76_CONNAC_LIB=m, CONFIG_MT7921E=m, CONFIG_TCG_TIS_I2C_CR50=m,
- CONFIG_SENSORS_AHT10=m, CONFIG_SENSORS_TPS23861=m, CONFIG_VIDEO_TW5864=m,
- CONFIG_DVB_MXL692=m, CONFIG_SND_INTEL_SOUNDWIRE_ACPI=m,
- CONFIG_SND_SOC_RT5659=m, CONFIG_SND_SOC_LPASS_RX_MACRO=m,
- CONFIG_SND_SOC_LPASS_TX_MACRO=m, CONFIG_USB_SERIAL_WISHBONE=m,
- CONFIG_USB_SERIAL_XR=m, CONFIG_LEDS_TRIGGER_TTY=m, CONFIG_LEDS_BLINK=y,
- CONFIG_VIRTIO_PCI_LIB=m, CONFIG_X86_PLATFORM_DRIVERS_DELL=y,
- CONFIG_IOMMU_IO_PGTABLE=y, CONFIG_ALTERA_FREEZE_BRIDGE=m,
- CONFIG_FPGA_DFL_NIOS_INTEL_PAC_N3000=m, CONFIG_F2FS_FS_LZ4HC=y,
- CONFIG_NFS_V4_2_SSC_HELPER=m, CONFIG_LZ4HC_COMPRESS=y,
- CONFIG_DEBUG_INFO_DWARF_TOOLCHAIN_DEFAULT=y, CONFIG_HAVE_ARCH_KFENCE=y,
- CONFIG_HAVE_OBJTOOL_MCOUNT=y and CONFIG_FTRACE_MCOUNT_USE_CC=y

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
- CONFIG_CAN_M_CAN_PCI=m, CONFIG_AUXILIARY_BUS=y,
- CONFIG_MHI_BUS_PCI_GENERIC=m,
- CONFIG_MTD_SPI_NOR_SWP_DISABLE_ON_VOLATILE=y,
- CONFIG_ZRAM_DEF_COMP_LZORLE=y, CONFIG_ZRAM_DEF_COMP="lzo-rle",
- CONFIG_MHI_NET=m, CONFIG_USB_RTL8153_ECM=m,
- CONFIG_PINCTRL_ALDERLAKE=m, CONFIG_PINCTRL_ELKHARTLAKE=m,
- CONFIG_PINCTRL_LAKEFIELD=m, CONFIG_SENSORS_CORSAIR_PSU=m,
- CONFIG_SENSORS_LTC2992=m, CONFIG_SENSORS_MAX127=m,
- CONFIG_SENSORS_PM6764TR=m, CONFIG_SENSORS_Q54SJ108A2=m,
- CONFIG_SENSORS_SBTSI=m, CONFIG_SND_SOC_ADI=m,
- CONFIG_SND_SOC_ADI_AXI_I2S=m, CONFIG_SND_SOC_ADI_AXI_SPDIF=m,
- CONFIG_SND_SOC_FSL_XCVR=m, CONFIG_SND_SOC_ADAU1372=m,
- CONFIG_SND_SOC_ADAU1372_I2C=m, CONFIG_SND_SOC_ADAU1372_SPI=m,
- CONFIG_SND_SOC_PCM5102A=m, CONFIG_SND_SOC_SIMPLE_MUX=m,
- CONFIG_SND_SOC_NAU8315=m, CONFIG_SND_SOC_LPASS_WSA_MACRO=m,
- CONFIG_SND_SOC_LPASS_VA_MACRO=m, CONFIG_AMD_SFH_HID=m,
- CONFIG_LEDS_CLASS_FLASH=m, CONFIG_LEDS_CLASS_MULTICOLOR=m,
- CONFIG_LEDS_AS3645A=m, CONFIG_LEDS_LM3601X=m,
- CONFIG_LEDS_SGM3140=m, CONFIG_LEDS_RT8515=m,
- CONFIG_EDAC_IGEN6=m, CONFIG_UV_SYSFS=m, CONFIG_AMD_PMC=m,
- CONFIG_DELL_WMI_SYSMAN=m, CONFIG_I2C_MULTI_INSTANTIATE=m,
- CONFIG_INTEL_UNCORE_FREQ_CONTROL=m, CONFIG_INTEL_PMT_CLASS=m,
- CONFIG_INTEL_PMT_TELEMETRY=m, CONFIG_INTEL_PMT_CRASHLOG=m,
- CONFIG_PSTORE_DEFAULT_KMSG_BYTES=10240,
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
- CONFIG_RANDOMIZE_BASE=y, CONFIG_X86_NEED_RELOCS=y,
- CONFIG_DYNAMIC_MEMORY_LAYOUT=y, CONFIG_RANDOMIZE_MEMORY=y
- and CONFIG_RANDOMIZE_MEMORY_PHYSICAL_PADDING=0xa
- [https://elrepo.org/bugs/view.php?id=1068]

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
- CONFIG_LLD_VERSION=0, CONFIG_TASKS_TRACE_RCU=y,
- CONFIG_LD_ORPHAN_WARN=y, CONFIG_ACPI_DPTF=y,
- CONFIG_DPTF_PCH_FIVR=m, CONFIG_HAVE_ARCH_SECCOMP=y,
- CONFIG_HAVE_STATIC_CALL=y, CONFIG_HAVE_STATIC_CALL_INLINE=y,
- CONFIG_ARCH_WANT_LD_ORPHAN_WARN=y, CONFIG_VMAP_PFN=y,
- CONFIG_QRTR=m, CONFIG_QRTR_MHI=m, CONFIG_CAN_MCP251XFD=m,
- CONFIG_PCIE_BUS_DEFAULT=y, CONFIG_MHI_BUS=m,
- CONFIG_LATTICE_ECP3_CONFIG=m, CONFIG_CHELSIO_INLINE_CRYPTO=y,
- CONFIG_PCS_XPCS=m, CONFIG_ATH11K=m, CONFIG_ATH11K_PCI=m,
- CONFIG_JOYSTICK_ADC=m, CONFIG_TOUCHSCREEN_AUO_PIXCIR=m,
- CONFIG_TOUCHSCREEN_CY8CTMG110=m, CONFIG_TOUCHSCREEN_TI_AM335X_TSC=m,
- CONFIG_TOUCHSCREEN_MC13783=m, CONFIG_TOUCHSCREEN_ZFORCE=m,
- CONFIG_TOUCHSCREEN_IQS5XX=m, CONFIG_TOUCHSCREEN_ZINITIX=m,
- CONFIG_HW_RANDOM_XIPHERA=m, CONFIG_PINCTRL_INTEL=y,
- CONFIG_GPIO_CDEV=y, CONFIG_GPIO_CDEV_V1=y, CONFIG_SENSORS_MR75203=m,
- CONFIG_SENSORS_ADM1266=m, CONFIG_SENSORS_MP2975=m,
- CONFIG_REGULATOR_RASPBERRYPI_TOUCHSCREEN_ATTINY=m,
- CONFIG_REGULATOR_RT4801=m, CONFIG_REGULATOR_RTMV20=m,
- CONFIG_BACKLIGHT_KTD253=m, CONFIG_SND_SOC_INTEL_CATPT=m,
- CONFIG_SND_SOC_CS4234=m, CONFIG_SND_SOC_TAS2764=m,
- CONFIG_HID_VIVALDI=m, CONFIG_LEDS_APU=m, CONFIG_LEDS_LP50XX=m,
- CONFIG_LEDS_TRIGGER_ACTIVITY=m, CONFIG_LEDS_TRIGGER_NETDEV=m,
- CONFIG_LEDS_TRIGGER_PATTERN=m, CONFIG_RTC_DRV_RV3032=m,
- CONFIG_VIRTIO_DMA_SHARED_BUFFER=m, CONFIG_QCOM_QMI_HELPERS=m,
- CONFIG_IIO_BUFFER_DMA=m, CONFIG_IIO_BUFFER_DMAENGINE=m,
- CONFIG_IIO_BUFFER_HW_CONSUMER=m, CONFIG_IIO_SW_DEVICE=m,
- CONFIG_IIO_SW_TRIGGER=m, CONFIG_IIO_TRIGGERED_EVENT=m,
- CONFIG_USB_LGM_PHY=m, CONFIG_PHY_CPCAP_USB=m,
- CONFIG_PHY_INTEL_LGM_EMMC=m, CONFIG_XFS_SUPPORT_V4=y,
- CONFIG_FUSE_DAX=y, CONFIG_CRYPTO_SM2=m,
- CONFIG_CRYPTO_USER_API_ENABLE_OBSOLETE=y and CONFIG_KGDB_HONOUR_BLOCKLIST=y

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
- CONFIG_MDIO_DEVRES=y, CONFIG_MT76_SDIO=m,
- CONFIG_MT7663_USB_SDIO_COMMON=m, CONFIG_MT7663S=m,
- CONFIG_WLAN_VENDOR_MICROCHIP=y, CONFIG_RTW88_8821C=m,
- CONFIG_RTW88_8821CE=m, CONFIG_HW_RANDOM_BA431=m,
- CONFIG_PINCTRL_EMMITSBURG=m, CONFIG_GPIO_PCA9570=m,
- CONFIG_SENSORS_CORSAIR_CPRO=m, CONFIG_THERMAL_NETLINK=y,
- CONFIG_REGULATOR_PCA9450=m, CONFIG_RC_XBOX_DVD=m,
- CONFIG_IR_TOY=m, CONFIG_CEC_CH7322=m, CONFIG_SND_HDA_GENERIC_LEDS=y,
- CONFIG_SND_SOC_MAX98373_I2C=m, CONFIG_XILINX_ZYNQMP_DPDMA=m,
- CONFIG_MLX5_VDPA=y, CONFIG_MLX5_VDPA_NET=m,
- CONFIG_XEN_UNPOPULATED_ALLOC=y, CONFIG_INTEL_ATOMISP2_LED=m,
- CONFIG_INTEL_ATOMISP2_PM=m, CONFIG_DECOMPRESS_ZSTD=y,
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

* Wed Sep 09 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.8-1
- Updated with the 5.8.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.8]

* Sun Sep 06 2020 Alan Bartlett <ajb@elrepo.org> - 5.8.7-1
- Updated with the 5.8.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.8.7]
- CONFIG_IEEE802154_HWSIM=m
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
- CONFIG_CC_VERSION_TEXT="gcc (GCC) 9.3.1 20200408 (Red Hat 9.3.1-2)",
- CONFIG_DEFAULT_INIT="", CONFIG_TASKS_RCU_GENERIC=y,
- CONFIG_TASKS_RUDE_RCU=y, CONFIG_HIBERNATION_SNAPSHOT_DEV=y,
- CONFIG_EFI_GENERIC_STUB_INITRD_CMDLINE_LOADER=y,
- CONFIG_AS_TPAUSE=y, CONFIG_XFRM_AH=m, CONFIG_XFRM_ESP=m,
- CONFIG_NET_ACT_GATE=m, CONFIG_BCM54140_PHY=m, CONFIG_MT7603E=m,
- CONFIG_MT7615_COMMON=m, CONFIG_MT7663U=m, CONFIG_MT7915E=m,
- CONFIG_RTW88_8822B=m, CONFIG_RTW88_8822C=m, CONFIG_RTW88_8723D=m,
- CONFIG_RTW88_8822BE=m, CONFIG_RTW88_8822CE=m, CONFIG_RTW88_8723DE=m,
- CONFIG_TOUCHSCREEN_CY8CTMA140=m, CONFIG_PINCTRL_MCP23S08_I2C=m,
- CONFIG_PINCTRL_MCP23S08_SPI=m, CONFIG_PINCTRL_JASPERLAKE=m,
- CONFIG_SENSORS_AMD_ENERGY=m, CONFIG_SENSORS_MAX16601=m,
- CONFIG_REGULATOR_MAX77826=m, CONFIG_CEC_SECO=m,
- CONFIG_MEDIA_SUPPORT_FILTER=y, CONFIG_VIDEO_V4L2_SUBDEV_API=y,
- CONFIG_VIDEO_IPU3_CIO2=m, CONFIG_VIDEO_TDA1997X=m,
- CONFIG_VIDEO_TLV320AIC23B=m, CONFIG_VIDEO_ADV7180=m,
- CONFIG_VIDEO_ADV7183=m, CONFIG_VIDEO_ADV7604=m,
- CONFIG_VIDEO_ADV7604_CEC=y, CONFIG_VIDEO_ADV7842=m,
- CONFIG_VIDEO_ADV7842_CEC=y, CONFIG_VIDEO_BT819=m,
- CONFIG_VIDEO_BT856=m, CONFIG_VIDEO_BT866=m,
- CONFIG_VIDEO_KS0127=m, CONFIG_VIDEO_ML86V7667=m,
- CONFIG_VIDEO_SAA7110=m, CONFIG_VIDEO_TC358743=m,
- CONFIG_VIDEO_TC358743_CEC=y, CONFIG_VIDEO_TVP514X=m,
- CONFIG_VIDEO_TVP7002=m, CONFIG_VIDEO_TW9910=m,
- CONFIG_VIDEO_VPX3220=m, CONFIG_DRM_I915_FENCE_TIMEOUT=10000,
- CONFIG_SND_SOC_AMD_RENOIR=m, CONFIG_SND_SOC_AMD_RENOIR_MACH=m,
- CONFIG_SND_SOC_FSL_EASRC=m, CONFIG_SND_SOC_MAX98390=m,
- CONFIG_SND_SOC_ZL38060=m, CONFIG_USB_CHIPIDEA_MSM=m,
- CONFIG_USB_CHIPIDEA_GENERIC=m, CONFIG_INFINIBAND_RTRS=m,
- CONFIG_INFINIBAND_RTRS_CLIENT=m, CONFIG_INFINIBAND_RTRS_SERVER=m,
- CONFIG_VIRTIO_MEM=m, CONFIG_INTEL_WMI_SBL_FW_UPDATE=m,
- CONFIG_F2FS_FS_LZORLE=y, CONFIG_LINEAR_RANGES=y,
- CONFIG_ARCH_USE_SYM_ANNOTATIONS=y, CONFIG_DYNAMIC_DEBUG_CORE=y,
- CONFIG_ARCH_HAS_EARLY_DEBUG=y, CONFIG_ARCH_HAS_DEBUG_WX=y,
- CONFIG_ARCH_HAS_DEBUG_VM_PGTABLE=y,
- CONFIG_CC_HAS_WORKING_NOSANITIZE_ADDRESS=y and CONFIG_HAVE_ARCH_KCSAN=y

* Fri Jul 31 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.12-1
- Updated with the 5.7.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.12]

* Wed Jul 29 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.11-1
- Updated with the 5.7.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.11]

* Wed Jul 22 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.10-1
- Updated with the 5.7.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.10]
- Enhanced the specification file to allow the kernel-ml
- package set to be built, using an updated gcc version from
- the Red Hat devtoolset-9 package, following an upstream
- increase in the minimum gcc version requirement.
- [https://elrepo.org/bugs/view.php?id=1023]

* Thu Jul 16 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.9-1
- Updated with the 5.7.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.9]
- CONFIG_USBIP_CORE=m, CONFIG_USBIP_VHCI_HCD=m,
- CONFIG_USBIP_VHCI_HC_PORTS=8, CONFIG_USBIP_VHCI_NR_HCS=1,
- CONFIG_USBIP_HOST=m and CONFIG_USBIP_VUDC=m
- [https://elrepo.org/bugs/view.php?id=1019]

* Wed Jul 08 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.8-1
- Updated with the 5.7.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.8]
- CONFIG_NILFS2_FS=m, CONFIG_F2FS_FS_SECURITY=y,
- CONFIG_F2FS_FS_COMPRESSION=y, CONFIG_F2FS_FS_LZO=y,
- CONFIG_F2FS_FS_LZ4=y, CONFIG_F2FS_FS_ZSTD=y, CONFIG_ZONEFS_FS=m,
- CONFIG_LZ4_COMPRESS=y, CONFIG_ZSTD_COMPRESS=y and
- CONFIG_ZSTD_DECOMPRESS=y
- [https://elrepo.org/bugs/view.php?id=1018]

* Wed Jul 01 2020 Alan Bartlett <ajb@elrepo.org> - 5.7.7-1
- Updated with the 5.7.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.7]
- Added a triggerin scriptlet to rebuild the initramfs image
- when the system microcode package is updated.
- [https://elrepo.org/bugs/view.php?id=1012]

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
- CONFIG_LD_VERSION=227000000, CONFIG_HARDIRQS_SW_RESEND=y,
- CONFIG_HAVE_ARCH_USERFAULTFD_WP=y, CONFIG_AS_AVX512=y,
- CONFIG_AS_SHA1_NI=y, CONFIG_AS_SHA256_NI=y,
- CONFIG_NUMA_KEEP_MEMINFO=y, CONFIG_PAGE_REPORTING=y,
- CONFIG_ZSWAP_COMPRESSOR_DEFAULT_LZO=y,
- CONFIG_ZSWAP_COMPRESSOR_DEFAULT="lzo",
- CONFIG_ZSWAP_ZPOOL_DEFAULT_ZBUD=y,
- CONFIG_ZSWAP_ZPOOL_DEFAULT="zbud",
- CONFIG_SATA_HOST=y, CONFIG_PATA_TIMINGS=y, CONFIG_ATA_FORCE=y,
- CONFIG_BAREUDP=m, CONFIG_DWMAC_INTEL=m, CONFIG_MDIO_XPCS=m,
- CONFIG_SERIAL_SPRD=m, CONFIG_SENSORS_AXI_FAN_CONTROL=m,
- CONFIG_SENSORS_W83795_FANCTRL=y,
- CONFIG_DRM_I915_MAX_REQUEST_BUSYWAIT=8000,
- CONFIG_TINYDRM_ILI9486=m, CONFIG_SND_BCM63XX_I2S_WHISTLER=m,
- CONFIG_SND_SOC_TLV320ADCX140=m, CONFIG_APPLE_MFI_FASTCHARGE=m,
- CONFIG_MMC_HSQ=m, CONFIG_VIRTIO_VDPA=m, CONFIG_VDPA=m,
- CONFIG_IFCVF=m, CONFIG_VHOST_IOTLB=m, CONFIG_VHOST_DPN=y,
- CONFIG_VHOST_MENU=y, CONFIG_VHOST_VDPA=m,
- CONFIG_SURFACE_3_POWER_OPREGION=m, CONFIG_AL3010=m,
- CONFIG_EXFAT_FS=m, CONFIG_EXFAT_DEFAULT_IOCHARSET="utf8" and
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
- CONFIG_SND_SOC_FSL_ASRC=m, CONFIG_SND_SOC_FSL_SAI=m,
- CONFIG_SND_SOC_FSL_MQS=m, CONFIG_SND_SOC_FSL_AUDMIX=m,
- CONFIG_SND_SOC_FSL_SSI=m, CONFIG_SND_SOC_FSL_SPDIF=m,
- CONFIG_SND_SOC_FSL_ESAI=m, CONFIG_SND_SOC_FSL_MICFIL=m,
- CONFIG_SND_SOC_IMX_AUDMUX=m, CONFIG_SND_SOC_MTK_BTCVSD=m,
- CONFIG_SND_SOC_XILINX_AUDIO_FORMATTER=m and
- CONFIG_SND_SOC_XILINX_SPDIF=m

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
- Updated with the 5.6 source tarball.
- CONFIG_BUILDTIME_TABLE_SORT=y, CONFIG_TIME_NS=y,
- CONFIG_ARCH_WANT_DEFAULT_BPF_JIT=y, CONFIG_BPF_JIT_DEFAULT_ON=y,
- CONFIG_IA32_FEAT_CTL=y, CONFIG_X86_VMX_FEATURE_NAMES=y,
- CONFIG_MMU_GATHER_TABLE_FREE=y, CONFIG_MMU_GATHER_RCU_TABLE_FREE=y,
- CONFIG_BLK_DEV_INTEGRITY_T10=m, CONFIG_NET_SCH_FQ_PIE=m,
- CONFIG_NET_SCH_ETS=m, CONFIG_VSOCKETS_LOOPBACK=m,
- CONFIG_ETHTOOL_NETLINK=y, CONFIG_WIREGUARD=m, CONFIG_BCM84881_PHY=y,
- CONFIG_ISDN_CAPI=y, CONFIG_CAPI_TRACE=y, CONFIG_PINCTRL_LYNXPOINT=m,
- CONFIG_SENSORS_ADM1177=m, CONFIG_SENSORS_DRIVETEMP=m,
- CONFIG_SENSORS_MAX31730=m, CONFIG_SENSORS_MAX20730=m,
- CONFIG_SENSORS_XDPE122=m, CONFIG_REGULATOR_MP8859=m,
- CONFIG_DRM_AMD_DC_DCN=y, CONFIG_SND_PCSP=m, CONFIG_SND_DUMMY=m,
- CONFIG_SND_HDA_PREALLOC_SIZE=0, CONFIG_SND_SOC_INTEL_BDW_RT5650_MACH=m,
- CONFIG_SND_SOC_MT6660=m, CONFIG_LEDS_TPS6105X=m, CONFIG_INTEL_IDXD=m,
- CONFIG_PLX_DMA=m, CONFIG_IOASID=y, CONFIG_PHY_INTEL_EMMC=m,
- CONFIG_NFS_DISABLE_UDP_SUPPORT=y, CONFIG_SECURITY_SELINUX_SIDTAB_HASH_BITS=9,
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
- Updated with the 5.5 source tarball.
- CONFIG_IRQ_MSI_IOMMU=y, CONFIG_CC_HAS_INT128=y,
- CONFIG_X86_IOPL_IOPERM=y, CONFIG_X86_UMIP=y,
- CONFIG_BLK_CGROUP_RWSTAT=y, CONFIG_MAPPING_DIRTY_HELPERS=y,
- CONFIG_FW_CACHE=y, CONFIG_NVME_HWMON=y, CONFIG_DP83869_PHY=m,
- CONFIG_PINCTRL_TIGERLAKE=m, CONFIG_SENSORS_LTC2947=m,
- CONFIG_SENSORS_LTC2947_I2C=m, CONFIG_SENSORS_LTC2947_SPI=m,
- CONFIG_SENSORS_BEL_PFE=m, CONFIG_SENSORS_TMP513=m,
- CONFIG_DRM_TTM_DMA_PAGE_POOL=y, CONFIG_DRM_TTM_HELPER=m,
- CONFIG_DRM_I915_HEARTBEAT_INTERVAL=2500,
- CONFIG_DRM_I915_PREEMPT_TIMEOUT=640,
- CONFIG_DRM_I915_STOP_TIMEOUT=100,
- CONFIG_DRM_I915_TIMESLICE_DURATION=1,
- CONFIG_BACKLIGHT_QCOM_WLED=m, CONFIG_SND_INTEL_NHLT=y,
- CONFIG_SND_INTEL_DSP_CONFIG=m,
- CONFIG_SND_SOC_INTEL_BXT_DA7219_MAX98357A_COMMON=m,
- CONFIG_SND_SOC_ADAU7118=m, CONFIG_SND_SOC_ADAU7118_HW=m,
- CONFIG_SND_SOC_ADAU7118_I2C=m, CONFIG_SND_SOC_TAS2562=m,
- CONFIG_SND_SOC_TAS2770=m, CONFIG_SF_PDMA=m,
- CONFIG_SYSTEM76_ACPI=m, CONFIG_IOMMU_DMA=y, CONFIG_IO_WQ=y,
- CONFIG_CRYPTO_SKCIPHER=y, CONFIG_CRYPTO_SKCIPHER2=y,
- CONFIG_CRYPTO_CURVE25519=m, CONFIG_CRYPTO_CURVE25519_X86=m,
- CONFIG_CRYPTO_BLAKE2B=m, CONFIG_CRYPTO_BLAKE2S=m,
- CONFIG_CRYPTO_BLAKE2S_X86=m, CONFIG_CRYPTO_ARCH_HAVE_LIB_BLAKE2S=m,
- CONFIG_CRYPTO_LIB_BLAKE2S_GENERIC=m, CONFIG_CRYPTO_LIB_BLAKE2S=m,
- CONFIG_CRYPTO_ARCH_HAVE_LIB_CHACHA=m,
- CONFIG_CRYPTO_LIB_CHACHA_GENERIC=m, CONFIG_CRYPTO_LIB_CHACHA=m,
- CONFIG_CRYPTO_ARCH_HAVE_LIB_CURVE25519=m,
- CONFIG_CRYPTO_LIB_CURVE25519_GENERIC=m,
- CONFIG_CRYPTO_LIB_CURVE25519=m, CONFIG_CRYPTO_LIB_POLY1305_RSIZE=4,
- CONFIG_CRYPTO_ARCH_HAVE_LIB_POLY1305=m,
- CONFIG_CRYPTO_LIB_POLY1305_GENERIC=m, CONFIG_CRYPTO_LIB_POLY1305=m,
- CONFIG_CRYPTO_LIB_CHACHA20POLY1305=m,
- CONFIG_CRYPTO_DEV_AMLOGIC_GXL=m, CONFIG_MEMREGION=y,
- CONFIG_SYMBOLIC_ERRNAME=y, CONFIG_HAVE_ARCH_KASAN_VMALLOC=y,
- CONFIG_HAVE_DYNAMIC_FTRACE_WITH_DIRECT_CALLS=y and
- CONFIG_DYNAMIC_FTRACE_WITH_DIRECT_CALLS=y

* Sun Jan 26 2020 Alan Bartlett <ajb@elrepo.org> - 5.4.15-1
- Updated with the 5.4.15 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.15]

* Thu Jan 23 2020 Alan Bartlett <ajb@elrepo.org> - 5.4.14-1
- Updated with the 5.4.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.14]

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
- CONFIG_DRM_RADEON_USERPTR=y
- [https://elrepo.org/bugs/view.php?id=972]

* Mon Nov 25 2019 Alan Bartlett <ajb@elrepo.org> - 5.4.0-1
- Updated with the 5.4 source tarball.
- CONFIG_ARCH_CPUIDLE_HALTPOLL=y, CONFIG_HALTPOLL_CPUIDLE=y,
- CONFIG_HAVE_ASM_MODVERSIONS=y, CONFIG_ASM_MODVERSIONS=y,
- CONFIG_HMM_MIRROR=y, CONFIG_NET_TC_SKB_EXT=y,
- CONFIG_CAN_J1939=m, CONFIG_CAN_KVASER_PCIEFD=m,
- CONFIG_CAN_M_CAN_PLATFORM=m, CONFIG_CAN_M_CAN_TCAN4X5X=m,
- CONFIG_CAN_F81601=m, CONFIG_PCI_HYPERV_INTERFACE=m,
- CONFIG_NET_VENDOR_PENSANDO=y, CONFIG_IONIC=m, CONFIG_ADIN_PHY=m,
- CONFIG_ATH9K_PCI_NO_EEPROM=m, CONFIG_JOYSTICK_FSIA6B=m,
- CONFIG_SERIAL_8250_DWLIB=y, CONFIG_SERIAL_FSL_LINFLEXUART=m,
- CONFIG_SPI_MEM=y, CONFIG_SENSORS_AS370=m,
- CONFIG_SENSORS_INSPUR_IPSPS=m, CONFIG_VIDEO_V4L2_I2C=y,
- CONFIG_DRM_MIPI_DBI=m, CONFIG_DRM_GEM_CMA_HELPER=y,
- CONFIG_DRM_KMS_CMA_HELPER=y, CONFIG_DRM_AMDGPU_USERPTR=y,
- CONFIG_DRM_AMD_DC_DCN2_1=y, CONFIG_TINYDRM_HX8357D=m,
- CONFIG_TINYDRM_ILI9225=m, CONFIG_TINYDRM_ILI9341=m,
- CONFIG_TINYDRM_MI0283QT=m, CONFIG_TINYDRM_REPAPER=m,
- CONFIG_TINYDRM_ST7586=m, CONFIG_TINYDRM_ST7735R=m,
- CONFIG_SND_INTEL_NHLT=m,
- CONFIG_SND_SOC_INTEL_DA7219_MAX98357A_GENERIC=m,
- CONFIG_SND_SOC_UDA1334=m, CONFIG_USB_ROLE_SWITCH=m,
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

* Mon Oct 07 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.5-1
- Updated with the 5.3.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.5]

* Sat Oct 05 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.4-1
- Updated with the 5.3.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.4]
- Note: There was no linux-5.3.3 release due to an upstream
- developer "mishap". Details can be seen via the following link:
- https://lore.kernel.org/lkml/20191001070738.GC2893807@kroah.com/

* Tue Oct 01 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.2-1
- Updated with the 5.3.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.2]
- CONFIG_NVME_MULTIPATH=y [https://elrepo.org/bugs/view.php?id=945]
- CONFIG_NVME_CORE=m [https://elrepo.org/bugs/view.php?id=946]

* Sat Sep 21 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.1-1
- Updated with the 5.3.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.1]

* Mon Sep 16 2019 Alan Bartlett <ajb@elrepo.org> - 5.3.0-1
- Updated with the 5.3 source tarball.
- CONFIG_CC_CAN_LINK=y, CONFIG_X86_HV_CALLBACK_VECTOR=y,
- CONFIG_CPU_SUP_ZHAOXIN=y, CONFIG_HAVE_KVM_NO_POLL=y,
- CONFIG_HAVE_FAST_GUP=y, CONFIG_ARCH_HAS_PTE_DEVMAP=y,
- CONFIG_NFT_SYNPROXY=m, CONFIG_NF_TABLES_BRIDGE=m,
- CONFIG_NFT_BRIDGE_META=m, CONFIG_NF_CONNTRACK_BRIDGE=m,
- CONFIG_NET_ACT_MPLS=m, CONFIG_NET_ACT_CTINFO=m,
- CONFIG_NET_ACT_CT=m, CONFIG_BT_HCIBTUSB_MTK=y,
- CONFIG_FW_LOADER_PAGED_BUF=y, CONFIG_NET_VENDOR_GOOGLE=y,
- CONFIG_GVE=m, CONFIG_XILINX_AXI_EMAC=m, CONFIG_MDIO_I2C=m,
- CONFIG_PHYLINK=m, CONFIG_SFP=m, CONFIG_NXP_TJA11XX_PHY=m,
- CONFIG_MISDN_HDLC=m, CONFIG_JOYSTICK_IFORCE_USB=m,
- CONFIG_JOYSTICK_IFORCE_232=m, CONFIG_SERIAL_MCTRL_GPIO=y,
- CONFIG_POWER_SUPPLY_HWMON=y, CONFIG_SENSORS_NPCM7XX=m,
- CONFIG_SENSORS_IRPS5401=m, CONFIG_SENSORS_PXE1610=m,
- CONFIG_WATCHDOG_OPEN_TIMEOUT=0, CONFIG_REGULATOR_SLG51000=m,
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
- CONFIG_PROC_PID_ARCH_STATUS=y, CONFIG_KEYS_REQUEST_CACHE=y,
- CONFIG_CRYPTO_XXHASH=m, CONFIG_CRYPTO_LIB_ARC4=m,
- CONFIG_CRYPTO_DEV_ATMEL_I2C=m, CONFIG_CRYPTO_DEV_ATMEL_ECC=m,
- CONFIG_CRYPTO_DEV_ATMEL_SHA204A=m, CONFIG_DIMLIB=y,
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

* Fri Aug 16 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.9-1
- Updated with the 5.2.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.9]

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

* Sun Jul 14 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.1-1
- Updated with the 5.2.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2.1]

* Mon Jul 08 2019 Alan Bartlett <ajb@elrepo.org> - 5.2.0-1
- Updated with the 5.2 source tarball.
- CONFIG_ARCH_HAS_SET_DIRECT_MAP=y, CONFIG_CONTIG_ALLOC=y,
- CONFIG_ARCH_HAS_HMM_MIRROR=y, CONFIG_ARCH_HAS_HMM_DEVICE=y,
- CONFIG_NETFILTER_XT_TARGET_MASQUERADE=m, CONFIG_BT_MTKSDIO=m,
- CONFIG_NET_DEVLINK=y, CONFIG_NET_VENDOR_XILINX=y,
- CONFIG_XILINX_LL_TEMAC=m, CONFIG_AX88796B_PHY=m,
- CONFIG_MT7615E=m, CONFIG_RTW88=m, CONFIG_RTW88_CORE=m,
- CONFIG_RTW88_PCI=m, CONFIG_RTW88_8822BE=y, CONFIG_RTW88_8822CE=y,
- CONFIG_I2C_AMD_MP2=m, CONFIG_SENSORS_IR38064=m, CONFIG_SENSORS_ISL68137=m,
- CONFIG_HPWDT_NMI_DECODING=y, CONFIG_MEDIA_CONTROLLER=y,
- CONFIG_MEDIA_CONTROLLER_DVB=y, CONFIG_DRM_GEM_SHMEM_HELPER=y,
- CONFIG_SND_USB_AUDIO_USE_MEDIA_CONTROLLER=y, CONFIG_LEDS_LM3532=m,
- CONFIG_INFINIBAND_EFA=m, CONFIG_NVMEM_SYSFS=y,
- CONFIG_INIT_STACK_NONE=y, CONFIG_CRYPTO_RSA=y, CONFIG_CRYPTO_DH=m,
- CONFIG_CRYPTO_ECC=m, CONFIG_CRYPTO_ECDH=m, CONFIG_CRYPTO_ECRDSA=m,
- CONFIG_CORDIC=m, CONFIG_RATIONAL=y, CONFIG_ARCH_STACKWALK=y,
- CONFIG_OPTIMIZE_INLINING=y and CONFIG_DEBUG_MISC=y

* Wed Jul 03 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.16-1
- Updated with the 5.1.16 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.16]

* Tue Jun 25 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.15-1
- Updated with the 5.1.15 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.15]

* Sat Jun 22 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.14-1
- Updated with the 5.1.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.14]

* Sat Jun 22 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.13-1
- Updated with the 5.1.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.13]
- Not released due to a patch being missing from the upstream
- stable tree. [https://lkml.org/lkml/2019/6/21/875]

* Wed Jun 19 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.12-1
- Updated with the 5.1.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.12]

* Mon Jun 17 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.11-1
- Updated with the 5.1.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.11]

* Sat Jun 15 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.10-1
- Updated with the 5.1.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.10]

* Tue Jun 11 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.9-1
- Updated with the 5.1.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.9]

* Sun Jun 09 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.8-1
- Updated with the 5.1.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.8]

* Tue Jun 04 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.7-1
- Updated with the 5.1.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.7]
- Added NO_LIBZSTD=1 directive to the %%global perf_make line.

* Fri May 31 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.6-1
- Updated with the 5.1.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.6]

* Sat May 25 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.5-1
- Updated with the 5.1.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.5]

* Wed May 22 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.4-1
- Updated with the 5.1.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.4]

* Thu May 16 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.3-1
- Updated with the 5.1.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.3]
- Purge the source tree of all unrequired dot-files.
- [https://elrepo.org/bugs/view.php?id=912]

* Tue May 14 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.2-1
- Updated with the 5.1.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.2]

* Sat May 11 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.1-1
- Updated with the 5.1.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.1.1]

* Mon May 06 2019 Alan Bartlett <ajb@elrepo.org> - 5.1.0-1
- Updated with the 5.1 source tarball.
- CONFIG_CC_HAS_WARN_MAYBE_UNINITIALIZED=y,
- CONFIG_CC_DISABLE_WARN_MAYBE_UNINITIALIZED=y,
- CONFIG_CONTEXT_TRACKING=y, CONFIG_IO_URING=y,
- CONFIG_EFI_EARLYCON=y, CONFIG_ARCH_USE_MEMREMAP_PROT=y,
- CONFIG_UNIX_SCM=y, CONFIG_NF_CT_PROTO_GRE=y,
- CONFIG_NF_NAT_MASQUERADE=y, CONFIG_IPVLAN_L3S=y,
- CONFIG_IPMI_PLAT_DATA=y, CONFIG_IR_RCMM_DECODER=m,
- CONFIG_SND_SOC_CS35L36=m, CONFIG_SND_SOC_CS4341=m,
- CONFIG_SND_SOC_RK3328=m, CONFIG_SND_SOC_WM8904=m,
- CONFIG_SND_SOC_MT6358=m, CONFIG_USB_AUTOSUSPEND_DELAY=2,
- CONFIG_INFINIBAND_BNXT_RE=m, CONFIG_INFINIBAND_HFI1=m,
- CONFIG_INFINIBAND_QEDR=m, CONFIG_INFINIBAND_RDMAVT=m,
- CONFIG_RDMA_RXE=m, CONFIG_EDAC_I10NM=m, CONFIG_RTC_DRV_ABEOZ9=m,
- CONFIG_RTC_DRV_RV3028=m, CONFIG_RTC_DRV_SD3078=m,
- CONFIG_CHARLCD_BL_FLASH=y, CONFIG_IOMMU_IOVA=y,
- CONFIG_HYPERV_IOMMU=y, CONFIG_DEV_DAX_KMEM=m,
- CONFIG_DEV_DAX_PMEM_COMPAT=m, CONFIG_VALIDATE_FS_PARSER=y,
- CONFIG_LSM="yama,loadpin,safesetid,integrity,selinux,smack,tomoyo,apparmor",
- CONFIG_DMA_DECLARE_COHERENT=y and CONFIG_UBSAN_ALIGNMENT=y

* Sun May 05 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.13-1
- Updated with the 5.0.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.13]

* Sat May 04 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.12-1
- Updated with the 5.0.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.12]

* Thu May 02 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.11-1
- Updated with the 5.0.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.11]

* Sat Apr 27 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.10-1
- Updated with the 5.0.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.10]

* Sat Apr 20 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.9-1
- Updated with the 5.0.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.9]

* Wed Apr 17 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.8-1
- Updated with the 5.0.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.8]

* Fri Apr 05 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.7-1
- Updated with the 5.0.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.7]

* Wed Apr 03 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.6-1
- Updated with the 5.0.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.6]

* Wed Mar 27 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.5-1
- Updated with the 5.0.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.5]

* Sat Mar 23 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.4-1
- Updated with the 5.0.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.4]
- CONFIG_SQUASHFS_LZ4=y and CONFIG_SQUASHFS_ZSTD=y
- [https://elrepo.org/bugs/view.php?id=908]

* Tue Mar 19 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.3-1
- Updated with the 5.0.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.3]

* Wed Mar 13 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.2-1
- Updated with the 5.0.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.2]

* Sun Mar 10 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.1-1
- Updated with the 5.0.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.0.1]

* Tue Mar 05 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.0-2
- CONFIG_BLK_WBT=y, CONFIG_BLK_WBT_MQ=y,
- CONFIG_MQ_IOSCHED_DEADLINE=y, CONFIG_MQ_IOSCHED_KYBER=y,
- CONFIG_IOSCHED_BFQ=y and CONFIG_BFQ_GROUP_IOSCHED=y
- [https://elrepo.org/bugs/view.php?id=905]

* Mon Mar 04 2019 Alan Bartlett <ajb@elrepo.org> - 5.0.0-1
- Updated with the 5.0 source tarball.
- CONFIG_CC_HAS_ASM_GOTO=y, CONFIG_PVH=y, CONFIG_HAVE_MOVE_PMD=y,
- CONFIG_SKB_EXTENSIONS=y, CONFIG_HAVE_EISA=y, CONFIG_HAVE_PCI=y,
- CONFIG_NVME_TCP=m, CONFIG_NVME_TARGET_TCP=m,
- CONFIG_USB_NET_AQC111=m, CONFIG_QTNFMAC_PCIE=m,
- CONFIG_TQMX86_WDT=m, CONFIG_SND_SOC_AMD_ACP3x=m,
- CONFIG_SND_SOC_INTEL_SKL=m, CONFIG_SND_SOC_INTEL_APL=m,
- CONFIG_SND_SOC_INTEL_KBL=m, CONFIG_SND_SOC_INTEL_GLK=m,
- CONFIG_SND_SOC_INTEL_CNL=m, CONFIG_SND_SOC_INTEL_CFL=m,
- CONFIG_SND_SOC_INTEL_SKYLAKE_FAMILY=m,
- CONFIG_SND_SOC_INTEL_KBL_RT5660_MACH=m,
- CONFIG_SND_SOC_XILINX_I2S=m, CONFIG_SND_SOC_AK4118=m,
- CONFIG_SND_SOC_RT5660=m, CONFIG_LEDS_TRIGGER_AUDIO=m,
- CONFIG_XEN_FRONT_PGDIR_SHBUF=m, CONFIG_HUAWEI_WMI=m,
- CONFIG_NVDIMM_KEYS=y, CONFIG_CRYPTO_NHPOLY1305=m,
- CONFIG_CRYPTO_NHPOLY1305_SSE2=m, CONFIG_CRYPTO_NHPOLY1305_AVX2=m,
- CONFIG_CRYPTO_ADIANTUM=m, CONFIG_CRYPTO_STREEBOG=m,
- CONFIG_XXHASH=y, CONFIG_KASAN_STACK=1 and CONFIG_DYNAMIC_EVENTS=y

* Wed Feb 27 2019 Alan Bartlett <ajb@elrepo.org> - 4.20.13-1
- Updated with the 4.20.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.13]

* Sat Feb 23 2019 Alan Bartlett <ajb@elrepo.org> - 4.20.12-1
- Updated with the 4.20.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.12]

* Wed Feb 20 2019 Alan Bartlett <ajb@elrepo.org> - 4.20.11-1
- Updated with the 4.20.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.11]
- CONFIG_SND_SOC_AC97_BUS=y, CONFIG_SND_SOC_COMPRESS=y,
- CONFIG_SND_SOC_TOPOLOGY=y, CONFIG_SND_SOC_ACPI=m,
- CONFIG_SND_SOC_AMD_ACP=m,
- CONFIG_SND_SOC_AMD_CZ_DA7219MX98357_MACH=m,
- CONFIG_SND_SOC_AMD_CZ_RT5645_MACH=m,
- CONFIG_SND_ATMEL_SOC=m, CONFIG_SND_DESIGNWARE_PCM=y,
- CONFIG_SND_I2S_HI6210_I2S=m, CONFIG_SND_SOC_IMG=y,
- CONFIG_SND_SOC_IMG_I2S_IN=m, CONFIG_SND_SOC_IMG_I2S_OUT=m,
- CONFIG_SND_SOC_IMG_PARALLEL_OUT=m, CONFIG_SND_SOC_IMG_SPDIF_IN=m,
- CONFIG_SND_SOC_IMG_SPDIF_OUT=m,
- CONFIG_SND_SOC_IMG_PISTACHIO_INTERNAL_DAC=m,
- CONFIG_SND_SOC_INTEL_SST_TOPLEVEL=y, CONFIG_SND_SST_IPC=m,
- CONFIG_SND_SST_IPC_PCI=m, CONFIG_SND_SST_IPC_ACPI=m,
- CONFIG_SND_SOC_INTEL_SST_ACPI=m, CONFIG_SND_SOC_INTEL_SST=m,
- CONFIG_SND_SOC_INTEL_SST_FIRMWARE=m, CONFIG_SND_SOC_INTEL_HASWELL=m,
- CONFIG_SND_SST_ATOM_HIFI2_PLATFORM=m,
- CONFIG_SND_SST_ATOM_HIFI2_PLATFORM_PCI=m,
- CONFIG_SND_SST_ATOM_HIFI2_PLATFORM_ACPI=m,
- CONFIG_SND_SOC_INTEL_SKYLAKE=m, CONFIG_SND_SOC_INTEL_SKYLAKE_SSP_CLK=m,
- CONFIG_SND_SOC_INTEL_SKYLAKE_HDAUDIO_CODEC=y,
- CONFIG_SND_SOC_INTEL_SKYLAKE_COMMON=m, CONFIG_SND_SOC_ACPI_INTEL_MATCH=m,
- CONFIG_SND_SOC_INTEL_MACH=y, CONFIG_SND_SOC_INTEL_HASWELL_MACH=m,
- CONFIG_SND_SOC_INTEL_BDW_RT5677_MACH=m,
- CONFIG_SND_SOC_INTEL_BROADWELL_MACH=m,
- CONFIG_SND_SOC_INTEL_BYTCR_RT5640_MACH=m,
- CONFIG_SND_SOC_INTEL_BYTCR_RT5651_MACH=m,
- CONFIG_SND_SOC_INTEL_CHT_BSW_RT5672_MACH=m,
- CONFIG_SND_SOC_INTEL_CHT_BSW_RT5645_MACH=m,
- CONFIG_SND_SOC_INTEL_CHT_BSW_MAX98090_TI_MACH=m,
- CONFIG_SND_SOC_INTEL_CHT_BSW_NAU8824_MACH=m,
- CONFIG_SND_SOC_INTEL_BYT_CHT_DA7213_MACH=m,
- CONFIG_SND_SOC_INTEL_BYT_CHT_ES8316_MACH=m,
- CONFIG_SND_SOC_INTEL_BYT_CHT_NOCODEC_MACH=m,
- CONFIG_SND_SOC_INTEL_SKL_RT286_MACH=m,
- CONFIG_SND_SOC_INTEL_SKL_NAU88L25_SSM4567_MACH=m,
- CONFIG_SND_SOC_INTEL_SKL_NAU88L25_MAX98357A_MACH=m,
- CONFIG_SND_SOC_INTEL_BXT_DA7219_MAX98357A_MACH=m,
- CONFIG_SND_SOC_INTEL_BXT_RT298_MACH=m,
- CONFIG_SND_SOC_INTEL_KBL_RT5663_MAX98927_MACH=m,
- CONFIG_SND_SOC_INTEL_KBL_RT5663_RT5514_MAX98927_MACH=m,
- CONFIG_SND_SOC_INTEL_KBL_DA7219_MAX98357A_MACH=m,
- CONFIG_SND_SOC_INTEL_KBL_DA7219_MAX98927_MACH=m,
- CONFIG_SND_SOC_INTEL_GLK_RT5682_MAX98357A_MACH=m,
- CONFIG_SND_SOC_INTEL_SKL_HDA_DSP_GENERIC_MACH=m,
- CONFIG_SND_SOC_XTFPGA_I2S=m, CONFIG_ZX_TDM=m, CONFIG_SND_SOC_AC97_CODEC=m,
- CONFIG_SND_SOC_ADAU_UTILS=m, CONFIG_SND_SOC_ADAU1701=m,
- CONFIG_SND_SOC_ADAU17X1=m, CONFIG_SND_SOC_ADAU1761=m,
- CONFIG_SND_SOC_ADAU1761_I2C=m, CONFIG_SND_SOC_ADAU1761_SPI=m,
- CONFIG_SND_SOC_ADAU7002=m, CONFIG_SND_SOC_AK4104=m,
- CONFIG_SND_SOC_AK4458=m, CONFIG_SND_SOC_AK4554=m, CONFIG_SND_SOC_AK4613=m,
- CONFIG_SND_SOC_AK4642=m, CONFIG_SND_SOC_AK5386=m, CONFIG_SND_SOC_AK5558=m,
- CONFIG_SND_SOC_ALC5623=m, CONFIG_SND_SOC_BD28623=m, CONFIG_SND_SOC_BT_SCO=m,
- CONFIG_SND_SOC_CS35L32=m, CONFIG_SND_SOC_CS35L33=m, CONFIG_SND_SOC_CS35L34=m,
- CONFIG_SND_SOC_CS35L35=m, CONFIG_SND_SOC_CS42L42=m, CONFIG_SND_SOC_CS42L51=m,
- CONFIG_SND_SOC_CS42L51_I2C=m, CONFIG_SND_SOC_CS42L52=m,
- CONFIG_SND_SOC_CS42L56=m, CONFIG_SND_SOC_CS42L73=m, CONFIG_SND_SOC_CS4265=m,
- CONFIG_SND_SOC_CS4270=m, CONFIG_SND_SOC_CS4271=m, CONFIG_SND_SOC_CS4271_I2C=m,
- CONFIG_SND_SOC_CS4271_SPI=m, CONFIG_SND_SOC_CS42XX8=m,
- CONFIG_SND_SOC_CS42XX8_I2C=m, CONFIG_SND_SOC_CS43130=m,
- CONFIG_SND_SOC_CS4349=m, CONFIG_SND_SOC_CS53L30=m, CONFIG_SND_SOC_DA7213=m,
- CONFIG_SND_SOC_DA7219=m, CONFIG_SND_SOC_DMIC=m, CONFIG_SND_SOC_ES7134=m,
- CONFIG_SND_SOC_ES7241=m, CONFIG_SND_SOC_ES8316=m, CONFIG_SND_SOC_ES8328=m,
- CONFIG_SND_SOC_ES8328_I2C=m, CONFIG_SND_SOC_ES8328_SPI=m,
- CONFIG_SND_SOC_GTM601=m, CONFIG_SND_SOC_HDAC_HDMI=m,
- CONFIG_SND_SOC_HDAC_HDA=m, CONFIG_SND_SOC_INNO_RK3036=m,
- CONFIG_SND_SOC_MAX98088=m, CONFIG_SND_SOC_MAX98090=m,
- CONFIG_SND_SOC_MAX98357A=m, CONFIG_SND_SOC_MAX98504=m,
- CONFIG_SND_SOC_MAX9867=m, CONFIG_SND_SOC_MAX98927=m,
- CONFIG_SND_SOC_MAX98373=m, CONFIG_SND_SOC_MAX9860=m,
- CONFIG_SND_SOC_MSM8916_WCD_DIGITAL=m, CONFIG_SND_SOC_PCM1681=m,
- CONFIG_SND_SOC_PCM1789=m, CONFIG_SND_SOC_PCM1789_I2C=m,
- CONFIG_SND_SOC_PCM179X=m, CONFIG_SND_SOC_PCM179X_I2C=m,
- CONFIG_SND_SOC_PCM179X_SPI=m, CONFIG_SND_SOC_PCM186X=m,
- CONFIG_SND_SOC_PCM186X_I2C=m, CONFIG_SND_SOC_PCM186X_SPI=m,
- CONFIG_SND_SOC_PCM3060=m, CONFIG_SND_SOC_PCM3060_I2C=m,
- CONFIG_SND_SOC_PCM3060_SPI=m, CONFIG_SND_SOC_PCM3168A=m,
- CONFIG_SND_SOC_PCM3168A_I2C=m, CONFIG_SND_SOC_PCM3168A_SPI=m,
- CONFIG_SND_SOC_PCM512x=m, CONFIG_SND_SOC_PCM512x_I2C=m,
- CONFIG_SND_SOC_PCM512x_SPI=m, CONFIG_SND_SOC_RL6231=m,
- CONFIG_SND_SOC_RL6347A=m, CONFIG_SND_SOC_RT286=m, CONFIG_SND_SOC_RT298=m,
- CONFIG_SND_SOC_RT5514=m, CONFIG_SND_SOC_RT5514_SPI=m, CONFIG_SND_SOC_RT5616=m,
- CONFIG_SND_SOC_RT5631=m, CONFIG_SND_SOC_RT5640=m, CONFIG_SND_SOC_RT5645=m,
- CONFIG_SND_SOC_RT5651=m, CONFIG_SND_SOC_RT5663=m,
- CONFIG_SND_SOC_RT5670=m, CONFIG_SND_SOC_RT5677=m, CONFIG_SND_SOC_RT5677_SPI=m,
- CONFIG_SND_SOC_RT5682=m, CONFIG_SND_SOC_SGTL5000=m, CONFIG_SND_SOC_SIGMADSP=m,
- CONFIG_SND_SOC_SIGMADSP_I2C=m, CONFIG_SND_SOC_SIGMADSP_REGMAP=m,
- CONFIG_SND_SOC_SIMPLE_AMPLIFIER=m, CONFIG_SND_SOC_SIRF_AUDIO_CODEC=m,
- CONFIG_SND_SOC_SPDIF=m, CONFIG_SND_SOC_SSM2305=m, CONFIG_SND_SOC_SSM2602=m,
- CONFIG_SND_SOC_SSM2602_SPI=m, CONFIG_SND_SOC_SSM2602_I2C=m,
- CONFIG_SND_SOC_SSM4567=m, CONFIG_SND_SOC_STA32X=m, CONFIG_SND_SOC_STA350=m,
- CONFIG_SND_SOC_STI_SAS=m, CONFIG_SND_SOC_TAS2552=m, CONFIG_SND_SOC_TAS5086=m,
- CONFIG_SND_SOC_TAS571X=m, CONFIG_SND_SOC_TAS5720=m, CONFIG_SND_SOC_TAS6424=m,
- CONFIG_SND_SOC_TDA7419=m, CONFIG_SND_SOC_TFA9879=m,
- CONFIG_SND_SOC_TLV320AIC23=m, CONFIG_SND_SOC_TLV320AIC23_I2C=m,
- CONFIG_SND_SOC_TLV320AIC23_SPI=m, CONFIG_SND_SOC_TLV320AIC31XX=m,
- CONFIG_SND_SOC_TLV320AIC32X4=m, CONFIG_SND_SOC_TLV320AIC32X4_I2C=m,
- CONFIG_SND_SOC_TLV320AIC32X4_SPI=m, CONFIG_SND_SOC_TLV320AIC3X=m,
- CONFIG_SND_SOC_TS3A227E=m, CONFIG_SND_SOC_TSCS42XX=m,
- CONFIG_SND_SOC_TSCS454=m, CONFIG_SND_SOC_WM8510=m, CONFIG_SND_SOC_WM8523=m,
- CONFIG_SND_SOC_WM8524=m, CONFIG_SND_SOC_WM8580=m, CONFIG_SND_SOC_WM8711=m,
- CONFIG_SND_SOC_WM8728=m, CONFIG_SND_SOC_WM8731=m, CONFIG_SND_SOC_WM8737=m,
- CONFIG_SND_SOC_WM8741=m, CONFIG_SND_SOC_WM8750=m, CONFIG_SND_SOC_WM8753=m,
- CONFIG_SND_SOC_WM8770=m, CONFIG_SND_SOC_WM8776=m, CONFIG_SND_SOC_WM8782=m,
- CONFIG_SND_SOC_WM8804=m, CONFIG_SND_SOC_WM8804_I2C=m,
- CONFIG_SND_SOC_WM8804_SPI=m, CONFIG_SND_SOC_WM8903=m, CONFIG_SND_SOC_WM8960=m,
- CONFIG_SND_SOC_WM8962=m, CONFIG_SND_SOC_WM8974=m, CONFIG_SND_SOC_WM8978=m,
- CONFIG_SND_SOC_WM8985=m, CONFIG_SND_SOC_ZX_AUD96P22=m,
- CONFIG_SND_SOC_MAX9759=m, CONFIG_SND_SOC_MT6351=m, CONFIG_SND_SOC_NAU8540=m,
- CONFIG_SND_SOC_NAU8810=m, CONFIG_SND_SOC_NAU8822=m, CONFIG_SND_SOC_NAU8824=m,
- CONFIG_SND_SOC_NAU8825=m, CONFIG_SND_SOC_TPA6130A2=m,
- CONFIG_SND_SIMPLE_CARD_UTILS=m, CONFIG_SND_SIMPLE_CARD=m and
- CONFIG_SND_XEN_FRONTEND=m [https://elrepo.org/bugs/view.php?id=900]

* Fri Feb 15 2019 Alan Bartlett <ajb@elrepo.org> - 4.20.10-1
- Updated with the 4.20.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.10]

* Fri Feb 15 2019 Alan Bartlett <ajb@elrepo.org> - 4.20.9-1
- Updated with the 4.20.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.9]
- Not released due to the application of an inappropiate patch
- to the upstream -stable tree which breaks userland.
- [https://lkml.org/lkml/2019/2/13/853]

* Tue Feb 12 2019 Alan Bartlett <ajb@elrepo.org> - 4.20.8-1
- Updated with the 4.20.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.8]

* Wed Feb 06 2019 Alan Bartlett <ajb@elrepo.org> - 4.20.7-1
- Updated with the 4.20.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.7]
- CONFIG_DM_UNSTRIPED=m, CONFIG_DM_WRITECACHE=m, CONFIG_DM_VERITY_FEC=y,
- CONFIG_DM_INTEGRITY=m and CONFIG_DM_ZONED=m
- [https://elrepo.org/bugs/view.php?id=897]

* Thu Jan 31 2019 Alan Bartlett <ajb@elrepo.org> - 4.20.6-1
- Updated with the 4.20.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.6]

* Sat Jan 26 2019 Alan Bartlett <ajb@elrepo.org> - 4.20.5-1
- Updated with the 4.20.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.5]

* Tue Jan 22 2019 Alan Bartlett <ajb@elrepo.org> - 4.20.4-1
- Updated with the 4.20.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.4]
- CONFIG_FPGA=m, CONFIG_ALTERA_PR_IP_CORE=m, CONFIG_FPGA_MGR_ALTERA_PS_SPI=m,
- CONFIG_FPGA_MGR_ALTERA_CVP=m, CONFIG_FPGA_MGR_XILINX_SPI=m,
- CONFIG_FPGA_MGR_MACHXO2_SPI=m, CONFIG_FPGA_BRIDGE=m,
- CONFIG_XILINX_PR_DECOUPLER=m, CONFIG_FPGA_REGION=m, CONFIG_FPGA_DFL=m,
- CONFIG_FPGA_DFL_FME=m, CONFIG_FPGA_DFL_FME_MGR=m, CONFIG_FPGA_DFL_FME_BRIDGE=m,
- CONFIG_FPGA_DFL_FME_REGION=m, CONFIG_FPGA_DFL_AFU=m and CONFIG_FPGA_DFL_PCI=m
- [https://elrepo.org/bugs/view.php?id=892]

* Wed Jan 16 2019 Alan Bartlett <ajb@elrepo.org> - 4.20.3-1
- Updated with the 4.20.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.3]

* Sun Jan 13 2019 Alan Bartlett <ajb@elrepo.org> - 4.20.2-1
- Updated with the 4.20.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.2]

* Wed Jan 09 2019 Alan Bartlett <ajb@elrepo.org> - 4.20.1-1
- Updated with the 4.20.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.20.1]
- CONFIG_PSI=y and CONFIG_PSI_DEFAULT_DISABLED=y
- [https://elrepo.org/bugs/view.php?id=888]

* Sun Dec 23 2018 Alan Bartlett <ajb@elrepo.org> - 4.20.0-1
- Updated with the 4.20 source tarball.

* Fri Dec 21 2018 Alan Bartlett <ajb@elrepo.org> - 4.19.12-1
- Updated with the 4.19.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.12]

* Wed Dec 19 2018 Alan Bartlett <ajb@elrepo.org> - 4.19.11-1
- Updated with the 4.19.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.11]

* Mon Dec 17 2018 Alan Bartlett <ajb@elrepo.org> - 4.19.10-1
- Updated with the 4.19.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.10]

* Thu Dec 13 2018 Alan Bartlett <ajb@elrepo.org> - 4.19.9-1
- Updated with the 4.19.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.9]
- CONFIG_HID_ASUS=m [https://elrepo.org/bugs/view.php?id=884]

* Sat Dec 08 2018 Alan Bartlett <ajb@elrepo.org> - 4.19.8-1
- Updated with the 4.19.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.8]

* Wed Dec 05 2018 Alan Bartlett <ajb@elrepo.org> - 4.19.7-1
- Updated with the 4.19.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.7]

* Sat Dec 01 2018 Alan Bartlett <ajb@elrepo.org> - 4.19.6-1
- Updated with the 4.19.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.6]

* Tue Nov 27 2018 Alan Bartlett <ajb@elrepo.org> - 4.19.5-1
- Updated with the 4.19.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.5]

* Fri Nov 23 2018 Alan Bartlett <ajb@elrepo.org> - 4.19.4-1
- Updated with the 4.19.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.4]

* Wed Nov 21 2018 Alan Bartlett <ajb@elrepo.org> - 4.19.3-1
- Updated with the 4.19.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.3]

* Tue Nov 13 2018 Alan Bartlett <ajb@elrepo.org> - 4.19.2-1
- Updated with the 4.19.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.2]

* Sun Nov 04 2018 Alan Bartlett <ajb@elrepo.org> - 4.19.1-1
- Updated with the 4.19.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.1]

* Mon Oct 22 2018 Alan Bartlett <ajb@elrepo.org> - 4.19.0-1
- Updated with the 4.19 source tarball.

* Sat Oct 20 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.16-1
- Updated with the 4.18.16 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.16]

* Thu Oct 18 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.15-1
- Updated with the 4.18.15 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.15]

* Sat Oct 13 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.14-1
- Updated with the 4.18.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.14]

* Wed Oct 10 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.13-1
- Updated with the 4.18.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.13]

* Thu Oct 04 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.12-1
- Updated with the 4.18.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.12]

* Sat Sep 29 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.11-1
- Updated with the 4.18.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.11]

* Wed Sep 26 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.10-1
- Updated with the 4.18.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.10]

* Thu Sep 20 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.9-1
- Updated with the 4.18.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.9]

* Sat Sep 15 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.8-1
- Updated with the 4.18.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.8]

* Sun Sep 09 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.7-1
- Updated with the 4.18.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.7]

* Wed Sep 05 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.6-1
- Updated with the 4.18.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.6]
- Added NO_LIBBABELTRACE=1 directive to the %%global perf_make line.

* Fri Aug 24 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.5-1
- Updated with the 4.18.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.5]

* Wed Aug 22 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.4-1
- Updated with the 4.18.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.4]
- CONFIG_NET_FOU_IP_TUNNELS=y
- [https://elrepo.org/bugs/view.php?id=865]

* Sat Aug 18 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.3-1
- Updated with the 4.18.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.3]

* Sat Aug 18 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.2-1
- Updated with the 4.18.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.2]
- Not released due to a source code defect.

* Thu Aug 16 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.1-1
- Updated with the 4.18.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.1]

* Sun Aug 12 2018 Alan Bartlett <ajb@elrepo.org> - 4.18.0-1
- Updated with the 4.18 source tarball.

* Thu Aug 09 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.14-1
- Updated with the 4.17.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.14]

* Mon Aug 06 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.13-1
- Updated with the 4.17.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.13]

* Fri Aug 03 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.12-1
- Updated with the 4.17.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.12]

* Sat Jul 28 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.11-1
- Updated with the 4.17.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.11]

* Wed Jul 25 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.10-1
- Updated with the 4.17.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.10]

* Sun Jul 22 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.9-1
- Updated with the 4.17.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.9]

* Wed Jul 18 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.8-1
- Updated with the 4.17.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.8]

* Tue Jul 17 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.7-1
- Updated with the 4.17.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.7]
- Not released due to a source code defect.

* Wed Jul 11 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.6-1
- Updated with the 4.17.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.6]

* Sun Jul 08 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.5-1
- Updated with the 4.17.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.5]

* Tue Jul 03 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.4-1
- Updated with the 4.17.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.4]

* Tue Jun 26 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.3-1
- Updated with the 4.17.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.3]
- CONFIG_ZONE_DEVICE=y, CONFIG_DEV_DAX=m and CONFIG_FS_DAX=y
- [https://elrepo.org/bugs/view.php?id=860]
- CONFIG_NVME_TARGET_FCLOOP=m
- [https://elrepo.org/bugs/view.php?id=861]

* Sat Jun 16 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.2-1
- Updated with the 4.17.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.2]
- CONFIG_SND_X86=y and CONFIG_HDMI_LPE_AUDIO=m
- [https://elrepo.org/bugs/view.php?id=859]

* Mon Jun 11 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.1-1
- Updated with the 4.17.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.17.1]
- CONFIG_EFI_MIXED=y [https://elrepo.org/bugs/view.php?id=858]

* Sun Jun 03 2018 Alan Bartlett <ajb@elrepo.org> - 4.17.0-1
- Updated with the 4.17 source tarball.

* Wed May 30 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.13-1
- Updated with the 4.16.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.13]

* Fri May 25 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.12-1
- Updated with the 4.16.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.12]

* Tue May 22 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.11-1
- Updated with the 4.16.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.11]

* Sun May 20 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.10-1
- Updated with the 4.16.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.10]

* Wed May 16 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.9-1
- Updated with the 4.16.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.9]

* Wed May 09 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.8-1
- Updated with the 4.16.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.8]
- CONFIG_MD_CLUSTER=m [https://elrepo.org/bugs/view.php?id=847]
- CONFIG_BLK_DEV_ZONED=y [https://elrepo.org/bugs/view.php?id=848]

* Wed May 02 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.7-1
- Updated with the 4.16.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.7]

* Sun Apr 29 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.6-1
- Updated with the 4.16.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.6]

* Thu Apr 26 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.5-1
- Updated with the 4.16.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.5]
- CONFIG_MISC_RTSX=m, CONFIG_MISC_RTSX_PCI=m and CONFIG_MISC_RTSX_USB=m
- [https://elrepo.org/bugs/view.php?id=840]
- CONFIG_MMC_REALTEK_PCI=m, CONFIG_MMC_REALTEK_USB=m,
- CONFIG_MEMSTICK_REALTEK_PCI=m and CONFIG_MEMSTICK_REALTEK_USB=m

* Tue Apr 24 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.4-1
- Updated with the 4.16.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.4]

* Thu Apr 19 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.3-1
- Updated with the 4.16.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.3]

* Thu Apr 12 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.2-1
- Updated with the 4.16.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.2]

* Sun Apr 08 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.1-1
- Updated with the 4.16.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.1]

* Mon Apr 02 2018 Alan Bartlett <ajb@elrepo.org> - 4.16.0-1
- Updated with the 4.16 source tarball.

* Sat Mar 31 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.15-1
- Updated with the 4.15.15 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.15]

* Wed Mar 28 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.14-1
- Updated with the 4.15.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.14]

* Sun Mar 25 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.13-1
- Updated with the 4.15.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.13]

* Wed Mar 21 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.12-1
- Updated with the 4.15.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.12]

* Sun Mar 18 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.11-1
- Updated with the 4.15.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.11]

* Thu Mar 15 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.10-1
- Updated with the 4.15.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.10]

* Sun Mar 11 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.9-1
- Updated with the 4.15.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.9]

* Fri Mar 09 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.8-1
- Updated with the 4.15.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.8]

* Wed Feb 28 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.7-1
- Updated with the 4.15.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.7]

* Sun Feb 25 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.6-1
- Updated with the 4.15.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.6]

* Fri Feb 23 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.5-1
- Updated with the 4.15.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.5]
- Reverted "libxfs: pack the agfl header structure so XFS_AGFL_SIZE
- is correct" [https://elrepo.org/bugs/view.php?id=829]

* Sat Feb 17 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.4-1
- Updated with the 4.15.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.4]

* Mon Feb 12 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.3-1
- Updated with the 4.15.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.3]
- Ensure that objtool is present in the kernel-ml-devel package
- if CONFIG_STACK_VALIDATION is set.
- [https://elrepo.org/bugs/view.php?id=819]

* Wed Feb 07 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.2-1
- Updated with the 4.15.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.2]

* Sun Feb 04 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.1-1
- Updated with the 4.15.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.15.1]

* Mon Jan 29 2018 Alan Bartlett <ajb@elrepo.org> - 4.15.0-1
- Updated with the 4.15 source tarball.

* Wed Jan 24 2018 Alan Bartlett <ajb@elrepo.org> - 4.14.15-1
- Updated with the 4.14.15 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.15]

* Wed Jan 17 2018 Alan Bartlett <ajb@elrepo.org> - 4.14.14-1
- Updated with the 4.14.14 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.14]
- CONFIG_RETPOLINE=y and CONFIG_GENERIC_CPU_VULNERABILITIES=y

* Wed Jan 10 2018 Alan Bartlett <ajb@elrepo.org> - 4.14.13-1
- Updated with the 4.14.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.13]

* Fri Jan 05 2018 Alan Bartlett <ajb@elrepo.org> - 4.14.12-1
- Updated with the 4.14.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.12]

* Tue Jan 02 2018 Alan Bartlett <ajb@elrepo.org> - 4.14.11-1
- Updated with the 4.14.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.11]
- CONFIG_PAGE_TABLE_ISOLATION=y

* Sat Dec 30 2017 Alan Bartlett <ajb@elrepo.org> - 4.14.10-1
- Updated with the 4.14.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.10]

* Mon Dec 25 2017 Alan Bartlett <ajb@elrepo.org> - 4.14.9-1
- Updated with the 4.14.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.9]
- CONFIG_UNWINDER_FRAME_POINTER=y

* Wed Dec 20 2017 Alan Bartlett <ajb@elrepo.org> - 4.14.8-1
- Updated with the 4.14.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.8]

* Sun Dec 17 2017 Alan Bartlett <ajb@elrepo.org> - 4.14.7-1
- Updated with the 4.14.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.7]
- CONFIG_TLS=m and CONFIG_XEN_PVCALLS_BACKEND=y
- [https://elrepo.org/bugs/view.php?id=806]

* Thu Dec 14 2017 Alan Bartlett <ajb@elrepo.org> - 4.14.6-1
- Updated with the 4.14.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.6]
- CONFIG_PINCTRL_AMD=m, CONFIG_PINCTRL_MCP23S08=m,
- CONFIG_PINCTRL_CHERRYVIEW=m, CONFIG_PINCTRL_INTEL=m,
- CONFIG_PINCTRL_BROXTON=m, CONFIG_PINCTRL_CANNONLAKE=m,
- CONFIG_PINCTRL_DENVERTON=m, CONFIG_PINCTRL_GEMINILAKE=m,
- CONFIG_PINCTRL_LEWISBURG=m and CONFIG_PINCTRL_SUNRISEPOINT=m
- [https://elrepo.org/bugs/view.php?id=804]
- CONFIG_DRM_AMDGPU_SI=Y and CONFIG_DRM_AMDGPU_CIK=Y
- [https://elrepo.org/bugs/view.php?id=805]

* Sun Dec 10 2017 Alan Bartlett <ajb@elrepo.org> - 4.14.5-1
- Updated with the 4.14.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.5]
- Adjusted the list of files to be removed, as they will be
- created by depmod at the package installation time.
- [https://elrepo.org/bugs/view.php?id=803]
- CONFIG_ARCH_HAS_REFCOUNT=y

* Tue Dec 05 2017 Alan Bartlett <ajb@elrepo.org> - 4.14.4-1
- Updated with the 4.14.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.4]

* Thu Nov 30 2017 Alan Bartlett <ajb@elrepo.org> - 4.14.3-1
- Updated with the 4.14.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.3]

* Fri Nov 24 2017 Alan Bartlett <ajb@elrepo.org> - 4.14.2-1
- Updated with the 4.14.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.2]

* Tue Nov 21 2017 Alan Bartlett <ajb@elrepo.org> - 4.14.1-1
- Updated with the 4.14.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.1]

* Mon Nov 13 2017 Alan Bartlett <ajb@elrepo.org> - 4.14.0-1
- Updated with the 4.14 source tarball.

* Wed Nov 08 2017 Alan Bartlett <ajb@elrepo.org> - 4.13.12-1
- Updated with the 4.13.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.12]

* Thu Nov 02 2017 Alan Bartlett <ajb@elrepo.org> - 4.13.11-1
- Updated with the 4.13.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.11]

* Fri Oct 27 2017 Alan Bartlett <ajb@elrepo.org> - 4.13.10-1
- Updated with the 4.13.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.10]

* Sun Oct 22 2017 Alan Bartlett <ajb@elrepo.org> - 4.13.9-1
- Updated with the 4.13.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.9]

* Wed Oct 18 2017 Alan Bartlett <ajb@elrepo.org> - 4.13.8-1
- Updated with the 4.13.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.8]

* Sat Oct 14 2017 Alan Bartlett <ajb@elrepo.org> - 4.13.7-1
- Updated with the 4.13.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.7]

* Thu Oct 12 2017 Alan Bartlett <ajb@elrepo.org> - 4.13.6-1
- Updated with the 4.13.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.6]

* Thu Oct 05 2017 Alan Bartlett <ajb@elrepo.org> - 4.13.5-1
- Updated with the 4.13.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.5]

* Wed Sep 27 2017 Alan Bartlett <ajb@elrepo.org> - 4.13.4-1
- Updated with the 4.13.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.4]

* Wed Sep 20 2017 Alan Bartlett <ajb@elrepo.org> - 4.13.3-1
- Updated with the 4.13.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.3]

* Wed Sep 13 2017 Alan Bartlett <ajb@elrepo.org> - 4.13.2-1
- Updated with the 4.13.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.2]

* Sun Sep 10 2017 Alan Bartlett <ajb@elrepo.org> - 4.13.1-1
- Updated with the 4.13.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.1]

* Sun Sep 03 2017 Alan Bartlett <ajb@elrepo.org> - 4.13.0-1
- Updated with the 4.13 source tarball.

* Wed Aug 30 2017 Alan Bartlett <ajb@elrepo.org> - 4.12.10-1
- Updated with the 4.12.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.10]

* Fri Aug 25 2017 Alan Bartlett <ajb@elrepo.org> - 4.12.9-1
- Updated with the 4.12.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.9]

* Thu Aug 17 2017 Alan Bartlett <ajb@elrepo.org> - 4.12.8-1
- Updated with the 4.12.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.8]

* Mon Aug 14 2017 Alan Bartlett <ajb@elrepo.org> - 4.12.7-1
- Updated with the 4.12.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.7]
- CONFIG_MOUSE_PS2_VMMOUSE=y [https://elrepo.org/bugs/view.php?id=767]

* Fri Aug 11 2017 Alan Bartlett <ajb@elrepo.org> - 4.12.6-1
- Updated with the 4.12.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.6]

* Sun Aug 06 2017 Alan Bartlett <ajb@elrepo.org> - 4.12.5-1
- Updated with the 4.12.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.5]

* Fri Jul 28 2017 Alan Bartlett <ajb@elrepo.org> - 4.12.4-1
- Updated with the 4.12.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.4]

* Fri Jul 21 2017 Alan Bartlett <ajb@elrepo.org> - 4.12.3-1
- Updated with the 4.12.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.3]

* Sat Jul 15 2017 Alan Bartlett <ajb@elrepo.org> - 4.12.2-1
- Updated with the 4.12.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.2]

* Thu Jul 13 2017 Alan Bartlett <ajb@elrepo.org> - 4.12.1-1
- Updated with the 4.12.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.12.1]

* Mon Jul 03 2017 Alan Bartlett <ajb@elrepo.org> - 4.12.0-1
- Updated with the 4.12 source tarball.

* Thu Jun 29 2017 Alan Bartlett <ajb@elrepo.org> - 4.11.8-1
- Updated with the 4.11.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.8]

* Sat Jun 24 2017 Alan Bartlett <ajb@elrepo.org> - 4.11.7-1
- Updated with the 4.11.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.7]

* Sat Jun 17 2017 Alan Bartlett <ajb@elrepo.org> - 4.11.6-1
- Updated with the 4.11.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.6]

* Wed Jun 14 2017 Alan Bartlett <ajb@elrepo.org> - 4.11.5-1
- Updated with the 4.11.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.5]

* Wed Jun 07 2017 Alan Bartlett <ajb@elrepo.org> - 4.11.4-1
- Updated with the 4.11.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.4]
- CONFIG_HAMRADIO=y, CONFIG_AX25=m, CONFIG_AX25_DAMA_SLAVE=y,
- CONFIG_NETROM=m, CONFIG_ROSE=m, CONFIG_MKISS=m,
- CONFIG_6PACK=m, CONFIG_BPQETHER=m, CONFIG_BAYCOM_SER_FDX=m,
- CONFIG_BAYCOM_SER_HDX=m, CONFIG_BAYCOM_PAR=m and CONFIG_YAM=m
- [https://elrepo.org/bugs/view.php?id=745]

* Fri May 26 2017 Alan Bartlett <ajb@elrepo.org> - 4.11.3-1
- Updated with the 4.11.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.3]

* Sun May 21 2017 Alan Bartlett <ajb@elrepo.org> - 4.11.2-1
- Updated with the 4.11.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.2]

* Sun May 14 2017 Alan Bartlett <ajb@elrepo.org> - 4.11.1-1
- Updated with the 4.11.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.11.1]
- CONFIG_DETECT_HUNG_TASK=y, CONFIG_DEFAULT_HUNG_TASK_TIMEOUT=120
- and CONFIG_BOOTPARAM_HUNG_TASK_PANIC_VALUE=0
- [https://elrepo.org/bugs/view.php?id=733]

* Mon May 01 2017 Alan Bartlett <ajb@elrepo.org> - 4.11.0-1
- Updated with the 4.11 source tarball.

* Thu Apr 27 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.13-1
- Updated with the 4.10.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.13]
- CONFIG_MLX5_CORE_EN=y and CONFIG_MLX5_CORE_EN_DCB=y
- [https://elrepo.org/bugs/view.php?id=730]

* Fri Apr 21 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.12-1
- Updated with the 4.10.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.12]

* Tue Apr 18 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.11-1
- Updated with the 4.10.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.11]
- CONFIG_USERFAULTFD=y
- [https://lists.elrepo.org/pipermail/elrepo/2017-April/003540.html]

* Wed Apr 12 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.10-1
- Updated with the 4.10.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.10]

* Sat Apr 08 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.9-1
- Updated with the 4.10.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.9]

* Fri Mar 31 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.8-1
- Updated with the 4.10.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.8]

* Thu Mar 30 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.7-1
- Updated with the 4.10.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.7]

* Sun Mar 26 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.6-1
- Updated with the 4.10.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.6]

* Wed Mar 22 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.5-1
- Updated with the 4.10.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.5]

* Sat Mar 18 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.4-1
- Updated with the 4.10.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.4]

* Wed Mar 15 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.3-1
- Updated with the 4.10.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.3]

* Sun Mar 12 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.2-1
- Updated with the 4.10.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.2]

* Sun Feb 26 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.1-1
- Updated with the 4.10.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.1]
- Added NO_PERF_READ_VDSO32=1 and NO_PERF_READ_VDSOX32=1
- directives to the %%global perf_make line.
- [https://elrepo.org/bugs/view.php?id=719]

* Sun Feb 19 2017 Alan Bartlett <ajb@elrepo.org> - 4.10.0-1
- Updated with the 4.10 source tarball.
- CONFIG_NVME_FC=m and CONFIG_NVME_TARGET_FC=m
- [https://elrepo.org/bugs/view.php?id=705]

* Sat Feb 18 2017 Alan Bartlett <ajb@elrepo.org> - 4.9.11-1
- Updated with the 4.9.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.11]
- CONFIG_MODVERSIONS=y [https://elrepo.org/bugs/view.php?id=718]

* Wed Feb 15 2017 Alan Bartlett <ajb@elrepo.org> - 4.9.10-1
- Updated with the 4.9.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.10]
- CONFIG_CPU_FREQ_STAT=y and CONFIG_CPU_FREQ_STAT_DETAILS=y
- [https://elrepo.org/bugs/view.php?id=717]

* Thu Feb 09 2017 Alan Bartlett <ajb@elrepo.org> - 4.9.9-1
- Updated with the 4.9.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.9]

* Sat Feb 04 2017 Alan Bartlett <ajb@elrepo.org> - 4.9.8-1
- Updated with the 4.9.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.8]

* Wed Feb 01 2017 Alan Bartlett <ajb@elrepo.org> - 4.9.7-1
- Updated with the 4.9.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.7]

* Thu Jan 26 2017 Alan Bartlett <ajb@elrepo.org> - 4.9.6-1
- Updated with the 4.9.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.6]
- Remove any orphaned initramfs-xxxkdump.img file
- found post kernel uninstall. [Akemi Yagi]

* Fri Jan 20 2017 Alan Bartlett <ajb@elrepo.org> - 4.9.5-1
- Updated with the 4.9.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.5]

* Mon Jan 16 2017 Alan Bartlett <ajb@elrepo.org> - 4.9.4-1
- Updated with the 4.9.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.4]

* Fri Jan 13 2017 Alan Bartlett <ajb@elrepo.org> - 4.9.3-1
- Updated with the 4.9.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.3]

* Tue Jan 10 2017 Alan Bartlett <ajb@elrepo.org> - 4.9.2-1
- Updated with the 4.9.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.2]
- CONFIG_CAN=m, CONFIG_CAN_RAW=m, CONFIG_CAN_BCM=m, CONFIG_CAN_GW=m,
- CONFIG_CAN_VCAN=m, CONFIG_CAN_SLCAN=m, CONFIG_CAN_DEV=m,
- CONFIG_CAN_CALC_BITTIMING=y, CONFIG_CAN_LEDS=y, CONFIG_CAN_JANZ_ICAN3=m,
- CONFIG_CAN_C_CAN=m, CONFIG_CAN_C_CAN_PLATFORM=m, CONFIG_CAN_C_CAN_PCI=m,
- CONFIG_CAN_CC770=m, CONFIG_CAN_CC770_ISA=m, CONFIG_CAN_CC770_PLATFORM=m,
- CONFIG_CAN_IFI_CANFD=m, CONFIG_CAN_M_CAN=m, CONFIG_CAN_SJA1000=m,
- CONFIG_CAN_SJA1000_ISA=m, CONFIG_CAN_SJA1000_PLATFORM=m,
- CONFIG_CAN_EMS_PCMCIA=m, CONFIG_CAN_EMS_PCI=m, CONFIG_CAN_PEAK_PCMCIA=m,
- CONFIG_CAN_PEAK_PCI=m, CONFIG_CAN_PEAK_PCIEC=y, CONFIG_CAN_KVASER_PCI=m,
- CONFIG_CAN_PLX_PCI=m, CONFIG_CAN_SOFTING=m, CONFIG_CAN_SOFTING_CS=m,
- CONFIG_CAN_MCP251X=m, CONFIG_CAN_EMS_USB=m, CONFIG_CAN_ESD_USB2=m,
- CONFIG_CAN_GS_USB=m, CONFIG_CAN_KVASER_USB=m, CONFIG_CAN_PEAK_USB=m
- and CONFIG_CAN_8DEV_USB=m [https://elrepo.org/bugs/view.php?id=707]

* Fri Jan 06 2017 Alan Bartlett <ajb@elrepo.org> - 4.9.1-1
- Updated with the 4.9.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.1]
- CONFIG_NVME_CORE=m, CONFIG_NVME_FABRICS=m, CONFIG_NVME_RDMA=m,
- CONFIG_NVME_TARGET=m, CONFIG_NVME_TARGET_LOOP=m and
- CONFIG_NVME_TARGET_RDMA=m [https://elrepo.org/bugs/view.php?id=705]

* Mon Dec 12 2016 Alan Bartlett <ajb@elrepo.org> - 4.9.0-1
- Updated with the 4.9 source tarball.

* Fri Dec 09 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.13-1
- Updated with the 4.8.13 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.13]

* Fri Dec 02 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.12-1
- Updated with the 4.8.12 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.12]

* Sat Nov 26 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.11-1
- Updated with the 4.8.11 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.11]

* Mon Nov 21 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.10-1
- Updated with the 4.8.10 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.10]

* Sat Nov 19 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.9-1
- Updated with the 4.8.9 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.9]
- CONFIG_BPF_SYSCALL=y and CONFIG_BPF_EVENTS=y
- [https://elrepo.org/bugs/view.php?id=690]

* Tue Nov 15 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.8-1
- Updated with the 4.8.8 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.8]

* Thu Nov 10 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.7-1
- Updated with the 4.8.7 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.7]
- CONFIG_ORANGEFS_FS=m [https://elrepo.org/bugs/view.php?id=677]
- CONFIG_FMC=m, CONFIG_FMC_CHARDEV=m and CONFIG_FMC_WRITE_EEPROM=m
- [https://elrepo.org/bugs/view.php?id=680]

* Mon Oct 31 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.6-1
- Updated with the 4.8.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.6]

* Fri Oct 28 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.5-1
- Updated with the 4.8.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.5]

* Sat Oct 22 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.4-1
- Updated with the 4.8.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.4]

* Thu Oct 20 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.3-1
- Updated with the 4.8.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.3]

* Mon Oct 17 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.2-1
- Updated with the 4.8.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.2]

* Fri Oct 07 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.1-1
- Updated with the 4.8.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.1]

* Mon Oct 03 2016 Alan Bartlett <ajb@elrepo.org> - 4.8.0-1
- Updated with the 4.8 source tarball.

* Fri Sep 30 2016 Alan Bartlett <ajb@elrepo.org> - 4.7.6-1
- Updated with the 4.7.6 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.7.6]

* Sat Sep 24 2016 Alan Bartlett <ajb@elrepo.org> - 4.7.5-1
- Updated with the 4.7.5 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.7.5]

* Thu Sep 15 2016 Alan Bartlett <ajb@elrepo.org> - 4.7.4-1
- Updated with the 4.7.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.7.4]

* Wed Sep 07 2016 Alan Bartlett <ajb@elrepo.org> - 4.7.3-1
- Updated with the 4.7.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.7.3]
- Disabled CONFIG_FW_LOADER_USER_HELPER_FALLBACK
- [https://elrepo.org/bugs/view.php?id=671]

* Sat Aug 20 2016 Alan Bartlett <ajb@elrepo.org> - 4.7.2-1
- Updated with the 4.7.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.7.2]

* Wed Aug 17 2016 Alan Bartlett <ajb@elrepo.org> - 4.7.1-1
- Updated with the 4.7.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.7.1]

* Sun Jul 24 2016 Alan Bartlett <ajb@elrepo.org> - 4.7.0-1
- Updated with the 4.7 source tarball.

* Tue Jul 12 2016 Alan Bartlett <ajb@elrepo.org> - 4.6.4-1
- Updated with the 4.6.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.6.4]

* Sat Jun 25 2016 Alan Bartlett <ajb@elrepo.org> - 4.6.3-1
- Updated with the 4.6.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.6.3]

* Wed Jun 08 2016 Alan Bartlett <ajb@elrepo.org> - 4.6.2-1
- Updated with the 4.6.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.6.2]

* Thu Jun 02 2016 Alan Bartlett <ajb@elrepo.org> - 4.6.1-1
- Updated with the 4.6.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.6.1]

* Mon May 16 2016 Alan Bartlett <ajb@elrepo.org> - 4.6.0-1
- Updated with the 4.6 source tarball.

* Thu May 12 2016 Alan Bartlett <ajb@elrepo.org> - 4.5.4-1
- Updated with the 4.5.4 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.4]

* Thu May 05 2016 Alan Bartlett <ajb@elrepo.org> - 4.5.3-1
- Updated with the 4.5.3 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.3]

* Wed Apr 20 2016 Alan Bartlett <ajb@elrepo.org> - 4.5.2-1
- Updated with the 4.5.2 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.2]

* Sat Apr 16 2016 Alan Bartlett <ajb@elrepo.org> - 4.5.1-1
- Updated with the 4.5.1 source tarball.
- [https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.1]

* Mon Mar 14 2016 Alan Bartlett <ajb@elrepo.org> - 4.5.0-1
- Updated with the 4.5 source tarball.

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
- Add calls of weak-modules to the %%posttrans and %%preun scripts.

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
