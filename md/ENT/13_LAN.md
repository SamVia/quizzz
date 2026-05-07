# Master Cheat Sheet: System Programming & Virtual LANs (VLANs)

## 1. Fundamentals of VLANs
### Why Multiple LANs?
A single, massive LAN is inefficient. Multiple LANs are required for:
* **Performance:** A single LAN suffers from too much broadcast traffic and flooded traffic (e.g., due to frequent Spanning Tree Protocol (STP) reconfigurations).
* **Separation of Concerns:** Enhances privacy and security. It prevents stations from leaking information and mitigates layer 2 attacks like MAC Flooding and ARP spoofing.
* **Management:** Creates smaller networks with simple, uniform policies, allowing administrators to partition different users into different LANs .
* **Resource Efficiency:** Building N distinct physical networks requires N links and N devices, which wastes resources .

### What is a VLAN?
* A VLAN allows multiple logical networks to exist on a **single physical infrastructure** (same devices, same cabling).
* It eliminates the need for switches with unused ports or multiple fiber runs in the backbone.
* Each VLAN is a **strictly separate broadcast domain**. Layer 2 Ethernet frames cannot propagate to another VLAN.

### Logical Architecture of a VLAN-Enabled Switch
* VLANs are created through logical separation inside the switch (both intra-switch and inter-switch).
* Each VLAN has its own independent **Backward Learning** process and **Filtering Database** (MAC table) .
* **Hardware Reality:** While logically separate, real implementations utilize a single unique filtering database. This is usually made with a single TCAM (Ternary Content-Addressable Memory) utilizing a VLAN ID tag to optimize resource usage, as the exact number of VLANs needed cannot be predicted *a priori*.

---

## 2. Layer 3 Interconnectivity & IP Addressing
* **The L2 Boundary:** Because a station cannot send an L2 frame directly to a station in another VLAN, broadcasts (like ARP requests) cannot cross VLAN boundaries .
* **The Router Requirement:** A device operating at Layer 3 (a router) is mandatory to interconnect VLANs. 
* **Routing Process:** The router performs a Layer 3 lookup (IP destination address). The original L2 header is completely thrown away, and a new L2 header is created with new source and destination MAC addresses.
* **Security Integration:** Routers interconnecting VLANs are often used to enforce L3 or L4/L7 protection, such as firewalls.
* **IP Rule:** Hosts residing in different VLANs **must** belong to different IP networks (e.g., Network 1: `10.0.1.0/24`, Network 2: `10.0.2.0/24`) .

---

## 3. VLAN Assignment Methods
### Static Methods
* **Port-Based VLANs:** The switch associates received frames to the VLAN explicitly configured on the receiving physical port. Only one VLAN per port is allowed.
    * *Default State:* All ports default to Access mode and are associated with VLAN 1.
    * *Pros:* Completely transparent to the user, maximum compatibility, no host configuration required . Most common choice in current networks.
    * *Cons:* Privileges depend on the physical network socket. There is no seamless Layer 3 mobility; a host must change its IP address if moved to a port on a different VLAN .

### Dynamic Methods
* **Transparent Assignment:** VLAN assigned per MAC address or per L3 protocol (IEEE 802.1v, which is no longer used).
    * *Pros:* Admin retains full control of the user-VLAN association; allows seamless mobility.
    * *Cons:* Logistical nightmare to keep the MAC database aligned (e.g., when a host changes its NIC). Mostly historical.
* **Per-User Assignment (802.1x):** The switch port is enabled only if the user authenticates successfully. The switch assigns the VLAN dynamically based on the User ID, not the host .
* **Cooperative Assignment ("Anarchic" VLANs):** Users maintain control by explicitly setting the VLAN ID on their NICs.
    * *Mobility:* Allows seamless mobility within a campus but creates problems if the user connects to a different network (e.g., home) .
    * *Risks:* Users can join the wrong VLAN due to negligence or bad will.
    * *Use Case:* Highly trusted devices controlled by network admins, such as routers or servers that must participate in multiple VLANs . Requires manual configuration on PCs and the usage of Trunk interfaces on the switch .

