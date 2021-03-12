## Usergate-firewall-export-import-tool


## RU
Инструмент для переноса конфигураций МЭ и правил NAT между устройствами UserGate UTM версий 5 и 6.

Для того чтобы начать пользоваться API интерфейсом, его нужно активировать:
1. Открыть консоль администратора с включенной скрытой фичей (в 6й версии это доступно сразу) вот по такой ссылке [https://<usergate_ip>:8001/?features=zone-xml-rpc](https://<usergate_ip>:8001/?features=zone-xml-rpc)
2. Пойти в настройки зоны с которой вы будете работать, и активировать функцию **XML-RPC для управления**

Протестировано в следующих вариациях:
- UTM 5 -> UTM 5
- UTM 5 -> UTM 6

### Как пользоваться:
Читать встроеный help:
**$ python3 firewall_rulex_exporter.py --help**

## EN
Basic python scripts to export\import firewall rules from Usergate UTM 5/6 over API

To enable API interface, you have to go to the web admin console with extended feature enabled:
https://<usergate_ip>:8001/?features=zone-xml-rpc

Then go to network \ Zones and enable XML-RPC feature on zone you will be accessing from.

Tested:
- UTM 5 -> UTM 5
- UTM 5 -> UTM 6

### USAGE:
**$ python3 firewall_rulex_exporter.py --help**

### TODO 
- Add l7 apps import (export is done)
- Add time criteria export\import
- Add scenario criteria export\import
- Add users criteria export\import
- Do something with imports section. It is not pretty.
- Unify print arguments
