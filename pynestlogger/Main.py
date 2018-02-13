from argparse import ArgumentParser
from Config import Config
import nest
from sys import version_info

def main():
	parser = ArgumentParser()
	parser.add_argument("-r", "--reauth", help="force reauthorisation", action="store_true")
	parser.add_argument("-k", "--client-id", help="Nest API key")
	parser.add_argument("-s", "--client-secret", help="Nest API secret")
	args = parser.parse_args()

	config = Config()

	if ("client-id" not in config.json and not args.client_id) or \
		("client-secret" not in config.json and not args.client_secret):
		print "API key and secret must be in either config or on command line"

		parser.print_help()
		exit(-1)

	save_config = False

	if args.client_id:
		config.json["client-id"] = args.client_id
		save_config = True

	if args.client_secret:
		config.json["client-secret"] = args.client_secret
		save_config = True

	napi = nest.Nest(client_id=config.json["client-id"],
											client_secret=config.json["client-secret"],
											access_token_cache_file="pynestlogger-auth.json",
												)

	if args.reauth or napi.authorization_required:
		print('Go to ' + napi.authorize_url + ' to authorize, then enter PIN below')
		if version_info[0] < 3:
			pin = raw_input("PIN: ")
		else:
			pin = input("PIN: ")

		napi.request_token(pin)

	if save_config:
		config.write()

	for structure in napi.structures:
		print ('Structure %s' % structure.name)
		print ('    Away: %s' % structure.away)
		print ('    Devices:')

		for device in structure.thermostats:
			print ('        Device: %s' % device.name)
			print ('            Temp: %0.1f' % device.temperature)

