# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 18:39:30 2020

@author: theor
"""
#%% Load Imports
import requests

#%% define payload
payload = {"name": "Pinterest",
           "url": "https://www.pinterest.com/pin/27373510214883341/",
           "description": "Innovation Engine"}

#%% POST
rPost = requests.post("http://127.0.0.1:5000/api/bookmarks", data = payload)
print(rPost)
print(rPost.text)

#%% GET
rGet = requests.get("http://127.0.0.1:5000/api/bookmarks/Pinterest")
print(rGet)
print(rGet.text)

#%% DELETE
rDelete = requests.delete("http://127.0.0.1:5000/api/bookmarks/Pinterest")
print(rDelete)
print(rDelete.text)

#%% QR Code
rQR = requests.get("http://127.0.0.1:5000/api/bookmarks/Pinterest/qrcode")
print(rGet)
print(rGet.text)

#%% Conditional GET
rQR = requests.get("http://127.0.0.1:5000/api/bookmarks/Pinterest/stats")
print(rGet)
print(rGet.text)

#%% Get Keys
def getKeys():
    rGet = requests.get("http://127.0.0.1:5000/keys")
    print(rGet)
    print(rGet.text)

def clearKeys():
    rGet = requests.get("http://127.0.0.1:5000/clearKeys")
    print(rGet)
    print(rGet.text)
    
#%%