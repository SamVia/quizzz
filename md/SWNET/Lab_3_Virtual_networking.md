## Master Cheat Sheet: Fundamentals of Virtual Networking

### Background: Linux Namespaces

* **Definition**: Linux namespaces partition kernel resources, providing isolated views for different sets of processes.


* **Virtualization Context**: Namespaces are a building block for lightweight virtualization (like Docker), offering weaker isolation than Virtual Machines because the kernel is shared, but with significantly reduced overhead.


* **Types**: The Linux kernel provides eight types of namespaces, dealing with resources like networking, mount points, process IDs, and IPC.


* **Network (NET) Namespaces**: NET namespaces give processes completely independent network setups.


* **NET Resources**: Each NET namespace contains its own set of IP addresses, routing table, firewall rules, and loopback interface.


* **Initial State**: A newly created NET namespace only contains a loopback interface.


* **Interfaces**: Physical or virtual network interfaces can be attached to namespaces, but each network interface is present in exactly one namespace at a time.



### Background: Software Switches

* **Functionality**: Software switches implement switching functions (Layer 2 or OpenFlow) inside a Linux environment, connecting entities like network namespaces or VMs through a virtual data-link layer network.


* **Features**: They support basic data forwarding, backward learning algorithms, VLANs support, and the Spanning Tree Protocol (STP).


* **Alternatives**: Two well-known alternatives are the Linux Bridge (simple, reliable, standard part of Linux) and Open vSwitch (advanced features, tunneling, OpenFlow).


* **Open vSwitch (OvS)**: OvS is an open-source, multilayer software switch designed to function as a virtual switch in virtual machine environments, supporting standard management interfaces and programmable forwarding functions.


* **OvS Compatibility**: It distributes traffic across multiple servers and works with Xen/XenServer, KVM, VirtualBox, etc..


* **OvS Modes**: OvS can act as a traditional 802.1d bridge, an OpenFlow switch, or in mixed-mode.


* **OvS Spanning Tree Protocol**: STP is disabled by default in OvS and must be explicitly turned on with the appropriate command to prevent loop-induced broadcast storms.


* **OvS Configuration Storage**: Configurations are stored in a local database and read by an internal daemon; hence, configurations are preserved even if we reboot the machine.


* **OvS Tools**: `ovs-vsctl` manages bridging logic (creating bridges, adding ports, setting tags), while `ovs-ofctl` manages OpenFlow rules.



### Background: GRE Tunnels

* **Definition**: Generic Routing Encapsulation (GRE) is a basic tunneling protocol which can encapsulate a variety of network layer protocols inside point-to-point links over an IP network.


* **Simplicity**: GRE requires no connection establishment prior to starting sending data.


* **Security**: GRE does not include any support for the encryption of the payload, so it is often paired with L3 encryption like IPsec.


* **gretun vs gretap**:
* `gretun`: Encapsulates a payload with just its IP header (L3). The frame layout is `Outer Eth | Outer IP | GRE | IP | Payload`.


* `gretap`: Encapsulates the entire L2 frame. The frame layout is `Outer Eth | Outer IP | GRE | Eth | IP | Payload`.




* **Tunnel Dependencies**: Interfaces like `gre0`, `gretap0`, and `erspan0` are automatically generated special interfaces required for the correct functioning of the kernel module; they are present in all network namespaces and cannot be removed.



---

### Master Command Reference

#### Linux Namespace Commands

```bash
# List available network namespaces
ip netns list
ip netns

# Create a network namespace
sudo ip netns add ns1

# Execute a command inside a specific namespace
sudo ip netns exec <namespace_name> <command>

# Bring up the loopback interface in a namespace
sudo ip netns exec ns1 ip link set dev lo up

# Delete a namespace
sudo ip netns del ns1

```

#### Virtual Ethernet (veth) Commands

```bash
# Create a veth pair (two virtual interfaces acting like a wire)
sudo ip link add veth0-root type veth peer name veth0-ns1

# Create a veth pair and place one end directly into a namespace
sudo ip link add veth0-root type veth peer name veth0-ns1 netns ns1

# Attach a veth end to a specific namespace
sudo ip link set veth0-ns1 netns ns1

# Bring a veth interface up
sudo ip link set dev veth0-root up

# Delete a veth pair
sudo ip link del veth0-root

```

#### IP Addressing & Routing Commands

