## Network Monitoring with eBPF: Master Cheat Sheet

### 1. Core Technologies & Concepts

* **eBPF (Extended Berkeley Packet Filter):** A technology used to analyze network traffic and extract statistics. Programs are executed in the kernel at a high privilege level.


* **libbpf:** A C library that manages the lifecycle of eBPF programs.


* Embeds an eBPF loader to parse eBPF objects in ELF (Executable and Linkable Format).


* Identifies eBPF programs and maps, injecting them into the kernel.


* Provides an API abstracting the Linux `bpf()` system call.


* Provides helper methods like `bpf_map_lookup_elem()` to interact with maps from user space.




* **bpftool:** A command-line utility built on `libbpf` for interacting with the eBPF subsystem.


* Can generate a C header "skeleton" from an eBPF object, allowing the application to be shipped as a single, self-contained executable.





### 2. Architecture of an eBPF Application

An eBPF application comprises two main components:

1. **In-kernel eBPF program:** Attached to a hook point and executed for each packet.


2. **User-space control program:** Manages the eBPF program's lifecycle and interacts with it via eBPF maps.



**Standard File Structure:**

* `network_monitor.h`: Shared C header with definitions (e.g., map statistics) common to both user space and the eBPF program.


* `network_monitor.bpf.c`: The eBPF program itself. Defines the map and the function executed at the hook point. Accepts a `struct __sk_buff` parameter containing packet metadata and buffer pointers. Updates L3 protocol statistics.


* `network_monitor.c`: The user-space control program. Includes the generated eBPF skeleton, creates the hook point, loads/attaches the program, polls statistics, and cleans up upon exit.



### 3. Hook Points & Networking Stack

An eBPF hook point is a designated location in the kernel where eBPF programs can be attached.

* **Low-level hooks (eBPF/XDP, eBPF/TC):** Process bare packets early in the network stack. Offer higher processing throughput but increased complexity.


* **High-level hooks (eBPF/socket):** Slower but easier to use due to ready-to-use kernel data structures.


* **Kernel functions:** e.g., kprobes tracing TCP connection operations.



**eBPF/TC (Traffic Control):**

* Allows analysis of bare packets (incoming and outgoing) early in the stack.


* Attached via **qdisc (queuing discipline)**, which defines packet scheduling.


* Uses a qdisc of type **clsact (Classify Action)** to attach classifiers/filters in both ingress and egress directions.



### 4. The eBPF Verifier

To guarantee kernel integrity, the verifier analyzes programs before injection to prevent invalid memory accesses.

* **Packet Bound Checks:** Programmers must explicitly check that packet buffers are large enough before accessing headers.


* **Action on Failure:** If limits are exceeded, the packet should be dropped or processing aborted (e.g., returning `TC_ACT_SHOT`).


* **Map Lookup Checks:** The `bpf_map_lookup_elem()` helper returns a pointer that must be checked for validity (`!= NULL`) prior to access.



### 5. Advanced Monitoring Techniques

* **Quintuple Extraction:** Extracting Source IP, Source Port, Destination IP, Destination Port, and L4 Protocol (TCP/UDP) to form unique session keys in a hash map.


* **Bi-directional Session Management:**
1. *User-space merge:* Read both directions from the map and combine them.


2. *In-kernel atomic operations:* Store both directions in a single map entry, using atomic increments to prevent cross-core race conditions.


3. *Per-CPU Hash Maps:* Use `BPF_MAP_TYPE_PERCPU_HASH` to store independent instances per CPU core, removing the need for atomic operations; data is merged in user-space.




* **Purging Old Entries:** Track the last packet timestamp using `bpf_ktime_get_ns()` and remove sessions inactive for >60 seconds.



### Practical Exercises & Commands

**1. Environment Setup & Dependencies**

```bash
# Clone the repository
git clone https://github.com/FedeParola/network-monitoring-ebpf.git
cd network-monitoring-ebpf
git submodule update --init --recursive

# Install prerequisites
sudo apt update
sudo apt install -y clang libelf-dev zlib1g-dev gcc-multilib

```

**2. Building libbpf and bpftool**

```bash
# Build libbpf
cd ./libbpf/src
make
sudo make install
sudo ldconfig /usr/lib64

# Build bpftool
cd ../../bpftool/src
make
sudo make install

```

**3. Compiling the eBPF Application**

```bash
# Compile eBPF program
clang -g -O2 -target bpf -c network_monitor.bpf.c -o network_monitor.bpf.o

# Generate eBPF skeleton
bpftool gen skeleton ./network_monitor.bpf.o > network_monitor.skel.h

# Compile control program
gcc -g -Wall -O2 -o network_monitor network_monitor.c -lbpf

```

