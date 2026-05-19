## **1. Historic Trends & The Path to Datacenters**

* 
**Evolution of Computing:** The industry transitioned from mainframes to minicomputers, and then to scattered servers.


* 
**The Problem with Scattered Servers:** * Servers were distributed across companies and controlled by various organizations, leading to permission and access silos.


* Security risks were high; hard disks could easily be stolen from unprotected servers.


* Permissions and backups were often mismanaged.




* 
**The Solution:** Centralize servers into a single location: the **datacenter**.


* **Data Access Models:**
* 
**Mainframes:** Centralized access (historic).


* 
**Client-Server** and **Peer-to-Peer**.


* Mixed models are also utilized.




* **Datacenter Consolidation Benefits:**
* 
**Storage:** Disks are decoupled from computational resources, providing immense flexibility in storage space allocation.


* 
**Computational Resources:** Enhanced flexibility and optimized power consumption.




* **Cloud Computing:** Access environments anywhere, anytime, on any device. Mobile devices prioritize battery, thereby possessing limited processing power, which makes cloud/datacenter reliance essential.



---

## **2. Storage Basics: Physical and Logical Disks**

### **Physical Disks & Addressing**

* **CHS (Cylinder-Head-Sector) Addressing:** * A historic method to index data. A specific track is determined by the head and cylinder numbers.


* 
**Sector:** The smallest storage unit addressable by a hard drive, usually **512 bytes**.


* Disk controllers map logical to physical addresses (e.g., accounting for fewer bytes in inner tracks).


* CHS is inappropriate for non-disk devices like magnetic tapes.




* **LBA (Logical Block Addressing):**
* Replaced CHS; it is a simple integer index of the block inside the virtualized disk.


* Introduced in 2003 with the **ATA-6** standard.


* LBA uses a **48-bit** number, supporting storage capacities up to **128 PiB**.


* Storage devices typically use a **512-byte** block (though this can be changed). Note: This block size is independent of the Operating System block size (UNIX typically uses a **1KB** block).





### **Logical Disk Structure**

Operating Systems abstract raw disks into structures accessible to applications.

* 
**Master Boot Record (MBR):** The first **512 bytes** of the disk.


* 
**Boot Loader:** Occupies **446 bytes**.


* 
**Partition Table:** Occupies the remaining space via **4 slots of 16 Bytes each**.




* 
**File System Hierarchy:** Consists of the File Allocation Table, Directories, and individual files.



---

## **3. Traditional Storage Architecture**

### **Direct Attached Storage (DAS)**

* 
**Definition:** Each server has exclusive access to its attached storage devices.


* **SCSI (Small Computer System Interface):**
* A standard defining a set of commands, a transaction protocol, and a physical interface.


* 
**Block-Oriented:** The host OS views the storage as contiguous sets of fixed-size data blocks.


* **Legacy SCSI:** Operated as a complete protocol stack (from cables to application commands). It used a parallel and shared bus, allowing multiple devices per host.


* 
**Addressing:** Devices are addressed using a **LUN** (Logical Unit Number).


* 
**SCSI Limits:** Maximum length of **25 meters**, supporting a maximum of **16 devices**.


* 
**Characteristics:** Guaranteed data integrity with a very low error rate (though error recovery was inefficient), and extremely low latency (milliseconds through disk, microseconds through cache).




* **SCSI Commands:**
* Perform operations on "physical" disks (e.g., READ, WRITE, FORMAT).


* **CDB (Command Description Block):** Contains the data and execution parameters. A READ CDB includes: Operation code, LUN, Logical Block Address (LBA), Transfer Length (in blocks), and Allocation Length (in bytes).





---

## **4. The Storage Evolution: NAS and SAN**

Storage decoupled from servers via networks to solve DAS limitations (poor scalability, difficult backup/sharing, severe distance limits).

### **Network Attached Storage (NAS)**

* 
**Definition:** Separates storage from compute, allowing servers/clients to connect over standard network technologies (LAN/WAN or Internet).


* **Characteristics:**
* Usually dedicated appliances running proprietary/optimized OS.


* High capacity, utilizing RAID and Hot-Swap for continuity.


* **Virtualizes shared disks at the file level:** It serves files over the network. The raw file system is completely invisible to the client.




* **Protocol Stack:**
* Relies primarily on **NFS** or **CIFS**.


* Runs over **TCP/IP** (or UDP) on **Ethernet**.




