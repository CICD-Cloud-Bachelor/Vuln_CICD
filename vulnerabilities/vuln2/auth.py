import getopt
import sys
import json
import re
from msal import PublicClientApplication

def printUsage():
  print('auth.py -u <username> -p <password> -a <authority> -r <resource> -c <clientId>')

def main(argv):
  try:
    options, args = getopt.getopt(argv, 'hu:p:a:r:c:')
  except getopt.GetoptError:
    printUsage()
    sys.exit(-1)

  username = ''
  password = ''
  authority = ''
  resource = ''

  clientId = ''
    
  for option, arg in options:
    if option == '-h':
      printUsage()
      sys.exit()
    elif option == '-u':
      username = arg
    elif option == '-p':
      password = arg
    elif option == '-a':
      authority = arg
    elif option == '-r':
      resource = arg
    elif option == '-c':
      clientId = arg

  if username == '' or password == '' or authority == '' or resource == '' or clientId == '':
    printUsage()
    sys.exit(-1)

  # ONLY FOR DEMO PURPOSES AND MSAL FOR PYTHON
  # This shouldn't be required when using proper auth flows in production.  
  if authority.find('common') > 1:
    authority = authority.split('/common')[0] + "/organizations"
   
  app = PublicClientApplication(client_id=clientId, authority=authority)  
  
  result = None  

  if resource.endswith('/'):
    resource += ".default"    
  else:
    resource += "/.default"
  
  # *DO NOT* use username/password authentication in production system.
  # Instead, consider auth code flow and using a browser to fetch the token.
  result = app.acquire_token_by_username_password(username=username, password=password, scopes=[resource])  
  print(result['access_token'])

if __name__ == '__main__':  
  main(sys.argv[1:])