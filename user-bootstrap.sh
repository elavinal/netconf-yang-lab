#!/usr/bin/env bash

echo "Provisioning guest VM..."

sudo apt-get update

sudo apt-get install -y --no-install-recommends --fix-missing\
  autoconf \
  automake \
  build-essential \
  unzip \
  libncurses5 \
  libxml2-utils \
  libtool \
  python-paramiko \
  python3-dev \
  python3-setuptools \
  python3-wheel \
  python3-pip

# ---- ConfD ----
echo "Installing ConfD..."
wget --quiet https://www.irit.fr/~Emmanuel.Lavinal/cours/SPC/confd-basic-6.4.linux.x86_64.zip
unzip confd-basic-6.4.linux.x86_64.zip
~/confd-basic-6.4.linux.x86_64/confd-basic-6.4.linux.x86_64.installer.bin ~/confd-6.4
echo ""  >> ~/.profile
echo "# EDIT NETCONF/YANG LAB"  >> ~/.profile
echo "source ~/confd-6.4/confdrc"  >> ~/.profile

# ---- Symlinks to /vagrant folders  ----
echo "Making sym links to NETCONF/YANG dhcpd folders..."
ln -fs /vagrant/dhcpd ~/dhcpd
ln -fs /vagrant/dhcpd_ncclient ~/dhcpd_ncclient
ln -fs /vagrant/yang ~/yang
ln -fs /vagrant/examples ~/examples

# ---- pyang ----
echo "Installing pyang..." 
pip3 install pyang

# ---- Overwrite ConfD's pyang version ----
mv ~/confd-6.4/bin/pyang ~/confd-6.4/bin/pyang-old
ln -fs ~/.local/bin/pyang ~/confd-6.4/bin/pyang

# ---- ncclient ----
echo "Installing ncclient..."
pip3 install ncclient

# ---- pyangbind ----
echo "Installing pyangbind..."
git clone https://github.com/robshakir/pyangbind.git
cd pyangbind
python3 setup.py install --prefix ~/.local
cd
PLUGINPATH=`python3 -c 'import pyangbind; import os; print("{}/plugin".format(os.path.dirname(pyangbind.__file__)))'`
echo "export PYBINDPLUGIN=$PLUGINPATH" >> ~/.profile

echo "**** DONE PROVISIONING VM ****"
