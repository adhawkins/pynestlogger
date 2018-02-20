from argparse import ArgumentParser
import nest
from sys import version_info
from pynestlogger.Config import Config
from pynestlogger.PyNestLoggerDB import PyNestLoggerDB
import time

def main():
	parser = ArgumentParser()
	parser.add_argument("-r", "--reauth", help="force reauthorisation", action="store_true")
	parser.add_argument("-k", "--client-id", help="Nest API key")
	parser.add_argument("-s", "--client-secret", help="Nest API secret")
	parser.add_argument("-d", "--db-host", help="Database host")
	parser.add_argument("-n", "--db-db", help="Database name")
	parser.add_argument("-u", "--db-user", help="Database user")
	parser.add_argument("-p", "--db-passwd", help="Database password")
	args = parser.parse_args()

	config = Config()

	if ("client-id" not in config.json and not args.client_id) or \
		("client-secret" not in config.json and not args.client_secret) or \
		("db-host" not in config.json and not args.db_host) or \
		("db-db" not in config.json and not args.db_db) or \
		("db-user" not in config.json and not args.db_user) or \
		("db-passwd" not in config.json and not args.db_passwd):
		print("API key, secret, db host, db, user and password must be in either config or on command line")

		parser.print_help()
		exit(-1)

	save_config = False

	if args.client_id:
		config.json["client-id"] = args.client_id
		save_config = True

	if args.client_secret:
		config.json["client-secret"] = args.client_secret
		save_config = True

	if args.db_host:
		config.json["db-host"] = args.db_host
		save_config = True

	if args.db_db:
		config.json["db-db"] = args.db_db
		save_config = True

	if args.db_user:
		config.json["db-user"] = args.db_user
		save_config = True

	if args.db_passwd:
		config.json["db-passwd"] = args.db_passwd
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

	db = PyNestLoggerDB(host = config.json['db-host'],
						database = config.json['db-db'],
						user = config.json['db-user'],
						password = config.json['db-passwd'])

	for structure in napi.structures:
		for thermostat in structure.thermostats:
			db.record_measurement(structure._serial, thermostat.device_id, thermostat.temperature, thermostat.humidity, thermostat.target, thermostat.hvac_state)


