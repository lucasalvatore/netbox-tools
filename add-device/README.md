This tool will add a device to netbox, give lo0 an IPv4 and IPv6 address, and set the addresses as primay.

Multiple arguments are required, some and mandatory, some are not. 

If you want to just add a device without mgmt IPs, do not include the interface, ipv4 or ipv6 flags. 

run python netbox_add_device.py -h to see info on arguments:

```(venv) Lucas-MacBook-Pro:venv luca$ python netbox_add_device.py -h
usage: netbox_add_device.py [-h] --dev_name DEV_NAME --role ROLE
                             --manufacturer MANUFACTURER --model MODEL
                             --serial SERIAL --site SITE --status STATUS
                             [--iface IFACE] [--ipv4 IPV4] [--ipv6 IPV6]

optional arguments:
  -h, --help            show this help message and exit
  --dev_name DEV_NAME, -d DEV_NAME
                        Device Name
  --role ROLE, -r ROLE  Device role e.g "TOR Switch
  --manufacturer MANUFACTURER, -ma MANUFACTURER
                        Device Manufacturer
  --model MODEL, -mo MODEL
                        Device Model Number
  --serial SERIAL, -s SERIAL
                        Device Serial Numner
  --site SITE, -si SITE
                        Site where device is installed
  --status STATUS, -st STATUS
                        Device Status (e.g. "Active"
  --iface IFACE, -i IFACE
                        Devices Interface where the IPs will be assigned
  --ipv4 IPV4, -ip4 IPV4
                        IPv4 address of mgmt interface
  --ipv6 IPV6, -ip6 IPV6
                        IPv6 address of mgmt interface```
                        
 python netbox_add_device.py -d luca-test22 -r "TOR Switch" -ma Juniper -mo EX4300-48T -s abc123 -si EWR1 -st Active -i ae0 -ip4 6.7.8.9/32 -ip6 2001::a/128
luca-test22 Has been added to NetBox
6.7.8.9/32 Added and set to primary on luca-test22
2001::a/128 Added and set to primary on luca-test22
                        
                      
