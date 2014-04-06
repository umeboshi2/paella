# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "umeboshi/trumpet-i386"

  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  config.vm.synced_folder 'vagrant/salt/roots/salt/', '/srv/salt/'
  config.vm.synced_folder 'vagrant/salt/roots/pillar/', '/srv/pillar/'

  # debrepos for reprepro
  config.vm.synced_folder 'vagrant/debrepos', '/srv/debrepos'
  
  # debianlive config
  config.vm.synced_folder 'vagrant/netboot', '/srv/livebuild/'

  config.vm.provider "virtualbox" do |vb|
    # Don't boot with headless mode
    #vb.gui = true

    # Use VBoxManage to customize the VM. For example to change memory:
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