---

## 4. Tagging and Frame Structure (IEEE 802.1Q)
When multiple VLANs must cross a single link (e.g., switch-to-switch), the receiving switch must be able to differentiate the frames.

### Tagging vs. Tunneling
* **Tagging (IEEE 802.1Q):** The standard method. Adds an additional 4-byte header directly into the MAC header .
* **Tunneling (Old Method):** Encapsulated the entire Ethernet (or Token Ring/FDDI) frame inside another frame using proprietary solutions like Cisco's ISL (Inter-Switch Link) .

### IEEE 802.1Q Tag Encoding Rules
The 802.1Q tag can be encapsulated in standard Ethernet (DIX) or any link layer using LLC SNAP. In both cases, the max frame length must be extended by 4 bytes (e.g., Ethernet grows from 1518 to **1522 bytes**). *Note: The minimum frame length remains unchanged at 64 bytes. Standard Hubs cannot handle frames > 1518 bytes and will fail*.

**The 32-bit (4-byte) Tag Format:**
1.  **TPID (Tag Protocol Identifier) [16 bits]:** Uses the Ethertype `0x8100` to indicate a VLAN-tagged frame.
2.  **PCP (Priority Code Point) [3 bits]:** Dictates the User Priority (maps to IEEE 802.1p priority).
3.  **CFI (Canonical Format Indicator) [1 bit]:** * `1`: MAC address in non-canonical format (e.g., Token Ring).
    * `0`: Standard canonical format (e.g., Ethernet).
4.  **VID (VLAN Identifier) [12 bits]:** Values range from `1-4094`.
    * `1`: Usually the default VLAN.
    * `0xFFF`: Reserved.
    * `0`: Indicates the frame does *not* belong to any VLAN. This is used exclusively when a user wants to set 802.1p priority for their traffic without assigning a VLAN .

---

## 5. Link Types & Native vs. Default VLANs

### Link Types
1.  **Access Links:** Receive and transmit only **untagged** frames. This is the default configuration for hosts, switches, and end-stations. The VLAN configured on an access port is *not* propagated outside the switch .
2.  **Trunk Links:** Receive and transmit **tagged** frames. Must be explicitly configured. Used primarily for switch-to-switch, router, or server connections. Cannot utilize hubs .
3.  **Hybrid Links:** Accept both tagged and untagged frames, differentiating them by the presence of the `0x8100` Ethertype. Most trunk links function inherently as hybrid links due to the Native VLAN .

### Native VLAN vs. Default VLAN
These are orthogonal concepts.
* **Native VLAN (Trunk Link Concept):** Dictates which frames travel *untagged* over an 802.1Q trunk interface. All untagged traffic received on a trunk port is assigned to the Native VLAN, and any traffic destined for the Native VLAN is transmitted untagged . *Warning: If two adjacent switches have different native VLANs configured, traffic will leak into the wrong VLAN*.
* **Default VLAN (Access/Management Concept):** Dictates management behaviors (STP, CDP, VTP) and is the fallback VLAN for unconfigured access ports (usually VLAN 1).
* *Example Application:* If Default VLAN = 1 and Native VLAN = 2 on a switch, traffic originating from an access port defaults to VLAN 1, but traffic crossing the trunk link belonging to VLAN 2 goes entirely untagged .

---

## 6. Advanced Architecture & Multiple VLANs per NIC

When devices (like servers or routers) must exist in multiple VLANs simultaneously, they use a single physical Trunk connection combined with internal software configurations .

### The One-Arm Router (Router on a Stick)
* Replaces the need for multiple physical ports and cables on a router. It mimics a multi-port router using software .
* **Architectural Rule:** The software requires the creation of virtual interfaces (V-NICs) matching the number of VLANs. 
* **Configuration Rule:** Each virtual interface handles exactly one VLAN ID and requires its own unique Layer 3 IP configuration (IP address and Default Gateway). Crucially, the IP addresses associated with these virtual interfaces **must belong to different IP networks** .

