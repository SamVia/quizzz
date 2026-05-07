# Master Cheat Sheet: Link Aggregation (IEEE 802.3ad)

## 1. Core Concepts and Fundamentals
Link aggregation is a solution that combines several physical ports into a single logical channel.
* **Primary Benefits**:
    * Resolves Spanning Tree Protocol (STP) issues that arise when there are multiple links between the same devices.
    * Provides an incremental increase in bandwidth capacity without the need to purchase much more expensive technology (e.g., upgrading directly to 10x speed, which may be costly or non-existent).
    * Improves network resiliency by offering a smooth decrease of bandwidth in the event of a link fault, rather than a total outage.
    * Avoids STP convergence time if a single link within the aggregate fails, as it is highly unlikely all cables will break simultaneously.
* **Typical Usage**: Commonly deployed between switches, and occasionally between a switch and a computer/server.

## 2. Pre-Standard Solutions vs. IEEE 802.3ad
Before the official IEEE standard, proprietary solutions (such as Cisco EtherChannel) were used. 
* **Static Configuration Issues**: Pre-standard static setups struggled with errors, such as links terminating at different switches, or connecting devices with different maximum channel capacities.
* **IEEE 802.3ad Features**:
    * Standardized the aggregation of several ports into a single channel.
    * Introduced Autoconfiguration: Devices can dynamically recognize the number of available links and verify that all links correctly terminate at the same two endpoint switches.
    * Often referred to as a "port channel," retaining the original Cisco terminology.

## 3. Configuration Rules & Specifications
To successfully form a link aggregation group under 802.3ad, strict physical and logical requirements apply:
* **Link Requirements**: 
    * Available only on full-duplex links.
    * All links must terminate at the exact same devices.
    * All physical links within the group must operate at the identical speed.
    * *Note:* It is not required for the physical links to be numerically in sequence (e.g., port 1 and port 4 can be aggregated).
* **Grouping Parameters**:
    * Usually, 2 to 4 physical links are grouped into one aggregate. 
    * If more than 4 links are needed, upgrading to a 10x faster technology is usually recommended.
    * Multiple aggregations can exist, but STP will only allow one aggregate to be active to prevent loops.
    * Convergence is extremely fast (typically less than 1 second).

## 4. Link Aggregation Control Protocol (LACP)
LACP is the protocol responsible for the automatic configuration of link aggregation.
* **LACPDU Transmission**: 
    * Transmitted via multicast.
    * Exchanged periodically in three scenarios: when ports are first connected, periodically every 3 or 90 seconds, and immediately when a link failure occurs.
* **Actor/Partner Model**: Each device acts simultaneously as both an "Actor" and a "Partner," and LACPDUs contain parameters for both.

### LACPDU Frame Format
The structure of an LACPDU frame is strictly defined byte-by-byte:
* **Destination Address**: 6 octets (Fixed to `01-80-C2-00-00-02`) 
* **Source Address**: 6 octets 
* **Length/Type**: 2 octets (Value = `88-09`) 
* **SubType**: 1 octet (1 = Link Aggregation Control Protocol, 2 = Link Aggregation Marker Protocol) 
* **Version**: 1 octet 
* **LACP Info**: 108 octets 
* **FCS**: 4 octets 

## 5. Link Aggregation Group Identifier (LAG ID)
The LAG ID uniquely identifies the aggregate and determines if two individual ports belong to the same membership group. It consists of three main components, which are also utilized for STP configuration:
1.  **System Identifier**: Composed of the System Priority (default is 32768) and the device's MAC Address (or a management-specified MAC for virtual switches).
2.  **Operational Key**: A key associated with all ports in the aggregate, explicitly configured by the network manager.
3.  **Port Identifier**: Composed of the Port Priority and the port number (set to zero if deemed unnecessary).

