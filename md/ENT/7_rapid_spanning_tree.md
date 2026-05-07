# Master Cheat Sheet: Rapid Spanning Tree Protocol (RSTP - IEEE 802.1w)

## 1. Introduction and Context
*   **Evolution:** RSTP (IEEE 802.1w, 2001) was developed to provide fast convergence for mission-critical bridged LANs, later incorporated into 802.1D-2004.
*   **Multiple Spanning Tree (MST):** RSTP is often used alongside MST (IEEE 802.1s, 2002), which caters to Metropolitan area networks and allows coexistence of STP and RSTP.
*   **Convergence Speed:** Usually less than 1 second, and in the best cases (e.g., fault detected at the physical layer), convergence can be $\sim 10\text{ms}$.
*   **Hardware Requirements:** All switches must support 802.1w. Links must be point-to-point (twisted pair or fiber) and full duplex. It does not operate optimally on shared mediums or with hubs, although edge hubs are tolerated.

---

## 2. Port States and Roles
RSTP explicitly separates port states (operational behavior regarding frames) from port roles (position within the calculated topology).

### 2.1 Operational Port States
STP's five states are reduced to three in RSTP by merging Disabled, Blocking, and Listening into a single **Discarding** state.

| Port State | Forward Frames? | Learn MACs? | Process/Receive BPDUs? | Transmit BPDUs? | Possible RSTP Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Discarding** | NO | NO | YES | YES | Alternate or Backup |
| **Learning** | NO | YES | YES | YES | On the way to become Root or Designated |
| **Forwarding** | YES | YES | YES | YES | Root, Designated, or Edge |

### 2.2 Port Roles
*   **Root Port:** The optimal path to the Root Bridge (same as STP).
*   **Designated Port:** The active port connecting a LAN segment to the Root Bridge (same as STP).
*   **Alternate Port:** A blocked port providing an alternative path to the Root Bridge. It receives a better BPDU from *another* bridge and serves as a fast replacement if the current Root Port fails. 
*   **Backup Port:** A blocked port providing an alternative path for a specific LAN segment. It receives a better BPDU from the *same* bridge and replaces a Designated Port if it fails. Exists only when a bridge has multiple connections to the same shared LAN.
*   **Edge Port:** Connects strictly to end-stations (no other switches). Requires explicit administrator configuration. Transitions immediately to Forwarding state without a Learning phase. If it receives a BPDU, it reverts to standard RSTP rules for loop protection. Changing an Edge Port's state does not trigger a Topology Change Notification.

---

## 3. BPDU Architecture and Handling
RSTP bridges independently generate BPDUs every Hello Time (default $2\text{ sec}$), acting as a "keep-alive" mechanism, unlike STP where non-root bridges merely relayed the root's BPDU.

### 3.1 802.1w BPDU Format
*   **Version:** Set to 2.
*   **BPDU Type:** Set to 2 (Only configuration BPDUs exist; TCN BPDUs are obsolete).
*   **Flags Byte (8 bits):**
    *   `Bit 0`: Topology Change
    *   `Bit 1`: Proposal
    *   `Bit 2-3`: Port Role ($00 = \text{Unknown}$, $01 = \text{Alternate/Backup}$, $10 = \text{Root}$, $11 = \text{Designated}$)
    *   `Bit 4`: Learning
    *   `Bit 5`: Forwarding
    *   `Bit 6`: Agreement
    *   `Bit 7`: Topology Change ACK

### 3.2 Faster Information Aging
*   If a BPDU is missed for **3 consecutive Hello Times**, the stored BPDU is declared obsolete.
*   The bridge no longer waits for the `MaxAge` timer to expire to detect a failure.

### 3.3 Accepting Inferior BPDUs
*   If a bridge receives an *inferior* BPDU (worse RootID or worse path cost) on its Root Port, it immediately overwrites the stored superior BPDU.
*   **Rationale:** Being received on the Root Port implies the upstream path deteriorated or the Root Bridge failed. This immediately triggers a re-computation of the tree instead of waiting for timeouts.

---

## 4. Rapid Transition and Synchronization
### 4.1 Fast Failover
*   **Root Port Failure:** The best Alternate Port is immediately promoted to Root Port.
*   **Designated Port Failure:** The best Backup Port is immediately promoted to Designated Port.
*   **No Alternate/Backup Available:** The bridge immediately promotes itself as Root and sets all ports to Designated.

### 4.2 The Proposal/Agreement (SYNC) Sequence
When a new point-to-point link goes up, RSTP uses an active handshake to safely put the port into Forwarding state, bypassing standard timers.
1.  A bridge puts a new port into **Designated Discarding** (or Learning) state and sends a BPDU with the **Proposal** bit set.
2.  The downstream neighbor receives the BPDU. If the BPDU contains superior root information, it starts the **SYNC** process.
3.  **SYNC Process:** The downstream bridge blocks all active ports (Root and Designated ports move to Discarding). Edge, Alternate, and Backup ports remain unchanged.
4.  Once synced, the downstream bridge replies with a BPDU with the **Agreement** bit set and updates its port roles.
5.  Upon receiving the Agreement, the upstream bridge immediately moves its port to **Forwarding**.
6.  *Fallback Rule:* If no Agreement is received, the upstream port falls back to traditional 802.1D listening/learning timers.

---

