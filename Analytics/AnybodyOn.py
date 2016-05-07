import argparse
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

import time
import RPi.GPIO as GPIO
 
import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read("ga-config.ini")
Config.sections()
Config.options('config')

DEBUG = True
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GREEN_LED = 18
GPIO.setup(GREEN_LED, GPIO.OUT)



def get_service(api_name, api_version, scope, key_file_location, service_account_email):
  
  credentials = ServiceAccountCredentials.from_p12_keyfile(service_account_email, key_file_location, scopes=scope)
  http = credentials.authorize(httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http)

  return service



def get_results(service, profile_id):
  
  return service.data().realtime().get(ids='ga:' + profile_id, metrics='rt:activeUsers').execute()


def print_totals_for_all_results(results):

  totals = results.get('totalsForAllResults')
  
  for metric_name, metric_total in totals.iteritems():
    print 'Current Active Users = %s' % metric_total

    if int(float(metric_total)) > 0:
      GPIO.output(GREEN_LED, True)
    else:
      GPIO.output(GREEN_LED, False)



def main():

  scope = Config.get('config', 'scope')
  service_account_email = Config.get('config', 'service_account_email')
  key_file_location = Config.get('config', 'key_file_location')
  version = Config.get('config', 'version')
  api_name = Config.get('config', 'api_name')
  analytics_id = Config.get('config', 'analytics_id')
  
  # Authenticate and construct service.
  service = get_service(api_name, version, scope, key_file_location, service_account_email)

  try:
    while True:
      #profile = get_first_profile_id(service)
      print_totals_for_all_results(get_results(service, analytics_id))
      time.sleep(1)
  finally:
      print "cleaning up"
      GPIO.cleanup()
    
if __name__ == '__main__':
  main()
