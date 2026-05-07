Here is the exhaustive master cheat sheet based entirely on the provided lecture materials. 

## **Master Cheat Sheet: Quality of Service (QoS) in IEEE 802 LANs**

### **1. The Fundamental Problem: Congestion in LANs**
* QoS in traffic forwarding is necessary when there is a limited amount of network resources.
* Congestion occurs when the offered traffic exceeds the network's capacity to drain data.
* While LANs are typically over-provisioned (using only 30-40% of available bandwidth), congestion is still possible and can severely impact performance.
* Expanding the network is generally cheaper than enforcing strict QoS, leading to a false sense that QoS is unnecessary.

**Common Congestion Scenarios:**
* **Backbone Not Well Dimensioned:** Insufficient core infrastructure capacity.
* **Many-to-One Transfers:** Data transferred from multiple hosts to a single server simultaneously.
* **Speed Mismatches:** Data transfers from a fast host to a slow host, which can refer to link speed (e.g., 1 Gbps toward 100 Mbps) or CPU capacity limitations.

**Types of LAN Congestions:**
* **Micro-congestions on Uplinks:** Extremely bursty client traffic can affect other clients' short-term transmission intervals. This is emphasized when the ratio of uplink speed to access speed is approximately 1.
* **Persistent Congestions on Edge Servers:** This is emphasized when the ratio of uplink speed to access speed is greater than 1.
* **Temporary Congestions on Clients:** Historically present due to long data transfers over slow links; however, packet-level multiplexing generally alleviates this.

---

### **2. Effects of Missing QoS**
* **Delay Variations (Jitter):** Congestion creates variable delays. Receiving timings strictly influence the behavior of sensitive, real-time applications such as voice, telephony, music, video, videoconferencing, and storage.
* **Dropped Packets:** Congestion causes packet drops due to the very small hardware buffers in network interface cards (NICs) on edge hosts and in network switches (often just tens of KB).
* **Protocol Impact:** TCP recovers dropped packets via timeout and/or fast retransmit, but it halves its window size, leading to steep throughput declines. UDP traffic (like CIFS, NFS) and other protocols (like FCoE) suffer directly. Ironically, network upgrades can sometimes cause performance decreases due to these transport layer dynamics.

---

### **3. Hardware Limitations & Economic Factors**
* **Switch Ubiquity:** A corporate campus can easily have hundreds of switches, potentially connecting thousands of devices (e.g., 100 switches $\times$ 48 ports = 4800 devices).
* **SRAM vs. DRAM Constraints:** Packet buffers must absorb data at extremely high speeds, requiring expensive and power-hungry Static RAM (SRAM). By contrast, standard DRAM has poor memory latency (60-70ns) despite good bandwidth ($>100\text{ GB/s}$).
* **Speed vs. Buffer Math Example:** A 10G port runs at 1.25 GBps. This equals processing 1 byte every 0.8ns, or one 64-byte frame every 51.2ns. 
* **Datasheet Reality Check:** A switch with a $720\text{ Gbps}$ aggregated bandwidth ($48 \times 10\text{Gbe} + 6 \times 40\text{Gbe}$) might only have a $12\text{ MB}$ global packet buffer. Divided up, this results in roughly $170\text{ KB}$ per port, equating to only $0.14\text{ ms}$ of absorbed traffic buffer. (Note: these buffers are usually shared across the switch, not strictly hard-partitioned per port) .

---

### **4. Possible QoS Solutions**
To mitigate variable delays and dropped frames, networks can utilize:
* Large hardware buffers and better congestion control mechanisms.
* Queuing and scheduling algorithms to optimally select the next packet in the buffer, though complex Layer 2 switches are generally undesirable.
* Admission control to limit frames competing for network resources (normally not used in Layer 2 switches).

**IEEE 802 Specific Solutions:**
* **IEEE 802.1p:** A scheduling-based solution utilizing priority control. Valid on all IEEE 802 technologies.
* **IEEE 802.3x:** A congestion control solution utilizing flow control. Valid strictly on IEEE 802.3 (Ethernet) networks.

---

