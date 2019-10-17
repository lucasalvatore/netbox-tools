import pynetbox
import napalm
from napalm import get_network_driver
import re
import argparse
import sys

nb = pynetbox.api(
    http://[NETBOX_URL]",
    private_key_file="/path/to/key",
    token="token",
)


def arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dev_name", "-d", default=None, help="Device Name", required=True
    )

    parser.add_argument(
        "--username", "-u", default=None, help="Username", required=True
    )

    return parser.parse_args()


args = arguments()


def main():
    dev_name = args.dev_name
    driver = get_network_driver("junos")
    optional_args = {"allow_agent": "True", "use_keys": "True"}
    device = driver(args.dev_name, args.username, "", optional_args=optional_args)
    device.open()
    print(f"Getting interface list from {args.dev_name}")
    interfaces = device.get_interfaces_ip()
    device.close()

    v4_ints = {}
    v6_ints = {}
    v4_ips_to_check = []
    v4_ips_to_update = []
    v4_ip_update = {}
    v6_ips_to_check = []
    v6_ips_to_update = []
    v6_ip_update = {}
    ignore_ints = "bme|em1|em2|jsrv|lo"

    # create new dictionay with just interface as key and ip,mask,form_factor as list of values
    for k, v in interfaces.items():
        for family, address in v.items():
            for a, b in address.items():
                for x, y in b.items():
                    if family == "ipv4":
                        if not re.search(ignore_ints, k):
                            if "xe-" in k:
                                v4_ints.update(
                                    {
                                        k.replace(".0", ""): [
                                            str(a) + "/" + str(y),
                                            "1200",
                                        ]
                                    }
                                )
                            elif "ae" in k:
                                v4_ints.update(
                                    {
                                        k.replace(".0", ""): [
                                            str(a) + "/" + str(y),
                                            "200",
                                        ]
                                    }
                                )
                            elif "irb" in k:
                                v4_ints.update(
                                    {k.replace(".0", ""): [str(a) + "/" + str(y), "0"]}
                                )
                            elif "ge" in k:
                                v4_ints.update(
                                    {
                                        k.replace(".0", ""): [
                                            str(a) + "/" + str(y),
                                            "1000",
                                        ]
                                    }
                                )
                            elif "et" in k:
                                v4_ints.update(
                                    {
                                        k.replace(".0", ""): [
                                            str(a) + "/" + str(y),
                                            "1400",
                                        ]
                                    }
                                )
                    elif family == "ipv6":
                        if not re.search(ignore_ints, k):
                            if "2604" in a:
                                if "xe-" in k:
                                    v6_ints.update(
                                        {
                                            k.replace(".0", ""): [
                                                str(a) + "/" + str(y),
                                                "1200",
                                            ]
                                        }
                                    )
                                elif "ae" in k:
                                    v6_ints.update(
                                        {
                                            k.replace(".0", ""): [
                                                str(a) + "/" + str(y),
                                                "200",
                                            ]
                                        }
                                    )
                                elif "irb" in k:
                                    v6_ints.update(
                                        {
                                            k.replace(".0", ""): [
                                                str(a) + "/" + str(y),
                                                "0",
                                            ]
                                        }
                                    )
                                elif "ge" in k:
                                    v6_ints.update(
                                        {
                                            k.replace(".0", ""): [
                                                str(a) + "/" + str(y),
                                                "1000",
                                            ]
                                        }
                                    )
                                elif "et" in k:
                                    v6_ints.update(
                                        {
                                            k.replace(".0", ""): [
                                                str(a) + "/" + str(y),
                                                "1400",
                                            ]
                                        }
                                    )

    # Get netbox device ID
    dev_id = nb.dcim.devices.get(name=args.dev_name).id

    # Add V4 interfaces to netbox
    print(f"Adding Interfaces to Device {args.dev_name}")
    for interface, values in v4_ints.items():
        try:
            nb.dcim.interfaces.create(
                device=dev_id, name=interface, form_factor=values[1], enabled="true"
            )
        except pynetbox.RequestError as err:
            print("NOTE PyNetBox Error is ", err.error)
    # Get interface IDs and append to v4 dict
    for interface, values in v4_ints.items():
        interface_id = nb.dcim.interfaces.get(
            name=interface, device=args.dev_name
        ).id
        v4_ints[interface].append(interface_id)

    # Get interface IDs and append to v6 dict
    for interface, values in v6_ints.items():
        interface_id = nb.dcim.interfaces.get(
            name=interface, device=args.dev_name
        ).id
        v6_ints[interface].append(interface_id)

    ##add IPv4 to netbox
    print(f"Adding IPv4 addresses to Device {args.dev_name}")
    for interface, values in v4_ints.items():
        # check if IP already exists
        v4_check = nb.ipam.ip_addresses.filter(values[0])
        if len(v4_check) == 0:
            print(f"IP {values[0]} not found, adding to {args.dev_name}")
            try:
                nb.ipam.ip_addresses.create(address=values[0], interface=values[2])
            except pynetbox.RequestError as err:
                print("NOTE PyNetBox Error is ", err.error)
        else:
            print(f"IP {values[0]} already exists, not adding.")
            v4_ips_to_check.append(values[0])

    # Check if IP is not assigned to an interface, add to list if found
    print("Checking for unassigned IPv4 addresses")
    for line in v4_ips_to_check:
        print(f"Checking {line}")
        ip = nb.ipam.ip_addresses.get(q=line)
        if ip.interface == None:
            v4_ips_to_update.append(line)

    # Search v4_ints dict for IPs found above and copy values to new dict
    if len(v4_ips_to_update) != 0:
        print("updating unassigned ips...")
        for interface, values in v4_ints.items():
            for line in v4_ips_to_update:
                if line == values[0]:
                    v4_ip_update.update({interface: [values[0], values[1], values[2]]})

        # Update IP with interface ID
        for interfaces, values in v4_ip_update.items():
            try:
                ip = nb.ipam.ip_addresses.get(q=values[0])
                print(f"Found existing IP {values[0]} without Interface... Updating")
                ip.update({"interface": values[2]})
            except pynetbox.RequestError as err:
                print("NOTE PyNetBox Error is ", err.error)
    else:
        if len(v4_ips_to_update) == 0:
            pass

    # Print add Ipv6 to NetBox
    print(f"Adding IPv6 addresses to Device {args.dev_name}")
    for interface, values in v6_ints.items():
        # check if IP already exists
        v6_check = nb.ipam.ip_addresses.filter(values[0])
        if len(v6_check) == 0:
            print(f"IP {values[0]} not found, adding to {args.dev_name}")
            try:
                nb.ipam.ip_addresses.create(address=values[0], interface=values[2])
            except pynetbox.RequestError as err:
                print("NOTE PyNetBox Error is ", err.error)
        else:
            print(f"IP {values[0]} already exists, not adding.")
            v6_ips_to_check.append(values[0])

    # Check if IP is not assigned to an interface, add to list if found
    print("Checking for unassigned IPv6 addresses")
    for line in v6_ips_to_check:
        print(f"Checking {line}")
        ip = nb.ipam.ip_addresses.get(q=line)
        if ip.interface == None:
            v6_ips_to_update.append(line)

    # Search v6_ints dict for IPs found above and copy values to new dict
    if len(v6_ips_to_update) != 0:
        print("updating unassigned ips...")
        for interface, values in v6_ints.items():
            for line in v6_ips_to_update:
                if line == values[0]:
                    v6_ip_update.update({interface: [values[0], values[1], values[2]]})

        # Update IP with interface ID
        for interfaces, values in v6_ip_update.items():
            try:
                ip = nb.ipam.ip_addresses.get(q=values[0])
                print(f"Found existing IP {values[0]} without Interface... Updating")
                ip.update({"interface": values[2]})
            except pynetbox.RequestError as err:
                print("NOTE PyNetBox Error is ", err.error)
    else:
        if len(v6_ips_to_update) == 0:
            pass
    print("Done!")


if __name__ == "__main__":
    main()
# check int description on ESRs to get ESR <> BSR link / IP and add to device
