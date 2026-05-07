Here is the exhaustive cheat sheet covering all the concepts, system call mechanics, and OS161 architectural specifics from the provided document.

## Part 1: Processes and Threads

### Process vs. Thread Concepts
*   **Process:** A program in execution (an active entity), whereas a program is merely a passive entity stored on a disk. One program can spawn several processes (e.g., multiple users running the same program).
*   **Thread:** Represents the control state of an executing program.
*   **Context:** A thread's state includes the CPU state (Program Counter (PC), stack pointer, execution mode) and the stack.
*   **Process Memory Layout:** 
    *   **Text (Code):** The program code.
    *   **Data:** Global variables (initialized and uninitialized).
    *   **Heap:** Memory dynamically allocated during run time (e.g., via `malloc`).
    *   **Stack:** Contains temporary data like function parameters, local variables, and return addresses.

### User Threads vs. Kernel Threads
*   **User Threads:** Managed entirely by user-level libraries (e.g., POSIX Pthreads, Windows threads, Java threads) without direct kernel support.
*   **Kernel Threads:** Supported and managed directly by the operating system (e.g., Windows, Linux, Mac OS X, iOS, Android).

### Multithreading Models

*   **One-to-One:** Maps each user thread to a single kernel thread. It provides maximum concurrency on multicore systems, but the overhead of creating a kernel thread for every user thread can burden system performance.
*   **Many-to-One:** Maps many user threads to a single kernel thread. Multiple threads cannot run in parallel on multicore systems because only one can access the kernel at a time, and a single blocking thread blocks the entire process.
*   **Many-to-Many:** Maps many user threads to a smaller or equal number of kernel threads. This allows parallel execution on multiprocessors without overloading the system with kernel threads.

---

## Part 2: OS161 Thread & Process Architecture

### OS161 Data Structures
*   **Thread Control Block (TCB - `struct thread`):** Stores a thread's name, execution state, kernel-level stack pointer, saved register context (`switchframe`), the CPU it runs on, and a pointer to its parent process.
*   **Process Control Block (PCB - `struct proc`):** Stores the process name, a spinlock, the number of threads, its virtual address space (`addrspace`), and the current working directory (`vnode`).
*   **Relationship:** In OS161, a thread knows which process it belongs to, but a process does not contain a list of its threads.
*   **Dual Stacks:** Each OS161 thread is associated with two stacks: a user stack (used while executing unprivileged code) and a kernel stack (used while executing privileged kernel code).

### OS161 Thread Library Functions
The OS161 thread library manages context switching and thread lifecycles:
*   **`thread_fork`:** Creates a new thread by allocating a TCB (`thread_create`), initializing the registers (`switchframe_init`), and moving it to the ready queue (`thread_make_runnable`). It expects an entry point, arguments, and associates the thread to a CPU.
*   **`thread_yield`:** Pauses the current thread, keeping it runnable, and asks the OS to schedule the next thread.
*   **`thread_exit`:** Causes the current thread to exit.
*   **`thread_switch`:** Called to change the state of the current thread, fetch the next thread from the ready list, and trigger the assembly-level context switch (`switchframe_switch`).

---

## Part 3: MIPS Registers & System Calls

### MIPS Register Organization
The MIPS architecture has 31 registers that must be saved and restored during context switches:
*   **`R0`:** Always returns 0.
*   **`R2 - R3` (`$v0 - $v1`):** Return values / system call numbers.
*   **`R4 - R7` (`$a0 - $a3`):** First four subroutine arguments.
*   **`R8 - R15, R24 - R25` (`$t0 - $t9`):** Temporary registers (not preserved by subroutines).
*   **`R16 - R23` (`$s0 - $s7`):** Preserved registers (must be saved before using).
*   **`R28` (`$gp`):** Global pointer.
*   **`R29` (`$sp`):** Stack pointer.
*   **`R30` (`$s8/$fp`):** Frame pointer.
*   **`R31` (`$ra`):** Return address.

### System Call Mechanics
*   System calls provide an interface to OS services (file management, device management, communication, etc.) and are mapped to specific ID numbers.
*   **OS161 Available Syscalls:** `fork` and `execv` (creation), `_exit` (destruction), `waitpid` (synchronization), and `getpid` (attribute management).
*   **The MIPS Trap:** On MIPS, a single exception handler (`mips_trap`) handles system calls, exceptions, and hardware interrupts. The hardware sets a code indicating the reason.
*   **Trap Frame:** When shifting from user mode to kernel mode, the CPU's state is saved into a "trap frame" on the thread's kernel stack so execution can resume later.
*   **Execution:** The `syscall(struct trapframe *tf)` function reads the system call number from `tf->tf_v0` and uses a switch statement to execute the appropriate kernel function.

---

## Part 4: OS161 Memory Management & Execution

### MIPS R3000 Address Space

MIPS uses a 32-bit architecture (4GB total address space) divided strictly into user and kernel zones:
*   **`kuseg` (0 to 2GB):** User space. All addresses must be translated by the TLB.
*   **`kseg0` (0.5GB):** Kernel space. Directly accesses physical memory (unmapped by TLB) but is cached.
*   **`kseg1` (0.5GB):** Kernel space. Unmapped by TLB and uncached (used for I/O device mapping).
*   **`kseg2` (1GB):** Kernel space, but unused in OS161.

