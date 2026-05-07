## Master Cheat Sheet: System Programming & Memory Management

### Core Concepts & Architectural Rules

#### Memory Management: Variable Contiguous Partitions
* **Worst-Fit Allocation**: Memory is allocated by selecting the largest available partition from the free list. 
* **Free List Management**: Free partitions are managed via a linked list, which is ordered by decreasing partition size.
    * **Node Structure**: Each node in the list contains a pointer to the next partition and the size of the current partition.
    * **Memory Footprint**: Both the pointer and size fields are represented on 4 bytes each, with the value 0 acting as a null pointer.
    * **Header Placement**: These 8 bytes of header information (pointer and size) are stored directly in the first bytes of the free partition they represent.
* **Hexadecimal Representation**: It is highly recommended to maintain memory addresses and partition sizes in hexadecimal format for calculations.

#### Paging and Memory Fragmentation
* **External Fragmentation**: In a paged memory system, external fragmentation is exactly 0 by definition.
* **Internal Fragmentation**: 
    * **Worst Case**: Equal to the total size of one page (e.g., $2\text{ KByte}$).
    * **Average Case**: Equal to half the size of a page (e.g., $1\text{ KByte}$).
    * **Optimal Case**: 0, which occurs when a process's virtual address space is a perfect multiple of the page size.

#### Virtual Memory: Page Tables
* **Hierarchical (2-Level) Page Tables**: Logical addresses are split into multiple parts (e.g., $p_1$, $p_2$, $d$ from MSB to LSB) to index into different levels of the table.
    * The total number of entries in a specific table level corresponds to $2^{n}$, where $n$ is the number of bits allocated to that level's index.
    * Table size in bytes is calculated as the number of entries multiplied by the byte size of each entry.
* **Effective Access Time (EAT)**: EAT calculations must account for the Translation Look-aside Buffer (TLB) hit ratio and the memory access time.
    * **Formula**: $\text{EAT}=(P_{\text{hit}} * T_{\text{RAM}}) + (P_{\text{miss}} * T_{\text{miss\_penalty}})$.
    * **Critical Rule for 2-Level PT Miss Penalty**: A TLB Miss in a 2-level page table requires exactly 3 memory accesses (2 accesses to traverse the page table levels + 1 access for the actual requested RAM data).

#### Inverted Page Tables (IPT)
* **Advantages**:
    * **Memory Savings**: The overall size of the table is proportional to the physical RAM size, rather than the vast virtual address space.
    * **Singular Structure**: There is only one single table for all processes combined, as each physical frame maps to only one process at a time.
* **Disadvantages**:
    * **Search Latency**: The primary drawback is slowness; the system must actively search for a page rather than accessing it directly via an index.
    * **Mitigation**: To combat this, IPTs are usually paired with Hash Tables.
* **Row Structure**: Each entry (row) in an IPT typically contains a page index and the process ID (PID) to ensure proper mapping.

---

## Practical Exercises: Step-by-Step Breakdowns

### Exercise 1: Variable Partitions & Worst-Fit Allocation 
**System Specifications:**
* **Total Physical Memory**: $512\text{ MByte}$.
* **Minimum Allocation Unit**: $64\text{ Byte}$.
* **OS Allocation**: First $128\text{ MByte}$ permanently reserved.
* **Initial Free List**: $(08000000, 08000000)$ and $(100A0000, 07760000)$.
* **Initial Allocated Processes**: $P_{10}$ at $(10000000, 000A0000)$ and $P_{11}$ at $(17800000, 08800000)$.

**Scenario Breakdown:**
1.  **Allocate $P_{12}$ ($25\text{ MB}$)**:
    * Convert requirement to hex: $25\text{ MB} = 01900000\text{ B}$.
    * Using Worst-Fit, allocate from the largest free partition: $(08000000, 08000000)$.
    * $P_{12}$ is allocated at $(08000000, 01900000)$.
    * Calculate remaining free space: $08000000\text{ B} - 01900000\text{ B} = 06700000\text{ B}$.
    * The newly created free partition $(09900000, 06700000)$ moves to the end of the free list because it is smaller than the other available partition.
