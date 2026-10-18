## Part I: eBPF Introduction

* **Primary Purpose:** eBPF is extensively used for kernel monitoring and network packet processing within the Linux kernel.


* **Packet Interception & Actions:** After intercepting and processing a network packet, an eBPF program can perform three primary actions:


* Return the packet to the standard Linux stack to proceed unmodified.


* Drop the packet entirely.


* Redirect the packet to another location within the kernel.




* **Routing and Delivery Constraints:** The available destination modules for a redirected packet depend strictly on the interception point. For instance, a packet can be redirected from TC-ingress to TC-egress, but it cannot be redirected from XDP to TC-egress.


* **Use Cases for eBPF Network Shortcuts:**
* **Cloud-Native Apps:** Shortcutting traffic directly from one container to another utilizing Traffic Control (TC), as XDP is typically bypassed for containers.


* **Load Balancing:** Shortcutting traffic from server to server via XDP, exemplified by the Facebook Katran load balancer.


* **Security:** Early dropping of network packets to mitigate DDoS attacks.




* **Kernel Cooperation:** Instead of bypassing the stack, eBPF can cooperate with it, such as acting as a Netfilter module to perform firewalling without configuring `iptables` rules.



## Part II: BPF and eBPF Basics

* **Classic BPF (cBPF):** The Berkeley Packet Filter was introduced in Linux kernel 2.1.75 in 1997 as a generic, in-kernel, event-based virtual CPU. It was initially designed as a packet filter for capture tools like `tcpdump` via `libpcap`.


* **Benefits of cBPF:** Operating in-kernel removes system call overhead and context switching between kernel and user space, allowing processing as soon as an event (like a network packet reception) occurs.


* **Virtual CPU Architecture:** The virtual CPU uses a secure sandbox containing a control unit, an ALU with an application-specific instruction set, generic registers, an accumulator, a program counter, main memory, and dedicated packet memory.


* **eBPF Origins:** Extended BPF (eBPF) was proposed by Alexei Starovoitov (PLUMgrid) in 2013 and officially integrated into the Linux kernel starting with version 3.15, though kernel 4.x is practically required for advanced features.



## Part III: eBPF Key Features

* **#1 Runtime Bytecode Injection:** eBPF programs can be dynamically generated and injected at run-time into a vanilla Linux kernel without requiring patches, additional kernel modules, or recompilation. This drops deployment time from years (kernel release cycles) to seconds or minutes. It allows the creation of dynamically tailored software based on real-time configuration or traffic patterns (e.g., optimizing matching algorithms based on the volume of rules or elephant vs. mice sessions).


* **#2 Safety (Sandbox & Verifier):** The kernel is protected from malicious or erroneous code by a verifier. The verifier enforces bounded program sizes, a maximum number of total instructions, and strict bounds per execution path. Loops must be unrolled; eBPF code cannot contain unbounded loops, meaning it is not Turing complete. Invalid memory access is prevented by the sandbox.


* **#3 Efficiency:** BPF runtime consumes minimal resources, preventing its use as a denial-of-service vector. The bytecode is natively translated at run-time into machine architecture (e.g., x64) via a Just-in-Time (JIT) compiler. The traditional interpreter was completely removed in kernel 4.17.


* **#4 React to Generic Kernel Events:** eBPF code binds to kernel events via handlers. Events include network packet reception, socket message reception, disk writes, memory page faults, file modifications, Kprobes, Uprobes, and tracepoints. The context (metadata) delivered to the handler depends strictly on the hook point.


* **#5 On-Path vs. Aside Interception:** Depending on the event, eBPF either receives the actual event on-path (allowing modification of the payload/packet) or a strict copy aside (where the original event continues unmodified).


* **#6 Memory for Stateful Processing (MAPs):** eBPF utilizes defined, preformatted key/value data structures called maps (e.g., Array, HashMap, LRUMap) rather than unstructured memory pages. Maps prevent specific offset access and handle concurrency issues. Maps are shared across boundaries to export statistics to userspace, push configurations from userspace to the kernel, share state between chained eBPF programs, or share data across CPU cores. Per-CPU maps exist to optimize cache synchronization, requiring manual syncing if needed.


* **#7 Multiple Networking Hook Points:**
* **Traffic Control (TC):** Hooked at `net/sched/sch_ingress.c` (TC_INGRESS_HOOK) and `net/sched/sch_egress.c` (TC_EGRESS_HOOK).


