## Interconnecting Devices for Local Area Networks

### 1. Overview of LAN Interconnecting Devices
*   **Layer 1 (L1) Devices**: Include Repeaters and Hubs. They separate physical domains but maintain the same collision domain.
*   **Layer 2 (L2) Devices**: Include Bridges and Switches. They separate collision domains but maintain the same broadcast domain.
*   **Layer 3 (L3) Devices**: Include Routers and L3 Switches. They separate broadcast domains, are not transparent to MAC addresses, and are not specific solely to LANs.

---

### 2. Physical Layer Devices (Layer 1)

#### Repeaters
*   **Function**: Provide interconnection strictly at the physical layer by receiving and propagating a sequence of bits.
*   **Use Cases**: 
    *   Interconnecting networks that use the same Medium Access Control (MAC).
    *   Ensuring all connected ports operate at the exact same speed (e.g., Ethernet 10Mbps fiber to copper).
    *   Recovering signal degradation over long cables to allow for larger physical distances.

#### Multiport Repeaters: Hubs
*   **Definition**: A repeater equipped with more than two ports.
*   **Cabling Implementation**: Required for twisted pair and fiber optic cabling to form a hub-and-spoke topology.
*   **Evolution**: Became widely common with the adoption of structured cabling, offering more flexibility and robustness than older coaxial cable networks.
*   **Legacy**: While no longer used today, they permanently transformed bus-based LANs into hub-and-spoke topologies, facilitating the easy, drop-in replacement of "old" hubs with "new" switches on Ethernet networks.
*   **Medium Sharing**: Under a hub, the transmission is "physically" shared; the actual electromagnetic signal propagates across the entire LAN.

---

### 3. Data-Link Layer Devices (Layer 2)

#### Bridges
*   **Origins**: Introduced by Digital Equipment Corporation (DEC) in 1983 (specifically the LANBridge 100).
*   **Architecture**: Originally pure software-based with only 2 ports (mainly due to economic reasons).
*   **Function**: Provide interconnection at the data-link layer, allowing connections across different MACs (e.g., Ethernet to WiFi, Ethernet to Fast Ethernet) because they handle different medium access mechanisms and framing.
*   **Primary Objectives**:
    *   Interconnecting different LAN technologies (though often impossible in practice due to max frame size constraints since L2 cannot fragment frames).
    *   Extending the total LAN diameter, highly useful for FastEthernet and above (which has a 200m limit).
    *   Solving collision domain issues and significantly increasing network speed.
*   **Operation (Store and Forward)**:
    1.  **Store**: The bridge receives and fully buffers the frame.
    2.  **Modify**: Modifies the frame if converting between mediums (e.g., Ethernet to Token Ring).
    3.  **Forward**: Transmits the frame out.
*   **Layer Traversals**: When a frame crosses a bridge, the L1 portion is created entirely from scratch, the L2 (MAC) portion is regenerated (e.g., MAC conversion), and the Logical Link Control (LLC) and upper layers transit completely unchanged.
*   **Medium Sharing**: Bridges create a "logically" shared medium. The logical transmission (frames), rather than the physical signal, propagates.

---

### 4. Communication Modes & Topologies

#### Half Duplex vs. Full Duplex
*   **Half Duplex**: Receive (RX) and Transmit (TX) cannot happen simultaneously. If they do, it registers as a collision.
*   **Full Duplex**: A Network Interface Card (NIC) can send and receive data simultaneously.
*   **Enablers of Full Duplex**: Massive adoption of hub-and-spoke topologies, modern cables utilizing dedicated wires for TX and RX, and bridges operating in "store and forward" (which stops collisions from propagating). Full duplex was standardized as part of 802.3x for Fast Ethernet.

#### Advantages of Full Duplex
*   **Bandwidth**: Theoretically doubles throughput, though in practice clients saturate downlinks and servers saturate uplinks. Very beneficial for backbone bridges which have symmetrical traffic.
*   **CSMA/CD Elimination**: CSMA/CD is no longer needed because collisions are physically impossible.
*   **Ethernet Constraints Lifted**: Removing CSMA/CD removes the minimum frame size requirement and lifts limits on maximum network size (since the collision domain is eliminated).

---

### 5. Smart Forwarding and Switches

