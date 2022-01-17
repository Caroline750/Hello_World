#HW9
import tkinter
import math
import ssl
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlencode, quote_plus
import json
import webbrowser
import string

from twitteraccess import *

#
# In HW8 Q2 and HW 9, you will use two Google services, Google Static Maps API
# and Google Geocoding API.  Both require use of an API key.
# 
# When you have the API key, put it between the quotes in the string below
GOOGLEAPIKEY = "AIzaSyBTAamleaEHST9ohjgLAIJ4pR8KTINwzYQ"


# To run the HW9 program, call the last function in this file: HW9().

# The Globals class demonstrates a better style of managing "global variables"
# than simply scattering the globals around the code and using "global x" within
# functions to identify a variable as global.
#
# We make all of the variables that we wish to access from various places in the
# program properties of this Globals class.  They get initial values here
# and then can be referenced and set anywhere in the program via code like
# e.g. Globals.zoomLevel = Globals.zoomLevel + 1
#
class Globals:
   
   rootWindow = None
   mapLabel = None

   defaultLocation = "Mauna Kea, Hawaii"
   mapLocation = defaultLocation
   mapFileName = 'googlemap.gif'
   mapSize = 400
   zoomLevel = 9
   mapType = None
   currentIndex = 0
   coordinate = []
   
# Given a string representing a location, return 2-element tuple
# (latitude, longitude) for that location 
#
# See https://developers.google.com/maps/documentation/geocoding/
# for details about Google's geocoding API.
#
#
def geocodeAddress(addressString):
   global geoURL
   global jsonResult
   urlbase = "https://maps.googleapis.com/maps/api/geocode/json?address="
   geoURL = urlbase + quote_plus(addressString)
   geoURL = geoURL + "&key=" + GOOGLEAPIKEY

   # required (non-secure) security stuff for use of urlopen
   ctx = ssl.create_default_context()
   ctx.check_hostname = False
   ctx.verify_mode = ssl.CERT_NONE
   
   stringResultFromGoogle = urlopen(geoURL, context=ctx).read().decode('utf8')
   jsonResult = json.loads(stringResultFromGoogle)
   if (jsonResult['status'] != "OK"):
      print("Status returned from Google geocoder *not* OK: {}".format(jsonResult['status']))
      result = (0.0, 0.0) # this prevents crash in retrieveMapFromGoogle - yields maps with lat/lon center at 0.0, 0.0
   else:
      loc = jsonResult['results'][0]['geometry']['location']
      result = (float(loc['lat']),float(loc['lng']))
   return result

# Contruct a Google Static Maps API URL that specifies a map that is:
# - is centered at provided latitude lat and longitude long
# - is "zoomed" to the Google Maps zoom level in Globals.zoomLevel
# - Globals.mapSize-by-Globals.mapsize in size (in pixels), 
# - will be provided as a gif image
#
# See https://developers.google.com/maps/documentation/static-maps/
#
# YOU WILL NEED TO MODIFY THIS TO BE ABLE TO
# 1) DISPLAY A PIN ON THE MAP
# 2) SPECIFY MAP TYPE - terrain vs road vs ...
#
def getMapUrl():
   lat, lng = geocodeAddress(Globals.mapLocation)
   urlbase = "http://maps.google.com/maps/api/staticmap?"
   args = "center={},{}&zoom={}&size={}x{}&format=gif&maptype={}&markers=color:red%7Clabel:C%7C{},{}".format(lat,lng,Globals.zoomLevel,Globals.mapSize,Globals.mapSize,Globals.mapType,lat,lng)
   args = args + "&key=" + GOOGLEAPIKEY
   mapURL = urlbase + args + generateMarkerString(Globals.currentIndex, Globals.coordinate, [lat, lng])
   print([Globals.coordinate])
   print([lat, lng])
   return mapURL

# Retrieve a map image via Google Static Maps API, storing the 
# returned image in file name specified by Globals' mapFileName
#
def retrieveMapFromGoogle():
   url = getMapUrl()
   urlretrieve(url, Globals.mapFileName)

########## 
#  basic GUI code

def displayMap():
   retrieveMapFromGoogle()    
   mapImage = tkinter.PhotoImage(file=Globals.mapFileName)
   Globals.mapLabel.configure(image=mapImage)
   # next line necessary to "prevent (image) from being garbage collected" - http://effbot.org/tkinterbook/label.htm
   Globals.mapLabel.mapImage = mapImage

def displayTweet():
   tweetText.configure(state=tkinter.NORMAL)
   tweetText.delete(1.0, tkinter.END)
   if len(Globals.tweets) != 0:
      screenName = Globals.tweets[Globals.currentIndex]['user']['screen_name']
      
      coordinate = None
      if Globals.tweets[Globals.currentIndex]['coordinates'] != None:
         coordinate = Globals.tweets[Globals.currentIndex]['coordinates']['coordinates']
         
