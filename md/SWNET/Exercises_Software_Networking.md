## Master Cheat Sheet: Software Networking

### 1. Introduction to OpenFlow

* **Separation of Planes:** In classical network devices (e.g., routers, switches), both the data plane (packet forwarding) and the control plane (routing decisions) are implemented on the device itself. An OpenFlow Switch separates these two functions.


* **Data Plane:** Resides on the switch.


* **Control Plane:** Is moved to a separate device called an OpenFlow controller.


* **Protocol:** The switch and the controller interact via the OpenFlow protocol.


* **Flow Table Abstraction:** The OpenFlow switch is abstracted using a flow table. Each entry contains a set of packet fields to match and an action (e.g., send-to-port, modify-field, drop).


* **Proactive Mode:** The controller populates the OpenFlow switch's flow table *a priori* with all required rules. The switch processes incoming packets using these entries without sending any traffic to the controller.


* **Reactive Mode:** The switch possesses a rule (usually the lowest priority) that sends all unmatched packets to the controller. The controller decides how to handle the packet and inserts a new flow entry in the switch for subsequent packets of that flow. This allows granular, state-based decisions but introduces latency, whereas proactive mode is simpler and faster.



### 2. Practical Exercises

#### Exercise 1: Service Chain with OpenFlow

* **Scenario:** Two users (Green and Red) on Wi-Fi (port 1) must be routed through their respective Firewalls, a shared NAT, and out to the Internet via an OpenFlow switch.


* **Solution 1 (IP Traffic Only):**
* Outgoing traffic rules match `IP Src` (e.g., `IP_GREEN` or `IP_RED`) and forward to the respective firewall ports.


* Incoming traffic rules match `IP Dst` and route through the chain backwards.




* **Solution 2 (All Traffic, including ARP):**
* Outgoing traffic is selected using the `MAC Src` address of the host, capturing all generated traffic (unicast/multicast/broadcast).


* Incoming unicast traffic is routed using the `MAC Dst` address (Green/Red host).


* Incoming multicast/broadcast traffic duplicates the frame to both chains by checking the Individual/Group bit in the Ethernet frame. A value of '1' in the last bit of the first byte indicates a group. The bitwise mask used is `0x010000000000`.





```text
Rules for incoming multicast/broadcast traffic:
IN Port | MAC Src | MAC Dst                                           | Action(s)
6       | *       | (mac.dst bitwand 0x010000000000) == 0x010000000000| out-port: 5; out-port: 3

```

#### Exercise 2: NAT Service with OpenFlow

* **Scenario:** Implementing NAT using an external SDN controller (avoiding NFV technology).


* **Reactive Mode Processing Algorithm:**
1. TCP/UDP packets with no matching entries are sent to the controller.


2. The controller forwards the packet to the NAT service.


3. The NAT service injects a rule replacing `IP Src` with the public NAT IP and `Port Src` with an unused L4 port.


4. The reverse rule (matching returning Internet traffic) is injected first to ensure the return traffic finds a match.


5. The original packet is translated and sent out port 2.


6. The OpenFlow switch handles subsequent packets automatically.




* **State Management:** The NAT service keeps an association table between internal and external L4 ports to track usage.


* **Timeout & Purging:** Rules are injected with a "timeout" mechanism (e.g., 10 minutes of inactivity). The switch informs the NAT service when a rule is purged to delete the internal NAT table entry and free the L4 port.


* **Generic Traffic (ARP):** The algorithm does not work for ARP because an internal host must discover the MAC address of the default gateway hidden in the Internet cloud. Rules must be added to translate ARP `ipsrc` and `ipdst` fields, or ARP can be handled dynamically by the NAT service.



```text
Example NAT OpenFlow Rules (TCP session):
IN Port | IP Src   | IP Dst   | Port Src | Port Dst | Action(s)
1       | 10.0.0.1 | *        | 2000     | *        | set-field ip.src: 20.2.2.1; set-field tcp.sport: 3000; out-port: 2
2       | *        | 20.2.2.1 | *        | 3000     | set-field ip.dst: 10.0.0.1; set-field tcp.dport: 2000; out-port: 1

```

