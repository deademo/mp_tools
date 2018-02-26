Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.hostname = "deabox"
  config.vm.network :private_network, ip: "192.168.93.123"

  config.vm.provider :virtualbox do |vb|
    vb.customize [
      "modifyvm", :id,
      "--cpuexecutioncap", "50",
      "--memory", "1024",
    ]
  end
  config.vm.synced_folder ".", "/opt/project", SharedFoldersEnableSymlinksCreate: false
end