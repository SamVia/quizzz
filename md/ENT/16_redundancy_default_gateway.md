# Master Cheat Sheet: Redundancy of the Default Gateway

## 1. Introduction and Core Problem
In enterprise networks, routers (Default Gateways) connect local hosts to remote networks. 
* **The Single Point of Failure (SPOF):** If the local router fails, connectivity is lost. 
* **Why Duplication Isn't Enough:** Simply adding a second router to the LAN does not solve the problem because the Default Gateway (DG) configured on the end-hosts is fixed. Hosts on a LAN cannot learn network topology via Layer 3 routing protocols.
* **Standard Solutions:** HSRP, VRRP, and GLBP.

---

## 2. Hot Standby Routing Protocol (HSRP)

### 2.1 Protocol Overview
* **Definition:** A Cisco proprietary protocol defined in RFC 2281. Its specifications are public, but it cannot be implemented by other manufacturers.
* **Objectives:** Provide redundancy for the default gateway and attempt load balancing (though load balancing is not handled very well natively).
* **Core Mechanism:** Multiple routers belong to the same "HSRP Group," which emulates a single virtual router.
    * One router is elected **Active** (master) and operates using a **Virtual IP (vIP)** and **Virtual MAC (vMAC)**.
    * If the Active fails, the vIP and vMAC are moved to the Stand-by router.

### 2.2 Router States
* **Active:** The router that currently has the right to serve the LAN. It is the *only* router that processes traffic directed to the vMAC and vIP.
* **Stand-by:** The router designated to take over if the Active fails. It only serves packets destined to its *own* primary IP/MAC until promoted.
* **Listen:** All other participating routers that are neither Active nor Stand-by.

### 2.3 The Election Process
* The Active router is chosen based on the highest **Priority** (configurable default is 100).
* **Tie-breaker:** If priorities are equal, the router with the highest real IP address wins.
* **Preemption:** A configured parameter. If a new router comes online with a higher priority, it can force the current Active to step down using a "Coup" message *only* if preemption is enabled. Without preemption, the current Active retains its role until failure.

### 2.4 Timers and Keep-Alives
Routers broadcast periodic "Hello" keep-alive packets for election and failure tracking. Listen routers do *not* generate Hellos unless the Active or Stand-by fails.
* **Hello-Time:** Period between Hello messages (Default: 3 seconds).
* **Hold-Time:** Time a Backup router waits before proposing itself as Active if no Hellos are received (Default: 10 seconds).
* **Convergence:** HSRP convergence takes approximately 10 seconds under default settings.

### 2.5 Addressing Rules
* **Active Router Interface:** Holds the Primary IP, Physical MAC, Virtual IP, and Virtual MAC.
* **Standby/Listen Interface:** Holds only the Primary IP and Physical MAC.
* **Virtual MAC Format (Standard):** `00-00-0C-07-AC-xx` (where `xx` is the HSRP Group in hexadecimal). `00-00-0C` is a Cisco OUI. Valid groups: 0-255.
* **Virtual MAC Format (Token Ring):** Token Ring behaves differently. Valid groups are 0, 1, and 2. MACs are `C0-00-00-01-00-00`, `C0-00-00-02-00-00`, and `C0-00-00-04-00-00`.

### 2.6 HSRP Packet Format & Encapsulation
* **Encapsulation:** UDP. Source and Destination Port is 1985.
* **IP Layer:** Multicast to `224.0.0.2` ("all routers"). Does not require IGMP, bypasses IGMP Snooping. Source IP is the router's real IP. TTL = 1.
* **MAC Layer:** Destination is derived from `224.0.0.2`. Source MAC is the Virtual MAC.
* **Op Code Field:**
    * `0 = Hello` (Running/Capable) 
    * `1 = Coup` (Wants to be Active) 
    * `2 = Resign` (No longer wants to be Active) 
* **State Field:**
    * `0 = Initial` (HSRP not running) 
    * `1 = Learn` (Waiting for vIP from Active) 
    * `2 = Listen` (Knows vIP, but is neither Active nor Standby) 
    * `4 = Speak` (Actively participating in election) 
    * `8 = Standby` (Candidate for next Active) 
    * `16 = Active` (Currently forwarding packets for vMAC) 
