Introduction
============

ityou.whoisonline is a Plone product that shows all online users 
in a portlet. It wirks fine with Plone 4.1. With Plone 4.2 it's not 
yet tested but should also work.

Installation
----------------
Important: This product is based in sqlite3. You first have to install
sqlite3 and sqlite3 headers.

On Ubuntu LTS 12.4, you can do this with

	sudo apt-get install sqlite3 libsqlite3-dev

For further information please see docs/INSTALL.txt.

Plone configuration
----------------------
After restart of Plone, you have to activate the product in Plone. 
Go to the Site Setup, click "add-ons" and select  
"ITYOU ESI - Who is online" to activate.  

After activating the product, the portlets "Who is online" and "Who am I"
will be installed automatically. 

  




