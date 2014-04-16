# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # This project depends on using debian wheezy for
  # development.  While the paella automated installer
  # can install various operating systems, the hosting 
  # environment for the installer is debian specific.
  #
  # I generally use my trumpet base box for development.
  # However, the chef/debian-7.4-i386 should work as well.
  # The virtualbox guest modules on the chef machines use
  # a 4.3 version, which are newer than the 4.1.18 version 
  # that ships with debian-7.4.

  # I have configured the code below to default to using 
  # the chef/debian-7.4-i386 box if the umeboshi/trumpet-i386
  # box doesn't seem to be present.

  # Also, if your virtualbox doesn't match the version on 
  # the chef box, you can easily create a new base box with 
  # the proper extensions by executing:
  # vagrant up --no-provision
  # vagrant package 
  # vagrant box add package.box --name chef-debian-7.4-i386-vboxguest-4.1.18
  #
  # Then, adjust this Vagrantfile and use the box you 
  # most desire.
  # 
  #boxname = 'chef-debian-7.4-i386-vboxguest-4.1.18'
  boxname = 'umeboshi-VAGRANTSLASH-trumpet-i386'
  dirname = ENV['HOME'] + '/.vagrant.d/boxes/' + boxname
  if File.directory?(dirname)
    config.vm.box = 'umeboshi/trumpet-i386'
  else
    config.vm.box = 'chef/debian-7.4-i386'
  end

  config.vm.hostname = 'paella'

  # This can be helpful when wanting to test the 
  # paella web server
  #config.vm.network "forwarded_port", guest: 80, host: 8080

  # salt 
  config.vm.synced_folder 'vagrant/salt/roots/salt/', '/srv/salt/'
  config.vm.synced_folder 'vagrant/salt/roots/pillar/', '/srv/pillar/'
  config.vm.synced_folder 'vagrant/salt/roots/pillar.local/', '/srv/pillar.local/'

  # debrepos for reprepro
  config.vm.synced_folder 'vagrant/debrepos', '/srv/debrepos'

  # for wsgi server
  config.vm.synced_folder 'src', '/srv/src'

  config.vm.provider "virtualbox" do |vb|
    # Don't boot with headless mode
    #vb.gui = true
    
    # if you need a different nat ip
    #vb.customize ["modifyvm", :id, "--natnet1", "10.0.3/24"]
    

    vb.customize ["modifyvm", :id, "--memory", "512"]
    # a secondary internal network is used for the paella installer
    vb.customize ["modifyvm", :id, "--nic2", "intnet"]
    vb.customize ["modifyvm", :id, "--intnet2", "intloc"]
  end

  config.vm.provision "shell", path: "vagrant/scripts/vagrant-bootstrap.sh"

  config.vm.provision :salt do |salt|
    salt.minion_config = 'vagrant/salt/minion'
    salt.run_highstate = true
    salt.verbose = true
  end

end
