import requests
import datetime

class  PyNestLoggerConditionsLookup:
	def __init__(self, key, latitude, longitude):
		r = requests.get("https://api.wunderground.com/api/"+key+"/geolookup/q/"+str(latitude)+","+str(longitude)+".json")
		#print(r.url)
		data = r.json()

		location=data['location']['l']

		r = requests.get("http://api.wunderground.com/api/13828230156f18f7/conditions/"+location+".json")
		#print(r.url)
		data = r.json()

		self.time=datetime.datetime.fromtimestamp(float(data['current_observation']['observation_epoch']))
		self.temp=data['current_observation']['temp_c']
