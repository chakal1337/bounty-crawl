#!/bin/bash
sudo apt install apache2 php php-mysql mariadb-server python3 python3-pip;
sudo service mysql start;
sudo mysql -u'root' <<< "alter user 'root'@'localhost' identified by 'root';";
sudo mysql -u'root' -p'root' < db.sql;
pip3 install requests mysql-connector bs4;
sudo service apache2 restart;
sudo cp www/* /var/www/html/;