### **5. IEEE 802.1p: Priority Scheduling**
* **Overview:** A simple solution that limits troubles but does *not* truly solve the QoS problem. It strictly implements "priority," not comprehensive QoS guarantees.
* **Hardware Queues:** Usually implemented directly in hardware, mapping traffic into at least 2, and at most 8, different logical queues.
* **Tag Coding (802.1Q integration):** * The priority is encoded as a 3-bit field within the VLAN tag, yielding 8 priority levels (0 to 7). 
    * These 8 levels do not inherently imply a hierarchical relationship.
    * The 802.1Q Tag follows the Source Address and contains: `Length/Type = TPID (81-00)` [2 bytes], `user priority` [3 bits], `CFI` [1 bit], and `VID (VLAN ID)` [12 bits].
* **Suggested Priority/Traffic Associations:** (Not legally mandated) 
    * **0:** Best Effort (BE) 
    * **1:** Background (BA) 
    * **2:** (not defined) 
    * **3:** Excellent Effort (EE) 
    * **4:** Controlled Load (CL) 
    * **5:** Video (VI) â€” Latency & jitter $< 100\text{ms}$ 
    * **6:** Voice (VO) â€” Latency & jitter $< 10\text{ms}$ 
    * **7:** Network Control (NC) 
* **Scheduling Algorithms:** Recommends fixed priority, but configurations can leverage variable priority algorithms like Round Robin, Weighted Round Robin, or Weighted Fair Queuing.
* **Marking the Packet:**
    * **Per-Port Marking (Switch-based):** Simple, but problematic if multiple users share a single access link. 
    * **Per-VLAN Marking (Edge Device):** Common in modern networks with IP phones. Works well if the edge device is trusted.
    * **Host NIC Marking:** Problematic because software configurations vary, L3-L4 inspection is required for proper app identification, and keeping MAC databases updated is difficult. Access sides also require VLAN trunking.

**IEEE 802.1p Switch Functional Architecture Pipeline:**
1. Filtering Frames 
2. Enforcing topology restrictions (STP) 
3. Queuing Frames 
4. Selecting frames for transmission 
5. Mapping priority 
6. Recalculating FCS (Frame Check Sequence) 

---

### **6. IEEE 802.3x: Flow Control**
* **Overview:** Implements flow control at the Layer 2 Ethernet level, completely independent of the existing TCP-level flow control. 
* **The PAUSE Packet Mechanism:** * Uses a special, multicast `PAUSE` packet confined strictly to a single physical link.
    * Upon receiving it, the device must temporarily halt data transmission for an exact amount of "idle" time specified within the packet payload.
    * This timer can be actively extended or reduced if another PAUSE packet arrives before the original timer expires. 
    * In a switch, receiving a PAUSE on one link does not stop the switch from sending/receiving data on its other interfaces.

**PAUSE Packet Frame Structure (64 Bytes Total):**
* **Destination Address:** `01-80-C2-00-00-01` (6 octets) 
* **Source Address:** (6 octets) 
* **Length/Type:** `8808` (2 octets) 
* **OpCode:** `00-01` representing PAUSE (2 octets) 
* **Pause_time:** Number of pause-quanta (2 octets) 
* **PAD:** All zeros (42 octets) 
* **FCS:** Frame Check Sequence (4 octets) 

**Formulas & Timing (The Pause Quanta):**
* Pause time is defined purely in "pause-quanta", accepting values from $0$ to $65535$.
* One single pause-quanta equals $512$ bit times.
* **For Links $\le 100 \text{ Mb/s}$:** $T_{\text{Pause}} = \text{pause-quanta} \times 512$ 
* **For Links $> 100 \text{ Mb/s}$:** $T_{\text{Pause}} = \text{pause-quanta} \times 512 \times 2$ 

**Flow Control Operational Modes:**
* **Asymmetric Mode:** Only one edge device is allowed to send the PAUSE packet; the other device just receives it and obeys the transmission halt.
* **Symmetric Mode:** Both devices on the edge of the link can transmit and receive PAUSE packets.
* These are set on each port, and an auto-negotiation phase establishes the final coherent configuration.

