import xmlrpclib
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
	server = xmlrpclib.ServerProxy("http://%s:4040/rpc" % args.server, allow_none=1)
except Exception as err:
    sys.exit(err)


print("Successfully connected to " + server.v2.core.node.status()['node_name'])


#Authenticate and get AUTH TOKEN
try:
    token = server.v2.core.login(args.user,args.passwd,{})["auth_token"]
except Exception as err:
    sys.exit(err)


print("Ok, we are in, the token is " + token)


##############################################################
#                -=[ Delete old FW Rules ]=-                 #
# NOTE: we have to delete 'em BEFORE objects in these rules. #
##############################################################

#       Pull firewall rules from UTM we are importing in.
##############################################################
# try:
#     totalRules = server.v1.firewall.rules.list(token,0,0,{})['count']
#     fwRules = server.v1.firewall.rules.list(token,0,totalRules,{})
# except Exception as err:
#     sys.exit(err)
#
# #       Remove all defined firewall rules.
# ##############################################################
# print("*\tNow clearing firewall rules...")
#
# for fwRule in fwRules['items']:
#     time.sleep(0.1)
#
#     try:
#         server.v1.firewall.rule.delete(token, fwRule['id'])
#     except Exception as err:
#         print(err)
#     print('- \trule '+ fwRule['name']+ ' removed.')
#
#
# ##############################################################
# #                -=[ Delete old NAT Rules ]=-                #
# # NOTE: we have to delete 'em BEFORE objects in these rules. #
# ##############################################################
#
# #       Pull NAT rules from UTM we are importing in.
# ##############################################################
#
# try:
#     totalNatRules = server.v1.traffic.rules.list(token, 0,0,{})['count']
#     natRules = server.v1.traffic.rules.list(token, 0, totalNatRules, {})
# except Exception as err:
#     print(err)
#
#
# #       Remove all defined NAT rules.
# ##############################################################
# print("*\tNow clearing NAT rules...")
#
# for natRule in natRules['items']:
#     time.sleep(0.1)
#
#     try:
#         server.v1.traffic.rule.delete(token, natRule['id'])
#     except Exception as err:
#         print(err)
#     print('-\trule '+ natRule['name']+ ' removed.')
#
#
#
#
# ############################################################
# #                -=[ Import Zones ]=-                      #
# ############################################################
#
# #       Load zone objects from file
# #################################################
# print("*\tImporting Zones...")
# try:
#     with open('zones.json', 'r') as fh:
#         importZones = json.load(fh)
# except Exception as err:
#     sys.exit(err)
# print("file zones.json loaded.")
# print("found " + str(len(importZones)) +" zones.")
#
# #       Pull zones from UTM
# #################################################
# try:
#     UTMzones = server.v1.netmanager.zones.list(token)
# except Exception as err:
#     sys.exit(err)
#
# #Since we cannot just remove existing zones, we will created new zones based on exported data.
# #The user will have to fine tune this crap by hands after import.
# c = 0
# for zone in importZones:
#     #We will import only zones we did not find in UTM we importing in. e.g. if we see there is already 'Trusted' zone, we will not import it.
#     if not foundZoneByName(UTMzones, zone['name']):
#         try:
#             print("Importing zone: "+zone['name'])
#             server.v1.netmanager.zone.add(token, zone)
#             c +=1
#         except Exception as err:
#             print(err)
#
# print('*\tImported '+ str(c) + ' Zones')
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
    UTM2ServicesList = server.v1.libraries.services.fetch(token,range(100,9999))
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

############################################################
#           -=[ Import firewall rules ]=-                  #
############################################################


