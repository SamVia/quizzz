# Master Cheat Sheet: Spanning Tree Protocol (STP)

## 1. The Core Problem: Loops in Bridged Networks
*   **The Loop Problem**: In meshed networks, frames can enter an infinite loop.
*   **Backward Learning Failure**: Switches may have an inconsistent filtering database because an entry might change ports indefinitely and never reach a stable state.
*   **Broadcast Storms**: Loops generate massive network loads due to broadcast/multicast traffic or frames sent to non-existing stations (which act as unknown unicast).
*   **Lack of TTL**: Unlike Layer 3 networks (which tolerate transient loops using a "time-to-live" field), Layer 2 frames lack a TTL, rendering operators practically impotent unless a physical loop is broken (e.g., unplugging a cable).

---

## 2. Spanning Tree Protocol (STP) Fundamentals
*   **Objective**: To avoid broadcast storms by eliminating loops in the physical network topology.
*   **Standard**: IEEE 802.1D (Original concept by Radia Perlman at DEC).
*   **Mechanism**: Detects meshes and temporarily disables loops by setting specific ports to a forwarding state and others to a blocking state.
*   **Topology**: Creates a single, unique, loop-free path (a tree) between any source and any destination across the entire network.
*   **Optimization Limitation**: Paths are optimized only with respect to the root of the tree, unlike L3 routing where each source calculates its own optimized tree.
*   **Operation Frequency**: Operates periodically (typically every second).

---

## 3. STP Parameters & Identifiers
### Bridge Identifier (Bridge ID)
*   **Size**: 8 bytes.
*   **Components**: 
    *   **Bridge Priority**: 2 bytes. The default value is **32768** to guarantee "plug&play" operation.
    *   **Bridge MAC Address**: 6 bytes. Chosen via vendor-specific algorithms from the MAC addresses associated with the bridge's ports.
*   **Modification**: Priority can be set via management, while the MAC address cannot be modified.

### Port Identifier (Port ID)
*   **Components**:
    *   **Port Priority**: 1 byte. Default value is **128**.
    *   **Port Number**: 1 byte.
*   **Hardware Limit**: Theoretically limits a bridge to no more than 256 ports, though the Port Priority field can be leveraged in practice if needed.

### Root Path Cost
*   **Definition**: The cumulative cost to reach the Root Bridge.
*   **Formula**: $\text{Root Path Cost} = \sum \text{costs of all traversed links}$.

---

## 4. Port Roles & States
### Port Roles
*   **Root Port**: The port on a non-root bridge with the best path toward the Root Bridge. Each bridge has exactly one Root Port. The Root Bridge has zero Root Ports.
*   **Designated Port**: The port on a given link with the best cost toward the Root Bridge. Each link must have exactly one Designated Port to avoid circular paths. The Root Bridge usually has all its ports set to Designated.
*   **Blocked Port**: Ports that are neither Root nor Designated.

### Data Traffic Behavior
*   **Active Ports** (Designated and Root) are responsible for sending and receiving data traffic.
*   **Blocked Ports** never send data on their link and discard all received data frames (they only listen for BPDU configuration messages).

### Port Status Transitions & Security
*   **Disabled**: Port does not participate.
*   **Blocking**: Ignores received packets. Transmits NO data, updates NO filtering DB. Receives and processes BPDUs.
*   **Listening**: BPDUs are sent/received, but the port remains blocked for data forwarding.
*   **Learning**: BPDUs are processed. Begins populating the filtering database with MAC addresses to limit future flooding. Still blocks data forwarding.
*   **Forwarding**: Port fully operational (sends/receives data and BPDUs).

---

## 5. The 4-Step Spanning Tree Algorithm
### Step 1: Root Bridge Election
*   **Rule**: Choose the bridge with the lowest Bridge ID.
*   **Tie-breaker**: Since Priority is checked first, the bridge with the lowest priority wins. If priorities are equal, the lowest MAC address wins.

### Step 2: Root Port Selection (Per Bridge)
*   **Rule**: Calculate the root path cost for all ports on the bridge. The port with the smallest cost becomes the Root Port.
*   **Tie-breakers (in decreasing priority order)**:
    1.  Smallest path cost to the root bridge.
    2.  Smallest Bridge Identifier of the upstream (connected) bridge.
    3.  Smallest Port Identifier of the upstream (connected) port.
    4.  Smallest local Port Identifier.

