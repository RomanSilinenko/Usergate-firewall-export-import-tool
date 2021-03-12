## Usergate-firewall-export-import-tool
Basic python scripts to export\import firewall rules from Usergate UTM 5 over API

To enable API interface, you have to go to the web admin console with extended feature enabled:
https://<usergate_ip>:8001/?features=zone-xml-rpc

Then go to network \ Zones and enable XML-RPC feature on zone you will be accessing from.

Tested:
- UTM 5 -> UTM 5
- UTM 5 -> UTM 6

## USAGE:
$ python firewall_rulex_exporter.py --help

## TODO 
- Add l7 apps import (export is done)
- Add time criteria export\import
- Add scenario criteria export\import
- Add users criteria export\import
- Unify findXbyY functions
- Do something with imports section. It is not pretty.
