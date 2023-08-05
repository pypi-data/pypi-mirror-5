##########Flipkart API############

Steps to install 

If you use pip you can install by 
sudo pip install Flipkart

or 

1.install setup tools first if not installed 
read more at
https://pypi.python.org/pypi/setuptools#installation-instructions

2.extract this setup
and run

python setup.py build            #to do the building

and 

sudo python setup.py install          #to install


Example Program:

from fk.Flipkart import Flipkart
from fk.Flipkart import Item
f = Flipkart()
items = f.search("data structure") 
#or items = f.search("data structure",2) # where 2 is page number 
for item in items:
    print item.image
    print item.title
    print item.product_subtitle
    print item.product_fsp
    print item.product_mrp