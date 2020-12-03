# RouterOS-api

[![Build Status](https://github.com/socialwifi/RouterOS-api/actions/workflows/python.yml/badge.svg)](https://github.com/socialwifi/RouterOS-api/actions/workflows/python.yml)
[![Latest Version](https://img.shields.io/pypi/v/RouterOS-api.svg)](https://pypi.python.org/pypi/RouterOS-api/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/RouterOS-api.svg)](https://pypi.python.org/pypi/RouterOS-api/)
[![Wheel Status](https://img.shields.io/pypi/wheel/RouterOS-api.svg)](https://pypi.python.org/pypi/RouterOS-api/)
[![License](https://img.shields.io/pypi/l/RouterOS-api.svg)](https://github.com/socialwifi/RouterOS-api/blob/master/LICENSE)

Python API to RouterBoard devices produced by [MikroTik](https://mikrotik.com/) written by [Social WiFi](https://socialwifi.com).

<a href="https://socialwifi.com">
<img src="https://socialwifi.com/media/static/logo-gradient.svg" width="200" title="Social WiFi logo" alt="Social WiFi logo"/>
</a>

## Usage

### Connection

```python
import routeros_api

connection = routeros_api.RouterOsApiPool('IP', username='admin', password='', plaintext_login=True)
api = connection.get_api()
```
Use `plaintext_login=True` option when connecting to RouterOS version 6.43 and newer.

#### Connection parameters

```python
routeros_api.RouterOsApiPool(
    host,
    username='admin',
    password='',
    port=8728,
    plaintext_login=True,
    use_ssl=False,
    ssl_verify=True,
    ssl_verify_hostname=True,
    ssl_context=None,
)
```

Parameters:

* `host` - String - Hostname or IP of device

Optional Parameters:

* `username` - String - Login username - Default 'admin'
* `password` - String - Login password - Default empty string
* `port` - Integer - TCP Port for API - Default 8728 or 8729 when using SSL
* `plaintext_login` - Boolean - Try plaintext login (for RouterOS 6.43 onwards) - Default **False**
* `use_ssl` - Boolean - Use SSL or not? - Default **False**
* `ssl_verify` - Boolean - Verify the SSL certificate? - Default **True**
* `ssl_verify_hostname` - Boolean - Verify the SSL certificate hostname matches? - Default **True**
* `ssl_context` - Object - Pass in a custom SSL context object. Overrides other options. - Default **None**

#### Using SSL

If we want to use SSL, we can simply specify `use_ssl` as `True`:

```python
connection = routeros_api.RouterOsApiPool('<IP>', username='admin', password='', use_ssl=True)
```

This will automatically verify SSL certificate and hostname. 
The most flexible way to modify SSL parameters is to provide an SSL Context object using the 
`ssl_context` parameter, but for typical use-cases with self-signed certificates, the shorthand options of
 `ssl_verify` and `ssl_verify_hostname` are provided.

e.g. if using a self-signed certificate, you can (but probably shouldn't) use:

```python
connection = routeros_api.RouterOsApiPool(
    '<IP>',
    username='admin',
    password='',
    use_ssl=True,
    ssl_verify=False,
    ssl_verify_hostname=False,
)
```

#### Login for RouterOS v6.43 onwards

RouterOS Versions v6.43 onwards now use a different login method. 
The disadvantage is that it passes the password in plain text. 
For security we only attempt the plaintext login if requested using the `plaintext_login` parameter. 
It is highly recommended only to use this option with SSL enabled.

```python
routeros_api.RouterOsApiPool(host, username='admin', password='', plaintext_login=True)
```

#### Handling non UTF-8 characters

The API does not assume any particular encoding, so non utf-8 characters will
not be shown correctly.
A default encoding can be specified if needed. For some cases the `latin-1` 
encoding will be the best one to use, for others - `windows-1250` will work 
better. 
Ref. https://forum.mikrotik.com/viewtopic.php?t=106053#p528460

It is possible to use specific encoding by defining custom default structure 
like this:

```python
import collections
import routeros_api
from routeros_api.api_structure import StringField

connection = routeros_api.RouterOsApiPool('ip', username='admin', password='password', plaintext_login=True)
api = connection.get_api()
# This part here is important:
default_structure = collections.defaultdict(lambda: StringField(encoding='windows-1250'))
api.get_resource('/system/identity', structure=default_structure).get()
```


### Execute Commands

Call this with a resource and parameters as name/value pairs.

```python
api.get_resource('/').call('<resource>', { <dict of params> })
```

You can also use the "binary" version, but in this case, all dict values
should be encoded to bytes and the result will be returned as bytes.

```python
api.get_binary_resource('/').call('<resource>', { <dict of params> })
```

#### Examples

```python
>>> api.get_resource('/tool').call('fetch', {'url': 'http://example.com', 'dst-path': 'output.html'})
[{'status': 'connecting', '.section': '0'}, {'status': 'finished', 'downloaded': '1', 'total': '1', 'duration': '1s', '.section': '1'}]

>>> api.get_resource('/').call('ping', {'address': '8.8.8.8', 'count': '4'})
[
 {'seq': '0', 'host': '8.8.8.8', 'size': '56', 'ttl': '58', 'time': '14ms612us', 'sent': '1', 'received': '1', 'packet-loss': '0', 'min-rtt': '14ms612us', 'avg-rtt': '14ms612us', 'max-rtt': '14ms612us'}, 
 {'seq': '1', 'host': '8.8.8.8', 'size': '56', 'ttl': '58', 'time': '22ms237us', 'sent': '2', 'received': '2', 'packet-loss': '0', 'min-rtt': '14ms612us', 'avg-rtt': '18ms424us', 'max-rtt': '22ms237us'}, 
 {'seq': '2', 'host': '8.8.8.8', 'size': '56', 'ttl': '58', 'time': '13ms823us', 'sent': '3', 'received': '3', 'packet-loss': '0', 'min-rtt': '13ms823us', 'avg-rtt': '16ms890us', 'max-rtt': '22ms237us'}, 
 {'seq': '3', 'host': '8.8.8.8', 'size': '56', 'ttl': '58', 'time': '8ms614us', 'sent': '4', 'received': '4', 'packet-loss': '0', 'min-rtt': '8ms614us', 'avg-rtt': '14ms821us', 'max-rtt': '22ms237us'}
]
```

### Fetch List/Resource

```python
list = api.get_resource('/command')
```

#### Example

```python
list_queues = api.get_resource('/queue/simple')
```

#### Show all elements

```python
list_queues.get()
```

### Add rules

```python
list.add(attribute='vale', attribute_n='value')
```

**NOTE**: Attributes with `-`, like `max-limit` use underscore `_`: `max_limit`

#### Example:

```python
list_queues.add(name='001', max_limit='512k/4M', target='192.168.10.1/32')
```

### Update Values

```python
list.set(id, attributes)
```

#### Example:

```python
list_queues.set(id='*2', name='john')
```

### Get element:

```python
list.get(attribute=value)
```

#### Example:

```python
list_queues.get(name='john')
```

### Remove element:

```python
list.remove(id)
```

#### Example:

```python
list_queues.remove(id='*2')
```

### Close conection:

```python
connection.disconnect()
```

### Return results and count of results

Let's take DHCP leases as an example.

CLI: `/ip/dhcp-server/lease/print`

```python
api.get_resource('/ip/dhcp-server/lease').get()
```

Now, let's use `count-only`.

CLI: `/ip/dhcp-server/lease/print count-only` (returns 13)

```python
>>> api.get_resource('/ip/dhcp-server/lease').call('print', {'count-only': None}).done_message

{'ret': '13'}
```

Now, let's use `count-only` and `where`.

CLI: `/ip/dhcp-server/lease/print count-only where server=developers` (returns 4)

```python
>>> api.get_resource('/ip/dhcp-server/lease').call('print', {'count-only': None}, {'server': 'developers'}).done_message

{'ret': '4'}
```

Now, let's use `count-only` and `where` with boolean value.

CLI: `/ip/route/pri count-only where static` (returns 1)

```python
>>> api.get_resource('/ip/route').call('print', {'count-only': None}, {'static': 'yes'}).done_message

{'ret': '1'}
```

### Run script and get output

The example script only prints "hello". Here's a simplified example of how 
to run it and get the output:

```python
>>> api.get_resource('/system/script').get()[0]['source']
'/put "hello"'
>>> response = api.get_resource('/system/script').call('run', {'number': '0'})
>>> response.done
True
>>> response.done_message['ret']
'hello'
```

### Run monitor and get output

CLI command: `/interface/ethernet/poe/monitor numbers=0 once`

```python
>>> response = api.get_resource('/interface/ether/poe').call('monitor', {'numbers': '0', 'once': None})
>>> response
[{'name': 'ether10', 'poe-out': 'auto-on', 'poe-out-status': 'waiting-for-load'}]
```

### Set value using numbers

CLI command: `/interface/ethernet/poe set poe-out=off 0`

```python
api.get_resource('/interface/ethernet/poe').call('set', {'poe-out': 'off', 'numbers': '0'}
```

### Set value using id

```python
>> api.get_resource('/interface/ethernet/poe').call('print')
[{'id': '*B', 'name': 'ether10', 'poe-out': 'off', 'poe-priority': '10', 'poe-lldp-enabled': 'false', 'power-cycle-ping-enabled': 'false', 'power-cycle-interval': 'none'}]

>> api.get_resource('/interface/ethernet/poe').call('set', {'poe-out': 'off', '.id': "*B"})
```

### Add and remove item

```python
list_address = api.get_resource('/ip/firewall/address-list')
list_address.add(address='192.168.0.1', comment='P1', list='10M')
response = list_address.get(comment='P1')
list_address.remove(id=response[0]['id'])
```
