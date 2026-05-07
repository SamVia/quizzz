***

# OS/161 Master Cheat Sheet: User Processes & System Calls

## 1. Process Creation & Address Spaces
When the kernel creates a process to run a program, it creates an **address space** and loads the program's code and data into it. The kernel creates a user process inside the `common_prog` function: `int common_prog(int nargs, char **args);`.

### Core System Calls for Process Creation
* **`fork()`**: Allows process creation by duplicating a user process (keeps the same executable file). Signature: `pid_t fork(void);`.
* **`execv()`**: Allows a user process to replace its executable file, program, and address space. Signature: `int execv(const char *program, char **args);`. The `program` parameter is the name of the ELF executable file to be loaded.

### Thread and Process Structures
The OS keeps track of processes and threads using specific structures linking kernel/user states:
* **`proc` (Process Structure):** Tracks process metadata. Includes `p_name` (e.g., `args[0]`), `p_lock`, `p_numthreads` (starts at 1), `p_addrspace` (starts as `NULL`), and `p_cwd`.
* **`curthread` (Current Thread):** Contains `t_name`, `t_stack`, `t_context`, and `t_proc` (which points to `curproc`).

### Memory Layout
A running thread utilizes multiple address spaces:
* **Kernel:** `Kernel stack`.
* **User (`p_addrspace`):** Code (`as_vbase1`), Data (`as_vbase2`), and User stack (`as_stackpbase`).

---

## 2. The `runprogram` Execution Flow
To load and run a program, the kernel follows a strict chronological execution flow inside `runprogram`:

```c
int runprogram(char *progname) {
    struct addrspace *as;
    struct vnode *v;
    vaddr_t entrypoint, stackptr;
    int result;

    /* 1. Open the file. */
    result = vfs_open(progname, O_RDONLY, 0, &v);

    /* 2. Create a new address space. */
    as = as_create();

    /* 3. Switch to it and activate it. */
    proc_setas(as);
    as_activate();

    /* 4. Load the executable. */
    result = load_elf(v, &entrypoint);

    /* 5. Done with the file now. */
    vfs_close(v);

    /* 6. Define the user stack in the address space */
    result = as_define_stack(as, &stackptr);

    /* 7. Warp to user mode. */
    enter_new_process(0/*argc*/, NULL/*userspace addr of argv*/,
                      NULL /*userspace addr of environment*/,
                      stackptr, entrypoint);

    /* 8. enter_new_process does not return. */
    panic("enter_new_process returned\n");
    return EINVAL;
}
```
**

---

## 3. ELF Files (Executable and Linking Format)
OS/161 expects executables in ELF format, generated when compiling and linking. 
* **Purpose:** Contains address space segment descriptions, the virtual address of the program's first instruction, section descriptors, and symbol tables used by loaders/debuggers.

### ELF Segments vs. Sections
* **Segments (Used for Loading):** Describe a contiguous region of the virtual address space. A segment header includes the virtual address, virtual length, file location, and file length. The image is an exact binary copy copied into memory; if the image is smaller than the segment, the rest is zero-filled. 
* **OS/161 `dumbvm` Segments:** Assumes 2 segments: Text (code/read-only data) and Data (global data). The stack is NOT described in the ELF; `dumbvm` creates it manually (12 pages long, ending at `0x7fffffff`).
* **Sections (Used for Properties):** Group code/data by property.
    * `.text`: Program code (Part of Text segment).
    * `.rodata`: Read-only global data (Part of Text segment).
    * `.data`: Initialized global data (Part of Data segment).
    * `.bss`: Uninitialized global data / Block Started by Symbol (Part of Data segment).
    * `.sbss`: Small uninitialized global data (Part of Data segment).
    * *Note:* Local program variables allocate directly on the stack at runtime.

---

## 4. The `load_elf` Sequence
The kernel initializes the address space by copying segments from the ELF via the `load_elf` function.

1.  **Read Executable Header:** Reads `Elf_Ehdr eh` from offset 0. Uses `UIO_READ`.
2.  **Read Segment Headers:** Loops through `i=0` to `eh.e_phnum` reading `Elf_Phdr ph`. 
    * Offset formula: `off_t offset = eh.e_phoff + i*eh.e_phentsize;`.
    * Calls `as_define_region(as, ph.p_vaddr, ph.p_memsz, ph.p_flags & PF_R, ph.p_flags & PF_W, ph.p_flags & PF_X);`.
