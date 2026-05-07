Here is the exhaustive master cheat sheet based on the provided document.

## **System Programming: Mass Storage & File System Cheat Sheet**

### **1. File System Architecture & Block Calculations**

**FAT vs. Inode File Systems**
* **System Parameters Context**: When comparing a FAT-based file system (F1) and an Inode-based file system (F2) with 32-bit pointers ($4 \text{ Bytes}$) and $4 \text{ KB}$ block sizes.
* **Data Block Capacity**: The maximum number of data blocks is calculated by dividing the total memory allocated for the FAT by the size of a single pointer.
    * *Formula*: $N_{F1} = \frac{\text{FAT Size}}{\text{Pointer Size}}$.
    * *Calculation*: $150 \text{ MB} / 4 \text{ B} = 37.5 \text{ M}$ blocks.
    * F2 has the exact same theoretical max capacity of data blocks as F1 because the space reserved for data blocks is the same.
* **Free Data Blocks**: The maximum number of free data blocks equals the maximum capacity of data blocks (e.g., $37.5 \text{ M}$ blocks for both F1 and F2).

**Free List Management**
* **FAT Systems**: The free list can be represented directly within the FAT. The FAT holds references to blocks occupied by files as well as the free-list. Indices of unused blocks are available specifically to be used for the free list.
* **Inode Systems**: Free blocks can be organized using a linked list of index blocks, where each index block contains a pointer to the next index block and $N_{Free}$ pointers to free data blocks. This is valid because using Inodes for files does not force free blocks to be structured as an additional Inode-accessible file. Simple lists or bitmaps are also valid alternatives.

### **2. Storage Hardware: SSDs vs. Magnetic Disks**

**Disk Scheduling & Compatibility**
* **SCAN and C-SCAN Policies**: These scheduling algorithms are useless for Solid State Drives (SSDs). They are designed to minimize total head travel distance (measured in block/cylinder index differences) on magnetic disks to reduce seek time. SSDs do not incur penalties or costs based on differences in block indices.
* **Mixed Volume Systems**: It is entirely possible to combine a magnetic disk (e.g., 500GB) and an SSD (e.g., 200GB) into a single continuous volume (e.g., 700GB). This is because disk technology is abstracted at the low-level device driver layer, and standard partitioning and formatting can merge multiple physical disks into one volume. Performance will vary depending on which device is actively being accessed.
* **Swapping Efficiency**: A raw swap partition is far more efficient in terms of access times than a swapfile housed within an existing filesystem. Raw partitions manage and utilize physical disk blocks directly, entirely bypassing the overhead of filesystem layers.

**SSD Lifespan Constraints**
* **Limiting Factor**: The lifespan of an SSD is fundamentally limited by its maximum number of erase operations.
* **Erase vs. Write**: Erasures are executed at the block/page level. This directly impacts the maximum number of writes because every write (or re-write) operation must be explicitly preceded by an erase operation.
* **Read Limit**: There is no limit on read operations; reading data does not degrade the SSD.

**RAID Metrics**
* **MTTR (Mean Time To Repair)**: The average time required to repair and fully restore a disk after a failure has occurred.
* **MTTDL (Mean Time To Data Loss)**: The average time (the inverse of failure frequency/probability) until data is permanently lost. Data loss occurs in a mirrored RAID when a second, independent disk failure happens before the first failed disk has finished repairing.

### **3. File System DAGs (Directed Acyclic Graphs)**

* **Shared Files & Directories**: If a file system allows both files and directories to be shared, the directory tree becomes a DAG.
* **The Problem with Cycles**: Cycles destroy the DAG property, meaning a directory could theoretically have its own ancestor/predecessor as a descendant/successor. This must be strictly avoided.
* **Prevention Strategies**:
    1.  Only allow files (leaves) to be shared, completely forbidding directory sharing.
    2.  Garbage Collection: Permit cycles to form temporarily (saving time on checking every link operation), but run a periodic system check that detects and deletes them.
    3.  Active Prevention: Perform a cycle-check algorithm dynamically every time a new link is generated; if a cycle is detected, invalidate the operation.

---

## **Practical Exercises & Step-by-Step Math Breakdowns**

### **Exercise A: Data Block Allocation (FAT vs. Inode)**
**Scenario**: FAT pointer = 32-bit ($4 \text{ B}$). Block size = $4 \text{ KB}$.
* **Calculating maximum pointers in an index block**:
    $N_{pointers} = \frac{4 \text{ KB}}{4 \text{ B}} = 1024$ pointers.
* **Calculating $N_{Free}$ for a linked list of index blocks**:
    One pointer is reserved to point to the next list block, so:
    $N_{Free} = 1024 - 1 = 1023$ pointers to free data blocks.
* **Calculating max index blocks for F2's free list**:
    $\text{Max blocks} = \frac{37.5 \text{ M}}{1023} \approx 37.5 \text{ K}$ index blocks.

### **Exercise B: Calculating Blocks Used by Specific Files**
**Scenario**: File "a.mp4" (317 MB in FAT) and "b.mp4" (751 MB in Inode with 10 direct, 1 single, 1 double, 1 triple indirect layout). Block size = 4 KB.

**File a.mp4 (FAT System):**
* **Data Blocks**: $\frac{317 \text{ MB}}{4 \text{ KB}} = \frac{317}{4 \text{ K}} = 79.25 \text{ K}$ blocks.
* **FAT Indices**: Exactly equal to the data blocks = $79.25 \text{ K}$ indices.

