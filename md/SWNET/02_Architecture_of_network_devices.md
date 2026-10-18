# Architecture of Network Devices: Master Cheat Sheet

## 1. Conceptual Architecture of a Network Device

Network devices are conceptually divided into three interacting planes.

### The Three Planes

* **Data Plane**: Handles packets as fast as possible. Responsible for receiving, processing, and transmitting packets (like an assembly line). Handles QoS (marking), filtering (security), encapsulations, queuing, and policing. Traffic usually travels *through* the device.


* **Control Plane**: Controls how the data plane behaves. Derives routing tables and discovers network topologies via routing protocols (OSPF, EIGRP, BGP). Packets usually originate or terminate at the device.


* **Management Plane**: Supervises the device and running services. Interacts with admins or Network Management Systems (NMS) via CLI, GUI, SNMP, NETConf, or RESTConf for configuration and monitoring.



### Device-Specific Implementations

* **Routers**:
* *Control Plane*: Executes OSPF, static routes.


* *Data Plane*: Forwards packets via the Forwarding Information Base (FIB) and hardware ASICs.




* **Firewalls**:
* *Control Plane*: Dynamically reacts to threats (e.g., adding malicious SessionIDs to blacklists).


* *Data Plane*: Checks packet headers (IP, TCP/UDP) and payloads (Deep Packet Inspection), exploiting ASICs, regular expression matching, and CAMs.





### Control Plane Operations on Received Traffic

* **ARP Handling**: If a next-hop MAC address is missing in the ARP cache, the data plane buffers the packet and sends the request to the control plane, which generates an ARP Request, waits for the reply, updates the ARP table, and resumes transmission.


* **ICMP Generation**: Packets with TTL = 0 generate a data plane exception and are routed to the control plane to generate an "ICMP time exceeded" message.



## 2. Hardware and Software Requirements

### Management and Control Planes

* Require a large amount of code but little processing power.


* Execute complex, low-frequency tasks (routing updates, configuration).


* Implemented entirely in software using general-purpose CPUs and standard DRAM.



### Data Plane

* Requires a small amount of code but massive processing power.


* Executed at extremely high speeds, putting severe pressure on processing budgets.


* For a 10Gbps link handling 64B packets, the processing budget per packet is just 67.2ns (or roughly 202 CPU ticks).


* Usually implemented in hardware (ASICs, FPGAs) for speeds above ~100 Gbps, though pure software data planes are emerging for cloud/virtualized environments.



### Memory Hierarchy & Latency

* **Register**: 0.2ns.


* **Cache**: 1-40ns.


* **Main Memory**: 80-140ns. (A single cache miss costs ~60ns, nearly exhausting the 10Gbps per-packet budget).


* **CXL-Memory**: 170-250ns.



## 3. Dedicated Data Plane Hardware

### Context-Addressable Memories (CAM)

Associative memory where the input is the data being searched for, and the output is the memory location.

* **BCAM (Binary CAM)**: Exact match lookup (returns port based on MAC address in 802.1D bridges).


* **TCAM (Ternary CAM)**: Matches 1s, 0s, and "don't care" (*) states. Enables longest prefix matching for CIDR routing. Very fast ($O(1)$ lookup time) but power-hungry, expensive, and limited in silicon space.



### Processors and Accelerators

* **ASICs (Application-Specific Integrated Circuits)**: Microchips designed for specific applications (e.g., L2/L3 forwarding). High development cost, limited programmability, excellent performance.


* **NPUs (Network Processing Units)**: Massive parallelism (100+ simple RISC cores), heavily multi-threaded to hide memory latency. Includes hardware accelerators for cryptography, regex, and table lookups. Requires a hardware scheduler/load balancer to prevent TCP packet reordering. Struggles with a few "elephant" sessions; works best with many "mice" sessions.


* **Fast/Slow Path Design**:
* *Fast Path*: Handles normal/minimal processing traffic via HW or highly optimized SW. Contains most-used routes.


* *Slow Path*: Handles complex, unusual traffic (IP fragmentation in older devices, full routing tables) flexibly in CPU software. Open vSwitch utilizes this design with Tuple Space Search classifiers.





## 4. Hardware Trends & Software Data Planes

### Processor Limitations

* **Dennard Scaling**: Stated that transistor dimensions scale down by 30% per generation, keeping power density constant while increasing clock frequency. This scaling ended around 2006, leading to a plateau in clock speeds.


* **Moore's Law**: Transistor density continues to increase.


* **Dark Silicon**: Because voltage scaling slowed down, powering all dense transistors simultaneously exceeds power envelopes, requiring "idle" cores or reduced clock speeds.


