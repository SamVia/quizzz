## **Master Cheat Sheet: OS161 File System and IO**

### **1. The OS161 File System Architecture**
The OS161 file system implementation is split across two primary directories:

* **Virtual File System (`kern/vfs/`)**: 
    * This is the file system independent layer. 
    * It acts as a framework making it easy to plug in and add new file systems.
    * **Crucial Tip**: You should thoroughly review `vfs.h` and `vnode.h` before exploring the rest of this directory.
* **Actual File System (`kern/fs/`)**: 
    * This directory houses the actual file system implementations. 
    * A specific subdirectory named `sfs` contains the implementation for the simple file system.
* **Emufs**: The `emufs` implementation is intentionally bypassed and not present in this directory structure; it goes directly to the device drivers.

---

### **2. LAMEBUS Architecture**
LAMEbus is the simple system bus architecture utilized in OS161 for I/O devices.

#### **Core Architectural Rules**
* The architecture provides exactly **32 slots**.
* Each slot is associated with a fixed-size addressable memory region.
* These regions are mapped sequentially into the system's physical memory space.
* **No DMA (Direct Memory Access)**: All data transfers must be manually performed by the CPU.
* The CPU uses transfer buffers that appear within the specific address space of the device. (Note: DMA may be introduced in future versions ).
* The primary header file for this architecture is located at `Kern/dev/lamebus/lamebus.h`.

#### **Bus Region Memory Math & Layout**
* **Slot Constraints**: 32 total slots, with each slot having a 64K address space.
* **Total Bus Size**: The whole bus region calculation is mathematically expressed as $64K^{*}32=2MB$.
* **LAMEBASE**: The base physical address for this region is known as `LAMEBASE`. Its exact value depends on the underlying processor architecture, as different processors impose distinct physical memory organization restrictions.
* **The Bus Controller**:
    * The bus controller is permanently situated in **slot 31**.
    * Its 64K address space is cleanly divided into two halves.
    * **Lower Half**: Divided into 32 separate 1K configuration regions (one per slot).
    * **Upper Half**: Divided into 32 separate 1K control regions (one per CPU).
    * The config region belonging to the bus controller itself contains the bus controller's own hardware registers.

#### **LAMEBUS Device Definitions**
The following CS161 device constants are defined:

| Device Name | Constant Name | Value |
| :--- | :--- | :--- |
| Upbus Controller | `#define LBCS161_UPBUSCTL` | 1 |
| Timer | `#define LBCS161_TIMER` | 2 |
| Disk | `#define LBCS161_DISK` | 3 |
| Serial | `#define LBCS161_SERIAL` | 4 |
| Screen | `#define LBCS161_SCREEN` | 5 |
| Network | `#define LBCS161_NET` | 6 |
| Emulated FS | `#define LBCS161_EMUFS` | 7 |
| Trace | `#define LBCS161_TRACE` | 8 |
| Random | `#define LBCS161_RANDOM` | 9 |
| Mpbus Controller| `#define LBCS161_MPBUSCTL` | 10 |

---

### **3. Hardware Devices & Serial Console**
External documentation for SFS, LAMEBUS, and Hardware devices can be found at the `os161.eecs.harvard.edu` resource directories.

#### **Serial Console Behavior**
* The Serial Console provides a very simple interface.
* **Writing**: Writing directly to the first register prints a character.
* **Reading**: Reading from it returns the very last character that was typed.
* **Strict Rule**: You must wait for one write operation to fully complete before starting a new one; otherwise, the output may become garbled.
* **Device Specs**: Device id is 4, Oldest revision is 1, Current revision is 1.

#### **Serial Console Register Offsets**
The serial console utilizes the following register map:

| Offset | Description |
| :--- | :--- |
| 0-3 | Character buffer |
| 4-7 | Write IRQ register |
| 8-11 | Read IRQ register |
| 12-15 | Reserved |

---

### **4. Device Driver Implementation Code (`lser.c` & `lser.h`)**

