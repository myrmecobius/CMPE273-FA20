# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:24:46 2020

@author: theor
"""

#%% Load imports
import consul
import time

c = consul.Consul()
a = c.agent

a.service.register(
    name = "node2"
    #address = "127.0.0.1",
    #port = "8000"
    )

a.service.deregister("node1")

#%% remove all services
k = a.services().keys()
for key in k:
    a.service.deregister(key)

#%% Server test
time.sleep(3)
a.service.register(name="8001", port=8001)
time.sleep(1)
a.service.register(name="8002", port=8002)
time.sleep(1)
a.service.deregister("8002")
time.sleep(2)
a.service.register(name="8001", port=8001)