3.  **Read Segments:** Calls `load_segment` and finishes with `as_complete_load(as);`.
4.  **Set Entry Point:** `*entrypoint = eh.e_entry;`.

### Structs Used During I/O (`vnode` & `uio`)
* **`struct vnode`:** Represents the file. Contains `vn_refcount`, `vn_countlock`, `vn_fs`, `vn_data`, and operations pointer `vn_ops` (`emufs_ops` or `sfs_ops`).
* **`struct uio`:** Manages the data buffer between spaces. Contains pointer `*uio_iov` (to `struct iovec`), `uio_iovcnt`, `uio_offset`, `uio_resid`, `uio_segflg`, `uio_rw`, and `*uio_space`.
    * *Kernel Space Read:* `uio_segflg = UIO_SYSSPACE`, `uio_space = NULL`. `iov_len` is `sizeof(ph)`.
    * *User Space Read:* `uio_segflg = UIO_USERSPACE`, `uio_space` points to `as` (address space). `iov_len` matches user segment (e.g., `8192`).

---

## 5. System Calls (The Software Interrupt)
System calls are the programming interface for user programs to request kernel services. They trigger a software interrupt, redirecting to `void syscall(struct trapframe *tf)`.

### System Call Execution & `trapframe`
Arguments and syscall numbers are passed via MIPS registers stored in the trapframe:
* `callno = tf->tf_v0;` extracts the syscall number.
* `tf->tf_a0`, `tf->tf_a1`, `tf->tf_a2` hold arguments.

**Success/Error Handling Pattern:**
```c
if (err) {
    tf->tf_v0 = err;    // return error code
    tf->tf_a3 = 1;      // signal an error
} else {
    tf->tf_v0 = retval; // return result
    tf->tf_a3 = 0;      // signal no error
}
```
**

### Implementing Base Syscalls
**`sys_read` (From stdin):**
```c
int sys_read(int fd, userptr_t buf, int size) {
    if (fd == STDIN_FILENO) {
        char *p = (char *)buf;
        int i;
        for (i=0; i<size; i++) {
            int c = getch();
            if (c < 0) return i; /* EOF */
            p[i] = (char)c;
        }
        return size;
    } else {
        kprintf("not yet implemented\n");
        return -1;
    }
}
```
**

**`sys_write` (To stdout):**
```c
int sys_write(int fd, userptr_t buf, int size) {
    if (fd == STDOUT_FILENO) {
        int i;
        for (i=0; i<size; i++) {
            putch(((char *)buf)[i]);
        }
        return size;
    } else {
        kprintf("not yet implemented\n");
        return -1;
    }
}
```
**

---

## 6. Process Synchronization: Exit and Wait
When a process exits (`SYS_exit`), it must safely destroy its address space and thread. Simultaneously, a parent process might call `waitpid`. 

### The Race Condition Problem
If `sys_waitpid(7)` invokes `proc_wait()`, which immediately calls `proc_destroy(p)`, it might destroy the process structure *before* or *during* the child's `thread_exit()` routine finishes detaching the thread.
**Rule:** You must do `proc_destroy` *after* `thread_exit` detaches the thread from the process (`proc->p_numthreads == 0`).

### The Solution: Semaphores & Detaching
We use a semaphore (`end_sem`) or condition variables. Furthermore, we must detach the thread from the process early.

**Child (`sys_exit`):**
```c
sys_exit (int status) {
    struct proc *p = curproc;
    curproc->status = status;
    proc_remthread(curthread); // Detach before signaling!
    V(p->end_sem);             // Signal parent
    thread_exit();
}
```
** *(Note: `proc_remthread` / `thread_exit` must be modified to support an already removed thread ).*

**Parent (`sys_waitpid` -> `proc_wait`):**
```c
proc_wait (struct proc *p) {
    P(p->end_sem);             // Wait for child signal
    proc_destroy(p);
}
```
**

### Tracking PIDs
To convert a `pid` to a pointer in `sys_waitpid`, the kernel uses an array tracking system in `proc.c`.
* Direct access: `struct proc *proc[PID_MAX+1];`.
* If max processes are limited: `struct proc *proc[MAXPROC];` where `MAXPROC << PID_MAX`.
* Alternative: `kmalloc`.

---

## 7. Practical Exercises: The `segments.c` Walkthrough
*This section walks through the practical examination of an ELF file using OS/161 tools based on the document's `segments.c` example.*

