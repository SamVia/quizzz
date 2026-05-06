## Advanced Features on Ethernet Networks: Master Cheat Sheet

### **1. Autonegotiation**

#### **Overview and Capabilities**
*   **Definition**: Autonegotiation is a plug-and-play oriented feature that allows connected devices to choose the best possible mode of operation.
*   **Negotiation Parameters**:
    *   **Speed**: Can be negotiated only over copper cables.
    *   **Duplex Mode**: Half or full duplex can be negotiated over both copper and fiber optic cables.

#### **Negotiation Sequence Hierarchy**
When negotiating, devices will attempt to connect using the highest possible performance setting from the following sequence (from highest to lowest priority):
1.  1 Gb/s full-duplex
2.  1 Gb/s half-duplex
3.  100 Mb/s full-duplex
4.  100 Mb/s half-duplex
5.  10 Mb/s full-duplex
6.  10 Mb/s half-duplex

#### **Edge Cases and Hardware Rules**
*   **Operational Requirement**: Autonegotiation is only possible if the host is connected to another host, a bridge, or a switch.
*   **Hub Limitations**: Hubs operate at a fixed speed and lack the ability to negotiate.
    *   **Rule**: If the negotiating station does not receive a response from the other party during the procedure, it assumes it is connected to a hub.
*   **Configuration Errors (Example Scenario)**:
    *   If one side is manually fixed to **100Mbps Full Duplex**, it will not send negotiation messages.
    *   The other party, receiving no messages, assumes it is connected to a hub and configures its interface to **100Mbps Half Duplex**.
    *   **Result**: This mismatch leads to unexpected errors, specifically a massive amount of false collisions on the host configured for half-duplex.

---

### **2. Ethernet Max Frame Specifications**

#### **Historical and Standard Limits**
*   **Original Specifications**: The theoretical maximum Ethernet frame size is strictly **1518 bytes**.
*   **MTU Legacy**: The standard Maximum Transmission Unit (MTU) remains **1500 bytes** strictly for historical reasons. 

#### **Frame Expansions and Added Headers**
Over time, the maximum frame size has been expanded to accommodate new networking features:
*   **VLAN Tagging (IEEE 802.1Q)**: Adds **4 bytes** to the frame.
*   **Provider Bridge (IEEE 802.1ad)**: Also known as **802QinQ**, adds **8 bytes** to the frame.
*   **Ethernet Frame Expansion (IEEE 802.3as)**: Proposed a new total frame size of **2000 bytes**.
    *   **Rule**: Despite the expansion, the data portion (payload) of the frame strictly remains between 46 and 1500 octets, meaning the MTU does not change from 1500 bytes.
*   **Fibre Channel over Ethernet (FCoE)**: The T11 committee adopted an MTU of **2500 bytes** specifically for FCoE frames.
*   **MPLS Frame Size Calculation**: MPLS encapsulation increases the maximum Ethernet frame size based on the number of stacked labels. The mathematical formula for the maximum frame size is:
    $1518 + (n \times 4)$ bytes
    *(Where $n$ is the exact number of stacked labels)*.

#### **Categorizing Larger Frames**
Larger frames are divided into two distinct logical categories:
1.  **Larger frames due to added headers**: These have no impact on the hosts and are required by new Ethernet extensions.
2.  **Larger frames to transport more data**: These actively impact the MTU and are desirable for network efficiency, but present backward-compatibility issues. 
    *   *Note*: The maximum frame size can be enlarged without causing significant latency impacts because Gigabit Ethernet (GbE) utilizes "frame bursting".

#### **Classification of "Ethernet Giants"**
*   **Baby Giant**: Refers to frames that carry just extra headers, primarily used with MPLS, 802.1Q, 802.1ad, and 802.3AE.
*   **Mini Jumbo**: Refers to frames carrying bigger data payloads. It specifically describes an MTU size of **2500 bytes** and is synonymous with the frame size used by FCoE.
*   **Jumbo (or "Giants" / "Giant Frames")**: Refers to frames carrying much larger data payloads, often going up to **9KB**. While non-standard, they are widely supported by hardware.