### Duplicated MAC Addresses
Because V-NICs or virtual machines often share or duplicate MAC addresses, collisions might seem likely. However, switches handle the filtering databases of different VLANs as strictly distinct entities. Duplicate MACs do not cause troubles as long as they belong to different VLANs .

---

## 7. Optimizing Backbone Traffic & GVRP

To prevent switches from flooding broadcast traffic across trunk links to switches that do not have active ports for that VLAN, traffic must be filtered . This can be done manually, via proprietary methods, or automatically using **GVRP**.

### GARP and GVRP
* **GARP (Generic Attribute Registration Protocol):** Defined in IEEE 802.1p. Registers/unregisters attributes into a switch entity called GID (GARP Information Distribution). Uses GIP (GARP Information Propagation) to spread state machines across bridges via LLC type 1 .
* **GVRP (GARP VLAN Registration Protocol):** A specialization of GARP. A GVRP-Aware switch registers its known VLANs with the remote switch across a trunk. It prunes uninterested switches from the VLAN tree to optimize broadcast traffic . GVRP operates strictly on the STP active topology. *Note: It adds CPU load and complexity (bugs), making it less popular than manual configuration for robust networks* .

### Exact GVRP Packet Format Data Trace
```text
[Destination MAC]   01-80-C2-00-00-21 (Multicast)
[Source MAC]        Bridge Unicast Address
[Protocol ID]       00-01
[Attribute Type]    01
[Attribute Length]  04
[Attribute Event]   0 = LeaveALL, 1 = JoinEmpty, 2 = JoinIn, 
                    3 = LeaveEmpty, 4 = LeaveIN, 5 = Empty
[VLAN ID]           (Target VLAN)
[End Mark]          00
```


---

## 8. VLANs and Spanning Tree Protocol (STP)

Theoretically, VLANs and STP are independent (STP disables loops first, and VLANs utilize the resulting unique forwarding tree) . However, this wastes bandwidth on blocked links. 

### Per-VLAN Spanning Tree (PVST)
Allows multiple spanning trees (one per VLAN), optimizing network load across all physical links .
* **CPU Limitation:** Running $N$ instances of STP simultaneously increases CPU load significantly.
* **Bridge Priority Rule:** To prevent all VLANs from building the exact same topology, the Bridge Priority parameter must be manually configured per-VLAN to differentiate the Root Bridge.

### Cisco's STP Implementations
Cisco strictly forces per-VLAN STP (it cannot be turned off to fall back to a single STP tree).
* **PVST:** Old solution using ISL tunneling.
* **PVST+:** Modern implementation using 802.1Q tagging.
* **Rapid-PVST+:** Applies PVST architecture to RSTP for fast convergence using 802.1Q.

**Cisco Bridge ID Breakdown (16 bits):**
* **Bridge Priority:** 4 bits (Default is 8)
* **STP Instance (VLAN ID):** 12 bits (Default is 0)


**Bridge ID Trace Example:**
If VLAN 2 is assigned Priority 32768: `1000 0000 0000 0010`.
If VLAN 3 is assigned Priority 28672: `0111 0000 0000 0011`.

### STP Compatibility & Untagged BPDU Rule
* Interoperability between PVST switches and non-PVST switches causes broadcast storms and broken topologies.
* **BPDU Tagging Rule:** Can STP BPDUs have VLAN tags? No. On Cisco, standard STP is the "last resort" protocol for backward compatibility. Standard STP BPDUs are **always untagged** and mapped strictly to VLAN 1 (the unchangeable default VLAN on Cisco).
* If Native VLAN = 2, PVST BPDUs for VLAN 2 are sent untagged. PVST BPDUs for VLAN 1 will be tagged.

---

## 9. Network Isolation Limits & Switch Hardware

### Incomplete Network Isolation
VLANs do not offer 100% hardware isolation. Because physical links are shared, a broadcast storm occurring in one VLAN can flood and saturate a shared trunk link. While the broadcast frames won't bleed into other VLANs, the physical congestion denies service to the other VLANs sharing the trunk. Solving this requires strict Per-VLAN QoS (Quality of Service), such as a "Round-robin" service model to guarantee minimum bandwidth per VLAN .