## 5. Topology Changes (TC)
### 5.1 What Constitutes a Topology Change?
*   A link going DOWN is **no longer** considered a TC.
*   Only a non-edge port moving into the **Forwarding** state triggers a TC.

### 5.2 TC Detection and Propagation
1.  **Detection:** A bridge detecting a TC starts the **TC While timer** ($2 * \text{Hello Time}$) for all its non-edge active ports, flushes MAC addresses on those ports, and floods BPDUs with the TC bit set.
2.  **Propagation:** A neighbor receiving a TC BPDU starts its own **TC While timer** on all Designated and Root ports *except* the port where the TC was received.
3.  **Flushing:** The neighbor clears MAC addresses on all ports running the timer. It does *not* clear MACs on the port that received the TC BPDU because those hosts are still valid on that path. 
4.  **Edge Ports:** Edge ports neither trigger TCs nor flush their MACs during a TC. If an end-user moves between edge ports, it must send a broadcast frame to update the filtering database.

---

## 6. Hardware & Architecture Limits
### 6.1 Default Path Costs (802.1t Standardized)
| Port speed | Recommended Value | Recommended Range |
| :--- | :--- | :--- |
| $\le 100\text{ Kb/s}$ | $200,000,000$ | $20,000,000 - 200,000,000$ |
| $1\text{ Mb/s}$ | $20,000,000$ | $2,000,000 - 20,000,000$ |
| $10\text{ Mb/s}$ | $2,000,000$ | $200,000 - 2,000,000$ |
| $100\text{ Mb/s}$ | $200,000$ | $20,000 - 200,000$ |
| $1\text{ Gb/s}$ | $20,000$ | $2,000 - 20,000$ |
| $10\text{ Gb/s}$ | $2,000$ | $200 - 20,000$ |
| $100\text{ Gb/s}$ | $200$ | $20 - 2,000$ |
| $1\text{ Tb/s}$ | $20$ | $2 - 200$ |
| $10\text{ Tb/s}$ | $2$ | $1 - 20$ |

### 6.2 Legacy STP (802.1D) Compatibility
*   **Migration Delay Timer:** When an RSTP port receives a legacy 802.1D BPDU (Version 0), it locks itself into STP compatibility mode. A $3\text{ sec}$ Migration Delay Timer starts, during which the mode is locked. 
*   **Per-Port Scope:** Operation mode is defined on a per-port basis.
*   **Risks & Instability:** 
    *   Fast convergence is entirely lost on links operating in 802.1D mode.
    *   Because 802.1D BPDUs only flow downstream, an RSTP bridge locked in STP mode facing a legacy switch has no way to revert to 802.1w mode automatically if the legacy switch dies (requires manual intervention).
    *   Mixing modes can cause out-of-sequence packets, packet duplication, and transient loops.
*   **Link Flapping Risk:** Rapid reactions to unstable physical links (flapping) can keep the network in constant transient states. Recommended mitigation is using proprietary "anti-flapping" limits (e.g., Cisco's "error disable") requiring manual restart.

---

## 7. Practical Exercises
### Scenario 1: Proposal/Agreement Cascade (Network Convergence)
**Context:** Root Bridge (RB) is connected to Bridge 1 (B1), which branches to B2 and B3. B3 connects to B4. B4 also connects to RB via a secondary path with Cost 3. A new direct link is added between RB and B1.
**Step-by-Step Solution:**
1.  **Link Initialization:** RB and B1 set the new link's ports to *Designated Discarding*.
2.  **Initial Proposal:** RB sends a BPDU with the Proposal flag to B1.
3.  **Sync on B1:** B1 receives the superior BPDU and must sync. B1 blocks its downstream ports toward B2 and B3.
4.  **B1 Agreement:** B1 sends an Agreement BPDU to RB. RB immediately moves its port to Forwarding. B1's upstream port is now Forwarding (Root Port).
5.  **Cascade to B2 & B3:** B1 sends Proposal BPDUs down to B2 and B3. B2 and B3 put their downstream ports into SYNC state. B2 and B3 send Agreements to B1, allowing B1 to move its downstream ports to Forwarding. 
6.  **Edge Case at B4:** B3 sends a Proposal down to B4. However, B4 has a better alternate path to the Root Bridge (via the Cost 3 link). Therefore, B4 *rejects* B3's proposal and replies with its own superior Proposal BPDU. B4 performs no SYNC because its port roles don't change. B3 acknowledges B4's proposal, and B4 puts its port facing B3 into the *Alternate* state.

### Scenario 2: Topology Change MAC Flushing
**Context:** Bridge 1 (B1) connects to B2 and B3. B3 connects to Host 1 (H1). The network experiences a change where the primary link connecting the root moves, forcing B1 to use a new Root Port. H1 was previously reachable via B1's Port 1.
**Step-by-Step Solution:**
1.  **TC Received:** B1 receives a BPDU with the TC bit set on Port 2.
2.  **Action on Receiving Port:** B1 does *not* clear the MAC addresses learned on Port 2, because downstream hosts on that port are still valid.
3.  **Action on Other Ports:** B1 clears the MAC database for all *other* active ports (e.g., Port 1 and Port 3) and starts the TC While timer.
4.  **Stale Entry Removed:** The stale MAC entry for H1 on Port 1 is successfully purged, preventing traffic from being blackholed.