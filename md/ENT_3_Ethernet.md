## Master Cheat Sheet: Ethernet Fundamentals & System Architecture

### 1. History & Fundamentals
*   **Initial Concept:** The first prototype was developed in 1973 at Xerox PARC, operating at a speed of 2.94 Mbps.
*   **Commercial Standardization:** The first commercial specifications were released in 1980 with a speed of 10 Mbps.
*   **DIX Consortium:** Ethernet design was heavily driven by Digital, Intel, and Xerox (DIX), and this standard is also known as Ethernet 2.0.
*   **Market Position:** It was the first successful Local Area Network (LAN) technology, initially competing mostly against Token Ring.
*   **Topology:** Originally based on a physical bus topology, which later evolved into a logical bus.
*   **Hardware Components:** Early physical layouts included components such as the Terminator, Tap, Transceiver, Interface Cable, and Interface Controller connecting the station to "The Ether" (the bus).

### 2. CSMA/CD Protocol Principles
Ethernet utilizes **CSMA/CD** (Carrier Sense, Multiple Access with Collision Detection). This MAC (Medium Access Control) protocol is non-deterministic and has no upper limit for the waiting time before transmission.
*   **Carrier Sense:** Defined as "Listen before talking.". A station will only transmit data if it senses that no one else is currently talking.
*   **Multiple Access:** Everyone on the network can talk, potentially at the same time.
*   **Collision Detection:** Defined as "Listen while talking!". Because propagation speed is not infinite, two stations might start transmitting simultaneously and cause a collision. Stations continue to listen to the channel while transmitting to detect these collisions.

### 3. Collision Detection Mechanics
*   **The Problem of Propagation:** The "listen while talking" mechanism works in theory, but because signal propagation speed is not infinite, collisions may initially happen undetected by the sending stations.
*   **The Active Talker Rule:** To accurately detect a collision, all transmitting stations *must still be active* (still transmitting) when the collision reaches them.
*   **Interdependent Variables:** This physical requirement ties together three critical variables: the maximum distance between stations, the signal propagation speed, and the minimum duration of a transmission (minimum frame size).
*   **Worst-Case Scenario:** The worst-case collision scenario occurs when Hosts A and B are at the maximum allowed distance. If Host A starts transmitting at $t_1$, and Host B starts transmitting right before A's signal arrives (at $t_1 + t_p - \epsilon$), Host B detects the collision at $t_1 + t_p$, but Host A will not detect the collision until time $2t_p - 2\epsilon$.

#### Real-World Collision Detection Hardware Behaviors
*   **Coax Cable:** Collisions are detected by measuring the average Direct Current (DC) on the link. All stations on a coax network can report the correct number of total network collisions.
*   **Twisted Pair / Fiber:** Transmitting stations detect collisions by observing simultaneous activity on both their TX (transmit) and RX (receive) links. Because these are bidirectional, each station only knows its *own* number of collisions.
*   **Role of CRC:** Receiving stations cannot always detect a collision just by inspecting the physical signal. Therefore, collisions appear as wrong CRC (Cyclic Redundancy Check) errors to other listening stations.
*   **Hub Behavior:** Hubs simply propagate incoming signals to all ports except the port the signal originated from.

### 4. The Jamming Sequence
*   **Purpose:** To guarantee that a collision results in an invalid CRC, maximizing the probability that all stations recognize the error.
*   **Structure:** It is a 32-bit sequence.
*   **Execution:** When a collision is detected, the station transmits the Jamming Sequence repeatedly until the total transmission time equals the "minimum duration of the talk" (minimum frame length). This ensures the transmission is exactly the minimum frame length and no more, keeping channel arbitration highly efficient.
*   **Calculation Example:** If a station detects a collision after transmitting 100 bits, it must repeat the 32-bit Jamming Sequence $(512 - 100) / 32$ times to reach the 512-bit minimum.

### 5. Back-Off Algorithm
When a collision occurs, it is not an error but a feature used to arbitrate the channel (with zero overhead when no collisions occur, unlike token passing). Collided frames must be reliably re-transmitted. 
*   **Wait Time:** Each station waits for a random time interval before re-trying to avoid immediate subsequent collisions.
*   **Algorithm:** Ethernet uses the **Truncated Binary Exponential Back-off algorithm**.
*   **Parameters:**
    *   $\tau$ = time required to transmit a 512-bit slot.
    *   $n$ = number of collisions that have occurred on the *current* frame.
*   **Formulas:**
    *   A random value $r$ is chosen according to the inequality: $0 \le r < 2^k$.
    *   The exponent $k$ is calculated as: $k = \min(n, 10)$.
    *   The total waiting time $T$ between two consecutive transmissions is: $$T = r \cdot \tau$$.
*   **Maximum Limit:** The system allows a maximum of 16 re-transmissions for the same frame. If 16 is reached, the transmission is aborted, which usually indicates a network health issue.

### 6. Frame Formatting & Standards
*   **Network Limits:** Maximum speed is 10 Mbps. Minimum frame size is 64 bytes (to guarantee adequate collision diameter). Maximum frame size is 1518 bytes (to guarantee adequate statistical multiplexing over shared channels).
*   **Slot Time Definition:** The time required to send a minimum Ethernet frame, expressed in "bit times". For Ethernet, this is 512 bit times (or $51.2 \mu\text{s}$). Slot time does *not* include the Preamble and Start Frame Delimiter.
*   **Inter-Frame Gap (IFG):** The minimum silence required between two frames. It is 96 bit times ($9.6 \mu\text{s}$). Also called "Inter-Frame Spacing" in IEEE 802.3.

