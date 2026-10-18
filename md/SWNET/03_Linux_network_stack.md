## The Linux Network Stack: Master Cheat Sheet

### Part I: OS Kernel and Interrupts

* **Kernel Reactivity**: The kernel is a strictly reactive component; it does not constantly run in the background. It executes by stealing time from userspace applications or CPU idle processes.


* **Concurrency**: Any CPU core can host kernel processing. Kernel routines often run concurrently across multiple cores, necessitating synchronization primitives like Spinlocks, Mutexes, and RCU.


* **Interrupt Types**:
* **Exceptions**: Generated internally by the CPU (e.g., Divide by zero, page fault).


* **Hardware Interrupts**: Caused by external devices (e.g., Device I/O, Timer ticks).


* **Software Interrupts**: Triggered by predefined instructions (e.g., x86 INT instruction, system calls).




* **Interrupt Table**: Interrupts are indexed 0-255.


* `0-31`: Processor interrupts (e.g., 14 for page faults).


* `32-255`: Software configured.


* `32-47`: Device interrupts (IRQs), generally software configurable via APIC.


* `128`: Linux System Call.




* **Top Half vs. Bottom Half Processing**:
* **Top Half Handler (hardirq)**: Executed immediately upon interrupt reception. Hardware interrupts are disabled to prioritize fast execution and prevent data loss. Registered using `request_irq()`.


* **Bottom Half Handler (softirq)**: Handles tasks that require more time and can be deferred. Interrupts are enabled, but preemption is disabled.




* **Networking Softirqs**: Networking relies heavily on `NET_TX_SOFTIRQ` and `NET_RX_SOFTIRQ`, registered during system initialization via `open_softirq()` in `net/core/dev.c`.


* **ksoftirqd**: If softirqs are still pending after `MAX_SOFTIRQ_RESTART` scans or `MAX_SOFTIRQ_TIME`, a low-priority per-CPU kernel thread (`ksoftirqd/n`) is scheduled to handle the remaining tasks.


* **NAPI (New API)**: Uses a mixed approach that adaptively switches between interrupt-driven execution and polling based on the actual workload to mitigate livelock under heavy packet loads.



### Part II: The Socket Buffer (`sk_buff`)

* **Purpose**: The socket buffer provides an efficient, uniform way for kernel components to access packet data and metadata across varying NIC architectures and protocols.


* **Buffer Architecture**:
* `*head` and `*end`: Point to the absolute limits of the allocated buffer memory.


* `*data` and `*tail`: Delimit the actual packet data within the buffer. This allows header pushing/popping without memory reallocation.





```c
// Key fields from struct sk_buff[cite: 18]
struct sk_buff {
    // ...
    struct net_device *dev; // The input or output device
    ktime_t tstamp;         // The timestamp of reception
    __be16 protocol;        // The L3 protocol of the packet
    u16 transport_header;   // Pointers to the various headers in the buffer
    u16 network_header;
    u16 mac_header;
    // ...
}

```

### Part III: Packet Reception (Input Path)

1. **DMA & Interrupt**: The NIC transfers packet data to pre-allocated buffers via DMA and signals the CPU with a hardware interrupt.


2. **Driver IRQ Handler**: The Top Half handler disables further hardware interrupts for the device and schedules a `NET_RX_SOFTIRQ` by appending the device's `napi_struct` to the local CPU's `softnet_data->poll_list` via `__napi_schedule()`.


3. **Softirq Execution**: `net_rx_action()` executes the driver-specific `poll` method for every `napi_struct` in the list. Fair handling is guaranteed by a per-device budget limit (stored in `napi_struct.weight`).


4. **Driver Poll Method**:
* Identifies the descriptor and executes XDP (eBPF) via `bpf_prog_run_xdp()`. Packets can be Dropped, Tx'd, Redirected, or Passed.


* Allocates a new `sk_buff` and copies NIC metadata.


* Calls `eth_type_trans()` to determine L2 features (destination type, L3 protocol).


* Passes the packet up via `__netif_receive_skb_core()` (sometimes grouping packets via GRO - Generic Receive Offload).