```bash
# Assign an IP address to a virtual interface in a namespace
sudo ip netns exec ns1 ip addr add 10.255.0.1/24 dev veth0-ns1

# Flush/remove an IP address from an interface
sudo ip netns exec ns2 ip addr flush dev veth1-ns2

# Add a specific route
sudo ip route add {NETWORK/MASK} via {GATEWAY_IP}
sudo ip netns exec ns1 ip route add 10.255.1.0/24 via 10.255.0.254

# Add a default gateway
sudo ip netns exec h1-ns ip route add default via 10.255.0.254

# Enable IP forwarding (routing) on a host/namespace
sudo sysctl net.ipv4.ip_forward=1
sudo ip netns exec ns-br sysctl net.ipv4.ip_forward=1

# Change iptables FORWARD default policy to ACCEPT
sudo iptables -P FORWARD ACCEPT

# Configure NAT Masquerade for namespace Internet access
sudo iptables -t nat -A POSTROUTING --source 10.255.0.0/24 -j MASQUERADE

```

#### Linux Bridge Commands

```bash
# Create a Linux Bridge
sudo ip link add br0 type bridge

# Bring the bridge up
sudo ip link set dev br0 up

# Attach an interface to the Linux Bridge
sudo ip link set dev veth0-root master br0

# Delete a Linux Bridge
sudo ip link del br0

```

#### Open vSwitch (OvS) Commands

```bash
# Create an OvS bridge
sudo ovs-vsctl add-br ovs-br0

# Attach a port to an OvS bridge
sudo ovs-vsctl add-port ovs-br0 veth0-root

# Set a VLAN tag on an OvS port (access mode)
sudo ovs-vsctl set port veth0-root tag=100
sudo ovs-vsctl set Port veth0-root tag=1

# Remove a VLAN tag
sudo ovs-vsctl remove port veth0-root tag 100
sudo ovs-vsctl remove port veth0-root tag 1

# View the OvS configuration
sudo ovs-vsctl show

# Clear the OvS database configuration
sudo ovs-vsctl emer-reset

# Delete an OvS bridge (and clear associated IP configs)
sudo ovs-vsctl del-br ovs-br0

```

#### OpenFlow Commands

```bash
# Display currently installed OpenFlow rules
sudo ovs-ofctl dump-flows ovs-br0

# Delete the default NORMAL flow (L2 bridging) by matching its priority (0)
sudo ovs-ofctl del-flows ovs-br0 priority=0 --strict

# Add a direct port-to-port forwarding rule
sudo ovs-ofctl add-flow ovs-br0 in_port="veth0-root", actions="veth2-root"

```

#### GRE Tunnel Commands

```bash
# Create an L2 GRE Tunnel (gretap)
sudo ip link add tun0 type gretap local IP_HOST_1 remote IP_HOST_2 dev NIC_HOST_1

# Create an L3 GRE Tunnel (gretun)
sudo ip link add tun0 type gre local IP_HOST_1 remote IP_HOST_2 dev NIC_HOST_1

# View extended info for a tunnel interface
ip -d link show dev tun0

```

#### Utility & Debugging Commands

```bash
# Ping a specific IP from a namespace
sudo ip netns exec ns1 ping 10.255.0.2

# Custom DNS resolution for namespaces overriding systemd-resolved
sudo mkdir -p /etc/netns/h1-ns
echo 'nameserver 10.96.0.10' | sudo tee /etc/netns/h1-ns/resolv.conf

```

---

### Practical Exercises

#### Exercise 1: Connecting Two Namespaces via OvS

1. **Initialize Namespaces**: Create namespaces `ns1` and `ns2`, and bring up their loopback interfaces.


2. **Create Links**: Create `veth0-root`/`veth0-ns1` mapped to `ns1`, and `veth1-root`/`veth1-ns2` mapped to `ns2`.


3. **Configure IPs**: Assign `10.255.0.1/24` to `ns1` and `10.255.0.2/24` to `ns2`.


4. **Deploy Switch**: Create an OvS switch (`ovs-br0`), attach `veth0-root` and `veth1-root`, and bring interfaces UP.


5. **Verify**: Run `sudo ip netns exec ns1 ping 10.255.0.2`.



#### Exercise 2: Connecting Namespaces Through a Third Namespace (Routing)

1. **Prepare Topology**: Ensure `ns1` (`10.255.0.1/24`) and `ns2` (`10.255.1.1/24`) are created and on distinct networks.


2. **Create Router Namespace**: Create `ns-br`. Map `veth0-root` and `veth1-root` to `ns-br`.


3. **Configure Router IPs**: Assign `10.255.0.254/24` to `veth0-root` and `10.255.1.254/24` to `veth1-root` inside `ns-br`.


4. **Enable Routing**: Run `sudo ip netns exec ns-br sysctl net.ipv4.ip_forward=1`.


5. **Configure Edges**: Add specific routes: `sudo ip netns exec ns1 ip route add 10.255.1.0/24 via 10.255.0.254` and `sudo ip netns exec ns2 ip route add 10.255.0.0/24 via 10.255.1.254`.