#### Ethernet V2.0 (DIX) Format
Direct encapsulation method retaining the older standard format.
*   **Preamble:** 7 bytes (used to sync source/receiver).
*   **SFD (Start of Frame Delimiter):** 1 byte (special invalid L1 code signaling frame start). Note: There is no end-of-frame delimiter.
*   **MAC Dest:** 6 bytes.
*   **MAC Source:** 6 bytes.
*   **Ethertype:** 2 bytes (Used for protocol demultiplexing. Must be $\ge 1536$ or $0\text{x}0600$). Common types: IP = $0\text{x}0800$, ARP = $0\text{x}0806$, IPv6 = $0\text{x}86\text{DD}$.
*   **Data:** 46 to 1500 bytes. L3 protocols must include a "length" field if their protocol is $< 46$ bytes because DIX is missing a Padding field.
*   **FCS (Frame Check Sequence):** 4 bytes.

#### IEEE 802.3 (+ SNAP) Format
Created to standardize Ethernet, though many protocols kept DIX to avoid adding useless complexity.
*   **Header (14 bytes):** MAC Dest (6 bytes) + MAC Source (6 bytes) + Length (2 bytes, must be $\le 1500$).
*   **LLC + SNAP (8 bytes):** AA-AA-03 (3 bytes) + OUI 00-00-00 (3 bytes) + Ethertype (2 bytes).
*   **Data:** 0 to 1492 bytes.
*   **Pad:** 0 to 43 bytes.
*   **FCS:** 4 bytes.

### 7. Physical Layer Architecture (10 Mbps, 100ns bit time)
All standard 10 Mbps Ethernet specifications utilize Manchester physical coding at 10MHz.

*   **10Base5 (Thick Coax):** 
    *   Cable: RG213 "Yellow cable (IBM)" (50 Ohm).
    *   Max cable length: 500 m.
    *   Min distance between transceivers: 2.5 m.
    *   Max transceivers: 100.
    *   Max transceiver cable length: 50 m.
    *   Connectors: Vampire taps, Barrel connectors.
*   **10Base2 (Thin Coax):**
    *   Cable: RG58 (50 Ohm).
    *   Max cable length: 185 m.
    *   Min distance between stations: 0.5 m.
    *   Max stations: 30.
    *   Connectors: "T" connectors. Transceivers are located directly on the NIC board.
*   **10BaseT (Twisted Pair):**
    *   Cable: UTP minimum Category 3. Can also be STP (Shielded) or FTP (Foiled/Fully Shielded).
    *   Max length: 100 m.
    *   Connectors: 8-pin RJ45 wall sockets and connectors.
    *   Topology Limit: Limits diameter to ~200 m. Requires an intermediate Hub which simulates the bus internally using two unidirectional cables (1 TX only, 1 RX only).
*   **Fiber Optics:** 
    *   Provides immunity to electromagnetic fields and allows larger network diameters (~3Km).
    *   **FOIRL:** Asynchronous, repeater-to-repeater (1000 m).
    *   **10BaseFL:** Asynchronous, station or repeater-to-repeater (2000 m).
    *   **10BaseFB:** Synchronous, repeater-to-repeater (2000 m).

---

### 8. Practical Math: Collision Detection Formulas
When calculating the maximum distance of a collision domain, repeaters must be taken into consideration. Because repeaters can shorten the Preamble, no more than 4 cascading repeaters are allowed in an IEEE 802.3 network. 

*   **Input Data Variables:**
    *   $D_{max}$ = Maximum distance.
    *   $S_{signal}$ = Signal propagation speed.
    *   $F_{min}$ = Minimum transmission size.
    *   $B$ = Network bandwidth.

*   **Core Derivations:**
    *   Propagation Time: $$t_p = \frac{D_{max}}{S_{signal}}$$.
    *   Collision Window (Min Frame duration): $$\frac{F_{min}}{B} = 2 \cdot t_p$$.

*   **The Master Formula:**
    $$D_{max} = \frac{(F_{min} - 1 \text{ bit}) \cdot S_{signal}}{2 \cdot B}$$.

#### Step-by-Step Practical Exercise Breakdown
**Problem:** Calculate the Maximum Distance ($D_{max}$) for a standard 10 Mbps Ethernet network based on the provided IEEE 802.3 parameters.

**Step 1: Identify the Given Values**
*   Bandwidth ($B$): $10 \text{ Mbps} = 10,000,000 \text{ bits/second}$
*   Signal Speed ($S_{signal}$): $200,000 \text{ Km/s} = 200,000,000 \text{ meters/second}$
*   Minimum Frame Size ($F_{min}$): $64 \text{ bytes (Data+MACs)} + 7 \text{ bytes (Preamble)} + 1 \text{ byte (SFD)} = 72 \text{ bytes total}$

**Step 2: Convert Minimum Frame Size to Bits**
*   $F_{min} = 72 \text{ bytes} \cdot 8 \text{ bits/byte} = 576 \text{ bits}$

**Step 3: Apply the Values to the Master Formula**
*   $$D_{max} = \frac{(576 \text{ bits} - 1 \text{ bit}) \cdot 200,000,000 \text{ m/s}}{2 \cdot 10,000,000 \text{ bps}}$$
*   $$D_{max} = \frac{575 \text{ bits} \cdot 200,000,000 \text{ m/s}}{20,000,000 \text{ bps}}$$

**Step 4: Solve the Equation**
*   $$D_{max} = \frac{115,000,000,000}{20,000,000}$$
*   **Result:** $$D_{max} = 5750 \text{ m}$$.