2.  **Allocate $P_{13}$ ($150\text{ MB}$)**:
    * Convert requirement to hex: $150\text{ MB} = 09600000\text{ B}$.
    * Current free blocks are too small. We must resolve fragmentation.
    * **Solution**: Swap-out $P_{10}$ to generate a single contiguous free partition.
    * Calculate new contiguous block size: $06700000 + 000A0000 + 07760000 = 0DF00000\text{ B}$.
    * $P_{13}$ is allocated into this block: $(09900000, 09600000)$.
    * Remaining free space from this block: $(12F00000, 04900000)$.
3.  **Terminate $P_{11}$**:
    * $P_{11}$ frees up its partition of $08800000\text{ B}$.
    * This directly increases the size of the single adjacent block in the free list.
    * New Free List block size: $04900000 + 08800000 = 0D100000\text{ B}$.
    * *Note*: At this stage, sufficient space exists to swap $P_{10}$ back in.

---

### Exercise 2: Hierarchical Paging and EAT Calculation 
**System Specifications:**
* **Virtual Space of $P_1$**: $100\text{ MByte}$.
* **Address Breakdown**: 32-bit logical address split into $p_1$ ($10\text{ bit}$), $p_2$ ($11\text{ bit}$), and $d$ ($11\text{ bit}$).
* **TLB Hit Ratio**: $99\%$.
* **RAM Access Time**: $300\text{ ns}$.

**Step-by-step Solution:**
1.  **Determine Page/Frame Size**: 
    * Derived from the $11\text{ bit}$ displacement ($d$): $2^{11}\text{ Byte} = 2\text{ KByte}$.
2.  **Calculate Page Table Dimensions for $P_1$**:
    * Assume each table entry requires $32\text{ bits}$ ($4\text{ Bytes}$).
    * **Level 2 Table**: Indexed by $p_2$ ($11\text{ bits}$). Entries = $2^{11}$. Size = $2^{11} * 4\text{ Byte}$.
    * **Level 1 Table**: Since $P_1$'s virtual space ($100\text{ MB}$) is strictly less than $128\text{ MB}$ (which is $2^{27}\text{ Byte}$), only $5\text{ bits}$ of the $10$-bit $p_1$ index are required. Entries = $2^5$. Size = $2^5 * 4\text{ Byte}$.
3.  **Calculate Fragmentation for $P_1$**:
    * External: $0$.
    * Internal: $0$, because $100\text{ MByte}$ is a perfect multiple of $2\text{ KByte}$.
4.  **Calculate Effective Access Time (EAT)**:
    * Apply the 3-access rule for a 2-level PT miss.
    * $\text{EAT} = (0.99 * 300 + 0.01 * 3 * 300)\text{ ns}$.
    * $\text{EAT} = 1.02 * 300\text{ ns} = 306\text{ ns}$.

---

### Exercise 3: Standard Page Table vs. Inverted Page Table (IPT) 
**System Specifications:**
* **Virtual Address Space**: $32\text{ GB}$.
* **Physical RAM**: $8\text{ GB}$.
* **Architecture**: 64-bit, byte-addressable.
* **Page/Frame Size**: $1\text{ KB}$.
* **Field Constraints**: PID is $16\text{ bit}$ ($2\text{ B}$); Page/Frame indices are $32\text{ bit}$ ($4\text{ B}$).

**Step-by-step Solution & Comparison:**
1.  **Calculate Standard Page Table Size**:
    * Number of Pages = $\frac{32\text{ GB}}{1\text{ KB}} = 32\text{M}$ entries.
    * Table Size = $32\text{M} * 4\text{ B} = 128\text{ MB}$.
2.  **Calculate Inverted Page Table (IPT) Size**:
    * Number of Frames = $\frac{8\text{ GB}}{1\text{ KB}} = 8\text{M}$ entries.
    * Row Size = Page Index ($4\text{ B}$) + PID ($2\text{ B}$) = $6\text{ B}$ per entry.
    * Table Size = $8\text{M} * (4\text{ B} + 2\text{ B}) = 48\text{ MB}$.