#### Exercise 3: Creating a L3 GRE Tunnel Across Hosts

1. **Prepare Hosts**: On both Server H1 and H2, enable IP forwarding and configure iptables FORWARD default policy to ACCEPT.


2. **Create Namespaces**: Create `h1-ns` (`10.255.0.1/24`) on H1 and `h2-ns` (`10.255.1.1/24`) on H2.


3. **Create L3 Tunnel**: Run `sudo ip link add tun0 type gre local IP_HOST_1 remote IP_HOST_2 dev NIC_HOST_1` on H1, and the reverse on H2.


4. **IP Tunnel Interfaces**: Assign `10.255.255.1/30` to `tun0` on H1, and `10.255.255.2/30` to `tun0` on H2.


5. **Route over Tunnel**: On H1, run `sudo ip route add 10.255.1.0/24 via 10.255.255.2`. On H2, run `sudo ip route add 10.255.0.0/24 via 10.255.255.1`.



---

### Full Configuration Scripts

#### 1. Connecting Two Namespaces via a Switch in the Root Namespace

```bash
#!/bin/bash
function cleanup {
set +e
# Delete all the veth pairs created by the script
sudo ip link del veth0-root
sudo ip link del veth1-root
# Delete all the namespaces created by the script
sudo ip netns del ns1
sudo ip netns del ns2
# Delete all the virtual switches created by the script
sudo ip link del br0
sudo ovs-vsctl del-br ovs-br0
}
trap cleanup EXIT
set -x
set -e
# Create all the required namespaces and veth
sudo ip netns add ns1
sudo ip netns add ns2
sudo ip netns exec ns1 ip link set dev lo up
sudo ip netns exec ns2 ip link set dev lo up
sudo ip link add veth0-root type veth peer name veth0-ns1 netns ns1
sudo ip link add veth1-root type veth peer name veth1-ns2 netns ns2
sudo ip link set dev veth0-root up
sudo ip link set dev veth1-root up
sudo ip netns exec ns1 ip link set veth0-ns1 up
sudo ip netns exec ns2 ip link set veth1-ns2 up
sudo ip netns exec ns1 ip addr add 10.255.0.1/24 dev veth0-ns1
sudo ip netns exec ns2 ip addr add 10.255.0.2/24 dev veth1-ns2
# Perform the Linux Bridge configuration
sudo ip link add br0 type bridge
sudo ip link set dev br0 up
sudo ip link set dev veth0-root master br0
sudo ip link set dev veth1-root master br0
read -p "Press ENTER to delete the Linux Bridge and replace it with an OVS one..."
# Perform the OVS configuration
sudo ip link del br0
sudo ovs-vsctl add-br ovs-br0
sudo ovs-vsctl add-port ovs-br0 veth0-root
sudo ovs-vsctl add-port ovs-br0 veth1-root
read -p "Press ENTER to delete the current configuration..."
# When exiting from the script, cleanup() will be executed,
# automatically cleaning up the environment

```

#### 2. Connecting Two Namespaces Through a Third Namespace