### VLAN-Aware vs. VLAN-Unaware Switches
VLANs are not "plug and play" like basic STP.
* **VLAN-Aware (Professional/Enterprise):** Hardware designed to read, handle, and forward tagged and untagged frames.
* **VLAN-Unaware (SOHO/Domestic):** Hardware that does not understand 802.1Q tags. Because tags extend the frame to 1522 bytes, these switches will often flag the frames as "too big" and silently discard them . 
* **The Danger of Mixing:** Placing a VLAN-unaware switch inside a backbone will partition the network. Trunks will drop, and STP blocked ports will fail to open properly, isolating host groups entirely. VLAN-unaware switches are only safe at the extreme access edge, provided all connected hosts strictly belong to the exact same VLAN.

---

## 10. Practical Exercises: Cisco IOS Configuration Guide

Below are exact system call traces and commands for managing VLANs based on Cisco IOS.

### Scenario 1: Creating a VLAN
*(Note: Older systems use the `vlan database` mode, modern IOS allows this in standard config mode.)*
```text
switch# vlan database
switch(vlan)# vlan 2 name Administration
VLAN 2 added:
Name: Administration
switch(vlan)# exit
APPLY completed.
Exiting....
switch#
```


### Scenario 2: Associating a Port to an Access VLAN
Assign physical port FastEthernet 0/1 to VLAN 2.
```text
switch# configure terminal
switch(config)# interface FastEthernet 0/1
switch(config-if)# switchport access vlan 2
switch(config-if)# exit
```


**Verification Trace:**
```text
switch# show vlan brief
VLAN Name           Status    Ports
1    default        active    Fa0/2, Fa0/3, Fa0/4
2    Administration active    Fa0/1
```


### Scenario 3: Configuring a Trunk Link & Allowed VLANs
Set FastEthernet 0/2 to trunk mode and restrict it to only carry VLANs 1 and 2.
```text
switch# configure terminal
switch(config)# interface FastEthernet 0/2
switch(config-if)# switchport mode trunk
switch(config-if)# switchport trunk allowed vlan add 1,2 
switch(config-if)# exit
```
*(Note: "add all" can also be used)*


### Scenario 4: Checking Trunk Interface & Modifying Native VLAN
Check current trunk, modify the Native VLAN from 1 to 2, and verify the change.
```text
cisco# show interface Fa0/8 trunk

Port   Mode  Encapsulation  Status  Native vlan
Fa0/8  on    802.1q         other   1

cisco(config-if)# switchport trunk native vlan 2

cisco# show interface f0/8 trunk

Port   Mode  Encapsulation  Status  Native vlan
Fa0/8  on    802.1q         other   2
```


---

## 11. IEEE Protocol Standards Summary

* **IEEE 802.1Q:** Defines VLAN-aware bridges, per-port VLAN assignment (access/trunk), multiple filtering databases identified by FID (Filtering Identifier), frame tagging encapsulation, and GVRP .
* **IEEE 802.3ac:** Defines the new Ethernet frame format accounting for VLAN tagging, officially extending the maximum frame size from 1518 bytes to 1522 bytes .
* **IEEE 802.1p:** Defines the Packet priority field (3-bit User Priority) and GARP (Generic Attribute Registration Protocol).

---

## **Part I: VLAN Stacking & Backbone Technologies**

### **1. VLAN Stacking (IEEE 802.1ad)**
VLAN Stacking allows a backbone provider, such as a metro Ethernet operator, to transport Layer 2 tagged traffic from customers across their network. 

* **Also Known As:** Provider bridging, Stacked VLANs, QinQ (or Q-in-Q).
* **Core Mechanism:** It requires adding multiple VLAN tags to an Ethernet frame, overcoming the original 802.1Q specification which only allows a single VLAN tag. This creates a "VLAN tag stack".
* **Tag Structure:**
    * **Outer Tag:** Known as the Service Tag or S-TAG, representing the provider. The preceding Ethertype header is `0x88A8`.
    * **Inner Tag:** Known as the Customer Tag or C-TAG. The preceding Ethertype header is `0x8100`.
