# geoapi

## Dowload the BAN (Base d'Adresses Nationale)

First download and unzip in /data/ban the open BAN database.

## Prerequisites

How to do to launch the geoapi code : 

### if not already done : install homebrew
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

### if not already done : install python3

  brew install python3

### install postgis
brew install postgis

### Create virtual env
virtualenv -p python3 env

### Switch to virtual env
source env/bin/activate

### Install dependencies
pip install -r requirements.txt

### or directly : 

pip install numpy==1.11.2

pip install pandas==0.19.1

pip install python-dateutil==2.6.0

pip install requests==2.12.1

pip install Unidecode==0.4.19


### in /src, you may have to delete 2 references to "src."  :    

```import db as db
``` 

instead of 

```import src.db as db
```   

```import utils as utils
``` 

instead of

```import utisrc.ls as util
```    

### Launch index.py to index BAN DB

pip install pyproj
python3 src/index.py

### Then before launching geocode :  
line 51 : src/geocode.py
                code_post = values[5].zfill(5)  # FLEC : change col index with the one containing zipcode
                city = values[6]                # FLEC : change col index with the one containing city
                # query = values[3] or values[2] or values[1]
                query = values[4]               # FLEC : change col index with the one containing road
                
### modify src/adresse.py : 

Delete reference to IRIS.
