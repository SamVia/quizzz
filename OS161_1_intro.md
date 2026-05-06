## OS161 & System/161 Overview

### OS161 Basics
*   **What it is:** A simplified, Unix BSD-like operating system written in C designed for educational purposes.
*   **Branches:**
    *   **1.x (2001):** Provides a uniprocessor kernel programming environment.
    *   **2.x (2009/2015):** Moves into the multicore era, adding multiprocessor support and modern attributes.
*   **Architecture:** Features a conventional "macrokernel" design and a simple userland containing test programs.
*   **Included Baseline Features:** Low-level trap/interrupt handling, device drivers, in-kernel threads, a basic scheduler, a simple file system, and a minimal virtual memory system (`dumbvm`).
*   **Missing Features (To be built):** Locks, system calls, full file systems, and a complete virtual memory system. *(Note: The included `dumbvm` is only good for bootstrapping; it never reuses memory and cannot support `malloc` or large processes)*.

### System/161 Simulator
*   **What it is:** A realistic machine simulator designed specifically to run OS161.
*   **Specs:** It acts as a 32-bit MIPS system that supports up to 32 processors.
*   **Toolchain:** Includes tools for cross-compiling the OS161 kernel for the MIPS processor (e.g., `mips-harvard-os161-gcc`), as well as `make`, `Configure`, and `gdb`.
*   **Debugging:** Supports fully transparent debugging via remote `gdb` connected directly into the simulator.

---

## Directory Structure
Understanding the directory tree (based on the provided Ubuntu VM) is critical for navigating the OS source.

*   **`~/os161_doc`:** Contains documentation and browsable code.
*   **`~/pds-os161/root`:** The execution directory where the compiled kernel runs.
    *   **`.../testscripts`:** User program executables called within the OS161 test menu.
*   **`~/os161`:** Contains the toolchain and OS161 source code.
    *   **`.../tools`:** Compilation, build, and debug tools.
    *   **`.../os161-base-2.0.2` (or `2.0.3`):** The main directory for building the kernel and user programs.
        *   **`.../userland`:** User source programs.
        *   **`.../kern`:** The main kernel source directory.
        *   **`.../kern/conf`:** Kernel configuration files (e.g., `conf.kern`, `DUMBVM`, `GENERIC`).
        *   **`.../kern/compile`:** Where the kernel is actually compiled and built.
        *   **`.../kern/main`:** Contains the main kernel execution files (e.g., `main.c`, `menu.c`).

---

## Building the OS161 Kernel
To build a new kernel release (e.g., creating a custom configuration named "HELLO"), you must execute a strict 4-step process:

### Step 1: Configure
1. Navigate to the configuration directory: `cd os161/os161-base-2.0.3/kern/conf/`.
2. Copy an existing configuration to make your new one: `cp DUMBVM HELLO`.
3. Run the config script: `./config HELLO`.
*Result: This generates the necessary files (`files.mk`, `Makefile`, etc.) in the `kern/compile/HELLO` directory*.

### Step 2: Depend
1. Navigate to the new compile directory: `cd ../compile/HELLO/`.
2. Run the dependency generator: `bmake depend`.
*Result: Scans C files and generates rules to automatically recompile source files if their associated `.h` headers are modified*.

### Step 3: Compile
1. In the same directory, run: `bmake`.
*Result: Compiles the source code into the `kernel` executable. If there are code errors (e.g., syntax errors, missing prototypes), the build will fail. You must fix the code and run `bmake` again*.

### Step 4: Install
1. Run the install command: `bmake install`.
*Result: Copies your newly compiled kernel to the `~/pds-os161/root/` execution directory as `kernel-HELLO` and creates a symbolic link named `kernel` pointing to it*.

---

## Running and Debugging OS161
All execution and debugging must be done from inside the **`~/pds-os161/root/`** directory.

### Configuration & Running
*   **`sys161.conf`:** The file used to configure the MIPS virtual machine hardware (e.g., `mainboard ramsize=1024K cpus=1`).
*   **Standard Run:** Execute `sys161 kernel` (runs without debugger support).

### Debugging (Two-Terminal Setup)
To use the debugger, you must open two separate terminal windows:

**Terminal 1 (Start the Simulator):**
*   Run: `sys161 -w kernel` (The `-w` flag tells the simulator to wait for a debugger connection on a socket before executing).

**Terminal 2 (Launch the Debugger):**
Choose one of the following three options to connect to the waiting simulator:
*   **Option 1 (Command Line TUI):** Run `mips-harvard-os161-gdb -tui kernel`.
*   **Option 2 (DDD GUI):** Run `ddd --debugger mips-harvard-os161-gdb kernel`.
*   **Option 3 (Emacs GUI):** Run `emacs &`, go to *Tools -> Debugger*, and change the run command to `mips-harvard-os161-gdb -i=mi .gdbinit`.

**Basic Debugger Flow:**
1. Set a breakpoint at the kernel start: `break kmain`.
2. Continue execution until the breakpoint: `c`.

---

## Lab 01 Walkthrough: Adding `hello()` to the Kernel
This lab demonstrates how to add a custom `hello()` function that prints during the OS boot sequence.

**1. Create the Header (`kern/include/hello.h`):**
*   Create a new file and add the prototype: `void hello(void);`.

**2. Create the Source (`kern/main/hello.c`):**
*   Include the required headers: `#include <types.h>`, `#include <lib.h>`, `#include "hello.h"`.
*   Define the function: `void hello(void) { kprintf("Hello OS161\n"); }`. *(Note: The document shows a simulated compilation error where this is misspelled as `voi helllo (void)`. It must be fixed to compile correctly)*.

**3. Modify Kernel Main (`kern/main/main.c`):**
*   Include the new header at the top: `#include "hello.h"`.
*   Inside the `kmain()` function, add the call to `hello();` directly after `boot();` and before `menu(arguments);`.

**4. Update the Configuration (`kern/conf/conf.kern`):**
*   Scroll to the bottom and register the new files so the compiler includes them:
    *   `defoption hello`.
    *   `optfile hello main/hello.c`.

**5. Build and Run:**
*   You must completely rebuild the configuration to apply the `conf.kern` changes.
*   Run `./config HELLO` -> `bmake depend` -> `bmake` -> `bmake install`.
*   Run `sys161 kernel`, and you will see "Hello OS161" printed in the boot sequence.