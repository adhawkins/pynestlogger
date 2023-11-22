import os.path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from urllib.parse import urlparse, parse_qs
from collections import namedtuple


class NestThermostat:
    SCOPES = ["https://www.googleapis.com/auth/sdm.service"]

    def __init__(self, auth_file, secrets_file, project_id):
        self.auth_file = auth_file
        self.secrets_file = secrets_file
        self.project_id = project_id
        self.credentials = None

        self.authenticate()

    def authenticate(self):
        if os.path.exists(self.auth_file):
            self.credentials = Credentials.from_authorized_user_file(
                self.auth_file, NestThermostat.SCOPES
            )

        if not self.credentials or not self.credentials.valid:
            if (
                self.credentials
                and self.credentials.expired
                and self.credentials.refresh_token
            ):
                self.credentials.refresh(Request())
            else:
                # Create the flow using the client secrets file from the Google API
                # Console.
                flow = Flow.from_client_secrets_file(
                    self.secrets_file,
                    scopes=NestThermostat.SCOPES,
                    redirect_uri="https://www.google.com",
                )

                # Tell the user to go to the authorization URL.
                auth_url, _ = flow.authorization_url(prompt="consent")

                print("Please go to this URL: {}".format(auth_url))

                # The user will get a URL containing authorization code.

                uri = input("Enter the URL you were redirected to: ")
                parsed = urlparse(uri)
                if parsed.query:
                    query = parse_qs(parsed.query)
                    if "code" in query:
                        # This code is used to get the access token.

                        flow.fetch_token(code=query["code"][0])
                        self.credentials = flow.credentials

            if self.credentials and self.credentials.valid:
                with open(self.auth_file, "w") as token:
                    token.write(self.credentials.to_json())

    def getMeasurement(self):
        if self.credentials and self.credentials.valid:
            service = build("smartdevicemanagement", "v1", credentials=self.credentials)

            enterprises = service.enterprises()

            devices = enterprises.devices()
            devices_list = devices.list(
                parent=f"enterprises/{self.project_id}"
            ).execute()

            device = devices_list["devices"][0]

            if "traits" in device:
                traits = device["traits"]

                if (
                    ("sdm.devices.traits.Humidity" in traits)
                    and ("sdm.devices.traits.Temperature" in traits)
                    and ("sdm.devices.traits.ThermostatTemperatureSetpoint" in traits)
                    and ("sdm.devices.traits.ThermostatHvac" in traits)
                ):
                    Measurement = namedtuple(
                        "Measurement", "ambient humidity target state"
                    )
                    measurement = Measurement(
                        traits["sdm.devices.traits.Temperature"][
                            "ambientTemperatureCelsius"
                        ],
                        traits["sdm.devices.traits.Humidity"]["ambientHumidityPercent"],
                        traits["sdm.devices.traits.ThermostatTemperatureSetpoint"][
                            "heatCelsius"
                        ],
                        traits["sdm.devices.traits.ThermostatHvac"]["status"],
                    )
                    return measurement
        else:
            print("No creds")

        return None