**Example of an Individual Link's LAG ID Payload**:
```text
System Parameters (S,T)
Partner SKP: System Priority = 0x8000, System Identifier = AC-DE-48-03-67-80
Partner TLQ: System Priority = 0x8000, System Identifier = AC-DE-48-03-FF-FF

Key Parameter (K,L)
Partner SKP: Key = 0x0001
Partner TLQ: Key = 0x00AA

Port Parameters (P, Q)
Partner SKP: Port Priority = 0x80, Port Number = 0x0002
Partner TLQ: Port Priority = 0x80, Port Number = 0x0002

Complete LAG ID Representation:
[(SKP), (TLQ)] = [(8000,AC-DE-48-03-67-80,0001,80,0002), (8000,AC-DE-48-03-FF-FF,00AA,80,0002)]
```

## 6. Packet Distribution and Load Balancing
The 802.3ad standard does *not* specify a mandatory load balancing algorithm; it only suggests criteria, meaning switches from different vendors may route traffic differently (and return paths may differ from outgoing paths). Packets are not segmented and reassembled; multiple conversations simply flow over a single port.

* **The Reordering Problem**: Packet reordering must be avoided. A large frame (e.g., 1500B) sent on Link 1 may take longer to arrive than a smaller frame (e.g., 100B) sent immediately after on Link 2. Reordering triggers the TCP fast retransmit algorithm (3 duplicate ACKs), which shrinks the TCP window and significantly damages throughput. This happens even if the cables are the exact same length.
* **The Solution**: All packets belonging to the same conversation (like a TCP session) must be pinned to the same physical link. If a conversation is moved (due to a link failure or new link addition), a small delay is introduced before transmission resumes to ensure in-order delivery.

### Packets Distribution Criteria
Algorithms assign conversations based on single or combined factors. More complex criteria require more expensive L3/L4 switches, though they do not guarantee better performance:
* Source MAC Address 
* Destination MAC Address 
* Receiving port 
* Type of destination address (unicast, multicast, broadcast) 
* Length/Type value 
* Higher Layer Protocol (e.g., Layer 4 port information) 

### Cisco Distribution Criteria (K-OR Math Logic)
Cisco utilizes a bitwise K-OR (XOR) operation on the last bits of the Source and Destination MAC addresses to choose the link.

* **Example 1**: Src `...01` (Last bits: 01), Dst `...04` (Last bits: 00). `01 XOR 00 = 01` -> **Link 2**.
* **Example 2**: Src `...02` (Last bits: 10), Dst `...05` (Last bits: 01). `10 XOR 01 = 11` -> **Link 4**.
* **Example 3**: Src `...03` (Last bits: 11), Dst `...07` (Last bits: 11). `11 XOR 11 = 00` -> **Link 1**.
* **Example 4**: Src `...06` (Last bits: 10), Dst `...08` (Last bits: 00). `10 XOR 00 = 10` -> **Link 3**.

## 7. Practical Scenarios and Edge Cases
### Known Distribution Problems
* **Limited MACs**: Datacenters often have limited unique MAC addresses, leading to sub-optimal balance across links.
* **Server to Router Constraint**: If a server receives traffic from a router via an aggregate, both Src and Dst MACs remain identical for all flows, pushing all traffic onto a single physical link.
* **Elephant Flows**: A single gigantic TCP session (like a nightly backup) will only use one link, capping out its bandwidth.
* **Asymmetric Balancing**: Servers might round-robin traffic, but routers often still rely strictly on MAC-based criteria.

### Practical Exercise / Bad Design: CrownLabs @ POLITO
* **Scenario**: Server 1 communicates exclusively with Server 2 through a 10G switch. Both servers have dual-port 10G NICs set up in link aggregation.
* **Upstream (S1 to Switch)**: Linux acts intelligently, utilizing TCP-level (L4) information to distribute the various TCP sessions perfectly across both physical links.
* **Downstream (Switch to S2)**: The switch is a Layer 2 device and can only look at MAC addresses. Since all packets have `MACsrc = S1` and `MACdst = S2`, the switch's algorithm pins every single frame to only *one* link.
* **The Result**: S1 transmits 20G of traffic. The switch attempts to funnel 20G down a single 10G pipe to S2. Frames buffer until full, drops occur, TCP shrinks its speed, and interface counters on the switch explode with "buffer overflow" errors. 
* **Conclusion**: Link aggregation is counter-productive for massive 1:1 server traffic, but highly effective if S1 was instead communicating with many servers (S2, S3, S4) creating "mice flows" and distinct MACs.