**4. Running the Monitor**

```bash
# Run the application
sudo ./network_monitor <ifname>

# View debug trace logs
sudo cat /sys/kernel/debug/tracing/trace_pipe

```

Warning: Modifying or dropping packets can sever connectivity. Test on the loopback interface (`lo`) before remote interfaces.

**5. Example Verifier Bound Check Code**

```c
void *data = (void *)(unsigned long) ctx->data;
void *data_end = (void *)(unsigned long) ctx->data_end;
struct ethhdr *eth = data;

if ((void *)(eth + 1) > data_end) {
    return TC_ACT_SHOT;
}
bpf_printk("Processed packet with l3proto 0x%04x\n", bpf_ntohs(eth->h_proto));

```
To be completely candid: while the cheat sheet captured all the core technical mechanics, commands, code blocks, and architectural rules, it did omit a few granular details from the text to maintain readability. If we are adhering strictly to your "Zero Omissions" rule, here are the exact additions needed to make it 100% exhaustive:

**1. Official Documentation URLs Provided in the Text**
The text explicitly lists several reference links for further reading:

* **libbpf:** `[https://libbpf.readthedocs.io/en/latest/libbpf_overview.html](https://libbpf.readthedocs.io/en/latest/libbpf_overview.html)`

* **bpftool:** `[https://github.com/libbpf/bpftool/tree/main/docs](https://github.com/libbpf/bpftool/tree/main/docs)`

* **eBPF Skeletons:** `[https://nakryiko.com/posts/libbpf-bootstrap/](https://nakryiko.com/posts/libbpf-bootstrap/)`

* **General eBPF:** `[https://docs.kernel.org/bpf/index.html](https://docs.kernel.org/bpf/index.html)`

* **eBPF Helpers:** `[https://man7.org/linux/man-pages/man7/bpf-helpers.7.html](https://man7.org/linux/man-pages/man7/bpf-helpers.7.html)`

* **eBPF Maps:** `[https://docs.kernel.org/bpf/maps.html](https://docs.kernel.org/bpf/maps.html)`


**2. The Target Output Table for the Enriched Program (Section 3)**
When extending the program to extract L3/L4 information, the text dictates that the user-space output must look specifically like this:

| Source IP | sport | Destination IP | dport | proto | pkt | bytes |
| --- | --- | --- | --- | --- | --- | --- |
| 172.16.38.105 | 19804 | 130.192.181.193 | 443 | TCP | 184 | 48705 |
| 130.192.181.193 | 443 | 172.16.38.105 | 19804 | TCP | 286 | 345860 |
| 172.16.38.105 | 35476 | 142.250.180.100 | 80 | TCP | 2 | 128 |
| 172.16.38.105 | 12098 | 130.192.225.102 | 22 | TCP | 12 | 2100 |
| 172.16.38.105 | 12098 | 130.192.225.102 | 22 | TCP | 14 | 3456 |
| 172.16.38.105 | * | 130.192.225.102 | * | ICMP | 2 | 168 |
| 130.192.225.102 | * | 172.16.38.105 | * | ICMP | 2 | 168 |
| 172.16.38.105 | 14222 | 8.8.8.8 | 53 | UDP | 4 | 1058 |
| 8.8.8.8 | 53 | 172.16.38.105 | 14222 | UDP | 4 | 3587 |

**3. Environment-Specific Warning**
The warning regarding packet modification specifically highlights **CrownLabs VMs**. If working remotely on a CrownLabs VM, modifying or dropping packets on the main interface (e.g., `enp1s0`) is especially dangerous and can result in completely losing connectivity to the host.

**4. Verifier Output Trace**
If you fail to include the `(data + sizeof(*eth) > data_end)` boundary check, the verifier spits out this exact error trace:

```text
0: (61) r7 = *(u32 *)(r1 +76)
1: (71) r3 = *(u8 *)(r7 +13)
invalid access to packet, off=13 size=1, R7(id=0,off=0,r=0)
R7 offset is outside of the packet
processed 2 insns (limit 1000000) max_states_per_insn 0 total_states 0 peak_states 0 mark_read 0

```

