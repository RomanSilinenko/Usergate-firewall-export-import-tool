## Usergate-firewall-export-import-tool


## RU
Инструмент для переноса конфигураций МЭ и правил NAT между устройствами UserGate UTM версий 5 и 6.

Для того чтобы начать пользоваться API интерфейсом, его нужно активировать:
1. Открыть консоль администратора с включенной скрытой фичей (в 6й версии это доступно сразу) вот по такой ссылке [https://<usergate_ip>:8001/?features=zone-xml-rpc](https://<usergate_ip>:8001/?features=zone-xml-rpc)
2. Пойти в настройки зоны с которой вы будете работать, и активировать функцию **XML-RPC для управления**

Протестировано в следующих вариациях:
- UTM 5 -> UTM 5
- UTM 5 -> UTM 6

#### Общая идея работы скриптов
Вводные:\

Все записи в системе индексируются по внутреннему уникальному идентификатору. Т.е. Имя записи не есть его уникальный идентификатор. И если мы возьмем запись с именем "Block List X" и создадим на другом инстансе запись с точно таким же именем, это будут две разные записи. Поэтому мы не можем прямо переносить записи их одного инстанса в другой.


Пример:\
Вытащим из ЮТМ одно из правил МЭ:
```
{'id': 763,
 'deleted_users': [],
 'name': 'block to Black Listed',
 'guid': '10368c87-8486-4e50-8b4a-4d7457303ae9',
 'description': '',
 'action': 'drop',
 'position': 1,
 '..пропущено...',
 'src_zones': [2],
 'dst_zones': [],
 'src_ips': [['list_id', 1071]],
 'dst_ips': [['list_id', 1040], ['list_id', 1062]],
 'services': [],
 'apps': [],
 'users': [],
 'enabled': True,
 'limit': True,
 '..пропущено...',
 'send_host_icmp': ''}
```

Видим, что все отсылки к IP-листам или к зонам идут через внутренние идентификаторы. Даже если мы предварительно создадим на целевой системе все списки, с точно такими же _именами_, идентификаторы у них будут другие.\
Поэтому делаем так:
1. Выкачиваем из донора различные базы (ip-списки, сервисы, приложения) и правила МЭ.
2. Транслируем ID-шники в читаемые имена.
3. Закачиваем на реципиента все базы
4. Транслируем имена из файлов импорта в корректные для новой системы ID-шники.
5. Пушим конфигурацию.
6. PROFIT.


### Как пользоваться:
Читать встроеный help:
>$ python3 firewall_rulex_exporter.py --help

## EN
Basic python scripts to export\import firewall rules from Usergate UTM 5/6 over API

To enable API interface, you have to go to the web admin console with extended feature enabled:
https://<usergate_ip>:8001/?features=zone-xml-rpc

Then go to network \ Zones and enable XML-RPC feature on zone you will be accessing from.

Tested:
- UTM 5 -> UTM 5
- UTM 5 -> UTM 6

### USAGE:
>$ python3 firewall_rulex_exporter.py --help

### TODO 
- Add l7 apps import (export is done)
- Add time criteria export\import
- Add scenario criteria export\import
- Add users criteria export\import
- Do something with imports section. It is not pretty.
- Unify print arguments
