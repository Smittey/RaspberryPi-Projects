import argparse

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

import time
import RPi.GPIO as GPIO
 
DEBUG = True
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GREEN_LED = 18
GPIO.setup(GREEN_LED, GPIO.OUT)



def get_service(api_name, api_version, scope, key_file_location, service_account_email):
  
  credentials = ServiceAccountCredentials.from_p12_keyfile(service_account_email, key_file_location, scopes=scope)
  http = credentials.authorize(httplib2.Http())

  # Build the service object.
  service = build(api_name, 'v3', http=http)

  return service


def get_first_profile_id(service):

  # Get a list of all Google Analytics accounts for this user
  accounts = service.management().accounts().list().execute()

  if accounts.get('items'):
    
    # Get the first Google Analytics account.
    account = accounts.get('items')[0].get('id')

    # Get a list of all the properties for the first account.
    properties = service.management().webproperties().list(accountId=account).execute()

    if properties.get('items'):
      # Get the first property id.
      property = properties.get('items')[0].get('id')

      # Get a list of all views (profiles) for the first property.
      profiles = service.management().profiles().list(accountId=account, webPropertyId=property).execute()

      if profiles.get('items'):
        # return the first view (profile) id.
        return profiles.get('items')[0].get('id')

  return None


def get_results(service, profile_id):

  return service.data().realtime().get(ids='ga:' + '117568134', metrics='rt:activeUsers').execute()


def print_totals_for_all_results(results):

  totals = results.get('totalsForAllResults')

  
  for metric_name, metric_total in totals.iteritems():
    print 'Current Active Users = %s' % metric_total

    if int(float(metric_total)) > 0:
      GPIO.output(GREEN_LED, True)
    else:
      GPIO.output(GREEN_LED, False)



def main():

  scope = ['https://www.googleapis.com/auth/analytics.readonly']
  service_account_email = 'rpi-835@raspberrypianalytics.iam.gserviceaccount.com'
  key_file_location = '/home/pi/client_secrets.p12'
  # Authenticate and construct service.
  service = get_service('analytics', 'v3', scope, key_file_location, service_account_email)

  try:
    while True:
      profile = get_first_profile_id(service)
      print_totals_for_all_results(get_results(service, profile))
      time.sleep(10)
  finally:
      print "cleaning up"
      GPIO.cleanup()
    
if __name__ == '__main__':
  main()