* **Frame Format:** The frame begins with MAC Destination and MAC Source. This is followed by the Outer Tag (Ethertype `0x88A8` + VLAN ID) , the Inner Tag (Ethertype `0x8100` + VLAN ID) , the original Ethertype (e.g., `0x800` for IP) , the Payload Data , and the FCS.
* **Advantages:**
    * Extends the VLAN-ID range beyond the original 12 bits, which is often insufficient for large installations.
    * Each stack maintains its own Priority (PRI) field, allowing different priorities per stack.
    * Highly flexible and non-disruptive, allowing different entities (like different companies) to reuse the same VLAN-IDs.
    * Tags can be easily added or removed using push and pop operations.
* **Limitations & Problems:**
    * **Scale:** A Metro provider can support a maximum of 4096 customers unless an additional tag is used. Furthermore, the provider must learn and store the MAC addresses of all customers, leading to scalability issues where core switches reach their MAC table limits.
    * **Performance & Security:** Broadcast and flooded traffic (from unknown addresses) can degrade overall backbone performance. Broadcast storms in one company's network could negatively impact other companies.
    * **Duplicated MAC Addresses:** If different customers use the same MAC address, it is unproblematic at the edge. However, once inside the metro network, the frames appear indistinguishable because the inner customer VLAN tag is not used for forwarding decisions. The metro network sees the same MAC address arriving from potentially different sources.

### **2. Provider Backbone Bridges (PBB / IEEE 802.1ah)**
PBB was introduced to overcome the scalability and duplicated MAC limitations of 802.1ad. It is now part of the 802.1Q-2011 standard.

* **Also Known As:** MAC-in-MAC.
* **Core Mechanism:** PBB-Edge switches encapsulate customer traffic inside an entirely new MAC-in-MAC frame. It adds new source and destination MAC addresses that point exclusively to the ingress and egress backbone bridges. Core bridges do not learn customer MAC addresses; they only know edge bridge addresses.
* **Addressing & Forwarding:**
    * **B-DA (Backbone Destination Address):** Determined by the customer's Destination Address.
    * **Forwarding Logic:** Core switches forward frames based on the Backbone Destination Bridge Address and a 60-bit Backbone-VLAN ID.
    * **Unicast Traffic:** If the MAC destination is known, the PBB destination address is the MAC address of the exit bridge connecting to the target.
    * **Broadcast/Multicast/Flooded:** The PBB destination address is derived from the target MAC and flooded across the entire PBB network to learn the location of customer MAC addresses.
* **PBB Frame Format Specifications:**
    * The EtherType used is similar to 802.1ad Q-in-Q.
    * Frame order: `B-DA` (48 bits) -> `B-SA` (48 bits) -> `Type 0x88A8` (16 bits) -> `B-VID` (16 bits) -> `Type 0x88C8` (16 bits) -> `I-SID` (32 bits) -> `C-DA` (48 bits) -> `C-SA` (48 bits) -> `Type 0x88A8` (16 bits) -> `S-VID` (16 bits) -> `Type 0x8100` (16 bits) -> `C-VID` (16 bits) -> `Type` (16 bits) -> `Payload`.
    * The structure is logically broken down into the Backbone Headers (B-DA, B-SA, B-Tag), the Service Instance Tag (I-Tag), and the original Customer frame (C-MACs, S-Tag, C-Tag) .

---

## **Part II: Private VLANs (PVLANs)**

When a massive number of tiny VLANs are required (e.g., hotel rooms, apartments, server racks, ADSL DSLAMs), standard VLANs fail due to configuration complexity, the 4094 VLAN limit, and IP address exhaustion from assigning `/30` subnets to each VLAN . The solution is Private VLANs, also known as "Port isolation". 

### **1. Private VLAN Edge (PVLAN Edge)**
A simplified, potentially interoperable segmenting mechanism implemented in Cisco switches.