### Step 3: Designated Port Selection (Per Link)
*   **Rule**: The port on a link with the smallest cost to the Root Bridge becomes the Designated Port ("master" of the link).
*   **Tie-breakers (in decreasing priority order)**:
    1.  Smallest path cost toward the root bridge.
    2.  Smallest Bridge Identifier.
    3.  Smallest Port Identifier.

### Step 4: Blocked Port Enforcement
*   **Rule**: All ports that are neither Root nor Designated are moved into the blocking state.

---

## 6. Bridge Protocol Data Unit (BPDU)
BPDUs are frames used for STP and network reconfiguration.

### Header Structure
*   **MAC Dest.**: `01-80-C2-00-00-00` (Multicast).
*   **MAC Src**: MAC address of the sending bridge (changes at every hop).
*   **DSAP / SSAP**: $0\times42$ / $0\times42$.
*   **Control**: $0\times03$.

### BPDU Payload Fields
*   **Protocol Identifier**: `00-00`.
*   **Version**: `00`.
*   **BPDU Type**: `00` (Configuration BPDU) or `80` (Topology Change Notification BPDU).
*   **Flags**: 2 bits used. Topology Change (TC) and Topology Change Acknowledgement (TCA).
*   **Root Identifier**: Bridge ID of the root bridge.
*   **Root Path Cost**: Cost to reach the root bridge on the path used by the message (sum of costs of all links traversed except the last link).
*   **Bridge Identifier**: ID of the bridge propagating the BPDU.
*   **Port Identifier**: ID of the port forwarding the BPDU.
*   **Message Age**: Incremented by `TransitDelay` (which is $\text{HelloTime}/2$) at each hop. Root Bridge generates with Age = 0. Expiration occurs at Max Age. In units of $1/256$ seconds (~4 ms).
*   **Max Age**: Validity period of a BPDU. In units of $1/256$ seconds.
*   **Hello Time**: Interval between consecutive BPDUs from the root. In units of $1/256$ seconds.
*   **Forward Delay**: Time required to force a port transition (Listening $\rightarrow$ Learning $\rightarrow$ Forwarding). Also defines max duration of filtering database entries during a topology change. In units of $1/256$ seconds.

### BPDU Propagation Rules
*   **Root Bridge**: Generates the BPDU every "hello time" with Age = 0.
*   **Other Bridges**: Only propagate received BPDUs (never generate autonomously).
*   **Root Ports**: Receive the best BPDUs.
*   **Designated Ports**: Inject/propagate the BPDUs onto their links.
*   **Blocked Ports**: Listen to BPDUs but never send them.

---

## 7. STP Dynamic Behavior & Topologies
### Evaluating Incoming BPDUs
*   **If $\text{RootID} < \text{CurrentRootID}$**: Recognizes a better root. Stops own BPDU generation, starts repeating the new BPDU with updated BridgeID, PortID, Root Path Cost (adds incoming link cost), and Message Age.
*   **If $\text{RootID} > \text{CurrentRootID}$**: Ignored.
*   **If $\text{RootPathCost} < \text{CurrentRootPathCost}$**: Port becomes Root Port.
*   **If $\text{RootPathCost} > \text{CurrentRootPathCost}$**: Ignored for Root Port Selection.
*   **If $\text{Priority} < \text{CurrentPriority}$**: Receiving port becomes Blocked.
*   **If $\text{Priority} > \text{CurrentPriority}$**: Ignored for Designated Port Selection (usually from a bridge not yet in the network).

### Timers & Convergence
*   **Hello Time**: Range 1-10s. Default/Recommended: **2s**.
*   **Max Age**: Range 6-40s. Default/Recommended: **20s**.
*   **Forward Delay**: Range 4-30s. Default/Recommended: **15s**.
*   **Total Convergence Time**: $\approx 50\text{ seconds}$ ($\text{MaxAge} + 2 \times \text{ForwardDelay}$).
*   **Max Bridge Diameter**: Default is 7 bridges.

---

## 8. Topology Change Notification (TCN) Process
When a topology change occurs (e.g., a port goes down, or a port moves to forwarding state while a root port exists), the filtering database risks holding invalid paths for its aging time (e.g., 5 minutes), causing black holes.