* **Sockets & RAW:** Operates on local delivery and creation paths.


* **eXpress Data Path (XDP):** Hooked directly inside the networking device driver (e.g., `ixgbe`) for extreme performance before the kernel allocates an `skb` (socket buffer). XDP Native requires driver support, while XDP Generic is provided for drivers without native support by setting `XDP_FLAGS_SKB_MODE`. XDP Native can only redirect packets to other XDP Native devices, while Generic can redirect to all XDP Generic devices.




* **#8 Service Chains (Tail Calls):** eBPF programs can be linked using "tail calls," which act as function calls without returning, jumping execution directly into another eBPF program to build modular services.


* **#9 Kernel Helpers:** Because of safety constraints, eBPF code utilizes helper functions implemented natively in the Linux kernel to perform complex loop-based processing or to safely access kernel structures like the routing table. Helpers such as `bpf_map_lookup_elem()` arbitrate map access and mutual exclusion.


* **#10 Portability:** BPF bytecode is independent of hardware architectures and runs effectively on MIPS/ARM embedded CPUs and x64 enterprise servers.



## Part IV: Creating eBPF Programs

* **Workflow:** eBPF source code is written in restricted C, parsed by the Clang frontend into an intermediate representation, optimized by the LLVM compiler, output as assembly eBPF bytecode, and finally JIT-compiled into native instructions in the kernel.


* **BCC (BPF Compiler Collection):** A toolkit designed for kernel tracing, network traffic control, and packet filtering, allowing kernel instrumentation in C with front-ends in Python and Lua.


* **Licensing:** While Linux kernel code requires a GPL license, injected eBPF bytecode may be non-GPL. However, the program must explicitly declare its license, and certain kernel helpers will refuse to execute if called by non-GPL eBPF code.



## Part V: Polycube Architecture

* **Objective:** To define, implement, and validate a framework for fast, lightweight, dynamically loadable network functions (bridge, router, firewall, NAT, load balancer) using eBPF.


* **#1 Fast, Slow, and Control Paths:**
* **Fast Path:** Runs inside the kernel handling the vast majority of standard packet forwarding.


* **Slow Path:** Runs in userspace to implement complex data plane tasks not supported by eBPF or the verifier (e.g., ARP handling, complex ICMP processing, or when a missing routing entry requires a user-space lookup). Upstream communication (kernel to userspace) utilizes a Performance Ring Buffer, transferring the complete hex dump, Module ID, InPort ID, Reason, and custom metadata. Downstream communication utilizes a Tap interface and an eBPF map.


* **Control Path:** Implements out-of-band management protocols (e.g., Spanning Tree, Routing Protocols) and CLI/REST interactions.




* **#2 Polycube Daemon (`polycubed`):** A single point of entry to handle the lifecycle, connection, and setup of the entire virtual network, connecting services to endpoints like VMs, Docker containers, or veth interfaces.


* **#3 Service-Agnostic Control:** Uses a YANG data model to define the structure, syntax, and semantics of service data. This model auto-generates REST APIs and consistent CLI interfaces, eliminating the need for developers to write boilerplate CLI/REST code.


* **#4 Code Tailoring:** Polycube leverages eBPF's dynamic compilation to generate only the exact, minimum data path code required for enabled features (e.g., injecting a simple bridge, then dynamically replacing it with a VLAN+STP bridge if those features are toggled on), ensuring optimal performance.



## Part VI: BTF and CO-RE

* **BTF (BPF Type Format):** A highly compact variant of DWARF utilized to represent type information in the kernel and eBPF programs. The entire BTF section in a 6.8 kernel is under 6MB. It is exposed via `/sys/kernel/btf/vmlinux` and is used internally by the eBPF verifier, allows direct read-only in-kernel memory access for tracing programs, and generates personalized kernel headers.


* **CO-RE (Compile Once, Run Everywhere):** Solves the portability issue where structural layout changes in kernel structures (like `task_struct`) across different Linux versions or configurations break eBPF programs. The Clang compiler emits BTF relocations capturing the program's intent, and the `libbpf` loader matches these relocations dynamically against the specific running kernel's BTF information at injection time.



## Part VII: Miscellaneous Comparisons

