Here is the exhaustive master cheat sheet based on the provided OS161 System Programming lecture document.

# OS161 Address Space & Memory Management - Master Cheat Sheet

## 1. OS161 Memory Management Overview
### DumbVM and Kmalloc Interfaces
Memory management in OS161 relies on two primary interfaces:
*   **`kmalloc`**: Handles kernel memory allocation.
*   **`dumbvm`**: Handles user memory allocation.

### Allocation Model and Limitations
*   Memory is allocated strictly in pages.
*   The standard page size is 4KB ($4096 \text{ Bytes}$).
*   A strict requirement is that allocated pages must be contiguous in physical memory.
*   **DumbVM Limitations:** It is called "dumb" because it lacks advanced memory features. Specifically, it has no real virtual memory, no page table, no swapping, and no page replacement mechanisms.

---

## 2. MIPS Virtual Address Space Architecture
OS161 is designed to run on a MIPS processor, which is a 32-bit architecture. Therefore, addresses are 32 bits long, resulting in a total logical address space of 4 GB ($2^{32} \text{ bytes}$).

MIPS partitions this 4 GB virtual address space into specific segments:

### User Space Segment
*   **`kuseg` (2GB)**: Dedicated to user space. It spans the lower half of the memory and is TLB mapped. Address boundary starts at `0x00000000` and ends at `0x80000000`.

### Kernel Space Segments (2GB Total)
MIPS maps the OS kernel directly into the logical memory space of the process. Consequently, the process "sees" both the user space and kernel space within its memory. 
*   **`kseg0` (0.5GB)**: Used for the Kernel. It is TLB unmapped but **cached**. Address range is `0x80000000` to `0xa0000000`. 
*   **`kseg1` (0.5GB)**: Used for I/O devices. It is TLB unmapped and **uncached**. Address range is `0xa0000000` to `0xc0000000`.
*   **`kseg2` (1GB)**: Not used by the system. It is TLB mapped. Address range is `0xc0000000` to `0xffffffff`.