**The Algorithm:**
1.  **Fault Detection**: A bridge detects a topology change and sends a TCN BPDU (`Type 80`) out its root port toward the Root Bridge.
2.  **Upstream Relays**: The upstream bridge receives the TCN, forwards it out its root port, and sends back an acknowledgment (TCA bit set) to the originating bridge so it stops re-transmitting the TCN.
3.  **Root Bridge Action**: Once the Root Bridge receives the TCN, it generates Configuration BPDUs with the Topology Change (TC) bit set. It does this for $\text{MaxAge} + \text{ForwardDelay}$ seconds (default: $20 + 15 = 35\text{s}$).
4.  **Network Reaction**: When bridges receive a BPDU with the TC flag, they set their filtering database Ageing Time to match the Forward Delay timer (15s). This rapidly purges inactive MAC entries, forcing flooding for unknown MACs to relearn the new topology.

---

## 9. IEEE 802.1t Enhancements
### New Bridge ID Format
Introduced to allow multiple STP instances (e.g., PVST+, MST) in the same physical network (for VLANs).
*   **Bridge Priority field** is partitioned:
    *   **Bridge Priority**: 4 bits (Default 8, Suggested increment 4096).
    *   **STP Instance**: 12 bits (Default 0).
*   **Bridge MAC Address**: 6 bytes (48 bits).

### New Path Costs
Extended to support much faster interface speeds. Range expanded to 1 - 200,000,000.
*   $<= 100\text{ Kb/s}$: 200,000,000
*   $1\text{ Mb/s}$: 20,000,000
*   $10\text{ Mb/s}$: 2,000,000
*   $100\text{ Mb/s}$: 200,000
*   $1\text{ Gb/s}$: 20,000
*   $10\text{ Gb/s}$: 2,000
*   $100\text{ Gb/s}$: 200
*   $1\text{ Tb/s}$: 20
*   $10\text{ Tb/s}$: 2

*(Note: Older 802.1D costs were based on $1000 / \text{Speed in Mb/s}$, e.g., 100 for 10Mb/s, 19 for 100Mb/s).*

---

## 10. Real-World Constraints & Security
*   **Unidirectional Paths**: If the "direct" propagation path breaks (but links stay physically up), a downstream bridge might not receive BPDUs, assume it is Designated, and forward data, creating a loop.
*   **PortFast / Edge Ports**: Disabling STP on edge ports is dangerous. Cisco uses "PortFast" to jump directly to Forwarding state (bypassing Listening/Learning) while still running STP. This stops PCs joining/leaving from constantly triggering TCNs.
*   **BPDU Guard**: Enabled on edge ports. If a BPDU is received, the port immediately enters the "error disable" state. Protects against accidental rogue switches.
*   **BPDU Filter**: Disables sending/receiving BPDUs entirely on a port, typically used between different STP domains (e.g., between two different providers in a data center).

---

## 11. Practical Exercises: Step-by-Step Selection

### Scenario 1: Root Bridge Election
*   **B1**: Priority 32768, MAC 00-08-00-22-33-44
*   **B2**: Priority 28672, MAC 00-08-00-11-22-33
*   **B3**: Priority 32768, MAC 00-08-00-33-44-55
*   **Solution Step 1**: Check Priorities. B2 has the lowest priority (28672 < 32768).
*   **Solution Step 2**: B2 wins and becomes the Root Bridge. If Priorities were all 32768, B2 would still win because `11-22-33` is the lowest MAC.

### Scenario 2: Root Port Selection
*   **Context**: B0 is Root. B1 and B2 connect to B0. B1 connects to B2.
*   **B0 (Root)**: Priority 28672, MAC `33-44-55`. Port ID `128,1` faces B1; Port ID `128,2` faces B2.
*   **B1**: Priority 32768, MAC `11-22-33`. B1 $\rightarrow$ B0 Link Cost = 10.
*   **B2**: Priority 32768, MAC `22-33-44`. B2 $\rightarrow$ B0 Link Cost = 5. B2 $\rightarrow$ B1 Link Cost = 10.
*   **B1's Evaluation**:
    *   Path via B0 direct = 10.
    *   Path via B2 = Cost of B2 direct (5) + Cost of link B1-B2 (10) = 15.
    *   **Result**: B1 selects the port facing B0 directly as its Root Port (Cost 10 < Cost 15).
