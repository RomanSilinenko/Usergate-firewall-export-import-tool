#use this script with Pything 2.7
########################################################
#             CONFIGURATION SECTION                    #
# use it if you have issues with ARGPARSE module import#
########################################################
UseraGateAddress = '127.0.0.1'
UserName = 'Admin'
Password = ''

libnames = {'time': False,
            'sys': False,
            'argparse': False,
            'json': False,
            'xmlrpclib': False,
            'unicodecsv': False
            }

for libname in libnames.keys():
    try:
        lib = __import__(libname)
        libnames[libname] = True
    except:
        print(sys.exc_info())
#        sys.exit()
    else:
        globals()[libname] = lib


##  This function returns name of defined network object by its ID
##  NetwoksList is expected to be List
##  search_id   is expected tp be Int
def findNetByID(NetwoksList, search_id):
#    This doesn't work. Dono why.
#    return(item['name'] if item['id'] == id for item in NetwoksList)

    for item in NetwoksList:
        if item['id'] == search_id:
            return item['name']

#if we have argparse module imported, we can use comand line args.
#if we do not have argparse module, one will have to provide configure connection options manually.
if libnames['argparse'] == True:
    argparser = argparse.ArgumentParser(description='Process command line params')
    argparser.add_argument("-s", "--server", required=True, help="Provide usergate appliance IP address")
    argparser.add_argument("-u", "--user", required=False, default='Admin', help="Admin login name (default is Admin)")
    argparser.add_argument("-p", "--passwd", required=False, default='', help="User password (default is blank)")
    args = argparser.parse_args()


    #Connect to API endpoint
    try:
	    server = xmlrpclib.ServerProxy("http://%s:4040/rpc" % args.server if libnames['argparse'] == True else UseraGateAddress)
    except Exception as err:
        sys.exit(err)

print("Successfully connected to " + server.v2.core.node.status()['node_name'])


#Authenticate and get AUTH TOKEN
try:
	token = server.v2.core.login(args.user if libnames['argparse'] == True else UserName, args.passwd if libnames['argparse'] == True else  Password,{})["auth_token"]
except Exception as err:
    sys.exit(err)


print("Ok, we are in, the token is " + token)

print("Starting FW rules export...")



###############################################################
#                     Pull Zones info                         #
###############################################################
print("Pulling avaliable zones...")
zones = server.v1.netmanager.zones.list(token)
#Dump Zones defined in the appliance on disk.
if len(zones) > 0:
    try:
        with open('zones.json','w') as f:
            json.dump(zones, f)
    except Exception as err:
        sys.exit(err)
    print('Exported '+str(len(zones))+' zones.')
    f.close()
time.sleep(1)

###############################################################
#                     Pull services catalog                   #
###############################################################

print("Pulling services catalog...")
services = server.v1.libraries.services.fetch(token, range(100,999))
#Dump Services defined in the appliance on disk.
if len(services) > 0:
    with open('services.json','w') as f:
        json.dump(services, f)
    print("Exported '+str(len(services))+' services.")
    f.close()
time.sleep(1)


###############################################################
#                     Pull l7 apps catalog                    #
###############################################################
l7Apps = server.v2.core.get.l7apps(token, 0, 10000, '')
#Dump l7 apps catalog on disk
if len(l7Apps):
    with open('l7_apps.json','w') as f:
        json.dump(l7Apps, f)
    f.close()
time.sleep(1)


###############################################################
#                     Pull l7 app categories                  #
###############################################################
l7Categories = server.v2.core.get.l7categories(token, 0, 10000, '')
#Dump l7 categories catalog on disk
if len(l7Categories):
    with open('l7_categories.json','w') as f:
        json.dump(l7Categories, f)
    f.close()
time.sleep(1)


###############################################################
#               Pull user defined network objects             #
###############################################################
print("Pulling user defined networks...")
#try:
userDefinedNets= server.v2.nlists.list(token, 'network', 0, 10000, {})
#except Exception as err:


#remove 'Last Update' field contents, bacuase it is not apropriate data to dump to JSON file. When we will create objects in new UTM, it will populate that field with current time
tempUserDefinedNets = list()
for obj in userDefinedNets['items']:
    if obj['editable']:
        obj['last_update'] = ''
        netObjContents = server.v2.nlists.list.list(token, obj['id'],0,1000,'',[])
        obj['netObjContents'] = netObjContents['items']
        tempUserDefinedNets.append(obj)

#tempUserDefinedNets[0]['netObjContents'].append

###############################################################
#            #Dump user defined network objects on disk       #
###############################################################
if len(tempUserDefinedNets):
    with open('network_objects.json','w') as f:
        json.dump(tempUserDefinedNets, f)
    f.close()
    print('Exported '+str(len(tempUserDefinedNets))+' network objects.')
del tempUserDefinedNets
time.sleep(0.5)



###############################################################
#            #Dump firewall rules                             #
###############################################################
#Pull firewall rules
print("Pulling firewall rules...")
totalRules = server.v1.firewall.rules.list(token,0,0,{})['count']
fwRules = server.v1.firewall.rules.list(token,0,totalRules,{})

