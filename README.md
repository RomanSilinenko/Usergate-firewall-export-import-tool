# Usergate-firewall-export-import-tool
Basic python scripts to export\import firewall rules from Usergate UTM 5 over API

To anable API interface, you have to go to the web admin console with extended feature anabled:
https://<usergate_ip>:8001/?features=zone-xml-rpc

Then go to network \ Zones and enable XML-RPC feature on zone you will be accessing from.

Scripts we developed for python 2.7. So may require some tuning to run with Python 3.


# USAGE:
$ python firewall_rulex_exporter.py --help
usage: firewall_rulex_exporter.py [-h] -s SERVER [-u USER] [-p PASSWD]

Process command line params

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Provide usergate appliance IP address
  -u USER, --user USER  Admin login name (default is Admin)
  -p PASSWD, --passwd PASSWD
                        User password (default is blank)

# TODO 
- Add l7 apps export\import
- Add time criteria export\import
- Add scenario criteria export\import
- Add users criteria export\import
- Adapt to Python 3