3.  **Determine Maximum Virtual Address Space with given IPT**:
    * Constrained by the $32\text{ bit}$ page index.
    * Maximum Virtual Pages = $2^{32} = 4\text{G}$.
    * Maximum Virtual Space = $4\text{G} * 1\text{ KB} = 4\text{ TB}$.


---
## PART 2
---

# Master Cheat Sheet: System Programming - Memory Management

This document covers practical problem-solving methodologies for memory management, specifically focusing on page replacement algorithms, address translation, and fragmentation.

---

## Major Topics

### 1. Second-Chance Set Page Replacement Algorithm
This section details how to trace the Second-Chance set replacement algorithm given a specific sequence of memory references.

**Scenario Parameters:**
* **Program Size:** 1000 words.
* **Page Size:** 200 words.
* **Available Frames:** 3 (limit of available frames for the resident set).
* **Initial State:** The program is already running. The 3 frames are pre-allocated to pages 4, 3, and 1.
* **FIFO Queue Initial State:** $4_0, 3_1$ (where the subscript represents the reference bit).
* **Rule:** A page fault initializes a page's reference bit to 0.

**Step-by-Step Breakdown:**
1.  **Calculate the Reference String:** To find the page number, integer division is used (Note: Page numbering starts at 0). 
    * *Example:* $261 / 200 = 1$.
    * Memory accesses: 261, 409, 985, 311, 584, 746, 632, 323, 470, 915, 858.
    * Resulting Reference String: 1, 2, 4, 1, 2, 3, 3, 1, 2, 4, 4.

2.  **Execution Trace:**
    * The resident set evolves as follows (Tracking Reference bits and Page Faults):
    * **Ref 1**: Hits page $1_0$.
    * **Ref 2**: Page Fault (PF). Replaces a page. State updates to include $2_0$.
    * **Ref 4**: Page Fault (PF). State includes $4_0$.
    * **Ref 1**: Hit. Updates to $1_1$.
    * **Ref 2**: Hit. Updates to $2_0$.
    * **Ref 3**: Page Fault (PF). State includes $3_0$.
    * **Ref 3**: Hit. Updates to $3_1$.
    * **Ref 1**: Hit. State tracks $1_1$.
    * **Ref 2**: Hit. Updates to $Z_1$ (Note: represented as $Z_1$ in raw output, indicating reference bit set to 1).
    * **Ref 4**: Page Fault (PF). State includes $4_0$.
    * **Ref 4**: Hit. Updates to $4_1$.
* **Final Result:** A total of 5 Page Faults occur.

---

### 2. Paging, Internal Fragmentation, and LRU (Least Recently Used)
This section outlines address translation from hexadecimal to binary, calculation of total pages, fragmentation, and the LRU replacement strategy.

**Scenario Parameters:**
* **Logical/Physical Addresses:** 12 bits.
* **Page Size:** 128 Bytes.
* **Maximum Address:** C10 (hexadecimal).
* **Memory Accesses (R=Read, W=Write):** R 3F5, R 364, W 4D3, W 47E, R 4C8, W 2D1, R 465, W 2A0, R 3BA, W 4E6, R 480, R 294, R 0B8, R 14E.
* **Available Frames:** 3 (at physical addresses 780, A00, B00).

**Step-by-Step Breakdown: Address Space & Fragmentation:**
1.  **Calculate Total Pages:**
    * Max Address $C10_{16} = 1100\ 0001\ 0000_2$.
    * Max page index: $2 * C_{16} = 2 * 12_{10} = 24 \Rightarrow$ Total space includes 25 pages.
    * *Alternative Math Method:* $$C10_{H}+1=3089_{10}$$ 
        $$NP=\lceil3089/128\rceil=25$$ 
