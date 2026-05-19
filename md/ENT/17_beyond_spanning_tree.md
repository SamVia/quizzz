
**Part I: Beyond Spanning Tree** 

**Types of Network Devices** 

When building network infrastructures, devices generally fall into three categories:

* 
**Standalone Switches:** * A single device that is usually not expandable.


* Typically used in small or SOHO (Small Office/Home Office) networks.


* Available in managed or non-managed varieties.




* **Stackable Switches:**
* A single device with no (or limited) hardware customization capabilities.


* Can be aggregated with other "sibling" devices to form a stack.


* Primarily used in the access part of enterprise infrastructures.


* They provide a less expensive option compared to modular chassis switches.




* **Chassis-based Switches (Modular):**
* A device made of a single physical chassis with multiple interchangeable components (e.g., mechanical chassis, power supplies, supervision linecards, data linecards).


* Heavily customizable by inserting or swapping modules to grow the switch.


* Modules themselves can be of different types but do not contain built-in power supplies.


* Primarily used in the distribution or core part of enterprise infrastructures.


* 
*Example:* Cisco Nexus 9000 family.





**Stacked Network Switches** 

A stacked network switch is a group of physical switches that have been cabled together to act as a single logical switch.

* **Key Characteristics:**
* Provides a single management and control plane.


* Creates a single configurable logical switch, allowing administrators to configure all aggregated ports from the same console.


* Utilizes a single OS image for all switches, simplifying OS upgrades.


* Provides better reliability.




* **Connection Methods:**
* 
**Backplane Stacking:** Uses specific proprietary stacking modules (usually on the back of the switch) and specific proprietary cables.


* 
**Front-plane Stacking:** Uses standard Ethernet ports and standard Ethernet cables.




* 
**Topology Options:** * **Daisy chain or bus:** Cheap, but rarely used due to poor resiliency properties.


* 
**Ring or redundant dual ring:** Offers better resiliency, but packet paths may not be optimal.


* 
**Mesh or full mesh:** Provides the highest resiliency and optimal packet paths, but is more expensive.





**Benefits of Stacking** 

* 
**Simplified Management:** Provides a logical switch view with a single management interface, eliminating the need to configure each switch individually.


* 
**Port Flexibility:** Supports a variable combination of port speeds, media types, and different switch models (e.g., mixing standard switches with PoE switches for IoT or client connections).


* 
**Link Aggregation:** Enables link aggregation between ports on different physical switches within the same stack. This increases downstream bandwidth and resiliency, simplifying the design so that multiple physical cables act as one logical link (using LAG, LACP, or EtherChannel).



**Spanning Tree Protocol (STP) in Modern Networks** 

Traditionally, access switches required many redundant links to core switches, but STP would disable direct connections between access switches to prevent loops.

* 
**Current State of STP:** By utilizing switch stacking and link aggregation, the resulting virtual topology eliminates loops entirely. As a result, physical redundant paths (both links and devices) are no longer visible from the STP point of view.


* 
**Is STP still useful?** While not strictly needed to reduce meshes into trees anymore, STP (Rapid or Multiple) is still used as a safety mechanism. Modern networks do not have built-in protection against broadcast storms caused by unplanned loops—such as a user mistakenly plugging a cable into two ports of the same switch, or incorrectly adding a SOHO switch to the network.



**Relevant Modern Protocols** 

* **Proprietary Switch Aggregation Protocols:** E.g., Cisco VSS. These are incompatible across different manufacturers and often between different product lines of the same manufacturer. They also have strict requirements (e.g., needing at least a 10Gbps connection between switches).


* 
**Link Aggregation:** Includes both standard and proprietary solutions.


* 
**STP:** Rapid or Multiple configurations to prevent unplanned user-generated loops. Protection can also be achieved via proprietary switch features.



---

**Part II: Network Topologies** 

**The Cisco 3-Layer Hierarchical Model** 

When designing infrastructure, specific device classes should be chosen per layer based on cost, speed, and upgradeability.

#### 1. 

Access Layer 

* 
**Goal:** Allow user devices (PCs, IP phones, wireless APs, printers, scanners) to connect to the enterprise network.


* **Challenges & Functions:**
* Traffic control (QoS, traffic marking).


* Security (Access Control Lists).


* Device configuration (IP addressing, usually via an automatic DHCP server integrated into the L3 default gateway).