* **Authentication Data:** 8-character clear-text password. Default is "cisco".

### 2.7 HSRP Configuration & Architecture Rules
* **Per-Interface Operation:** HSRP is not a router-wide function; it is specific to a given IP network and configured per-interface.
* **VLANs:** Each VLAN represents a separated LAN and requires its own HSRP group on a specific virtual sub-interface.
* **Gratuitous ARP:** When a router becomes Active, it sends a broadcast gratuitous ARP Reply (`Virtual IP is at Virtual MAC`). This updates switch Filtering Databases and helps older OSs/Token ring environments.
* **The "Track" Function:** Tracks the link-layer status of an interface (e.g., a WAN link). If it goes down, it dynamically decreases HSRP Priority (default is by 10) to force a failover. *Warning:* Tracking is useless if connected to an active L2 switch where the physical link stays up despite downstream routing failures.
* **Configuration Code Trace:**
```cisco
R1(config)# interface ethernet 0
R1(config-if)# ip address 10.1.1.1 255.255.255.0
R1(config-if)# standby 24 ip 10.1.1.5
R1(config-if)# standby 24 priority 105
R1(config-if)# standby 24 preempt
```
*(Derived from source text page 39)* 

---

## 3. Virtual Router Redundancy Protocol (VRRP)

### 3.1 Protocol Overview
* **Definition:** A standard protocol defined in RFC 3768. It functions almost identically to HSRP but without infringing Cisco patents.
* **Key Distinctions from HSRP:**
    * States are **Master** and **Backup** (No "Listen" state).
    * Hello Messages are called **Advertisement** messages (Sent *only* by the Master).
    * HSRP Group is referred to as **Virtual Router ID (VRID)**.
    * A VRRP router can backup *one or more* virtual routers and control *multiple* IP addresses per Master.
    * The Master router may use an IP address that perfectly matches the group virtual router IP.
    * There is no "tracking" feature.
    * "Preempt" is the specified, baked-in behavior.

### 3.2 Addressing & Prioritization
* **Virtual MAC Address (Ethernet):** `00-00-5E-00-01-xx` (`xx` = VRID). The `C0-00-00` OUI is avoided as Cisco owns it.
* **Priority 255:** Assigned automatically to the router that owns the real IP address matching the vIP (the "virtual address owner").
* **Priority 1-254:** Normal configurable values (Default Backup is 100). Tiebreaker goes to the highest real IP address.
* **Priority 0:** Means the router stops participating. Used during an orderly shutdown of a master to force a Backup to promote immediately without timing out.
* **Authentication:** Removed in RFC 3768 (`0 = No Authentication`) because operational experience proved clear-text offered no security and caused multi-master conflicts.

### 3.3 VRRP Packet Format & Encapsulation
* **Encapsulation:** Native IP payload with **Protocol Type 112** (No UDP header).
* **IP Layer:** Multicast to `224.0.0.18`.
* **TTL Security:** Packet TTL *must* equal 255. A VRRP router will immediately discard packets where TTL â‰  255 to ensure they haven't crossed a hop.
* **Type Field:** `1 = Advertisement` (The only valid type).

### 3.4 VRRP Timers & Formulas
VRRP convergence is faster than HSRP by default, taking approximately 4 seconds.

* **Advertisement Interval:** Default is $1$ second.
* **Skew Time Formula:** Added to delay backup election proportionally to priority.
    $$Skew\_Time = \frac{256 - Priority}{256} \text{ seconds}$$ 
* **Master Down Interval Formula:** The time a Backup waits before declaring the Master dead.
    $$Master\_Down\_Interval = (3 \times Advertisement\_Interval) + Skew\_Time$$ 

---

## 4. Gateway Load Balancing Protocol (GLBP)

### 4.1 Protocol Overview
* **Definition:** Cisco proprietary protocol designed to enhance and replace HSRP.
* **Objective:** Automatic load balancing across default gateways without the configuration burden of mHSRP.
* **Core Architecture:** Uses **One Virtual IP** tied to **Multiple Virtual MAC addresses**.