```bash
#!/bin/bash
function cleanup {
set +e
# Delete all the veth pairs created by the script
sudo ip link del veth0-root
sudo ip link del veth1-root
sudo ip link del veth2-root
sudo ip link del veth3-root
# Delete all the namespaces created by the script
sudo ip netns del ns1
sudo ip netns del ns2
sudo ip netns del ns-br
# Delete the virtual switch created by the script
sudo ovs-vsctl del-br ovs-br0
}
trap cleanup EXIT
set -x
set -e
# Create all the required namespaces and veth
sudo ip netns add ns1
sudo ip netns add ns2
sudo ip netns exec ns1 ip link set dev lo up
sudo ip netns exec ns2 ip link set dev lo up
sudo ip link add veth0-root type veth peer name veth0-ns1 netns ns1
sudo ip link add veth1-root type veth peer name veth1-ns2 netns ns2
sudo ip link set dev veth0-root up
sudo ip link set dev veth1-root up
sudo ip netns exec ns1 ip link set veth0-ns1 up
sudo ip netns exec ns2 ip link set veth1-ns2 up
sudo ip netns exec ns1 ip addr add 10.255.0.1/24 dev veth0-ns1
sudo ip netns exec ns2 ip addr add 10.255.0.2/24 dev veth1-ns2
# Perform the OVS configuration
sudo ovs-vsctl add-br ovs-br0
sudo ovs-vsctl add-port ovs-br0 veth0-root
sudo ovs-vsctl add-port ovs-br0 veth1-root
sudo ovs-vsctl set Port veth0-root tag=1
sudo ovs-vsctl set Port veth1-root tag=2
# Create the third namespace and the Linux Bridge
sudo ip netns add ns-br
sudo ip netns exec ns-br ip link add br0 type bridge
sudo ip netns exec ns-br ip link set dev br0 up
# Create and configure the veth pairs connected to the third namespace
sudo ip link add veth2-root type veth peer name veth2-ns-br netns ns-br
sudo ip link add veth3-root type veth peer name veth3-ns-br netns ns-br
sudo ip link set dev veth2-root up
sudo ovs-vsctl add-port ovs-br0 veth2-root
sudo ovs-vsctl set Port veth2-root tag=1
sudo ip link set dev veth3-root up
sudo ovs-vsctl add-port ovs-br0 veth3-root
sudo ovs-vsctl set Port veth3-root tag=2
sudo ip netns exec ns-br ip link set veth2-ns-br up
sudo ip netns exec ns-br ip link set veth3-ns-br up
sudo ip netns exec ns-br ip link set dev veth2-ns-br master br0
sudo ip netns exec ns-br ip link set dev veth3-ns-br master br0
read -p "Press ENTER to replace the VLAN configuration with OpenFlow rules..."
# Remove the 'NORMAL' flow
sudo ovs-ofctl del-flows ovs-br0 priority=0 --strict
# Delete the VLAN configurations
sudo ovs-vsctl remove port veth0-root tag 1
sudo ovs-vsctl remove port veth1-root tag 2
sudo ovs-vsctl remove port veth2-root tag 1
sudo ovs-vsctl remove port veth3-root tag 2
# Configure the OpenFlow rules
sudo ovs-ofctl add-flow ovs-br0 in_port="veth0-root", actions="veth2-root"
sudo ovs-ofctl add-flow ovs-br0 in_port="veth2-root", actions="veth0-root"
sudo ovs-ofctl add-flow ovs-br0 in_port="veth1-root", actions="veth3-root"
sudo ovs-ofctl add-flow ovs-br0 in_port="veth3-root", actions="veth1-root"
read -p "Press ENTER to replace the OVS bridge with direct connections..."
# Delete the OVS bridge from the root namespace
sudo ovs-vsctl del-br ovs-br0
sudo ip link del veth2-root
sudo ip link del veth3-root
# Configure the direct interconnection between the namespaces
sudo ip link set veth0-root netns ns-br
sudo ip link set veth1-root netns ns-br
sudo ip netns exec ns-br ip link set veth0-root up
sudo ip netns exec ns-br ip link set veth1-root up
sudo ip netns exec ns-br ip link set dev veth0-root master br0
sudo ip netns exec ns-br ip link set dev veth1-root master br0
read -p "Press ENTER to replace the Linux Bridge with a routing process..."
# Remove the virtual switch
sudo ip netns exec ns-br ip link del br0
# Edit the IP configuration of ns2
sudo ip netns exec ns2 ip addr flush dev veth1-ns2
sudo ip netns exec ns2 ip addr add 10.255.1.1/24 dev veth1-ns2
# Configure the IP addresses of the router
sudo ip netns exec ns-br ip addr add 10.255.0.254/24 dev veth0-root
sudo ip netns exec ns-br ip addr add 10.255.1.254/24 dev veth1-root
# Add the appropriate routes
sudo ip netns exec ns1 ip route add 10.255.1.0/24 via 10.255.0.254
sudo ip netns exec ns2 ip route add 10.255.0.0/24 via 10.255.1.254
# Ensure forwarding is enabled
sudo ip netns exec ns-br sysctl net.ipv4.ip_forward=1
read -p "Press ENTER to delete the current configuration..."
# When exiting from the script, cleanup() will be executed,
# automatically cleaning up the environment

```

#### 3. Configuration for Host H1 (GRE Tunnel Scenario)

