#### Contents of the preconfiguration file (for wheezy)
### Localization
# Preseeding only locale sets language, country and locale.
d-i debian-installer/locale string en_US

#d-i preseed/early_command string wget -O /usr/share/keyrings/archive.gpg http://${paella_server_ip}/debrepos/paella.bin.gpg

d-i keymap select us
d-i console-setup/ask_detect boolean false
d-i keyboard-configuration/xkb-keymap select us
d-i keyboard-configuration/layoutcode string us

d-i netcfg/choose_interface select auto
d-i netcfg/get_hostname string ${hostname}
d-i netcfg/get_domain string unassigned-domain

d-i netcfg/wireless_wep string

d-i mirror/country string manual
d-i mirror/http/hostname string ftp.us.debian.org
d-i mirror/http/directory string /debian
%if settings.get('paella_apt_proxy', ''):
d-i mirror/http/proxy string ${settings.get('paella_apt_proxy')}
%endif

#d-i apt-setup/${paella_server_ip}/key string http://${paella_server_ip}/debrepos/paella.gpg

d-i mirror/suite string ${release}
d-i mirror/udeb/suite string ${release}

d-i passwd/root-login boolean true
# Root password, either in clear text
d-i passwd/root-password password root
d-i passwd/root-password-again password root
# or encrypted using an MD5 hash.
#d-i passwd/root-password-crypted password [MD5 hash]


d-i passwd/make-user boolean false

# To create a normal user account.
#d-i passwd/user-fullname string Debian User
#d-i passwd/username string debian
# Normal user's password, either in clear text
#d-i passwd/user-password password debian
#d-i passwd/user-password-again password debian

# or encrypted using an MD5 hash.
#d-i passwd/user-password-crypted password [MD5 hash]

d-i clock-setup/utc boolean true
d-i time/zone string US/Central
d-i clock-setup/ntp boolean true
# NTP server to use. The default is almost always fine here.
#d-i clock-setup/ntp-server string ntp.example.com




# FIXME: there is currently no support for raid
<% method = 'lvm' %>
%if recipe is not None and 'raid' in recipe:
<% method = 'raid' %>
%endif

# FIXME: if there are multiple disks on the machine the disk needs to be selected
#d-i partman-auto/disk string /dev/sda /dev/sdb
%if disk_list is not None:
d-i partman-auto/disk string ${' '.join(disk_list)}
%endif

d-i partman-auto/method string ${method}
d-i partman-lvm/device_remove_lvm boolean true
d-i partman-md/device_remove_md boolean true


%if recipe is None:
d-i partman-auto/choose_recipe select atomic
%else:
d-i partman-auto/expert_recipe string ${recipe}
%endif

# FIXME: raid support
#d-i partman-auto-raid/recipe string <insert raid recipe>
%if raid_recipe is not None:
d-i partman-auto-raid/recipe string ${raid_recipe}
%endif

# Or provide a recipe of your own...
# If you have a way to get a recipe file into the d-i environment, 
# you can just point at it.
#d-i partman-auto/expert_recipe_file string /hd-media/recipe

# This makes partman automatically partition without confirmation, 
# provided that you told it what to do using one of the methods above.
d-i partman-md/confirm boolean true
d-i partman-md/confirm_nooverwrite boolean true
d-i partman-partitioning/confirm_write_new_label boolean true
d-i partman-partitioning/confirm_new_label boolean true
d-i partman/choose_partition select finish
d-i partman/confirm boolean true
d-i partman/confirm_nooverwrite boolean true
d-i partman-lvm/confirm_nooverwrite boolean true
d-i partman-auto-lvm/no_boot boolean true
d-i mdadm/boot_degraded boolean true

d-i apt-setup/use_mirror boolean false
d-i apt-setup/services-select multiselect 
d-i debian-installer/allow_unauthenticated boolean false

# Additional repositories, local[0-9] available
# FIXME put salt branch in settings
<% 
data = {}
for num in range(10):
  local = 'local%d' % num
  for name in ['repository', 'comment', 'key']:
    dckey = 'apt-setup/%s/%s' % (local, name)
    skey = 'paella_debrepo_%d_%s_%s' % (num, release, name)
    if settings.get(skey, ''):
      data[dckey] = settings.get(skey)
%>
%for key, value in data.items():
d-i ${key} string ${value}
%endfor

# select a task or we'll get desktop if desktop task is in repository
tasksel tasksel/first multiselect standard


# Individual additional packages to install
d-i pkgsel/include string salt-minion python-requests

popularity-contest popularity-contest/participate boolean false

# This is fairly safe to set, it makes grub install automatically to the MBR
# if no other operating system is detected on the machine.
d-i grub-installer/only_debian boolean true

# use default device for grub: #712907, #759737
d-i grub-installer/bootdev string default


# Avoid that last message about the install being complete.
d-i finish-install/reboot_in_progress note

d-i preseed/late_command string wget -O /target/tmp/configure-salt http://${paella_server_ip}/paella/latecmd/${uuid} ; in-target python /tmp/configure-salt