### Step 1: The Source Code
```c
#include <unistd.h>
#define N (200)

int x = 0xdeadbeef;
int y1;
int y2;
int y3;
int array[4096];
char const *str = "Hello World\n";
const int z = 0xabcddcba;

struct example {
    int ypos;
    int xpos;
};

int main() {
    int count = 0;
    const int value = 1;
    y1 = N;
    y2 = 2;
    count = x + y1;
    y2 = z + y2 + value;
    reboot(RB_POWEROFF);
    return 0; /* avoid compiler warnings */
}
```
**

### Step 2: Section Breakdown & Tool Commands
Using the tool `mips-harvard-os161-readelf -a segments`, we can inspect the section headers:
* Flags: `W` (write), `A` (alloc), `X` (execute).
* Size calculation: Size is listed in hex. e.g., the `.text` section size `0x000200` equals 512 bytes.

### Step 3: Inspecting Section Contents (`objdump`)
Using `mips-harvard-os161-objdump -s segments`, we view the raw memory bytes.

**Decoding `.text` (Instruction Breakdown):**
Hex dump shows: `3c1c1001`. We decode this MIPS instruction:
1.  Binary conversion: `0x3c1c1001` = `0011 1100 0001 1100 0001 0000 0000 0001`.
2.  Split into MIPS format (6-bit opcode, 5-bit rs, 5-bit rt, 16-bit immediate):
    * Opcode: `001111` -> `LUI` (Load unsigned immediate).
    * rs (unused here): `00000`.
    * rt (target register): `11100` -> Register 28.
    * Immediate: `0001 0000 0000 0001` -> `0x1001`.
3.  Result: `lui gp, 0x1001`.

**Decoding `.rodata` (Memory Alignment):**
The `.rodata` section contains the string literal and constant integer `z`.
* "Hello World\n": `0x48='H' 0x65='e' 0x0a='\n' 0x00='\0'`. Size = 13 bytes.
* Padding: Hardware aligns the next `int` to a 4-byte boundary. 13 bytes + 3 bytes padding = 16 bytes.
* Constant `z` (`0xabcddcba`): Adds 4 bytes. Total = 20 bytes.
* Final Alignment: Hardware aligns the section to the next 16-byte boundary, bringing the total size to 32 bytes (`0x20`).

**Decoding `.data`:**
Contains initialized global variables `x` and `str`.
* `int x` = `deadbeef` (4 bytes).
* `char const *str` = `004002b0` (4 bytes). **Note:** This is *not* the string itself; it is the pointer address referencing the start of the string literal in the `.rodata` section. Size = 16 bytes (`0x10`).

### Step 4: Inspecting Uninitialized Data (`nm`)
Using `mips-harvard-os161-nm -b segments`:
* There are no values for uninitialized variables in the ELF file.
* `y1`, `y2`, and `y3` map to `.sbss` (Small BSS).
* `array` maps to `.bss`.

---

### Addendum 1: Exact Structural Data Types (`uio`, `iovec`, `vnode`)
When `load_elf` reads from the executable file, it uses strict structures to bridge kernel space and user space.

**1. `struct iovec` (I/O Vector)** 
Defines the base address and length of the memory segment being read into.
* `iov_base`: Pointer to the buffer. 
* `iov_len`: Size of the buffer. 

**2. `struct uio` (User I/O)** 
Manages the data transfer. 
```c
struct uio {
    struct iovec     *uio_iov;     // Pointer to the iovec array 
    unsigned         uio_iovcnt;   // Number of iovecs 
    off_t            uio_offset;   // Offset into the file 
    size_t           uio_resid;    // Remaining bytes to process 
    enum uio_seg     uio_segflg;   // UIO_SYSSPACE or UIO_USERSPACE 
    enum uio_rw      uio_rw;       // UIO_READ or UIO_WRITE 
    struct addrspace *uio_space;   // Destination address space (NULL if kernel) 
};
```

**3. `struct vn` (Vnode - Virtual Node)** 
Represents the open file in the filesystem.
```c
struct vn {
    int vn_refcount;                       // Number of active references 
    struct spinlock vn_countlock;          // Lock for the refcount 
    struct fs *vn_fs;                      // Pointer to filesystem 
    void *vn_data;                         // Private filesystem data 
    const struct vnode_ops *vn_ops;        // Operations vector (vops) 
};
```
*Note on `vn_ops`: This points to either `emufs_ops` (emulator filesystem) or `sfs_ops` (simple filesystem), which route `vop_read` to `emufs_read` or `sfs_read` respectively. *

---

### Addendum 2: The Deep File System Read Traces
The text provides the exact code for how `vop_read` executes down to the hardware/disk level depending on the filesystem.

