## Ethernet Evolutions: Master Cheat Sheet

### Historical Perspective & Paradigm Shifts
*   **Wired Network Dominance:** Ethernet is the unequivocally successful and *de facto* standard for wired Local Area Networks (LANs), having eliminated all other wired competitors.
*   **Technological Shifts:**
    *   **Hubs to Switches:** The physical evolution from hubs to switches fundamentally altered Ethernet topology and capabilities.
    *   **CSMA/CD Obsolescence:** The Carrier-Sense Multiple Access with Collision Detection (CSMA/CD) algorithm has disappeared, replaced by Full Duplex communication.
    *   **Removal of Collision Domains:** By eliminating CSMA/CD, the strict size limitations previously imposed by collision domains were eradicated.
    *   **New Diameter Limits:** Currently, the maximum LAN diameter is solely determined by the physical layer's transmission quality and optical/electrical degradation.
*   **Initial Adoption Challenges:** Fast Ethernet (100 Mbps) initially experienced slow market adoption until network switches were broadly introduced.

### Lessons Learned in Network Engineering
*   **The Winning Formula:** Technologies win the market by being simple and cheap, driving massive adoption, even if they lack 100% delivery guarantees. 
*   **Defeated Competitors:** Ethernet outlasted competitors including Token Ring, FDDI, 100VG-Anylan, Gigabit Token Ring, and ATM.
*   **Physical Layer (PHY) Reuse:** Engineering standards for physical layers can be recycled (e.g., Fast Ethernet leveraged the existing FDDI physical layer) to drastically speed up market adoption and cut development costs.
*   **The Necessity of Backward Compatibility:**
    *   **Frame Format:** Maintaining a consistent frame format over decades has been crucial.
    *   **Human Capital:** Preserving workforce investments is vital, as converting network engineers to entirely new technologies is difficult.
    *   **Infrastructure:** Preserving physical infrastructure (like existing cabling) heavily dictates technological success.
*   **Standardization Politics:** While standards are necessary, the industry always features factions aggressively pushing for rapid advancement alongside factions pushing back to block or delay standardization.

---

### Main Ethernet Standards & Performance Metrics

| Metric | Ethernet (10 Mbps) | Fast Ethernet (100 Mbps) | Gigabit Ethernet (1 Gbps) | 10 Gigabit Ethernet | 100 Gigabit Ethernet |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Transmission Speed** | 10 Mbps | 100 Mbps | 1 Gbps | 10 Gbps | 100 Gbps |
| **Bit Time** | 100 ns | 10 ns | 1 ns | 0.1 ns | 0.01 ns |
| **Inter-frame Gap (IFG)** | 9.6 us | 0.96 us | 96 ns | 9.6 ns | 0.96 ns |
| **Minimum Frame Time** | 51.2 us | 5.12 us | 512 ns | 51.2 ns | 51.2 ns |
| **Physical Cabling** | Thin coax / RJ45 copper | RJ45 copper | RJ45 copper (shielded) / fiber optics | Mainly fiber optics | Mainly fiber optics |

---

### Architectural Limits & Layer Specifications

#### Fast Ethernet (IEEE 802.3u)
*   **Core Architecture:** Kept the same frames and CSMA/CD algorithm as 10 Mbps Ethernet, but changed the collision domain (max network diameter).
*   **Topological Limitations:**
    *   **Hubs:** Limited to a maximum distance of roughly 210 meters (e.g., 100m to hub + 10m to second hub + 100m to node).
    *   **Switches:** Enabled networks spanning several kilometers using multiple cascading switches (e.g., 100m to switch + ~1 Km backbone + 100m to node).
*   **Physical Layer (PHY) Variations:**
    *   **100BASE-T4:** Uses twisted pair cable (4 pairs), operates at 37.5MHz, and utilizes 8B/6T coding.
    *   **100BASE-TX:** Uses twisted pair cable (2 pairs), operates at 31.25MHz, and utilizes 4B/5B + MLT-3 coding.
    *   **10BaseT (Baseline):** Uses twisted pair cable (2 pairs), operates at 10MHz, and utilizes Manchester coding.

#### Gigabit Ethernet (GbE - IEEE 802.3z)
*   **Operational Mode:** While the standard defined CSMA/CD mode, it was never utilized in practice; GbE is exclusively deployed in switched (full-duplex) mode.
*   **Use Case:** Currently deployed mostly for connecting user/edge devices, while backbone links leverage 10Gbps+.
*   **Physical Layer Engineering:** The majority of modern Ethernet evolution now occurs strictly at the physical layer, falling under electronic/telecommunication engineering, leaving computer engineers with little influence.
*   **1000BASE-T Specification:** Uses Unshielded Twisted Pair (UTP) balanced 100 Ohm Category 5E cabling. Requires all 4 pairs and supports a maximum distance of 100m.
*   **Fiber Specifications:** Multiple standards exist supporting from ~250m up to several kilometers.
    *   **MMF:** Multi Mode Fiber (older technology).
    *   **SMF:** Single Mode Fiber (newer, superior performance).