```bash
#!/bin/bash
# Note: adapt the content of the following variables depending on your configuration
IP_HOST_1=172.16.0.1 # The IP address of the current host
IP_HOST_2=172.16.0.2 # The IP address of the peer host
NIC_HOST_1=enp1s0    # The name of the NIC of the current host

function cleanup {
set +e
# Delete all components created by the script
sudo ip netns del h1-ns
sudo ip link del h1-veth-root
sudo ip link del tun0
sudo ip link del h1-br
# Delete the NAT rule
sudo iptables -t nat -D POSTROUTING --source 10.255.0.0/24 -j MASQUERADE
}
trap cleanup EXIT
set -x
set -e
# Enable the forwarding behavior
sudo sysctl net.ipv4.ip_forward=1
sudo iptables -P FORWARD ACCEPT
# Create the network namespace and the veth pair
sudo ip netns add h1-ns
sudo ip link add h1-veth-root type veth peer name h1-veth-ns netns h1-ns
# Set the interfaces 'up' and configure the IP address
sudo ip link set dev h1-veth-root up
sudo ip netns exec h1-ns ip link set dev lo up
sudo ip netns exec h1-ns ip link set dev h1-veth-ns up
sudo ip netns exec h1-ns ip address add 10.255.0.1/24 dev h1-veth-ns
# Create the Linux Bridge and configure the interface
sudo ip link add h1-br type bridge
sudo ip link set dev h1-br up
sudo ip link set dev h1-veth-root master h1-br
# Create and configure the L2 GRE tunnel interface
sudo ip link add tun0 type gretap local ${IP_HOST_1} remote ${IP_HOST_2} dev${NIC_HOST_1}
sudo ip link set dev tun0 up
sudo ip link set dev tun0 master h1-br
# Configure the default gateway and the NAT rule
sudo ip address add 10.255.0.254/24 dev h1-br
sudo ip netns exec h1-ns ip route add default via 10.255.0.254
sudo iptables -t nat -A POSTROUTING --source 10.255.0.0/24 -j MASQUERADE
read -p "Press ENTER to replace the L2 GRE tunnel with an L3 GRE TUNNEL..."
# Delete the L2 GRE tunnel interface
sudo ip link del dev tun0
# Create and configure the L3 GRE tunnel interface
sudo ip link add tun0 type gre local ${IP_HOST_1} remote ${IP_HOST_2} dev${NIC_HOST_1}
sudo ip link set dev tun0 up
sudo ip address add 10.255.255.1/30 dev tun0
sudo ip route add 10.255.1.0/24 via 10.255.255.2
read -p "Press ENTER to delete the current configuration..."
# When exiting from the script, cleanup() will be executed,
# automatically cleaning up the environment

```

#### 4. Configuration for Host H2 (GRE Tunnel Scenario)

```bash
#!/bin/bash
# Note: adapt the content of the following variables depending on your configuration
IP_HOST_1=172.16.0.1 # The IP address of the peer host
IP_HOST_2=172.16.0.2 # The IP address of the current host
NIC_HOST_2=enp1s0    # The name of the NIC of the current host

function cleanup {
set +e
# Delete all components created by the script
sudo ip netns del h2-ns
sudo ip link del h2-veth-root
sudo ip link del tun0
sudo ip link del h2-br
# Delete the NAT rule
sudo iptables -t nat -D POSTROUTING --source 10.255.1.0/24 -j MASQUERADE
}
trap cleanup EXIT
set -x
set -e
# Enable the forwarding behavior
sudo sysctl net.ipv4.ip_forward=1
sudo iptables -P FORWARD ACCEPT
# Create the network namespace and the veth pair
sudo ip netns add h2-ns
sudo ip link add h2-veth-root type veth peer name h2-veth-ns netns h2-ns
# Set the interfaces 'up' and configure the IP address
sudo ip link set dev h2-veth-root up
sudo ip netns exec h2-ns ip link set dev lo up
sudo ip netns exec h2-ns ip link set dev h2-veth-ns up
sudo ip netns exec h2-ns ip address add 10.255.0.2/24 dev h2-veth-ns
# Create the Linux Bridge and configure the interface
sudo ip link add h2-br type bridge
sudo ip link set dev h2-br up
sudo ip link set dev h2-veth-root master h2-br
# Create and configure the L2 GRE tunnel interface
sudo ip link add tun0 type gretap local ${IP_HOST_2} remote ${IP_HOST_1} dev${NIC_HOST_2}
sudo ip link set dev tun0 up
sudo ip link set dev tun0 master h2-br
# Configure the default gateway
sudo ip netns exec h2-ns ip route add default via 10.255.0.254
read -p "Press ENTER to replace the L2 GRE tunnel with an L3 GRE TUNNEL..."
# Delete the L2 GRE tunnel interface
sudo ip link del dev tun0
# Update the IP address of the network namespace
sudo ip netns exec h2-ns ip address flush dev h2-veth-ns
sudo ip netns exec h2-ns ip address add 10.255.1.1/24 dev h2-veth-ns
# Configure the default gateway and the NAT rule
sudo ip address add 10.255.1.254/24 dev h2-br
sudo ip netns exec h2-ns ip route add default via 10.255.1.254
sudo iptables -t nat -A POSTROUTING --source 10.255.1.0/24 -j MASQUERADE
# Create and configure the L3 GRE tunnel interface
sudo ip link add tun0 type gre local ${IP_HOST_2} remote ${IP_HOST_1} dev${NIC_HOST_2}
sudo ip link set dev tun0 up
sudo ip address add 10.255.255.2/30 dev tun0
sudo ip route add 10.255.0.0/24 via 10.255.255.1
read -p "Press ENTER to delete the current configuration..."
# When exiting from the script, cleanup() will be executed,
# automatically cleaning up the environment

```