* **Result**: Performance scaling shifted exclusively to multicore architectures (parallelism), shifting the optimization burden to programmers.



### Future Directions

* **Domain-Specific Architectures (DSA)**: Tailoring hardware to specific domains rather than single applications (e.g., GPUs for graphics, Tensor Units for ML, SmartNICs for networks). Utilizes Domain-Specific Languages (DSL) like P4.


* **SmartNICs**: Offload eBPF (XDP) programs to general-purpose CPUs on the NIC, or use specific ASICs (e.g., Pensando CAPRI) to run P4 data planes at wire speed while maintaining coherency.



## 5. Router Architectures

### Pure Software Routers

* **Architecture**: PHY/MAC functions on NIC, packets sent across a shared bus to main memory, processed by the central CPU.


* **Bottleneck**: Packets cross the shared bus twice. Memory access and central CPU speed strictly limit throughput to hundreds of Mbps (or 100-200Gbps using highly optimized software/multicore setups).



### Linecard-Based Routers & Switching Fabrics

* **Architecture**: Dedicated linecards with local packet processors and FIBs. Connected via a dedicated Switching Fabric (Crossbar) rather than a shared bus.


* **Switching Fabric Queuing Strategies**:
* **Output Queuing (OQ)**: Requires no arbiter. Demands a switching fabric speedup of $N$ and a memory buffer access speed of $N \times R$ (where $N$ = physical ports, $R$ = port speed). Expensive and energy-hungry.


* **Input Queuing (IQ)**: Requires a speedup of $1$ and access speed $R$. Suffers from **Head-of-Line (HoL) Blocking**, where a blocked packet at the head of a queue prevents subsequent packets from reaching idle output ports. Maximum theoretical utilization is 58.6%.


* **Virtual Output Queuing (VOQ)**: Solves HoL blocking. Maintains a separate queue for every output port at each input port (total of $N^2$ queues). Requires an arbiter to configure the crossbar and find a non-blocking subgraph per cycle.


* **Buffered Fabric**: Places buffers directly inside the crossbar to handle collisions. Expensive due to limited on-chip memory limits.





---

## Practical Exercises

**Exercise 1: Packet Processing Budget Calculation**
**Scenario:** You are programming a software data plane for a 100Gbps half-duplex Ethernet link. Calculate the maximum number of packets per second for 64B packets and the corresponding CPU time budget per packet.
**Step-by-Step Solution:**

1. Determine the maximum packets per second for 100Gbps. Based on network fundamentals scaling up from 10Gbps (14.88 Mpps):
$Mpps_{100G} = 14.88 \times 10 = 148.8 \text{ Mpps}$.


2. Calculate the time interval between packets:
$Time = \frac{1}{148,800,000} \text{ seconds} = 6.72 \text{ ns}$.


3. **Result:** Your processing budget per packet is strictly 6.72ns. If a main memory access (cache miss) costs ~60ns, you must utilize local registers or highly optimized L1 caches, or else the system will drop packets.



**Exercise 2: Crossbar Queuing Architecture Strategy**
**Scenario:** A 16-port 10Gbps switch requires a new crossbar fabric design. Compare the memory speed requirements of Output Queuing (OQ) versus Virtual Output Queuing (VOQ), and determine the number of queues needed for VOQ.
**Step-by-Step Solution:**

1. Determine parameters: $N = 16$, $R = 10 \text{ Gbps}$.


2. Calculate OQ requirements: OQ requires a buffer access speed of $N \times R$.
$Speed_{OQ} = 16 \times 10 = 160 \text{ Gbps}$.


3. Calculate VOQ requirements: VOQ requires a buffer access speed equal to the line rate $R$.
$Speed_{VOQ} = 10 \text{ Gbps}$.


4. Calculate VOQ total queues: VOQ maintains an output queue for every input port.
$Queues = N^2 = 16^2 = 256 \text{ virtual output queues}$.


5. **Result:** VOQ avoids HoL blocking and only requires 10Gbps memory access speeds, but demands managing 256 separate queues and a complex central arbiter.

