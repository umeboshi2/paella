# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "umeboshi/trumpet-i386"

  config.vm.network "forwarded_port", guest: 8080, host: 8080

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # salt 
  config.vm.synced_folder 'salt/roots/salt/', '/srv/salt/'
  config.vm.synced_folder 'salt/roots/pillar/', '/srv/pillar/'

  # config.ssh.forward_agent = true

  config.vm.provider "virtualbox" do |vb|
    # Don't boot with headless mode
    #vb.gui = true
    
    # if you need a different nat ip
    #vb.customize ["modifyvm", :id, "--natnet1", "10.0.3/24"]
  end

  config.vm.provision "shell", path: "vagrant-bootstrap.sh"

  config.vm.provision :salt do |salt|
    salt.minion_config = 'salt/minion'
    salt.run_highstate = true
    salt.verbose = true
  end

end