**File b.mp4 (Inode System):**
* **Data Blocks**: $\frac{751 \text{ MB}}{4 \text{ KB}} = \frac{751}{4 \text{ K}} = 187.75 \text{ K}$ blocks.
* **Index Blocks Breakdown**:
    1.  The first 10 data blocks use direct pointers (0 index blocks).
    2.  The next $1024$ ($1 \text{ K}$) data blocks use the single indirect pointer = $1$ index block.
    3.  Remaining blocks: $187.75 \text{ K} - 10 \text{ (direct)} \approx 187.75 \text{ K}$ to map.
    4.  Double Indirect First Level: $1$ index block.
    5.  Double Indirect Second Level: $\lceil \frac{187.75 \text{ K} - 10}{1 \text{ K}} \rceil - 1 = 187$ index blocks.
    * **Total Index Blocks**: $1 \text{ (single)} + 1 \text{ (double level 1)} + 187 \text{ (double level 2)} = 189$ blocks.

### **Exercise C: Unix Inode Maximums & Fragmentation**
**Scenario**: Unix FS, 13 pointers (10 direct, 1 single, 1 double, 1 triple). 32-bit pointers ($4 \text{ B}$), 2KB blocks. 1000 files, average size 15MB, total internal fragmentation 1MB.

**Step 1: Determine Global System Stats**
* Pointers per block = $\frac{2 \text{ KB}}{4 \text{ B}} = 512$.
* Gross total size = $15000 \text{ MB} + 1 \text{ MB (frag)} = 15001 \text{ MB}$.
* Total gross blocks = $15001 \times 512$.

**Step 2: Calculate Min Occupations for File Types**
* Min blocks for Double Indirect ($MIN_2$) = $10 + 512 + 1 = 523$ blocks.
* Min blocks for Triple Indirect ($MIN_3$) = $10 + 512 + 512^2 + 1$ blocks.

**Step 3: Calculate Max Files ($N2$ and $N3$)**
* Max Double Indirect ($N2$) = $\lfloor \frac{15001 \times 512}{523} \rfloor = 14685$ files.
    * *Correction*: Since the system only has 1000 files total, the true max limit for $N2$ is naturally capped at 1000.
* Max Triple Indirect ($N3$) = $\lfloor \frac{15001 \times 512}{523 + 512^2} \rfloor = 29$ files.

**Step 4: Maximizing Files with Zero Internal Fragmentation**
* To maximize files with $0$ fragmentation, you must concentrate all $1 \text{ MB}$ of system fragmentation into the fewest possible files.
* Max fragmentation possible per file = 1 full block minus 1 byte = $2 \text{ KB} - 1 \text{ B} = 2047 \text{ B}$.
* Minimum files bearing fragmentation ($N_{min}$) = $\lceil \frac{1 \text{ MB}}{2047 \text{ B}} \rceil = 513$ files.
* Max files with $0$ fragmentation = Total files $- N_{min} = 1000 - 513 = 487$ files.

### **Exercise D: Deep Dive into Triple Indirect Pointers**
**Scenario**: A file uses exactly $2000$ index blocks. Calculate the min/max data blocks and file dimensions.
* **Determining Needed Levels**: A fully utilized double indirect structure requires $514$ index blocks ($1$ single + $1$ double level-1 + $512$ double level-2). Thus, 2000 blocks mean the file requires a triple indirect pointer, leaving $2000 - 514 = 1486$ blocks for the triple indirect structure.
* **Triple Indirect Breakdown**:
    * $\lceil \frac{1486}{512} \rceil = 3$.
    * This breaks down to: $1 \text{ (level 1)} + 3 \text{ (level 2)} + 1482 \text{ (level 3)}$.
* **Data Block Computations ($NBL$)**:
    * $NBL_{min}$ assumes the last index block holds only 1 pointer.
        $NBL_{min} = 10 \text{ (direct)} + 512 \text{ (single)} + 512 \times 512 \text{ (double)} + 1481 \times 512 + 1 \text{ (triple)} = 1020939$ blocks.
    * $NBL_{MAX}$ assumes the last index block is fully populated (adding 511 pointers).
        $NBL_{MAX} = NBL_{min} + 511 = 1021450$ blocks.
* **File Dimensions ($DIM$)**:
    * $DIM_{min}$ assumes maximum internal fragmentation in the last block ($2047 \text{ B}$).
        $DIM_{min} = (NBL_{min} \times 2 \text{ KB}) - 2047 \text{ B}$.
    * $DIM_{MAX}$ assumes exactly $0$ internal fragmentation.
        $DIM_{MAX} = NBL_{MAX} \times 2 \text{ KB}$.

### **Exercise E: RAID MTTDL Calculation**
**Scenario**: RAID with 2 disks in "mirrored" configuration. Disks fail independently. $MTTF = 50000$ hours. $MTTR = 20$ hours.
* *Formula*: $MTTDL = \frac{MTTF^2}{2 \times MTTR}$.
* *Calculation Breakdown*:
    $MTTDL = \frac{50000^2}{2 \times 20}$ hours.
    $MTTDL = \frac{2.5 \times 10^9}{40}$ hours.
    $MTTDL = 6.25 \times 10^7$ hours.

### **Exercise F: SSD Lifetime Writes**
**Scenario**: 1TB SSD, guaranteed 3 years, max limit of 5TB written per day.
* *Calculation Breakdown*:
    $N_{write\_max} = 5 \text{ TB} \times 3 \text{ years} \times 365 \text{ days}$.
    $N_{write\_max} = 5 \times 1095 \text{ TB}$.
    $N_{write\_max} \approx 5.5 \times 10^3 \text{ TB}$.