*(Note: During OS161 boot, the kernel is mapped to a physical address which is later mapped into the process's logical memory via the TLB.)*

---

## 3. Kernel Loader & Boot Time Execution
During the boot phase, the OS uses a specific portion of memory to load the OS161 kernel starting from address 0. The loader is handled by `sys161: start.S`.

### Memory Mapping Layout During Boot
Below is the exact logical-to-physical address mapping mapping trace during boot (mapped within `KSEG0`):

| Logical Address (KSEG0) | Physical Address | Memory Content |
| :--- | :--- | :--- |
| `0x80000000` | `0x0` | Exception handlers |
| `0x80000200` | `0x200` | Kernel |
| `0x80039d54` (`_end`) | `0x39d54` | Arg string for boot + Page align |
| `0x8003a000` (P) | `0x3a000` | Stack for first thread (1 page = 4096 B) |
| `0x8003b000` (`firstfree`) | `0x3b000` (`firstpaddr`) | **FREE MEMORY** (Start of available RAM) |
| `0x80100000` | `0x100000` | `ramsize` (e.g., 1MB defined in `sys161.conf`) |

**Boot Phase Conclusion:** At the end of the boot phase, the OS saves the first available physical address (`firstpaddr`), marking the beginning of Free Memory. 

### Complete Physical Memory Layout
The physical memory starts from the first free address (`firstpaddr`) and continues up to the total dimension of the memory (`ramsize`). 
*   The address of `firstpaddr` is dynamic and depends entirely on the size of the compiled kernel. 
*   The last address depends on the total RAM size configured for the system.

---

## 4. Memory Manager Architecture & Code Execution
Memory allocation is split into two distinct paths (User Space vs Kernel Space), but both eventually converge on a common low-level allocation mechanism.

### Allocation Paths
*   **User Space Allocation (`dumbvm.c`):** 
    1. Called when a program is loaded. 
    2. Requests $n$ contiguous pages.
    3. Calls `as_prepare_load()`.
    4. Calls `getppages()`.
*   **Kernel Space Allocation (`kmalloc.c` & `kpages.c`):**
    1. Request dynamic kernel allocation.
    2. Calls `kmalloc()` (in `kern/vm/kmalloc.c`).
    3. Converts requested size to pages.
    4. Calls `alloc_kpages()` (in `kern/vm/kpages.c`).
    5. Requests $n$ contiguous pages.
    6. Calls `getppages()` (in `dumbvm.c`).
*   **Common Allocation Path:** 
    Both domains invoke `getppages()` $\rightarrow$ `ram_stealmem()` (in `ram.c`) $\rightarrow$ Returns `paddr()` (the physical address of the first allocated page).

### Architecture-Dependent Allocation: `ram_stealmem`
This function handles low-level memory management and is architecture-dependent (located in `kern/arch/mips/vm/ram.c`). If you want to change from contiguous allocation to another model, this module must be modified.

It calculates the size needed using the formula: 
$size = npages \times PAGE\_SIZE$

```c
// kern/arch/mips/vm/ram.c
paddr_t ram_stealmem (unsigned long npages) {
    paddr_t paddr;
    size_t size = npages * PAGE_SIZE;

    // Checking if the requested allocation exceeds physical memory
    if(firstpaddr + size > lastpaddr) {
        return 0; // Fails to allocate memory
    }

    // Successful memory allocation
    paddr = firstpaddr;
    firstpaddr += size; // Advances the free memory pointer
    return paddr; // Returns address of the first available physical free memory
}
```
*   **Parameters:** `npages` is the number of pages requested from the OS.
*   **Failure Condition:** If the `firstpaddr` + requested `size` is greater than `lastpaddr`, the system returns `0` to indicate allocation failure.

### DumbVM Abstraction: `getppages`
Located in `kern/arch/mips/vm/dumbvm.c`, this function acts as an intermediary, asking for a specific number of physical pages and returning a pointer to that memory zone.

```c
// kern/arch/mips/vm/dumbvm.c
static paddr_t getppages (unsigned long npages) {
    paddr_t addr;
    
    spinlock_acquire(&stealmem_lock); // Acquires lock for mutual exclusion
    addr = ram_stealmem (npages);
    spinlock_release(&stealmem_lock); // Releases lock
    
    return addr;
}
```
*   **Concurrency Control:** The `spinlock` allows mutual exclusion when multiple processes are running, preventing the corruption of the `ram_stealmem` function.

---

## 5. Practical Exercises & Development Requirements

### Scenario: The Missing Memory Deallocation Paths
The document outlines a critical flaw/to-do item in the current OS161 DumbVM implementation.

*   **Current State:** The system correctly implements memory **allocation** (`alloc_kpages` for the kernel, and `as_prepare_load` for the user space).
*   **The Issue:** The functions responsible for **releasing** memory are strictly defined but left EMPTY.
*   **Unimplemented Functions:**
    *   `free_kpages` (Kernel side equivalent of `alloc_kpages`).
    *   `as_destroy` (User side equivalent of `as_prepare_load`).

### Your Task / Assignment
**"Your Job to solve this issue."**
You must implement the logic to track, reclaim, and free physical pages. This requires tracing the execution path from `free_kpages` and `as_destroy` down into `dumbvm.c` and subsequently down into `ram.c` to effectively return memory addresses to the system's pool of available physical memory.

To solve this, you must replace the default "bump allocator" in `ram.c` with a tracked memory system (a Core Map) so the system remembers the size and state of allocated page chunks.

### 1. Implement the Core Map Data Structure
You need a data structure to track the allocation state of every physical page in RAM.

```c
/* Add this to a header file (e.g., kern/include/vm.c or dumbvm.h) */

struct coremap_entry {
    int is_allocated;  /* 0 if free, 1 if allocated */
    int chunk_size;    /* Number of contiguous pages allocated together */
};

/* Global pointer to the coremap array */
struct coremap_entry *coremap;
```

### 2. Create the Low-Level Free Function (`freeppages`)
Create the architectural inverse of `getppages` to update the core map when memory is returned. 

```c
/* Add this to kern/arch/mips/vm/dumbvm.c */

void freeppages(paddr_t addr) {
    int index;
    int i;
    int chunks;

    /* Lock the memory system to prevent race conditions */
    spinlock_acquire(&stealmem_lock);

    /* Calculate the core map index based on the physical address */
    index = addr / PAGE_SIZE;

    /* Retrieve how many contiguous pages were allocated here */
    chunks = coremap[index].chunk_size;

    /* Mark all pages in this chunk as free */
    for (i = 0; i < chunks; i++) {
        coremap[index + i].is_allocated = 0;
        coremap[index + i].chunk_size = 0;
    }

    spinlock_release(&stealmem_lock);
}
```

### 3. Solution for `free_kpages` (Kernel Space)
This function takes a **virtual address** used by the kernel, converts it to a physical address, and passes it to your low-level free function.

```c
/* Update this in kern/vm/kpages.c (or wherever free_kpages is stubbed) */

void free_kpages(vaddr_t addr) {
    paddr_t paddr;

    if (addr == 0) {
        return;
    }

    /* Convert MIPS kernel virtual address (kseg0) to physical address */
    /* OS161 provides KVADDR_TO_PADDR macro, or you can manually subtract 0x80000000 */
    paddr = KVADDR_TO_PADDR(addr); 

    /* Free the physical pages */
    freeppages(paddr);
}
```

### 4. Solution for `as_destroy` (User Space)
This function tears down a user process's address space when it exits, freeing the code, data, and stack segments.

```c
/* Update this in kern/arch/mips/vm/dumbvm.c */

void as_destroy(struct addrspace *as) {
    if (as == NULL) {
        return;
    }

    /* Free the physical pages for each segment stored in the addrspace struct */
    /* Note: variable names might slightly differ based on your exact OS161 version */
    
    if (as->as_pbase1 != 0) {
        freeppages(as->as_pbase1);   /* Free Code segment */
    }
    
    if (as->as_pbase2 != 0) {
        freeppages(as->as_pbase2);   /* Free Data segment */
    }
    
    if (as->as_stackpbase != 0) {
        freeppages(as->as_stackpbase); /* Free Stack segment */
    }

    /* Finally, free the memory used by the addrspace struct itself */
    kfree(as);
}
```