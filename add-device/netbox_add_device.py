import pynetbox
import sys
from sys import argv
import requests

nb = pynetbox.api('[NETBOX_URL',
private_key_file='/path/to/key/',
token='xxx'
                  )

nb_sites = requests.get("http://netbox/api/dcim/sites/").json()
nb_device_roles = requests.get("http://netbox/api/dcim/device-roles/").json()
nb_device_types = requests.get("http://netbox/api/dcim/device-types/").json()
nb_device_status = requests.get("http://netbox/api/dcim/_choices/").json()
nb_dev_url = "http://netbox/api/dcim/interfaces/?device_id="
nb_ipam_url = "http://netbox/api/ipam/ip-addresses/"

script, dev_name, role, manufacturer, device_type, serial_number, site, status, iface, ip4_dev_ip_address, ip6_dev_ip_address = argv

# covert names passed in argments to netbox IDs
for name in nb_sites['results']:
	if site == name['name'].upper():
		site = (name['id'])

for name in nb_device_roles['results']:
	if role == name['name']:
		role = (name['id'])

for model in nb_device_types['results']:
	if device_type == model['model']:
		device_type = (model['id'])

for label in nb_device_status['device:status']:
	if status == label['label']:
		status = (label['value'])

# add device to netbox
try:
	nb.dcim.devices.create(
		name = dev_name,
		device_role = role,
       	device_type = device_type,
       	serial = serial_number,
       	site = site,
       	status = status
       	)
except pynetbox.RequestError as e:
	print("Error is", e.error)
else:
	print(dev_name,"Has been added to NetBox")


#get device id
dev_id = nb.dcim.devices.get(name=dev_name).id

#gets device interface list
dev_int = requests.get(nb_dev_url + str(dev_id) + "&limit=100000").json()	

#get interface ID from device inerface list
for name in dev_int['results']:
     if iface == name['name']:
          iface = (name['id'])

 
#Add IP to interface 
try:
	nb.ipam.ip_addresses.create(
		address = ip4_dev_ip_address,
		interface = iface)

	nb.ipam.ip_addresses.create(
		address = ip6_dev_ip_address,
		interface = iface)
except pynetbox.RequestError as e:
	print("Error is", e.error)
else:
	print(ip4_dev_ip_address, "&", ip6_dev_ip_address, "Have been added to", dev_name)

#set IP to primary
#get IP address data
ip4_id = requests.get(nb_ipam_url + "?address=" + ip4_dev_ip_address).json()
ip6_id = requests.get(nb_ipam_url + "?address=" + ip6_dev_ip_address).json()

#get IPv4 address ID
for address in ip4_id['results']:
	if ip4_dev_ip_address == address['address']:
		ip4_id = (address['id'])

#get IPv6 address ID
for address in ip6_id['results']:
	if ip6_dev_ip_address == address['address']:
		ip6_id = (address['id'])

#update device with primary IP
dev_update = nb.dcim.devices.get(dev_id)

#udpate device
try:
	dev_update.update({
		"primary_ip4": ip4_id,
		"primary_ip6": ip6_id
		})
except pynetbox.RequestError as e:
	print("Error is", e.error)
else:
	print(ip4_dev_ip_address, "&", ip6_dev_ip_address, "Have been set to primary on", dev_name)
