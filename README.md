#Shlv.me

Build and share shelves of books, movies, albums, and most anything on the web

##Developing shlv.me -- Setting up your Django environment

###Install Django

curl -LO https://www.djangoproject.com/download/1.4/tarball/
tar xvfz Django-1.4.tar.gz
cd Django-1.4
sudo python setup.py install

Django should be ready to roll, but give it a test (no errors == good):
python
>>> import django

###Install required shlv.me packages and Django

Install the MySQL driver

If you're using MySQL to power Django, you'll need the driver:

curl -LO http://downloads.sourceforge.net/project/mysql-python/mysql-python/1.2.3/MySQL-python-1.2.3.tar.gz
tar xvzf MySQL-python-1.2.3.tar.gz
cd MySQL-python-1.2.3
sudo python setup.py install

If you get an error after the Django syncdb, have a look at http://stackoverflow.com/questions/6383310/python-mysqldb-library-not-loaded-libmysqlclient-18-dylib

Install Bottlenose so that we can get  Amazon Product API data, https://github.com/dlo/bottlenose

sudo easy_install bottlenose

Install lxml:

http://lxml.de/installation.html

(If you work in OS X, this might be helpful: http://stackoverflow.com/questions/1277124/how-do-you-install-lxml-on-os-x-leopard-without-using-macports-or-fink)

Install Beautiful Soup:

easy_install BeautifulSoup

###Create your database and load some data to get started

If you're using MySQL your database creation process might look something like this (these DB credentials should match what you have in settings.py):

mysql -u root -psomepasshere
mysql> create database shlvme_matt; grant all on shlvme_matt.* to shlvme_matt@'%' identified by 'shlvme_matt';
mysql -u shlvme_matt -psomepasshere shlvme_matt

Create your tables:
python manage.py syncdb

Load some data:
python manage.py loaddata shlvme/fixtures/bootstrap.json

(this should create a user with the username of 'willy' and the password of 'pass')

###Setup mail
If you want the "reset password" functionality to work, you'll need a mail server.

If you're running an ubuntu system and want to run mail locally:

apt-get install mailutils

Be sure you mail options are pointing to the right place in settings.py 

###Install shlv.me

Clone the repo:
git clone git://github.com/harvard-lil/shlvme.git

Get the develop branch:
git checkout -b develop origin/develop
git pull

Config your Django project settings:
cd lil
cp settings.py.example settings.py
(At a minimum, youll probably update LOGGING, DATABASES and SECRET_KEY)

Configure your Django app (local settings):
cd shlvme
cp local_settings.example.py local_settings.py

Start the Django web server:
python manage.py runserver hlsl7.law.harvard.edu:8000

###Update site name
Set the Django site name in the database by updating the django_site table:

update django_site set domain = 'shlv.me'; update django_site set name = 'shlv.me';

## License

Dual licensed under the MIT license (below) and [GPL license](http://www.gnu.org/licenses/gpl-3.0.html).

<small>
MIT License

Copyright (c) 2012 The Harvard Library Innovation Lab

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
</small>
