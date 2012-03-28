#Shlv.me

Build and share shelves of books, movies, albums, and most anything on the web

## Installation


### Required packages

Install the MySQL DB Driver (if you've configured Django to use MySQL), http://sourceforge.net/projects/mysql-python/

    wget http://downloads.sourceforge.net/project/mysql-python/mysql-python/1.2.3/MySQL-python-1.2.3.tar.gz
    tar xvzf MySQL-python-1.2.3.tar.gz
    cd MySQL-python-1.2.3
    sudo python setup.py install
    
    If you get an error after the Django syncdb, have a look at http://stackoverflow.com/questions/6383310/python-mysqldb-library-not-loaded-libmysqlclient-18-dylib

Install the lxml package, http://lxml.de

These install guides should get you close:

  * http://stackoverflow.com/questions/1277124/how-do-you-install-lxml-on-os-x-leopard-without-using-macports-or-fink
  * http://lxml.de/installation.html

Install the Amazon Product API package, http://packages.python.org/python-amazon-product-api/

    wget http://pypi.python.org/packages/source/p/python-amazon-product-api/python-amazon-product-api-0.2.5.tar.gz#md5=86206766f8741d2f3ff477fec1e106bd
    tar xvfz python-amazon-product-api-0.2.5.tar.gz
    cd python-amazon-product-api-0.2.5
    sudo python setup.py install

### Setup configs

Copy the example configs:

    cd lil/
    cp settings.example.py settings.py
    cd shlvme/
    cp local_settings.example.py local_settings.py

Configure settings.py:

    Set DATABASES with your DB settings
    Set SECRET_KEY with your secret key

Configure local_settings.py:

    Set AMZ.KEY to your Amazon Product Advertising key
    Set AMZ.SECRET_KEY to your Amazon Product Advertising secret key
    Set AMZ.ASSOCIATE_TAG to your Amazon Product Advertising associate tag

## License

Dual licensed under the MIT license (below) and [GPL license](http://www.gnu.org/licenses/gpl-3.0.html).

<small>
MIT License

Copyright (c) 2012 The Harvard Library Innovation Lab

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
</small>
