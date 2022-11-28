import sys
import time
import json
import threading
import random
import string
import requests
import urllib
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import mysql.connector

mysql_host = "localhost"
mysql_user = "root"
mysql_password = "root"
mysql_database = "bountycrawl"

def get_database():
 mydb = mysql.connector.connect(
  host=mysql_host,
  user=mysql_user,
  password=mysql_password,
  database=mysql_database
 )
 return mydb

def query_urls(queryparam):
 queryparam = "%{}%".format(queryparam)
 mydb = get_database()
 mycursor = mydb.cursor()
 mycursor.execute("SELECT * FROM urls where url like %s", (queryparam,))
 myresult = mycursor.fetchall()
 for myres in myresult:
  print(myres[2])
  
if len(sys.argv) < 2:
 print("<query>")
 sys.exit(0)
query_urls(sys.argv[1])
