## Virtual Memory Basics

### Core Concepts
*   **Virtual Memory:** The separation of user logical memory from physical memory[cite: 3].
*   **Benefits:** Allows a program to be larger than physical memory, allows processes to share files/memory, allows more concurrent programs to run, and requires less I/O to load or swap processes[cite: 3].
*   **Virtual Address Space:** The logical view of how a process is stored in memory, usually starting at address 0 and contiguous, while underlying physical pages may be non-contiguous[cite: 3].
*   **Demand Paging:** A technique where pages are loaded into memory only as they are demanded (needed) during execution[cite: 3].
*   **Zero-Fill-On-Demand:** A technique where the OS zeroes out the contents of a free frame before allocating it to a process[cite: 3].
*   **Copy-on-Write (COW):** Allows parent and child processes to initially share the same pages in memory[cite: 3]. A copy of a shared page is only created if either process modifies it[cite: 3].

### Page Fault Handling
A page fault occurs when a process attempts to access a page marked as "invalid" (not currently in memory)[cite: 3]. 

**Steps to Handle a Page Fault:**
1. Check the internal table to determine if the memory reference was valid or invalid[cite: 3].
2. If invalid, terminate the process. If valid but not in memory, trigger a trap to the OS[cite: 3].
3. Find a free frame (from the free-frame list)[cite: 3].
4. Schedule a disk operation to read the desired page into the newly allocated frame[cite: 3].
5. Reset the page table to indicate the page is now in memory (Valid-Invalid bit set to "valid")[cite: 3].
6. Restart the instruction that was interrupted by the trap[cite: 3].

---

## Performance & Effective Access Time (EAT)

Demand paging performance depends heavily on the page-fault rate ($p$), where $0 \le p \le 1$[cite: 3]. 
*   If $p = 0$, there are no page faults[cite: 3].
*   If $p = 1$, every reference causes a fault[cite: 3].

**EAT Formula:**
$$EAT = (1 - p) \times \text{memory access} + p \times (\text{page fault overhead} + \text{swap page out} + \text{swap page in})$$[cite: 3]

*   **Modify (Dirty) Bit:** Hardware sets this bit if a page is written to[cite: 3]. If the modify bit is set, the page must be written to storage before being replaced; if not set, writing to storage can be skipped, cutting the page-fault service time in half[cite: 3].

---

## Page Replacement Algorithms

When memory is over-allocated and no frames are free, the OS must select a "victim" frame to replace[cite: 3]. 

### Basic Algorithms
*   **FIFO (First-In-First-Out):** Replaces the oldest page brought into memory using a queue[cite: 3].
    *   *Belady’s Anomaly:* A phenomenon unique to FIFO (and some others) where allocating *more* physical frames actually *increases* the page-fault rate for certain reference strings[cite: 3].
*   **Optimal (OPT):** Replaces the page that will not be used for the longest period of time in the future[cite: 3]. It guarantees the lowest possible page-fault rate but is impossible to implement in practice; it is used as a benchmark for other algorithms[cite: 3].
*   **LRU (Least Recently Used):** Replaces the page that has not been used for the longest amount of time in the past[cite: 3]. It does not suffer from Belady's Anomaly and is typically implemented using counters or a stack[cite: 3].

### LRU Approximations
Because true LRU requires hardware support and can be slow, systems use **Reference Bits** (initially 0, set to 1 by hardware when the page is accessed)[cite: 3].
*   **Second-Chance (Clock) Algorithm:** FIFO-based[cite: 3]. If the chosen page's reference bit is 0, replace it[cite: 3]. If it is 1, clear the bit to 0, give it a "second chance", and move to the next page in the circular queue[cite: 3].
*   **Enhanced Second-Chance:** Uses both the Reference Bit and Modify Bit to group pages into four classes to find a victim[cite: 3]:
    1.  **(0, 0):** Neither recently used nor modified (Best to replace)[cite: 3].
    2.  **(0, 1):** Not recently used but modified (Must write out before replacing)[cite: 3].
    3.  **(1, 0):** Recently used but clean[cite: 3].
    4.  **(1, 1):** Recently used and modified (Worst to replace)[cite: 3].