#### 10 Gigabit Ethernet (IEEE 802.3ae)
*   **Deployment Environment:** Not intended for desktop use due to lack of necessity and incompatibility with existing Cat5E twisted-pair cabling.
*   **Datacenter & Backbone:** Relies heavily on copper (10GBaseX, twinax) for server datacenters, and fiber for datacenter backbones.
*   **Distance Capabilities:** Supported over long distances for Metropolitan Area Networks (MAN) and Wide Area Networks (WAN), with varying maximal limits (<100m up to 40/100 Km) depending on optics quality and cost.

---

### Frame Formatting & Backward Compatibility

#### The Frame Size Dilemma
*   **Minimum Limit:** The minimum Ethernet frame size is 64 bytes (denoted as $F_{min} = 64\text{ bytes}$). This value is entirely anachronistic, originally defined strictly for the CSMA/CD algorithm, but is maintained universally for backward compatibility.
*   **Maximum Limit:** The maximum Ethernet frame size is 1518 bytes (denoted as $F_{max} = 1.5\text{ Kbytes}$). This boundary was originally calculated to guarantee reasonable network multiplexing on 10Mbps links.
*   **Transmission Time Calculation:** The 1518-byte maximum frame requires exactly 1.2 milliseconds of transmission time at 10 Mbps.
*   **Efficiency Trade-off:** Larger frames drastically reduce header overhead and decrease header processing requirements (lowering per-packet processing costs).

#### Ethernet Frame Structures
Currently, there are two widely used frame formats: **Ethernet DIX** ("original") and **IEEE** ("official"). A boundary value of $\ge 1536$ (0x0600) in the length/type field distinguishes the DIX Ethertype from the IEEE length.

**1. Ethernet DIX Structure:**
```text
[Preamble (7)] [SFD (1)] | [Dest. MAC (6)] | [Source MAC (6)] | [Ether type (2)] | [Data (46-1500)] | [FCS (4)] | [IFG (8 or 3)]
```
*(Note: Data length can also be represented as 0-1497 or 0-1492 with padding)*.

**2. IEEE Structure:**
```text
[Preamble (7)] [SFD (1)] | [Dest. MAC (6)] | [Source MAC (6)] | [Length (2)] | [LLC + SNAP (8)] | [Data (Pad) (≤ 1500)] | [FCS (4)] | [IFG (8 or 3)]
```
*   *LLC + SNAP Breakdown:* `AA-AA-03` (3 bytes) | `OUI 00-00-00` (3 bytes) | `Ether type` (2 bytes).
*   *Acronym:* **SFD** stands for Start of Frame Delimiter.

---

### Copper Cabling Support Matrix (1 Gbps to 10 Gbps)

The emergence of intermediate speeds (2.5Gbps and 5Gbps) occurred to maximize the utility of existing physical infrastructure, avoiding the high costs of upgrading to 100Gbps before specifications were fully ready.

| Cable Category | 1 Gbps | 2.5 Gbps | 5 Gbps | 10 Gbps |
| :--- | :--- | :--- | :--- | :--- |
| **Category 5e** | Supported | Supported | Supported | Not Supported |
| **Category 6** | Supported | Supported | Supported | Supported (max 55m) |
| **Category 6a** | Supported | Supported | Supported | Supported |

---

### Emerging Trends & Future Evolutions

*   **Higher Speeds:** Infrastructure supporting 25 Gbps, 40 Gbps, and 100 Gbps is actively deployed in Datacenters, MANs, and WANs.
*   **Parallelism Strategy:** Future speed enhancements rely heavily on parallelism, mimicking the CPU industry's shift to multi-core architectures. For example, 40Gbps standards are achieved by aggregating multiple 10Gbps links. DWDM (Dense Wavelength Division Multiplexing) development heavily influenced the 40Gbps tier.
*   **Protocol Supremacy:** Ethernet is expected to permanently replace specialized backend standards such as Fibre Channel and Infiniband due to new features like "lossless Ethernet".
*   **Recommended Reading:** *Speed Matters: How Ethernet Went From 3Mbps to 100Gbps... and Beyond* (Wired, July 2011).

---

### Practical Exercises
*There are no direct math scenarios, terminal commands, or exam-style practical exercises provided in the source document.*