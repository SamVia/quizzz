
## **OS161 File System & System Calls Master Cheat Sheet**

### **System Calls Related to File Systems**
The system relies on various C library system calls to manage file input/output operations. The standard file operations are primarily declared in `unistd.h`.

```c
/*
 * Open actually takes either two or three args:
 * the optional third arg is the file mode used for creation.
 * Unless you're implementing security and permissions,
 * you can ignore it.
 */
int open (const char *filename, int flags, ...);
ssize_t read(int filehandle, void *buf, size_t size);
ssize_t write(int filehandle, const void *buf, size_t size);
int close(int filehandle);
off_t lseek(int filehandle, off_t pos, int code);
int dup2 (int filehandle, int newhandle);
```


When executing a file open command from user space, the call is translated by the kernel interface. The kernel-side prototype for opening a file is:
```c
int sys_open(userptr_t filename, int flags, int mode, int *retval);
```


---

### **The System Calls Interface Architecture**
The OS161 architecture separates User Space and Kernel Space, connected via the System Call Interface. 

* **User Space:**
    * User applications 
    * GNU C library 
* **Kernel Space (File System Layer):**
    * **Virtual File System (VFS):** Sits directly below the system call interface, acting as an intermediary abstraction.
    * **Caches:** Alongside VFS are the **Inode cache** and **Directory cache**.
    * **Individual File Systems:** Sit directly below the VFS.
    * **Buffer cache:** Located below the individual file systems.
* **Hardware Interface:**
    * **Device drivers:** Reside at the lowest level of the file system architecture.

---

### **Core Data Structures & Metadata**
When designing file tracking, do not consider the data structure used for organizing data directly on the disk (e.g., `inode`/`vnode`); focus strictly on the metadata of the files. 

**Note on Process Forking:** A forked process (child) shares files with its parent, meaning they share the same offset into the open file.

#### **1. Representing Opened Files**
To represent opened files for each process, you need the following structures:
* **`openfile` structure:** Represents an individual opened file.
* **`fileTable` (Per-Process):** An array or list of `openfile*` items. 
* **File Descriptor (FD):** Acts as an index or reference to the `fileTable` array. Operations like `read()`, `write()`, and `lseek()` use the file descriptor to target and operate on specific opened files.

*Standard File Descriptors:*
* `0`: `stdin` 
* `1`: `stdout` 
* `2`: `stderr` 

#### **2. Designing the `openfile` Structure**
A complete `openfile` structure requires the following components:
* **File pointer:** Used to locate data; it acts as a pointer to the `vnode`.
    * *Where is vnode defined?* `kern/include/vnode.h`.
    * *How is the vnode obtained?* Via the `vfs_open()` function.
* **Mode:** Indicates permissions such as Read-only, write-only, or read-write.
* **Offset:** Tracks the current seek/read/write position within the file.
* **Lock:** Protects the structure.
* **Reference count:** Tracks how many descriptors/processes are pointing to this open file.

#### **3. Locating the `fileTable`**
* **Where should the `fileTable` reside?** Place the `fileTable` directly inside the `proc` structure. 
* *Definition location:* The `proc` structure is defined in `kern/include/proc.h`.

---

### **Concurrency & Sharing Edge Cases**

* **Multiple Opens:** Can a file be opened multiple times? Yes. In this case, there will be two completely separate `openfile` structures, indicated by two separate file descriptors, which both eventually point to the same underlying internal file descriptor (`vnode`).
* **Thread Concurrency:** Are `openfile` structures shared by concurrent threads? 
    * *Initial phase:* No, you do not need to deal with critical section issues initially.
    * *Advanced phase:* Yes, if implemented, you must use a lock to protect the shared `openfile`. The lock should be added directly inside the `openfile` struct.

---

### **Algorithms & Practical Implementation Steps**

#### **Designing `sys_open`**
Algorithm to design `sys_open(filename, flag, retfd)`:
1.  **Create:** Allocate and create a new `openfile` item.
2.  **Obtain Vnode:** Call `vfs_open()` to obtain the vnode. 
    * *Prototype location:* `kern/include/vfs.h`.
    * *Sample Reference:* See `kern/test/fstest.c`.
3.  **Initialize Data:** Set the initial offset inside the `openfile` struct.
4.  **Store & Link:** Place the new `openfile` into the `systemFiletable` to generate a File Descriptor (`fd`).
5.  **Return:** Return the assigned file descriptor of the openfile item.

*Example `vfs_open()` call snippet:*
```c
struct vnode *vn;
...
err = vfs_open(name, flags, &vn);
```


#### **Designing `sys_close`**
Algorithm to design `int sys_close(fd)`:
1.  **Locate:** Use the provided `fd` to locate the target `openfile` item inside the `fileTable`.
2.  **Evaluate Multiple Opens:** Check if this is the absolute last open instance of this file.
3.  **Delete:** If it is the last open instance, completely delete the `openfile` from the System `fileTable`. (Note: Implementation will vary depending on if the table is built as an array or a singly-linked list) .

#### **Designing `sys_read`**
Algorithm to design `int sys_read(int fd, userptr_t buf, size_t size, int *retval)`:
1.  **Locate:** Use the `fd` to translate the file descriptor number to a file handle object (the `openfile` item from the `fileTable`).
2.  **Access Offset:** Retrieve the current offset from the located `openfile` struct.
3.  **Setup I/O Record:** Create and set up a `uio` record, which manages userspace I/O. 
    * *Definition location:* See `kern/include/uio.h`.
4.  **Execute Read:** Call `VOP_READ(openfile->vnode, userio)` to perform the actual read operation. **Crucial Rule:** The file must be locked while this occurs.
    * *Prototype location:* `kern/include/vnode.h`.
    * *Sample Reference:* See `kern/userprog/loadelf.c`.
5.  **Update Seek Position:** Update the `openfile`'s seek position to match the post-read offset: `Openfile->offset = userio.offset;`.
6.  **Return Data:** Set the `*retval` parameter to the exact amount of data successfully read.
