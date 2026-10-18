## Master Cheat Sheet: OpenFlow

### 1. The Origins and Purpose of OpenFlow

* **The Research Problem:** Researchers needed a way to test new networking protocols and ideas on realistic networks with scale and real traffic.


* **The Challenge:** Current network devices were closed to third-party software, making them difficult and expensive to program. Software routers had limited throughput, while custom hardware required huge effort.


* **The OpenFlow Solution:** Launched around 2008 by McKeown, Peterson et al. (with ancestors like Ethane), OpenFlow introduced the concept of **Slicing**. Slicing allows the same physical network to handle both untouched production traffic and experimental research traffic simultaneously.



### 2. Core OpenFlow Architecture and SDN Pillars

OpenFlow is a protocol and represents the first implementation of Software-Defined Networking (SDN).

* **Protocol Functions:** It sends forwarding rules to the switch, receives packets that do not match any rule, injects packets into the switch, and requests/receives switch statistics (e.g., counters).


* **Three Standard SDN Pillars Supported:**
1. Separate control path from data path.


2. Simple data path ("plumbing").


3. Centralized control (at least logically).




* **Context-Based Control Path (Fourth Characteristic):** The control path takes run-time decisions based on actual traffic. Unrecognized traffic is sent to the controller, which can inspect it, return a forwarding decision, and dynamically add new forwarding rules to the switch. The switch effectively acts as a "cache" for these forwarding decisions.



### 3. Configuration Models and Routing Granularity

* **Reactive Configuration:** Packets sent to the controller trigger the insertion of new flow entries.


* *Pros:* Efficient use of the flow table (only needed rules are configured).


* *Cons:* Small additional delay due to flow setup time; switch has limited utility if the control connection is lost.




* **Proactive Configuration:** The controller pre-populates the flow table in the switch.


* *Pros:* Zero additional flow setup time; loss of control connection does not disrupt traffic.


* *Cons:* Requires aggregated (wildcard) rules, similar to an IP routing table.




* **Fine-grained Routing:** Matching is done at a very fine granular level (e.g., one entry per flow, exact-match). Ideal for campus networks and datacenters.


* **Aggregated Routing:** One forwarding rule (flow entry) covers a large group of flows using wildcards. Ideal for backbones.



### 4. Flow Rules and Flow Table Entries

A **Flow Rule** is a traffic flow abstraction connecting arbitrary switch ports, potentially crossing multiple switches, and isolated from other rules. A **Flowmod** is an OpenFlow message used to instantiate, modify, or delete a flow rule on a single switch.

A Flow Table Entry consists of the following components:

* **Match:** List of fields (with netmask/wildcards) matched against packets. Matches arbitrary bits in L2-L4 headers (e.g., Input port, MAC src/dst, VLAN tag, IP src/dst, TCP/UDP ports). Note: L7 fields are not supported.


* **Priority:** A 16-bit value indicating matching precedence. Matching starts at the highest priority; if no match, it checks highest-1, continuing until a match is found.


* **Action(s):** Modifies the action set or pipeline processing. Common actions include:


* Forwarding (to port(s), to controller, or to "normal" processing pipeline).
* Drop.
* Overwrite header field (e.g., replacing a source IP).
* Push/Pop fields (e.g., adding/removing VLAN tags, GRE keys, MPLS labels).


* **Counters:** Statistics (packet/byte counters) updated upon a match.


* **Timeouts:** Maximum amount of time or idle time before the switch expires the flow.


* **Cookies:** Opaque data chosen by the controller to filter entries for statistics, modifications, or deletions (not used for processing packets).


* **Flags:** Alters flow entry management (e.g., `OFPFF_SEND_FLOW_REM` triggers flow removed messages).



### 5. OpenFlow 1.2/1.3 Pipeline Processing

* Unlike OpenFlow 1.0, versions 1.2 and 1.3 utilize multiple tables rather than a simple pipeline.


* A packet enters at Table 0. Each flow in Table $M$ can be redirected to Table $N$ (where $M < N$ to prevent loops).


* Some actions (like send to controller or drop) are applied immediately; others are added to an *Action set*.


* The Action set is executed in a predefined order at the very end of the pipeline.



### 6. Limitations, Economics, and Future

* **Limitations:** While good for separating control and data planes, OpenFlow offers a switch model that is too simple (only tables) and struggles with specialized hardware (encryption, content matching) or complex applications.


* **Computing Alignment:** OpenFlow is constrained by differing hardware table capabilities. Alternatives like P4 and eBPF are emerging because they enable both control *and* data plane programmability, whereas OpenFlow only enables control plane programmability with data-plane configurability.