* 
**Pros:** High compatibility across OS platforms, works over WAN, and has minimal impact on existing infrastructure.


* **Cons:**
* Clients lack physical disk control (cannot format or manage at the block level).


* Mandatory concurrency checks introduce overhead.


* Incompatible with applications requiring raw block access (e.g., booting computers, specific databases for performance, swap files).


* NAS handles user rights, complicating outsourcing to Storage Service Providers.


* High computational burden on the NAS to translate file requests into block requests.


* TCP/Ethernet protocol stack is unoptimized for storage performance.





### **Storage Area Network (SAN)**

* 
**Definition:** A dedicated storage network that virtualizes physical disks and provides access via logical blocks (not files).


* 
**Architecture:** Acts as a two-tier or three-tier model, interacting with disks exactly as DAS did.


* 
**SCSI Integration:** Maintains the upper layers of the SCSI protocol stack (end-to-end communication) to guarantee compatibility with all existing SCSI applications.


* 
**Network Requirements:** Demands high speed, low latency, very low error rates, high node compatibility, and metropolitan distance coverage. Ethernet alone is historically insufficient to build a SAN.



---

## **5. Disk Cabinets and Virtualization**

### **RAID vs. JBOD**

* **RAID (Redundant Array of Independent/Inexpensive Disks):**
* Divides, replicates, and distributes data concurrently across multiple drives (e.g., RAID 0 stripes data across multiple disks to accelerate Read/Write operations).


* Read/Write is significantly faster than JBOD.


* Requires drives of similar capacities and consumes raw space to store redundant data.


* Protects against localized disk loss, but data is unavailable if the entire RAID enclosure fails.




* **JBOD (Just a Bunch Of Disks):**
* Individual disks can serve as separate volumes or be concatenated/spanned to form a single LUN.


* Drives can be of varied sizes, and 100% of the raw space is utilized.


* Slower sequential performance (stores data on one disk at a time).