2.  **Calculate Internal Fragmentation:**
    * The last page is occupied up to offset $001\ 0000_2$ (16).
    * Since offsets start at 0, 16 means 17 bytes are used.
    * Formula: $128-17=111$ Bytes.
    * *Alternative Math Method:*
        $$128-3089\%128=128-17=111$$ Bytes 

**Step-by-Step Breakdown: LRU Algorithm Trace:**
1.  **Extract Logical Addresses (p, d):**
    * Page size = 128 Bytes $\Rightarrow$ 7 bits needed for displacement ($d$), leaving 5 bits for the page ($p$).
    * *Shortcut for $p$:* Double the first hex digit + the most significant bit (MSB) of the second hex digit.
    * *Example Binaries:* R ($0011\ 1,111\ 0101$), R ($0011\ 0,110\ 0011$), W ($0100\ 1,101\ 0011$).
2.  **Reference String Calculation:**
    * String: 7, 6, 9, 8, 9, 5, 8, 5, 7, 9, 9, 5, 1, 2.
3.  **Resident Set Trace (Frames 780, A00, B00):**
    * *Ref 7:* Frame 780 $\leftarrow$ 7.
    * *Ref 6:* Frame A00 $\leftarrow$ 6.
    * *Ref 9:* Frame B00 $\leftarrow$ 9.
    * *Ref 8:* Frame 780 $\leftarrow$ 8 (PF).
    * *Ref 9:* Hit in B00.
    * *Ref 5:* Frame A00 $\leftarrow$ 5 (PF).
    * *Ref 8, 5:* Hits.
    * *Ref 7:* Frame B00 $\leftarrow$ 7 (PF).
    * *Ref 9:* Frame 780 $\leftarrow$ 9 (PF).
    * *Ref 9, 5:* Hits.
    * *Ref 1:* Frame B00 $\leftarrow$ 1 (PF).
    * *Ref 2:* Frame 780 $\leftarrow$ 2 (PF).
    * **Note:** Logical page 7 is placed in two different frames (780 and B00) at different times during execution.
* **Final Result:** A total of 9 Page Faults occur.

**Step-by-Step Breakdown: Physical Address Translation:**
* R 3F5 ($0011\ 1,111\ 0101_2$) $\Rightarrow$ R ($0111\ 1,111\ 0101_2$) = 7F5.
* W 4D3 ($0100\ 1,101\ 0011_2$) $\Rightarrow$ W ($1011\ 0,101\ 0011_2$) = B53.
* R 3BA ($0011\ 1,011\ 1010_2$) $\Rightarrow$ R ($1011\ 0,011\ 1010_2$) = B3A.

---

### 3. Enhanced Second-Chance Algorithm
This section demonstrates the Enhanced Second-Chance (Clock) algorithm utilizing both a Reference bit and a Modify bit.

**Scenario Parameters:**
* **Program Size:** 4K words.
* **Page Size:** 512 words ($2^9$).
* **Frames Available:** 3.
* **Algorithm Rules:**
    * State is represented as `(reference, modify)`. Reference bit initializes to 0 on the first access after a page fault.
    * A page is always modified (modify bit = 1) upon a Write (W).
    * **Pass 1:** Search for victim without modifying reference bits. Priority order: `(0,0), (0,1), (1,0), (1,1)`.
    * **Pass 2:** Once the victim is found, zero out the reference bits of the "saved" pages that were bypassed (from starting pointer up to the victim).

**Address Calculation Rules:**
* Every hexadecimal digit represents 4 bits.
* To divide by $512$ ($2^9$), eliminate the two least significant hexadecimal digits (8 bits) and divide the first hex digit by 2.

**Memory Access Sequence & Reference String:**
* **Accesses:** W 3A1, R 3F5, R A64, W BD3, W 57E, R A08, R B85, W 3A0, R A1A, W A36, R B20, R 734, R AB8, R C4E, W B64.
* **Read/Write Operations:** W, R, R, W, W, R, R, W, R, W, R, R, R, R, W.

