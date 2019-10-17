# CLI tool to add missing interfaces and IP addresses to NetBox
<br>
This will will logon to a device and pull down a list of all interfaces with IPs assigned
<br>
It will then check the device in NetBox and if the interface / IP is missing, it will be added
<br>
Contains checks so that it won't add an IP if it already exists

## Usage
Pass device name and username via CLI args
<br>
`python netbox_interface_ip_add.py -d switch1.mydomain.net -u luca`