* Zero hardware redundancy; if a spanned disk is corrupted, all data is at risk. Protection relies on software-managed redundancy (e.g., Google's methodology).


* Cheaper storage controllers.





### **Data Virtualization**

SAN allows virtual resources to be decoupled from physical resources.

* 
**Enclosure Level:** Disk controllers map physical disks into virtual drives, aggregating or splitting capacity, and providing transparent replication/RAID.


* **Datacenter Level:** Required because a failing enclosure takes down all its internal replication. Implementing virtualization blades (L7) in datacenter switches or using software controllers enables transparent data duplication across geographically separate datacenters (this is why JBODs are often preferred over smart enclosures here).



---

## **6. SAN Protocol Stacks**

SAN supports multiple transport implementations for the SCSI command layer:

* 
**Parallel SCSI:** Obsolete.


* **Fibre Channel (FC):** Native evolution of SCSI. Supports higher speeds and complex network topologies.


* **iSCSI:** Native SCSI encapsulated over TCP/IP. Primarily used for low-cost host-to-SAN connections over Ethernet.


* **FCIP:** Fibre Channel over IP. Used to interconnect separate FC domains via geographic TCP/IP links (ideal for remote backups/redundancy).


* 
**FCoE (Fibre Channel over Ethernet):** Maps FC higher layers directly onto a lossless Ethernet physical layer, designed heavily for datacenter convergence.



### **SAN over Ethernet (TCP/IP)**

* 
**Advantages:** Extreme network simplicity, low infrastructural/training costs, fast upgrade paths leveraging Ethernet economies of scale, and the ability to run a single converged network.


* **Problems:**
* No intrinsic data delivery guarantees (frame loss is a feature of standard Ethernet).


* Error recovery relies strictly on TCP timeouts, which operate on a massive scale (hundreds/thousands of milliseconds).


* TCP is highly complex to implement in hardware.


* No latency guarantees.





---

## **7. Fibre Channel (FC) Deep Dive**

### **Overview & Topologies**

* 
**Purpose:** Created as a reliable, high-speed serial replacement for parallel Ultra3 SCSI.


* 
**Speeds:** Native support for **1, 2, 4, 8, and 16 Gbps**.


* 
**Control/Data Planes:** The data plane remains standard SCSI, but the control plane introduces complex new disk management features and strict lossless modes.


* **Connection Modes:**
* 
**Direct Connection:** Point-to-point (historic SCSI replacement).


* 
**Arbitrated Loop:** Ring topology connecting up to **127 nodes** (historic).


* 
**Switched Fabric:** Meshed network utilizing full-duplex links between switches and nodes.





### **Fibre Channel Protocol Stack**

* 
**FC-0:** Physical layer interface definitions.


* 
**FC-1:** Transmission, encoding, and low-level link control.


* 
**FC-2:** Signalling/End-to-End data transfer (defines Frame format, Addressing, Segmentation, Flow control, Error detection/correction).


* 
**FC-3:** Common services (Cryptography, Compression, Channel bonding).


* 
**FC-4:** ULP Mapping (Protocol mapping between upper layers and the FC transport layer).



### **FC Port Types**

* 
**N_port:** Host Bus Adapter (HBA) on end nodes.


* 
**F_port:** Switch port connecting to an HBA.


* 
**E_port:** Switch-to-switch connection (Inter-Switch Link / ISL).


* 
**NL_port / FL_port:** Ports operating in loop functioning.



### **Addressing in Fibre Channel**

* 
**World Wide Name (WWN):** A unique, hardcoded **64-bit** name identifier assigned at the factory for nodes, ports, and switches.


* 
**Dynamic Address:** During data exchanges, a **24-bit** address is dynamically assigned, comprising three 8-bit components:


1. 
**Domain_ID (8 bits):** Assigned to switches (range 00h to EFh), max **239 switches**. The range F0h to FFh is reserved for "Well Known Addresses" (e.g., address 00 is for Fabric services implemented internally by the switches).


2. 
**Area_ID (8 bits)** & **Port_ID (8 bits):** Assigned to end nodes, theoretically allowing **65536 nodes per switch**.





### **Routing & Communication**

* 
**FSPF (Fabric Shortest Path First):** The link-state routing protocol used to propagate domain/area reachability (similar to IP's OSPF).


* 
**Loops Limit:** Fibre Channel does **not** have a TTL (Time To Live) mechanism; therefore, infinite packet loops are possible, requiring FSPF to converge as fast as possible.


* 
**Data Exchange:** Communication between nodes opens an "exchange," which expects half-duplex frame "sequences" while managing flow control, resource reservation, and ordered delivery.


* 
**Flow Control:** Executed End-to-End or Buffer-to-Buffer utilizing a strict **credit mechanism**.


* 
*Edge case / Flaw:* Deadlock can occur; entire links can be blocked due to a lack of credits.





---

## **8. Advanced Concepts & 10GbE Consolidation**

### **Frame Overhead Comparisons**

* **Fibre Channel Frame:** Strict **36 bytes** overhead.
* Breakdown: SOF (4 Bytes) + Header (24 Bytes) + Data Payload (4 to 2112 Bytes) + CRC (4 Bytes) + EOF (4 Bytes).




* **Ethernet - TCP/IP Frame:** Minimum **58 bytes** overhead.
* Breakdown: Ethernet Header (18 Bytes) + IP Header (20 Bytes) + TCP Header (20 Bytes) + iSCSI/FC-IP encapsulation data.





### **Advanced SAN Features**

* **VSAN (Virtual SAN):** Logical partitioning of a physical SAN (analogous to Ethernet VLANs). Critical for Storage Service Providers.


* 
**Network Optimization:** SANs support Link Aggregation and Load Balancing natively.



### **I/O Consolidation & The Path to 10GbE**

* **The Hardware Sprawl Problem:** Historically, a single server required 1 NIC for LAN, 1 HBA for Storage (FC), and 1 NIC for clustering (Infiniband)—doubled for redundancy. This led to high costs, excess power draw, depleted PCI slots, rack crowding, and cable nightmares.


* 
**The 10GbE / FCoE Solution:** * 10Gb Ethernet provides the necessary bandwidth to consolidate all these onto a single network type.


* To overcome Ethernet's frame loss flaw, **Priority Flow Control** (per-priority PAUSE, submitted to IEEE 802.3) provides lossless behavior at the network layer.


* **FCoE (Fibre Channel over Ethernet):** Pushes FC logic strictly over physical Ethernet. It uses a **Convergent Network Adapter (CNA)** hardware card, which exposes both an Ethernet NIC and an FC HBA to the upper OS layers, preserving legacy application compatibility. Unlike FCIP, FCoE is strictly for datacenter environments and is **not routable**.





### **Major Industry Vendors**

* 
**SAN Specialists:** Brocade, Cisco.


* 
**NAS Specialists:** NetApp, HP, Dell.


* 
**Turnkey Enterprise Solutions:** IBM, EMC.