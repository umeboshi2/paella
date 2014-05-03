ui vesamenu.c32
prompt 0

%if machine.autoinstall:
timeout 100
default install
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

menu title Network Boot Menu

label install
      menu label ^Install ${machine.name} with Paella
      kernel installer/i386/linux
      append vga=788 initrd=installer/i386/initrd.gz auto=true priority=critical url=http://${paella_server_ip}/paella/preseed/${machine.uuid}

#label live
include live/live.cfg Standard Live System



