## WiFi for Enterprise Networking: Master Cheat Sheet

This master cheat sheet is based on the expert lecture by **Claudio Casetti** from **Politecnico di Torino**.

---

## 1. Introduction to IEEE 802.11 and WiFi
*   **IEEE 802.11**: A family of standards covering Wireless Local Area Network (WLAN) technology, specifically the **Physical (PHY)** layer, **MAC** layer, device interconnection, and security.
*   **WiFi**: A certification of interoperability and standard compliance released by the **WiFi Alliance**.
*   **Standard Scope**: Specifies the wireless interface between a client and a **base station (Access Point - AP)** and between wireless clients.
*   **Protocol Stack**:
    *   **Layer 2 (Data Link)**: Split into **Logical Link Control (LLC)** (defined in 802.2) and **Medium Access Control (MAC)**.
    *   **Layer 1 (Physical)**: **PHY** layer.

### 1.1 The 802.11 Standards Family
| Standard | Key Features | Date |
| :--- | :--- | :--- |
| **802.11** | Original 1-2 Mbit/s, 2.4 GHz RF and IR | 1999 |
| **802.11a** | 54 Mbit/s, 5 GHz | 1999 |
| **802.11b** | Enhancements for 5.5 and 11 Mbit/s | 1999 |
| **802.11e** | **QoS** and packet bursting enhancements | 2005 |
| **802.11g** | 54 Mbit/s, 2.4 GHz (backwards compatible with b) | 2003 |
| **802.11n** | **WiFi 4**: High-speed WLAN (up to 600 Mb/s) | 2009 |
| **802.11ac** | **WiFi 5**: High-speed (up to 7 Gb/s), 5 GHz only | 2014 |
| **802.11ax** | **WiFi 6**: High-efficiency, 2.4/5/6 GHz | 2021 |
| **802.11be** | **WiFi 7**: Extremely High Throughput (up to 46 Gb/s) | 2024 |

---

## 2. WLAN Architecture and Association
*   **Basic Service Set (BSS)**: Also known as a **"cell"**.
    *   **Infrastructure Mode**: Contains wireless hosts and one **Access Point (AP)**.
    *   **Ad Hoc Mode**: Contains wireless hosts only.
*   **Channels**: Spectrum is divided into channels at different frequencies; AP admins choose frequencies to minimize interference from neighbors.
*   **Scanning Methods**:
    *   **Passive Scanning**:
        1. APs send **Beacon frames**.
        2. Host (H1) sends **Association Request** to selected AP.
        3. AP sends **Association Response**.
    *   **Active Scanning**:
        1. Host (H1) broadcasts **Probe Request**.
        2. APs send **Probe Response** frames.
        3. Host sends **Association Request** to selected AP.
        4. AP sends **Association Response**.

---

## 3. Wireless Communication Principles

### 3.1 Fundamental Definitions
*   **Signal Spectrum**: The set of frequencies composing a signal $x(t)$.
*   **Bandwidth ($B$)**: Width of the transmitted signal spectrum.
*   **Transmission Rate ($R_b$)**: Rate of information transmission (e.g., bit/s).
*   **Symbol Time**: Time needed to transmit a single symbol (e.g., a bit).
*   **Energy per bit ($E_b$)**: Transmitted energy per bit.
*   **Transmit Power**: $P_t = E_b R_b$.
*   **Noise ($N_0$)**: Noise power density on the channel.

### 3.2 Modulation
Modulation controls parameters of a carrier sinusoid: $A \sin(\omega t + \phi) = A \sin(2\pi ft + \phi)$.
*   **Digital Modulation Types**:
    *   **Amplitude Shift Keying (ASK)**: $A(t)\sin(\omega t + \phi)$.
    *   **Frequency Shift Keying (FSK)**: $A \sin(2\pi f(t)t + \phi)$.
    *   **Phase Shift Keying (PSK)**: $A \sin(\omega t + \phi(t))$.
*   **Multi-level Modulation**:
    *   **QAM (Quadrature-Amplitude Modulation)**: Sum of two AM sinusoids $90^\circ$ out of phase.
    *   **Capacity**: Higher-order modulations (e.g., 256-QAM) carry more bits per waveform but require better **Signal-to-Noise Ratio (SNR)**.