### 4.2 GLBP Roles
* **Active Virtual Gateway (AVG):** One router is elected per group. It handles all ARP requests for the vIP and assigns a distinct vMAC to the forwarders.
* **Active Virtual Forwarder (AVF):** Up to 4 routers per group. They receive a vMAC from the AVG and actively route the traffic destined to that specific vMAC. If an AVF fails, another AVF takes over its assigned vMAC.

### 4.3 Load Balancing Algorithms
* **None:** Operates exactly like HSRP (no balancing).
* **Weighted:** Routers advertise their weight/capacity; the AVG assigns MACs proportionately (ideal for mismatched exit link capacities).
* **Host-dependent:** Ensures a specific host always receives the same vMAC in the ARP reply (mandatory if NAT is running externally).
* **Round Robin:** The AVG cycles sequentially through the available AVF vMACs when replying to ARP requests.

---

## 5. Practical Scenarios, Routing Behaviors & Edge Cases

### 5.1 Redundancy Limits & Asymmetric Routing
HSRP determines *first-hop* ingress to the gateway, but **has no influence on L3 routing or WAN paths**.
* **MAC Asymmetry:** DG routers use their *real* Physical MAC as the source address when delivering L3 traffic to hosts, even though hosts used the *Virtual* MAC as the destination to reach the router. Hosts experience two different MACs for send/receive operations.
* **Multi-group HSRP (mHSRP):** Used to load share by physically partitioning half the LAN hosts to one DG, and half to another. Requires complex DHCP configuration and cannot adapt dynamically if traffic is unbalanced. Load sharing with VLANs (where one router is Active for VLAN 2 and Stand-by for VLAN 3) achieves similar results.
* **Inbound Traffic Blind Spot:** HSRP cannot load-balance incoming Internet traffic. Inbound routing depends entirely on external routing protocols (e.g., OSPF, BGP).

### 5.2 Scenario: "Traffic Tromboning"
* **The Problem:** Happens when HSRP gateway selection conflicts with optimal L3 routing tables.
* **The Trace:** Host `H1` sends exit traffic to the Active `R1` (via vMAC). `R1` evaluates its routing table, removes the L2 header, and determines the best next-hop is actually `R2` on the *same* LAN segment. `R1` routes the traffic back onto the LAN to `R2`, which forwards it to the Internet.
* **Result:** Double bandwidth consumption on the local LAN segment. `R1` may generate an **ICMP Redirect** warning to `H1`.

### 5.3 Scenario: L2 Flooding due to Asymmetric Timers
* **The Problem:** Stand-by/Listen routers often process returning L3 traffic from the Internet due to asymmetric routing.
* **The Edge Case Trigger:**
    1.  Egress traffic updates switch databases along the exit path.
    2.  Ingress traffic returns via the Stand-by router, which has a long ARP Cache (e.g., 5 minutes) and knows the MAC of Host H1.
    3.  However, the Layer 2 Switch's Filtering Database (FDB) has a shorter *Max Ageing Time* (e.g., 2 minutes).
    4.  The switch has forgotten which port H1 is on.
* **Result:** Because the switch lacks the FDB entry but the router didn't ARP for it, the switch must physically flood the MAC frame out of all ports.
* **Solution:** Increase the Max Ageing Time on the switches or force hosts to send frequent periodic broadcast frames.

### 5.4 Scenario: Unidirectional Link Failure
* **The Problem:** If the link between `R1` and `R2` breaks in only one direction, `R1` stops receiving Hello packets from the Active `R2`.
* **Result:** `R1` assumes `R2` is dead and promotes itself to Active. Both routers are now Active and both source their frames using the shared Virtual MAC. The Layer 2 Switch constantly oscillates its Filtering Database port mappings, crashing connectivity.

### 5.5 Layer 2 Resiliency Rule
HSRP **does not** protect against Layer 2 LAN faults. Network engineers must physically guarantee data-link level resiliency using STP/RSTP (which risks a 50s convergence delay) or **Link Aggregation** (the preferred method for rapid convergence).
---