* **P4 vs. eBPF:** P4 is a high-level language specifically designed for protocol-independent packet processing dataplanes on various hardware targets. eBPF does not natively enforce protocol independency, is entirely software-based at the network edge, but supports generic system events beyond just network packets. P4 code can be compiled to eBPF using frontend tools.


* **SmartNICs:** eBPF programs can be offloaded directly to SmartNICs equipped with embedded hardware accelerators. Offloaded `bpfilter` hardware processing can achieve 59.5 Mpps (40 Gbps line rate), vastly outperforming host JIT XDP (38.7 Mpps) or legacy iptables (10.9 Mpps). Challenges include sharing eBPF maps seamlessly between userspace and the SmartNIC.


* **DPDK vs. XDP:** DPDK requires modified systems with additional kernel modules and bypasses the kernel completely to provide extremely fast userspace processing using Turing-complete logic. eBPF/XDP operates on vanilla kernels without patches and integrates natively with the kernel, though arbitrary processing is restricted to the userspace slow path.



---

## Practical Exercises

### Exercise 1: Understanding Classic BPF Assembly Generation

**Scenario:** Inspect the virtual assembly instructions generated for standard protocol filtering.
**Step 1:** Use `tcpdump` with the `-d` flag to dump the compiled cBPF bytecode for filtering IPv4 packets.

```bash
user@linux$ tcpdump -d ip

```

**Step 2:** Analyze the instruction output representing the state machine.

```nasm
(000) ldh      [12]
(001) jeq      #0x800           jt 2    jf 3
(002) ret      #96
(003) ret      #0

```

*Explanation:* The code loads a half-word at offset 12 (the Ethernet type field). It compares the value to `0x800` (IPv4). If true (`jt`), it jumps to instruction 2 and returns 96 bytes of the packet. If false (`jf`), it jumps to instruction 3 and returns 0 bytes (drops the packet).

### Exercise 2: Implementing a Socket-bound eBPF Program in C

**Scenario:** Create a restricted C program to intercept socket data and count packets per protocol type.
**Step 1:** Write the restricted C code utilizing map helpers.

```c
int bpf_rx_handler(struct sk_buff *skb)
{
    /* 14 is the length of the Ethernet header; */
    /* 9 is the offset of the protocol type field in IP */
    int index = load_byte(skb, 14 + 9);
    long *value;
    
    value = bpf_map_lookup_elem(&my_map, &index);
    if (value)
        __sync_fetch_and_add(value, 1);
        
    return 0;
}

```

**Step 2:** Compile to bytecode using Clang/LLVM.
**Step 3:** Inject the bytecode using the `bpf()` system call to obtain a file descriptor (`fd`).
**Step 4:** Attach the loaded program to a specific socket using `setsockopt`.

```c
setsockopt(socket, SOL_SOCKET, SO_ATTACH_BPF, &fd, sizeof(fd));

```

*Note:* Socket-attached eBPF programs cannot manipulate or drop the packet; they strictly observe and update userspace maps for telemetry.

---



## Master Cheat Sheet: Granular Technical Specifications

### I. eBPF Compilation, Assembly Traces, and Helpers

**Classic BPF (cBPF) `tcpdump` Traces**
When filtering via `tcpdump`, the cBPF virtual CPU executes specific instruction sets depending on the protocol.

* **Filter: `ip` (IPv4)**:


```nasm
(000) ldh      [12]
(001) jeq      #0x800           jt 2    jf 3
(002) ret      #96
(003) ret      #0

```


* **Filter: `ip6` (IPv6)**:


```nasm
(000) ldh      [12]
(001) jeq      #0x86dd          jt 2    jf 3
(002) ret      #96
(003) ret      #0

```


* **Filter: `tcp**`:


```nasm
(000) ldh      [12]
(001) jeq      #0x86dd          jt 2    jf 4
(002) ldb      [20]
(003) jeq      #0x6             jt 7    jf 8
(004) jeq      #0x800           jt 5    jf 8
(005) ldb      [23]
(006) jeq      #0x6             jt 7    jf 8
(007) ret      #96
(008) ret      #0

```



**eBPF Compilation Pipeline: C to x86 Native Code**
The compilation from restricted C to native machine code involves intermediate eBPF bytecode generation via Clang/LLVM, followed by in-kernel JIT compilation.