### 3.3 Orthogonal Frequency Division Multiplexing (OFDM)
*   Signal organized into **OFDM symbols** (e.g., $4\mu s$ in WiFi) spread over $N$ sub-carriers.
*   **Bits per OFDM symbol formula**: $N \log_2(M)$, where $M$ is the modulation level (e.g., $M=16$ for 16-QAM).
*   **Example**: 802.11a/g uses 48 subcarriers in a 20MHz channel.

---

## 4. Radio Propagation and Path Loss

### 4.1 Power in Decibels
*   **Relative Power (dB)**: $dB = 10 \log(\frac{P_1}{P_2})$.
*   **Absolute Power (dBm)**: $dBm = 10 \log(\frac{P_1}{1\text{ mW}})$.
    *   10 W = 40 dBm; 1 mW = 0 dBm; $1\mu W$ = -30 dBm.

### 4.2 Free Space Propagation (Friis Equation)
$$P_R = \frac{P_T G_T G_R}{(4\pi R / \lambda)^2}$$
*   **Path Loss ($L$)**: $L = \frac{P_T}{P_R} = \frac{(4\pi R)^2}{G_T G_R} (\frac{f}{c})^2$.
*   **Observations**: $P_R$ decreases quadratically with distance $R$ and increases with the square of frequency $f$.

### 4.3 Real-World Attenuation
*   **Shadowing (Slow Fading)**: Slow variation due to large obstacles.
*   **Multipath (Fast Fading)**: Fast variation due to signals reaching the receiver via different paths with different delays/phases.
*   **Interference**:
    *   **Constructive**: Phase difference $\Delta D = \lambda$.
    *   **Destructive**: Phase difference $\Delta D = \frac{\lambda}{2}$.

### 4.4 Link Quality Metrics
*   **SNR**: $SNR = \frac{P_{rx}}{N_0 B}$.
*   **SINR (Multiple TX-RX)**: $SINR = \frac{P_{rx}}{I + N_0 B}$, where $I$ is interference power.
*   **In practice**: $SNR|_{dB} = RSSI|_{dBm} - Noise|_{dBm}$.

---

## 5. 802.11 Physical Layer (PHY) Details

### 5.1 Frequency Bands (ISM)
*   **2.4 GHz Band**: 2.4-2.485 GHz. Divided into 14 channels (5 MHz spacing). Channels **1, 6, 11** are non-overlapping (25 MHz spacing).
*   **5 GHz Band**: 5.15-5.725 GHz. More than 20 independent 20-MHz channels. Supports channel aggregation (up to 160 MHz).
*   **6 GHz Band**: Used by 802.11ax/be.

### 5.2 Advanced PHY Capabilities
*   **Rate Adaptation**: Dynamically change modulation/rate as SNR varies.
*   **MIMO (Multiple Input Multiple Output)**: Uses multiple antennas to increase capacity (Spatial Multiplexing) or reduce errors (Diversity).
*   **Beamforming**: Requires **Null Data Packets (NDP)** for channel sounding to establish preferred transmission directions.

---

## 6. 802.11 Medium Access Control (MAC) Layer

### 6.1 Distributed Coordination Function (DCF)
Uses **CSMA-CA (Collision Avoidance)**. Stations are half-duplex.
*   **Time Slots**: System unit time (e.g., $9\mu s$ in 802.11ac).
*   **InterFrame Spaces (IFS)** (Priority order: Shortest = Highest Priority):
    1.  **SIFS**: Short IFS (e.g., $16\mu s$ for 11ac). Separates frames in the same dialogue (Data-ACK).
    2.  **PIFS**: Point Coordination IFS.
    3.  **DIFS**: Distributed IFS. $DIFS = SIFS + 2 \times slots$.
    4.  **EIFS**: Extended IFS. Used after a reception error.

### 6.2 DCF Operation Rules
1.  **Rule #1**: If channel is idle for DIFS/EIFS, transmit immediately.
2.  **Rule #2**: If channel is busy, wait for idle DIFS, then execute **Exponential Backoff**.
*   **Backoff Procedure**:
    *   Select random integer in $[0, CW]$.
    *   $CW_{min}=15$, $CW_{max}=1023$. $CW$ doubles after each failure and resets after success.
    *   Counter decrements while idle, freezes when busy.
