import consul
import os
import pprint

print("Starting up...")
c = consul.Consul()

print("Adding nodes...")
num_nodes = 4
for i in range(num_nodes):
    port = 2000 + i
    c.agent.service.register(str(port), port = port)

print(f"Brought up {num_nodes} nodes.")
pprint.pprint(c.agent.services())

