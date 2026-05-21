Here is the exhaustive master cheat sheet based entirely on the provided lecture materials.

## Types of Network Devices

Network devices are categorized into three primary architectures based on their expandability, components, and use cases:

* **Standalone Switches:** These are single devices that are usually not expandable. They are mostly utilized in small or SOHO (Small Office/Home Office) networks and can be either managed or non-managed.


* **Stackable Switches:** These are single physical devices that typically have limited or no hardware customization capabilities. However, they can be aggregated with other "sibling" devices to form a stack. They are primarily used in the access layer of enterprise infrastructures. They provide a less expensive option compared to modular chassis switches.


* **Chassis-based Switches (Modular):** These are composed of multiple interchangeable physical components housed in a mechanical chassis, such as power suppliers, supervision linecards, and data linecards. This design makes them heavily customizable. The modules inserted into the slots do not have their own power supplies. These are typically used in the distribution and core parts of enterprise infrastructures. An example is the Cisco Nexus 9000 family.



---

## Stacked Network Switches & Link Aggregation

A stacked network switch represents a group of physical switches that have been cabled together and grouped to operate as a single logical switch.

### Characteristics and Benefits

* **Unified Management:** Stacking provides a single management and control plane. This simplifies operational tasks, as all ports of the aggregated switch can be configured from a single console, eliminating the need to manage each switch individually.


* **Simple Upgrades:** The stack runs a single OS image across all physical switches, simplifying operating system upgrades.


* **Port Flexibility:** Stacks support a variable combination of port speeds, media types, and varying switch models with different capabilities (e.g., mixing standard switches with PoE-enabled switches for connecting clients or IoT devices).


* **Resiliency & Bandwidth:** Link aggregation is supported between ports of different physical switches within the same stack. This approach treats multiple cross-switch cables as a single logical link (utilizing protocols like LAG, LACP, or EtherChannel), which drastically improves downstream link bandwidth and network resiliency.



### Stacking Topologies and Connections

Stacks are typically built using specific cables connecting switches in predefined topologies:

* **Backplane Stacking:** Relies on specific, proprietary stacking modules usually located on the back of the switch and uses specific proprietary cables.


* **Front-plane Stacking:** Uses standard Ethernet ports and standard Ethernet cables to interconnect the stack.


* **Topology Options:** * **Daisy chain or bus:** A cheap option, but rarely used due to poor resiliency.


* **Ring or redundant dual ring:** Offers better resiliency, though packet paths may not be perfectly optimal.


* **Mesh or full mesh:** Provides the highest resiliency and optimal packet paths, but is more expensive.





---

## Beyond Spanning Tree Protocol (STP)

### Virtual Topology vs. Physical Topology

* In traditional access-to-core setups, connections require many links to guarantee redundancy (e.g., two links per access switch).


* Direct connections between access switches are traditionally useless because STP disables them to prevent loops.


* When using switch and link aggregation, multiple physical links are combined into one logical link (Link Aggregation).


* This results in a cleaner, more efficient virtual topology from the perspective of STP, where no redundant paths or loops are visible.



### The Modern Role of STP

* STP's original design was to prevent loops in L2 networks, as loops break Backward Learning algorithms used by switches.


* Due to the intelligent use of switch and link aggregation, modern virtual topologies inherently do not have loops, making STP logically unnecessary for routing redundant paths.


* **Crucial Edge Case:** STP (Rapid or Multiple) is still actively used as a protection mechanism against *unplanned* loops (e.g., a user mistakenly connecting two ports of the same switch with a cable). Current networks lack built-in protection against broadcast storms generated outside the controlled infrastructure (like a physical loop on a SOHO switch added by an end-user). Protection features are mostly achieved by turning on proprietary switch features.



### Relevant Network Protocols

1. **Proprietary Protocols for Switch Aggregation:** Examples include Cisco VSS. These are often incompatible between different manufacturers and sometimes even within different product lines from the same manufacturer. They may have strict hardware requirements, like needing a minimum 10Gbps connection between switches.


2. **Link Aggregation:** Includes both standard and proprietary protocols.


3. **STP (Rapid or Multiple):** Retained purely for emergency loop protection.



---

## Cisco's 3-Layer Hierarchical Network Model

The standard enterprise network follows a 3-layer hierarchical model: **Access Layer, Distribution Layer, and Core Layer**.

### 1. Access Layer

* **Goal:** To allow user devices (PCs, IP phones, wireless access points, printers, scanners) to connect to the enterprise network.


* **Challenges & Functions:**
* Traffic control (e.g., QoS, traffic marking).


* Security (e.g., access control lists).


* Device configuration (e.g., IP addressing, often achieved via local/remote DHCP server integrated into the L3 default gateway).