*   **Virtual Carrier Sensing**: Uses the **Network Allocation Vector (NAV)**. Stations read the duration field in headers to know how long the channel will be busy.

### 6.3 DCF with Handshaking (RTS/CTS)
Used to solve the **Hidden Terminal Effect**.
1.  **RTS (Request to Send)**: 20 bytes. Neighbors set NAV.
2.  **CTS (Clear to Send)**: 14 bytes. Sent after SIFS.
3.  **Data**: Transmitted after receiving CTS.
4.  **ACK**: Final acknowledgement.

### 6.4 Frame Format
*   **Preamble**: Sync (80 bits) + Start Frame Delimiter (16 bits).
*   **PLCP Header**: Includes Length and modulation/coding rate. Always sent at the **Basic Rate** (slowest) so all stations can hear it.
*   **MAC Addresses**:
    *   **Address 1**: Receiver MAC.
    *   **Address 2**: Transmitter MAC.
    *   **Address 3**: Router interface MAC.
    *   **Address 4**: Used in ad-hoc mode only.

---

## 7. Practical Exercises: Math & Scenarios

### 7.1 SNR Calculation
**Scenario**: $RSSI = -55\text{ dBm}$, $Noise = -93\text{ dBm}$. Find $SNR$.
**Solution**:
1.  $SNR|_{dB} = RSSI|_{dBm} - Noise|_{dBm}$
2.  $SNR = -55 - (-93) = 38\text{ dB}$.

### 7.2 Path Loss in Free Space
**Formula**: $L = \frac{(4\pi R)^2}{G_T G_R} (\frac{f}{c})^2$
**Example**: If frequency $f$ doubles while distance $R$ remains constant:
1.  $L_{new} \propto (2f)^2 = 4f^2$
2.  Attenuation increases by a factor of 4 (or $+6\text{ dB}$).

### 7.3 Throughput vs. Data Rate
**Scenario**: Calculate bits per OFDM symbol for 64-QAM ($M=64$) with 48 subcarriers ($N=48$).
**Solution**:
1.  Determine bits per subcarrier: $\log_2(64) = 6\text{ bits}$.
2.  Total bits: $48 \times 6 = 288\text{ bits per symbol}$.

### 7.4 DCF Timing Calculation
**Scenario**: Calculate DIFS for 802.11ac where $SIFS = 16\mu s$ and $Slot = 9\mu s$.
**Solution**:
1.  $DIFS = SIFS + 2 \times Slot$
2.  $DIFS = 16 + 2(9) = 16 + 18 = 34\mu s$.

---

## 8. Hardware & Architecture Specifics

### 8.1 Critical System Timings
These exact values are defined by the physical layer implementation and are mandatory for synchronization:

| Parameter | 802.11b (2.4 GHz) | 802.11ac (5 GHz) |
| :--- | :--- | :--- |
| **Slot Time** | $20\ \mu s$ (5 $\mu s$ turnaround + 15 $\mu s$ detection) | $9\ \mu s$ |
| **SIFS** | $10\ \mu s$ | $16\ \mu s$ |
| **DIFS** | $50\ \mu s$ | $34\ \mu s$ |

### 8.2 MAC Frame Field Sizes (Strict)
*   **Frame Control**: 2 bytes
*   **Duration/ID**: 2 bytes
*   **Addresses (1-4)**: 6 bytes each
*   **Sequence Control**: 2 bytes
*   **Payload**: 0 - 2312 bytes
*   **CRC**: 4 bytes

### 8.3 Control Frame Handshaking Sizes
*   **RTS (Request to Send)**: 20 bytes
*   **CTS (Clear to Send)**: 14 bytes
*   **ACK**: 14 bytes (Logic: CTS size = ACK size)

---

## 9. Advanced Technology Evolution

### 9.1 Multi-User MIMO (MU-MIMO) & Beamforming

