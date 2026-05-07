## Part 1: Storage Hardware & Architecture

### Hard Disk Drives (HDD)
*   **Mechanism:** Mechanical devices that store data magnetically on spinning platters using a moving arm.
*   **Organization:** 
    *   **Tracks:** Circular paths on the disk surface.
    *   **Sectors:** The smallest unit of data.
    *   **Cylinder:** A set of tracks vertically aligned across all platters.
*   **Performance Components:**
    *   **Seek Time:** The time it takes to move the arm to the correct track (typically 3-12 ms).
    *   **Rotational Latency:** The time spent waiting for the correct sector to rotate under the read-write head.
    *   **Transfer Rate:** The speed of reading/writing data once the head is in position.

### Nonvolatile Memory Devices (NVM / SSD)
*   **Mechanism:** Electrical storage (flash memory) with no moving parts, resulting in very low latency.
*   **Constraints & Management:**
    *   Data is read/written in **pages** but must be erased in **blocks** (multiple pages).
    *   **No In-Place Overwrite:** A block must be erased before it can be rewritten.
    *   **Flash Translation Layer (FTL):** Maps logical addresses to physical pages and tracks valid vs. invalid data.
    *   **Garbage Collection:** Finds blocks with many invalid pages, moves the remaining valid data elsewhere, and erases the block to free it up.
    *   **Endurance:** Cells wear out over time, measured in **DWPD (Drive Writes Per Day)**.

---

## Part 2: Important Formulas & Calculations

### HDD Performance & Time Equations
*   **Access Time:** $\text{Seek Time} + \text{Rotational Latency}$.
*   **Average Rotational Latency:** $\frac{1}{2} \times \text{Rotation Time}$.
*   **Total I/O Time:** $\text{Access Time} + \text{Data Transfer Time} + \text{Controller Overhead}$.
*   **Rotation Time Calculation:** If a disk is 5400 RPM (Revolutions Per Minute), one rotation takes $\frac{1}{5400} \times 60 \text{ seconds} = 11 \text{ ms}$.

### HDD Capacity Calculations
*   **Bytes per Track:** $\text{Bytes/Sector} \times \text{Sectors/Track}$.
*   **Bytes per Surface:** $\text{Bytes/Track} \times \text{Tracks/Surface}$.
*   **Total Disk Capacity:** $\text{Bytes/Surface} \times \text{Surfaces/Disk}$.
*   *Note on Block Sizes:* A valid block size must be a multiple of the sector size and must fit entirely within a single track without crossing over.

### Reliability & Failure Equations (RAID)
*   **MTTF (Mean Time To Failure):** Average time a component operates before failing.
*   **MTTR (Mean Time To Repair):** Average time required to repair a failed system.
*   **MTTDL (Mean Time To Data Loss):** Average time before a permanent data loss occurs.
*   **MTTDL Formula for 2 Mirrored Disks:** $MTTDL \approx \frac{MTTF^2}{2 \times MTTR}$.

---

## Part 3: Disk Scheduling Algorithms

### HDD Scheduling
Because HDD performance is bottlenecked by seek time, the OS schedules an I/O queue to minimize physical head movement.
*   **FCFS (First-Come, First-Served):** Processes requests in the exact order they arrive. Simple and fair, but can cause wild head swings and poor performance.
*   **SCAN (Elevator Algorithm):** The arm starts at one end, moves to the other end servicing requests along the way, and reverses direction when it hits the end.
*   **C-SCAN (Circular SCAN):** Similar to SCAN, but when it reaches the far end, it immediately sweeps back to the beginning *without* servicing requests on the return trip, providing a more uniform wait time.
*   **Deadline Scheduler (Linux):** Prevents starvation by maintaining separate read and write queues (prioritizing reads) alongside standard FIFO queues; if a request waits too long, it is serviced immediately.

### NVM Scheduling
*   Because seek time and rotational latency are zero, complex scheduling algorithms (like SCAN) are largely unnecessary for SSDs.
*   OS schedulers generally use simple **FCFS** or **NOOP** and focus merely on merging adjacent logical block addresses into larger requests.

---

## Part 4: RAID (Redundant Arrays of Independent Disks)

RAID organizes multiple drives to improve reliability (redundancy), performance (parallelism), or both.
*   **RAID 0 (Striping):** Splits data blocks across multiple drives for high performance, but offers zero redundancy.
*   **RAID 1 (Mirroring):** Duplicates every write across two physical drives for high reliability.
*   **RAID 4 (Block-Interleaved Parity):** Stripes blocks across drives and reserves one dedicated drive exclusively for parity (error-correction) data.
*   **RAID 5 (Block-Interleaved Distributed Parity):** Stripes both data and parity across all drives, avoiding the bottleneck of a single dedicated parity drive.
*   **RAID 6 (P + Q Redundancy):** Similar to RAID 5 but stores extra redundant information, allowing the system to survive *two* simultaneous drive failures.
*   **RAID 0+1 / 1+0:** Combines mirroring and striping to provide both top-tier performance and high reliability.

---

## Part 5: Storage Attachment & Management

### Formatting & Error Handling
*   **Low-Level (Physical) Formatting:** Divides the blank storage device into sectors containing metadata, actual data, and Error Correction Codes (ECC).
*   **Logical Formatting:** Partitions the disk and creates the initial file-system data structures (free space maps, empty directories).
*   **Error Detection vs. Correction:** Parity bits can *detect* if an odd/even bit flip occurred, while ECC can both detect and *correct* "soft" errors.