#### Modern Switches
*   **Definition**: Multiport bridges are called "switches". They perform the exact same functions but feature a distinct hardware-based internal architecture.
*   **Logical LAN emulation**: A switch guarantees that frames are only sent to legitimate recipients rather than broadcasting physically.
*   **Traffic Segregation**: Ports belong to different collision domains, allowing switches to send and receive traffic simultaneously on different ports. Switches possess buffers to absorb bursts of data.
*   **Aggregate Bandwidth**: While the single-link bandwidth does not change, traffic segregation significantly increases the overall aggregate bandwidth of the network.

#### The Smart Forwarding Process Rules
*   **General Rule**: Receives frame, stores in buffer, analyzes destination address, forwards to correct port. The Ethernet frame puts MAC Destination before MAC Source specifically to speed up this process.
*   **Unicast**: Forwarded only on the specific port that reaches the destination (Destination MAC-based forwarding).
*   **Multicast/Broadcast**: Triggers "flooding", meaning the frame is forwarded to all ports *except* the port on which it was received. Note: Flooding is delayed forwarding, unlike a hub that repeats bits immediately.
*   **Same-Port Rule**: Switches **never** send a frame back out the exact same port it was received on.
*   **Transient State**: If a MAC address is not found in the local table, the switch behaves temporarily like a hub and duplicates the frame on all ports except the origin port via "MAC Flooding".

---

### 6. The Filtering Database (FDB)

In order for a switch/bridge to operate as "plug and play" without admin configuration, it relies on three components: a Filtering Database, Backward Learning, and the Spanning Tree Protocol.

#### FDB Structure and Rules
*   **Purpose**: A local lookup table mapping the "location" of any MAC address in the network.
*   **Table Fields**: MAC Address, Destination Port, and Age (Ageing time).
*   **Dynamic Entries**: Populated automatically by the backward learning process. Switch capacity ranges from $2 \div 64\text{ K}$ maximum entries. Old entries (zombies) are purged automatically; the default expiration time is 300 seconds.
*   **Static Entries**: Inputted manually and are not updated or overwritten by the dynamic learning process. Typically restricted to $< 1\text{ K}$ entries.
*   **Unreachable Hosts**: If a host is *not* in the DB, it is reachable because the switch will flood its frames. If a host *is* in the DB but moved, it may be unreachable for a maximum duration equal to the Aging Time.

#### Code Trace: Cisco MAC Filtering Database
Below is an exact code trace of a Cisco switch's filtering database mapping output:
```text
Cisco-switch-1> show cam dynamic
* = Static Entry. + = Permanent Entry.
# = System Entry X = Port Security Entry

Dest MAC Address      Ports   Age
00-00-86-1a-a6-44     1/1     1
00-00-c9-10-b3-0f     1/1     0
00-00-f8-31-1c-3b     1/2     4
00-00-f8-31-f7-a0     1/1     2
00-01-e7-00-e3-80     2/2     0
00-02-a5-84-a7-a6     2/1     1
00-02-b3-1e-b4-aa     2/1     5
00-02-b3-1e-da-da     2/5     1
00-02-b3-1e-dc-fd     2/4     2
```

---

### 7. Backward Learning Algorithm

*   **Mechanism**: The topology is organically learned by inspecting the **Source MAC Address** of all incoming frames.
*   **Rule**: If a bridge receives a frame sourced from Host H1 on Port P1, it permanently notes that Host H1 is reachable via Port P1. The destination MAC is completely ignored for the learning phase.
*   **Updates**: Refreshing the database means updating the "Port" (if the host moved) and resetting the "Age" so the entry stays alive.
*   **Multi-Bridge Operation**: Remote bridges accurately learn a host's location through intermediate links, even if the end-system is not directly connected to them locally.

---

### 8. L2 Network Attacks

*   **MAC Flooding Attack**: The attacker generates a massive amount of frames with randomized MAC source addresses. This quickly fills the Filtering Database capacity. Once full, the bridge defaults to operating like a hub (flooding all unrecognized destination frames), allowing the attacker to sniff and intercept traffic generated by other stations, and simultaneously slowing down the entire network. Mitigation: Administrators can configure limits on the number of MAC addresses learned per port.
*   **Packet Storms**: The attacker generates frames targeting non-existing stations. Because the destinations are unknown, the switch floods the frames across the entire network, causing severe congestion.
*   **MAC Spoofing**: The attacker alters their own MAC address to match a victim's MAC address to impersonate them (easier on Linux, harder on Windows).