---

### **3. Jumbo Frames: Deep Dive**

#### **Advantages**
*   **Reduced Header Overhead**: Less bandwidth is wasted on headers, though this is usually not considered a highly important factor in practical application.
*   **Application-Specific Payload Support**: Jumbo frames perfectly accommodate:
    *   **2500-byte** FCoE frames.
    *   **8192-byte** NFS data blocks.
    *   **8K** iSCSI blocks (which are derived from the typical TCP Window size).
*   **Reduced OS Overhead**: Decreases the amount of CPU interrupt handling required for each new packet, which provides a very significant cost saving for network-intensive servers.
*   **Legacy Network Transport**: Provides the capability to transport traffic natively from networks with larger MTUs (e.g., historically used to transport Token Ring frames across corporate backbones).

#### **Problems and Edge Cases**
*   **Latency**: Jumbo frames physically increase overall network latency.
*   **Switch Buffer Pressure**: They increase buffer pressure on network switches, which typically possess very small internal memory buffers.
*   **OS/Stack Tuning**: Most network stacks, operating systems, and internal buffer dimensions are natively tuned and optimized exclusively for 1500-byte frames.
*   **IP Level Fragmentation**: If a massive jumbo frame must be delivered to a traditional 1500-byte station, it forces fragmentation at the IP level.
*   **CRC Algorithm Redesign**: The original Ethernet CRC calculation algorithm was not mathematically robust enough to check frames of Jumbo sizes, forcing a new CRC calculation to be defined.

---

### **4. Power Over Ethernet (PoE)**

#### **Overview**
*   **Definition**: A technology allowing the delivery of electrical power alongside data directly through the Ethernet cable.
*   **Hardware Rules**: It functions exclusively over twisted-pair copper cabling; it cannot be used over fiber optic cables.
*   **Compatibility**: It is 100% backward compatible with non-PoE network stations.
*   **Use Cases**: It is highly useful for connecting devices with moderate power requirements, such as IP phones, WiFi access points, surveillance cameras, and virtual desktop terminals.
*   **Benefits**: It completely avoids the need for additional electrical cabling and power cords, and provides more raw power over longer distances than USB connections.

#### **Architecture Risks and Problems**
*   **Catastrophic Switch Failures**: A single failure of a centralized PoE switch can bring down critical infrastructure (network, phones, surveillance cameras simultaneously), causing panic.
*   **Complex Redundancy Needs**: To mitigate failure risks, networks must be designed with complex switches featuring proper redundant power supplies, increasing design and maintenance complexity.
*   **Power Consumption Limits**: PoE switches consume massive amounts of power. 
    *   *Calculation Example*: A single switch with 48 ports providing 25W each consumes 1.2 KW of power ($48 \times 25\text{W} = 1.2\text{KW}$).
    *   **Environmental Needs**: This necessitates specifically dimensioned electrical power lines and dedicated thermal cooling systems in server rooms.

#### **Hardware Standards and Specifications**
*   **IEEE 802.3af-2003 (Original PoE)**:
    *   Supplies up to **15.4 W** of DC power to each port.
    *   Requires a minimum of **44V DC** and **350mA**.
    *   *Hardware Limit*: Due to electrical dissipation within the twisted pair cable, only a maximum of **12.95 W** is assured to be physically available at the receiving powered device.
*   **IEEE 802.3at-2009 (PoE+ / PoE plus)**:
    *   An updated standard providing up to **25.5 W** of power to connected devices.
*   **Proprietary High-Power Standards**:
    *   There are products explicitly designed to provide even more power, such as **Cisco Universal Power Over Ethernet (UPOE)**.
    *   UPOE can supply **51W** or **60W** of power over a single cable.
    *   *Architectural Detail*: It achieves this massive power delivery by utilizing all four pairs of wires inside a Category 5 (Cat.5) Ethernet cable.