#      print(coordinate)
      
      name = Globals.tweets[Globals.currentIndex]['user']['name']
      info = "Screen name: @" + screenName + " Name: " + name
      tweetInfo.configure(text=info)

      content = Globals.tweets[Globals.currentIndex]['text']
      contentDisplayed = content
      contentDisplayed = contentDisplayed.encode('utf-8')
      tweetText.insert(1.0, contentDisplayed)
   else:
      tweetText.insert(1.0, "No tweet found")
   tweetText.configure(state=tkinter.DISABLED)
   tweetLabel.configure(text="Tweet {} of {}".format(Globals.currentIndex + 1, len(Globals.tweets)))

def previousTweet():
   if Globals.currentIndex >= 1:
      Globals.currentIndex -= 1
   displayTweet()
   displayMap()

   
def nextTweet():   
   if Globals.currentIndex < len(Globals.tweets)-1:
      Globals.currentIndex += 1
   displayTweet()
   displayMap()

def displayURL():
   global currentURL
   tweetURL.configure(state=tkinter.NORMAL)
   tweetURL.delete(1.0,tkinter.END)
   if len(Globals.URLs) > 0:
      currentURL = Globals.URLs[Globals.currentIndex]
      tweetURL.insert(1.0, currentURL)
   else:
      tweetURL.insert(1.0, "No URL found")
   tweetURL.configure(state=tkinter.DISABLED)
   URLLabel.configure(text="Tweet URL {} of {}".format(Globals.currentIndex + 1, len(Globals.URLs)))

def previousURL():
   if Globals.currentIndex >= 1:
      Globals.currentIndex -= 1
   displayURL()

def nextURL():
   if Globals.currentIndex < len(Globals.URLs) - 1:
      Globals.currentIndex += 1
   displayURL()

def openURL():
   webbrowser.open(currentURL)

def readEntriesSearchTwitterAndDisplayMap():
   global entry1
   global entry2

   #### you should change this function to read from the location from an Entry widget
   #### instead of using the default location
   address = entry1.get()
   addressCode = geocodeAddress(address)
   searchTerm = entry2.get()
   tweets = searchTwitter(searchTerm, latlngcenter=[addressCode[0],addressCode[1]])
   
#   print(address)
#   print(searchTerm)
#   print(addressCode)

   Globals.currentIndex = 0
   Globals.tweets = []
   Globals.URLs = []
   Globals.coordinate = []
   for item in tweets:
      Globals.tweets += [item]
#      Globals.tweets += [item['user']['name'] + ": " + item['text'] + item['user']['screen_name']]
   
      if len(item['entities']['urls']) == 0:
         Globals.URLs += []
      else:
         Globals.URLs.append(item['entities']['urls'][0]['url'])

      coordinate = None
      if item['coordinates'] != None:
         coordinate = item['coordinates']['coordinates']
         Globals.coordinate.append([coordinate[1],coordinate[0]])
      else:
         Globals.coordinate.append(None)
         
         
#   print(Globals.tweets)
#   print(Globals.URLs)
#   print(Globals.coordinate)


   

#   print(Globals.mapLocation)
   Globals.mapLocation = address
   displayMap()
   displayTweet()
   displayURL()
     
