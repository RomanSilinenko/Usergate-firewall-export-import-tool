#use this script with Pything 3
########################################################
#             CONFIGURATION SECTION                    #
# use it if you have issues with ARGPARSE module import#
########################################################
UseraGateAddress = '127.0.0.1'
UserName = 'Admin'
Password = ''

import xmlrpc.client

libnames = {'time': False,
            'sys': False,
            'argparse': False,
            'json': False,
            #'xmlrpc.client': False,
            }

for libname in libnames.keys():
    try:
        lib = __import__(libname, globals(), locals(), [], 0)
        libnames[libname] = True
    except:
        print(sys.exc_info())
#        sys.exit()
    else:
        globals()[libname] = lib


#if we have argparse module imported, we can use comand line args.
#if we do not have argparse module, one will have to provide configure connection options manually.
if libnames['argparse'] == True:
    argparser = argparse.ArgumentParser(description='Process command line params')
    argparser.add_argument("-s", "--server", required=True, help="Provide UserGate appliance IP address")
    argparser.add_argument("-u", "--user", required=False, default='Admin', help="Admin login name (default is Admin)")
    argparser.add_argument("-p", "--passwd", required=False, default='', help="User password (default is blank)")
    args = argparser.parse_args()

    #Connect to API endpoint
    try:
        server = xmlrpc.client.ServerProxy("http://%s:4040/rpc" % args.server if libnames['argparse'] == True else UseraGateAddress)
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
services = server.v1.libraries.services.list(token, 0, 9999, {}, [])
servicesList = []
for service in services['items']:
    servicesList.append(service['id'])
services = server.v1.libraries.services.fetch(token, servicesList)

#Dump Services defined in the appliance on disk.
if len(services) > 0:
    with open('services.json','w') as f:
        json.dump(services, f)
    print("Exported "+str(len(services))+" services.")
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


print("Done!")
