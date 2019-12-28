import pandas as pd
import re
from bs4 import BeautifulSoup
from collections import Counter,defaultdict
import datetime 
import math  

#opening the xml file containing gps data 
with open("C://Users//mahdi//Desktop//Py Project//Assilah to Ouzzane.gpx") as datagps:
    soup= BeautifulSoup(datagps,"html.parser")
    #print (soup) # print the xml file

#spliting all the track point of the track segmentation
points=soup.find_all('trkpt')
#printing all the trackpoints marked in trajectory 
#print (points)
print(list(i.get_text() for i in points[0].findChildren()))

#looping in every track point information to get it's specific axes(Elevation,Time...) and storing in a dictionnary

dict_data=[]
for p in points:
    data=list(i.get_text() for i in p.findChildren())
    dict_data.append({
        'Elevation':data[0],
        'Time':data[1]
    })
#print(dict_data)

#storing the data (xml) to Panda Dataframe
df=pd.DataFrame.from_records(dict_data)
#print(df.head())

#  Another way to Get the Elevation and Time data 
with open("C://Users//mahdi//Desktop//Py Project//Assilah to Ouzzane.gpx") as datagps:
    soup= BeautifulSoup(datagps,"html.parser")
elev=[i.get_text() for i in soup.find_all('ele')]
time=[i.get_text() for i in soup.find_all('time')][1:] #removed the first time record because its the time we connect to gps
mix_both=zip(elev,time)

#print(list(mix_both))
df1=pd.DataFrame.from_records(mix_both)
df1.columns=['Elevation','Time']
#print(df1)
df1['ele_in_m']=df1['Elevation'].map(lambda x: (float(x) * 1000))
#print(df1.head())


# Calculate Duration between every point of the Track
from dateutil import parser
df1['Time']=df1['Time'].map(lambda timetostr:parser.parse(timetostr))
inttime=pd.to_datetime(df1['Time'], format='%b-%y')

df1['next_trkpnt_Time']=df1['Time'].shift(1)
df1['duration']=df1['Time']-df1['next_trkpnt_Time']

#Using google maps Api to compute distance between points

import googlemaps
api_key="AIzaSyAfSCK2iEM7F1vFr4py5hYjlzt6-gUsFRo"
gmaps = googlemaps.Client(key=api_key)
gmaps.distance_matrix(
    (35.4668836 , -6.0378672),(35.4669533,-6.0366808))['rows'][0]['elements'][0]['duration']['text']
'''↑↑↑↑ We used Lat Long to get the values 
of that tracjectory and digged into its values (List)
and picked the duration from it ↑↑↑ '''

#Visualisation Part Using Matplotlib
import matplotlib.pyplot as plt

fig=plt.figure()
# I chosed to visualise the gain of the elevation in the whole Trajectory (Assilah to Ouezzane)
df1['ele_in_m_next']=df1['ele_in_m'].shift(1)
df1['Elevation_Gained']=(df1['ele_in_m_next'] - df1['ele_in_m']) 
ax1=fig.add_subplot(111) # Creating the first Axe
ax2=ax1.twinx() # Creating the seconde Axe that shares the same ax1 
df1.ele_in_m.plot(kind='line',color='red',ax=ax1)
df1.Elevation_Gained.plot(kind='line',alpha=0.6,color='blue', linewidth=1,ax=ax2)
ax1.set_ylabel('Elevation')
ax2.set_ylabel('Elevation Gain')
plt.show()

#Another way to Calculate distance between point pairs
pts=soup.find_all('trkpt')
fpts=[{float (x.attrs['lat']),float (x.attrs['lon'])} for x in pts] #Converting all the Points to float values 
pts_pairs=list(zip(fpts[::1],fpts[1:]))# collecting pair points
from geopy.distance import vincenty
start=pts_pairs[0][0]
end=pts_pairs[0][-1]
print(vincenty(start, end).meters) #Distance between two points using geopy Vincenty 
print(df1['duration'].sum()) # Duration of the trajectory
print(df1['ele_in_m'].max()) # Maximum Elevation of the trajectory


