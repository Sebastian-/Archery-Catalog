# Archery Equipment Catalog

A Flask web application used to catalog commonly used archery equipment.

## Features

* Supports CRUD operations on catalog items by authenitcated users.
* Dynamically generates pages based on the attributes of each item class.
* Google based OAuth2 login.
* JSON endpoint providing data on all items in the catalog.

## Requirements

* Vagrant
* Virtual Box
* Linux-style Shell

## Getting Started

1. Install Vagrant and Virtual Box
2. Clone the Archery-Catalog repository
3. Create a Google OAuth2 client credentials JSON file
   
   a) Visit https://console.developers.google.com

   b) Navigate the options to create an OAuth client ID

   c) Edit the credentials by adding http://localhost:8000 to Authorized JavaScript origins

   
   d) Similarly add http://localhost:8000/login and http://localhost:8000/gconnect to Authorized redirect URIs
   
   e) Download the credentials file into the catalog directory and name it "client_secrets.json"

4. In the catalog directory, run `vagrant up` followed by `vagrant ssh` to connect to the virtual machine that will act as the server.
5. Navigate to the application files: `cd /vagrant/catalog`
6. Enter `python database_setup.py` to instantiate the database.
7. Enter `python init_database.py` to insert some preliminary items into the database.
8. Enter `python item_calaog.py` to begin running the server.
9. Visit http://localhost:8000 to view the catalog and http://localhost:8000/catalog.json for JSON requests.

## Attributions

All vagrant-related setup files were provided by Udacity at https://github.com/udacity/fullstack-nanodegree-vm