#Pull all lists mentioned in firewall rules
#Since we do not controll IDs and GUIDs, we have to replace each ID record with its Name of all used Services, Lists and so on. We will use names in import process to restore corect IDs.
for fwRule in fwRules['items']:


    # This section is for Source IP lists
    if len(fwRule['src_ips'])>0:
        for item in fwRule['src_ips']:
            itemID = item[1]
            item.remove(itemID)
            item.append(findNetByID(userDefinedNets['items'],itemID))

    # This section is for Destination IP lists
    if len(fwRule['dst_ips'])>0:
        for item in fwRule['dst_ips']:
            itemID = item[1]
            item.remove(itemID)
            item.append(findNetByID(userDefinedNets['items'],itemID))

    # This section is for Source Zones list
    if len(fwRule['src_zones'])>0:
        for index, item in enumerate(fwRule['src_zones']):
            if type(item) == type(int()):
                response = server.v1.netmanager.zone.fetch(token,item)['name']
                fwRule['src_zones'][index] = response

    # This section is for Destination Zones list
    if len(fwRule['dst_zones'])>0:
        for index, item in enumerate(fwRule['dst_zones']):
            if type(item) == type(int()):
                response = server.v1.netmanager.zone.fetch(token,item)['name']
                fwRule['dst_zones'][index] = response

    # This section is for Services list
    if len(fwRule['services'])>0:
        for index, item in enumerate(fwRule['services']):
            if type(item) == type(int()):
                response = server.v1.libraries.service.fetch(token,item)['name']
                fwRule['services'][index] = response


    # This section is for Apps lists
#    if len(fwRule['apps'])>0:
#        temporaryItem = list()
#        for app in fwRule['apps']:
#            if len(app) == 2:
#                l7Type, AppID = app
#                if l7Type == 'app':
#                    response = server.v2.core.find.l7apps(token,[AppID])
#                    print response
#                    temporaryItem.append(['app',response[0]['name']])
#                    #fwRule['apps'].append(temporaryItem)
#                elif l7Type == 'ro_group':
#                   response = server.v2.core.find.l7categories(token,[AppID])
#                    print response
#                    temporaryItem.append(['ro_group',response[0]['name']])
#                    #fwRule['apps'].append(temporaryItem)
#        fwRule['apps'] = temporaryItem
#        temporaryItem = []


#dump firewall rules on disk
with open('firewall_rules.json','w') as f:
    json.dump(fwRules, f)
f.close()

#Create also CSV view of firewall rules is we have unicodecsv module imported
if libnames['unicodecsv'] == True:
    fieldnames = fwRules['items'][0].keys()
    with open('firewall_rules.csv','w') as f:
        write = unicodecsv.DictWriter(f, fieldnames=fieldnames, dialect='excel', encoding='utf-8-sig')
        write.writeheader()
        write.writerows(fwRules['items'])
    f.close()

###############################################################
#            #Dump NAT rules                                  #
###############################################################
#Pull nat rules
print("Pulling NAT rules...")
totalNatRules = server.v1.traffic.rules.list(token, 0,0,{})['count']
natRules = server.v1.traffic.rules.list(token, 0, totalNatRules, {})

#Pull all lists mentioned in nat rules
#Since we do not controll IDs and GUIDs, we have to replace each ID record with its Name of all used Services, Lists and so on. We will use names in import process to restore corect IDs.
for natRule in natRules['items']:
#    sys.stdout.write(next(spinner))
#    sys.stdout.flush()
#    sys.stdout.write('\b')
#    time.sleep(0.5)

    # This section is for Source IP lists
    if len(natRule['source_ip'])>0:
        for item in natRule['source_ip']:
            itemID = item[1]
            item.remove(itemID)
            item.append(findNetByID(userDefinedNets['items'],itemID))

    # This section is for Destination IP lists
    if len(natRule['dest_ip'])>0:
        for item in natRule['dest_ip']:
            itemID = item[1]
            item.remove(itemID)
            item.append(findNetByID(userDefinedNets['items'],itemID))

    # This section is for Source Zones list
    if len(natRule['zone_in'])>0:
        for index, item in enumerate(natRule['zone_in']):
            if type(item) == type(int()):
                response = server.v1.netmanager.zone.fetch(token,item)['name']
                natRule['zone_in'][index] = response

    # This section is for Destination Zones list
    if len(natRule['zone_out'])>0:
        for index, item in enumerate(natRule['zone_out']):
            if type(item) == type(int()):
                response = server.v1.netmanager.zone.fetch(token,item)['name']
                natRule['zone_out'][index] = response

    # This section is for Services list
    if len(natRule['service'])>0:
        for index, item in enumerate(natRule['service']):
            if type(item) == type(int()):
                response = server.v1.libraries.service.fetch(token,item)['name']
                natRule['service'][index] = response


#dump nat rules on disk
with open('nat_rules.json','w') as f:
    json.dump(natRules, f)
f.close()

#Create also CSV view of firewall rules is we have unicodecsv module imported
if libnames['unicodecsv'] == True:
    fieldnames = natRules['items'][0].keys()
    with open('nat_rules.csv','w') as f:
        write = unicodecsv.DictWriter(f, fieldnames=fieldnames, dialect='excel', encoding='utf-8-sig')
        write.writeheader()
        write.writerows(natRules['items'])
    f.close()



print("Done!")