## 6. Advanced Configuration & Code Traces

### 6.1 Multi-Group HSRP (mHSRP) Advanced Configuration
To achieve load sharing, you can configure multiple HSRP groups on the same interfaces so that `R1` is Active for Group 1 and Standby for Group 2, while `R2` is the reverse. Below is the exact configuration trace provided in the document:

**Router 1 (R1) Configuration:**
```cisco
R1(config)# interface ethernet 0
R1(config-if)# ip address 10.1.1.1 255.255.255.0
R1(config-if)# standby 1 ip 10.1.1.5
R1(config-if)# standby 1 priority 105
R1(config-if)# standby 1 preempt
R1(config-if)# standby 1 track Serial0
R1(config-if)# standby 2 ip 10.1.1.6
R1(config-if)# standby 2 preempt
R1(config-if)# standby 2 track Serial0
```
**

**Router 2 (R2) Configuration:**
```cisco
R2(config)# interface ethernet 0
R2(config-if)# ip address 10.1.1.2 255.255.255.0
R2(config-if)# standby 1 ip 10.1.1.5
R2(config-if)# standby 1 preempt
R2(config-if)# standby 1 track Serial0
R2(config-if)# standby 2 ip 10.1.1.6
R2(config-if)# standby 2 priority 105
R2(config-if)# standby 2 preempt
R2(config-if)# standby 2 track Serial0
```
**

---

## 7. Exhaustive Routing Table Traces

### 7.1 "Traffic Tromboning" Routing Table
When HSRP gateway selection is uncoordinated with Layer 3 routing rules, "traffic tromboning" occurs. Traffic is sent to the DG, which then realizes the best path is through *another* router on the same LAN, pushing the traffic back out. The exact routing table trace that causes this on `R1` is:

```text
C 20.1.1.0/24   20.1.1.254 (eth0)
C 30.1.1.1/30   30.1.1.1 (eth1)
S 40.1.1.0/24   20.1.1.253 (eth0)
S 0.0.0.0/0     30.1.1.2 (eth1) (default route)
```
**

* **C:** Connected network.
* **S:** Static route.
* Because the route to `40.1.1.0/24` points to `20.1.1.253` (which is R2 on the same `eth0` subnet), R1 will forward the packet to R2 and may generate an **ICMP Redirect** toward the originating host.

---

## 8. Hardware Specifics: VRRP Token Ring Functional Addresses

Unlike standard Ethernet which uses the `00-00-5E-00-01-xx` format for VRRP virtual MACs, Token Ring requires specific Functional Addresses mapped to the Virtual Router ID (VRID). 

**Exact VRID to Token Ring MAC Mappings:**
* **VRID 1:** `03-00-02-00-00-00` 
* **VRID 2:** `03-00-04-00-00-00` 
* **VRID 3:** `03-00-08-00-00-00` 
* **VRID 4:** `03-00-10-00-00-00` 
* **VRID 5:** `03-00-20-00-00-00` 
* **VRID 6:** `03-00-40-00-00-00` 
* **VRID 7:** `03-00-80-00-00-00` 
* **VRID 8:** `03-00-00-01-00-00` 
* **VRID 9:** `03-00-00-02-00-00` 
* **VRID 10:** `03-00-00-04-00-00` 
* **VRID 11:** `03-00-00-08-00-00` 

---

## 9. Document Conclusions

The document concludes with the following overarching rules regarding gateway redundancy:

* **HSRP/VRRP Reality:** They are widely used in practice because they are simple and effective. Often, a single group per VLAN is deployed, keeping in mind that outgoing traffic is typically much smaller than incoming traffic.
* **GLBP Limitations:** It remains proprietary and is not well documented.
* **Layer 2 Network Hazards:** You must be highly careful with the L2 network, specifically regarding L2 resiliency, L2 flooding, and other data-link faults. 
* **The "Track" Function:** Ultimately deemed "not effective" for true WAN load sharing or comprehensive fault protection.


