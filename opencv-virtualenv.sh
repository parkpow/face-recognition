#!/usr/bin/env bash

set -e
set -o pipefail


# Install required dependencies
sudo apt-get -y install cmake
sudo apt-get -y install gcc g++

sudo apt-get -y install python3-dev python3-numpy

sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get -y install libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev

sudo apt-get -y install libgtk-3-dev


sudo apt-get -y install libpng-dev
sudo apt-get -y install libjpeg-dev
sudo apt-get -y install libopenexr-dev
sudo apt-get -y install libtiff-dev
sudo apt-get -y install libwebp-dev


# End Install required dependencies


FILE=/tmp/opencv.zip

if [ -f "$FILE" ]; then
    echo "$FILE exists."
else
    echo "$FILE does not exist."
    # mkdir -p /tmp/opencv/
    # Download to tmp
    wget "https://codeload.github.com/opencv/opencv/zip/4.5.1" -O $FILE

    # Unzip to
    unzip /tmp/opencv.zip -d /tmp/ # opencv-src
fi


# Create virtualenv
sudo apt-get -y install virtualenv
VIRTUAL_ENV=`pwd`'/env'
virtualenv $VIRTUAL_ENV --python=python3

## Install Numpy
source "$VIRTUAL_ENV/bin/activate"
pip install numpy


FILE=build
if [ -d "$FILE" ]; then
    echo "$FILE directory reuse."
else
    mkdir build
fi

cd build

cmake -D MAKE_BUILD_TYPE=RELEASE -D \
    CMAKE_INSTALL_PREFIX=$VIRTUAL_ENV/ -D \
    PYTHON_EXECUTABLE=$VIRTUAL_ENV/bin/python -D \
    PYTHON_PACKAGES_PATH=$VIRTUAL_ENV/lib/python3.8.5/site-packages /tmp/opencv-4.5.1/

make -j8 /tmp/opencv-4.5.1/
make install /tmp/opencv-4.5.1/