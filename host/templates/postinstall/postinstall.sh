#!/bin/bash

logfile='/root/postinstall.log'

echo "Post install started on $(date)" > $logfile
echo "" >> $logfile

# Allow password-based root-login
echo "Permitting root login" >> $logfile
sed -i 's/^PermitRootLogin\ .*$/PermitRootLogin\ Yes/' /etc/ssh/sshd_config
systemctl restart sshd

# Install updates
echo "Installing updates" >> $logfile
apt-get update
apt-get -y upgrade

# Configure the kernel a little
echo "Enable icmp redirects" >> $logfile
echo "net.ipv4.conf.all.accept_redirects=1" >> /etc/sysctl.conf
echo "net.ipv6.conf.all.accept_redirects=1" >> /etc/sysctl.conf
sysctl -p

# Install puppet agent
distro=$(lsb_release -c -s)
echo "Installing puppet" >> $logfile
wget https://apt.puppet.com/puppet5-release-${distro}.deb
dpkg -i puppet5-release-${distro}.deb
apt-get update
apt-get -y install puppet-agent
rm puppet5-release-${distro}.deb
echo "[agent]" >> /etc/puppetlabs/puppet/puppet.conf
echo "server = {{puppetserver}}" >> /etc/puppetlabs/puppet/puppet.conf 
echo "ca_server = {{puppetca}}" >> /etc/puppetlabs/puppet/puppet.conf 
export PATH="$PATH:/opt/puppetlabs/bin"
systemctl enable  puppet

echo "Post install completed on $(date)" >> $logfile 

exit 0