**Practical Implementations & Problems with 802.3x:**
* **Host Constraints:** Handled in the NIC hardware, making it OS-independent. However, OS/NIC interaction can sometimes prevent generation, causing livelocks in the kernel.
* **Switch Constraints:** 802.3x is highly problematic for backbones. Finding the "responsible" party for a full queue is difficult in output-buffered switches or congested switching matrixes (should it block *all* IN ports?). Many commercial switches will obey incoming PAUSE packets but are physically incapable of generating and sending them outward. 
* **Network Halting:** Because PAUSE halts the entire link, one slow cluster of stations can cascade and completely block backbone segments for periods of time.
* **The Realistic Deployment Architecture:** Do not use full-feature flow control everywhere. Apply **Asymmetric Flow Control exclusively on the access network** (hosts can pause the switch, but the switch cannot pause the hosts), and leave **No Flow Control in the core backbone**. This absorbs temporary host NIC congestion without risking entire backbone paralysis.


### **Appendix A: IEEE 802.1p Recommended Queue Aggregation Matrix**
If a switch does not physically support 8 separate hardware queues, the IEEE recommends aggregating the 8 priority types (Background [BK], Best Effort [BE], Excellent Effort [EE], Controlled Load [CL], Video [VI], Voice [VO], Network Control [NC]) based on the number of available queues.

Here is the exact recommended aggregation mapping from the lecture:

| Number of Queues | Queue 1 | Queue 2 | Queue 3 | Queue 4 | Queue 5 | Queue 6 | Queue 7 | Queue 8 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | BE | | | | | | | |
| **2** | BE | VO | | | | | | |
| **3** | BE | CL | VO | | | | | |
| **4** | BK | BE | CL | VO | | | | |
| **5** | BK | BE | VI, CL | VO | | | | |
| **6** | BK | BE | EE | VI, CL | VO | | | |
| **7** | BK | BE | EE | VI, CL | VO | NC | | |
| **8** | BK | BE | EE | VI | CL | VO | NC | *(Queue 8 explicitly separates VI and CL)* |

---

### **Appendix B: Granular Hardware Datasheet Metrics**
To illustrate exactly why switches drop packets due to SRAM costs, the document provides a literal datasheet screenshot of modern Layer 3 switches running **Cumulus Linux**. Here are the exact hardware limits, ASIC names, and specific register boundaries mentioned:

*   **Switch Models Referenced:** N5850-48S6Q, N5000-48B6C, N8000-32Q, N8500-32C.
*   **Switching Capacity / Forwarding:** Ranging from 1.44 Tbps (1.07 Bpps) up to 6.4 Tbps (4.7 Bpps) full-duplex.
*   **Latency:** Ranges from 500ns to 800ns.
*   **Packet Buffers (SRAM):** Precisely **12MB** or **16MB** depending on the model.
*   **Routing Table Exact Limits:** 
    *   IPv4 Route entries: 131,072 or 65,536.
    *   IPv6 Route entries: 20,480 or 8,192.
*   **Specific CPUs & ASICs Used:**
    *   **CPUs:** Broadwell-DE 2.2Ghz 2-core, or Intel Rangeley C2538 2.4Ghz 4-core.
    *   **Switch Chips:** Broadcom Trident 2 (BCM56850), Broadcom Tomahawk (BCM56960), Broadcom Trident 2+ (BCM568X), Broadcom Tomahawk+ (BCM5696x).

---

### **Appendix C: The Host NIC Internal Bus Trace**
When a host generates a `PAUSE` packet, it relies heavily on the internal bus architecture. The document outlines the specific hardware trace between the host components:

*   **The Hardware Path:**
    *   The **NIC** is attached to the **PCI Bus**.
    *   Memory accesses happen via **DMA (Direct Memory Access)** bridging the PCI Bus and the system **RAM**.
    *   Processing interrupts happen via **IRQ** signals bridging the PCI Bus and the **CPU**.
*   **The Bottleneck:** Because flow control *can* be handled entirely by the NIC hardware (bypassing the OS), it is fast. However, if the NIC driver forces an OS interaction via this IRQ/CPU path, it can result in a kernel livelock, preventing the PAUSE frame from ever generating. 