def initializeGUIetc():
   global entry1
   global entry2
   global label1
   global label2
   global zoomLabel
   global increaseButton
   global decreaseButton
   global choiceVar
   global tweetText
   global tweetInfo
   global decreaseButton
   global increaseButton
   global tweetURL
   global tweetLabel
   global URLLabel
   global URLButton

   authTwitter()

   Globals.rootWindow = tkinter.Tk()
   Globals.rootWindow.title("HW9")

   mainFrame = tkinter.Frame(Globals.rootWindow) 
   mainFrame.pack()

   zoomFrame = tkinter.Frame(Globals.rootWindow)
   zoomFrame.pack()

   twitterFrame =tkinter.Frame(Globals.rootWindow)
   twitterFrame.pack()

   label1 = tkinter.Label(mainFrame, text = "Map location:")
   label1.pack()

   entry1 = tkinter.Entry(mainFrame)
   entry1.pack()

   label2 = tkinter.Label(mainFrame, text = "Search terms:")
   label2.pack()

   entry2 = tkinter.Entry(mainFrame)
   entry2.pack()



   # until you add code, pressing this button won't change the map (except
   # once, to the Beijing location "hardcoded" into readEntryAndDisplayMap)
   # you need to add an Entry widget that allows you to type in an address
   # The click function should extract the location string from the Entry widget
   # and create the appropriate map.
   term = entry2.get()
   location = entry1.get()

   readEntriesSearchTwitterAndDisplayMapButton = tkinter.Button(mainFrame, text="Search Twitter and display map", command=readEntriesSearchTwitterAndDisplayMap)
   readEntriesSearchTwitterAndDisplayMapButton.pack()

   tweetInfo = tkinter.Label(twitterFrame)
   tweetInfo.pack()
   
   tweetText = tkinter.Text(twitterFrame, width=72, height=3, bd=2)
   tweetText.insert(1.0, "Current Tweet")
   
   tweetText.configure(state=tkinter.DISABLED)
   tweetText.pack()

   decreaseButton = tkinter.Button(twitterFrame, text='<', command = previousTweet)
   decreaseButton.pack()

   tweetLabel = tkinter.Label(twitterFrame, text = "Tweet 0 of 0")
   tweetLabel.pack()
   
   increaseButton = tkinter.Button(twitterFrame, text='>', command = nextTweet)
   increaseButton.pack()


   tweetURL = tkinter.Text(twitterFrame, width=72, height=3, bd=2)
   tweetURL.insert(1.0, "Current URL")

   tweetURL.configure(state=tkinter.DISABLED)
   tweetURL.pack()

   URLdecreaseButton = tkinter.Button(twitterFrame, text='<', command = previousURL)
   URLdecreaseButton.pack()

   URLLabel = tkinter.Label(twitterFrame, text = "Tweet 0 of 0")
   URLLabel.pack()

   URLButton = tkinter.Button(twitterFrame, text='Open URL', command = openURL)
   URLButton.pack()

   URLincreaseButton = tkinter.Button(twitterFrame, text='>', command = nextURL)
   URLincreaseButton.pack()

   
   zoomLabel = tkinter.Label(zoomFrame, text = "Zoom: {}".format(Globals.zoomLevel))
   zoomLabel.pack(side=tkinter.LEFT)

   increaseButton = tkinter.Button(zoomFrame, text = "+", command = increaseZoom)
   increaseButton.pack(side=tkinter.LEFT)
   decreaseButton = tkinter.Button(zoomFrame, text = "-", command = decreaseZoom)
   decreaseButton.pack(side=tkinter.LEFT)

   Globals.mapType = "roadmap"
   choiceVar = tkinter.IntVar()
   choiceVar.set(1)

   mapButton1 = tkinter.Radiobutton(zoomFrame, text="Road map", variable=choiceVar, value=1, command=buttonChosen)
   mapButton1.pack(side=tkinter.TOP)
   mapButton2 = tkinter.Radiobutton(zoomFrame, text="Satellite map", variable=choiceVar, value=2, command=buttonChosen)
   mapButton2.pack(side=tkinter.TOP)
   mapButton3 = tkinter.Radiobutton(zoomFrame, text="Hybrid map", variable=choiceVar, value=3, command=buttonChosen)
   mapButton3.pack(side=tkinter.BOTTOM)
   mapButton4 = tkinter.Radiobutton(zoomFrame, text="Terrain map", variable=choiceVar, value=4, command=buttonChosen)
   mapButton4.pack(side=tkinter.BOTTOM)

   # we use a tkinter Label to display the map image
   Globals.mapLabel = tkinter.Label(mainFrame, width=Globals.mapSize, bd=2, relief=tkinter.FLAT)
   Globals.mapLabel.pack()

def buttonChosen():
   
   if choiceVar.get() == 1:
      Globals.mapType = "roadmap"
   elif choiceVar.get() == 2:
      Globals.mapType = "satellite"
   elif choiceVar.get() == 3:
      Globals.mapType = "hybrid"
   else:
      Globals.mapType = "terrain"
   displayMap()
   

def HW9():
    initializeGUIetc()
    displayMap()
    Globals.rootWindow.mainloop()


def increaseZoom():
   Globals.zoomLevel += 1
   zoomLabel.configure(text = "Zoom: {}".format(Globals.zoomLevel))
   displayMap()

def decreaseZoom():
   Globals.zoomLevel -= 1
   zoomLabel.configure(text = "Zoom: {}".format(Globals.zoomLevel))
   displayMap()

def generateMarkerString(currentTweetIndex, tweetLatLonList, mapCenterLatLon):
    displayedTweet = tweetLatLonList[0][currentTweetIndex]
    print("currentIndex", currentTweetIndex)
    print("list",tweetLatLonList)
    if displayedTweet == None:
        displayedTweet = mapCenterLatLon
    displayedTweetString = str(displayedTweet)[1:-1]
        
    otherTweet = []
    for index in range(0,len(tweetLatLonList)):
        if index != currentTweetIndex:
            if tweetLatLonList[index] != None:
                otherTweet.append(tweetLatLonList[index])
            else:
                otherTweet.append(mapCenterLatLon)
    otherTweetString = ""
    for item in otherTweet:
        otherTweetString += "|{}".format(str(item)[1:-1])

    result = "&markers=color:red|{}&markers=color:blue|size:small{}".format(displayedTweetString, otherTweetString)
    result = result.replace(" ","")
#    test = "http://maps.google.com/maps/api/staticmap?center=40.758895,-73.985131&zoom=13&size=400x400&key=AIzaSyDvHY6EBndIg5eS0bFE5Bgbx-7e24LjhQ8" + result
#    print (test)
    return result
   

authTwitter()