**Path A: `emufs_read` -> `emu_doread`** 
Interacts with the emulator hardware using registers:
```c
int emu_doread (struct emu_softc *sc, uint32_t handle, uint32_t len, uint32_t op, struct uio *uio) {
    lock_acquire(sc->e_lock); 
    emu_wreg(sc, REG_HANDLE, handle); 
    emu_wreg(sc, REG_IOLEN, len); 
    emu_wreg(sc, REG_OFFSET, uio->uio_offset); 
    emu_wreg(sc, REG_OPER, op); 
    result = emu_waitdone(sc); 
    if (result) { goto out; } 
    membar_load_load(); 
    result = uiomove(sc->e_iobuf, emu_rreg(sc, REG_IOLEN), uio); 
    uio->uio_offset = emu_rreg(sc, REG_OFFSET); 
out: lock_release(sc->e_lock); 
    return result; 
}
```

**Path B: `sfs_read` -> `sfs_blockio`** 
Calculates the block offset and fetches from the Simple File System:
```c
sfs_blockio(struct sfs_vnode *sv, struct uio *uio) {
    struct sfs_fs *sfs = sv->sv_absvn.vn_fs->fs_data; 
    /* Get the block number within the file */
    fileblock = uio->uio_offset / SFS_BLOCKSIZE; 
    /* Look up the disk block number */
    result = sfs_bmap(sv, fileblock, doalloc, &diskblock); 
    if (result) { return result; } 
    /* Do the I/O */
    result = sfs_rwblock(sfs, uio); 
    return result; 
}
```

---

### Addendum 3: The Iterative System Call Implementations
The document does not just present the final `sys_read` and `sys_write`; it builds them in partial/temporary stages.

**Iterative `sys_read()` Stages:**
1.  **Just 1 byte from stdin (using `kgets`):** Uses `char localBuf[2]; kgets(localBuf,1); *(char *)buf = localBuf[0];`.
2.  **Just 1 byte from stdin (using `getch`):** Simplifies to `*(char *)buf = getch();`.
3.  **Final Loop (from stdin):** Uses a `for (i=0; i<size; i++)` loop checking for `EOF` (`if (c<0) return i;`).

**Iterative `sys_write()` Stages:**
1.  **Just 1 byte to stdout (using `kprintf`):** `return kprintf("%c", ((char *)buf)[0]);`.
2.  **Just 1 byte to stdout (using `putch`):** `putch(((char *)buf)[0]);`.
3.  **Final Loop (to stdout):** Uses a `for` loop to write `size` bytes iteratively using `putch`.

**Additional Missing Syscalls (`sys_reboot` and `sys_time`):** 
Inside the `syscall` dispatcher switch statement:
* `case SYS_reboot: err = sys_reboot(tf->tf_a0); break;` 
* `case SYS_time: err = sys_time((userptr_t)tf->tf_a0, (userptr_t)tf->tf_a1); break;` 

---

### Addendum 4: ELF Program Headers Data
The practical exercise for `segments.c` included the exact Program Headers table, which is vital for understanding virtual-to-physical address mappings. 

| Type | Offset | VirtAddr | PhysAddr | FileSiz | MemSiz | Flg Align |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| REGINFO | `0x000094` | `0x00400094` | `0x00400094` | `0x00018` | `0x00018` | R `0x4` |
| LOAD | `0x000000` | `0x00400000` | `0x00400000` | `0x002d0` | `0x002d0` | RE `0x1000` |
| LOAD | `0x001000` | `0x10000000` | `0x10000000` | `0x00010` | `0x04030` | RW `0x1000` |

*Rules extracted from this table:*
* The `REGINFO` section is not used. 
* The first `LOAD` segment includes the `.text` and `.rodata` sections (Flag: Read/Execute `RE`). 
* The second `LOAD` segment includes `.data`, `.sbss`, and `.bss` (Flag: Read/Write `RW`). 

---

### Addendum 5: Granular Rules on Process Destruction Options
Regarding the race condition where `proc_destroy` happens before/during `thread_exit` , the document explicitly outlines two specific architectural solutions for when to allow process destruction (`proc->p_numthreads == 0`): 

1.  **Sleep/Polling:** Sleep and/or poll before calling `proc_destroy`. 
2.  **Detach before signal (The chosen method):** Modify `thread_exit` or `proc_remthread` so that a thread is explicitly detached *only* if it is still attached to a proc, ensuring the parent is safely signaled after detachment. 

***