## 8. STP/RSTP Integration
Link aggregation fundamentally alters how Spanning Tree Protocol views the topology:
* STP stops recognizing the physical links and only calculates based on the logical aggregate channel.
* **Configuration Warning**: You must disable automatic path cost and set the Path Cost manually to reflect the new massive bandwidth. RSTP is preferred due to its wider range of Path Cost values.
* **Failure Behavior**: If a single link within an aggregate breaks (e.g., a 2Gbps aggregate drops to 1Gbps), the cost of the logical link doubles. This cost change triggers a recalculation of STP/RSTP. However, because no *new* physical loops have been introduced, RSTP carefully keeps the 'old' topology alive, allowing the network to continue functioning without disruption during the transient.

## 9. Advanced Features: Standby Links
* Aggregation supports configuring an aggregate of $N$ links, where only $M$ (where $M < N$) are active.
* The inactive links act as hot "standbys" or backups. If an active link fails, a standby instantly takes over, guaranteeing the aggregate bandwidth does not decrease. 
* This is achieved by properly setting link priorities. Advanced configurations technically allow physical links to shift between primary and secondary groups dynamically, though this is rarely used in practice.

## 10. System Trace: Cisco Configuration Example
The following terminal trace shows the creation of a port-channel on a Cisco 2691 (Etherswitch linecard):

```text
R1#enable
R1#configure terminal
Enter configuration commands, one per line. End with CNTL/Z.
R1(config)#interface range FastEthernet 1/0 - 1
R1(config-if-range)#channel-group 1 mode on
Creating a port-channel interface Port-channel1

R1(config-if-range)#
*Mar 1 00:01:35.119: %EC-5-BUNDLE: Interface Fa1/0 joined port-channel Po1
*Mar 1 00:01:35.539: %EC-5-BUNDLE: Interface Fa1/1 joined port-channel Po1
R1(config-if-range)#

*Mar 1 00:01:37.967: %LINEPROTO-5-UPDOWN: Line protocol on Interface Port-channel1, changed state to up
R1(config-if-range)#end
*Mar 1 00:03:02.399: %SYS-5-CONFIG_I: Configured from console by console
R1#

R1#sh interface port-channel 1
Port-channel1 is up, line protocol is up
Hardware is EtherChannel, address is c001.07e3.f100 (bia c001.07e3.f100)
MTU 1500 bytes, BW 200000 Kbit, DLY 1000 usec,
reliability 255/255, txload 1/255, rxload 1/255
Encapsulation ARPA, loopback not set
Keepalive set (10 sec)
Full-duplex, 100Mb/s
Members in this channel: Fa1/0 Fa1/1
ARP type: ARPA, ARP Timeout 04:00:00
Last input 00:00:00, output never, output hang never
Last clearing of "show interface" counters never
Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
Queueing strategy: fifo
Output queue: 0/40 (size/max)
5 minute input rate 0 bits/sec, 0 packets/sec
5 minute output rate 0 bits/sec, 0 packets/sec
0 packets input, 0 bytes, 0 no buffer
Received 0 broadcasts, 0 runts, 0 giants, 0 throttles
0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
0 input packets with dribble condition detected
0 packets output, 0 bytes, 0 underruns
0 output errors, 0 collisions, 1 interface resets
0 unknown protocol drops
0 babbles, 0 late collision, 0 deferred
0 lost carrier, 0 no carrier
0 output buffer failures, 0 output buffers swapped out
```
