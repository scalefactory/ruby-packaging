%define rubyversion <%= version %>
%define packageversion %(eval echo %{rubyversion} | sed s/-//g)

%define _prefix		/opt/ruby/%{rubyversion}
%define _localstatedir	%{_prefix}/var
%define _mandir		%{_prefix}/man
%define _infodir	%{_prefix}/share/info

Name:      ruby%{rubyversion}
Version:   %{packageversion}

Group:     Development/Languages
Release:   1%{?dist}
License:   Ruby License/GPL - see COPYING
URL:       http://www.ruby-lang.org/
Source0:   <%= source %>
Summary:   An interpreter of object-oriented scripting language
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:	readline readline-devel ncurses ncurses-devel gdbm gdbm-devel glibc-devel tcl-devel tk-devel libX11-devel gcc unzip openssl-devel db4-devel byacc
<% buildrequires.each do |req| %>
BuildRequires: <%= req %>
<% end %>
<% requires.each do |req| %>
Requires: <%= req %>
<% end %>

%description
Ruby is the interpreted scripting language for quick and easy
object-oriented programming.  It has many features to process text
files and to do system management tasks (as in Perl).  It is simple,
straight-forward, and extensible.

%prep
%setup -n ruby-%{rubyversion}

%build
CFLAGS="$RPM_OPT_FLAGS -Wall -fno-strict-aliasing"
export CFLAGS
%configure \
    --enable-shared \
    --disable-rpath
make RUBY_INSTALL_NAME=ruby %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
# installing binaries ...
make install DESTDIR=$RPM_BUILD_ROOT
sed -i 's^#!/usr/bin/env ruby^%{_prefix}/bin/ruby^g' $RPM_BUILD_ROOT/%{_prefix}/bin/*
mkdir -p $RPM_BUILD_ROOT/etc/ld.so.conf.d
cat > $RPM_BUILD_ROOT/etc/ld.so.conf.d/ruby%{rubyversion}.conf <<EOF
%{_prefix}/lib
%{_prefix}/lib64
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-, root, root)
%doc README COPYING ChangeLog LEGAL ToDo
%{_prefix}
%{_prefix}/*
/etc/ld.so.conf.d/ruby%{rubyversion}.conf

%post
/sbin/ldconfig

%postun
/sbin/ldconfig


%changelog
 * Tue Apr 19 2011 Jon Topper <jon@scalefactory.com> - %{rubyversion}
   - Initial RPM build
