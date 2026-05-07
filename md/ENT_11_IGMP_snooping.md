# Master Cheat Sheet: IGMP Snooping
**Source Material:** "IGMP Snooping" by Fulvio Risso, Politecnico di Torino. Based on chapter 8 of M. Baldi, P. Nicoletti, "Switched LAN".

---

## 1. Packet Transmission Basics on a Switched LAN
Understanding how different traffic types are natively handled by a switch establishes the need for multicast optimizations.
* **Unicast:** Packets are forwarded exclusively on the port toward the specific destination.
* **Broadcast:** Packets are handled via flooding, meaning they are forwarded on all interfaces except the receiving one. There are no other solutions possible as frames cannot be natively filtered, but networks generally do not expect too much broadcast traffic.
* **Multicast:** By default, multicast traffic is also handled via flooding. This creates severe scalability problems when dealing with heavy traffic, such as delivering 50 courses in HDTV in real-time at 20Mbps each. A necessary alternative to flooding is knowing the exact location of members for each specific multicast group.

## 2. GMRP: The Precursor (GARP Multicast Registration Protocol)
Before IGMP snooping became prevalent, GMRP was introduced to handle multicast at Layer 2.
* **Definition:** GMRP is an instantiation of the Generic Attribute Registration Protocol (GARP). GARP is a meta-protocol defined in IEEE 802.1D that allows the registration of generic per-PC attributes in a VLAN.
* **Mechanism:** It allows end systems to communicate their group membership to the switch. The switch then communicates to its adjacent switches which groups are active on that specific portion of the network.
* **Adoption Failure:** GMRP is barely used. Although it was defined years ago and is supported by most switches, it is largely unsupported by applications and operating systems.

## 3. The Transition to IGMP Snooping
Rather than complicating network operations and management with an additional L2 protocol like GMRP, the industry shifted to leveraging existing L3 mechanisms.
* The multicast problem is naturally solved in multicast IP routing using IGMP (Internet Group Management Protocol) and various multicast routing protocols.
* **Core Assumption:** The primary architecture assumes that all the traffic is IPv4.
* **Standardization Status:** IGMP Snooping is technically not a standard, but it is a commonly used technology across the networking industry.

## 4. IP-to-MAC Multicast Mapping on Ethernet
To snoop efficiently, switches must map Layer 3 IP multicast addresses to Layer 2 Ethernet MAC addresses. 
* **Address Overlap:** A single multicast MAC address directly corresponds to $2^{5}$ distinct IP addresses. 
* **Collision Generation:** This overlap occurs because there are 5 bits which may generate collisions on the MAC address mapping.
* **Mathematical Mapping Breakdown:**
    * **Multicast IP Address:** Follows the binary format `$1110x_{27}x_{26}x_{25}x_{24}x_{23}x_{22}x_{21}x_{20}x_{19}x_{18}x_{17}x_{16}...x_{0}$`.
    * **Multicast MAC Address:** Follows the hex/binary format `01-00-5E` appended with `$0x_{22}x_{21}x_{20}x_{19}x_{18}x_{17}x_{16}...x_{0}$`.
* **Reserved Ranges:** The IEEE specifically reserved the MAC addresses ranging from `01-00-5E-00-00-00` to `01-00-5E-7F-FF-FF` (Global - Group addresses) for IP multicast traffic.

## 5. IP Multicast Address Scopes
Switches classify IP multicast addresses into categories that either require or bypass IGMP processing.
* **Addresses that DO NOT require IGMP:** `224.0.0.0` through `224.0.0.255`. These are strictly reserved for special "well-known" multicast addresses.
* **Addresses that DO require IGMP:**
    * **Globally-scoped:** `224.0.1.0` through `238.255.255.255`. These are Internet-wide multicast addresses.
    * **Administratively-scoped:** `239.0.0.0` through `239.255.255.255`. These are local multicast addresses.

## 6. IGMP Snooping Mechanisms & Architecture
The switch actively listens (snoops) to IGMP messages passed between hosts and routers to build dynamic forwarding tables.
* **Traffic Distinction:** Switches must natively distinguish between "well-known" multicast addresses and dynamic addresses. Traffic belonging to well-known addresses must pass without any IGMP signalling.
* **Communication Prerequisites:** Sending and receiving multicast packets must be preceded by a message coming from the multicast router (mrouter) and a registration to the group identified by its IP (multicast) address `G`.
* **Host Membership Reports (HMR):** End hosts send IGMP host membership report messages. These are transmitted inside a level 2 multicast frame addressed to the multicast MAC `g` belonging to IP address `G`.
* **The Snooping Process:**
    * **Query Snooping:** Switches snoop *Host membership query* messages to securely learn which interface is directed toward the mrouter.
    * **Report Snooping:** Switches snoop *Host membership report* messages to learn exactly on which interfaces there are active members of group `g`.
* **Switch Responses & Table Updates:**
    * Using the snooped data, switches update their internal multicast forwarding tables.
    * The switch then generates and sends exactly *one* HMR message on the "uplink" toward the mrouter.
    * **Crucial Rule:** This uplink HMR message is explicitly not propagated on other interfaces; this restriction exists so the switch is able to discover all individual listeners independently.

## 7. Practical Forwarding Application
Once the tables are populated, the switch applies strict forwarding rules.
* **Example Multicast Table state:** A switch maintains a dynamic map grouping L3 addresses to physical ports (e.g., Group "all" -> Port 1; Group "Green" -> Ports 1,3; Group "Blue" -> Ports 1,6; Group "Orange" -> Ports 1,7,8).
* **Well-known Addresses Rule:** Packets destined for well-known addresses are forwarded on all ports via flooding.
* **Dynamic Addresses Rule:** Packets destined for dynamic addresses are forwarded exclusively to the specific ports explicitly set in the multicast table.

## 8. Architectural Limitations and Conclusions
While functional, IGMP snooping introduces specific architectural conflicts.
* **Operational Reality:** Despite not being a standardized protocol, IGMP snooping works smoothly in modern networks.
* **OSI Model Violation:** Snooping represents a strict violation of the OSI model because Layer 2 switches are required to recognize and process part of the Layer 3 IP header.
* **L3 Protocol Compatibility Issues:** Network administrators must be careful regarding IPv6 and other non-IPv4 L3 protocols. To properly support these, networks need a feature that is entirely equivalent to IGMP snooping but designed for those specific protocols.
* **The Blocking Edge-Case:** If an equivalent feature is not available, non-IPv4 multicast traffic may be blocked by the switch. In this scenario, a possible (and often the only) option is to completely disable IGMP snooping and handle all multicast traffic via flooding.
