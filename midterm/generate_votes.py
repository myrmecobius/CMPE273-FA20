# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 19:35:04 2020

@author: theor
"""

#%% Load imports
import csv
import random

#%% Generate random x,y values
random.seed(45)
votes = ['x' if bool(random.randint(0,1)) else 'y' for i in range(10000) ]
count = sum([1 if votes[i] == 'x' else 0 for i in range(10000)])

split = random.randint(3000,7000)
votes_east = votes[:split]
votes_west = votes[split:]

countx_east = sum([1 if votes_east[i] == 'x' else 0 for i in range(len(votes_east))])
county_east = len(votes_east) - countx_east
total_east = countx_east + county_east

countx_west = sum([1 if votes_west[i] == 'x' else 0 for i in range(len(votes_west))])
county_west = len(votes_west) - countx_west
total_west = countx_west + county_west

total_x = countx_east + countx_west
total_y = county_east + county_west

print(f"East has {countx_east} votes for x and {county_east} for y for a total of {total_east}")
print(f"West has {countx_west} votes for x and {county_west} for y for a total of {total_west}")
print(f"x gets {total_x} votes total and y gets {total_y} votes total")

#%% Write to csv
file = open('votes/west.csv', 'w+', newline ='') 
  
# writing the data into the file 
with file:     
    write = csv.writer(file) 
    write.writerows(votes_west)
    
file = open('votes/east.csv', 'w+', newline ='') 
  
# writing the data into the file 
with file:     
    write = csv.writer(file) 
    write.writerows(votes_east) 
    