**Resident Set & Algorithm Trace:**
*(Format: $Page_{Reference,Modify}$)* 
* **Access 1:** $1_{01}$ (Page Fault: X)
* **Access 2:** $1_{11}$ 
* **Access 3:** $1_{11}$, $5_{00}$ (Page Fault: X)
* **Access 4:** $1_{11}$, $5_{11}$
* **Access 5:** $1_{11}$, $5_{11}$, $2_{01}$ (Page Fault: X)
* **Subsequent states track the priority search:** The FIFO pointer scans the states. For example, states evolve through $1_{11}, 5_{11}, 2_{01}$ maintaining the `(1,1)` modifications from continuous writes/reads to pages 1 and 5.
* When a victim must be selected, pages degrade their reference bits (e.g., $1_{11}$ becomes $1_{01}$, $5_{11}$ becomes $5_{01}$) as the pointer passes them during the search for `(0,0)` or `(0,1)`.
* Later allocations include page 3 ($3_{00}$) and page 6 ($6_{00}$) replacing the lowest priority targets.

* **Final Result:** A total of 5 Page Faults occur.

### 1. Granular Trace: Second-Chance Set Algorithm (Exercise 1)
Here is the exact progression of references, resident set bits, and page faults as extracted from the raw document trace:

* **String of References:** 1, 2, 4, 1, 2, 3, 3, 1, 2, 4, 4 
* **Frame 1 Trace (including reference bits):** $4_{0}$, $4_{0}$, $2_{0}$, $4_{c}$, $4_{0}$, 40, $3_{c}$, $3_{1}$, $3_{1}$, $3_{1}$, 30, 30, $3_{1}$, $3_{1}$, $3_{1}$, $\underline{30}$, $\underline{30}$ 
* **Frame 2 Trace:** 20, $\underline{2_{0}}$, $2_{0}$, $2_{0}$, $Z_{1}$, $4_{0}$, $4_{1}$ 
* **Frame 3 Trace:** $1_{0}$, $1_{1}$, $T_{1}$, 10, $1_{1}$, 11, $1_{0}$, $1_{0}$, 11, 11, $1_{0}$, $1_{0}$ 
* **Page Faults (PF):** PF PF, PF PF, PF 

---

### 2. Granular Trace: LRU Algorithm (Exercise 2)
Here is the exact step-by-step resident set and page fault trace for the LRU algorithm across the 3 physical frames (780, A00, B00):

* **Riferimenti (References):** 7, 6, 9, 8, 9, 5, 8, 5, 7, 9, 9, 5, 1, 2
* **Resident Set (Frame 780):** 780 7, 7, 7, 8, 8, 8, 9, 9, 2
* **Resident Set (Frame A00):** 6, 6, 6, 5, 5, 5, 5, 5 
* **Resident Set (Frame B00):** 9, 9, 9, 7, 7, 1, 1 
* **Page Faults (marked by *):** \*, \*, \*, \*, \*, \*, \*, \* 

---

### 3. Granular Trace: Enhanced Second-Chance Algorithm (Exercise 3)
Here is the exact state table provided in the document for the Enhanced Second-Chance algorithm, tracking the `(reference, modify)` bits for every single memory access:

| Riferimenti | 1 | 1 | | 5 | 2 | 5 | | 5 | 5 | 5 | 1 | 5 | | | 5 | 3 | 5 | 5 | 6 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Read/write** | WR | | | RWW | | R | | RWRW | | | R | R | R | RW | | | | | |
| **Resident Set** | $1_{01}$ | $1_{11}$ | $1_{11}$<br>$5_{00}$ | $1_{11}$<br>$5_{11}$ | $1_{11}$<br>$5_{11}$<br>$2_{01}$ | $1_{11}$<br>$5_{11}$<br>$2_{01}$ | $1_{11}$<br>$5_{11}$<br>$2_{01}$ | $1_{11}$<br>$1_{11}$<br>$5_{11}$<br>$5_{11}$<br>$2_{01}$<br>$2_{01}$ | | $1_{11}$<br>$5_{11}$<br>$2_{01}$ | $1_{11}$<br>$5_{11}$<br>$2_{01}$ | $1_{01}$<br>$5_{01}$<br>$3_{00}$ | $1_{01}$<br>$5_{11}$<br>$3_{00}$ | $1_{01}$<br>$1_{01}$<br>$5_{01}$<br>$5_{11}$<br>600<br>$6_{00}$ | | | | | |
| **Page Fault** | X | | X | X | | | | | | | X | | X | | | | | | |