Addendum: Exhaustive Granular Details1. Hardware Data & Historical TrendsNetwork Speed vs. Processing Budget (64B packets):   1Gbps (half duplex): 1.488Mpps | 672ns budget per packet.10Gbps (half duplex): 14.88Mpps | 67.2ns budget per packet.100Gbps (half duplex): 148.8Mpps | 6.72ns budget per packet.Memory Improvement (1999-2017): While DRAM capacity improved by 128x and bandwidth by 20x, latency only improved by 1.3x.   Traffic & Capacity Trends (1980-2001):   Line Capacity: $2x / 7 \text{ months}$.User Traffic: $2x / 12 \text{ months}$.Router Capacity & Moore's Law: $2x / 18 \text{ months}$.DRAM Random Access Time: $1.1x / 18 \text{ months}$.Shared Bus Limits: A PCIx 2.0 16x bus provides $8\text{GB/s}$, which is only just enough to support a single 40Gbps card operating in full duplex.   2. Instruction Set Architecture (ISA) & DSLsISA Usage Stats: A study of an IBM 360 compiler showed 10 instructions accounted for 80% of executed instructions, 16 for 90%, 21 for 95%, and 30 for 99%. For the IBM 370, a COBOL program executed only 84 of 183 available instructions, with 48 representing 99.08% of execution.   Domain-Specific Languages (DSL) Examples: OpenGL, TensorFlow (used for Google's Tensor unit chip), and P4.   3. "Dark Silicon" Academic QuotesAt 22nm, 21% of a fixed-size chip must be powered off; at 8nm, this grows to over 50%.   Through 2024, only a 7.9x average speedup is possible across parallel workloads, leaving a nearly 24-fold gap from a target of doubled performance per generation.   4. Highly Specific Vendor Hardware SpecsCisco MDS 9000 Family:   Data plane features Dual Redundant Centralized Arbiters capable of scheduling >1 Billion frames/second, and crossbars operate at 3x over speed utilizing "Superframing".   Modules explicitly listed in physical views: 16-Port and 32-Port 1/2-Gbps Host-Optimized Over-Subscribed Linecards, Cisco MDS 9513 Crossbar, Supervisor-1, Supervisor-2, and the 32-Port Storage Services Module (which includes Virtualization ASICs and TCAMs).   Cisco 12816 Physical Specs:   Capacity: 16 slots, 40 Gbps/slot, totaling 640Gbps (scaling to 1.28Tbps commercially).Weight: 187 Kg (fully configured).Power: 4800W maximum (requires 3 AC-input power supplies for N+1 redundancy).Dimensions: 19" wide, 60cm deep, 180cm tall.Cisco CSR-1 Specs:   Base chassis range from 320-Gbps, 640-Gbps, to 1.2-Tbps.Multi-chassis configurations scale from 1.2 Tbps up to 92 Tbps.Supports a maximum of 72 chassis per linecard and 8 chassis per fabric switching.