* **Protected Ports:** Layer 2 traffic originating from a protected edge port cannot be forwarded to any other protected edge port.
* **Non-protected Ports:** Layer 2 traffic originating from a non-protected edge port can be forwarded to any other port.
* **Consequences & Use Cases:** Direct peer-to-peer Layer 2 traffic between protected hosts is completely blocked. This is used to allow clients access to shared resources (like a default gateway or shared printer) without letting them see each other. 
* **L3 Communication:** Communication between isolated peers is theoretically possible at higher layers (via routers/firewalls), but requires the router to answer ARP requests on behalf of the protected hosts. A traditional Layer 2 switch will never forward a frame back out the exact same port it arrived on.
* **Multi-Switch Topology Limitations:** Protection can be maintained across edge switches if the aggregation switch uses protected ports facing the edge switches. However, this severely limits flexibility; for example, a host on one edge switch cannot access a shared printer attached to another edge switch if the traffic must cross protected ports on the aggregation switch.

**Code: PVLAN Edge Configuration** 
```cisco
! Router Configuration
interface FastEthernet 0
 ip address 10.0.0.1 255.255.255.0
!
! Switch Configuration
interface FastEthernet 0/0
 switchport mode access
!
interface range FastEthernet 0/1
 switchport mode access
 switchport protected
 switchport block unicast
 switchport block multicast
!
```
*Note: Ports are often configured to block unknown unicast and multicast flooding for added security.*

### **2. Full Private VLANs**
A Cisco proprietary extension of the PVLAN Edge concept for complex deployments . 

* **Domain Hierarchy:** A single Private VLAN domain consists of one Primary VLAN, at most one Secondary Isolated Subdomain, and an arbitrary number of Secondary Community Subdomains.
* **Subdomain Rules:**
    * **Isolated VLAN:** Ports within an isolated VLAN cannot communicate with each other.
    * **Community VLAN:** Ports within a community VLAN can communicate with one another, but cannot communicate with ports in other communities.
* **Port Types & Forwarding Behaviors:**
    * **Promiscuous Port:** Belongs to the Primary VLAN. It can communicate with all interfaces in the domain, including isolated and community host ports. Traffic flows downstream from the promiscuous port to all host ports.
    * **Isolated Port:** Has complete L2 isolation from all other ports in the domain, except for promiscuous ports. Traffic flows upstream only to promiscuous ports. All other traffic to isolated ports is blocked.
    * **Community Port:** Communicates with other ports in the same community and with promiscuous ports. It is strictly isolated at Layer 2 from interfaces in other communities and from isolated ports. Traffic flows upstream to the promiscuous port and peer community ports.
* **IP Addressing Strategy:** The IP address space is assigned entirely to the Primary VLAN. DHCP requests from secondary VLANs are served from this same space. This means all hosts can share a single address space, drastically reducing the IP fragmentation caused by partitioning addresses across multiple traditional VLANs.
* **PVLANs Across Multiple Switches:** PVLAN topologies can span multiple devices by trunking the primary, isolated, and community VLANs. However, only the Primary VLAN is visible externally (outside the domain).

**Code: Full Private VLAN Configuration** 
```cisco
! Defining the VLANs
vlan 1000
 private-vlan primary
 private-vlan association 1001,1002,1003
!
vlan 1001
 private-vlan community
!
vlan 1002
 private-vlan community
!
vlan 1003
 private-vlan isolated
!

! Configuring a Promiscuous Port (e.g., towards a Router)
interface FastEthernet0/0
 switchport mode private-vlan promiscuous
 switchport private-vlan mapping 1000 1001,1002,1003
!

! Configuring Host Ports in Community 1001
interface FastEthernet0/1
 switchport mode private-vlan host
 switchport private-vlan host-association 1000 1001
!
interface FastEthernet0/2
 switchport mode private-vlan host
 switchport private-vlan host-association 1000 1001
!

! Configuring a Host Port in Community 1002
interface FastEthernet0/3
 switchport mode private-vlan host
 switchport private-vlan host-association 1000 1002
!

! Configuring a Trunk Port (to propagate PVLANs across switches)
interface FastEthernet 0/7
 switchport trunk encapsulation dot1q
 switchport mode trunk
!
```
*Note: All VLANs are propagated on trunk ports, which requires VTP. There is no difference in the interface-level configuration commands when assigning ports to a community vs. an isolated subdomain.*