---

### Practical Exercises & Scenarios

#### Scenario A: ARP Spoofing (Man-in-the-Middle) Execution
**Context:** L2 protocols implicitly trust incoming addresses. A malicious actor can execute an ARP spoofing attack to intercept traffic between Host A ($10.1.1.1$, MAC A.A.A.A) and Host B ($10.1.1.2$, MAC B.B.B.B).
1.  **Initial State**: Host A attempts to communicate with Host B. It sends an ARP Request asking `? MAC for 10.1.1.2`. Host B sends a legitimate ARP reply `10.1.1.2 = MAC B.B.B.B`.
2.  **Attacker Intervention**: Host C (Attacker, $10.1.1.3$, MAC C.C.C.C) continuously generates "gratuitous ARP replies".
3.  **Poisoning the Tables**:
    *   Host C tells Host A: `10.1.1.2 is bound to MAC C.C.C.C`.
    *   Host C tells Host B: `10.1.1.1 is bound to MAC C.C.C.C`.
4.  **Result**: The subsequent gratuitous replies directly overwrite the legitimate ARP replies in the hosts' tables. Traffic from A to B is sent to C, and traffic from B to A is sent to C, creating a full Man-In-The-Middle intercept.

#### Scenario B: Host Mobility and Network Disruption
**Context:** A Host (H2) physically unplugs from Switch Port 3 and moves to Switch Port 1 on a different logical segment.
1.  **Broadcast Scenario**: If H2 generates a broadcast frame immediately upon reconnecting (common in Windows machines), the frame propagates to all bridges. Every bridge immediately executes Backward Learning, updates their FDB with H2's new port, and connectivity is completely seamless.
2.  **Unicast "Hole" Scenario**: If H2 generates only unicast traffic upon reconnecting, that frame may only reach a small portion of the network. Bridges outside that path still hold the old FDB entry. Traffic directed to H2 from other hosts will be forwarded to the old, dead port and permanently lost.
3.  **Silent Host Scenario**: If H2 is totally silent upon moving (common for UNIX servers and VMWare hosts), a total forwarding "hole" occurs. Traffic to H2 is black-holed at the old port until the aging time (default 5 minutes) expires, dropping the old entry.
4.  **Fault-Tolerant Mitigation**: High-availability environments require reactions faster than 5 minutes. Fault-tolerant NIC drivers are explicitly programmed to fire a gratuitous broadcast frame instantly upon sensing a link-up to force immediate network-wide FDB updates.

---

### 9. Transparent Bridges and End Hosts

*   **Standardization**: Standardized by IEEE as 802.1D.
*   **Transparency**: End-systems require absolutely zero configuration changes to operate on a bridged network.
*   **Frame Integrity**: A frame sent by a host undergoes no formatting changes (same MAC source, same MAC destination) as it transits. The bridge filters what frames arrive at the host, mimicking the hardware MAC filtering previously done by the host's NIC.
*   **Host Reception Rules**: A host connected to a bridge port receives:
    *   All frames sent/received on the immediate physical network segment.
    *   All broadcast and multicast frames (ignoring advanced IGMP snooping).
    *   Unicast frames exclusively matching its exact MAC address.
*   **Port MAC Addresses**: Every physical port on a bridge possesses a real MAC address. However, this MAC address is **never** used for forwarding data frames. It is strictly reserved for frames generated/received by the switch itself (e.g., management frames). Often, bridges assign the exact same MAC address to all ports.

---

### 10. The Loop Problem and Spanning Tree

#### The Broadcast Storm
*   **The Problem**: If a network features physical loops (multiple paths between switches), frames will enter an infinite loop. The backward learning algorithm entirely fails because source MACs arrive rapidly from conflicting ports.
*   **The Consequence**: Broadcast and multicast traffic creates a "Broadcast Storm," inducing a massive load that instantly crashes the LAN. This is one of the most dangerous L2 problems.
*   **The Root Cause**: Unlike L3 IP packets (which possess a TTL mechanism), L2 Ethernet frames lack a "time-to-live" field, meaning loops spin infinitely.