* **SDN vs. OpenFlow:** SDN is the broader concept (network programmability; "what to do"), while OpenFlow is just one southbound interface implementation ("how to do it").


* **Economics:** OpenFlow threatens network vendors due to low margins on simple forwarding switches. Vendors may attempt to create walled gardens to maintain customer lock-in (e.g., OpenDayLight, Open Networking Foundation).


* **Current Status:** Mostly deployed in virtualized environments (software switches, NFV services) rather than hardware networks.



### Practical Exercises

**Scenario 1: OpenFlow-based NAT for SOHO Devices**

* **Objective:** Implement a Network Address Translation (NAT) application using OpenFlow.
* **Option 1 (No Data/Control Splitting):**
* *Step 1:* A single wildcard flow rule (`If packet = "*" & priority 1`) sends ALL packets to the controller.


* *Step 2:* The NAT application running on the server changes IP/TCP headers, updates session ages, and sends modified packets back.


* *Result:* Very poor performance due to high overhead and bandwidth consumption on the TCP connection between the switch and controller.




* **Option 2 (Data/Control Splitting - The Correct Way):**
* *Step 1:* Only packets belonging to *new* flows are sent to the controller.


* *Step 2:* The controller creates a new entry in its NAT mapping table.


* *Step 3:* The controller updates the packet fields, sends it out, and sends a *Flowmod* to the switch.


* *Rule Example inserted via Flowmod:* `If Port.in=1, IP.src=10.0.0.1, TCP.sport=1000, Priority 10 -> Then change IP.src=20.2.2.2, change TCP.sport=2000, send to port 3`.


* *Result:* Excellent performance for long sessions as the switch acts as a high-speed cache for the controller's mapping table.





**Scenario 2: Dual-Homing Load Balancing & Backup**

* **Objective:** Handle an environment with a fixed primary line (ADSL) and a secondary wireless line (4G).


* **Step 1:** Controller sets initial forwarding rules in the switch to route standard traffic out of Port 2 (ADSL).


* **Step 2:** The controller periodically polls the switch to read traffic counters.


* **Step 3:** If a specific event occurs (e.g., primary link goes down or traffic load exceeds a defined threshold), the controller issues a new Flowmod to dynamically add a rule routing traffic to the 4G backup interface.


* **Edge Case to Consider:** Virtual and physical worlds must coordinate. If routing shifts from ADSL to 4G, the application must ensure IP addresses map correctly (e.g., spinning up a specific NAT instance for the 4G network).

---

Here are the granular details formatted as direct continuation sections. You can copy and paste this directly at the bottom of the original "Master Cheat Sheet" (just above the Practical Exercises or at the very end).

### 7. System Architecture: The Computing vs. Router Gap

OpenFlow struggles to bridge the fundamental architectural differences between how network devices and computing devices handle processing.

* **The Hardware/Software Evolution Constraints:** Software routers (defined specifically as servers with multiport NICs) suffered from limited throughput, while legacy custom hardware was resource-constrained, expensive, and required huge effort available only to big vendors.


* **The Router Perspective:** Traditional networking relies on L2 bridging, L3 routing, internal buses/crossbars, dedicated ASICs, and specific memory types (TCAM, SRAM, and DRAM) for lookup tables.


* **The Computing Perspective:** Computing environments rely on Network Processors, hardware accelerators, Deep Packet Inspection (DPI), VPNs, QoS, and NAT.


* **The Southbound API Problem:** Defining a unified API to accommodate all computing needs is incredibly difficult. To support everything, OpenFlow would theoretically need to support generic code (e.g., x86 instructions), which directly conflicts with its foundational model of "simple forwarding elements". Furthermore, different hardware tables possess different physical capabilities (e.g., Table T1 might natively only support MAC addresses), requiring complex software mapping by the controller.



### 8. Advanced Pipeline & Flow Table Mechanics

* **The Exact Pipeline Sequence:** In OpenFlow 1.2/1.3, the pipeline flows strictly as: `Packet in -> Table 0 -> Table 1 -> Table M -> Table N -> Execute Action Set -> Packet out`.


* **Inter-Table State:** As a packet moves between these tables, the state passed along is specifically the `Packet + ingress port + metadata`. Despite this complexity, it still does not fully solve the problem of creating a suitable hardware abstraction.


* **Additional Action Specifics:** Beyond forwarding, dropping, or modifying headers, OpenFlow supports the explicit action to "Forward at specific bit-rate".


* **Standard Table Structure Matrix:** A standard OpenFlow switch table utilizes the following specific columns to map rules: `MAC src | MAC dst | IP src | IP dst | Proto | Port src | Port dst | Action`.