#### Exercise 3: Load Balancer with OpenFlow

* **Scenario:** Load balancing traffic from the Internet (port 1) to a server farm of 4 web servers (ports 2-5).


* **Proactive Mode Implementation:**
* Traffic is split by assigning different IP address ranges to different servers.


* This is achieved by applying a bitwise AND on the last two bits of the IP source address (e.g., `ip.src bitwand 0.0.0.3`).


* **Limitations:**
1. **Un-balanced traffic:** IP addresses are not uniformly distributed; NAT can hide many clients behind one public IP. Hashing over the 5-tuple is preferred but impossible in proactive OpenFlow matching.


2. **Dynamic scaling:** It cannot address the dynamic insertion/removal of servers without dropping established sessions.


3. **Server load blind:** Incoming traffic is statically distributed regardless of actual CPU load.






* **Reactive Mode Implementation:**
* All web traffic (TCP ports 80/443) is forced to the controller.


* The LB logic calculates a heuristic (e.g., 5-tuple hash) to pick a server, and writes a session-specific flow rule replacing `IP Dst` with the specific server's IP.


* The switch can be configured to recognize TCP FIN/RST flags to explicitly delete flowrules, though state tracking is required since FIN only closes half the session.





#### Exercise 4: BPF Virtual Machine

* **Purpose:** The Berkeley Packet Filter (BPF) provides an execution environment for packet filtering.


* **Example BPF Program:**
```text
(000) ldh      [12]
(001) jeq      #0x800           jt 2    jf 3
(002) ret      #96
(003) ret      #0

```


* This program checks if the Ethernet ethertype field at offset 12 is `0x800` (IPv4). If true, it returns 96 (true); if false, it returns 0 (false).




* **Virtual CPU Architecture:**
* Includes specific **Packet Memory** separated from main RAM.


* Requires a specialized **Instruction Set** differentiating load/store operations (e.g., `ld` for packet memory, `ldx` for main memory).


* Contains an **ALU** optimized for network parsing (e.g., calculating IP header size).


* Components include: Control Unit, Registers (General Purpose, Accumulator, Program Counter), Main memory (RAM), Packet memory, and ALU.





#### Exercise 5: Analyzing libpcap Filters and BPF Code

* **Unidirectional Filter (`tcpdump -d`):**
* Filter: `src host 10.0.0.1 and dst host 20.0.0.2 and tcp src port 1080 and tcp dst port 80`.


* **BPF Execution Flow:**
1. `ldh [12]`: Load half-word (ethertype).


2. `jeq #0x86dd`: Skip if IPv6.


3. `jeq #0x800`: Continue if IPv4.


4. `ldb [23]`: Load protocol field.


5. `jeq #0x6`: Check if protocol is TCP.


6. `ldh [20]` & `jset #0x1fff`: Check fragment offset. If non-zero, it is not the first fragment (TCP port unavailable), so drop.


7. **IP Header Length Calculation:** `ldxb 4*([14]&0xf)`. The version/IHL byte is at offset 14. Masking with `0xf` isolates the header length in words, which is multiplied by 4 to get bytes, and loaded into register X. This is a highly specialized networking instruction.


8. Check ports relative to register X: `ldh [x + 16]` for destination port (offset by 14 bytes Ethernet + IP Header `x` + 2 bytes TCP offset), and `ldh [x + 14]` for source port.


9. Check IP addresses: `ld [26]` (Source IP `0xa000001`), `ld [30]` (Destination IP `0x14000002`).






* **Bidirectional Filter:**
* Requires explicit boolean OR grouping: `(src host 10.0.0.1 and dst host 20.0.0.2 and tcp src port 1080 and tcp dst port 80) or (dst host 10.0.0.1 and src host 20.0.0.2 and tcp dst port 1080 and tcp src port 80)`.