#### The Spanning Tree Protocol (STP)
*   **Origin**: Invented by Radia Perlman (PhD at DEC) and formalized in 802.1D.
*   **Mechanism**: A protocol that operates periodically (every 1 second) to detect physical meshes and algorithmically disable them, transforming the logical network into a strict "tree" with exactly one unique path between any source and destination.
*   **Action**: It dynamically forces specific redundant ports into a "blocking state" while leaving primary ports in a "forwarding state".
*   **Caveat**: Spanning Tree has an initial timeout (default 30 seconds) where it blocks traffic to calculate the tree, causing a noticeable delay when a host first connects.

---

### 11. Switch Hardware, Architecture, and Buffers

#### Bridge vs. Switch Architecture
*   **Legacy Bridge**: Software-based architecture where the Spanning Tree, Backward Learning, and Forwarding processes all share a central CPU/software path. Slow and no longer used.
*   **Modern Switch**: 
    *   **Forwarding & Learning**: Strictly hardware-based using extremely fast Content Addressable Memories (CAMs).
    *   **Spanning Tree**: Kept in software, as convergence natively takes several seconds, making hardware implementation useless for STP.
    *   **Cut-Through Mode**: Hardware switches can implement "cut-through" forwarding, meaning the switch begins transmitting the frame out the destination port the exact microsecond it decodes the Destination MAC (faster than store-and-forward, but mandates all ports run at the exact same speed).
*   **Internal Layout**: Consists of a shared bus or switching matrix, a central CPU/memory, full-duplex links, input/output interfaces, a queuing system on the links, and the Filtering Database.

#### Buffer Limits and Dropped Packets
*   **The Hub vs. Bridge Tradeoff**: Hubs suffered from collisions, but Ethernet's CSMA/CD guaranteed that collided frames were immediately retransmitted at L2. Switches eliminate collisions but introduce **dropped frames**. If a switch buffer fills up, incoming packets are dropped and are **never retransmitted at L2**.
*   **TCP Impact**: Dropped packets have a huge negative impact on TCP performance, as TCP interprets L2 drops as network congestion and aggressively reduces its transmission window.

#### Buffer Hardware Math
*   **Constraints**: Switch packet buffers are astonishingly small (e.g., $12\text{ MB}$ on a $1.44\text{ Tbps}$ switch).
*   **Latency vs. Bandwidth**: Memory bandwidth handles burst transfers, but memory latency dictates random access patterns. 
*   **The SRAM Requirement**: 
    *   Byte arrival time at a $10\text{ Gbps}$ line rate is just $0.8\text{ ns}$.
    *   Traditional DRAM access time is $\sim60\text{ ns}$.
    *   Therefore, switches absolutely require expensive SRAM to keep up with the line rate; standard DRAM is too slow.

#### Port Mirroring
*   **Feature**: Because switches inherently segment traffic, administrators cannot passively sniff a network link.
*   **Solution**: Enterprise switches feature a "mirror port" (known as a "span port" in Cisco environments).
*   **Operation**: The switch is configured to duplicate inbound, outbound, or bidirectional traffic from Monitored Ports ($P1 \dots P_N$) and blast it out a single Mirror Port ($P_{\text{mirror}}$) to a monitoring station.
*   **Limitations**: The aggregate input traffic from multiple ports can easily exceed the physical bandwidth limit of the single mirror link, causing dropped analytical frames. Furthermore, packets may be reordered, and hardware packet timestamps may become imprecise.
*   

### Supplemental Granular Details

*   **WiFi Access Points**: Explicitly defined in the text as functioning as bridges.
*   **Bridges: Pros**:
    *   Completely transparent to the network stack and to the application.
    *   Work seamlessly with all Layer 3 protocols.
    *   Provide automatic configuration via the backward learning algorithm.
    *   Allow for automatic reconfiguration in the event of network faults via the Spanning Tree Protocol.
    *   Increase overall network performance by segmenting into different collision domains.
    *   Truly "Plug and play!" (meaning they are often installed by technicians who do not know anything about the network).
*   **Bridges: Cons**:
    *   Not suitable for complex networks, such as Wide Area Networks (WANs).
    *   Provide absolutely no filtering for broadcast frames.
    *   Cannot perform load balancing over multiple parallel links.
    *   Despite being "plug and play," Spanning Tree configuration is, in practice, required to keep complex networks running properly. 