*   **NDP (Null Data Packet)**: Used for "channel sounding" to establish the preferred transmission direction.
*   **Group Addressing**: 802.11ac VHT (Very High Throughput) frames use a common signal field for all users and a dedicated signal field for individual user modulations.
*   **Uplink Rule**: While multi-user frames can be sent to multiple receivers simultaneously (Downlink), acknowledgements must be transmitted **individually** in the uplink direction.

### 9.2 OFDMA (WiFi 6/802.11ax)

*   **Resource Unit (RU)**: The basic building block, consisting of one OFDM subcarrier in a $12.8\ \mu s$ interval.
*   **Allocation**: RUs are either allocated directly by the AP or accessed randomly by stations via contention.

### 9.3 Target Wake Time (TWT)
*   **Goal**: Minimize contention and maximize battery life for IoT devices.
*   **Mechanism**: The AP negotiates scheduled intervals (multiples of beacon intervals) for devices to wake up, allowing them to operate at non-overlapping times/frequencies.

---

## 10. Comparative Master Table: 11n vs 11ac vs 11ax vs 11be

| Feature | 802.11n (WiFi 4) | 802.11ac (WiFi 5) | 802.11ax (WiFi 6) | 802.11be (WiFi 7) |
| :--- | :--- | :--- | :--- | :--- |
| **Bands** | 2.4 & 5 GHz | 5 GHz only | 2.4, 5, 6 GHz | 2.4, 5, 6 GHz |
| **Max Bandwidth**| 40 MHz | 160 MHz | 160 MHz | **320 MHz** |
| **Max Modulation**| 64-QAM | 256-QAM | 1024-QAM | **4096-QAM** |
| **MIMO (AP)** | $4 \times 4$ | $8 \times 8$ | $8 \times 8$ | **$16 \times 16$** |
| **Access Method** | Single-user | Multi-user | **OFDMA** | OFDMA + Enhancements |

---

## 11. Practical Exercises: Multi-User Scenarios

**Scenario: Throughput Calculation with Multi-Stream MIMO**
If a 802.11be (WiFi 7) system uses 4096-QAM and a $16 \times 16$ MIMO configuration:
1.  **Modulation Bits**: $\log_2(4096) = 12$ bits per symbol per subcarrier.
2.  **Spatial Streams**: 16 independent streams are sent simultaneously.
3.  **Result**: The theoretical peak rate is exactly **2 times** that of 802.11ax (which uses $8 \times 8$) and roughly **20% higher** per stream due to the move from 1024-QAM to 4096-QAM.

**Scenario: Hidden Terminal Collision Avoidance**
Station A and Station B are hidden from each other but associated with the same AP.
*   **Step 1**: Station A sends an **RTS** specifying duration $T$.
*   **Step 2**: The AP broadcasts a **CTS** specifying duration $T - (\text{SIFS} + \text{CTS\_time})$.
*   **Step 3**: Station B, though it couldn't hear A's RTS, **must** hear the AP's CTS and sets its **NAV** accordingly, preventing it from colliding with A's subsequent data transmission.


## 802.11 Quality of Service (QoS)

