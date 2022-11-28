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

lock = threading.Lock()

mysql_host = "localhost"
mysql_user = "root"
mysql_password = "root"
mysql_database = "bountycrawl"

link_tags = [
 ["a","href"],
 ["link","href"],
 ["iframe","src"],
 ["script","src"],
 ["embed","src"],
 ["form","action"]
]

def get_database():
 mydb = mysql.connector.connect(
  host=mysql_host,
  user=mysql_user,
  password=mysql_password,
  database=mysql_database
 )
 return mydb

def update_last_seen(domain):
 mydb = get_database()
 mycursor = mydb.cursor()
 sql = "UPDATE domains SET lastseen = now() WHERE name = %s"
 val = (domain,)
 mycursor.execute(sql, val)
 mydb.commit()
 mydb.close()

def update_domain_crawl_date(domainid):
 mydb = get_database()
 mycursor = mydb.cursor()
 sql = "UPDATE domains SET lastcrawl = now() WHERE id = %s"
 val = (domainid,)
 mycursor.execute(sql, val)
 mydb.commit()
 mydb.close()

def select_domain_task():
 mydb = get_database()
 mycursor = mydb.cursor()
 mycursor.execute("SELECT * FROM domains where lastcrawl < date_sub(now(), interval 1 day) and lastseen > date_sub(now(), interval 5 day) FOR UPDATE")
 myresult = mycursor.fetchall()
 if not len(myresult): return False
 mydb.close()
 update_domain_crawl_date(myresult[0][0])
 return myresult[0]

def insert_domain(domain, program):
 mydb = get_database()
 mycursor = mydb.cursor()
 sql = "INSERT INTO domains(name, program, lastcrawl, lastseen) VALUES (%s, %s, date_sub(now(), interval 2 day), now())"
 val = (domain, program)
 mycursor.execute(sql, val)
 mydb.commit()
 mydb.close()
 
def check_domain_exists(domain):
 mydb = get_database()
 mycursor = mydb.cursor()
 mycursor.execute("SELECT * from domains where name=%s", (domain,))
 myresult = mycursor.fetchall()
 mydb.close()
 if len(myresult): return True
 return False

def check_url_exists(url, domain_id):
 mydb = get_database()
 mycursor = mydb.cursor()
 mycursor.execute("SELECT * from urls where url=%s and did=%s", (url, domain_id))
 myresult = mycursor.fetchall()
 mydb.close()
 if len(myresult): return True
 return False

def add_url_to_database(url, domain_id):
 if not check_url_exists(url, domain_id):
  mydb = get_database()
  mycursor = mydb.cursor()
  sql = "INSERT INTO urls(did, url, dateadded) VALUES (%s, %s, now())"
  val = (domain_id, url)
  mycursor.execute(sql, val)
  mydb.commit()
  mydb.close()

def get_hackerone_datas():
 url = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/main/data/hackerone_data.json"
 r = requests.get(url=url)
 fullz = []
 datas = json.loads(r.text)
 for data in datas:
  if not "targets" in data: continue
  programname = data["name"]
  for target in data["targets"]["in_scope"]:
   if not target["asset_identifier"].startswith("*."): continue
   if not target["eligible_for_bounty"] == True: continue
   if not target["eligible_for_submission"] == True: continue
   target["asset_identifier"] = target["asset_identifier"].replace("*.", "")
   target["asset_identifier"] = target["asset_identifier"].replace("*", "")
   target["asset_identifier"] = target["asset_identifier"].replace("/", "")
   if "," in target["asset_identifier"]: target["asset_identifier"] = target["asset_identifier"].split(",")[0]
   fullz.append([target["asset_identifier"],programname])
 random.shuffle(fullz)
 return fullz

def _crawl(domain, domain_id):
 print("Starting the crawl process...")
 headers = {
  "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"    
 }
 url = "https://{}/".format(domain)
 r = requests.get(url=url, headers=headers, timeout=5, stream=True, allow_redirects=True)
 if r.status_code == 200:
  soup = BeautifulSoup(r.text, "html.parser")
  for link_tag in link_tags:
   links = soup.find_all(link_tag[0])
   for link in links:
    link_src = link.get(link_tag[1])
    if link_src:
     linkfull = urljoin(url, link_src)
     if not linkfull.startswith(url): continue
     add_url_to_database(linkfull, domain_id)

def _handler():
 while 1:
  time.sleep(1)
  try:
   with lock: domain_task = select_domain_task()
   if domain_task:
    print("Crawling: "+domain_task[1])
    _crawl(domain_task[1], domain_task[0])
  except Exception as error:
   print(error)

print("Starting up engine this might take a while...")
full_datas = get_hackerone_datas()
for datas in full_datas:
 domain = datas[0]
 program = datas[1]
 if not check_domain_exists(domain):
  insert_domain(domain, program)
 else:
  update_last_seen(domain)
for i in range(25):
 t=threading.Thread(target=_handler)
 t.start()
