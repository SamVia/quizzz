## **Master Cheat Sheet: Designing L2/L3 Networks**

### **1. Fundamental Packet Delivery Principles**

#### **How Hosts Deliver Packets**
* Hosts rely on simple routing tables, typically containing just two routes: one for the directly connected IP network and a default route for all other destinations.
* **Encapsulation Process:**
    * **IP.src:** Originating host.
    * **IP.dst:** The final target host.
    * **MAC.src:** Originating host.
    * **MAC.dst:** The target host on the LAN. This will be either the Default Gateway (if indirect addressing to another IP network) or the final target host (if direct addressing on the same IP network).

#### **How Routers Deliver Packets**
* Routers **never** change the IP addresses of the packets in transit.
* The router selects the most appropriate entry in its routing table to reach the destination.
* **Encapsulation Process:**
    * **MAC.src:** The originating router interface.
    * **MAC.dst:** The target device on the LAN where the frame is forwarded (either the final target host if directly reachable, or the next-hop router).

---

### **2. Architectural Configurations & Network Design**

#### **Configuration 1: Operating at L3 vs. L2**

**Option A: Upper Interfaces Operating at L3**
* Each interface is associated with a specific L3 network.
* IP networks are statically tied to specific floor switches (SW-x), meaning an IP network (e.g., 10.1.1.0/24) cannot be distributed across multiple switches.
* VLANs are only valid within each floor switch, making this inflexible (e.g., cannot support a company-wide "engineering VLAN").
* Lower interfaces at L3 function properly.
* **STP Implications:** 3 separate Spanning Tree Protocol (STP) instances are present. Bridge Priorities on Multilayer switches (ML-x) are not useful here. STP remains useful only to prevent loops on the switch itself.

**Option B: Upper Interfaces Operating at L2 (The Superior Option)**
* IP addresses are tied to the internal VLAN interface of the Multilayer switch.
* VLANs and IP networks can be distributed across *all* floor switches.
* Utilizes a single instance of STP.
* Requires configuring 3 separate Hot Standby Router Protocol (HSRP) groups.
* All links between switches operate in trunk mode.

**Configuration Summary for ML-1 & ML-2 (L2 setup):**
```text
ML-1 Configuration:
- VLAN 1 address: 10.1.1.253/24 
- VLAN 2 address: 10.1.2.253/24 
- VLAN 3 address: 10.1.3.253/24 
- HSRP Group 1 (active): 10.1.1.254 
- HSRP Group 2 (active): 10.1.2.254 
- HSRP Group 3 (active): 10.1.3.254 

ML-2 Configuration:
- VLAN 1 address: 10.1.1.252/24 
- VLAN 2 address: 10.1.2.252/24 
- VLAN 3 address: 10.1.3.252/24 
- HSRP Group 1 (standby): 10.1.1.254 
- HSRP Group 2 (standby): 10.1.2.254 
- HSRP Group 3 (standby): 10.1.3.254 
```
* **The Problem with Config 1 (L2):** Additional L3 traffic is pushed into the LAN. If ML-1 is the active router but ML-2 is the best path to a destination, ML-1 forwards traffic across the LAN to ML-2. Furthermore, routing protocols (like OSPF) propagate campus IP networks to the WAN and receive reachable IP networks to decide the best egress, creating unwanted L3 protocol noise in host VLANs. 

#### **Configuration 2: Adding a Dedicated L3 Link**
* A dedicated L3 link is added directly between ML-1 and ML-2.
* **Purpose:** Allows routing protocols to exchange messages without impacting hosts, and transports L3 packets to the best exit gateway.
* While a standard data VLAN *could* theoretically be used for this routing traffic, it is highly discouraged as local hosts would receive routing messages and could potentially intercept inter-router traffic.
* OSPF is enabled on the L3 inter-router link (eth3) and the WAN link (eth4).
* **The Problem with Config 2:** L2 and L3 operate entirely independently.
    * **Fault 1 (L2 Fault):** If an ML-1 link to a floor switch fails, the path becomes un-optimized. The dedicated L3 link between ML-1 and ML-2 does not participate in STP, meaning it cannot "re-protect" the L2 network.
    * **Fault 2 (L3 Fault):** If the dedicated link between ML-1 and ML-2 fails, VLANs must be reconfigured to allow pure L3 traffic and routing protocols to traverse the remaining L2 switch links. If routers detect two equivalent paths (e.g., both 1Gbps), they will use them both in load sharing instead of purely failing over.
* **Core Rule:** A fault in L2 cannot be automatically re-protected by L3, and an L3 fault cannot be automatically re-protected by L2.