### Storage Attachment Types
*   **Host-Attached:** Connected directly to local I/O ports via SATA, NVMe, USB, or Fibre Channel.
*   **NAS (Network-Attached Storage):** Storage accessed over a LAN/WAN as a remote file system using protocols like NFS, CIFS, or iSCSI.
*   **SAN (Storage Area Network):** A dedicated, flexible network (often Fibre Channel or InfiniBand) connecting multiple hosts to multiple storage arrays.
*   **Cloud Storage:** Similar to NAS but accessed over the internet via APIs (due to latency/failure protocols) rather than standard file system protocols.

### Advanced System Features
*   **ZFS:** A file system that pools storage (rather than using traditional volumes) and uses checksums on *all* data and metadata to automatically detect and correct silent corruption.
*   **Hot Spare:** An unused, spinning disk automatically drafted by the RAID controller to replace a failed disk and immediately begin rebuilding the array.
*   **Swap-Space Management:** A dedicated raw partition or file used to page/swap data out of DRAM to prevent memory exhaustion.

## Part 6: Practical Exercises & Calculations

### 1. Hard Disk Drive (HDD) Geometry & Capacity
*(From Exam 07/07/2023)*
**Scenario:** An HDD has standard geometry with:
*   Sector size: 512 Bytes
*   Tracks per surface: 2,048
*   Sectors per track: 50
*   Platters: 5 double-sided (10 surfaces total)
*   Average seek time: 10 msec

**Calculations:**
*   **Capacity of a track:** $512 \text{ Bytes/sector} \times 50 \text{ sectors} = 25,000 \text{ Bytes (25 KB)}$.
*   **Capacity of a surface:** $25 \text{ KB/track} \times 2,048 \text{ tracks} = 51,200 \text{ KB (50 MB)}$.
*   **Total Disk Capacity:** $50 \text{ MB/surface} \times 10 \text{ surfaces} = \text{500 MB}$.
*   **Number of Cylinders:** Equals the number of tracks per surface, which is **2,048**.

### 2. Valid Block Sizes (Cylinder-Head-Sector Addressing)
A valid block size on a disk must satisfy two rules: it must be a multiple of the sector size, and it must fit entirely within a single track without crossing over. 

**Scenario:** Same disk as above (Sector = 512 B, Track = 25 KB). Are the following block sizes valid?
*   **256 B:** **NO.** It is not a multiple of the 512 B sector size.
*   **2,048 B:** **YES.** It is a multiple of 512 B (4 sectors) and is smaller than the 25 KB track limit.
*   **51,200 B:** **NO.** While it is a multiple of 512 B, it exceeds the total size of a single track (25 KB).

### 3. Rotational Delay and Transfer Rate
*(From Exam 07/07/2023)*
**Scenario:** The disk platters rotate at 5,400 RPM (Revolutions Per Minute).
*   **Maximum Rotational Delay (Time for 1 full rotation):** 
    $$(\frac{1}{5400}) \times 60 \text{ seconds} = 0.011 \text{ seconds} = \text{11 ms}$$.
*   **Average Rotational Delay:** Half of the maximum = **5.5 ms**.
*   **Transfer Rate (Assuming 1 track transferred per revolution):** 
    $$25 \text{ KB} / 11 \text{ ms} = 2.25 \text{ MB/s}$$ (which is equivalent to **18 Mbit/s**).

### 4. Disk Scheduling Algorithm Traces
**Scenario:** A disk has 5,000 cylinders (0 to 4,999). The head is currently at 2,150, and the previous request was at 1,805 (meaning the head is moving *up* or *outward*). 
**Queue (Arrival Order):** 2,069; 1,212; 2,296; 2,800; 544; 1,618; 356; 1,523; 4,965; 3,681.

**FCFS (First-Come, First-Served) Trace:**
The head moves to each request in the exact order they arrived.
*   Path: 2,150 $\rightarrow$ 2,069 $\rightarrow$ 1,212 $\rightarrow$ 2,296 $\rightarrow$ 2,800 $\rightarrow$ 544 $\rightarrow$ 1,618 $\rightarrow$ 356 $\rightarrow$ 1,523 $\rightarrow$ 4,965 $\rightarrow$ 3,681.
*   *Note: This results in massive, inefficient swings back and forth across the disk.*

**SCAN (Elevator Algorithm) Trace:**
Sort the pending requests by cylinder number. Since the head is at 2,150 and moving UP (away from 1,805), it will service all larger requests first, hit the end of the disk, and then reverse to catch the smaller ones.
*   **Sorted Queue:** 356; 544; 1,212; 1,523; 1,618; 2,069; 2,296; 2,800; 3,681; 4,965.
*   **Path UP:** 2,150 $\rightarrow$ 2,296 $\rightarrow$ 2,800 $\rightarrow$ 3,681 $\rightarrow$ 4,965 $\rightarrow$ 4,999 (End of disk).
*   **Path DOWN:** 4,999 $\rightarrow$ 2,069 $\rightarrow$ 1,618 $\rightarrow$ 1,523 $\rightarrow$ 1,212 $\rightarrow$ 544 $\rightarrow$ 356.

***
