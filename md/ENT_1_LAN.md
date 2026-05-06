## Master Cheat Sheet: Introduction to Local Area Networks (LAN)

### 1. Fundamental Concepts & Definitions
*   **Definition**: A LAN is defined by the IEEE 802 standard as a communication system operating through a shared media.
*   **Purpose**: It allows independent devices to communicate together within a limited area using a high-speed and reliable communication channel.
*   **Key Characteristics**:
    *   **Shared media**: The physical communication path is shared among users.
    *   **Independent devices**: There are no privileged devices on the network.
    *   **Limited diameter**: Spans a small area, typically measured in kilometers (Km), contained within a private area or campus.
    *   **No public soil crossing**: LAN wiring does not cross public property.
    *   **High speed**: Capabilities exceed $> 100\text{ Mbps}$.
    *   **Reliability**: Provides a dependable, low-error connection.

### 2. Standardization Bodies
*   **IEEE (Institute of Electrical and Electronics Engineers)**: Responsible for protocols and physical layer standards (the IEEE 802 series).
*   **ISO (International Organization for Standardization)**: Delegated layer 1 and 2 standardizations to IEEE.
*   **ITU (International Telecommunication Union)**: Does *not* govern these LAN standards.
*   **Structured Cabling Standards**: Governed by EIA/TIA 568 and ISO/IEC 11801.

---

### 3. OSI vs. IEEE Network Models
*   **IEEE 802.1**: Handles higher layers, management, and architecture.
    *   *Part A*: Overview and Architecture.
    *   *Part B*: Addressing Internetworking and Network Management.
    *   *Part D*: MAC Bridges.
*   **Layer 2 (Data Link)**: Responsible for the reliable transmission of frames on a single logical link. Interface to L2 is a set of frames, interface to L1 is a stream of bytes. Split into two sublayers:
    *   **802.2 Logical Link Control (LLC)**: Common across all LAN technologies and defines the interface toward Layer 3.
    *   **Media Access Control (MAC)**: Specific to each technology (e.g., 802.3 Ethernet, 802.11 WiFi) and arbitrates access to the shared physical medium.
*   **Layer 1 (Physical)**: Responsible for the transmission of binary sequences on the communication channel (sending a stream of bytes).
    *   Specifies voltage for $0/1$ symbols, type of modulation, and connectors.
    *   Specifies physical link characteristics like type, size, and impedance.
    *   Examples include Ethernet (IEEE 802.3), WiFi (IEEE 802.11), Bluetooth (IEEE 802.15.1), and ZigBee (IEEE 802.15.4), which also specify the data-link layers.
    *   At this level, whether the physical link between two devices is point-to-point or broadcast is not a primary concern.

---

### 4. Addressing and Filtering Architecture
*   **Address Overlaps**: Addressing exists at multiple layers: Applications (ports), Transport (TCP/UDP), Network (IP), LLC, and MAC.

#### MAC Address Structure
*   **Size & Uniqueness**: Addresses are 6 bytes (48 bits) long, written as 6 hexadecimal numbers, and must be unique within the LAN (not globally).
*   **Components**: Divided into two 3-byte portions:
    *   **OUI (Organizationally Unique Identifier) / Vendor Code**: Assigned by IEEE. Can be used to identify device vendors in databases (e.g., a network sniffer).
    *   **NIC-specific ID**: A progressive number assigned by the hardware manufacturer.
*   **Notable OUIs**:
    *   Cisco: `00-00-0C`
    *   Broadcom: `00-1C-23`
    *   IBM: `08-00-5A`
    *   Sun: `08-00-20`

#### Bit-Level MAC Decoding ($I/G$ and $U/L$ bits)
*   **$I/G$ Bit (First bit transmitted)**:
    *   $0$: Individual (Unicast, assigned to a single station).
    *   $1$: Group (Multicast or Broadcast).
*   **$U/L$ Bit (Second bit transmitted)**:
    *   $0$: Universal (Globally unique, OUI enforced, no duplication exists).
    *   $1$: Local (Locally administered).
*   **Byte Ordering Caution**: IEEE 802.3 and 802.11 transmit the least significant bits of the first byte first. IEEE 802.5 transmits the most significant bits of the first byte first.

#### Address Types & Usage
*   **Unicast**: Individual station routing. Source MAC addresses are always unicast.
*   **Multicast / Broadcast**: Used heavily for service discovery/solicitation (asking for a service) and advertisement (broadcasting capabilities to other stations).
*   **Broadcast Address**: Strictly represented as `FF-FF-FF-FF-FF-FF`.