* **1. Restricted C Code:**
```c
static void init_array() {
    int key;
    for (key = 0; key < 1000; key++) {
        bpf_update_elem(map_fd[0], &key, &value1, BPF_ANY);
    }
}

```


* **2. eBPF Bytecode (Intermediate):**
```nasm
10: ldh [12]
11: jeq #0x800, 13, 12
12: jeq #0x805, 13, 18
13: ld [26]
14: jeq #SRC, 14, 18
15: ld len
16: jlt 0x400, 17, 18
17: ret #0xffff
18: ret #0

```


* **3. x86 Native Code (JIT Compiled):**
```nasm
mov eax, [ebp+8]
mov esi, [ebp+12]
mov edi, [ebp+16]
mov [ebp-4], edi
add [ebp-4], esi
add eax, [ebp-4]

```



**eBPF Helper Function Trace**
Helpers are native kernel functions called directly from eBPF assembly.

```nasm
// do some processing in assembly
(000) ...
(001) call bpf_ktime_get_ns()
(002) ...

```

---

### II. BTF (BPF Type Format) Base Supported Type Kinds

The BTF graph maps arbitrary C types to specific enumerated kinds to facilitate CO-RE relocations.

* `BTF_KIND_UNKN = 0` /* Unknown */


* `BTF_KIND_INT = 1` /* Integer */


* `BTF_KIND_PTR = 2` /* Pointer */


* `BTF_KIND_ARRAY = 3` /* Array */


* `BTF_KIND_STRUCT = 4` /* Struct */


* `BTF_KIND_UNION = 5` /* Union */


* `BTF_KIND_ENUM = 6` /* Enumeration up to 32-bit values */


* `BTF_KIND_FWD = 7` /* Forward */


* `BTF_KIND_TYPEDEF = 8` /* Typedef */


* `BTF_KIND_VOLATILE = 9` /* Volatile */


* `BTF_KIND_CONST = 10` /* Const */


* `BTF_KIND_RESTRICT = 11` /* Restrict */


* `BTF_KIND_FUNC = 12` /* Function */


* `BTF_KIND_FUNC_PROTO = 13` /* Function Proto */


* `BTF_KIND_VAR = 14` /* Variable */


* `BTF_KIND_DATASEC = 15` /* Section */


* `BTF_KIND_FLOAT = 16` /* Floating point */


* `BTF_KIND_DECL_TAG = 17` /* Decl Tag */


* `BTF_KIND_TYPE_TAG = 18` /* Type Tag */


* `BTF_KIND_ENUM64 = 19` /* Enumeration up to 64-bit values */



---

### III. Polycube CLI & REST API Generation

The Polycube framework translates YANG data models directly into interactive CLI commands and REST APIs.

**Auto-Generated REST API Endpoints (Bridge Example)**:

* `POST /bridge/`

* `GET /bridge/{name}/`

* `PUT /bridge/{name}/`

* `PATCH /bridge/{name}`

* `DELETE /bridge/{name}/`

* `GET /bridge/{name}/agingtime/`

* `PATCH /bridge/{name}/agingtime/`

* `GET /bridge/{name}/fwdtable/{mac}/{vlan}/`

* `PUT /bridge/{name}/fwdtable/{mac}/{vlan}/`

* `PATCH /bridge/{name}/fwdtable/{mac}/{vlan}/`

* `DELETE /bridge/{name}/fwdtable/{mac}/{vlan}/`

* `GET /bridge/{name}/fwdtable/{mac}/{vlan}/port/`

* `PATCH /bridge/{name}/fwdtable/{mac}/{vlan}/port/`


**CLI Syntax and Usage Examples**
The general syntax is `[object/context] [action] [parameters=value]`.

```bash
bridge add br1
bridge br1 ports add toveth1
bridge br1 ports toveth1 set peer="veth1"
bridge br1 filteringdb show 0xaabbccddeeff
bridge br1 stp show priority
bridge del br1

```

**Contextual CLI Help Menus**:

```bash
polycubectl bridge br1 ports add ?
keyword           type      description
<name>            string    Port Name
Optional Params:
status=value      string    Status of the port (UP or DOWN)
address=value     string    MAC address of the port
mode=value        string    Type of bridge interface: access/trunk
peer=value        string    Peer name, such as a network interfaces

```

---