---

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Network Device Architecture Quiz</title>
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 800px; margin: auto; padding: 20px; background-color: #f4f6f8; color: #333; }
    h1 { text-align: center; color: #2c3e50; }
    .quiz-container { background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .question { margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
    .question h3 { margin-top: 0; color: #34495e; font-size: 1.1em; }
    .options label { display: block; margin-bottom: 8px; cursor: pointer; padding: 8px; border-radius: 4px; transition: background 0.2s; }
    .options label:hover { background: #f0f2f5; }
    .options input { margin-right: 10px; }
    button { display: block; width: 100%; padding: 15px; font-size: 1.1em; background: #3498db; color: #fff; border: none; border-radius: 5px; cursor: pointer; margin-top: 20px; }
    button:hover { background: #2980b9; }
    .feedback { margin-top: 10px; padding: 15px; border-radius: 5px; display: none; font-size: 0.95em; line-height: 1.5; }
    .feedback.correct { background-color: #d4edda; color: #155724; border-left: 5px solid #28a745; display: block; }
    .feedback.incorrect { background-color: #f8d7da; color: #721c24; border-left: 5px solid #dc3545; display: block; }
</style>
</head>
<body>

<h1>Network Architecture Master Quiz</h1>
<div class="quiz-container" id="quizForm">
    <!-- Questions will be dynamically generated here -->
</div>
<button onclick="submitQuiz()">Submit Quiz & Reveal Explanations</button>

<script>
const quizData = [
    {
        q: "1. Which plane is strictly in charge of handling packets as fast as possible?",
        opts: ["Management Plane", "Control Plane", "Data Plane", "Forwarding Plane"],
        ans: 2,
        exp: "The Data plane is in charge of handling packets as fast as possible, performing tasks like filtering, encapsulations, and queuing[cite: 5]."
    },
    {
        q: "2. According to the architecture of a router, where are OSPF and routing protocols executed?",
        opts: ["Data Plane", "Control Plane", "ASIC", "Virtual Output Queue"],
        ans: 1,
        exp: "Routing protocols like OSPF, EIGRP, and BGP are executed in the Control plane to discover the network topology[cite: 6, 7]."
    },
    {
        q: "3. If a packet's TTL drops to 0, which component generates the ICMP time exceeded message?",
        opts: ["Data plane directly", "Control plane via an exception", "Management plane", "The switching arbiter"],
        ans: 1,
        exp: "Packets with TTL = 0 generate an exception in the data plane and are sent to the control plane, which generates the ICMP time exceeded message[cite: 10]."
    },
    {
        q: "4. What is the approximate processing budget per packet for a 10Gbps link dealing with 64-byte packets?",
        opts: ["6.72ns", "67.2ns", "672ns", "6.7µs"],
        ans: 1,
        exp: "At 10Gbps, a maximum of 14.88Mpps must be handled, providing exactly 67.2ns (or roughly 202 CPU ticks) to process a 64B packet[cite: 12, 13]."
    },
    {
        q: "5. What is the defining capability of a Ternary CAM (TCAM) compared to a Binary CAM (BCAM)?",
        opts: ["It uses 3-phase power", "It stores state internally without DRAM", "It can match 0, 1, and 'don't care' values", "It processes three packets simultaneously"],
        ans: 2,
        exp: "TCAM enables lookups to match both 1 and 0 bits but also have a 'don't care' value, often shown as '*', essential for longest prefix matching[cite: 19]."
    },
    {
        q: "6. Which component is known to be very fast ($O(1)$ lookup) but extremely power-hungry and expensive, limiting its size in network devices?",
        opts: ["SRAM", "ASIC", "TCAM", "NPU"],
        ans: 2,
        exp: "TCAMs are very fast (lookup in $O(1)$) but are power-hungry, expensive, and consume a large amount of silicon space[cite: 19]."
    },
    {
        q: "7. Why do Network Processing Units (NPUs) use massive parallelism and hardware threads?",
        opts: ["To reduce silicon footprint", "To overcome memory access latency", "To enable BGP routing", "To act as the management plane"],
        ans: 1,
        exp: "NPUs use a massive number of threads to overcome memory latency; when a thread waits on memory, the CPU switches to a new thread[cite: 24]."
    },
    {
        q: "8. A Fast/Slow path design in network processing implies:",
        opts: ["Hardware processes slow paths while software handles fast paths.", "Routing tables are split randomly.", "Common processing takes a highly optimized Fast Path; unusual/complex packets take a flexible CPU-based Slow Path.", "All packets are processed twice to ensure reliability."],
        ans: 2,
        exp: "The Fast Path handles packets needing minimal/normal processing, while the Slow Path acts as a flexible, CPU-based route for unusual/complex processing[cite: 27, 28]."
    },
    {
        q: "9. Which software switch utilizes a fast/slow path design with Tuple Space Search classifiers?",
        opts: ["Cisco IOS", "Open vSwitch", "Linux iptables", "DPDK"],
        ans: 1,
        exp: "Open vSwitch implements a slowpath with full OpenFlow and a fastpath with two cache levels using Tuple Space Search classifiers[cite: 29]."
    },
    {
        q: "10. Dennard scaling breakdown around 2006 directly resulted in the inability to:",
        opts: ["Increase transistor density.", "Increase CPU clock frequencies.", "Use hardware accelerators.", "Implement routing tables in memory."],
        ans: 1,
        exp: "The breakdown of Dennard scaling caused an inability to increase clock frequencies, triggering the shift to multicore processors[cite: 37]."
    },
    {
        q: "11. 'Dark silicon' refers to:",
        opts: ["Unused ASIC routing tables.", "The physical layer of fiber optic transceivers.", "Transistor area that must remain inactive to avoid violating power constraints.", "Silicon not yet initialized by the bootloader."],
        ans: 2,
        exp: "Due to power density limits, a fraction of an integrated circuit must remain inactive at any given time without violating power constraints, known as dark silicon[cite: 37]."
    },
    {
        q: "12. What was the major architectural bottleneck in early pure software routers (e.g., pre-1990s PCs)?",
        opts: ["The TCAM", "The Switching Arbiter", "The Shared Bus", "The Output Queue"],
        ans: 2,
        exp: "In early software routers, packets had to cross the shared bus twice (NIC to memory, memory to NIC), creating a significant bottleneck[cite: 54, 55]."
    },
    {
        q: "13. In modern linecard-based routers, how is the shared bus bottleneck resolved?",
        opts: ["By removing linecards entirely.", "By replacing it with a dedicated Switching Fabric (Crossbar).", "By using 100G Ethernet externally.", "By routing directly through the Supervisor CPU."],
        ans: 1,
        exp: "The shared bus is replaced with a dedicated switching fabric (crossbar), enabling multiple simultaneous packet transfers[cite: 60]."
    },
    {
        q: "14. Output Queuing (OQ) requires a switching fabric speedup of:",
        opts: ["1", "N / 2", "N", "N^2"],
        ans: 2,
        exp: "To guarantee wire speed transfers in Output Queuing, the switching fabric needs a speedup of N (the number of physical ports)[cite: 62]."
    },
    {
        q: "15. What is 'Head-of-Line (HoL) Blocking' in Input Queuing?",
        opts: ["When a packet is dropped due to TTL expiry.", "When a packet at the front of a queue blocks a subsequent packet destined for an idle port.", "When the arbiter runs out of memory.", "When TCAM limits are reached."],
        ans: 1,
        exp: "HoL blocking occurs when a packet cannot be transferred because it is blocked by a preceding packet in the same queue waiting for a busy port[cite: 63]."
    },
    {
        q: "16. How does Virtual Output Queuing (VOQ) resolve HoL blocking?",
        opts: ["By speeding up the crossbar to N.", "By moving all queues to the Supervisor.", "By creating a dedicated queue for each output port at every input port.", "By discarding colliding packets instantly."],
        ans: 2,
        exp: "VOQ creates separate queues at each input port for every output port (N^2 queues total), eliminating Head-of-Line blocking while maintaining a speedup of 1[cite: 65]."
    },
    {
        q: "17. A 'Buffered Fabric' design introduces buffers:",
        opts: ["Directly inside the Supervisor RAM.", "Directly inside the crossbar.", "Only on the egress MAC.", "In a remote datacenter storage server."],
        ans: 1,
        exp: "A buffered fabric has buffers inside the crossbar to store colliding packets, reducing the required speedup to 1, but is expensive[cite: 66]."
    },
    {
        q: "18. What is the fundamental concept behind P4?",
        opts: ["It is a hardware form of Linux iptables.", "It is a high-level programming language for protocol-independent packet forwarding.", "It stands for Peripheral PCIe Packet Processing.", "It is an older version of IPv6."],
        ans: 1,
        exp: "P4 is a high-level, protocol-independent programming language for packet forwarding data planes based on match and action concepts[cite: 51]."
    },
    {
        q: "19. The Pensando CAPRI ASIC is an example of a:",
        opts: ["Traditional unmanaged hub.", "Legacy pure-software router.", "SmartNIC providing hardware acceleration and P4 programmability.", "Pure TCAM memory stick."],
        ans: 2,
        exp: "The Pensando CAPRI ASIC is a SmartNIC that features ARM cores, hardware co-processors, and a P4 packet processing dataplane[cite: 50]."
    },
    {
        q: "20. Why might a network architect choose Domain-Specific Architectures (DSA) for future hardware?",
        opts: ["To maintain the legacy Dennard scaling laws.", "To use standard DRAM for packet processing.", "To achieve higher efficiency by tailoring hardware explicitly to the characteristics of a specific application domain.", "To run full graphical desktops on switches."],
        ans: 2,
        exp: "DSAs achieve higher efficiency by tailoring the hardware architecture to the domain's characteristics, introducing effective parallelism and memory use (e.g., neural net processors or programmable NICs)[cite: 46, 47]."
    }
];

const container = document.getElementById('quizForm');
quizData.forEach((qObj, index) => {
    let questionHTML = `<div class="question" id="q-block-${index}">
        <h3>${qObj.q}</h3>
        <div class="options">`;
    qObj.opts.forEach((opt, optIndex) => {
        questionHTML += `<label><input type="radio" name="q${index}" value="${optIndex}"> ${opt}</label>`;
    });
    questionHTML += `</div><div class="feedback" id="feedback-${index}"></div></div>`;
    container.innerHTML += questionHTML;
});

function submitQuiz() {
    quizData.forEach((qObj, index) => {
        const radios = document.getElementsByName('q' + index);
        let selectedValue = -1;
        for (let radio of radios) {
            if (radio.checked) {
                selectedValue = parseInt(radio.value);
                break;
            }
        }
        
        const feedbackDiv = document.getElementById('feedback-' + index);
        if (selectedValue === qObj.ans) {
            feedbackDiv.className = 'feedback correct';
            feedbackDiv.innerHTML = `<strong>Correct!</strong> <br><em>Motivation/Explanation:</em> ${qObj.exp}`;
        } else {
            feedbackDiv.className = 'feedback incorrect';
            feedbackDiv.innerHTML = `<strong>Incorrect.</strong> The correct answer was option ${qObj.ans + 1}. <br><em>Motivation/Explanation:</em> ${qObj.exp}`;
        }
    });
}
</script>
</body>
</html>

```