# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Subnet Designer
# Writen by Jordan Tremaine | P445327
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-==-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=


# ---------------------------------------------------------------------------------------------------------------------
# Data Structures Legend
# ---------------------------------------------------------------------------------------------------------------------
# ///LISTS                  In most cases, Sorted by useable hosts Large to Small
#
# network_id_list           [10.0.0.0, 10.0.0.8, 10.0.0.16]
# network_id_cidr_list      [10.0.0.0/29, 10.0.0.8/29, 10.0.0.16/29]
# ip_mod_netstat_list       [ipaddress.ip_address(10.0.0.0/29), ipaddress.ip_address(10.0.0.8/29)]
# ip_netmask_list           [10.0.0.0/255.255.255.248, 10.0.0.8/255.255.255.248]
# ip_netmask_list_split     [10.0.0.0 255.255.255.248, 10.0.0.8 255.255.255.248]
# hosts_in_subnet           [10.0.0.1, 10.0.0.2, 10.0.0.3, 10.0.0.4]
# hosts_in_subnet_netmask   [10.0.0.1 255.255.255.248, 10.0.0.2 255.255.255.248]
#
# ///DICTIONARIES           In most cases, Sorted by useable hosts Large to Small
#
# unsorted_vlans_hosts_dict {vlan10: 20, vlan30: 100, vlan20: 60}          -UNSORTED
# sorting_list              = Keys in unsorted_vlans_host_dict (vlans) sorted by values = (vlan30, vlan20, vlan10)
# network_vlan_dict         {network1: vlan30, network2: vlan20, network3: vlan10}  (Built using sorting_list)
# vlan_hostswanted_dict     {vlan30: 100, vlan20: 60, vlan10: 20} -SORTED
# network_hostswanted_dict  {network1: 120, network2: 80, network: 50}
# ip_netmask_dictionary     {network1: 10.0.0.0 255.255.255.248, network2: 10.0.0.8 255.255.255.248}
# hosts_in_subnet_dict      {network1: 6, network2: 6, network3: 6)
# hosts_in_subnet_netmask_dict {network1: [10.0.0.0 255.255.255.248, 10.0.0.8: 255.255.255.248], network2: etc}


# Modules I need
import ipaddress
import math
from time import sleep
import sys