#### **Register Offsets and IRQ Bits (`lser.c`)**
```c
/* Registers (offsets within slot) */
#define LSER_REG_CHAR 0
/* Character in/out */
#define LSER_REG_WIRQ 4
#define LSER_REG_RIRQ 8
/* Write interrupt status */
/* Read interrupt status */

/* Bits in the IRQ registers */
#define LSER_IRQ_ENABLE 1
#define LSER_IRQ_ACTIVE 2
#define LSER_IRQ_FORCE 4
...
/* functions: lser_irq, lser_write,
...
*/
```
*(Extracted verbatim from source )*

#### **Driver Header File (`lser.h`)**
```c
struct lser_softc {
};
/* Initialized by lower-level attachment function */
void *ls_busdata;
uint32_t ls_buspos;

/* Initialized by higher-level attachment function */
void *ls_devdata;
void (*ls_start) (void *devdata);
void (*ls_input) (void *devdata, int ch);

/* Functions called by lower-level drivers */
void lser_irq(/*struct lser_softc*/ void *sc);

/* Functions called by higher-level drivers */
void lser_write(/*struct lser_softc*/ void *sc, int ch);
void lser_writepolled(/*struct lser_softc*/ void *sc, int ch);
```
*(Extracted verbatim from source )*

---

### **5. The Life Cycle of An I/O Request**
When an I/O request occurs, it traverses multiple structural layers of the operating system:

1.  **User Land**: A process requests I/O, which invokes a system call.
2.  **Kernel (I/O Subsystem)**: The kernel checks if it can already satisfy the I/O request.
    * *If Yes*: It places the data into return values or into process space and returns from the system call.
    * *If No*: It sends the request down to the device driver and blocks the process if appropriate.
3.  **Device Driver**: The driver processes the request, issues the commands to the controller, and configures the controller to block until an interrupt is received.
4.  **Device Controller**: The hardware controller executes the command and monitors the device. Once the I/O is complete, it generates an interrupt.
5.  **Interrupt Handler**: The handler receives the interrupt. If the operation was input, it stores the data in the device-driver buffer. It then signals to unblock the device driver.
6.  **Device Driver (Wake Up)**: The driver determines exactly which I/O completed and indicates the state changes back to the kernel I/O subsystem.
7.  **Completion**: I/O is marked complete, input data is made available (or output completed), and the system returns from the system call.

---

### **6. Practical Code Traces: Execution Paths for I/O**

#### **A. The `putch()` Code Trace**
This demonstrates the execution path for printing/writing a character.

```c
// 1. Initial Entry Point
putch (int ch) {
    struct con_softc *cs = the_console;
    putch_intr(cs, ch);
}

// 2. Kernel IO Subsystem (console.c .h)
putch_intr (struct con_softc *cs, int ch) {
    P(cs->cs_wsem);
    cs->cs_send(cs->cs_devdata,ch);
}
con_start(void *vcs) {
    struct con_softc *cs = vcs;
    V(cs->cs_wsem);
}

// 3. Driver Level (lser.c .h)
lser_write (void *vls, int ch) {
    struct lser_softc *ls = vls;
    bus_write_register(ls->ls_busdata, ls->ls_buspos, LSER_REG_CHAR, ch);
}

// 4. Interrupt Handling
lser_irq(void *vsc) {
    struct lser_softc *ls = vsc;
    sc->ls_start(sc->ls_devdata);
}

/* write done interrupt */
lamebus_interrupt (...) {
    handler (data); // Serial console
}
```

#### **B. The `getch()` Code Trace**
This demonstrates the execution path for retrieving/reading a character.

```c
// 1. Initial Entry Point
int getch(void) {
    struct con_softc *cs = the_console;
    return getch_intr(cs);
}

// 2. Kernel IO Subsystem (console.c .h)
getch_intr (struct con_softc *cs) {
    P(cs->cs_rsem);
    /* read from buffer and return */
}
con_input (void *vcs, int ch) {
    struct con_softc *cs = vcs;
    /* write ch to buffer */
    V(cs->cs_rsem);
}

// 3. Driver Interrupt Handling (lser.c .h)
lser_irq(void *vsc) {
    struct lser_softc *ls = vsc;
    sc->ls_input(sc->ls_devdata, ch);
}

// 4. Base Hardware Interrupt
/* write done interrupt */
lamebus_interrupt (...) {
    handler (data); // Serial console
}
```