### Other Algorithms
*   **Counting-Based:** Keeps a counter of references[cite: 3]. Includes **LFU** (Least Frequently Used) and **MFU** (Most Frequently Used)[cite: 3].
*   **Page-Buffering:** Keeps a pool of free frames at all times[cite: 3]. The desired page is read into a free frame immediately, and the victim page is written out to disk afterward[cite: 3].

---

## Frame Allocation & Thrashing

### Frame Allocation Strategies
*   **Equal Allocation:** Splits $m$ total frames equally among $n$ processes ($m/n$ frames per process)[cite: 3].
*   **Proportional Allocation:** Allocates frames to processes based on the size of their virtual memory[cite: 3].
*   **Global Replacement:** A process selects a replacement frame from the pool of all frames, potentially stealing from another process (yields higher throughput)[cite: 3].
*   **Local Replacement:** A process selects a replacement only from its own allocated frames (provides more consistent per-process performance)[cite: 3].
*   **Reclaiming Pages (Reapers):** A kernel routine triggers when free memory falls below a minimum threshold, reclaiming pages until free memory hits a maximum threshold[cite: 3].

### Thrashing
*   **Thrashing:** Occurs when a process does not have enough frames and spends more time paging (swapping) than executing, leading to plummeted CPU utilization[cite: 3].
*   **Locality Model:** A running program moves through different "localities" (sets of pages actively used together)[cite: 3]. Thrashing happens if a process's allocated frames are smaller than its current locality[cite: 3].
*   **Working-Set Model:** Uses a parameter $\Delta$ (working-set window) to look at the most recent page references[cite: 3]. The set of unique pages in $\Delta$ is the "Working Set" and approximates the program's locality[cite: 3].
*   **Page-Fault Frequency (PFF):** Establishes acceptable upper and lower bounds on page-fault rates[cite: 3]. If the rate exceeds the upper bound, the process is given another frame; if it drops below the lower bound, frames are removed[cite: 3].

---

## Kernel Memory Allocation

Kernel memory is often allocated from a different pool than user memory because the kernel needs contiguous physical memory and creates data structures of varying sizes that must minimize fragmentation[cite: 3].

*   **Buddy System:** Allocates memory using a power-of-2 allocator[cite: 3]. If a request is smaller than the available chunk, the chunk is split into two equal "buddies" until an appropriately sized chunk is found[cite: 3]. When released, adjacent free buddies are rapidly coalesced back together[cite: 3].
*   **Slab Allocation:** A cache is created for each unique kernel data structure, and each cache is made of one or more "slabs" (contiguous physical pages)[cite: 3]. The cache is filled with exact instantiations ("objects") of the data structure, entirely eliminating fragmentation[cite: 3].

---

## System Architecture & OS Specifics

*   **Prepaging:** Loading all or some of a process's pages before they are referenced to reduce startup page faults[cite: 3].
*   **TLB Reach:** Defined as $(\text{TLB Size}) \times (\text{Page Size})$[cite: 3]. To increase reach, systems can increase the page size or provide multiple page sizes[cite: 3].
*   **I/O Interlock (Pinning):** Pages currently copying data to/from an I/O device must be "locked" or "pinned" in memory so they aren't evicted by a replacement algorithm[cite: 3].
*   **NUMA (Non-Uniform Memory Access):** In multi-CPU systems, a CPU can access its own local memory faster than the local memory of another CPU[cite: 3].
*   **Windows Implementation:** Uses demand paging with clustering (brings in pages surrounding the faulting page), assigns working set minimums/maximums, and utilizes automatic working set trimming[cite: 3].
*   **Solaris Implementation:** Maintains `lotsfree`, `desfree`, and `minfree` thresholds to dictate paging and swapping aggression[cite: 3]. A `pageout` process uses a modified clock algorithm with adjustable scan rates (`slowscan` to `fastscan`)[cite: 3].