### TLB and `dumbvm`
*   The MIPS Translation Lookaside Buffer (TLB) is entirely software-controlled and holds 64 entries.
*   The OS manages it using `tlb_write()`, `tlb_random()`, `tlb_read()`, and `tlb_probe()`.
*   If the MMU cannot find a translation, it throws an address exception handled by `vm_fault()`. 
*   **`dumbvm` limitations:** OS161's baseline virtual memory tracks the base and size of code, data, and stack segments. It is extremely primitive; if the TLB fills up completely, OS161 will simply crash.

### Program Execution (`runprogram` & ELF)
When a user launches a program via the command line, OS161 follows a specific boot sequence:
1.  **`vfs_open`:** Opens the target ELF executable file.
2.  **`as_create` & `proc_setas`:** Creates a new address space and associates it with the process.
3.  **`as_activate`:** Activates the address space.
4.  **`load_elf`:** Reads the ELF file, which contains headers specifying the contiguous virtual memory regions for the **text (code)** and **data** segments, and loads them into memory.
5.  **`as_define_stack`:** Because ELF files do not define a stack, `dumbvm` manually creates a 12-page stack segment ending exactly at `0x7fffffff`.
6.  **`enter_new_process`:** Warps the execution from kernel mode back into user mode to start the program.

## Part 5: OS161 Code Traces & Implementation Details

### 1. Code Trace: Creating Threads (`runthreads`)
When creating multiple threads in OS161, a loop is typically used with `thread_fork`.
*   **Parameters Passed:** The function name, `NULL` (meaning it associates with the current process), the function pointer (e.g., `loudthread` or `quietthread`), `NULL` (data pointer), and an integer `i` (data number).
*   **Error Handling:** If `thread_fork` fails (returns a non-zero result), the system calls `panic()` with the error message.

### 2. Inside `thread_fork` (The Wrapper)
`thread_fork` acts as a wrapper that calls three internal functions sequentially to get a thread ready for execution:
1.  **`thread_create(...)`**: Allocates memory for the thread control block using `kmalloc(sizeof(*thread))` and initializes its fields.
2.  **`switchframe_init(...)`**: Sets up the switch frame on the kernel stack, which memorizes the initial register values needed to start executing the `entrypoint`.
3.  **`thread_make_runnable(...)`**: Changes the thread's state to `S_READY` and adds it to the CPU's ready queue (`threadlist_addtail(&targetcpu->c_runqueue, target)`).

### 3. Inside the MIPS `syscall` Handler
When a system call is made, the MIPS trap saves the CPU state into a `trapframe` on the kernel stack and routes to the `syscall()` function:
*   It reads the system call number from the `v0` register: `callno = tf->tf_v0;`.
*   It uses a `switch (callno)` statement to find the right execution path.
*   *Example:* If `callno` is `SYS_reboot`, it executes `sys_reboot(tf->tf_a0);`.
*   *Default:* If the syscall number is unknown, it prints an error and sets the error code to `ENOSYS`.

### 4. Code Trace: `dumbvm` Address Space (`struct addrspace`)
Because `dumbvm` is incredibly basic, its `addrspace` structure does not use page tables. Instead, it relies on simple dynamic relocation using just three physical bases:
*   `vaddr_t as_vbase1`, `paddr_t as_pbase1`, `size_t as_npages1` (For the Code/Text segment).
*   `vaddr_t as_vbase2`, `paddr_t as_pbase2`, `size_t as_npages2` (For the Data segment).
*   `paddr_t as_stackpbase` (For the Stack segment).

---

## Part 6: Standard C Library & System Call Translations

### Standard C Library Wrappers
Programmers rarely invoke system calls directly; they use an API provided by a runtime library (like the standard C library).
*   *Example:* When a C program calls `printf("Greetings");`, the C library intercepts this call, translates it into the necessary system call (`write()`), executes the trap to switch to kernel mode, and then passes the returned value back to the user program.

### Windows vs. UNIX System Call Equivalents
The slides provide a direct translation table between Windows and UNIX (POSIX) system calls:

*   **Process Control:**
    *   Create: `CreateProcess()` (Windows) $\rightarrow$ `fork()` (UNIX).
    *   Exit: `ExitProcess()` (Windows) $\rightarrow$ `exit()` (UNIX).
    *   Wait: `WaitForSingleObject()` (Windows) $\rightarrow$ `wait()` (UNIX).
*   **File Management:**
    *   Open: `CreateFile()` (Windows) $\rightarrow$ `open()` (UNIX).
    *   Read/Write: `ReadFile()` / `WriteFile()` (Windows) $\rightarrow$ `read()` / `write()` (UNIX).
    *   Close: `CloseHandle()` (Windows) $\rightarrow$ `close()` (UNIX).
*   **Information Maintenance / Timing:**
    *   Get Process ID: `GetCurrentProcessID()` (Windows) $\rightarrow$ `getpid()` (UNIX).
    *   Sleep/Timer: `Sleep()` / `SetTimer()` (Windows) $\rightarrow$ `sleep()` / `alarm()` (UNIX).
*   **Communications (Pipes & Memory):**
    *   Pipe: `CreatePipe()` (Windows) $\rightarrow$ `pipe()` (UNIX).
    *   Shared Memory: `CreateFileMapping()` (Windows) $\rightarrow$ `shm_open()` (UNIX).
*   **Protection (Permissions):**
    *   Change Permissions: `SetFileSecurity()` (Windows) $\rightarrow$ `chmod()` (UNIX).

***