* User identification and authentication (e.g., 802.1x, captive portals).


* Power over Ethernet (PoE).




* **Design & Hardware Specifics:**
* Because large campuses require hundreds or thousands of access switches, **cost** is the most critical consideration. (Example: Politecnico di Torino has ~30,000 physical sockets, equaling 800-1000 48-port switches ).


* To keep expenses low, the access layer is often built using pure L2 stackable switches with very simple functions. Advanced features are often pushed up to the L3 device.


* Fixed networks frequently omit access-level controls (like user identification) entirely.


* **Wireless Exception:** In WiFi setups, the access hardware consists of "dumb" access points that forward all traffic to specialized controllers where additional features (like authentication) are handled.





### 2. Distribution Layer

* **Goal:** Provides connectivity bridging the access and core layers.


* **Functions:** If access switches are pure L2, the distribution layer assumes responsibilities for QoS, policy-based connectivity, and security (ACLs).



### 3. Core Layer

* **Goal:** Provides high-speed transport between distribution switches across the enterprise campus.


* **Functions:** Connects the campus to external (WAN) destinations, usually through dedicated routers.



### The Network Backbone

* The **Backbone** is the combination of the Distribution and Core layers.


* These layers do not host producers or consumers of traffic (users or servers). Therefore, the total ingress traffic equals the total egress traffic.


* The primary requirement for distribution and core chassis-based switches is to transport data as quickly as possible and scale for future technologies or campus expansion. They generally do not require sophisticated algorithmic processing like access control.



### Collapsed Core Architecture

* In "small" enterprise networks, the Distribution and Core layers can be merged into a "Collapsed Core Layer".


* If distribution switches communicate via a full mesh in a collapsed core, it optimizes packet paths but introduces well-known drawbacks regarding scalability and the high number of physical links required.



---

## Network Technologies, VLANs & IP Routing

### Locating the Default Gateway (DG)

* Traffic from a specific building is typically grouped into a single IP network/VLAN.


* **Pros:** Simplifies management; administrators can easily trace a user's physical location (or malicious activity) based on their IP address.


* **Cons:** Complicates user mobility. Moving a user to a different campus location while keeping them on their original building's VLAN is difficult.



### Routing Traffic into the Backbone

There are two primary models for how traffic flows from the VLANs into the backbone:

**Model 1: Fixed IP Address to Distribution Switch (Most Common)** 

* **How it works:** A Layer 3 interface with an IP address and network is assigned directly to the backbone link.


* **Characteristics:** Traditional, easy to understand, and predict.


* **Limitations:** IPs belonging to specific VLANs (e.g., VLAN A and B) are strictly localized. It does **not** support location transparency, meaning users of VLAN A cannot physically relocate to a different part of the campus and retain their network status.



**Model 2: VLAN-Based Backbone (Highly Flexible)** 

* **How it works:** All traffic is managed via VLANs spanning the entire campus, including dedicated VLANs specifically for the backbone. The links used are L2 VLAN trunks. User traffic hits the VLAN Default Gateway, then enters the backbone via a separate transport VLAN (e.g., VLAN C).


* **Characteristics:** Highly flexible and advanced, allowing "local" VLANs to extend campus-wide.


* **Limitations:** Generates higher management overhead.


* **Edge Case Warning:** If operating a single L3 domain across the backbone with the core switch operating at L2, administrators must account for potential issues with **OSPF adjacencies**. Alternatively, using multiple point-to-point L3 domains requires maintaining a significantly higher number of IP routes.



---

## Conclusions & Network Design Pillars

Network design is not an exact science, but architects must balance several critical pillars:

1. **CAPEX (Capital Expenditure):** The raw cost of the infrastructure. Utilizing simpler devices decreases upfront costs, but may lack required functionalities and complicate operations.


2. **OPEX (Operating Expenditure):** The ongoing cost to manage the network. This includes human operators, energy costs, and support.


3. **Flexibility vs. Complexity:** Designers must ask if maximum flexibility is truly needed. High flexibility can severely negatively impact a network operator's ability to manage the infrastructure or troubleshoot faults.


4. **Golden Rule:** Prefer simple solutions whenever possible. Simpler architectures make it drastically easier to understand what is going wrong during a troubleshooting scenario.



---
L3 Backbone Connectivity Options: When discussing the backbone based on L3 connectivity, there are two distinct sub-options:

Single L3 domain across the backbone: (Core switch operates at L2). This triggers the previously mentioned problem with OSPF adjacencies.

Multiple point-to-point L3 domains: This avoids the OSPF adjacency issue but explicitly "requires a higher number of IP routes" to be maintained.