*   **B2's Evaluation**:
    *   Path via B0 direct = 5.
    *   Path via B1 = Cost of B1 direct (10) + Cost of link B2-B1 (10) = 20.
    *   **Result**: B2 selects the port facing B0 directly as its Root Port (Cost 5 < Cost 20).

### Scenario 3: Designated Port Selection
*   **Context**: B1 and B2 from Scenario 2 share a link. Who dominates this link? Link cost is 1.
*   **B1's Data**: Path cost to root = 10. Bridge ID: `32768, 11-22-33`.
*   **B2's Data**: Path cost to root = 1. Bridge ID: `32768, 22-33-44`. *(Note: In this specific slide variant, B1 path cost is 1 and B2 path cost is 1).*
*   **Tie-Breaker Path**:
    *   **Rule 1 (Cost)**: Both have equal Path Cost to the Root (Cost = 1).
    *   **Rule 2 (Bridge ID)**: Compare Bridge IDs. B1 MAC `11-22-33` < B2 MAC `22-33-44`.
    *   **Result**: B1's port becomes the **Designated Port**. B2's port becomes the **Blocked Port**.

### Scenario 4: Two Bridges and One Hub
*   **Context**: B1 is Root. B2 connects to B1 via a hub. Two links from B2 connect to the identical hub segment.
*   **B1 (Root)**: Port ID 1 is `128,1`. Port ID 2 is `128,2`.
*   **Tie-Breaker Path for B2's Root Port**:
    *   **Rule 1 (Cost)**: Both physical ports on B2 reach the hub, connecting to B1. Cost is equal.
    *   **Rule 2 (Bridge ID)**: Both ports connect to the same upstream bridge (B1). Bridge ID is equal.
    *   **Rule 3 (Port ID)**: B2 examines the *sender's* Port ID. It receives BPDUs from B1's `128,1` and `128,2`.
    *   **Result**: B2 selects its port receiving from B1's `128,1` as the **Root Port** (1 is better than 2). The other port on B2 becomes a **Blocked Port**.

### Key System Parameters & Formulas
*   **Bridge ID ($8$ bytes)**: $\text{Priority (2 bytes)} + \text{MAC Address (6 bytes)}$.
*   **Port ID ($2$ bytes)**: $\text{Priority (1 byte)} + \text{Port Number (1 byte)}$.
*   **Root Path Cost**: The sum of the costs of all traversed links, excluding the final link.
    *   **IEEE 802.1D (1998) Cost**: $\frac{1000}{\text{Speed in Mb/s}}$.
    *   **IEEE 802.1t Cost**: Extended range up to $200,000,000$.



### The Port State Decision Matrix
This table summarizes the port behaviors during transition phases as described in the document:

| Port State | Receives Frames | Processes BPDU | Forwards Frames | Transmits BPDU | Updates Filtering DB |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Disabled** | NO | NO | NO | NO | NO |
| **Blocking** | NO | YES | NO | NO | NO |
| **Listening** | YES | YES | NO | YES | NO |
| **Learning** | YES | YES | NO | YES | YES |
| **Forwarding**| YES | YES | YES | YES | YES |

### The "Tie-Breaker" Algorithm
If a bridge or link has multiple options with equal path costs, the protocol follows this strict priority sequence to reach a deterministic state:
1.  **Smallest Path Cost** to the Root.
2.  **Smallest Bridge ID** (Priority first, then MAC).
3.  **Smallest Remote Port ID** (The ID of the port sending the BPDU).
4.  **Smallest Local Port ID**.



### Final Safety Rules for Implementation
*   **Max Bridge Diameter**: Default is $7$ bridges; timers are optimized for this limit.
*   **Transit Delay**: Defined as $\frac{\text{HelloTime}}{2}$.
*   **Root Placement**: A "Backup Root Bridge" should always be pre-configured by manually adjusting the **Bridge Priority** to the next lowest value.
*   **Security**: Always enable **BPDU Guard** on edge ports to prevent unauthorized home switches from claiming "Root" status and crashing the corporate network.