### IV. Performance Benchmarks and Metrics

**Table 1: XDP Real Apps Tests (Single CPU core, Kernel 4.14)**

| Network Function | Traffic Control (TC) | XDP Generic | XDP Native |
| --- | --- | --- | --- |
| **eBPF baseline** | 2.60 Mpps | 5.20 Mpps | 11.34 Mpps |
| **Polycube baseline** | 2.38 Mpps | 4.16 Mpps | 8.58 Mpps |
| **Bridge** | 2.08 Mpps | 2.68 Mpps | 3.27 Mpps |
| **Loadbalancer** | 2.23 Mpps | 4.02 Mpps | 4.76 Mpps |
| **Policy-based Forwarder** | 1.93 Mpps | 2.53 Mpps | 2.53 Mpps |

*(Note: The XDP Redirect sample app achieved 8.39 Mpps)*.

**Table 2: SmartNIC Hardware Offload vs. Host XDP**

| Technology | Throughput (Mpps) |
| --- | --- |
| **iptables (legacy)** | 10.9 Mpps |
| **nftables** | 12.4 Mpps |
| **bpfilter (host driver XDP, JIT)** | 38.7 Mpps |
| **bpfilter (hardware offload)** | 59.5 Mpps (40 Gbps) |

**Polycube Kubernetes (K8s) Plugin Performance**

* **Same Pod Location:** Polycube achieves ~58 Gbps throughput, outperforming Calico v3.3 (~38 Gbps), Cilium v1.3 (~47 Gbps), kube-router (~48 Gbps), Romana (~41 Gbps), and Weavenet (~47 Gbps).


* **Different Pod Location:** Polycube achieves ~31 Gbps throughput.



**Polycube Framework Overheads (Throughput vs Lines of Code)**

