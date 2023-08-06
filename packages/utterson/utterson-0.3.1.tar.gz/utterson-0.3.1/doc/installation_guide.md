# Installation Guide
At the moment installation is a very manual process. Luckily utterson is such as simple app that installation is mostly a file copy. The biggest item is making sure you have the requirements.

## Requirements
Utterson requires Python 3, Jekyll, and one python module, PyYaml. You will need to use the proper facilities of your operating system to get these installed. On Linux I recommend taking the time to get pip installed as you will find it useful over time. The same can be said for installing gem to then install Jekyll.

### Debian Based Requirements Installation (Debian, Ubunut, LinuxMint, etc)
Below are the steps I use to deploy on a new LinuxMint workstation. Obviously for Debian or any other distribution that doesn't require sudo remove that command.

#### Install Python 3
```
sudo apt-get install python3
```

#### Install pip
```
sudo apt-get install python3-setuptools
sudo curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | sudo python3
```

#### Install PyYaml with pip
```
sudo pip install pyyaml
```

#### Install Jekyll with apt-get
```
sudo apt-get install jekyll
```

### Debian Alternative
You could also use apt-get to install everything.
 
```
sudo apt-get install python3 python3-yaml jekyll
```


## Utterson Installation
At this point the only option is to pull down the source code or if there is a release the tar archive. The source code will include items that are not needed while the tar will contain only the files needed.

### Source
Pull down the source and move _utterson_ and the _templates_ folders to a directory called utterson wherever you want utterson to be installed at. Personally I place it in /opt/utterson

#### Final Structure

```
utterson
|- utterson
|- templates
   |- All the files and folders in templates
```

Finally make sure the utterson file is executable with a command such as:
```
chmod +x utterson
```

Next add the utterson file to your path via a symlink or adding the path to utterson to your path.

Symlink Option
```
sudo ln -s /opt/utterson/utterson /usr/local/bin/utterson
```

Adding the path option
```
export PATH=$PATH:/opt/utterson/
```

These are just examples and there are many ways to accomplish this. Also note I specified the path I normally install into. If you installed somewhere else update the path accordingly.

### Tar Archive Install
The archive install is just like the source install but you don't have to remove any files. Just copy the folder to the installation directory and then make sure the utterson file is executable and in your path.


# Mac OS X 
Temporary section for Mac OS basic instructions.

## Python 3
Install python using the proper [installer](http://python.org/download/)

## Setuptools
curl https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py | python3

## Install Pip
curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python3

## Install Yaml
pip install pyyaml

## Install rvm
\curl -L https://get.rvm.io | bash -s stable --ruby

## Install Ruby
rvm install 2.0.0

## Install Jekyll
gem install jekyll

## Configure Terminal
By default the Mac OS X Terminal application does not send a Ctrl-H when the delete key is pressed. The following steps will correct this.

* Open the Terminal Application
* Terminal => Preferences
* Settings => Advanced Tab
* Check the 'Delete sends Ctrl-H

