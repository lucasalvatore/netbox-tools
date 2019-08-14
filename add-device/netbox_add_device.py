import pynetbox
import sys
from sys import argv
import requests
import argparse

nb = pynetbox.api('<NETBOX_URL>',
private_key_file='<PATH TO PRIVATE KEY>',
token='<YOUR TOKEN>'
                  )

nb_sites = requests.get("http://netbox./api/dcim/sites/").json()
nb_device_roles = requests.get("http://netbox./api/dcim/device-roles/").json()
nb_device_types = requests.get("http://netbox./api/dcim/device-types/").json()
nb_device_status = requests.get("http://netbox./api/dcim/_choices/").json()
nb_dev_url = "http://netbox./api/dcim/interfaces/?device_id="
nb_ipam_url = "http://netbox./api/ipam/ip-addresses/"

#Define arguments
def arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--dev_name',
		'-d',
		default=None,
		help='Device Name',
		required=True
	)

	parser.add_argument(
		'--role',
		'-r',
		default=None,
		help='Device role e.g "TOR Switch',
		required=True
	)

	parser.add_argument(
		'--manufacturer',
		'-ma',
		default=None,
		help='Device Manufacturer',
		required=True
	)

	parser.add_argument(
		'--model',
		'-mo',
		default=None,
		help='Device Model Number',
		required=True
	)
	parser.add_argument(
		'--serial',
		'-s',
		default=None,
		help='Device Serial Numner',
		required=True
	)
	parser.add_argument(
		'--site',
		'-si',
		default=None,
		help='Site where device is installed',
		required=True
	)
	parser.add_argument(
		'--status',
		'-st',
		default=None,
		help='Device Status (e.g. "Active"',
		required=True
	)

	parser.add_argument(
		'--iface',
		'-i',
		default=None,
		help='Devices Interface where the IPs will be assigned',
		required=False
	)
	parser.add_argument(
		'--ipv4',
		'-ip4',
		default=None,
		help='IPv4 address of mgmt interface',
		required=False
	)
	parser.add_argument(
		'--ipv6',
		'-ip6',
		default=None,
		help='IPv6 address of mgmt interface',
		required=False
	)
	return parser.parse_args()

args = arguments()

# covert names passed in argments to netbox IDs
for name in nb_sites['results']:
	if args.site == name['name'].upper():
		args.site = (name['id'])

for name in nb_device_roles['results']:
	if args.role == name['name']:
		args.role = (name['id'])

for model in nb_device_types['results']:
	if args.model == model['model']:
		args.model = (model['id'])

for label in nb_device_status['device:status']:
	if args.status == label['label']:
		args.status = (label['value'])

# add device to netbox
try:
	nb.dcim.devices.create(
		name = args.dev_name,
		device_role = args.role,
       	device_type = args.model,
       	serial = args.serial,
       	site = args.site,
       	status = args.status
       	)
except pynetbox.RequestError as e:
	print("Error is", e.error)
else:
	print(args.dev_name,"Has been added to NetBox")


#Exit the script if no interface or IPs were added
if args.iface == None:
	print("No interface passed, exiting")
	sys.exit()


'''
Update the device just added with an IPv4 and IPv6 address
This requires finding the ID of the device and interface where the IPs will be added,
along with the IDs of the IPs
'''

#get device id
dev_id = nb.dcim.devices.get(name=args.dev_name).id

#gets device interface list
dev_int = requests.get(nb_dev_url + str(dev_id) + "&limit=100000").json()	

#prepare device to update
dev_update = nb.dcim.devices.get(dev_id)




#get interface ID from device inerface list
for name in dev_int['results']:
     if args.iface == name['name']:
          args.iface = (name['id'])

 
#Add IPv4 to interface 
if args.ipv4 == None:
	print("No IPv4 address passed")
elif args.ipv4 != None:
	try:
		nb.ipam.ip_addresses.create(
			address = args.ipv4,
			interface = args.iface)
	except pynetbox.RequestError as e:
		print("Error is", e.error)
	else:
		pass
	ip4_id = requests.get(nb_ipam_url + "?address=" + args.ipv4).json()
	for address in ip4_id['results']:
		if args.ipv4 == address['address']:
			ip4_id = (address['id'])
			try:
				dev_update.update({
					"primary_ip4": ip4_id
					})
			except pynetbox.RequestError as e:
				print("Error is", e.error)
			else:
				print(args.ipv4, "Added and set to primary on", args.dev_name)



#Add IPv6 to interface 
if args.ipv6 == None:
	print("No IPv6 address passed")
elif args.ipv6 != None:
	try:
		nb.ipam.ip_addresses.create(
			address =  args.ipv6,
			interface = args.iface)
	except pynetbox.RequestError as e:
		print("Error is", e.error)
	else:
		pass
	ip6_id = requests.get(nb_ipam_url + "?address=" + args.ipv6).json()
	for address in ip6_id['results']:
		if args.ipv6 == address['address']:
			ip6_id = (address['id'])
			try:
				dev_update.update({
					"primary_ip6": ip6_id
				})
			except pynetbox.RequestError as e:
				print("Error is", e.error)
			else:
				print(args.ipv6, "Added and set to primary on", args.dev_name)

	
