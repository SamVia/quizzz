# Master Cheat Sheet: Link Layer Discovery Protocol (LLDP)

## 1. Core Problem & Objective
* **The Problem:** There is a need to define a standard protocol to assist management tasks, such as discovering network topology or identifying the direct neighbors of a network device. 
* **Practical Example:** Determining exactly which device and port is connected to a local port (e.g., finding out that local port `GigaEthernet 1/3` is connected to switch `SW2` on port `GigaEthernet 2/1`, manufactured by Cisco, running software image `IOS Release 15.2(2)SE`).
* **Proprietary Predecessors:** Prior to LLDP, many proprietary solutions were used, such as Cisco Discovery Protocol (CDP) and Foundry Discovery Protocol.

## 2. LLDP Overview
* **Definition:** LLDP is a standard, vendor-neutral link-layer protocol. 
* **Standardization:** It is standardized under **IEEE 802.1AB**.
* **Purpose:** It allows networked devices to advertise their identity, capabilities, and configuration to their immediate neighbors.
* **Scope:** While initially designed for network devices, it is applicable to any networked endpoint, including IP phones, servers, and desktop PCs.
* **Design Philosophy:**
    * Low complexity leading to higher interoperability potential.
    * Practical for both cost-restrained endpoints and feature-rich devices.
    * Simple, leveraged design lowers development costs and increases the likelihood of vendor adoption.
* **Adoption:** It sees widespread industry adoption across most networks. Networks typically use either LLDP or a proprietary counterpart like Cisco CDP.

## 3. Advertised Information
Devices use LLDP to share an extensible set of information. Common information fields include:
* System name and description.
* Port name and description.
* VLAN name.
* IP management address.
* System capabilities (e.g., indicating if it acts as a switch, router, IP phone, wireless AP, etc.).
* MAC/PHY information.
* MDI power details.
* Link aggregation status.

## 4. Protocol Mechanics & Stateless Operation
* **Transmission:** LLDP is a simple one-way protocol that utilizes periodic transmissions. 
* **Stateless Nature:** The protocol acts entirely as a one-way advertisement without requests or acknowledgments. The protocol itself is stateless, though a central management entity is required to maintain the state and act on the peer information.
* **Update Frequency:** LLDP updates are strictly limited to a maximum of **1 per second**.
* **Triggers:** Anytime a local value changes, LLDP automatically sends a frame.
* **Constraints & Propagation:** LLDP frames are **not forwarded**; they are strictly constrained to a single point-to-point link. 
* **Performance:** The lack of state and constrained updates dramatically simplifies implementation and bounds performance requirements to ensure scalability.

## 5. Network Topology Discovery Strategy
* **Data Storage:** The receiver stores incoming LLDP information in a local neighbor database.
* **Ageing:** Time-to-Live (TTL) information is sent in the frames for ageing purposes. The receiver routinely ages out its Management Information Base (MIB) database to ensure only valid, current network data is available.
* **Accessibility:** The neighbor database is accessible via SNMP MIB.
* **Topology Limitation:** LLDP alone only provides a partial view of the topology (i.e., immediate neighbors only). It cannot natively discover the entire network topology.
* **Full Topology Discovery:** To discover the entire topology of an LLDP-enabled network, a management application must crawl the hosts and query their local MIB databases (typically via SNMP). 

## 6. Architecture: LLDP Frame & LLDPDU Format
LLDP utilizes a specific Ethernet frame structure containing an LLDP Data Unit (LLDPDU).

### IEEE 802.3 LLDP Frame Format
* **Destination Address (DA):** 6 octets. Set to the LLDP Multicast address `01-80-C2-00-00-0E`. *(Note: This is the same address used for Spanning Tree, except for the last octet)*.
* **Source Address (SA):** 6 octets. The sender's MAC address.
* **LLDP Ethertype:** 2 octets. Value is set to `88-CC`.
* **Data + Pad (LLDPDU):** Up to 1500 octets.
* **Frame Check Sequence (FCS):** 4 octets.

### LLDPDU Architecture
The LLDPDU consists of formatted TLVs (Type, Length, Value) containing useful attributes. There are mandatory (**M**) TLVs that must be present in all LLDPDUs, followed by optional TLVs.

**Mandatory LLDPDU Structure Order:**
1.  **Chassis ID TLV (M)**: Globally unique system identification.
2.  **Port ID TLV (M)**: Globally unique port identification.
3.  **Time To Live TLV (M)**: Ageing information.
4.  **Optional TLVs**: Organizational extensions, capabilities, names, etc..
5.  **End Of LLDPDU TLV (M)**.

## 7. Architecture: TLV Extensibility & Format
LLDP is highly and easily extensible by allowing the definition of organizational extensions via TLVs.

### Current Main Organizational Extensions
1.  **IEEE 802.1:** Defines Port VLAN, Port & Protocol VLANs, VLAN Name, and Protocol Entity.
2.  **IEEE 802.3:** Defines MAC/PHY configuration, PoE (Power over Ethernet) Power, Link Aggregation, and Maximum Frame Size.
3.  **TIA - IP Telephony Infrastructure (LLDP-MED):** Defines VLAN & QoS auto-config, Physical Location Discovery, Detailed Inventory, and PoE Power.

### Extension TLV Header & Information String Specification
The structural breakdown of an organizational extension TLV is as follows:

* **TLV Header:**
    * **Extension TLV type:** 7 bits. Set to `111 1111`.
    * **TLV string length:** 9 bits.
* **TLV Information String:** (Ranges from 4 to 511 octets total).
    * **Organizationally unique identifier (OUI):** 3 octets.
    * **Group-defined TLV subtype:** 1 octet.
    * **Group-defined information string:** Bounded length calculated as $0 \le n \le 507$ octets.
