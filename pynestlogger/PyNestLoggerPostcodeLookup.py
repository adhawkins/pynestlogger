import requests

class  PyNestLoggerPostcodeLookup:
	def __init__(self, key, country, postcode):
		r = requests.get("https://maps.googleapis.com/maps/api/geocode/json?address=sn55rb&country=gb&key=" + key)
		#print(r.url)
		data = r.json()
		self.latitude=data['results'][0]['geometry']['location']['lat']
		self.longitude=data['results'][0]['geometry']['location']['lng']
