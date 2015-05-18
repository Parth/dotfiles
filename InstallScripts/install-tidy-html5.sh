#!/bin/bash
 
# Check if user is root
if [ $(id -u) != "0" ]; then
    echo "Error: You must be root to run this script, please use root to install the software."
    exit 1
fi
 
apt-get remove libtidy-0.99-0 tidy 
apt-get install git-core automake libtool checkinstall
mkdir /tmp/htmltidy
cd /tmp/htmltidy
git clone https://github.com/w3c/tidy-html5
cd tidy-html5
 
sh build/gnuauto/setup.sh && ./configure --prefix=/usr && make
checkinstall --pkgversion $(date +"%Y%m%dcvs-1")
 
rm /tmp/htmltidy -rf