* Using `host 10.0.0.1 and host 20.0.0.2 and tcp port 1080 and tcp port 80` is incorrect because it selects traffic not belonging to the specific directional socket pairing.





#### Exercise 6: Memory Access Performance (Random vs Sequential)

* **Core Concept:** Sequential memory access (e.g., iterating a "Walking Table") is fast because cache prefetching algorithms preemptively copy required data into the CPU cache. Random memory access (using the Walking Table index to access random cells in a "Data Table") nullifies cache prefetching, creating a major performance cost in packet processing programs.


* **Cache Coherency:** When multiple threads update variables stored in the same cache line, the CPU cache coherency mechanism must re-align the entire cache line across all CPU caches, causing a noticeable performance drop.


* **Locking:** Applying a shared mutex lock (`ENABLE_LOCKING`) across all threads for a single shared variable demonstrates the high overhead of synchronization primitives.



```c
// Code Snippet: memtest.c
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdint.h>

// Compile with: gcc -pthread -o memtest memtest.c

//#define ENABLE_LOCKING
//#define ENABLE_CACHE_COHERENCY
//#define _DEBUG

#define MIN_READ 10000000
#define CACHE_LINE 64

typedef struct thread_table {
    pthread_t thread;
    uint thread_id;
    uint *data_table;
    uint *walking_table;
#ifndef ENABLE_LOCKING
    uint final_sum;
#endif
#ifndef ENABLE_CACHE_COHERENCY
    uint8_t pad [CACHE_LINE];
#endif
} thread_table_t;

#ifdef ENABLE_LOCKING
uint final_sum = 0;
#endif

thread_table_t *thread_table;
uint num_data, num_walk, num_test, num_thread;
uint test_instance;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

uint randnum_gen (uint min, uint max) {
    uint lowerLimit = min;
    uint upperLimit = max;
    uint r = lowerLimit + rand() % (upperLimit - lowerLimit);
    return r;
}

int create_threadtable (uint num) {
    thread_table = (thread_table_t *) malloc(sizeof(thread_table_t) * num);
    if (thread_table != NULL) return 1;
    else return 0;
}

int create_datatable (uint thread_id, uint num) {
    thread_table[thread_id].data_table = (uint *) malloc(sizeof(uint) * num);
    if (thread_table[thread_id].data_table != NULL) {
        for (uint i = 0; i < num; i++) {
            thread_table[thread_id].data_table[i] = 2;
        }
        return 1;
    } else return 0;
}

int create_walkingtable (uint thread_id, uint num, uint num_data) {
    thread_table[thread_id].walking_table = (uint *) malloc(sizeof(uint) * num);
    if (thread_table[thread_id].walking_table != NULL) {
        for (uint i = 0; i < num; i++) {
            thread_table[thread_id].walking_table[i] = randnum_gen(0, num_data);
        }
        return 1;
    } else return 0;
}

void *random_walk_thread (void *argv) {
    uint temp;
    double final_time = 0;
    uint number_repeat;
    thread_table_t *thread_data = (thread_table_t *) argv;
    number_repeat = MIN_READ / num_walk;
    if (MIN_READ % num_walk) number_repeat++;
    
    clock_t begin = clock();
    for (uint j = 0; j < number_repeat; j++) {
        for (uint i = 0; i < num_walk; i++) {
            temp = thread_data->walking_table[i];
#ifdef ENABLE_LOCKING
            pthread_mutex_lock(&mutex);
            final_sum += thread_data->data_table[temp];
            pthread_mutex_unlock(&mutex);
#else
            thread_data->final_sum += thread_data->data_table[temp];
#endif
        }
    }
    clock_t end = clock();
    final_time = (double) (end - begin) / CLOCKS_PER_SEC;
    printf ("Cost per memory read, random walk (thread #%d, test #%d, #mem_read %d): %f ns\n",
            thread_data->thread_id, test_instance, num_walk * number_repeat,
            final_time * 1000000000 / (num_walk * number_repeat));
    return NULL;
}

void linear_walk (uint test_instance) {
    double final_time = 0;
    uint final_sum = 0;
    uint number_repeat = MIN_READ / num_data;
    if (MIN_READ % num_data) number_repeat++;
    
    clock_t begin = clock();
    for (uint j = 0; j < number_repeat; j++) {
        for (uint i = 0; i < num_data; i++) {
            final_sum += thread_table[0].data_table[i];
        }
    }
    clock_t end = clock();
    final_time = (double) (end - begin) / CLOCKS_PER_SEC;
    printf("Cost per memory read, linear walk (test #%d, #mem_read %d): %f ns\n",
            test_instance, num_data * number_repeat,
            final_time * 1000000000 / (num_data * number_repeat));
}

void print_usage () {
    char message[] = "Usage example: memory <numdata> <numwalk> <numthread> <numtest>\n";
    printf("%s", message);
}

int main(int argc, char** argv) {
    // Initialization omitted for brevity; allocates memory, checks cache coherency, 
    // runs linear_walk() as baseline, and dispatches random_walk_thread().
    return 0;
}

```