*(Note: The table formatting above perfectly mirrors the layout and raw spacing of the CSV data provided in the original document text for Exercise 3 )*

## Major Topics: Memory Management & Algorithms

### 1. Working-Set Page Replacement (Exact Version)
* **Concept**: A page replacement algorithm that maintains a "window" of the most recently used pages.
* **Window Size ($\Delta$)**: Determines how many of the most recent memory accesses are considered part of the active working set.
* **Resident Set**: The set of pages currently loaded in memory frames.
* **Page Fault (PF)**: Occurs when an accessed page is not currently present in the resident set.
* **Page Out (PO)**: Occurs when a page is removed from the resident set because it falls outside the active window $\Delta$.

**Strict Frame Placement Rules (Hardware/Architecture Limits):**
* Each row in a resident set simulation represents a distinct physical frame.
* A page present in a frame cannot change its row (frame) while it remains in the resident set.
* **Page-Fault without Page-Out**: The algorithm utilizes the first free frame starting from the top.
* **Simultaneous Page-Out & Page-Fault**: The system reuses the exact frame that was just freed by the page-out.
* **Cancellation Rule**: If a page-out and a page-fault occur at the exact same time for the *same* page, the algorithm prevents both actions, keeping the page in memory without registering a PF or PO.

### 2. Program Locality Metrics

**Metric A: Reuse Distance ($RD$)**
* **Definition**: The Reuse Distance at time $T_i$ ($RD_i$) for an accessed page $P_i$ is defined as the number of *distinct* pages accessed since the previous access to that same page $P_i$.
* **First Access Rule**: For the very first access to any page, the $RD_i$ is conventionally set to the total number of distinct pages accessed up to that moment.
* **Example**: If the string is `..., 5, 7, 7, 5`, at the second access of `5`, the distance is `1` because only one distinct page (`7`) was accessed in between.
* **Locality Formula ($L$)**: The locality based on Reuse Distance is calculated as $L = \frac{1}{1 + RD_{avg}}$, where $RD_{avg}$ is the average of all individual $RD_i$ values.

**Metric B: Access-Based Locality ($L$)**
* **Definition**: A locality metric used when evaluating memory accesses in code blocks.
* **Variables**: 
    * $N_T$: Total number of memory accesses to data.
    * $N_L$: Number of accesses to data residing in the same page as one of the previous 10 accesses.
* **Formula**: $L = \frac{N_L}{N_T}$.

---

## Practical Exercises: Walkthroughs & Solutions

### Exercise 1: Working-Set & Reuse Distance Calculation 
* **Scenario**: Working-set exact algorithm with window $\Delta=3$ and a maximum of 3 frames available.
* **Reference String**: `5, 7, 7, 5, 1, 7, 1, 1, 1, 4, 3, 4, 1, 2, 3`.
* **Goal**: Calculate PF, PO, $RD_i$, $RD_{avg}$, and $L$.

**Step-by-Step Simulation Table:**

| Time/Access | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Riferimenti** | **5** | **7** | **7** | **5** | **1** | **7** | **1** | **1** | **1** | **4** | **3** | **4** | **1** | **2** | **3** |
| Frame 1 | 5 | 5 | 5 | 5 | 5 | 5 | | | | 4 | 4 | 4 | 4 | 4 | 3 |
| Frame 2 | | 7 | 7 | 7 | 7 | 7 | 7 | 7 | | | 3 | 3 | 3 | 2 | 2 |
| Frame 3 | | | | | 1 | 1 | 1 | 1 | 1 | 1 | 1 | | 1 | 1 | 1 |
| **Page Fault** | X | X | | | X | | | | | X | X | | X | X | X |
| **Page Out** | | | | | | | | X | | X | | | X | X | X |
| **RD** | 0 | 1 | 0 | 1 | 2 | 2 | 1 | 0 | 0 | 3 | 4 | 1 | 2 | 5 | 3 |