#### **Configuration 3: All Links at L2 + Inter-Router VLAN**
* **Design:** Configure all LAN links at L2 so they can re-protect each other.
* Requires a Single Spanning Tree and 4 VLANs: 3 for data (with HSRP) and 1 dedicated specifically to L3 data (OSPF + traffic to the best exit gateway).
* **The Problem with Config 3:** There is no guarantee that inter-router traffic (VLAN 4) will actually cross the direct physical link between ML-1 and ML-2 due to STP configurations. If a fault occurs in the campus network, the routing table remains completely unchanged because routes are tied to "VLAN" interfaces, not physical interfaces.

#### **Configuration 4: The "Definitive" Network**
* All campus links (except WAN) are L2.
* Two redundant links exist directly between the multilayer switches.
* Single Spanning Tree, 4 VLANs (3 data/HSRP, 1 L3/OSPF).
* **Final Improvement:** Bundle the links between ML-1 and ML-2 using Link Aggregation.
* **Benefits:** This provides more bandwidth and prevents an STP transient recalculation if one of the physical links fails.

#### **Configuration 5: Per-VLAN STP (PVST)**
* Different VLANs have different Root Bridges and HSRP Active gateways.
* This allows for load balancing across the physical infrastructure.

---

### **3. Practical Exercises & Edge Cases: Tracing Frames**

To trace frames in an L2-L3 network: 
1. Explode the multilayer switch logically to see L2 vs L3 links. 
2. Run STP on the L2 network to find port states. 
3. Determine the Active HSRP router within each VLAN. 
4. Determine the L3 packet path based on routing tables.

**Example 1: Forwarding strictly at L2**
* **Scenario:** Routing happens via L3 links which have no STP.
* **Rule:** When forwarding at L2, *only* the physical topology (the direct outcome of the Spanning Tree Protocol) dictates the path.

**Example 2: Forwarding at L3**
* **Scenario:** Traffic crosses VLAN boundaries.
* **Rule:** When forwarding at L3, you must account for *both* the STP physical topology AND the location of the HSRP Active Gateway.

**Example 3: Forwarding at L3 (Root Bridge != Active Gateway)**
* **Rule:** Network paths become severely un-optimized if the STP Root Bridge does not overlap with the HSRP Active Gateway.

**Example 4: Forwarding at L3 (Multiple Active Gateways)**
* **Scenario:** ML-1 is active for 10.1.1.0/24, ML-2 is active for 10.1.3.0/24.
* **Rule:** Multiple HSRP Active Gateways for different groups can result in completely asymmetric routing paths.
* **HSRP Router Mechanics:** An active HSRP router answers ARP requests using the Virtual MAC (VMAC). However, HSRP does *not* influence how that router forwards L3 packets. A standby router still uses the standard longest prefix matching algorithm and sends IP traffic using its actual physical MAC address.

**Examples 5 & 6: Fault Between ML-1 and ML-2**
* **Rule:** L3 forwarding will simply take the best path available on the L2 network resulting from STP.
* **Rule:** The L3 path (e.g., a host reaching its Default Gateway) is entirely independent of where the root bridge is physically located. Packets may physically travel to ML-2 and then bounce back to the user even if ML-1 is the root bridge.

---

### **4. Standard Reference Routing Table (Config 2 / Config 4)**

Here is the exact routing and interface configuration reference for a "Definitive" L2/L3 topology:

```text
Interfaces:
eth0: trunk 
eth1: trunk 
eth2: trunk 
eth3: 30.3.3.1/30 (toward ML-2) 
eth4: 20.2.2.1/30 (toward WAN) 
vlan1: 10.1.1.253/24, HSRP active 10.1.1.254 
vlan2: 10.1.2.253/24, HSRP active 10.1.2.254 
vlan3: 10.1.3.253/24, HSRP active 10.1.2.254 

Routing table:
C  10.1.1.0/24  10.1.1.253 (vlan1) 
C  10.1.2.0/24  10.1.2.253 (vlan2) 
C  10.1.3.0/24  10.1.3.253 (vlan3) 
C  30.3.3.0/30    30.3.3.1 (eth3, to ML2) 
C  20.2.2.0/30    20.2.2.1 (eth4, to WAN) 
O   network S1    30.3.3.2 (eth3, to ML2) 
(plus other routes learned through OSPF, next hop either 20.2.2.2 or 30.3.3.2) 

Routing protocols:
OSPF enabled on eth3 and eth4 
```

### **5. Concluding Architectural Takeaways**
* L2-L3 Multilayer switches are mainstream and offer extreme flexibility in defining where traffic is handled. 
* Whether a port acts as L2 or L3 is purely a matter of software configuration.
* **Standard Enterprise Deployment:** Most campus access networks are entirely L2 (utilizing VLANs). Pure L3 is reserved for the edges (servers, data centers) and for WAN connections. Multilayer switching is placed in the core to drastically speed up inter-VLAN routing.
* **The Golden Rule:** You must engineer the L3 network by deeply analyzing and considering the actual underlying L2 STP topology.