| Application | Throughput | Lines of Code (Fast Path) | Lines of Code (Slow/Ctrl Path) |
| --- | --- | --- | --- |
| **xdp_redirect** | 6.97 Mpps | 64 | 176 |
| **pcn_simplefwd (XDP)** | 6.86 Mpps | 53 | 56 |
| **tc_redirect** | 1.60 Mpps | 17 | 0 |
| **pcn_simplefwd (TC)** | 1.55 Mpps | 17 | 0 |

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Master eBPF & Polycube Interactive Quiz</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f7f6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 { text-align: center; color: #2c3e50; }
        .question-card {
            background: #fff;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .question-text { font-size: 1.1em; font-weight: 600; margin-bottom: 15px; }
        .options { list-style-type: none; padding: 0; }
        .options li {
            background: #eef2f5;
            margin-bottom: 10px;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            transition: background 0.3s;
            border: 2px solid transparent;
        }
        .options li:hover { background: #d5e1df; }
        .options li.selected { border-color: #3498db; background: #e8f4fd; }
        .options li.correct { background: #d4edda; border-color: #28a745; color: #155724; }
        .options li.incorrect { background: #f8d7da; border-color: #dc3545; color: #721c24; }
        .submit-btn {
            background: #3498db;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            display: block;
            margin-top: 15px;
        }
        .submit-btn:hover { background: #2980b9; }
        .submit-btn:disabled { background: #95a5a6; cursor: not-allowed; }
        .feedback {
            margin-top: 15px;
            padding: 15px;
            border-radius: 5px;
            display: none;
            font-size: 0.95em;
            line-height: 1.5;
            background: #e9ecef;
            border-left: 5px solid #6c757d;
        }
    </style>
</head>
<body>

    <h1>Master eBPF & Polycube Quiz</h1>

    <div id="quiz-container"></div>

    <script>
        const quizData = [
            {
                q: "1. In what year and kernel version was the original Berkeley Packet Filter (BPF) introduced?",
                options: [
                    "2013, Kernel 3.15",
                    "1997, Kernel 2.1.75",
                    "2018, Kernel 4.14",
                    "2012, Kernel 3.0"
                ],
                ans: 1,
                exp: "The original BPF was introduced in Linux kernel 2.1.75 in 1997 as a generic in-kernel, event-based virtual CPU for packet filtering tools like tcpdump[cite: 11]."
            },
            {
                q: "2. Why is an eBPF program considered NOT Turing complete?",
                options: [
                    "It lacks support for the C programming language.",
                    "It is restricted by the verifier to a bounded number of instructions and cannot have unbounded loops.",
                    "It cannot perform floating-point arithmetic calculations.",
                    "It relies exclusively on userspace memory maps."
                ],
                ans: 1,
                exp: "The eBPF verifier enforces a bounded program size and bounds the maximum number of instructions per execution path, which mandates that loops must be unrolled, making it impossible to support completely arbitrary (Turing complete) programs[cite: 19]."
            },
            {
                q: "3. What component translates eBPF assembly instructions into native architecture code (e.g., x64) at runtime?",
                options: [
                    "The eBPF Verifier",
                    "The Clang Frontend",
                    "The Just-In-Time (JIT) Compiler",
                    "The Polycube Daemon"
                ],
                ans: 2,
                exp: "The assembly BPF bytecode is translated into native assembly code at run-time utilizing a standard in-kernel Just-in-time translator (JIT)[cite: 20]."
            },
            {
                q: "4. Which of the following is NOT a valid action an eBPF program can take on a packet upon interception?",
                options: [
                    "Drop the packet",
                    "Queue the packet in a CPU sleep state indefinitely",
                    "Redirect the packet to another point in the kernel",
                    "Return the packet to the Linux stack unmodified"
                ],
                ans: 1,
                exp: "After processing, an eBPF program can return the packet to the stack, drop it, or redirect it to another point in the kernel[cite: 5]. There is no native construct to sleep the CPU indefinitely with a packet, which would violate the efficiency/DoS protections[cite: 20]."
            },
            {
                q: "5. When utilizing the eXpress Data Path (XDP), what is the key difference between XDP Generic and XDP Native?",
                options: [
                    "XDP Generic operates before skb allocation, while XDP Native operates after.",
                    "XDP Generic requires SmartNIC offload, while Native runs on the host CPU.",
                    "XDP Native is supported directly in the device driver and operates on raw packets, while XDP Generic offers fallback support for drivers without native capabilities.",
                    "XDP Native supports tail calls, whereas XDP Generic does not."
                ],
                ans: 2,
                exp: "XDP Native provides XDP support directly in the network device driver before the Linux skb is created. XDP Generic offers fallback support for drivers that do not provide native functionality and is invoked by setting XDP_FLAGS_SKB_MODE[cite: 31]."
            },
            {
                q: "6. How do eBPF programs establish 'Service Chains' to process complex functions in sequence?",
                options: [
                    "By invoking userspace REST APIs sequentially.",
                    "Using 'tail calls' which execute like function calls without returning, jumping directly to another eBPF program.",
                    "By modifying the Linux hardware interrupt vectors.",
                    "By compiling multiple C programs into a monolithic kernel module."
                ],
                ans: 1,
                exp: "eBPF programs can be connected via tail calls, which jump directly to another eBPF program (acting as a function call without a return) to split complex functions into modular components[cite: 33]."
            },
            {
                q: "7. How do eBPF programs safely implement complex processing that requires structural loops or kernel structural access?",
                options: [
                    "By escaping the sandbox to run raw C.",
                    "By utilizing eBPF Helpers (native kernel functions called from the eBPF bytecode).",
                    "By downloading dynamic libraries from userspace.",
                    "By disabling the in-kernel verifier at compile time."
                ],
                ans: 1,
                exp: "Because the verifier restricts complex processing like loops, eBPF code utilizes Helpers—functions implemented natively in the Linux kernel that are called as assembly function calls from the bytecode[cite: 34]."
            },
            {
                q: "8. What is the standard compilation toolchain pipeline for generating eBPF bytecode from C source code?",
                options: [
                    "GCC -> ELF binary -> JIT",
                    "Clang (C frontend) -> LLVM (optimizer/code gen) -> Assembly eBPF Code",
                    "Python interpreter -> BCC -> Native x64",
                    "YANG -> Polycubed -> JIT"
                ],
                ans: 1,
                exp: "Source code written in restricted C is passed to the Clang frontend to generate an intermediate representation, which is processed by the LLVM optimizer backend to output assembly eBPF code[cite: 38]."
            },
            {
                q: "9. In the Polycube architecture, where is complex protocol management like ARP handling or Spanning Tree Protocol executed?",
                options: [
                    "In the eBPF Fast Path.",
                    "In the SmartNIC hardware offload.",
                    "In the Slow Path running in userspace.",
                    "In the XDP Generic driver module."
                ],
                ans: 2,
                exp: "Tasks that are unfeasible in the kernel (e.g., missing ARP entries) or affect performance are moved to the Slow Path, which runs in userspace. The Control path handles routing protocols/Spanning Tree[cite: 47, 48]."
            },
            {
                q: "10. How does Polycube achieve 'Code Tailoring' to maintain optimal data plane performance?",
                options: [
                    "It pre-compiles 100 monolithic variants of every network function.",
                    "It dynamically creates and injects only the minimum eBPF data path code needed to support the specific features toggled on by the user.",
                    "It delegates all logic to DPDK to bypass the kernel.",
                    "It compresses the bytecode using BTF before injection."
                ],
                ans: 1,
                exp: "With eBPF, Polycube dynamically compiles and creates the minimum data path code needed to support requested features, turning features on/off dynamically to achieve optimal performance[cite: 59]."
            },
            {
                q: "11. What technology provides a compact, <6MB representation of arbitrary types in the Linux kernel to assist with eBPF relocations?",
                options: [
                    "DWARF",
                    "BCC",
                    "CO-RE",
                    "BTF (BPF Type Format)"
                ],
                ans: 3,
                exp: "BTF (BPF Type Format) is a compact variant of DWARF utilized to represent type information in the kernel, requiring less than 6MB for the entire section[cite: 68]."
            },
            {
                q: "12. What primary issue does eBPF CO-RE (Compile Once, Run Everywhere) solve?",
                options: [
                    "It allows eBPF code to run on Windows and macOS.",
                    "It resolves breakage caused when structural layouts in the kernel (e.g., task_struct) change across different Linux versions.",
                    "It automatically translates Python code into restricted C.",
                    "It replaces the LLVM compiler chain with a pure-Rust alternative."
                ],
                ans: 1,
                exp: "eBPF programs run within the volatile kernel environment where struct layouts vary. CO-RE fixes this by matching BTF relocations from the compiler against the live kernel's BTF data at load time[cite: 71, 73]."
            },
            {
                q: "13. According to the eBPF licensing model, what occurs if an eBPF program is compiled without a GPL license declaration?",
                options: [
                    "It is rejected by the Clang compiler.",
                    "It is executed normally but operates 50% slower.",
                    "Certain kernel helpers that require GPL will refuse to serve the program.",
                    "The verifier deletes the program immediately upon injection."
                ],
                ans: 2,
                exp: "Injected eBPF code requires an explicit license indication. Non-GPL code is allowed in the kernel, but some specific kernel helpers refuse to serve non-GPL programs[cite: 40]."
            },
            {
                q: "14. How does the Polycube framework generate its REST APIs and CLI interfaces?",
                options: [
                    "They are manually coded in C for every new network function.",
                    "They are automatically generated from a YANG data model describing the service.",
                    "They are scraped dynamically from the BPF verifier logs.",
                    "They are downloaded from the PLUMgrid external repository."
                ],
                ans: 1,
                exp: "Polycube uses a YANG data model to define the syntax and structure of the service data, from which both the CLI and REST APIs are automatically generated, removing the need for manual UI coding[cite: 53]."
            },
            {
                q: "15. Which of the following accurately describes the relationship between eBPF and P4?",
                options: [
                    "P4 is a subset of the restricted C language used by eBPF.",
                    "P4 focuses strictly on software events, while eBPF is heavily tied to hardware switches.",
                    "P4 is a high-level language for protocol-independent packet processing that can be compiled *to* eBPF as a target.",
                    "eBPF natively enforces protocol independency exactly like P4."
                ],
                ans: 2,
                exp: "P4 is a high-level programming language for packet forwarding that can be compiled for different targets, including eBPF. eBPF itself does not enforce protocol independency natively[cite: 75]."
            },
            {
                q: "16. In an eBPF socket-bound program created via `SO_ATTACH_BPF`, what limitation exists regarding packet manipulation?",
                options: [
                    "The program cannot read the packet metadata.",
                    "The program is unable to store data in eBPF maps.",
                    "The program cannot do anything to influence the delivery or modify the contents of the packet.",
                    "The program can only drop the packet, not redirect it."
                ],
                ans: 2,
                exp: "Programs attached to sockets via `SO_ATTACH_BPF` cannot influence delivery or modify the contents of the packet; they simply store information/telemetry into eBPF maps for userspace consumption[cite: 42]."
            },
            {
                q: "17. What mechanism allows Polycube's Slow Path to return packets downstream (Userspace -> Kernel)?",
                options: [
                    "Performance Ring Buffer",
                    "XDP Native Driver",
                    "A Tap interface combined with an eBPF map carrying metadata",
                    "Direct Memory Access (DMA) to the SmartNIC"
                ],
                ans: 2,
                exp: "For downstream communication (userspace to kernel), Polycube utilizes a Tap interface along with an eBPF map to transport the additional metadata (Module ID, InPort ID) needed to deliver the packet[cite: 50]."
            },
            {
                q: "18. What is the fundamental difference between DPDK and eBPF/XDP regarding integration?",
                options: [
                    "eBPF runs on vanilla Linux kernels, whereas DPDK requires modified systems and additional kernel modules.",
                    "eBPF is Turing complete, whereas DPDK is severely restricted by a verifier.",
                    "eBPF bypasses the kernel completely, whereas DPDK runs exclusively inside the kernel stack.",
                    "DPDK supports SmartNIC offloads, whereas eBPF does not."
                ],
                ans: 0,
                exp: "eBPF/XDP runs on vanilla kernels without kernel modifications or patches, whereas DPDK requires a modified system with additional kernel modules and bypasses the kernel entirely to user space[cite: 78]."
            },
            {
                q: "19. Which map type allows distinct eBPF programs, running concurrently on different CPU cores, to maintain isolated statistics without cache synchronization overhead?",
                options: [
                    "Global HashMap",
                    "Per-CPU Maps",
                    "LRUMap",
                    "AF_XDP Sockets"
                ],
                ans: 1,
                exp: "Per-CPU maps create multiple instances of the same map private to each CPU, preventing data synchronization overhead between CPU caches and providing much higher efficiency[cite: 26]."
            },
            {
                q: "20. When intercepting events 'Aside', how does eBPF interact with the kernel workflow?",
                options: [
                    "It delays the kernel workflow until eBPF processing completes.",
                    "It receives the actual event and can manipulate the payload before releasing it.",
                    "It terminates the event immediately.",
                    "It receives a copy of the event, and the original event continues its way through the kernel completely unmodified."
                ],
                ans: 3,
                exp: "In the 'aside' interception model, a copy of the event is delivered to eBPF for monitoring, while the original event continues through the kernel unhindered and unmodified[cite: 23]."
            }
        ];

        const container = document.getElementById('quiz-container');

        quizData.forEach((item, index) => {
            const card = document.createElement('div');
            card.className = 'question-card';

            const questionText = document.createElement('div');
            questionText.className = 'question-text';
            questionText.innerText = item.q;
            card.appendChild(questionText);

            const optionsList = document.createElement('ul');
            optionsList.className = 'options';

            let selectedIdx = null;

            item.options.forEach((optText, optIdx) => {
                const optLi = document.createElement('li');
                optLi.innerText = optText;
                optLi.onclick = () => {
                    if(card.querySelector('.submit-btn').disabled) return;
                    Array.from(optionsList.children).forEach(child => child.classList.remove('selected'));
                    optLi.classList.add('selected');
                    selectedIdx = optIdx;
                };
                optionsList.appendChild(optLi);
            });
            card.appendChild(optionsList);

            const submitBtn = document.createElement('button');
            submitBtn.className = 'submit-btn';
            submitBtn.innerText = 'Submit Answer';
            
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'feedback';
            feedbackDiv.innerHTML = `<strong>Explanation:</strong> ${item.exp}`;

            submitBtn.onclick = () => {
                if(selectedIdx === null) {
                    alert("Please select an answer first.");
                    return;
                }
                submitBtn.disabled = true;
                const listItems = optionsList.children;
                if(selectedIdx === item.ans) {
                    listItems[selectedIdx].classList.add('correct');
                } else {
                    listItems[selectedIdx].classList.add('incorrect');
                    listItems[item.ans].classList.add('correct');
                }
                feedbackDiv.style.display = 'block';
            };

            card.appendChild(submitBtn);
            card.appendChild(feedbackDiv);
            container.appendChild(card);
        });
    </script>
</body>
</html>

```