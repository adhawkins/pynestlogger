from argparse import ArgumentParser
from sys import version_info
from pynestlogger.Config import Config
from pynestlogger.PyNestLoggerDB import PyNestLoggerDB
from pynestlogger.NestThermostat import NestThermostat

import requests
import socket
import requests.packages.urllib3.util.connection as urllib3_cn


def main():
    parser = ArgumentParser()
    parser.add_argument("-d", "--db-host", help="Database host")
    parser.add_argument("-n", "--db-db", help="Database name")
    parser.add_argument("-u", "--db-user", help="Database user")
    parser.add_argument("-p", "--db-passwd", help="Database password")
    parser.add_argument("-i", "--project-id", help="Project ID")
    parser.add_argument("-f", "--config-file", help="Config file name")
    parser.add_argument("-a", "--auth-file", help="File for storing auth information")
    parser.add_argument(
        "-s", "--secrets-file", help="File containing secrets information"
    )

    args = parser.parse_args()

    config = Config(args.config_file)

    if (
        ("db-host" not in config.json and not args.db_host)
        or ("db-db" not in config.json and not args.db_db)
        or ("db-user" not in config.json and not args.db_user)
        or ("db-passwd" not in config.json and not args.db_passwd)
        or ("project-id" not in config.json and not args.project_id)
        or ("auth-file" not in config.json and not args.auth_file)
        or ("secrets-file" not in config.json and not args.secrets_file)
    ):
        print(
            "db host, db name, db user, db password, project ID, auth file and secrets file must be in either config or on command line"
        )

        parser.print_help()
        exit(-1)

    save_config = False

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

    if args.project_id:
        config.json["project-id"] = args.project_id
        save_config = True

    if args.auth_file:
        config.json["auth-file"] = args.auth_file
        save_config = True

    if args.secrets_file:
        config.json["secrets-file"] = args.secrets_file
        save_config = True

    if save_config:
        config.write()

    nest = NestThermostat(
        config.json["auth-file"], config.json["secrets-file"], config.json["project-id"]
    )

    measurement = nest.getMeasurement()

    def allowed_gai_family():
        """
        https://github.com/shazow/urllib3/blob/master/urllib3/util/connection.py
        """
        family = socket.AF_INET
        if urllib3_cn.HAS_IPV6:
            family = socket.AF_INET6  # force ipv6 only if it is available
        return family

    urllib3_cn.allowed_gai_family = allowed_gai_family

    loft = requests.get("http://nas.gently.org.uk:5000/").json()

    db = PyNestLoggerDB(
        host=config.json["db-host"],
        database=config.json["db-db"],
        user=config.json["db-user"],
        password=config.json["db-passwd"],
    )

    db.record_measurement(
        ambient=measurement.ambient,
        humidity=measurement.humidity,
        target=measurement.target,
        state=measurement.state,
        loft=loft[0]["internal temperature"],
    )
