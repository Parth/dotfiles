cd ~
sudo apt-get install -yyq build-essential libturbojpeg libtool autoconf libudev-dev cmake mesa-common-dev freeglut3-dev libxrandr-dev doxygen libxi-dev libopencv-dev
sudo ln -s /usr/lib/x86_64-linux-gnu/libturbojpeg.so.0 /usr/lib/x86_64-linux-gnu/libturbojpeg.so
git clone https://github.com/OpenKinect/libfreenect2