#       Load firewall rules info from file
#################################################
# try:
#     with open('firewall_rules.json', 'r') as fh:
#         importFirewallrules = json.load(fh)
# except Exception as err:
#     sys.exit(err)
# fh.close()
# print('firewall_rules.json loaded.')
# print('found '+ str(importFirewallrules['count'])+' Firewall rules.')
# rules_left = importFirewallrules['count']
#
#
# #       Import firewall rules
# ##############################################################
# try:
#     #Pull updated zones list from UTM
#     UTM2zones = server.v1.netmanager.zones.list(token)
#     #Pull updated services list from UTM
#     UTM2ServicesList = server.v1.libraries.services.fetch(token,range(100,9999))
#     #print 'Got updated service list. Total '+ str(len(UTM2ServicesList))+' service definitions'
#     #Pull updated networks list from UTM
#     UTM2NetworksList = server.v2.nlists.list(token, 'network',0,1000,'')['items']
#     #Pull L7 apps catalog from UTM
#     #UTM2L7AppCatalog = server.v2.nlists.list(token, 'network',0,1000,'')['items']
# except Exception as err:
#     print(err)
#
# print('****  -=[ Starting Firewall rules IMPORT ]=-   ****')
# for importFwRule in importFirewallrules['items']:
#     #replace SRC zone names with local IDs
#     for index, SrcZone  in enumerate(importFwRule['src_zones']):
#         importFwRule['src_zones'][index] = findZoneIDByName(UTMzones, SrcZone)
#     #replace DST zone names with local IDs
#     for index, DstZone in enumerate(importFwRule['dst_zones']):
#         importFwRule['dst_zones'][index] = findZoneIDByName(UTMzones, DstZone)
#
#     #replace SRC IP list names with local IDs
#     for index, SrcIP in enumerate(importFwRule['src_ips']):
#         listId, SrcIP_name = SrcIP
#         importFwRule['src_ips'][index] = [listId, findNetIDByName(UTM2NetworksList, SrcIP_name)]
#     #replace DST IP list names with local IDs
#     for index, DstIP in enumerate(importFwRule['dst_ips']):
#         listId, DstIP_name = DstIP
#         importFwRule['dst_ips'][index] = [listId, findNetIDByName(UTM2NetworksList, DstIP_name)]
#
#     #replace service names with lical IDs
#     for index, ServiceName in enumerate(importFwRule['services']):
#         importFwRule['services'][index] = findServiceIDByName(UTM2ServicesList, ServiceName)
#
#
#     importFwRule['apps'] = []
#     #replace L7 Application names with local IDs
# #    newAppsList = list()
# #    if len(importFwRule['apps']) > 0:
# #        #if it is not empty, then last element is the readable list of applications. we pasted it during export process.
# #        for app in importFwRule['apps'].pop():
# #            if app[0] == 'app':
# #                newAppsList.append([app[0],findL7AppIDByName()])
# #            elif app[0] == 'ro_group':
# #                newAppsList.append([app[0],findL7CatIDByName()])
# #            else:
# #                pass
# #        importFwRule['apps'] = newAppsList
# #    del newAppsList
#
#
#     print('Importing rule:'+' ['+str(importFirewallrules['count'])+'/'+str(importFirewallrules['count'] - rules_left +1) +']  Name: '+ importFwRule['name'])
#     #print 'Service: '+str(importFwRule['services'])
#     #time.sleep(10)
#     try:
#         server.v1.firewall.rule.add(token, importFwRule)
#         rules_left -=1
#     except Exception as err:
#         print('!!! Not imported:'+' ['+str(importFirewallrules['count'])+'/'+str(importFirewallrules['count'] - rules_left+ 1) +']'+importFwRule['name'])
#         print(err)
#         c+=1
#         pass
#     c+=1
#
# print('*\tImported '+str(c)+' Firewall rules')
# c = 0
#
#
# ############################################################
# #           -=[ Import NAT rules ]=-                       #
# ############################################################
#
#
# #       Load NAT rules info from file
# #################################################
# try:
#     with open('nat_rules.json', 'r') as fh:
#         importNATrules = json.load(fh)
# except Exception as err:
#     print("Cannot open NAT rules import file. NAT rules will not be imported.")
#     sys.exit(err)
# fh.close()
# print('nat_rules.json loaded.')
# print('found '+ str(importNATrules['count'])+' NAT rules.')
# rules_left = importNATrules['count']
#
# if rules_left > 0:
#     print('****  -=[ Starting NAT rules IMPORT ]=-   ****')
#     for importNATrule in importNATrules['items']:
#         #replace SRC zone names with local IDs
#         for index, SrcZone  in enumerate(importNATrule['zone_in']):
#             importNATrule['zone_in'][index] = findZoneIDByName(UTMzones, SrcZone)
#         #replace DST zone names with local IDs
#         for index, DstZone in enumerate(importNATrule['zone_out']):
#             importNATrule['zone_out'][index] = findZoneIDByName(UTMzones, DstZone)
#
#         #replace SRC IP list names with local IDs
#         for index, SrcIP in enumerate(importNATrule['source_ip']):
#             listId, SrcIP_name = SrcIP
#             importNATrule['source_ip'][index] = [listId, findNetIDByName(UTM2NetworksList, SrcIP_name)]
#         #replace DST IP list names with local IDs
#         for index, DstIP in enumerate(importNATrule['dest_ip']):
#             listId, DstIP_name = DstIP
#             importNATrule['dest_ip'][index] = [listId, findNetIDByName(UTM2NetworksList, DstIP_name)]
#
#         #replace service names with lical IDs
#         for index, ServiceName in enumerate(importNATrule['service']):
#             importNATrule['service'][index] = findServiceIDByName(UTM2ServicesList, ServiceName)
#
#         print('Importing rule:'+' ['+str(importNATrules['count'])+'/'+str(importNATrules['count'] - rules_left +1) +']  Name: '+ importNATrule['name'])
#         #print 'Service: '+str(importFwRule['services'])
#         #time.sleep(10)
#         try:
#             server.v1.traffic.rule.add(token, importNATrule)
#             rules_left -=1
#         except Exception as err:
#             print('!!! Not imported:'+' ['+str(importNATrules['count'])+'/'+str(importNATrules['count'] - rules_left+ 1) +']'+importNATrule['name'])
#             print(err)
#             c+=1
#             pass
#         c+=1
#
# print('*\tImported '+str(c)+' NAT rules')
# c = 0
#

print("Done!")


#Orignal
#In [56]: fwRules['items'][7]['services']
#Out[56]: [120, 121, 158, 104]

#In [57]: fwRules['items'][7]['apps']
#Out[57]: [['ro_group', 4], ['ro_group', 6], ['app', 7738], ['app', 230], ['app', 5577]]

#In [58]: fwRules['items'][7]['dst_zones']
#Out[58]: [2, 4, 1]

#In [59]: fwRules['items'][7]['dst_ips']
#Out[59]: [['list_id', 1039], ['list_id', 1002], ['list_id', 1018]]
