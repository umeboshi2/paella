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

  # If your virtualbox doesn't match the version on 
  # the chef box, you can easily create a new base box with 
  # the proper extensions by executing:
  # vagrant up --no-provision
  # vagrant package 
  # vagrant box add package.box --name chef-debian-7.4-vboxguest-4.1.18
  #
  # Then, adjust this Vagrantfile and use the box you 
  # most desire.
  # 
  boxname = 'chef-debian-7.4-vboxguest-4.1.18'
  dirname = ENV['HOME'] + '/.vagrant.d/boxes/' + boxname
  if File.directory?(dirname)
    config.vm.box = boxname
  else
    config.vm.box = 'chef/debian-7.4'
  end

  config.vm.hostname = 'paella'

  # This can be helpful when wanting to test the 
  # paella web server
  #config.vm.network "forwarded_port", guest: 80, host: 8080

  # salt 
  config.vm.synced_folder 'vagrant/salt/roots/salt/', '/srv/salt/'
  config.vm.synced_folder 'vagrant/salt/roots/pillar/', '/srv/pillar/'

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
    # bridged
    #vb.customize ["modifyvm", :id, "--nic2", "bridged"]
    #vb.customize ["modifyvm", :id, "--bridgeadapter2", "eth1"]
  end
  config.vm.provision "shell", path: "vagrant/scripts/restore-deb-cache.sh"
  config.vm.provision "shell", path: "vagrant/scripts/vagrant-bootstrap.sh"
  config.vm.provision "shell", inline: "sudo mkdir -p /etc/salt && sudo chown -R vagrant /etc/salt || true"
  config.vm.provision "file", source: "vagrant/salt/minion",
                      destination: "/etc/salt/minion"
  config.vm.provision :salt do |salt|
    salt.minion_config = 'vagrant/salt/minion'
    salt.run_highstate = true
    salt.verbose = true
    salt.no_minion = true
  end

end