#### NIC Address Memory & Filtering
*   Network Interface Cards (NICs) can have multiple MAC addresses dynamically configured at run-time.
*   A ROM keeps the "global" universal address, while volatile memory stores dynamically assigned bindings.
*   **Hardware Filtering Rules**:
    *   *Broadcast*: Always forwarded to the Operating System (OS).
    *   *Unicast*: Forwarded only if the destination matches the hardware MAC or another address loaded into the NIC's volatile memory.
    *   *Multicast*: Forwarded only if the address is registered in the proper memory area.
*   **Promiscuous Mode**: Disables all NIC hardware filtering, forcing all packets to be forwarded to the OS. This is considered mostly useless on modern switched networks.

---

### 5. Error Control: Frame Check Sequence (FCS)
*   **Mechanism**: Uses a CRC algorithm calculated across the MAC headers and the LLC PDU.
*   **Receiver Action**: The receiver performs the same calculation; if the resulting FCS does not match, the frame is discarded.
*   **Connectionless Limitation**: The MAC layer is connectionless, so it cannot inform the sender that a transmission failed.
*   **Recovery**: Collisions on Ethernet trigger automatic sender retransmissions; otherwise, recovery is handled by upper-layer protocols (e.g., TCP detecting a missing stream packet).

---

### 6. Frame Formats: Ethernet DIX vs. IEEE 802
*   **Frame Boundaries**: Valid LAN frame lengths span from 64 to 1518 bytes.
*   **Ethernet DIX (Original)**: Created before the IEEE standard, utilizing a 2-byte "Ethertype" field to handle protocol demultiplexing.
    *   Format: Preamble (7 bytes) | SFD (1) | MAC Dest. (6) | MAC Source (6) | Ethertype (2) | Data (46 - 1500) | FCS (4) | IFG.
*   **IEEE 802 Frame**: Replaced the Ethertype field with a 2-byte "Length" field, requiring LLC (native) or SNAP headers for protocol demultiplexing.
    *   Format: Preamble | SFD | MAC Dest. | MAC Source | Length | LLC + SNAP | Data | Pad (0-43) | FCS | IFG.
*   **Identification Logic (Length vs Type)**:
    *   If the 2-byte field is $\ge 1536$ ($0\text{x}0600$), it is an Ethernet DIX Ethertype.
    *   If the 2-byte field is $\le 1500$, it is an IEEE Length field.
*   **OS Network Stack Normalization**: Because Ethernet systems mix both legacy DIX and IEEE 802 formats, Operating Systems execute a "data link layer normalization" at the driver level, transforming incoming frames into a single equivalent format (usually the original Ethernet DIX format) to simplify processing for the OS network stack.

#### Subnetwork Access Protocol (SNAP)
*   **Why it exists**: The standard LLC SAP field is only 8 bits, which provides insufficient values to encompass all necessary protocols.
*   **Structure**: 
    *   Both SSAP and DSAP fields are set to $0\text{x}AA$.
    *   Requires a 5-byte Protocol Identifier appended after the LLC header.
*   **Protocol Identifier Breakdown**:
    *   *OUI (3 bytes)*: Identifies the organization that defined the protocol.
    *   *Protocol Type (2 bytes)*: If the OUI is set to $00-00-00$, this value is simply the legacy Ethernet DIX Ethertype value (e.g., $0\text{x}0800$ for IP, $0\text{x}0806$ for ARP).
*   **Usage**: SNAP is utilized in WiFi networks and also in Ethernet for specific L3 protocols.

---

### 7. Practical Exercises
*(Note: There are no specific scenarios, math problems, or exam exercises provided in the source text to solve.)*

### Additional Granular Definitions & Notes

**Physical vs. Logical Links**
*   **Link (Physical Layer)**: Defined strictly as the physical medium between two devices. At this level, the system does not care whether the link is point-to-point or broadcast.
*   **Logical Link (Data-Link Layer)**: Usually a physical link, but it can be a mixture of different physical links provided that the entire system remains a shared communication medium (e.g., using bridges).

**Data Terminology Distinctions**
*   **Frame vs. Packet**: A **"frame"** refers specifically to the data at the data-link level (e.g., containing no synchronization bits), whereas a **"packet"** refers to the data at Layer 3 (the Network layer).
*   **End of Frame**: In a standard typical LAN frame, an "End of Frame" marker may actually not be present if another mechanism is available to define where the frame ends.

**Multicast/Broadcast Functions**
*   **Solicitation**: Specifically occurs when a station needs to perform a service discovery; it sends a multicast/broadcast packet, and the station in charge of that service answers the question.
*   **Advertisement**: Specifically occurs when a station that already provides a service advertises its capabilities to all other stations through a multicast or broadcast packet.