* User identification and authentication (e.g., 802.1x or captive portals to restrict access to authorized users).


* Power over Ethernet (PoE).




* 
**Design Considerations:** Because large campuses require hundreds or thousands of access switches, cost is the most critical factor. Consequently, the access layer is typically built using pure, simple L2 stackable switches. Complex functions are either shifted to the L3 gateway, completely ignored in fixed networks, or handled by special controllers (in the case of WiFi networks with dumb APs).



#### 2. 

Distribution Layer 

* 
**Goal:** Provides connectivity between the Access and Core layers.


* 
**Functions:** If access switches are pure L2, the distribution layer handles the heavy lifting: QoS, policy-based connectivity, and security (ACLs).


* 
**Design Considerations:** Must transport data as fast as possible and easily upgrade to new technologies or user expansions. Typically utilizes chassis-based switches.



#### 3. 

Core Layer 

* 
**Goal:** Provides the fastest possible transport between distribution switches within the campus.


* 
**Functions:** Connects the campus to external (WAN/Internet) destinations, typically through dedicated routers. Does not require sophisticated algorithms (like access control), prioritizing pure speed and geographical connectivity.


* 
**Design Considerations:** Typically utilizes chassis-based switches.



### **Topology Variations**

* 
**Collapsed Core:** In smaller enterprise networks, the Distribution and Core layers can be collapsed into a single layer. In this setup, communication between distribution switches might happen through a full mesh, which optimizes paths but faces challenges with scalability and link count.


* 
**The Backbone:** A term used to describe the combined Distribution and Core layers. It is characterized as a transit area where traffic simply flows; there are no producers or consumers of traffic (users/servers) located here. Ingress traffic strictly equals egress traffic.



---

**Part III: Network Technologies** 

**Default Gateway Placement** 

* Traffic from a specific building is often grouped into a single IP network/VLAN.


* 
**Pros:** Simplifies management; administrators can easily identify a user's location (or locate a malicious actor) purely based on their IP address.


* 
**Cons:** Complicates user mobility across the campus (e.g., trying to attach a user to their home VLAN when they are physically in a different building).



**Routing Traffic into the Backbone** 

There are two primary models for handling L3 traffic entering the backbone:

**Model 1: Fixed IP Address to Distribution Switch (Most Common)** 

* 
**Mechanism:** Assigns a fixed L3 IP interface to the distribution switch.


* 
**Pros:** More traditional, making traffic flows easier to understand and predict.


* 
**Cons:** IPs belonging to specific VLANs are locked to that physical area, meaning no location transparency (users of a specific VLAN cannot be located elsewhere on campus).



**Model 2: Handling the Backbone with VLANs** 

* 
**Mechanism:** User traffic hits the VLAN Default Gateway, and then enters the backbone through a dedicated trunked VLAN.


* **Pros:** Highly flexible. "Local" VLANs can be extended across the entire campus via VLAN trunk links.


* 
**Cons:** Requires higher management overhead and is more advanced/complex.



**Backbone L3 Architecture Options** 

When configuring the L3 backbone itself, there are multiple options:

1. **Single L3 Domain Across Backbone:** The core switch operates at L2. *Warning:* This faces issues regarding OSPF adjacencies.


2. 
**Multiple Point-to-Point L3 Domains:** Highly routed approach, but requires a significantly higher number of IP routes.


3. 
**VLAN-based Backbone:** Highly flexible where all traffic is handled via VLANs spanning the campus, and all links are L2 VLAN trunks. *Warning:* This also faces the problem of OSPF adjacencies.



---

**Part IV: Conclusions** 

Network design is not an exact science, but decisions should be grounded in the following pillars:

* **CAPEX (Capital Expenditure):** The initial cost of the infrastructure. Buying simpler devices decreases costs but may complicate network operations or fail to provide required functionalities.


* 
**OPEX (Operating Expenses):** The ongoing cost of managing the infrastructure, heavily influenced by human operators, energy costs, and support needs.


* **Flexibility vs. Complexity:** Evaluate if high flexibility is truly needed. Excessive flexibility can negatively affect an operator's ability to manage the infrastructure or troubleshoot faults.


* **Simplicity is Key:** Always prefer simple solutions when possible. A simpler network is significantly easier to understand and troubleshoot when things go wrong.

