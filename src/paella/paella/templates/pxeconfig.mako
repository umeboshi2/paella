ui vesamenu.c32
prompt 0

%if machine.autoinstall:
timeout 100
default gtk_install
%endif

menu background paella-splash.png
#menu vshift 13
menu color tabmsg 37;44 #ffcccc55 #cc222200 std
menu color cmdline 37;44 #ffcccc55 #cc222200 std
menu color sel 7;37;40 #ffcccc55 #ff555555 all
menu color unsel 37;44 #ffcccc55 #cc222200 std
menu color title 1;36;44 #ffcccc55 #ee220000 std
menu color border 0 #00ffffff #55cc55cc std
menu color timeout_msg 37;44 #ffcccc55 #cc222200 std

menu title Paella Installer Menu

%if machine.ostype == 'debian':

<% release = 'wheezy' %>
%if machine.release is not None:
<% release = machine.release %>
%endif

label gtk_install
      menu label ^Install ${release}(${machine.arch}) to ${machine.name} with Paella (gtk)
      kernel debinstall/${release}/${machine.arch}/linux
      append vga=788 initrd=debinstall/${release}/${machine.arch}/initrd-gtk.gz auto=true priority=critical url=http://${paella_server_ip}/paella/preseed/${machine.uuid} hostname=${machine.name} netcfg/choose_interface=${machine.iface} ${debconf_debug} 
      
label console_install
      menu label ^Install ${release}(${machine.arch}) to ${machine.name} with Paella (console)
      kernel debinstall/${release}/${machine.arch}/linux
      append vga=788 initrd=debinstall/${release}/${machine.arch}/initrd-console.gz auto=true priority=critical url=http://${paella_server_ip}/paella/preseed/${machine.uuid} hostname=${machine.name} netcfg/choose_interface=${machine.iface} ${debconf_debug}

%elif machine.ostype == 'mswindows':

<% winpe = 'winpe.iso' %>
%if machine.arch == 'amd64':
<% winpe = 'winpe64.iso' %>
%endif


label install
      menu label WinPE Auto ^Install (${machine.arch})
      kernel memdisk
      append iso initrd=http://${paella_server_ip}/debrepos/${winpe}

%endif

      
#label live
include live-${machine.arch}.cfg Standard Live System (${machine.arch})