5. **`receive_skb` Function**:
* Applies RPS (Receive Packet Steering) to distribute load across CPUs.


* Delivers packet to Network Taps (e.g., for `tcpdump`) via `deliver_skb()`.


* Applies Traffic Control (TC) ingress classification.


* Checks for Linux Bridge routing via `br_handle_frame()` (returns `RX_HANDLER_PASS` or `RX_HANDLER_CONSUMED`).


* Delivers to the L3 handler (e.g., IPv4 `ip_rcv()`).





### Part IV: Packet Transmission (Output Path)

* **Traffic Control (TC)**: Manages QoS via packet scheduling.
* **Classless qdiscs**: E.g., `pfifo_fast` (default FIFO) and `tbf` (Token Bucket Filter) for rate limiting.


* **Classful qdiscs**: E.g., `htb` (Hierarchical Token Bucket), allowing classifiers to split traffic.


* **`clsact`**: A special qdisc that classifies packets and applies actions without queuing.




* **`dev_queue_xmit()`**:
* Selects the appropriate output queue via `netdev_core_pick_tx()` (using XPS or a hash function).


* Enqueues the packet to the Qdisc using the `enqueue()` virtual method.


* Triggers `qdisc_run()` to find the next packet.




* **Qdisc Execution**:
* `qdisc_restart()` calls `qdisc_dequeue()` and attempts transmission via `dev_hard_start_xmit()` and ultimately the driver's `ndo_start_xmit()`.


* If the device returns `NETDEV_TX_BUSY`, transmission is deferred with `dev_requeue_skb()` and a `NET_TX_SOFTIRQ` is scheduled to retry.




* **Driver `ndo_start_xmit()**`:
* Maps buffer for DMA, fills TX descriptors, and notifies the NIC.


* Post-transmission, the NIC fires an interrupt, and `NET_TX_SOFTIRQ` handles cleanup via `dev_kfree_skb_irq()`.





### Part V: Upper Layers and Packet Filtering

* **IPv4 Processing**:
* `ip_rcv()` checks packet validity and executes the `NF_INET_PRE_ROUTING` hook.


* `ip_rcv_finish()` checks destination (via `early_demux()` or routing subsystem).


* Forwards (`ip_forward()` -> `FORWARD` -> `POST_ROUTING`) or delivers locally (`ip_local_deliver()` -> `LOCAL_IN` -> L4 handler).




* **Netfilter**: Built-in kernel framework for packet filtering, NAT, and connection tracking.


* **Hooks**: `NF_INET_PRE_ROUTING`, `NF_INET_LOCAL_IN`, `NF_INET_FORWARD`, `NF_INET_LOCAL_OUT`, `NF_INET_POST_ROUTING`.


* **Tables**: Filter (packet filtering), Raw (pre-tracking manipulation), Mangle (alter IP headers), Nat (address translation).





## Practical Exercises

### Exercise 1: iptables Packet Dropping

**Scenario:** Block all outgoing HTTP traffic from the local machine.
**Implementation:**

```bash
# Append a rule to the OUTPUT chain of the default 'filter' table.
# Protocol is TCP, destination port is HTTP (80), action is DROP.[cite: 44]
sudo iptables -A OUTPUT -p tcp --dport http -j DROP

# Verify the rule was added[cite: 44]
sudo iptables -L

```

### Exercise 2: Packet Capturing with tcpdump

**Scenario:** Capture TCP traffic strictly on interface `enp1s0`, targeting port 443 and a specific destination IP `172.16.133.215`.
**Implementation:**

```bash
# List available interfaces first[cite: 46]
sudo tcpdump --list-interfaces

# Capture the filtered traffic on enp1s0[cite: 46]
sudo tcpdump -i enp1s0 'src port 443 and dst 172.16.133.215'

```

---