With these additions, every URL, specific table, and verbatim trace from the provided document is now accounted for.
---

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>eBPF Network Monitoring Quiz</title>
<style>
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
  .question-container { border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; background: #f9f9f9; }
  h3 { margin-top: 0; }
  .options { list-style-type: none; padding: 0; }
  .options li { margin-bottom: 10px; }
  button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
  button:hover { background: #0056b3; }
  .feedback { margin-top: 15px; padding: 15px; border-radius: 4px; display: none; }
  .correct { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
  .incorrect { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
</style>
</head>
<body>

<h1>eBPF Network Monitoring Master Quiz</h1>

<div id="quiz-container"></div>
<button onclick="submitQuiz()">Submit All Answers</button>

<script>
const quizData = [
  {
    q: "1. What is the primary purpose of libbpf?",
    options: ["To format hard drives", "To handle the lifecycle of eBPF programs", "To provide a GUI for network monitoring", "To replace the Linux kernel routing table"],
    ans: 1,
    exp: "libbpf is a C library used to handle the lifecycle of eBPF programs, embedding an eBPF loader to parse ELF objects and inject them into the kernel[cite: 4]."
  },
  {
    q: "2. Which system call does libbpf abstract for user-space interaction?",
    options: ["ptrace()", "bpf()", "socket()", "ioctl()"],
    ans: 1,
    exp: "libbpf provides an API that abstracts the use of the single eBPF-related system call provided by Linux, bpf()[cite: 4]."
  },
  {
    q: "3. What command lists all currently loaded eBPF programs on the system?",
    options: ["sudo bpf ls", "sudo bpftool map list", "sudo bpftool prog show", "sudo bpf-show"],
    ans: 2,
    exp: "The command 'sudo bpftool prog show' is used to list all the eBPF programs currently loaded on the system[cite: 4]."
  },
  {
    q: "4. What is an eBPF skeleton?",
    options: ["A malicious eBPF payload", "A C header file embedding the eBPF object as a variable", "A kernel panic dump", "A basic network topology map"],
    ans: 1,
    exp: "The skeleton is a C header file generated by bpftool that provides methods to interact with the eBPF program and embeds the object to allow shipping as a single executable[cite: 4]."
  },
  {
    q: "5. Why might a developer choose a lower-level hook point like eBPF/TC over eBPF/socket?",
    options: ["Higher processing throughput", "Easier access to data structures", "It requires zero programming", "It runs in user space"],
    ans: 0,
    exp: "The earlier a packet is processed (e.g., eBPF/TC), the higher the processing throughput that can be achieved, though it comes at an increased complexity burden[cite: 5]."
  },
  {
    q: "6. What does 'qdisc' stand for in the context of eBPF/TC?",
    options: ["Queue Discovery", "Queuing Discipline", "Quantum Disconnect", "Query Dispatch"],
    ans: 1,
    exp: "eBPF programs can be attached to the TC hook points leveraging the concept of queuing discipline (qdisc), which defines how packets are scheduled[cite: 5]."
  },
  {
    q: "7. Which qdisc type allows attaching eBPF filters in both ingress and egress directions?",
    options: ["fifo", "fq_codel", "clsact", "htb"],
    ans: 2,
    exp: "The laboratory leverages a qdisc of type clsact (Classify Action) that allows attaching eBPF classifiers both in ingress and egress[cite: 5]."
  },
  {
    q: "8. What is the parameter type passed into the eBPF program function attached to a TC hook?",
    options: ["struct __sk_buff", "struct packet_data", "struct net_device", "struct tc_info"],
    ans: 0,
    exp: "The function receives a single parameter in input of type struct __sk_buff, containing packet metadata and buffer pointers[cite: 6]."
  },
  {
    q: "9. Which component periodically dumps statistics from the eBPF map?",
    options: ["The eBPF Verifier", "bpftool daemon", "The user-space control program", "The qdisc clsact"],
    ans: 2,
    exp: "The user-space control program (network_monitor.c) is in charge of creating the hook, loading the program, and periodically dumping statistics from the map[cite: 6]."
  },
  {
    q: "10. What format is the compiled eBPF object file stored in before loading?",
    options: ["JSON", "ELF (Executable and Linkable Format)", "PE32+", "Raw Binary"],
    ans: 1,
    exp: "The libbpf library parses an eBPF object in ELF format (Executable and Linkable Format) before injecting it into the kernel[cite: 4]."
  },
  {
    q: "11. Which compiler toolchain is required to build the eBPF program?",
    options: ["GCC and Make", "Clang and LLVM", "Rustc", "MSVC"],
    ans: 1,
    exp: "Clang and LLVM are used to build the eBPF program, while libelf and libz are needed to parse the ELF object[cite: 6]."
  },
  {
    q: "12. In the build process, what is the exact flag used to specify the eBPF target in Clang?",
    options: ["-m ebpf", "-arch=bpf", "-target bpf", "--compile-bpf"],
    ans: 2,
    exp: "The build command uses the flag '-target bpf' (e.g., clang -g -O2 -target bpf -c ...)[cite: 7]."
  },
  {
    q: "13. What happens if the eBPF verifier detects a missing memory boundary check?",
    options: ["It silently pads the memory", "It rejects the program with an error", "It forces the packet to be dropped at runtime", "It moves the program to user-space"],
    ans: 1,
    exp: "Removing boundary checks results in an error from the verifier (e.g., 'invalid access to packet... offset is outside of the packet') and prevents injection[cite: 8]."
  },
  {
    q: "14. What return value should an eBPF/TC program use to discard a packet?",
    options: ["TC_ACT_SHOT", "DROP_PACKET", "0", "-1"],
    ans: 0,
    exp: "If the buffer is not big enough to contain the headers, the code discards the packet by returning TC_ACT_SHOT[cite: 8]."
  },
  {
    q: "15. What safety check must be performed on the pointer returned by bpf_map_lookup_elem()?",
    options: ["Check if it is > 0", "Check if it is != NULL", "Check if it matches data_end", "No check is required"],
    ans: 1,
    exp: "The map lookup helper returns a pointer to the entry, and a check for the validity of the pointer (!= NULL) is needed before accessing its content[cite: 8]."
  },
  {
    q: "16. When extending the program to L3/L4, which quintuple is suggested as the map key?",
    options: ["MAC addresses, IP addresses, and VLAN tag", "Source IP, Source Port, Dest IP, Dest Port, L4 Protocol", "Timestamp, Source IP, Dest IP, Packet Size, L3 Proto", "Source IP and Dest IP only"],
    ans: 1,
    exp: "The key can be a struct containing the quintuple: source IP address, source port, destination IP address, destination port, and L4 protocol[cite: 8]."
  },
  {
    q: "17. If bidirectional session data is merged inside the kernel using a standard hash map, what must be used?",
    options: ["Spinlocks", "Atomic operations", "Semaphores", "Mutexes"],
    ans: 1,
    exp: "If storing both directions in a single hash map entry, the developer must use atomic operations to increase counters since packets could be processed concurrently on different cores[cite: 9]."
  },
  {
    q: "18. Which map type eliminates the need for atomic operations when merging session data in the kernel?",
    options: ["BPF_MAP_TYPE_ARRAY", "BPF_MAP_TYPE_PERCPU_HASH", "BPF_MAP_TYPE_LRU_HASH", "BPF_MAP_TYPE_PROG_ARRAY"],
    ans: 1,
    exp: "BPF_MAP_TYPE_PERCPU_HASH removes the need for atomic operations because every CPU core has its own instance of the value, which are later merged in user space[cite: 9]."
  },
  {
    q: "19. Which eBPF helper function is recommended for tracking the last time a packet was detected?",
    options: ["bpf_get_current_pid_tgid()", "bpf_time_now()", "bpf_ktime_get_ns()", "bpf_timer_init()"],
    ans: 2,
    exp: "Tracking the last time a packet was detected to purge old entries can be achieved using the bpf_ktime_get_ns() helper[cite: 9]."
  },
  {
    q: "20. Why should you test the monitor on the loopback interface (`lo`) before remote interfaces like `enp1s0`?",
    options: ["Because eBPF only works on local traffic", "Because loopback traffic bypasses the verifier", "Because dropping packets on a remote interface can cause total loss of connectivity", "Because `lo` requires fewer privileges"],
    ans: 2,
    exp: "Modifying or dropping packets can result in communication problems. Working on a remote environment means connectivity to the host can be completely lost, so it's suggested to test on the loopback interface first[cite: 7]."
  }
];

const container = document.getElementById('quiz-container');

quizData.forEach((q, index) => {
  const qDiv = document.createElement('div');
  qDiv.className = 'question-container';
  qDiv.innerHTML = `<h3>${q.q}</h3>`;
  
  const ul = document.createElement('ul');
  ul.className = 'options';
  
  q.options.forEach((opt, optIndex) => {
    ul.innerHTML += `
      <li>
        <label>
          <input type="radio" name="q${index}" value="${optIndex}">
          ${opt}
        </label>
      </li>
    `;
  });
  
  const feedback = document.createElement('div');
  feedback.id = `feedback-${index}`;
  feedback.className = 'feedback';
  
  qDiv.appendChild(ul);
  qDiv.appendChild(feedback);
  container.appendChild(qDiv);
});

function submitQuiz() {
  quizData.forEach((q, index) => {
    const selected = document.querySelector(`input[name="q${index}"]:checked`);
    const feedback = document.getElementById(`feedback-${index}`);
    feedback.style.display = 'block';
    
    if (selected && parseInt(selected.value) === q.ans) {
      feedback.className = 'feedback correct';
      feedback.innerHTML = `<strong>Correct!</strong> <br> ${q.exp}`;
    } else {
      feedback.className = 'feedback incorrect';
      feedback.innerHTML = `<strong>Incorrect.</strong> <br> ${q.exp}`;
    }
  });
}
</script>
</body>
</html>

```