### Per-packet Fairness and the Anomaly Effect in 802.11
*   CSMA/CA inherently provides **per-packet fairness**.
*   Per-packet fairness means that if two adjacent senders (within each other's radio range) continuously attempt to transmit packets, they will both send the same number of packets in the long run.
*   If stations continuously attempt to send packets of the same size but at different rates, per-packet fairness implies they will achieve the same throughput, which can lead to significant inefficiency known as the **"802.11 anomaly effect"**.

#### Practical Exercise: Throughput Computation and The Anomaly Effect
**Scenario 1: Two Slow Sources**
*   Assume two slow sources with a rate of $r=1~Mb/s$.
*   Both have packets of length (L) constantly ready to transmit and are in radio range.
*   **Approximate throughput computation for a Slow source:**
    $$\frac{L/1}{L/1+L/1}*0.7*1~Mb/s=0.35~Mb/s$$

**Scenario 2: Two Fast Sources**
*   Assume two fast sources with a rate of $R=11~Mb/s$.
*   Both have packets of length (L) constantly ready to transmit and are in radio range.
*   **Approximate throughput computation for a Fast source:**
    $$\frac{L/11}{L/11+L/11}*0.7*11~Mb/s=3.85~Mb/s$$

**Scenario 3: The Anomaly Effect (One Fast, One Slow Source)**
*   Assume one fast source ($R=11~Mb/s$) and one slow source ($r=1~Mb/s$).
*   Both have packets of length (L) constantly ready to transmit and are in radio range.
*   **Approximate throughput computation for the Slow source:**
    $$\frac{L/1}{L/11+L/1}*0.7*1~Mb/s=0.64~Mb/s$$
*   **Approximate throughput computation for the Fast source:**
    $$\frac{L/11}{L/11+L/1}*0.7*11~Mb/s=0.64~Mb/s$$
*   **Conclusion:** Both stations achieve the same throughput, but it is drastically lowered for the fast station, showcasing the inefficiency of the anomaly effect.

### Downlink/Uplink Unfairness
*   An Access Point (AP) sending data to all stations (STAs) handles multiple flows but only utilizes one CSMA/CA instance.
*   Conversely, an individual STA has only one data flow (towards the AP) and one CSMA/CA instance.

---

## The 802.11e Amendment (IEEE 802.11e-2005)
*   This amendment was incorporated into the published 802.11-2007 standard.
*   It introduced the **Hybrid Coordination Function (HCF)**, which features 2 modes:
    *   **EDCA** (Enhanced Distributed Channel Access).
    *   **HCCA** (HCF Controlled Channel Access).
*   It cooperates with non-QoS devices.
*   **nQSTA:** Regular stations that utilize only DCF (Distributed Coordination Function) and optionally PCF (Point Coordination Function).
*   **QSTA:** QoS-enabled stations where both DCF and HCF are present.

### Enhancements of 802.11e
*   **Contention Free Bursts (CFB):** Allows stations to transmit multiple frames in a row without contention if the allocated Transmission Opportunity (TXOP) permits.
*   **Block Ack (optional):** Improves channel efficiency by transmitting a block of data frames separated by a SIFS period and aggregating several acknowledgements into ONE frame.
*   **No Ack Policy:** Used for applications where strict delay requirements make retransmission useless. There is no MAC-level recovery, reducing reliability. A protective mechanism (like RTS/CTS) should be used to reduce collisions during the TXOP.
*   **Direct Link Setup (DLS):** Enables direct communication between STAs without the AP's involvement.

### 802.11e MAC Architecture
*   **Distributed Coordination Function (DCF):** The basis for PCF, HCF, and MCF, used for contention services.
*   **Point Coordination Function (PCF):** Required for contention-free services for non-QoS STA (optional otherwise).
*   **HCF Controlled Access (HCCA):** Required for parameterized QoS services.
*   **HCF/MCF Contention Access (EDCA):** Required for prioritized QoS services.
*   **MCF Controlled Access (MCCA):** Required for controlled mesh services.

### Enhanced Distributed Channel Access (EDCA)
*   EDCA divides traffic into 8 User Priorities (UP, identical to 802.1D) or Traffic Categories (TC), mapped onto 4 **Access Categories (AC)**.
*   Access for each AC is controlled using 4 parameters:
    1.  **Transmission Opportunity (TXOP):** Defines the starting time and maximum duration a station can transmit 1+ frames.
    2.  **Arbitration Interframe Space (AIFS):** A variable DIFS replacing the standard minimum idle duration time.
    3.  **Minimum contention window size:** $(aCWmin)$.
    4.  **Maximum contention window size:** $(aCWmax)$.

#### Arbitration Inter-Frame Space (AIFS) Formulas and Rules
*   QSTAs use AIFS to transmit all data and management frames.
*   A QSTA obtains a TXOP if the medium is sensed idle at the $AIFS[AC]$ slot boundary (after correctly receiving a frame) and the AC's backoff time has expired.
*   **AIFSN (AIFS Number):** The number of slots after a SIFS that a non-AP QSTA must defer before invoking a backoff or starting transmission.
*   **Formula for AIFS:**
    $$AIFS[AC]=AIFSN[AC]\times aSlotTime+aSIFSTime$$

#### Default EDCA Parameter Set
| AC | CWmin | CWmax | AIFSN | TXOP Limit (Clause 15/DSSS) | TXOP Limit (Clause 17/OFDM) | TXOP Limit (Other) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AC_BK** (Background) | $aCWmin$ | $aCWmax$ | 7 | 0 | 0 | 0 |
| **AC_BE** (Best Effort) | $aCWmin$ | $aCWmax$ | 3 | 0 | 0 | 0 |
| **AC_VI** (Video) | $(aCWmin+1)/2-1$ | $aCWmin$ | 2 | 6.016 ms | 3.008 ms | 0 |
| **AC_VO** (Voice) | $(aCWmin+1)/4-1$ | $(aCWmin+1)/2-1$ | 2 | 3.264 ms | 1.504 ms | 0 |
*All data directly sourced from.*

#### Scheduling the AC Queues
*   Data $(MSDU, UP)$ is mapped to an Access Category and placed in transmit queues.
*   **Internal collision resolution:** If an AP has varying traffic (VoIP, video, background), the per-queue EDCA functions compete. The high-priority AC wins the transmission right; lower-priority ACs back off as if they experienced a physical collision. Highest priority traffic statistically wins.

#### Parameter Recommendations per Application
*   **VoIP/Gaming:** Short AIFS, low CWmin for quick access (Packet every 10-20 ms).
*   **Video:** Large TXOP for bursts from I-frames (Packet bursts every 40-50 ms).
*   **TCP:** Low AIFS and CW to minimize TCP-ACK RTT and avoid TCP congestion control.
*   **Best-effort/Background:** Values larger than the above categories.

---

## Design Principles and Deployment

### Site Surveying (Offsite vs. Onsite)
*   Surveys are necessary to evaluate coverage areas prior to deployment.
*   **Offsite surveys entail:** Map/scale of the area, building materials, line of business, and client types. This helps approximate the required number of APs.

#### Object Attenuation Table
| Object in Signal Path | Signal Attenuation |
| :--- | :--- |
| Office window | 1-3 dB |
| Plasterboard wall | 3 dB |
| Cinderblock wall | 4 dB |
| Phone and body position | 3-6 dB |
| Glass wall with metal frame | 6 dB |
| Metal door | 6 dB |
| Brick wall | 8 dB |
| Concrete wall | 12 dB |
| Phone near field absorption | Up to 15 dB |
*All data directly sourced from.*

### Deployment Models
*   Driven by client hardware, device density, and running applications.

#### Data Deployment Model
*   Applications like email, web browsing, social media, and file transfers lack specific service-level expectations.
*   The primary factor is the **minimum data rate supported by each AP**.
*   Lower data rates cover greater distances.
*   Higher minimum data rates require a higher density of APs, reducing the number of clients per AP, and mitigating the anomaly effect.
*   **Cell boundary rules:** The minimum data rate dictates cell size. Beyond a cell boundary where the signal is intelligible, fast, and has low retries, a client should be able to reach another AP.

#### Transmit Power and Receiver Sensitivity
*   Cell size depends on AP transmit power and receiver sensitivity.
*   **Effective Isotropic Radiated Power (EIRP):** The total energy radiated out of the AP antennas on a particular channel.
*   **EIRP Formula:**
    $$EIRP=Tx~power(dBm)+antenna~gain(dBi)-cable~loss(dB)$$
*   **ETSI Rules:**
    *   **2.4GHz band:** Max EIRP is 20 dBm (indoors/outdoors), with a max Tx power of 17 dBm using a 3 dBi antenna.
    *   **5GHz band:** Between 20dBm and 23dBm depending on sub-bands and indoor/outdoor usage.
*   **Receiver Sensitivity:** The threshold dividing intelligible from unintelligible signals. A common cell boundary is -67 dBm, highly dependent on the noise floor and resulting SNR (Signal-to-Noise Ratio).

#### Sensitivity and SNR Table (802.11ac VHT 20MHz Channel)
| Data Rate | MCS | Receive Sensitivity | Minimum SNR |
| :--- | :--- | :--- | :--- |
| 6.5Mbps | MCS0 | -93 dBm | 7 dB |
| 13Mbps | MCS1 | -90 dBm | 10 dB |
| 19.5Mbps | MCS2 | -87 dBm | 13 dB |
| 26Mbps | MCS3 | -84 dBm | 16 dB |
| 39Mbps | MCS4 | -81 dBm | 19 dB |
| 52Mbps | MCS5 | -76 dBm | 24 dB |
| 58.5Mbps | MCS6 | -75 dBm | 25 dB |
| 65Mbps | MCS7 | -74 dBm | 26 dB |
| 78Mbps | MCS8 | -70 dBm | 30 dB |
*All data directly sourced from.*

#### Voice/Video Deployment Model
*   Real-time apps must minimize Latency, Jitter, and Packet loss. Bandwidth is required but less stringent.
*   **Voice Requirements:** Bandwidth $64~kb/s$, Latency < 150ms, Jitter < 30ms, Frame Loss 1%, MOS (Mean Opinion Score) = 4.1.
*   **Video Camera Requirements:** Bandwidth $1.5~Mb/s$, Latency < 150ms, Jitter < 30ms, Frame Loss 5%.

#### Practical Exercise: Determining the Minimum RSSI for Voice Calls
*   **Goal:** Calculate the modulation required to maintain Voice QoS boundaries.
*   **Step 1:** Assume a 64-bit frame size.
*   **Step 2:** To achieve a 1% frame loss (0.99 success probability requirement for voice), reference the transfer probability charts to determine a needed bit error rate (BER) of 3.2E-5.
*   **Step 3:** Assume the cell uses a minimum rate of $24~Mb/s$. This speed requires a modulation of 4-QAM or above.
*   **Step 4:** At the cell boundary, measure the values. Assuming RSSI = -67 dBm and a noise floor of -83 dBm, calculate SNR:
    $$SNR = 16~dBm$$
*   **Step 5:** Cross-reference the 16 dBm SNR line with the target BER of 3.2E-5 on a modulation chart.
*   **Conclusion:** 256-QAM and 64-QAM will not work at this threshold. 16-QAM intercepts the line perfectly to achieve the basic rate and successfully support the voice call MOS.

### Industry-Specific Deployment Models
*   **Enterprise Office:** High density of APs set to low power, utilizing directional antennas for bleeding coverage in open spaces.
*   **Hospitals:** Complex 3D environments (multi-story). Features lead-lined rooms (trauma/X-ray) that stop RF signals. Must support a wide mix of legacy ($802.11b/g$) and modern devices.
*   **Hotels:** Guest WiFi often rated as the top service. Needs WLANs for inventory/staff alongside high-compatibility, low-friction guest networks with limited security.

---

## Connecting to the Backhaul & Wireless Network Control

### The Wireless LAN Controller (WLC)
*   In Enterprise networks, APs perform only real-time 802.11 operations.
*   The WLC acts as a central hub for configuring, monitoring, and optimizing performance.
*   **Tasks:** Centralized Management, Load Balancing/Traffic Management, Security Enforcement (Authentication, Rogue AP detection), Monitoring, and Roaming Support.

### CAPWAP Protocol (RFC 5415)
*   **Control And Provisioning of Wireless Access Points** binds an AP with a WLC by encapsulating traffic in a virtual CAPWAP tunnel. Standardized from Cisco's proprietary LWAPP.
*   **Benefits:** Centralized control, cross-vendor interoperability, improved security, simplified management.
*   **Architecture:**
    *   **Data Plane:** Forwards data packets via UDP port 5247.
    *   **Control Plane:** Configures/manages APs via UDP port 5246.
*   **Workflow States:** AP Boots Up -> Discovery -> DTLS Setup -> Join -> Config -> Image Data -> Run -> Reset.

### Network Provisioning Factors
*   Modern APs have massive bandwidth requirements ($802.11ac$ single AP max theoretical ~1.3Gbps; $802.11ax$ > 10Gbps).
*   The CAPWAP channel relies directly on physical infrastructure limits:
    *   Oversubscription of the access switch uplink.
    *   Backbone capacity of the core network.
    *   Network access speeds to the controller.
    *   Performance capabilities of the WLC.

---

## Client Mobility Design (Roaming)

### Client Roaming Principle
*   As a client moves away from AP-1, RF conditions degrade.
*   The client discovers AP-2's better signal and sends an 802.11 reassociation frame.
*   Upon successful reassociation, AP-1 tears down the old association and relays any unsent data to AP-2 over the wired network.

### Roaming Archetypes
1.  **Autonomous APs:** No backend mechanism. The client must request a new IP address from a DHCP server when crossing subnets. Highly disruptive.
2.  **Intra-Controller (Layer 2) Roaming:** The client moves between APs managed by the *same* WLC. The WLC updates its internal association table. The SSID, security, and IP subnet remain consistent. No DHCP exchange is needed.
3.  **Inter-Controller (Layer 2) Roaming:** The client moves between APs on *different* WLCs, but both offer the exact same IP Subnet. The client keeps its IP. No DHCP exchange is needed.
4.  **Inter-Controller (Layer 3) Roaming:** The client moves between APs on different WLCs offering *different* IP subnets.
    *   **Anchor Controller (WLC-1):** Provides the initial IP address (POP).
    *   **Foreign Controller (WLC-2):** Takes over management of the AP the client roamed to (POA).
    *   The Foreign WLC builds an *additional* CAPWAP tunnel back to the Anchor WLC.
    *   The client is marked as a "visitor" and retains its original IP address (e.g., 192.168.100.88), even though it is physically in a new subnet space (e.g., 192.168.200.0/24).

### Mobility Operations
*   Controllers must be grouped into **mobility groups** to support seamless roaming.
*   WLCs track group members by MAC address, management IP address, and mobility group name.
*   **Intra-controller:** WLC sends a "Mobility Announce" message to all group members.
*   **Inter-controller:** Controllers coordinate handoffs via Mobile Anchor Handshakes and Mobile Handoffs.

### Other 802.11 Standards Supporting Mobility
*   **802.11k:** Provides nearby AP lists. Reduces scan time *before* roaming.
*   **802.11v:** Recommends clients to roam to a better AP. Allows configuration while connected.
*   **802.11r (Fast Transition / FT):** Allows fast roaming to a better AP via pre-authentication. Reduces authentication time *during* roaming.

---

## Case Study: Polito WiFi
*   In production since 2004.
*   Supported protocols: $802.11a/g/n/ac/ax$.
*   SSIDs: `polito`, `eduroam`.
*   **Hardware (Current):** Cisco Aironet 3700i (Dual-band, WiFi 5, 4 omni antennas, max speed 600Mbps at 20/40MHz, MIMO $4\times4$).
*   **Hardware (Planned):** Cisco Catalyst 9166D1 (Triple-band, WiFi 6/6E, 4 directional antennas, integrated air quality/power monitoring).
*   **Controllers:** Dual Cisco Catalyst 5520s in Active/Hot-Standby (Supports 1500 APs, 20 Gb/s throughput, 20k clients). Synchronizes config, firmware, DB, internal DHCP, timers, and CAC statistics. Planned migration to Cisco Catalyst 9800-40 (double capacity).
*   **Mobility Configuration:** Cisco Unified Wireless Network (CUWN) architecture using 802.11r Fast BSS Transition via Over-the-Distribution System (OtDS). 802.11k and 802.11v are disabled.

### Polito Hierarchical VLAN Allocation Scheme (Classroom R)
| Location | Radios # | APG-NAME | VLAN ID | IP Net |
| :--- | :--- | :--- | :--- | :--- |
| **R1** | 4 | APG-BOGGIO12 | 1140 | 172.21.134.0/23 |
| **R2** | 4 | APG-BOGGIO13 | 1142 | 172.21.136.0/23 |
| **R3** | 4 | APG-BOGGIO14 | 1143 | 172.21.138.0/23 |
| **R4** | 4 | APG-BOGGIO15 | 1144 | 172.21.140.0/23 |
| **R1B+R3B** | 8 | APG-BOGGIO20 | 1154 | 172.21.150.0/23 |
| **R2B+R4B** | 8 | APG-BOGGIO21 | 1155 | 172.21.152.0/23 |
| **CORRIDOR P1** | 6 | APG-BOGGIO09 | 1105 | 172.21.78.0/23 |
| **CORRIDOR PT** | 6 | APG-BOGGIO18 | 1152 | 172.21.146.0/23 |
| **STUDY ROOMS** | 4 | APG-BOGGIO19 | 1153 | 172.21.148.0/23 |
*All data directly sourced from.*