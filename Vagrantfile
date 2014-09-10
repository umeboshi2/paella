# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  boxname = 'chef-debian-7.4-vboxguest-4.1.18'
  dirname = ENV['HOME'] + '/.vagrant.d/boxes/' + boxname
  if File.directory?(dirname)
    config.vm.box = boxname
  else
    config.vm.box = 'chef/debian-7.4'
  end

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  # config.vm.box_url = "http://domain.com/path/to/above.box"
  #config.vm.box_check_update = false
  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network "forwarded_port", guest: 8080, host: 8080
  #config.vm.network "forwarded_port", guest: 6543, host: 6543

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # If true, then any SSH connections made will enable agent forwarding.
  # Default value: false
  # config.ssh.forward_agent = true

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"
  
  # TODO: share salt directories for provisioning
  config.vm.synced_folder 'vagrant/salt/roots/salt/', '/srv/salt/'
  config.vm.synced_folder 'vagrant/salt/roots/pillar/', '/srv/pillar/'


  # This config is needed for building nodejs
  # and can be readjusted once the package is built.
  config.vm.provider "virtualbox" do |vb|
    vb.memory = 1024
    vb.cpus = 4
  end
  #config.vm.provision "shell", path: "scripts/vagrant-bootstrap.sh"
  config.vm.provision "shell", path: "vagrant/scripts/vagrant-bootstrap.sh"

  config.vm.provision :salt do |salt|
    salt.minion_config = 'vagrant/salt/minion'
    salt.run_highstate = true
    salt.verbose = true
  end


end