# Script starts by calling class, class initiates all the data structures I need
# Probably don't need this many representations of IP and VLSM...
# But having things formatted for CISCO future proofs the usefulness of the script
class subnetdesigner:
    def __init__(self):
        #print('^INIT subnet designer')
        self.startloop = True
        self.commence = 'on'

        self.cidrlist = ['/30', '/29', '/28', '/27', '/26', '/25', '/24', '/23', '/22', '/21', '/20', '/19', '/18', '/17', '/16']

        # Define these variables as lists or dictionaries
        self.unsorted_vlan_hosts_dict = {}
        self.network_vlan_dict = {}
        self.hostlist = []
        self.inthostlist = []
        self.sorting_list = []
        self.ip_netmask_list = []
        self.total_hosts_per_subnet_list = []
        self.network_id_list = []
        self.network_id_cidr_list = []
        self.ipmod_netstart_list = []
        self.ip_netmask_list = []
        self.ip_netmask_list_split = []
        self.total_hosts_per_subnet_list = []
        self.ip_netmask_dictionary = {}
        self.hosts_in_subnet_dictionary = {}
        self.hosts_in_subnet_netmask_dictionary = {}

        # Call start function
        self.start_function()

    # Get Network ID from user
    #   - I need the entry to be a 'ip_address' for later
    #   - But I also need to verify its a valid network address now
    #   - Use a short For Loop, if ip_address as ip_network returns ALL exceptions, then I know the user gave me junk
    #   - If however some attempts get through, turn on a switch, if that switch is on after the loop, continue
    #   - If it turns out to be junk the interceptor will detect it
    # Get number of vlans / subnets the user wants
    def myip_subnets_wanted(self):
        print('')
        print('---------------------------------------------------------------------------')
        try:
            self.myip = (ipaddress.ip_address(input("Enter NETWORK ID, ex.'10.0.0.0': ")))
        except Exception:
            print("Error: Not a network address try again")
            self.myip_subnets_wanted()

        check_ip = self.myip
        true_switch = 'off'
        print('')
        #print("Checking if your network ID is valid")
        truecounter = 0
        falsecounter = 0
        for item in self.cidrlist:
            is_ip_network_addr = str(check_ip) + item
            try:
                justchecking = ipaddress.ip_network(is_ip_network_addr)
                #print(is_ip_network_addr, 'TRUE')
                truecounter = truecounter + 1
                true_switch = 'on'
            except Exception:
                #print(is_ip_network_addr, 'FALSE')
                falsecounter = falsecounter + 1
        print('Valid Networks Found:', truecounter)
        print('Invalid Networks Found:', falsecounter)


        if true_switch == 'off':
            print('')
            print("Error: No valid network addresses found, try again")
            self.myip_subnets_wanted()
        elif true_switch == 'on':
            print('Continue')
            print('')
            print('---------------------------------------------------------------------------')
            self.number_subnets = int(input('How many subnets do you need?: '))
            if self.number_subnets in range(1, 100):
                self.hosts_per_subnet_list()
            else:
                print('Error: Please Enter subnet range between 1-100')
                self.myip_subnets_wanted()


    # Input = Enter VLAN name, Enter hosts wanted per subnet
    # Work = Build dict {Sales:50, Management:100, Accounts:8}
    # Work = Build host list and order [100, 50, 8]
    # Work = Order the dictionary
    # Call to sorting function
    def hosts_per_subnet_list(self):
        print('')
        hw_counter = 0

        while self.startloop == True:
            # keep going until number of subnets reached
            if hw_counter < self.number_subnets:
                hw_counter = hw_counter + 1
                vlan_name = input(str(hw_counter) + " Enter VLAN ID ex. vlan " + str(hw_counter) + '0' + " -name: ")

                if '-' not in vlan_name:
                    print('Error: Your vlan name is not structured correctly')
                    self.hosts_per_subnet_list()

                key = vlan_name
                int_hostitem = input(str(hw_counter) + ' Enter Hosts Wanted: ')
                value = int(int_hostitem)
                str_hostitem = str(int_hostitem)

                # key = vlan 10, value = hostswanted
                self.unsorted_vlan_hosts_dict[key] = value
                # add hosts wanted to list
                self.hostlist.append(str_hostitem)

                print(str_hostitem, "hosts entered")
                print("")
            else:
                break

        # Sort list of hosts wanted from highest to lowest
        self.hostlist.sort(reverse=True)

        # Convert string to int for i in hostlist
        self.inthostlist = [int(i) for i in self.hostlist]

        # Sort hostlist from largest to smallest hostwanted
        self.inthostlist.sort(reverse=True)

        # This orders the items in vlan:hostswanted dictionary by the size of the value
        # We go from this {Sales:50, Management:100, Accounts:8) to this {Management:100, Sales:50, Accounts:8)
        # Sort dict pairs, by size of their keys
        self.sorting_list = sorted(self.unsorted_vlan_hosts_dict, key=self.unsorted_vlan_hosts_dict.get, reverse=True)

        # Call sorting hat
        self.sorting_hat()
    # Output = Inthostlist =  [600, 150, 50, 20, 10, 10]

    # This function takes this dictionary - {Management:100, Sales:50, Accounts:8)
    # Builds this new dictionary from keys - {Network1: Management, Network2: Sales, Network3: Accounts}
    # Now the host list is sorted by size, and the network dictionary is sorted by size
    def sorting_hat(self):
        sort_counter = 0
        for vlan_name in self.sorting_list:
            sort_counter = sort_counter + 1
            str_sort_counter = str(sort_counter)
            key = 'network' + str(str_sort_counter)
            self.network_vlan_dict[key] = vlan_name
            #print("\n", '^network vlan dict', self.network_vlan_dict)
        self.ip_networks_builder()

    # This function takes a list of numbers and matches to vlsm
    # Should probably be passing into the function, but no need
    def ip_networks_builder(self):
        #print('^Matching hosts wanted to variable length subnets')
        hl_counter = 0
        for i in self.inthostlist:
            hl_counter = hl_counter + 1
            #print('Subnet', hl_counter)

            # (2)Resolve hosts wanted to a network size for the operating octet only

            if 1 <= i < 3:
                networks_in_octet = int(64)
                cidr = '/30'
            elif 3 <= i < 7:
                networks_in_octet = int(32)
                cidr = '/29'
            elif 7 <= i < 15:
                networks_in_octet = int(16)
                cidr = '/28'
            elif 15 <= i < 31:
                networks_in_octet = int(8)
                cidr = '/27'
            elif 31 <= i < 63:
                networks_in_octet = int(4)
                cidr = '/26'
            elif 63 <= i < 127:
                networks_in_octet = int(2)
                cidr = '/25'
                # Octet border
            elif 127 <= i < 255:
                networks_in_octet = int(1)
                cidr = '/24'

            # Class B Networks
            elif 255 <= i < 511:
                networks_in_octet = int(128)
                cidr = '/23'
            elif 511 <= i < 1023:
                networks_in_octet = int(64)
                cidr = '/22'
            elif 1023 <= i < 2047:
                networks_in_octet = int(32)
                cidr = '/21'
            elif 2047 <= i < 5095:
                networks_in_octet = int(16)
                cidr = '/20'
            elif 5095 <= i < 8191:
                networks_in_octet = int(8)
                cidr = '/19'
            elif 8191 <= i < 16383:
                networks_in_octet = int(4)
                cidr = '/18'
            elif 16383 <= i < 32767:
                networks_in_octet = int(2)
                cidr = '/17'
            elif 32767 <= i < 65535:
                networks_in_octet = int(1)
                cidr = '/16'
            else:
                print('Hosts wanted out of range /16 - /30, try again')
                self.myip_subnets_wanted()

            # Finds number of raw hosts
            if 1 <= i < 255:
                add_this = int(256 / networks_in_octet)
            elif 255 <= i < 65535:
                add_this = int(65536 / networks_in_octet)

            # Previously we checked to see if the network ID matched any network ID possibility
            # Now we check if network ID can match the CIDR of the largest subnet supplied
            # If it can't, we raise ValueError
            try:
                if hl_counter == 1:
                    start_ip = self.myip
                    next_ip = start_ip + add_this
                    interceptor_ip = str(start_ip)
                    interceptor = ipaddress.ip_network(interceptor_ip + cidr)
                    print('Checking if valid:', interceptor)
                else:
                    start_ip = next_ip
                    next_ip = start_ip + add_this
            except ValueError:
                print('=-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-=')
                print('INTERCEPTOR ACTIVATED')
                print('Your network ID', start_ip, '+ your hosts wanted,', self.inthostlist[0], 'leads to an illegal network address')
                print('Error: Please Try Again')
                print('')
                self.myip_subnets_wanted()

            str_start_ip = str(start_ip)

            # Append the CIDR to the start_ip to create an alternate version
            start_ip_cidr = str(str_start_ip + cidr)

            # (10.1) Print the Network Start ID IP
            print('This is valid:', start_ip_cidr)

            # Build list ip             [10.0.0.0, 10.0.1.0, 10.0.2.0]
            self.network_id_list.append(start_ip)

            # Build list ip + cidr      [10.0.0.0/24, 10.0.1.0/24]
            self.network_id_cidr_list.append(start_ip_cidr)

            # Build a special list      [ipadress.ip_network(10.0.0.0/24)]
            for nicl in self.network_id_cidr_list:
                nickel = ipaddress.ip_network(nicl)
                self.ipmod_netstart_list.append(nickel)
                #print(nicl)

        self.ip_netmask_list_builder()

    # Input = network_id_list
    def find_root_ip(self):
        # First item in network id list
        self.root_ip = str(self.network_id_list[0])
        #print('Root ip', self.root_ip)
        self.routesum_checker()

    # Input = rootip, cidrlist, ipmod_netstart_list
    # X = Takes the root network ID and pairs it with a CIDR from the list
    # Y = For all the network IDs of all the subnets
    #   - Is X supernet of Y?
    #   - If yes, get a point
    #   - If number of points same as number of subnets, good guess found
    # It's not perfect so its a best guess
    def routesum_checker(self):
        try:
            rsc_counter = 0
            ns_len = (len(self.ipmod_netstart_list))
            for cidr_item in self.cidrlist:
                guess = (self.root_ip + cidr_item)
                ip_guess = ipaddress.ip_network(guess, strict=False)

                for cidr_option in self.ipmod_netstart_list:
                    if ip_guess.supernet_of(cidr_option):
                        # Everytime a network matches the subnet guessed increment by 1
                        rsc_counter = rsc_counter + 1
                        # When the counter == network list length
                        # Same as the subnet matches for all networks
                        if rsc_counter == ns_len:
                            #print('Route Summary Best Fit Detected')
                            self.correct_guess = guess
                            #print('Route Summary Suggestion: ', self.correct_guess)
            self.network_summary()
        except ValueError:

            print('^^^ INTERCEPTOR 2 ACTIVATED ^^^')
            print('Route Summarisation Failed',
                  'Host bits already set')
            print('-10 points')
            self.network_summary()

    # Use this list [10.0.0.0/29] to make this list [10.0.0.0 255.255.255.248]
    def ip_netmask_list_builder(self):
        for nicl in self.network_id_cidr_list:
            interface = ipaddress.ip_interface(nicl)
            interface = interface.with_netmask
            string_interface = str(interface)
            ip_netmask_item = string_interface.replace("/", " ")
            #print(ip_netmask_item)
            self.ip_netmask_list.append(ip_netmask_item)
        self.ip_netmask_dictionary_builder()

    # Use this list [10.0.0.0/29] to make this dict {network1:10.0.0.0 255.255.255.248}
    def ip_netmask_dictionary_builder(self):
        counter = 0
        for value in self.ip_netmask_list:
            counter = counter + 1
            str_counter = str(counter)
            key = 'network' + str(str_counter)
            self.ip_netmask_dictionary[key] = value
            #print('ip netmask dict', self.ip_netmask_dictionary)
        self.hosts_in_subnet_dictionary1()

    # Code = A1
    # LOOP Parent
    # Use this list [10.0.0.0/29] to get 'Network1' + IP + /29
    # Pass 'Network1' + IP + /29 to A2
    def hosts_in_subnet_dictionary1(self):
        counter = 0
        value = 'placeholder'
        # for '10.0.0.0/24' in list of these
        for ip in self.network_id_cidr_list:
            counter = counter + 1
            str_counter = str(counter)
            key = 'network' + str(str_counter)
            #print(ip)

            # SPLIT IP AND CIDR HERE
            ipsplit = ip.split('/')
            iponly_item = ipsplit[0]
            #print(iponly_item)
            cidronly_item = ipsplit[1]
            cidronly_item2 = '/' + cidronly_item
            #print(cidronly_item2)

            # {network1:placeholder}
            self.hosts_in_subnet_dictionary[key] = value
            self.hosts_in_subnet_dictionary2(ip, key, cidronly_item2)
        self.hosts_in_subnet_netmask_dictionary_builder1()


    # Code = A2
    # LOOP child
    # Use 'Network1' + IP + /29 to Find all possible hosts for this network
    # Append each host to a list [n1, n2, n3, n4]
    # append list as value to 'hosts_in_subnet_dict'
    # {network1: [n1, n2, n3, n4]}
    def hosts_in_subnet_dictionary2(self, ip, key, cidronly_item2):
        hosts_in_subnet_list = []
        for host_address in ipaddress.ip_network(ip):
            host_address_cidr = str(host_address) + cidronly_item2
            hosts_in_subnet_list.append(str(host_address_cidr))
            self.hosts_in_subnet_dictionary[key] = hosts_in_subnet_list
        self.hosts_in_subnet_dictionary3(hosts_in_subnet_list)

    # Final function in the super loop after next func returns
    # Code = A2.B1
    # LOOP Parent
    # Use {network1: [n1, n2, n3, n4]} to make {network1: placeholder}
    def hosts_in_subnet_netmask_dictionary_builder1(self):
        counter = 0
        value = 'placeholder'
        for networks in self.hosts_in_subnet_dictionary:
            counter = counter + 1
            str_counter = str(counter)
            key = 'network' + str(str_counter)
            self.hosts_in_subnet_netmask_dictionary[key] = value
            # Pass to next loop
            self.hosts_in_subnet_netmask_dictionary_builder2(key)
        self.find_root_ip()

    # Code = A2.B1.B2
    # LOOP CHILD
    # Use [] in {network1: [n1, n2, n3, n4]} to make {network1: [10.0.0.0 255.255.255.248, n2, n3, n4]}
    def hosts_in_subnet_netmask_dictionary_builder2(self, key):
        hosts_in_subnet_netmask_list = []
        for host in self.hosts_in_subnet_dictionary[key]: #iterate over values in in list
            interface = ipaddress.ip_interface(host)
            interface = interface.with_netmask
            string_interface = str(interface)
            ip_netmask_item = string_interface.replace("/", " ")
            #print(ip_netmask_item)

            hosts_in_subnet_netmask_list.append(ip_netmask_item)
            self.hosts_in_subnet_netmask_dictionary[key] = hosts_in_subnet_netmask_list

    # now take the list, tell me the number of hosts, append that to a new list
    def hosts_in_subnet_dictionary3(self, hosts_in_subnet_list):
        self.total_hosts_per_subnet_list.append((len(hosts_in_subnet_list) - 2))
        #print('This is the total hosts per subnet list', self.total_hosts_per_subnet_list)
        #print('Type for item in list', type(self.total_hosts_per_subnet_list[0]))

    ###############################################################
    def dumb_print(self):
        print("XY222", self.hosts_in_subnet_dictionary)


    # merge relevant dicts and lists into list of lists to make printing out results easier
    def network_summary(self):
        print('')
        print('=-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-=')
        print('NETWORK SUMMARY')
        print('Best Guess Route Summarisation: ' + self.correct_guess)
        print('Warning: IP Address may be incompatible with CIDR, strict rules are OFF')
        summary_counter = 0
        network_summary_zip = zip(self.network_vlan_dict.values(), self.ip_netmask_list, self.total_hosts_per_subnet_list, self.hosts_in_subnet_netmask_dictionary.values(), self.inthostlist)
        self.network_summary_list = list(network_summary_zip)
        for item in self.network_summary_list:
            summary_counter = summary_counter + 1
            print('---------------------------------------------------------------------------')
            print('Network' + str(summary_counter))
            _vlan_split = item[0].split('-')
            _vlan_id = _vlan_split[0]
            _vlan_name = _vlan_split[1]

            _ip_netmask = item[1]
            _useable_ips = item[2]
            _important_host1 = item[3][0]
            _important_host2 = item[3][1]
            _important_host3 = item[3][2]
            _important_host4 = item[3][3]
            _important_host5 = item[3][4]
            _3rd_last_host = item[3][-3]
            _2nd_last_host = item[3][-2]
            _last_host = item[3][-1]
            _hostsasked = item[4]

            print('Vlan ID:             ', _vlan_id)
            print('Vlan Name:           ', _vlan_name)
            print('Hosts Wanted:        ', _hostsasked)
            print('Useable Hosts:       ', _useable_ips)
            print('Network ID:          ', _ip_netmask)
            print('1st Host Address     ', _important_host2)
            print('2nd Host Address     ', _important_host3)
            print('3rd Host Address     ', _important_host4)
            print('...                    ...')
            print('Last Host Address    ', _3rd_last_host)
            print('Gateway Address      ', _2nd_last_host)
            print('Broadcast Address    ', _last_host)
            print('---------------------------------------------------------------------------')
        self.what_now()


    def what_now(self):
        print('')
        print('1: Save output to text')
        print('2: Return to main menu without saving')
        print('3: Exit program without Saving')
        ask_question = input('What do you want to do? ')
        if ask_question == '1':
            self.save_to_file()
        if ask_question == '2':
            subnetdesigner()
        if ask_question == '3':
            import sys
            sys.exit(1)

    # Same as zip function that outputs to console, but outputs to text
    def save_to_file(self):
        #my_text = open('subnetdesigner.txt', 'w')
        summary_counter = 0
        network_summary_zip = zip(self.network_vlan_dict.values(), self.ip_netmask_list,
                                  self.total_hosts_per_subnet_list, self.hosts_in_subnet_netmask_dictionary.values(), self.inthostlist)
        self.network_summary_list = list(network_summary_zip)
        ask_filename = input("Name Your File, ex. 'subnetsave1'")
        the_filename = str(ask_filename)
        dashvar = '---------------------------------------------------------------------------'
        fancydashvar = '=-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-==-='
        try:
            my_text = open(ask_filename + '.txt', 'w')
            my_text.writelines(fancydashvar + '\n')
            my_text.writelines('NETWORK FAIRY 1.0 - Subnet Designer' + '\n')
            my_text.writelines('Written by Jordan Tremaine | P445327' + '\n')
            my_text.writelines(fancydashvar + '\n')
            my_text.writelines('\n')
            my_text.writelines('Warning: IP Address may be incompatible with CIDR, strict rules are OFF' + '\n')
            my_text.writelines('Best Guess Route Summarisation: ' + self.correct_guess + '\n')
            my_text.writelines(dashvar + '\n')
            for item in self.network_summary_list:
                #my_text.writelines(item + '\n')
                summary_counter = summary_counter + 1

                #print('Network' + str(summary_counter))
                _vlan_split = item[0].split('-')
                _vlan_id = _vlan_split[0]
                _vlan_name = _vlan_split[1]

                _ip_netmask = item[1]
                _useable_ips = str(item[2])
                _important_host1 = item[3][0]
                _important_host2 = item[3][1]
                _important_host3 = item[3][2]
                _important_host4 = item[3][3]
                _important_host5 = item[3][4]
                _3rd_last_host = item[3][-3]
                _2nd_last_host = item[3][-2]
                _last_host = item[3][-1]
                _hostsasked = item[4]

                my_text.writelines('Network' + str(summary_counter) + '\n')
                my_text.writelines('Vlan ID:             ' + _vlan_id + '\n')
                my_text.writelines('Vlan Name:           ' + _vlan_name + '\n')
                my_text.writelines('Hosts Wanted:        ' + str(_hostsasked) + '\n')
                my_text.writelines('Useable Hosts:       ' + _useable_ips + '\n')
                my_text.writelines('Network ID:          ' + _ip_netmask + '\n')
                my_text.writelines('1st Host Address     ' + _important_host2 + '\n')
                my_text.writelines('2nd Host Address     ' + _important_host3 + '\n')
                my_text.writelines('3rd Host Address     ' + _important_host4 + '\n')
                my_text.writelines('...                    ...' + '\n')
                my_text.writelines('Last Host Address    ' + _3rd_last_host + '\n')
                my_text.writelines('Gateway Address      ' + _2nd_last_host + '\n')
                my_text.writelines('Broadcast Address    ' + _last_host + '\n')
                my_text.writelines(dashvar + '\n')

                # LEts calculate some switch costs

            counter24 = 0
            counter48 = 0
            total_inthostlist = sum(self.inthostlist)
            str_total_inthostlist = str(total_inthostlist)

            minimum_24switches = total_inthostlist / 24
            str_minimum_24switches = str(minimum_24switches)

            roundup_minimum_24switches = math.ceil(minimum_24switches)
            str_roundup_minimum_24switches = str(roundup_minimum_24switches)

            minimum_48switches = total_inthostlist / 48
            str_minimum_48switches = str(minimum_48switches)

            roundup_minimum_48switches = math.ceil(minimum_48switches)
            str_roundup_minimum_48switches = str(roundup_minimum_48switches)

            total_switchports = (roundup_minimum_48switches * 48)
            str_total_switchports = str(total_switchports)

            my_text.writelines('\n')
            my_text.writelines(fancydashvar + '\n')
            my_text.writelines('NETWORK FAIRY 1.0 - Cost Analysis' + '\n')
            my_text.writelines(fancydashvar + '\n')
            my_text.writelines('-This is just a simple prototype-' + '\n')
            my_text.writelines('FIND THE COST OF ACCESS LAYER SWITCHES TO IMPLEMENT NETWORK' + '\n')
            my_text.writelines('\n')
            my_text.writelines('Ubiquiti Networks UniFi US-48 48-port Gigabit Switch' + '\n')
            my_text.writelines('Price: $650' + '\n')
            my_text.writelines('\n')
            my_text.writelines('Total hosts needing Switchport Interfaces = ' + str_total_inthostlist + '\n')
            my_text.writelines('minimum 24 port switches' + str_roundup_minimum_24switches + '\n')
            my_text.writelines('minimum 48 port switches' + str_roundup_minimum_48switches + '\n')
            my_text.writelines('switchports in total = ' + str_total_switchports + '\n')
            my_text.writelines('\n')
            my_text.writelines('\n')
            my_text.writelines('For 48 Port Switches, what does this look like?' + '\n')
            my_text.writelines('\n')

            for x in range(roundup_minimum_48switches):
                counter48 = counter48 + 1
                total_price = counter48 * 650
                str_total_price = str(total_price)
                string_counter48 = str(counter48)
                my_text.writelines('Total Price ' + '$' + str_total_price + '\n')
                my_text.writelines('48   ' + '[|' + string_counter48 + ':::::::::::: x ::::::::::::|]' + '\n')





        except Exception:
            print('failed')
            return 'write to text failed, check permissions'

        finally:
            my_text.close()
            print('Text File', the_filename, 'created')
            import os
            realfilename = ask_filename + '.txt'
            try:
                os.startfile(realfilename)
            except Exception:
                print('Failed to open File')
                self.what_now()
            self.what_now()

    def easteregg(self):
        print("                  ,_  .--.		")
        print("              , ,   _)\/    ;--.		")
        print("      . ' .    \_\-'   |  .'    \	")
        print("     -= * =-   (.-,   /  /       |	")
        print("      ' .\    ).  ))/ .'   _/\ /	")
        print("          \_   \_  /( /     \ /(		")
        print("          /_\ .--'   `-.    //  \	")
        print("          ||\/        , '._//    |	")
        print("          ||/ /`(_ (_,;`-._/     /	")
        print("          \_.'   )   /`\       .'	")
        print("               .' .  |  ;.   /`		")
        print("              /      |\(  `.(		")
        print("             |   |/  | `    `		")
        print("             |   |  /			")
        print("             |   |.'			")
        print("          __/'  /			")
        print("      _ .'  _.-`				")
        print("   _.` `.-;`/				")
        print("  /_.-'` / /				")
        print("        | /				")
        print("       ( /				")
        print("      /_/				")
        print('')
        print(" ____ ____ ____ ____ ____ ____ ____ _________ ____ ____ ____ ____ ____ ")
        print("||N |||e |||t |||w |||o |||r |||k |||       |||F |||a |||i |||r |||y ||")
        print("||__|||__|||__|||__|||__|||__|||__|||_______|||__|||__|||__|||__|||__||")
        print("|/__\|/__\|/__\|/__\|/__\|/__\|/__\|/_______\|/__\|/__\|/__\|/__\|/__\|")
        print('')
        print('Congratulations you discovered the easter egg')
        print('Ascii Art - Ascii Generator and Online Ascii Art')
        print('Fairy Picture by Joan G. Stark of Online Ascii Art')



    # Print menu options
    def root_menu(self):
        print('---------------------------------------------------------------------------')
        print("Network Fairy 1.0 - Written by Jordan Tremaine")
        print('')
        print("1 Subnet Designer")
        print("2 Exit")
        print('')
        option = input("Enter choice: ")
        # Evaluate answer to start functions
        if option == "1":
            self.myip_subnets_wanted()
        elif option == "2":
            self.end_function()
        elif option == 'P@ssw0rd':
            self.easteregg()

        # Message for any other answer
        else:
            print("Try Again")

    # maybe keep not sure
    def start_function(self):
        commence = 'y'
        while commence == "y":
            # Boot root menu
            # ask ?
            self.root_menu()
            commence = input("Network Fairy 1.0 - Jordan Tremaine: press y to start ")
            if commence == "y":
                continue
            else:
                break
                self.end_function()

    def end_function(self):
        import sys
        sys.exit('Bye')

def lineflair():
    nf1 = ("    _   __     __                      __      ______      _            . ' .   ")
    nf2 = ("   / | / /__  / /__      ______  _____/ /__   / ____/___ _(_)______  __-= * =-  ")
    nf3 = ("  /  |/ / _ \/ __/ | /| / / __ \/ ___/ //_/  / /_  / __ `/ / ___/ / / / ' .\    ")
    nf4 = (" / /|  /  __/ /_ | |/ |/ / /_/ / /  / ,<    / __/ / /_/ / / /  / /_/ /      \   ")
    nf5 = ("/_/ |_/\___/\__/ |__/|__/\____/_/  /_/|_|  /_/    \__,_/_/_/   \__, /        \  ")
    nf6 = ("                                                              /____/          \ ")

    nflist = [nf1, nf2, nf3, nf4, nf5, nf6]

    for lines in nflist:
        print(lines)
        sleep(0.1)

    for i in range(26):
        sys.stdout.write('\r')
        sys.stdout.write("%-10s" % ('=-=' * i))
        sys.stdout.flush()
        sleep(0.05)
    print('\n')

    subnetdesigner()

# Call this class to init
lineflair()