## Part 2: Virtual Memory Practical Exercises

### 1. Matrix Initialization Page Faults (Row-Major vs. Column-Major)
The order in which nested loops access arrays drastically affects page faults due to memory layout (usually row-major order) and page sizes[cite: 3].
*   **Scenario:** Array `int A[100][100]` with a page size of 200 integers, using 3 frames (1 for the process, 2 empty for data)[cite: 3].
*   **Column-Major Access (Bad Locality):** Outer loop iterates columns (`j`), inner loop iterates rows (`i`)[cite: 3]. Accessing `A[i][j]` jumps across pages continuously[cite: 3]. 
    *   *Result:* 5,000 page faults[cite: 3].
*   **Row-Major Access (Good Locality):** Outer loop iterates rows (`i`), inner loop iterates columns (`j`)[cite: 3]. Accessing `A[i][j]` reads sequentially through the page before needing a new one[cite: 3].
    *   *Result:* 50 page faults[cite: 3].

### 2. Inverted Page Table Physical Address Calculation
*   **Scenario:** 64-bit system, $2^{48}$ byte virtual address space, 4 KB ($2^{12}$) page size, 16 GB ($2^{34}$) physical memory[cite: 3].
*   **Physical Frame Number Size:** $\frac{2^{34}}{2^{12}} = 2^{22}$ physical frames, so the physical frame number requires **22 bits**[cite: 3]. Total entries in the inverted page table equals the number of physical frames ($2^{22}$)[cite: 3].
*   **Calculating Physical Address from Virtual Address (`0x00007FFFFFFFF000` mapped to the 1024th frame):**
    1.  Offset = lower 12 bits (from 4 KB page size). The last 3 hex digits `000` represent the offset[cite: 3].
    2.  Frame number = 1024 (which is `0x00000400` in Hex)[cite: 3].
    3.  Physical Address = `(Frame Number << 12) | Offset`[cite: 3].
    4.  $0x00000400 \ll 12 = 0x00000400000$[cite: 3].
    5.  Final Address = `0x00000400000` + `0x000` = **`0x00000400000`**[cite: 3].

### 3. Reuse Distance and Locality ($L$)
"Reuse Distance" measures program locality[cite: 3]. 
*   **Reuse Distance ($RD_i$):** The number of *distinct* pages accessed between the previous access to page $i$ and the current access to page $i$[cite: 3]. For the very first access to a page, $RD$ equals the total number of pages accessed up to that point[cite: 3].
*   **Average Reuse Distance ($RD_{avg}$):** The sum of all $RD_i$ values divided by the total number of references[cite: 3].
*   **Locality ($L$):** Calculated as $L = \frac{1}{1 + RD_{avg}}$[cite: 3].

### 4. Internal Fragmentation Calculation (Hex & Binary)
*   **Scenario:** 12-bit addresses, 128 Byte ($2^7$) page size, Max virtual address is `0xC10`[cite: 3].
*   **Conversion:** `0xC10` in binary is `1100 0001 0000`[cite: 3].
*   **Split Address:** The lower 7 bits (`001 0000`) are the offset, and the upper 5 bits (`11000` or 24 in decimal) are the page number[cite: 3].
*   **Fragmentation Math:** The last page only uses up to offset `001 0000` (which is $2^4 = 16$, representing bytes 0 through 16, or 17 total bytes used)[cite: 3]. 
*   **Waste:** Page size (128) - Used bytes (17) = **111 bytes of internal fragmentation**[cite: 3].

### 5. Standard Algorithm Fault Comparisons
*   Given reference string `7,2,3,1,2,5,3,4,6,7,7,1,0,5,4,6,2,3,0,1` with 3 frames:
    *   **LRU:** 18 faults[cite: 3].
    *   **FIFO:** 17 faults[cite: 3].
    *   **Optimal:** 13 faults[cite: 3].