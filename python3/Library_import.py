import xmlrpc.client
import json
import argparse
import itertools
import sys
import os
import time


# Are we ready to import?
files = ['zones.json' ,'network_objects.json','services.json']
for fileName in files:
    if not os.path.isfile(fileName):
        sys.exit('Warning! Can\'t find '+fileName+' file. Run rules export script first. Exiting...')


#Just a spinning dash for terminal output
spinner = itertools.cycle(['-', '/', '|', '\\'])

# Return True is zoneName exists in zonesList
def foundZoneByName(zonesList, zoneName):
    for zone in zonesList:
        if zone['name'] == zoneName:
            return True
    return False

def findL7AppIDByName(l7Catalog, l7AppName):
    for app in l7Catalog:
        if app['name'] == str(l7AppName):
            return cat['app_id']

def findL7CatIDByName(l7Catalog, l7CatName):
    for cat in l7Catalog:
        if cat['name'] == str(l7CatName):
            return cat['id']

def findZoneIDByName(zonesList, zoneName):
    for zone in zonesList:
        if zone['name'] == str(zoneName):
            return zone['id']

def findServiceIDByName(seerviceList, serviceName):
    for service in seerviceList:
        if service['name'] == str(serviceName):
            return service['id']

def findNetIDByName(networksList, networkName):
    for net in networksList:
        if net['name'] == str(networkName):
            return net['id']


argparser = argparse.ArgumentParser(description='Process command line params')
argparser.add_argument("-s", "--server", required=True, help="Provide usergate appliance IP address")
argparser.add_argument("-u", "--user", required=False, default='Admin', help="Admin login name (default is Admin)")
argparser.add_argument("-p", "--passwd", required=False, default='', help="User password (default is blank)")
args = argparser.parse_args()

#Connect to API endpoint
try:
	server = xmlrpc.client.ServerProxy("http://%s:4040/rpc" % args.server, allow_none=1)
except Exception as err:
    sys.exit(err)


print("Successfully connected to " + server.v2.core.node.status()['node_name'])


#Authenticate and get AUTH TOKEN
try:
    token = server.v2.core.login(args.user,args.passwd,{})["auth_token"]
except Exception as err:
    sys.exit(err)


print("Ok, we are in, the token is " + token)



c = 0
#
############################################################
#   -=[ Import user defined network objects ]=-           #
############################################################

#       Load network objects info from file
#################################################
print('*\tImporting Network Objects...')
try:
    with open('network_objects.json', 'r') as fh:
        ImportedNetworkObjects = json.load(fh)
except Exception as err:
    sys.exit(err)
fh.close()
print('file network_objects.json loaded.')
print('found '+str(len(ImportedNetworkObjects))+ ' network objects.')

#       Pull network lists from UTM we are importing in.
##############################################################
try:
    UTM2NetworksList = server.v2.nlists.list(token, 'network',0,1000,'')['items']
except Exception as err:
    print(err)

#       Remove all lists we can remove (pass built in lists)
##############################################################
print('clearing network objects...')
for ListItem in UTM2NetworksList:
    if ListItem['editable']:
        try:
            server.v2.nlists.delete(token, ListItem['id'])
        except Exception as err:
            print(err)

#       Import list of network objects
##############################################################
for ListItem in ImportedNetworkObjects:
    netObjContents = ListItem.pop('netObjContents')
    try:
        print('Importing IP-list: '+ListItem['name'])
        uid = server.v2.nlists.add(token, ListItem)
        server.v2.nlists.list.add.items(token, uid, netObjContents)
        c += 1
    except Exception as err:
        print(err)
print('*\tImported '+str(c)+ ' network objects')
c = 0

############################################################
#   -=[ Import user defined services objects ]=-           #
############################################################
print('*\tImporting User defined Services Objects...')
#       Load services info from file
#################################################
try:
    with open('services.json', 'r') as fh:
        ImportedServicesObjects = json.load(fh)
except Exception as err:
    sys.exit(err)
print('file services.json loaded.')
print('found '+str(len(ImportedServicesObjects))+' services objects.')

#       Pull network lists from UTM we are importing in.
##############################################################
try:
    UTM2ServicesList = server.v1.libraries.services.fetch(token,list(range(100,9999)))
except Exception as err:
    print(err)

#       Remove all defined services.
##############################################################
print('clearing service definitions...')
if len(UTM2ServicesList) > 0:
    for service in UTM2ServicesList:
        try:
            server.v1.libraries.service.delete(token,service['id'])
        except Exception as err:
            print(err)

#       Import list of services objects
##############################################################
for ListItem in ImportedServicesObjects:
    try:
        print('Importing Service definition: '+ListItem['name'])
        server.v1.libraries.service.add(token, ListItem)
        c +=1
    except Exception as err:
        print(err)
print('*\tImported '+ str(c)+ ' service objects')
c = 0


print("Done!")