* *Example Trace:* `Rule 1` (IP dst 10.1.1.1) triggers `Send to port 1`, and `Rule 2` (IP dst 20.2.2.2) triggers `Send to port 2`.





### 9. Application Compatibility & Migration

* **Native Compatibility:** Applications developed by traditional network equipment vendors are natively compatible with OpenFlow's split data/control plane model because their internal architectures already rely on separating forwarding linecards from supervisors.


* **The Linux Rewrite Requirement:** Standard Linux networking applications cannot be ported directly. Software like `iptables` and `linuxbridge` must be entirely rewritten to comply with the OpenFlow control/data plane split.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OpenFlow Interactive Quiz</title>
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
    h1 { color: #2c3e50; }
    .question-block { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin-bottom: 20px; }
    .question-text { font-weight: bold; margin-bottom: 15px; }
    .options label { display: block; margin-bottom: 10px; cursor: pointer; }
    .submit-btn { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 10px; }
    .submit-btn:hover { background: #0056b3; }
    .feedback { margin-top: 15px; padding: 15px; border-radius: 5px; display: none; }
    .correct { background: #d4edda; border-left: 5px solid #28a745; }
    .incorrect { background: #f8d7da; border-left: 5px solid #dc3545; }
    .explanation { font-size: 0.9em; margin-top: 10px; }
</style>
</head>
<body>

<h1>Mastering OpenFlow: 20-Question Quiz</h1>
<div id="quiz-container"></div>

<script>
const quizData = [
    {
        question: "1. What was the primary problem that originally motivated the creation of OpenFlow?",
        options: [
            "A need to increase the hardware speed of linecards.",
            "Researchers had no way to test new network protocols on realistic networks because devices were closed.",
            "The necessity for a new Layer 7 packet inspection protocol.",
            "A desire to replace traditional IP routing tables completely."
        ],
        correctAnswer: 1,
        explanation: "The original OpenFlow question was 'How can researchers test out new ideas in a real network, given that current network devices are closed to third-party software?'[cite: 2]"
    },
    {
        question: "2. In the context of OpenFlow, what does 'Slicing' allow a network to do?",
        options: [
            "Slice packets into smaller MTUs for faster processing.",
            "Allow the same physical network to handle untouched production traffic and experimental research traffic simultaneously.",
            "Divide the controller's memory into isolated virtual machines.",
            "Partition the switch's flow table strictly by MAC address."
        ],
        correctAnswer: 1,
        explanation: "Slicing introduces the concept of splitting the network so production traffic remains untouched while research experiments can run simultaneously on the same hardware[cite: 4, 5]."
    },
    {
        question: "3. Which of the following is NOT one of the standard SDN pillars supported by OpenFlow?",
        options: [
            "Separate control path from data path.",
            "Simple data path.",
            "Decentralized, peer-to-peer control plane.",
            "Centralized control."
        ],
        correctAnswer: 2,
        explanation: "OpenFlow supports Centralized control (at least logically), not a decentralized control plane[cite: 9]."
    },
    {
        question: "4. What is the 'fourth characteristic' enabled by OpenFlow's architecture?",
        options: [
            "Context-based control path",
            "Hardware-accelerated encryption",
            "Automatic topology generation",
            "Distributed autonomous routing"
        ],
        correctAnswer: 0,
        explanation: "OpenFlow enables a context-based control path, allowing decisions to be taken at run-time based on actual traffic[cite: 9, 10]."
    },
    {
        question: "5. When using Reactive configuration in OpenFlow, what happens when an unrecognized packet arrives?",
        options: [
            "The switch immediately drops the packet.",
            "The switch broadcasts the packet to all ports.",
            "The packet is sent to the controller, triggering the insertion of new flow entries.",
            "The switch waits for the controller to push a proactive routing table."
        ],
        correctAnswer: 2,
        explanation: "In reactive mode, packets are sent to the controller which then triggers the insertion of new needed flow entries, making the switch act like a cache[cite: 12]."
    },
    {
        question: "6. What is a primary drawback of Proactive configuration?",
        options: [
            "It requires huge latency for flow setup time.",
            "Loss of control connection severely disrupts all traffic.",
            "It essentially requires aggregated (wildcard) rules, much like an IP routing table.",
            "It can only match exact L7 headers."
        ],
        correctAnswer: 2,
        explanation: "Proactive configuration has zero flow setup time and survives controller disconnections, but it essentially requires aggregated wildcard rules[cite: 12]."
    },
    {
        question: "7. Which fields CANNOT currently be matched by an OpenFlow Flow Table Entry?",
        options: [
            "MAC source and destination",
            "L7 (Application Layer) fields",
            "VLAN tags",
            "TCP/UDP ports"
        ],
        correctAnswer: 1,
        explanation: "OpenFlow can match L2-L4 headers, but L7 fields are not currently supported[cite: 18]."
    },
    {
        question: "8. How are Flow Rules evaluated in an OpenFlow switch?",
        options: [
            "By randomly checking rules until a match is found.",
            "Based on the lowest Priority value (16-bit) first.",
            "Based on the highest Priority value (16-bit) first.",
            "By always evaluating wildcard rules before exact match rules."
        ],
        correctAnswer: 2,
        explanation: "The matching process starts with the flow rules at the highest priority. If no match is found, it moves to (highest-1), and so on[cite: 19]."
    },
    {
        question: "9. What is a 'Flowmod'?",
        options: [
            "A hardware module added to the switch to increase table size.",
            "An OpenFlow message used to instantiate, modify, or delete a flow rule on a single switch.",
            "A protocol used for communication between two controllers.",
            "An action that modifies the payload of a packet."
        ],
        correctAnswer: 1,
        explanation: "A flowmod (OpenFlow flow modification) is an OF message used to instantiate, modify, delete a flow rule on a single switch[cite: 15]."
    },
    {
        question: "10. In OpenFlow 1.2/1.3 pipeline processing, what is the rule regarding multiple tables?",
        options: [
            "Each flow in Table M can be redirected to Table N where M > N.",
            "Loops in the pipeline are permitted for recursive packet inspection.",
            "Each flow in Table M can be redirected to Table N where M < N.",
            "All actions are applied immediately, and action sets are deprecated."
        ],
        correctAnswer: 2,
        explanation: "A flow in Table M can be redirected to another Table N only if M < N, meaning no loops in the pipeline are allowed[cite: 21]."
    },
    {
        question: "11. Where is the Action Set executed in OpenFlow 1.2/1.3?",
        options: [
            "Immediately after Table 0.",
            "At the end of the pipeline in a predefined order.",
            "In the order the action set was created.",
            "It is sent to the controller for execution."
        ],
        correctAnswer: 1,
        explanation: "At the end of the pipeline, the action set is executed in a predefined order, NOT in the order it was created[cite: 21]."
    },
    {
        question: "12. What role do 'Cookies' serve in a Flow Table Entry?",
        options: [
            "They track the user's browser session.",
            "They define the timeout limit for the flow.",
            "They are an opaque data value chosen by the controller to filter entries for statistics/modifications.",
            "They act as the packet/byte counters."
        ],
        correctAnswer: 2,
        explanation: "Cookies are an opaque data value used by the controller to filter flow entries affected by flow statistics, modification, and deletion. They are not used when processing packets[cite: 17]."
    },
    {
        question: "13. In the context of implementing NAT with OpenFlow, what is the problem with sending ALL packets to the controller?",
        options: [
            "It violates the OpenFlow protocol standard.",
            "It causes very poor performance due to high overhead and bandwidth consumption.",
            "It requires specialized P4 hardware.",
            "It prevents the switch from maintaining an Action set."
        ],
        correctAnswer: 1,
        explanation: "If all packets are sent to the controller, the TCP connection suffers from slow, high overhead, causing very poor network performance[cite: 35]."
    },
    {
        question: "14. How should a high-performance OpenFlow NAT be correctly designed?",
        options: [
            "The switch should run the NAT software natively.",
            "All packets should be proactively aggregated into one wildcard rule.",
            "Only packets for new flows are sent to the controller, which sets a rule; the switch acts as a cache.",
            "NAT should only be performed on the backup 4G link."
        ],
        correctAnswer: 2,
        explanation: "By splitting data and control, only new flows hit the controller. The controller sets up a flow rule mapping, and the switch acts as a cache for subsequent packets[cite: 38]."
    },
    {
        question: "15. In a dual-homing load-balancing scenario (ADSL and 4G backup), how does the controller know when to switch links?",
        options: [
            "It pings the switch every millisecond.",
            "It polls the switch and reads traffic counters, acting when thresholds are exceeded or events occur.",
            "The switch natively runs a BGP daemon that informs the controller.",
            "It relies on the 'Timeouts' field expiring."
        ],
        correctAnswer: 1,
        explanation: "The controller polls the switch to read traffic counters and dynamically adds a new rule when a specific event (like primary link down) occurs[cite: 41]."
    },
    {
        question: "16. Why is OpenFlow considered to have limitations regarding data plane abstraction?",
        options: [
            "It cannot separate control and data planes.",
            "The switch model is too simple (only tables) and struggles with specialized hardware like encryption.",
            "It requires all devices to run Linux.",
            "It does not support proactive control."
        ],
        correctAnswer: 1,
        explanation: "OpenFlow's switch model is just tables, making it hard to abstract specialized hardware (like deep packet inspection or encryption) or complex applications[cite: 25]."
    },
    {
        question: "17. What technology is emerging to enable both control AND data plane programmability, contrasting with OpenFlow's limits?",
        options: [
            "VLANs",
            "MPLS",
            "P4 and eBPF",
            "TCP/IP"
        ],
        correctAnswer: 2,
        explanation: "New proposals like P4 and eBPF enable both control and data plane programmability, whereas OpenFlow mainly configures the data plane[cite: 27]."
    },
    {
        question: "18. What represents a potential economic threat of OpenFlow to traditional network vendors?",
        options: [
            "It makes hardware more expensive to produce.",
            "Simple forwarding switches mean low margins for vendors.",
            "It increases the complexity of hardware ASICs.",
            "It requires vendors to pay licensing fees to the Open Networking Foundation."
        ],
        correctAnswer: 1,
        explanation: "OpenFlow pushes networks toward simple, generic forwarding switches, which means low margins and a loss of customer lock-in for traditional vendors[cite: 29]."
    },
    {
        question: "19. Where has OpenFlow seen its most significant deployment currently?",
        options: [
            "Enterprise physical access layer switches.",
            "Consumer home Wi-Fi routers.",
            "Mostly in virtualized environments (software switches) and NFV services.",
            "Undersea fiber optic repeaters."
        ],
        correctAnswer: 2,
        explanation: "OpenFlow has seen limited deployment on real hardware networks and is mostly used in virtualized environments (software switches)[cite: 23, 30]."
    },
    {
        question: "20. The concept of SDN vs OpenFlow can be summarized as:",
        options: [
            "They are exactly the same thing.",
            "SDN is an open-source tool, OpenFlow is a proprietary license.",
            "SDN is 'what to do' (programmability concept), OpenFlow is 'how to do it' (a southbound interface).",
            "OpenFlow is the controller, SDN is the physical switch."
        ],
        correctAnswer: 2,
        explanation: "SDN is a broader concept (network programmability / what to do), while OpenFlow represents just one way to implement the southbound interface of SDN (how to do)[cite: 28]."
    }
];

const container = document.getElementById('quiz-container');

quizData.forEach((q, index) => {
    const questionDiv = document.createElement('div');
    questionDiv.className = 'question-block';
    
    const questionTitle = document.createElement('div');
    questionTitle.className = 'question-text';
    questionTitle.innerText = q.question;
    questionDiv.appendChild(questionTitle);

    const optionsDiv = document.createElement('div');
    optionsDiv.className = 'options';
    
    q.options.forEach((opt, optIndex) => {
        const label = document.createElement('label');
        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = `question${index}`;
        radio.value = optIndex;
        
        label.appendChild(radio);
        label.appendChild(document.createTextNode(' ' + opt));
        optionsDiv.appendChild(label);
    });
    
    questionDiv.appendChild(optionsDiv);

    const submitBtn = document.createElement('button');
    submitBtn.className = 'submit-btn';
    submitBtn.innerText = 'Check Answer';
    questionDiv.appendChild(submitBtn);

    const feedbackDiv = document.createElement('div');
    feedbackDiv.className = 'feedback';
    
    const feedbackTitle = document.createElement('strong');
    const feedbackExp = document.createElement('div');
    feedbackExp.className = 'explanation';
    
    feedbackDiv.appendChild(feedbackTitle);
    feedbackDiv.appendChild(feedbackExp);
    questionDiv.appendChild(feedbackDiv);

    submitBtn.onclick = () => {
        const selected = document.querySelector(`input[name="question${index}"]:checked`);
        if (!selected) {
            alert('Please select an answer first.');
            return;
        }

        const isCorrect = parseInt(selected.value) === q.correctAnswer;
        feedbackDiv.style.display = 'block';
        feedbackDiv.className = 'feedback ' + (isCorrect ? 'correct' : 'incorrect');
        
        feedbackTitle.innerText = isCorrect ? 'Correct!' : 'Incorrect.';
        feedbackExp.innerText = q.explanation;
        
        // Disable radios after submission
        const radios = document.querySelectorAll(`input[name="question${index}"]`);
        radios.forEach(r => r.disabled = true);
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.5';
    };

    container.appendChild(questionDiv);
});
</script>

</body>
</html>

```