*Note: The choice of frame assignment is arbitrary; permuted frames are valid as long as max frames $\le 3$.*

**Mathematical Breakdown:**
* **Total Page Faults**: 8.
* **Total Page Outs**: 5.
* **Calculate $RD_{avg}$**: Sum of all $RD$ values is $0+1+0+1+2+2+1+0+0+3+4+1+2+5+3 = 25$. Total accesses = $15$.
    $$RD_{avg} = \frac{25}{15} = \frac{5}{3} \approx 1.67$$ 
* **Calculate $L$**: 
    $$L = \frac{1}{1 + \frac{5}{3}} = \frac{1}{\frac{8}{3}} = \frac{3}{8} = 0.375$$

---

### Exercise 2: Repeated Reference Strings & Cyclic Behavior 
* **Scenario**: Working-set exact algorithm, window $\Delta=3$.
* **Reference String**: `3, 4, 1, (3, 1, 4, 4, 3, 1, 1)*10`.
* *(...)\*n syntax implies a looping construct repeated n times.*
* **Goal**: Track resident set for the initial setup and the first two iterations of the loop, then deduce total PFs and POs.

**Step-by-Step Simulation Table:**

| Tempo | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Riferimenti** | **3** | **4** | **1** | **3** | **1** | **4** | **4** | **3** | **1** | **1** | **3** | **1** | **4** | **4** | **3** | **1** | **1** |
| Frame 1 | 3 | 3 | 3 | 3 | 3 | | | 3 | 3 | 3 | 3 | | | 4 | 4 | 4 | |
| Frame 2 | | 4 | 4 | 4 | | | 4 | 4 | 4 | | | 1 | 1 | 1 | 1 | 1 | 1 |
| Frame 3 | | | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 4 | | 3 | 3 | 3 |
| **Page Fault** | X | X | X | | | X | | X | | | | | X | | X | | |
| **Page Out** | | | | X | | | X | | X | X | | X | | X | | X | |

*Table data derived directly from the source.*

**Cyclic Behavior Analysis:**
* **Question**: Will the next 8 missing iterations behave exactly like the interval 10-16 repeated 8 times?
    * *Answer*: **NO**. While the period is 7 clock ticks long, pages 1 and 3 are not physically located in the same hardware frames at the beginning vs the end of the period.
* **Question**: Will it repeat the interval 3-16 four times?
    * *Answer*: **NO**. The first period has distinct initial behavior because page 4 is present at time 3, which is not true for subsequent cycles.
* **Actual Configuration**: The system repeats the interval 10-16 eight times, but it strictly alternates the contents of the first and third memory frames with each iteration. Alternatively, it repeats the 3-16 block four times, *only if* page 4 at time 3 and the page-out at time 4 are removed.
* **Final Calculation**: 
    * Visualized part: 9 PF, 7 PO.
    * Missing part (8 iterations): $8 \times (3 \text{ PF and } 3 \text{ PO})$.
    * Total PF: $9 + 24 = 33$ PF.
    * Total PO: $7 + 24 = 31$ PO.

---

### Exercise 3: C Code Compilation, Paging & Locality 
* **System Specs**: Paging active, 2KB page size, SECOND CHANCE replacement policy. `float` size = 32 bits (4 bytes). Instructions fit in 1 page.
* **Memory Allocation**: Matrices `M` and `V` are contiguous (M first, then V), starting at logical address `0x5524AE00`. Allocated "row major".
* **Target Code**:
```c
float M[512][512], V[512];
for (i=0; i<512; i++) {
    V[i]=0;
    for (j=0; j<=i; j++) {
        if (i%2==0) {
            V[i] += M[i][j];
        } else {
            V[i] -= M[i][511-j];
        }
    }
}
```