---

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Software Networking Quiz</title>
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; max-width: 800px; margin: auto; padding: 20px; line-height: 1.6; }
    h1 { text-align: center; color: #2c3e50; }
    .question-card { background: #fff; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .question { font-weight: bold; margin-bottom: 15px; font-size: 1.1em; }
    .options { list-style-type: none; padding: 0; }
    .options li { margin-bottom: 10px; }
    label { cursor: pointer; padding: 8px; display: block; border: 1px solid #ddd; border-radius: 4px; transition: background 0.2s; }
    label:hover { background: #e9ecef; }
    input[type="radio"] { margin-right: 10px; }
    .submit-btn { display: block; width: 100%; background: #3498db; color: #fff; border: none; padding: 12px; font-size: 1.1em; border-radius: 4px; cursor: pointer; margin-top: 10px; }
    .submit-btn:hover { background: #2980b9; }
    .feedback { margin-top: 15px; padding: 15px; display: none; border-radius: 4px; }
    .correct { background: #d4edda; border-left: 5px solid #28a745; color: #155724; }
    .incorrect { background: #f8d7da; border-left: 5px solid #dc3545; color: #721c24; }
    .motivation { margin-top: 10px; font-size: 0.95em; color: #555; }
</style>
</head>
<body>

<h1>Software Networking Mastery Quiz</h1>
<div id="quiz-container"></div>

<script>
    const quizData = [
        {
            question: "1. In OpenFlow, what is the primary difference between proactive and reactive mode?",
            options: [
                "Proactive mode requires the controller to calculate packet hashes, while reactive mode does not.",
                "Proactive mode populates the flow table a priori, while reactive mode sends unmatched packets to the controller.",
                "Reactive mode bypasses the SDN controller entirely to reduce latency.",
                "Proactive mode only operates on IP traffic, while reactive mode operates on MAC traffic."
            ],
            correct: 1,
            motivation: "In proactive mode, the controller populates the flow table a priori. In reactive mode, the switch has a lowest-priority rule that sends all unmatched packets to the controller for dynamic rule generation[cite: 4]."
        },
        {
            question: "2. When handling multicast and broadcast traffic for incoming frames in OpenFlow, how can you identify such traffic using the MAC address?",
            options: [
                "By matching the entire MAC address to FF:FF:FF:FF:FF:FF.",
                "By analyzing the IP destination address instead.",
                "By checking the Individual/Group bit, which is the last bit of the first byte.",
                "By sending the frame to the controller in reactive mode."
            ],
            correct: 2,
            motivation: "For multicast/broadcast traffic, you can check the proper bit in the MAC destination address (the Individual/Group bit, the last bit of the first byte) using a bitwise mask like 0x010000000000[cite: 6]."
        },
        {
            question: "3. Which traffic type requires special handling or secondary strategies because an OpenFlow NAT service using only TCP/UDP translation algorithms cannot process it directly?",
            options: [
                "ICMP Echo Requests",
                "ARP Traffic",
                "IPv6 Traffic",
                "HTTP Traffic"
            ],
            correct: 1,
            motivation: "The basic NAT algorithm discussed only translates TCP/UDP. It does not work for ARP traffic because a host needs to discover its default gateway's MAC address dynamically, requiring either proactive translation rules for ARP or handling by the SDN controller[cite: 8, 9]."
        },
        {
            question: "4. When implementing an OpenFlow Load Balancer in proactive mode, what is a common technique to distribute traffic across a 4-server web farm?",
            options: [
                "Hashing the 5-tuple payload.",
                "Calculating CPU load metrics across the farm.",
                "Applying a bitwise AND on the last two bits of the IP source address.",
                "Using the TCP sequence number."
            ],
            correct: 2,
            motivation: "In proactive mode, traffic can be split by applying a bitwise AND on the last two bits of the IP source address (e.g., ip.src bitwand 0.0.0.3) to create four static ranges[cite: 10]."
        },
        {
            question: "5. What is a major limitation of implementing an OpenFlow Load Balancer strictly in proactive mode?",
            options: [
                "It requires NFV technology.",
                "It cannot perform bitwise operations.",
                "It leads to un-balanced load distribution because IP addresses are not uniformly distributed.",
                "It drops all incoming ICMP traffic."
            ],
            correct: 2,
            motivation: "Splitting traffic based strictly on IP source addresses leads to un-balanced behavior because IP addresses are not uniformly distributed and NAT can hide a huge amount of clients behind a single public IP[cite: 11]."
        },
        {
            question: "6. To resolve the limitations of a proactive load balancer, an OpenFlow switch operating in reactive mode routes web traffic where first?",
            options: [
                "To the default gateway.",
                "To the OpenFlow controller.",
                "Directly to the server with the lowest CPU load.",
                "To the NAT engine."
            ],
            correct: 1,
            motivation: "In reactive mode, the switch forces all incoming web traffic arriving from the Internet to the SDN controller. The controller's LB logic then chooses a server using heuristics like a 5-tuple hash and inserts a flow rule[cite: 12]."
        },
        {
            question: "7. When a TCP session expires in a reactive load balancer setup, how might the OpenFlow switch clean up the associated flow rules?",
            options: [
                "The switch automatically deletes rules after 1 minute regardless of activity.",
                "The switch deletes the rule as soon as the first ACK is received.",
                "The switch can be configured to recognize TCP FIN/RST flags or rely on an inactivity timeout.",
                "The server farm broadcasts a rule deletion request."
            ],
            correct: 2,
            motivation: "Flowrules can be removed via an inactivity timeout or by configuring the OpenFlow switch to explicitly recognize packets with TCP FIN/RST flags enabled[cite: 12]."
        },
        {
            question: "8. In the BPF virtual machine architecture, why is the 'Packet memory' separated from 'Main memory'?",
            options: [
                "To allow direct internet routing.",
                "To store flow table actions.",
                "Because BPF is a general-purpose processor.",
                "It is an ad-hoc execution environment crafted for network processing, requiring specialized load/store instructions."
            ],
            correct: 3,
            motivation: "The BPF virtual CPU is an ad-hoc execution environment specially crafted for network processing. It includes specific memory for packets separated from main RAM, necessitating dedicated load/store instructions[cite: 13]."
        },
        {
            question: "9. In BPF assembly, what does the instruction `ldh [12]` typically accomplish when examining raw Ethernet frames?",
            options: [
                "It loads the TCP destination port.",
                "It calculates the IP header length.",
                "It loads a half-word (2 bytes) representing the ethertype field.",
                "It loads the IP source address."
            ],
            correct: 2,
            motivation: "The instruction `ldh [12]` loads a half-word (2 bytes) from the packet at offset 12, which corresponds to the Ethernet ethertype field (e.g., to check if it's 0x800 for IPv4)[cite: 13, 16]."
        },
        {
            question: "10. In the libpcap BPF code `ldxb 4*([14]&0xf)`, what is the purpose of the bitwise mask `0xf`?",
            options: [
                "It masks the fragment offset.",
                "It checks the TCP flags.",
                "It masks the 4 least-significant bits to isolate the IP header length field.",
                "It extracts the ethertype value."
            ],
            correct: 2,
            motivation: "The byte at offset 14 contains both the version and IP header length. The mask `0xf` selects the header length, which is then multiplied by 4 to convert it from words to bytes[cite: 16]."
        },
        {
            question: "11. Why is calculating the size of the IPv4 header an explicit hardware-level capability in the BPF ALU?",
            options: [
                "Because BPF requires IPv6 alignment.",
                "Because finding the IP header size is very uncommon in networking.",
                "Because it is required to locate the beginning of the TCP/UDP payload in almost all packets.",
                "Because OpenFlow switches require hardware multipliers."
            ],
            correct: 2,
            motivation: "This operation is very common in networking because the size of the IP header must be checked to locate the TCP/UDP payload. This justifies a specific instruction in the BPF assembly for higher execution speed[cite: 17]."
        },
        {
            question: "12. When tracking a bidirectional TCP session in libpcap, what logic must be applied?",
            options: [
                "Combining the properties using an explicit boolean OR logic to capture both directions.",
                "Omitting the destination port.",
                "Using the string `host X and host Y and tcp port A and tcp port B`.",
                "Enabling BPF cache coherency."
            ],
            correct: 0,
            motivation: "A bidirectional filter must explicitly define both directions and group them with an OR. Using `host X and host Y and tcp port A and tcp port B` is incorrect because it inadvertently selects traffic outside the desired session[cite: 17, 18]."
        },
        {
            question: "13. In the C program measuring memory access, what algorithm feature makes sequential array reading highly performant?",
            options: [
                "Mutex locking.",
                "CPU cache prefetching algorithms preemptively copying required data.",
                "Hardware multithreading.",
                "The Walking Table."
            ],
            correct: 1,
            motivation: "Reading data in sequence is low-cost because cache prefetching algorithms are highly effective at preemptively copying the required data into the CPU cache[cite: 19, 20]."
        },
        {
            question: "14. Why is random memory access detrimental to packet processing programs?",
            options: [
                "It causes BPF to halt.",
                "It triggers network drops in OpenFlow.",
                "It defeats CPU cache prefetching algorithms.",
                "It requires a lock on every read."
            ],
            correct: 2,
            motivation: "Reading from random memory locations renders cache prefetching algorithms ineffective, resulting in cache misses and significant performance costs during packet processing[cite: 20]."
        },
        {
            question: "15. What performance issue arises when multiple threads update separate variables that happen to be stored in the same cache line?",
            options: [
                "Mutex starvation.",
                "Memory leaks.",
                "CPU cache coherency protocol overhead.",
                "Kernel panics."
            ],
            correct: 2,
            motivation: "If private variables for different threads are close in memory (in the same cache line), the CPU cache coherency mechanism must re-align the entire cache line across CPU caches, causing a noticeable performance drop[cite: 20]."
        },
        {
            question: "16. In the BPF bytecode generated for TCP parsing, what does the instruction `jeq #0x6` at offset 23 verify?",
            options: [
                "The payload is ICMP.",
                "The IP fragment offset is zero.",
                "The protocol field in the IPv4 header is TCP.",
                "The MAC address is valid."
            ],
            correct: 2,
            motivation: "The byte at offset 23 is the IPv4 protocol field. The hex value `0x6` corresponds to TCP[cite: 16]."
        },
        {
            question: "17. What bitwise mask is used in BPF to check if a packet is an IP fragment (excluding the first fragment)?",
            options: [
                "0x800",
                "0xf",
                "0x86dd",
                "0x1fff"
            ],
            correct: 3,
            motivation: "The filter masks the flags and fragment offset with `0x1FFF` to preserve the 13-bit fragment offset. If non-zero, it drops the packet because the TCP port is only available in the first fragment[cite: 16]."
        },
        {
            question: "18. In Exercise 2 (NAT), how are returned packets from the Internet translated back to the internal user?",
            options: [
                "The controller injects a reverse rule matching the public IP and external L4 port.",
                "The client sends an ARP request to the controller.",
                "The switch performs stateful inspection automatically without rules.",
                "The internet gateway applies the reverse translation."
            ],
            correct: 0,
            motivation: "A reverse rule matching traffic directed to the public IP address and the external L4 port translates the packets back to the internal host IP and original L4 port. This is injected before the outgoing rule[cite: 8]."
        },
        {
            question: "19. In a C program using pthreads, what is the impact of enabling a shared mutex (`PTHREAD_MUTEX_INITIALIZER`) around a sum variable across multiple threads?",
            options: [
                "It enables cache coherency padding.",
                "It demonstrates the high execution cost of synchronizing variable access.",
                "It speeds up execution by preventing cache misses.",
                "It randomizes memory walking."
            ],
            correct: 1,
            motivation: "Sharing a single variable across multiple threads protected by a mutex lock is used to measure and demonstrate the significant overhead cost of synchronization primitives[cite: 20, 24]."
        },
        {
            question: "20. When parsing an IPv4 frame with BPF, how is the TCP destination port located dynamically?",
            options: [
                "By always loading byte offset 36.",
                "By sending the frame to the control plane.",
                "By adding 16 to the calculated IP header size (stored in register X).",
                "By masking the ethertype field."
            ],
            correct: 2,
            motivation: "The TCP destination port is located at an offset equal to the IP header size (calculated into register X) plus 16 (14 bytes for Ethernet + 2 bytes TCP offset to dport)[cite: 16]."
        }
    ];

    const container = document.getElementById('quiz-container');

    quizData.forEach((q, index) => {
        const questionHtml = `
            <div class="question-card" id="q${index}">
                <div class="question">${q.question}</div>
                <ul class="options">
                    ${q.options.map((opt, i) => `
                        <li>
                            <label>
                                <input type="radio" name="question${index}" value="${i}">
                                ${opt}
                            </label>
                        </li>
                    `).join('')}
                </ul>
                <button class="submit-btn" onclick="checkAnswer(${index})">Submit Answer</button>
                <div class="feedback" id="feedback${index}"></div>
            </div>
        `;
        container.innerHTML += questionHtml;
    });

    function checkAnswer(index) {
        const selected = document.querySelector(`input[name="question${index}"]:checked`);
        const feedbackDiv = document.getElementById(`feedback${index}`);
        
        if (!selected) {
            alert("Please select an answer.");
            return;
        }

        const answer = parseInt(selected.value);
        const correct = quizData[index].correct;
        const motivation = quizData[index].motivation;

        if (answer === correct) {
            feedbackDiv.className = "feedback correct";
            feedbackDiv.innerHTML = `<strong>Correct!</strong><div class="motivation">Explanation: ${motivation}</div>`;
        } else {
            feedbackDiv.className = "feedback incorrect";
            feedbackDiv.innerHTML = `<strong>Incorrect.</strong> The correct answer was option ${correct + 1}.<div class="motivation">Explanation: ${motivation}</div>`;
        }
        
        feedbackDiv.style.display = "block";
        const inputs = document.querySelectorAll(`input[name="question${index}"]`);
        inputs.forEach(input => input.disabled = true);
        document.querySelector(`#q${index} .submit-btn`).disabled = true;
        document.querySelector(`#q${index} .submit-btn`).style.opacity = "0.5";
    }
</script>
</body>
</html>

```