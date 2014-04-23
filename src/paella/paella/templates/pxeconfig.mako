default vesamenu.c32
prompt 0

menu background splash.png
#menu vshift 13
menu color unsel 37;44 #ffcccc55 #cc222200 std
menu color tabmsg 37;44 #ffcccc55 #cc222200 std
menu color sel 7;37;40 #ffcccc55 #ff555555 all
menu color cmdline 37;44 #ffcccc55 #cc222200 std
menu color unsel 37;44 #ffcccc55 #cc222200 std
menu color title 1;36;44 #ffcccc55 #cc220000 std
menu color border 0 #00ffffff #00000000 std

menu title Network Boot Menu

label install
      menu label ^Install ${machine} with Paella
      kernel installer/i386/linux
      append vga=788 initrd=installer/i386/initrd.gz auto=true priority=critical url=http://${paella_server_ip}/paella/preseed/${uuid}

#label live
include live/live.cfg Standard Live System