---

### Interactive HTML Quiz

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fundamentals of Virtual Networking Quiz</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: auto; padding: 20px; background-color: #f4f4f9; }
        h1 { text-align: center; color: #333; }
        .question-card { background: #fff; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .question { font-weight: bold; margin-bottom: 10px; font-size: 1.1em; }
        .options { list-style: none; padding: 0; }
        .options li { margin-bottom: 10px; }
        label { cursor: pointer; display: flex; align-items: baseline; gap: 10px; }
        .btn { display: block; width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; font-size: 1em; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        .feedback { display: none; margin-top: 15px; padding: 15px; border-radius: 4px; border-left: 5px solid; }
        .correct { border-color: #28a745; background: #e8f5e9; }
        .incorrect { border-color: #dc3545; background: #ffebee; }
    </style>
</head>
<body>

    <h1>Virtual Networking Interactive Quiz</h1>
    <div id="quiz-container"></div>
    <button class="btn" onclick="submitQuiz()">Submit Quiz</button>

    <script>
        const quizData = [
            {
                q: "What is the primary difference in isolation between Linux Namespaces and Virtual Machines?",
                options: [
                    "Namespaces provide hardware virtualization, while VMs do not.",
                    "Namespaces share the underlying kernel resulting in weaker isolation but lower overhead.",
                    "Virtual Machines share the underlying kernel resulting in weaker isolation.",
                    "There is no difference in isolation between them."
                ],
                ans: 1,
                explanation: "Linux namespaces are a building block of lightweight virtualization. The partitions created through Linux namespaces are weaker than the isolation obtained with virtual machines, as the underlying kernel is shared. Yet, also the overhead is reduced, since no virtualization is involved[cite: 6]."
            },
            {
                q: "When a new Network (NET) namespace is created, which network interface is present by default?",
                options: ["eth0", "veth0", "lo (loopback)", "None"],
                ans: 2,
                explanation: "Whenever a new network namespace is created, it contains only a loopback interface[cite: 6]."
            },
            {
                q: "Can a single network interface exist in multiple network namespaces simultaneously?",
                options: ["Yes, if it is a physical interface.", "Yes, if it is a virtual interface.", "No, each interface is present in exactly one namespace.", "Yes, up to 8 namespaces."],
                ans: 2,
                explanation: "Afterwords, it is possible to attach either physical or virtual interfaces to the newly created namespace (each network interface is present in exactly one namespace)[cite: 6]."
            },
            {
                q: "What is the default state of the Spanning Tree Protocol (STP) in Open vSwitch (OvS)?",
                options: ["Enabled by default", "Disabled by default", "Enabled only for OpenFlow mode", "Disabled only for Linux Bridge"],
                ans: 1,
                explanation: "The default configuration of OvS is to work in bridging mode. However, the Spanning Tree Protocol is disabled by default and must be turned on with the appropriate command[cite: 7]."
            },
            {
                q: "Which command is used to add a VLAN tag (e.g., VLAN 100) to a port in OvS?",
                options: [
                    "sudo ovs-ofctl add-flow vnet0 tag=100",
                    "sudo ovs-vsctl set port vnet0 tag=100",
                    "sudo ip link set dev vnet0 vlan 100",
                    "sudo ovs-vsctl set vlan vnet0 100"
                ],
                ans: 1,
                explanation: "The command that sets a VLAN ID on a port is 'sudo ovs-vsctl set port vnet0 tag=100', where port is one of the columns defined in the Open vSwitch database schema[cite: 7]."
            },
            {
                q: "How does Open vSwitch persist its configuration across system reboots?",
                options: [
                    "It reads from an XML file at startup.",
                    "It relies on the root namespace startup scripts.",
                    "It stores its configuration in a local database.",
                    "OvS configurations are ephemeral and do not survive reboots."
                ],
                ans: 2,
                explanation: "As OvS uses a local database to store its configuration, the configuration is preserved even if we reboot the machine[cite: 7]."
            },
            {
                q: "Which interface is used to connect a network namespace to the root namespace?",
                options: ["Loopback device", "GRE tunnel", "Virtual Ethernet pair (veth)", "VLAN interface"],
                ans: 2,
                explanation: "To connect the ns1 namespace to the 'root namespace', we need to create a Virtual Ethernet Device (veth), a network abstraction that can be seen as a wire with two ends, attached to different namespaces[cite: 10]."
            },
            {
                q: "What happens if a namespace attempts to ping its own loopback address or an internal IP address while the loopback interface ('dev lo') is in the DOWN state?",
                options: [
                    "The ping succeeds using the physical kernel loopback.",
                    "The ping fails; no addresses inside the namespace can be pinged.",
                    "Only the specific internal IP fails, but 127.0.0.1 succeeds.",
                    "The loopback interface automatically comes UP."
                ],
                ans: 1,
                explanation: "Note: in case the loopback device is down, you cannot ping neither the loopback address nor any additional address you may have in the namespace (e.g., the address 10.255.0.1)[cite: 10]."
            },
            {
                q: "Which command correctly lists all current network namespaces?",
                options: ["sudo ovs-vsctl show", "ip netns list", "ip link show netns", "sysctl list-netns"],
                ans: 1,
                explanation: "The list of available NET namespaces is visible by typing 'ip netns list' (or the shortest version 'ip netns')[cite: 10]."
            },
            {
                q: "When converting an OvS bridge to pure OpenFlow mode by deleting the default L2 bridging logic, which command must be issued?",
                options: [
                    "sudo ovs-vsctl emer-reset",
                    "sudo ovs-ofctl del-flows ovs-br0 priority=0 --strict",
                    "sudo ip link del br0",
                    "sudo ovs-vsctl del-br ovs-br0"
                ],
                ans: 1,
                explanation: "To delete the normal flow (which implements the classical L2 behavior and is characterized by priority equal to 0): 'sudo ovs-ofctl del-flows ovs-br0 priority=0 --strict'[cite: 16, 17]."
            },
            {
                q: "What command creates a Linux Bridge named 'br0'?",
                options: [
                    "sudo ovs-vsctl add-br br0",
                    "sudo ip link add br0 type bridge",
                    "sudo brctl create br0",
                    "sudo ip link set type bridge name br0"
                ],
                ans: 1,
                explanation: "Create a new Linux Bridge called 'br0': 'sudo ip link add br0 type bridge'[cite: 11]."
            },
            {
                q: "How must you configure a third namespace to act as a router between two other namespaces on different IP networks?",
                options: [
                    "Install OvS in the namespace and enable STP.",
                    "Create a Linux bridge inside the namespace.",
                    "Enable IP forwarding via sysctl and attach the respective veth endpoints.",
                    "Set the namespace to 'promiscuous' mode."
                ],
                ans: 2,
                explanation: "The routing functionality is automatically provided by Linux itself, which forwards packets based on the entries of the corresponding routing table. However, IP forwarding may not be enabled by default and might require manual activation: 'sudo ip netns exec ns-br sysctl net.ipv4.ip_forward=1'[cite: 19]."
            },
            {
                q: "If namespaces ns1 and ns2 are on different IP subnets and routed through ns-br, why would a ping initially fail even if IP forwarding is enabled?",
                options: [
                    "The veth pairs inherently block L3 traffic.",
                    "The root namespace drops the packets.",
                    "The namespaces lack a specific route for the remote destination.",
                    "The OvS bridge must be configured with an IP address."
                ],
                ans: 2,
                explanation: "The problem is related to the routing table of the namespaces, which do not have any specific route for the remote destination. The 'ip route' command must be used to add routes via the gateway IP[cite: 19]."
            },
            {
                q: "Which GRE tunnel variation encapsulates a payload with just its IP header (L3)?",
                options: ["gretap", "gretun", "ipsec", "veth"],
                ans: 1,
                explanation: "GRE can encapsulate a payload with just its IP header or the entire L2 frame. In the first case it is named gretun, while the latter is a gretap[cite: 24]."
            },
            {
                q: "Which interfaces are automatically generated by the kernel module when configuring a GRE tunnel and cannot be removed?",
                options: [
                    "veth0 and veth1",
                    "lo and br0",
                    "gre0, gretap0, and erspan0",
                    "tun0 and tun1"
                ],
                ans: 2,
                explanation: "Listing all interfaces, you may notice that a couple of additional ones have been created (gre0, gretap0 and erspan0). These interfaces are special and are required for the correct functioning of the kernel module... and cannot be removed[cite: 27]."
            },
            {
                q: "To allow network namespaces to reach external Internet destinations, what type of iptables rule must be applied on the physical host?",
                options: [
                    "PREROUTING DNAT",
                    "POSTROUTING MASQUERADE",
                    "FORWARD ACCEPT",
                    "INPUT DROP"
                ],
                ans: 1,
                explanation: "Adding the correct NAT rule maps the private IP addresses of the namespaces to the 'public' one of the host through a MASQUERADE rule: 'sudo iptables -t nat -A POSTROUTING --source 10.255.0.0/24 -j MASQUERADE'[cite: 27, 28]."
            },
            {
                q: "How can you resolve DNS issues inside a namespace caused by systemd-resolved listening only in the root namespace?",
                options: [
                    "By running 'systemctl restart systemd-resolved' inside the namespace.",
                    "By configuring the OvS bridge to act as a DNS forwarder.",
                    "By creating a custom resolv.conf inside /etc/netns/NS_NAME/.",
                    "DNS resolution is impossible inside a namespace."
                ],
                ans: 2,
                explanation: "DNS resolution may not work inside network namespaces... To solve the problem, it is possible to create a custom /etc/resolv.conf for each namespace... by creating a resolv.conf file in the /etc/netns/NS_NAME path, which will be automatically mounted[cite: 28]."
            },
            {
                q: "When executing commands inside a namespace, what is the correct syntax prefix?",
                options: [
                    "sudo netns exec <namespace_name>",
                    "ip exec netns <namespace_name>",
                    "sudo ip netns exec <namespace_name>",
                    "sudo ip run ns <namespace_name>"
                ],
                ans: 2,
                explanation: "A command (e.g., running an application) can be issued in the newly created namespace with 'ip netns exec <namespace_name> <command>' (often preceded by sudo)[cite: 10]."
            },
            {
                q: "What happens if a namespace interface lacks a VLAN tag but is connected to an OvS switch access port that has a VLAN tag set?",
                options: [
                    "The namespace interface drops all packets.",
                    "The packets inside the namespace act like standard Ethernet without tags, but the switch segregates them into the assigned VLAN.",
                    "The switch removes the interface automatically.",
                    "The namespace inherits the VLAN tag and displays it in its internal routing table."
                ],
                ans: 1,
                explanation: "We tag the port veth0-root with VLAN 1 (i.e., access port). Instead, ports veth0-ns1 and veth1-ns2, which are inside the two network namespaces, are not tagged at all. They look like simple Ethernet cables that connect traditional hosts, without any VLAN tags[cite: 15]."
            },
            {
                q: "When establishing an L3 GRE tunnel, what tunnel type should be specified in the 'ip link add' command?",
                options: ["type gretap", "type gre", "type tunnel", "type veth"],
                ans: 1,
                explanation: "For an L3 tunnel, the type of the tunnel is now gre (i.e. L3), instead of gretap (i.e. L2). The command is: 'sudo ip link add tun0 type gre local IP_HOST_1...'[cite: 29]."
            }
        ];

        const container = document.getElementById('quiz-container');

        quizData.forEach((item, index) => {
            const card = document.createElement('div');
            card.className = 'question-card';
            
            const qTitle = document.createElement('div');
            qTitle.className = 'question';
            qTitle.textContent = `${index + 1}. ${item.q}`;
            card.appendChild(qTitle);

            const optionsList = document.createElement('ul');
            optionsList.className = 'options';

            item.options.forEach((opt, oIndex) => {
                const li = document.createElement('li');
                const label = document.createElement('label');
                const radio = document.createElement('input');
                radio.type = 'radio';
                radio.name = `q${index}`;
                radio.value = oIndex;

                label.appendChild(radio);
                label.appendChild(document.createTextNode(opt));
                li.appendChild(label);
                optionsList.appendChild(li);
            });

            card.appendChild(optionsList);

            const feedback = document.createElement('div');
            feedback.id = `fb${index}`;
            feedback.className = 'feedback';
            card.appendChild(feedback);

            container.appendChild(card);
        });

        function submitQuiz() {
            quizData.forEach((item, index) => {
                const selected = document.querySelector(`input[name="q${index}"]:checked`);
                const feedbackDiv = document.getElementById(`fb${index}`);
                feedbackDiv.style.display = 'block';

                if (!selected) {
                    feedbackDiv.className = 'feedback incorrect';
                    feedbackDiv.innerHTML = `<strong>Incorrect!</strong> You didn't select an answer. <br><br><strong>Motivation/Explanation:</strong> ${item.explanation}`;
                    return;
                }

                if (parseInt(selected.value) === item.ans) {
                    feedbackDiv.className = 'feedback correct';
                    feedbackDiv.innerHTML = `<strong>Correct!</strong> <br><br><strong>Motivation/Explanation:</strong> ${item.explanation}`;
                } else {
                    feedbackDiv.className = 'feedback incorrect';
                    feedbackDiv.innerHTML = `<strong>Incorrect!</strong> <br><br><strong>Motivation/Explanation:</strong> ${item.explanation}`;
                }
            });
        }
    </script>
</body>
</html>

```