## Deliverable 2: Interactive HTML Quiz

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Linux Network Stack Master Quiz</title>
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
    .question-block { border: 1px solid #ddd; padding: 20px; margin-bottom: 20px; border-radius: 8px; background: #f9f9f9; }
    .options { list-style: none; padding: 0; }
    .options li { margin-bottom: 10px; }
    label { cursor: pointer; display: flex; align-items: baseline; gap: 10px; }
    .btn { background: #0066cc; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 16px; margin-top: 20px;}
    .btn:hover { background: #0052a3; }
    .feedback { display: none; padding: 15px; margin-top: 15px; border-radius: 4px; }
    .feedback.correct { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
    .feedback.incorrect { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
    .score-board { font-size: 24px; font-weight: bold; text-align: center; margin: 30px 0; display: none; }
</style>
</head>
<body>

<h1>Linux Network Stack Master Quiz</h1>
<p>Test your knowledge on the inner workings of the Linux Kernel Networking stack.</p>

<div id="quiz-container"></div>
<button class="btn" onclick="submitQuiz()">Submit All Answers</button>
<div id="score" class="score-board"></div>

<script>
const questions = [
    {
        q: "1. The Linux Kernel is best described as a component that:",
        opts: ["Runs a continuous event loop in the background", "Is strictly reactive, stealing time from userspace or CPU idle", "Operates exclusively on CPU Core 0", "Cannot utilize multithreading"],
        ans: 1,
        exp: "Crucially, the kernel is a strictly reactive component and is not always running in the background. It steals time from userspace applications or CPU idle[cite: 3, 4]."
    },
    {
        q: "2. Which interrupts are mapped to the 0-31 range in the interrupt table?",
        opts: ["Software Configurable IRQs", "Linux System Calls", "Processor Interrupts (e.g., page faults)", "Device Interrupts"],
        ans: 2,
        exp: "Indices 0-31 are for processor interrupts, generally fixed by Intel (e.g., 14 is always for page faults)[cite: 6]."
    },
    {
        q: "3. What is the primary characteristic of a Top Half Handler (hardirq)?",
        opts: ["It executes with interrupts enabled.", "It is scheduled by ksoftirqd.", "It executes upon interrupt reception with interrupts disabled to perform operations that cannot be delayed.", "It handles operations that take a long time to process."],
        ans: 2,
        exp: "The Top Half Handler is executed upon reception of the interrupt and performs operations that cannot be delayed. Interrupts and preemption are disabled to ensure it is as fast as possible[cite: 10]."
    },
    {
        q: "4. What happens when a network softirq monopolizes the CPU for too long?",
        opts: ["The kernel panics.", "Hardware interrupts are permanently disabled.", "The softirq continues indefinitely until finished.", "A low-priority per-cpu kernel thread (ksoftirqd/n) is scheduled to handle the remaining tasks."],
        ans: 3,
        exp: "To prevent the softirq from monopolizing the CPU, execution is capped by MAX_SOFTIRQ_RESTART and MAX_SOFTIRQ_TIME. Leftover tasks are scheduled to ksoftirqd/n[cite: 12]."
    },
    {
        q: "5. Why does the `sk_buff` structure use `data` and `tail` pointers?",
        opts: ["To point to the physical memory addresses required by DMA.", "To indicate the hardware timestamp location.", "To delimit the packet data within a larger buffer, allowing headers to be pushed/popped without reallocating memory.", "To link multiple socket buffers together in a circular list."],
        ans: 2,
        exp: "The size of the buffer is bigger than the packet itself. `data` and `tail` can be moved inside the buffer to create or remove space when pushing and popping headers without copying the packet or allocating new memory[cite: 17]."
    },
    {
        q: "6. During packet reception, which function schedules the `NET_RX_SOFTIRQ` softirq?",
        opts: ["__netif_receive_skb_core()", "__napi_schedule()", "br_handle_frame()", "dev_queue_xmit()"],
        ans: 1,
        exp: "The driver irq_handler disables hardware interrupts and schedules the execution of the softirq on the local CPU with the `__napi_schedule()` method[cite: 21, 22]."
    },
    {
        q: "7. To guarantee fair handling across multiple devices in `net_rx_action()`, the system relies on:",
        opts: ["A strict FIFO queue.", "A per-device maximum number of packets limit stored in the `weight` field of `napi_struct`.", "The size of the socket buffer.", "Hardware timestamping constraints."],
        ans: 1,
        exp: "To guarantee fair handling, every device has a maximum number of packets (budget) that can be processed before yielding. This value is stored in the `weight` field of the `napi_struct`[cite: 23]."
    },
    {
        q: "8. What is a possible outcome after executing an XDP (eBPF) program on a received packet descriptor?",
        opts: ["Dropped, Sent out from the same device, Redirected to another device, or Pass to network stack.", "Only Dropped or Passed.", "Immediately routed without consulting the routing table.", "Converted to an IPv6 packet."],
        ans: 0,
        exp: "According to the return value of the XDP program, the packet can be: Dropped, Sent out from the same device, Redirected to another device, or Proceed in its path in the network stack[cite: 24]."
    },
    {
        q: "9. Which software mechanism acts as an alternative to hardware Receive Side Scaling (RSS) to distribute packet processing across CPUs?",
        opts: ["NAPI", "TC", "RPS (Receive Packet Steering)", "GRO (Generic Receive Offload)"],
        ans: 2,
        exp: "RPS (Receive Packet Steering) is the software implementation of RSS. It enqueues the skb to the `softnet_data` of another CPU and wakes it with an inter-CPU interrupt[cite: 26]."
    },
    {
        q: "10. In the kernel receive path, what does `br_handle_frame()` returning `RX_HANDLER_CONSUMED` signify?",
        opts: ["The packet was corrupted.", "The packet has been consumed by the Linux bridge (e.g., forwarded) and should not proceed normally in the local network stack.", "The packet requires a TCP retransmission.", "The packet was intercepted by iptables."],
        ans: 1,
        exp: "The return value determines if the packet must proceed (`RX_HANDLER_PASS`) or has been consumed by the bridge, e.g. forwarded (`RX_HANDLER_CONSUMED`)[cite: 27]."
    },
    {
        q: "11. Which module is responsible for defining the algorithm used to enqueue and dequeue packets for Quality of Service (QoS)?",
        opts: ["Netfilter", "The L3 Protocol handler", "Traffic Control (Queuing Disciplines / qdiscs)", "The socket buffer (`sk_buff`)"],
        ans: 2,
        exp: "Traffic Control (TC) handles QoS through packet scheduling. It is composed of a rich set of queuing disciplines (qdiscs) that define the algorithm used to enqueue and dequeue packets[cite: 30]."
    },
    {
        q: "12. What distinguishes the `clsact` qdisc from standard qdiscs like `htb` or `tbf`?",
        opts: ["It performs strict priority queuing.", "It uses a token bucket to limit rate.", "It doesn't perform queuing but simply classifies packets and applies actions.", "It is only available for loopback interfaces."],
        ans: 2,
        exp: "The `clsact` (classify action) queuing discipline is a particular type of qdisc that doesn't perform queuing but simply classifies packets and applies actions based on the result[cite: 30]."
    },
    {
        q: "13. What occurs if `ndo_start_xmit()` returns `NETDEV_TX_BUSY`?",
        opts: ["The packet is instantly dropped.", "The packet is delivered locally.", "The transmission is deferred using `dev_requeue_skb()` and a TX softirq is scheduled.", "The CPU halts until the device is free."],
        ans: 2,
        exp: "If the device is not able to transmit all buffers (return code `NETDEV_TX_BUSY`), transmission is deferred with `dev_requeue_skb()`, and a softirq is scheduled with `raise_softirq_irqoff(NET_TX_SOFTIRQ)`[cite: 33]."
    },
    {
        q: "14. During packet transmission, how does the NIC typically inform the driver that a packet has been successfully sent?",
        opts: ["By calling a userspace application.", "Through the same interrupt used for packet reception.", "By modifying the `sk_buff` payload.", "By issuing a system call."],
        ans: 1,
        exp: "Usually, the device notifies the driver of a packet sent with the same interrupt used for reception[cite: 35]."
    },
    {
        q: "15. Which function is the main handler for incoming IPv4 packets?",
        opts: ["net_rx_action()", "dev_queue_xmit()", "ip_rcv()", "ip_forward()"],
        ans: 2,
        exp: "The `ip_rcv()` function is the handler for the IPv4 protocol. It performs checks to ensure the packet is valid[cite: 37]."
    },
    {
        q: "16. In Netfilter, which hook is traversed immediately before a routing decision is made for an incoming packet?",
        opts: ["NF_INET_LOCAL_IN", "NF_INET_PRE_ROUTING", "NF_INET_FORWARD", "NF_INET_POST_ROUTING"],
        ans: 1,
        exp: "`ip_rcv()` executes the Netfilter PRE_ROUTING hook passing the `ip_rcv_finish()` function as output, which is in charge of finding the destination of the packet (routing decision)[cite: 37]."
    },
    {
        q: "17. What does the `iptables -A OUTPUT ...` command syntax represent?",
        opts: ["Appends a rule to the end of the OUTPUT chain.", "Alters the OUTPUT interface.", "Allocates memory for the OUTPUT chain.", "Activates the OUTPUT table."],
        ans: 0,
        exp: "The `-A` flag in iptables means 'Append rule to end of a chain'. So `-A OUTPUT` appends a rule to the OUTPUT chain[cite: 40]."
    },
    {
        q: "18. Which Netfilter table is primarily used for altering IP headers (e.g., modifying the TTL field)?",
        opts: ["Filter", "Raw", "Mangle", "Nat"],
        ans: 2,
        exp: "The Mangle table is used to alter IP headers (e.g., TTL)[cite: 42]."
    },
    {
        q: "19. If you issue `iptables -F`, what action is taken on the selected table?",
        opts: ["Forwards the table to another host.", "Finds a specific rule.", "Flushes (Deletes all rules in) the selected table.", "Filters the table based on protocol."],
        ans: 2,
        exp: "The `-F` option stands for Flush. It deletes all the rules in the selected table[cite: 40]."
    },
    {
        q: "20. How do you specify the capture interface in `tcpdump`?",
        opts: ["-interface", "-i", "-net", "-iface"],
        ans: 1,
        exp: "The interface must be specified using the command `-i`[cite: 46]."
    }
];

const container = document.getElementById('quiz-container');

questions.forEach((qObj, index) => {
    let html = `<div class="question-block" id="qblock-${index}">
        <p><strong>${qObj.q}</strong></p>
        <ul class="options">`;
    
    qObj.opts.forEach((opt, optIndex) => {
        html += `<li>
            <label>
                <input type="radio" name="q${index}" value="${optIndex}">
                ${opt}
            </label>
        </li>`;
    });
    
    html += `</ul>
        <div class="feedback" id="feedback-${index}"></div>
    </div>`;
    
    container.innerHTML += html;
});

function submitQuiz() {
    let score = 0;
    questions.forEach((qObj, index) => {
        const selected = document.querySelector(`input[name="q${index}"]:checked`);
        const feedbackDiv = document.getElementById(`feedback-${index}`);
        
        if (selected) {
            const val = parseInt(selected.value);
            if (val === qObj.ans) {
                feedbackDiv.innerHTML = `<strong>Correct!</strong><br><em>Motivation/Explanation:</em> ${qObj.exp}`;
                feedbackDiv.className = "feedback correct";
                score++;
            } else {
                feedbackDiv.innerHTML = `<strong>Incorrect.</strong> The correct answer was option ${qObj.ans + 1}.<br><em>Motivation/Explanation:</em> ${qObj.exp}`;
                feedbackDiv.className = "feedback incorrect";
            }
        } else {
            feedbackDiv.innerHTML = `<strong>No answer selected.</strong> The correct answer was option ${qObj.ans + 1}.<br><em>Motivation/Explanation:</em> ${qObj.exp}`;
            feedbackDiv.className = "feedback incorrect";
        }
        feedbackDiv.style.display = "block";
    });
    
    const scoreDiv = document.getElementById('score');
    scoreDiv.innerHTML = `You scored ${score} out of ${questions.length}!`;
    scoreDiv.style.display = "block";
}
</script>
</body>
</html>

```