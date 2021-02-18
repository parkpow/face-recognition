# FaceRecognition


## Setup

### 1. Install OpenCV and Python Bindings

To install OpenCv system wide, run this command
```bash
apt-get install python3-opencv

```

To install OpenCv to a virtualenv, Build from source by running the script (Tested on Ubuntu18.04) 
```bash

./opencv-virtualenv.sh

```  
This will create a virtualenv `env` in the current directory


#### 2. Install other requirements
```bash

source env/bin/active # If using a Virtualenv 

pip install -r requirements.txt


```


### 3. Run the script on images