**Step 1: Paging and Memory Boundaries **
* **Size of Vector V**: $512 \text{ floats} \times 4 \text{ bytes} = 2\text{KB}$. Since 1 page = 2KB, ideally $V$ requires 1 page.
* **Size of Matrix M**: $512 \times 512 \text{ floats} \times 4 \text{ bytes} = 1\text{MB}$. $1\text{MB} / 2\text{KB} = 512 \text{ pages}$.
* **Address Alignment Rule**: The start address `0x5524AE00` is **NOT** page-aligned. A 2KB page requires the last 11 bits to be `0`. Because it starts in the middle of a page, a boundary correction is required: $V$ straddles 2 pages, and $M$ occupies 513 pages (sharing the first page with $V$).

**Step 2: Memory Access Calculations (Reads/Writes) **
* Outer loop ($N_i$): $512$ iterations. `V[i]=0` executes 512 times = **512 Writes**.
* Inner loop ($N_j$): Iterates $j=0$ to $j \le i$. Total inner iterations:
    $$N_j = \sum_{i=0}^{511}(i+1) = \frac{512 \times (512+1)}{2} = 128\text{K} + 256 = 131328$$ 
* Inside the inner loop: `V[i] += M...` requires **2 Reads** (`V[i]`, `M[...]`) and **1 Write** (`V[i]`) per iteration.

*Detailed breakdown of Even vs Odd iterations (Exact Math):*
* Even $i$ ($N_{j,0}$), assuming $k = i/2$: 
    $$N_{j,0} = \sum_{k=0}^{255}(2k+1) = 2 \times \sum_{k=0}^{255}(k+1) - 256 = 256 \times 257 - 256 = 256^2 = 65536$$ 
* Odd $i$ ($N_{j,1}$): 
    $$N_{j,1} = \sum_{k=0}^{255}(2k+2) = 2 \times \sum_{k=0}^{255}(k+1) = 256 \times 257 = 65792$$ 
* *Alternative Math *: The total iterations equal half the matrix plus half the diagonal: $\frac{512 \times 512}{2} + 256 = 131328$. Odd iterations outnumber even by 256. Therefore: $2 \times N_{j,0} + 256 = 131328 \rightarrow N_{j,0} = 65536$ ($64\text{K}$), $N_{j,1} = 65792$.

**Step 3: Calculating Data Locality ($L = N_L / N_T$) **
*(Assumption for exercise: Ideal page alignment used for simplicity )*
* Traversing a row forwards or backwards has no impact on locality or page faults because an entire row of $M$ fits exactly inside one 2KB page.
* **Matrix M accesses**: For each of the 512 rows, only the very first access ($j=0$) is a non-local miss (accessing a new page). Subsequent accesses in that row are hits. Total non-local accesses to $M = 512$.
* **Vector V accesses**: Since $V$ fits in a single page, only the first access is a miss. Total non-local accesses to $V = 1$.
* Total non-local accesses = $512 + 1 = 513$.
* Total Accesses ($N_T$) = Azzeramenti (512) + $3 \times N_j$ (2 read, 1 write per inner loop).
    $$N_T = 512 + 3 \times (131328) = 512 + 393984 = 394496$$
* Local Accesses ($N_L$) = $N_T - 513$.
* **Locality Calculation**:
    $$L = \frac{N_T - 513}{N_T} = 1 - \frac{513}{512 + 3 \times (128\text{K} + 256)} = 1 - \frac{512}{3 \times 128\text{K}} \approx 1 - 0.0013 = 0.9987$$

**Step 4: Page Fault Calculation **
* **Scenario**: 10 frames allocated. 1 frame is permanently locked for instructions.
* Vector $V$: Generates 1 page fault. *(2 page faults if strictly calculating for the non-alignment edge case ).*
* Matrix $M$: Generates 1 page fault for every single row/page as it is accessed sequentially. Total = 512 page faults.
* **Total Page Faults**: $1 + 512 = 513$. *(Or $2 + 512 = 514$ if factoring in the `0x5524AE00` misalignment ).*
