## Software Defined Networks (SDN) Master Cheat Sheet

### 1. Network Device Logical Architecture

* A network device is logically partitioned into three planes:


* **Management plane**: Used for user/admin configuration.


* **Control plane**: Handles dynamic configuration of data plane tables (e.g., routing protocols like OSPF).


* **Data plane**: Responsible for actual traffic forwarding.




* **Networking Domain vs. General Computing**:
* The networking market has historically been vertically integrated and closed to innovation (e.g., proprietary hardware and OS from vendors like Cisco and Huawei).


* General computing operates on a 3-layer market (hardware, OS, applications) with well-defined separation interfaces (e.g., CPU instruction sets, OS APIs).




* **Traditional Internet limitations**: Uses protocols defined in the mid-80s, offers limited control on network paths, has no control over applications, and cannot extend its operating system to provide virtualized network slices.



### 2. Original SDN Definition & The 4 Pillars

SDN physically separates the control plane from the forwarding plane, allowing a control plane to programmatically control multiple devices.

* **Pillar 1: Separate control from data plane**.


* Routing/application logic is implemented in a software application running on an external controller.


* Advantages: Control plane is easy to change (e.g., replacing IP routing with custom logic for network slices), and switches become simpler, faster, and cheaper.


* Interoperability is guaranteed by standard southbound interfaces (e.g., OpenFlow).




* **Pillar 2: Simple data plane ("plumbing")**.


* Traffic forwarding is based on a match/action paradigm (e.g., matching a header and executing "forward to" or "drop").


* These lookup tables can simulate bridges (MAC match) or routers (longest prefix match).




* **Pillar 3: Single point of control**.


* Software maintains a global view of the entire network, which is easier than isolated distributed routing protocols.


* **Big Switch Abstraction**: The SDN controller exports a view that hides internal network details, allowing administrators to use high-level commands (intents) like setting a direct path from Port A to Port B without managing individual switches.




* **Pillar 4: Context-based forwarding**.


* Decisions can be taken at run-time based on actual traffic, unlike traditional IP where decisions are pre-calculated based on topology.


* Example in OpenFlow: If no match is found, the switch sends the packet to the controller, which customizes rules dynamically based on the traffic (e.g., recognizing new hosts).





### 3. Controller Architecture & Distributed Systems

* **Logically Centralized Control**: While SDN defines a single control point, the controller does not mandate a single physical server; it can be distributed across a cluster for robustness and scalability.


* **CAP Theorem**: States that a distributed data store cannot simultaneously provide Consistency, Availability, and Partition tolerance (limited to two).


* **Eventual Consistency**: Distributed controllers often use algorithms (like Paxos/Raft) ensuring that if no new updates are made, all accesses will eventually return the last updated value.


* **Developer Impact**: Controllers try to export a "monolithic" development model so programmers don't have to write distributed apps, but developers must still define which data is shared vs. private.



### 4. SDN Architecture Components

* **Network Operating System (NetOS)**: A software layer offering a global view to upper applications, transforming single logical configurations into multiple physical commands.


* **Northbound Interface**: Open API connecting the SDN controller to complex user-defined applications (e.g., firewalls, load balancers, orchestrators).


* **Southbound Interface**: Standard protocol (e.g., OpenFlow) between the controller and data plane switches.


* **Slicing**: Virtualization layer allowing isolated slices (virtual networks) running on different network operating systems over the same physical hardware.



### 5. Current SDN Reality & Evolution

* **Raj Jain's Definition**: SDN is a software paradigm allowing automatic and dynamic management of devices, topology, traffic, and policies using third-party software and APIs, including FCAPS (faults, configuration, accounting, performance, security).


* **Disaggregation Reality**: Complete separation of data/control plane isn't universally practical because simple devices cannot react autonomously to faults. Modern devices keep local control planes for fast, local reactions, while the overarching controller handles domain-wide configuration.


* **Keywords**: End-to-end, Cross-layer, Orchestration, Agility, Third-party software.



### 6. SD-WAN (Software-Defined WAN)

* **Definition**: SDN applied to WAN connections (broadband, 4G, LTE, MPLS) to connect enterprise networks, branch offices, and data centers.


* **Characteristics**: Virtual CPE, WAN virtualization, policy-driven centralized management, and elastic traffic management.


* **Use Cases**: Dynamic setup of encrypted tunnels, reacting to changing network conditions, and prioritizing traffic based on user/app workloads.



### 7. SDN Controllers in Practice

* Controllers evolved from OpenFlow controllers (enabling programmability) and Network Management Systems (managing heterogeneous WAN devices).


* **Examples**:
* *Open Source*: OpenDaylight, ONOS, OpenContrail.


* *Proprietary*: Cisco NSO (Tail-f).




* **OpenDaylight**: Backed primarily by Cisco with a growing community, characterized by increasing complexity across releases (Hydrogen, Helium, Lithium).



### Practical Exercises

**Scenario 1: Resolving Unknown Traffic in OpenFlow**

1. **State**: Host A connects to an SDN switch and sends a packet. The switch table has zero rules for Host A.
2. **Action**: The switch relies on Pillar 4 (Context-based forwarding). It hits a default rule: `If no match, send to me (controller)`.


3. **Controller Intervention**: The controller analyzes the packet header, applies security/routing policies, and determines Host A's destination.
4. **Rule Deployment**: The controller sends the packet back to the switch to be forwarded and installs a new match/action rule (e.g., `If MAC=Host A, send to port 2`) so the switch caches the decision for future packets.



---

### Deliverable 2: Interactive 20-Question HTML Quiz

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SDN Master Quiz</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2rem; max-width: 800px; line-height: 1.6; }
        .question { margin-bottom: 2rem; padding: 1rem; border: 1px solid #ccc; border-radius: 8px; }
        .options { list-style: none; padding: 0; }
        .options li { margin: 0.5rem 0; }
        button { padding: 0.5rem 1rem; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .feedback { margin-top: 1rem; padding: 1rem; display: none; border-radius: 4px; }
        .correct { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .incorrect { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>

    <h1>Software Defined Networks (SDN) Quiz</h1>
    <div id="quiz-container"></div>

    <script>
        const quizData = [
            {
                q: "1. Which logical plane is responsible for dynamic configuration of data tables like OSPF routing?",
                options: ["Management plane", "Control plane", "Data plane", "Application plane"],
                ans: 1,
                exp: "The Control plane handles the dynamic configuration of data plane tables.[cite: 1]"
            },
            {
                q: "2. How does the general computing domain differ from the traditional networking domain?",
                options: ["Networking has open hardware standard interfaces", "Computing is vertically integrated", "Computing has a 3-layer market with clear separation interfaces", "There is no difference"],
                ans: 2,
                exp: "General computing is a 3-layer market (hardware, OS, apps) with well-defined separation interfaces, unlike the historically closed, vertically integrated networking domain.[cite: 1]"
            },
            {
                q: "3. What is the first original pillar of SDN?",
                options: ["Simple data plane", "Context-based forwarding", "Single point of control", "Separate control from data plane"],
                ans: 3,
                exp: "The first pillar is separating the control plane from the data plane, moving routing logic to an external controller.[cite: 1]"
            },
            {
                q: "4. The concept that creates 'network pipes' using a match/action paradigm refers to which SDN pillar?",
                options: ["Separate control plane", "Simple data plane", "Context-based forwarding", "Single point of control"],
                ans: 1,
                exp: "The Simple data plane ('plumbing') relies on match/action rules (e.g., forward or drop) to handle traffic.[cite: 1]"
            },
            {
                q: "5. What abstraction allows software to issue high-level 'intents' to the entire network?",
                options: ["Big switch abstraction", "Little router abstraction", "Distributed node abstraction", "Context abstraction"],
                ans: 0,
                exp: "The 'big switch' abstraction hides internal network details and allows high-level intents.[cite: 1]"
            },
            {
                q: "6. According to the CAP theorem, a distributed data store can simultaneously provide a maximum of how many guarantees?",
                options: ["One", "Two", "Three", "Four"],
                ans: 1,
                exp: "The CAP theorem states a distributed system can provide at most two of the following: Consistency, Availability, and Partition tolerance.[cite: 1]"
            },
            {
                q: "7. Which algorithm is commonly used to guarantee 'Eventual Consistency' in distributed SDN controllers?",
                options: ["Dijkstra", "Paxos/Raft", "Bellman-Ford", "RSA"],
                ans: 1,
                exp: "Paxos/Raft algorithms are utilized to ensure Eventual Consistency in distributed data stores.[cite: 1]"
            },
            {
                q: "8. Context-based forwarding means decisions are taken based on:",
                options: ["Topology calculated ahead of time", "Run-time actual traffic", "Pre-installed BGP rules", "The management plane only"],
                ans: 1,
                exp: "Context-based forwarding allows decisions to be taken at run-time based on actual traffic, as opposed to IP routing which computes tables ahead of time.[cite: 1]"
            },
            {
                q: "9. What happens in OpenFlow when a packet doesn't match any rules on the switch?",
                options: ["It broadcasts the packet", "It drops the packet instantly", "It sends the packet to the controller", "It loops the packet"],
                ans: 2,
                exp: "If there is no match in the forwarding table, OpenFlow rules typically dictate sending the packet to the controller for a context-based decision.[cite: 1]"
            },
            {
                q: "10. The interface that connects the SDN controller to the data plane switches is called the:",
                options: ["Northbound Interface", "Westbound Interface", "Southbound Interface", "Eastbound Interface"],
                ans: 2,
                exp: "The Southbound interface (e.g., OpenFlow) is the standard protocol between the controller and the hardware switches.[cite: 1]"
            },
            {
                q: "11. The interface that connects user-defined complex applications to the SDN controller is called the:",
                options: ["Northbound API", "Southbound API", "Management API", "Hardware API"],
                ans: 0,
                exp: "The Northbound API connects complex network applications and orchestration services to the controller operating system.[cite: 1]"
            },
            {
                q: "12. What enables the creation of isolated virtual networks over the same physical hardware?",
                options: ["Context Forwarding", "Virtualization or Slicing Layer", "Northbound API", "Raft consensus"],
                ans: 1,
                exp: "A Virtualization or 'Slicing' layer allows multiple Network Operating Systems to operate isolated slices over shared simple hardware.[cite: 1]"
            },
            {
                q: "13. In modern actual SDN deployments, what happened to the 'dumb data plane' concept?",
                options: ["It was adopted universally", "Switches kept a local control plane to react to faults quickly", "It replaced all Cisco hardware", "It was abandoned for manual CLI configurations"],
                ans: 1,
                exp: "Complete disaggregation didn't fully happen; devices keep a local control plane to react autonomously and rapidly to external stimuli like faults.[cite: 1]"
            },
            {
                q: "14. SD-WAN is primarily intended to connect:",
                options: ["Home IoT devices", "Servers within a single datacenter rack", "Enterprise networks, branch offices, and data centers over large distances", "Only mobile phones"],
                ans: 2,
                exp: "SD-WAN is an application of SDN to WAN connections intended to connect enterprise networks, branches, and data centers over large geographic areas.[cite: 1]"
            },
            {
                q: "15. Which of the following is an open-source SDN controller?",
                options: ["Cisco NSO", "Tail-f", "OpenDaylight", "Cumulus"],
                ans: 2,
                exp: "OpenDaylight is a major open-source SDN controller framework backed initially by Cisco.[cite: 1]"
            },
            {
                q: "16. Why do network operators support open-source SDN initiatives?",
                options: ["They prefer complex code", "To avoid suffering from vendor lock-in", "They want to sell hardware", "Open source has no bugs"],
                ans: 1,
                exp: "Operators prefer open-source controllers to prevent vendor lock-in and share the cost of basic network software infrastructure.[cite: 1]"
            },
            {
                q: "17. What does FCAPS stand for in the context of SDN management?",
                options: ["Forwarding, Control, Apps, Policies, Security", "Faults, Configuration, Accounting, Performance, Security", "Fast Connectivity And Processing System", "Flow Control And Path Setup"],
                ans: 1,
                exp: "FCAPS stands for faults, configuration, accounting, performance, and security management.[cite: 1]"
            },
            {
                q: "18. Which controller release names are associated with OpenDaylight?",
                options: ["Alpha, Beta, Gamma", "Hydrogen, Helium, Lithium", "V1, V2, V3", "Red, Blue, Green"],
                ans: 1,
                exp: "OpenDaylight release slides show versions named Hydrogen, Helium, and Lithium.[cite: 1]"
            },
            {
                q: "19. What is a recognized downside of the original 'dumb' SDN forwarding hardware?",
                options: ["It was too fast", "It was not scalable without hardware speedups and went against major vendor interests", "It consumed too much software memory", "It could only route IP"],
                ans: 1,
                exp: "Simple packet hardware struggled with scalability without hardware speedup and fundamentally conflicted with the business interests of incumbent network vendors.[cite: 1]"
            },
            {
                q: "20. SD-WAN achieves dynamic traffic management by using what approach?",
                options: ["Strict manual CLI configs", "Policy-driven, centralized management prioritizing traffic by app", "Randomized routing", "Only open-source hardware"],
                ans: 1,
                exp: "SD-WAN uses policy-driven, centralized management to provide elastic traffic management, automatically prioritizing by user or application.[cite: 1]"
            }
        ];

        const container = document.getElementById('quiz-container');

        quizData.forEach((item, index) => {
            const qDiv = document.createElement('div');
            qDiv.className = 'question';
            qDiv.innerHTML = `<h3>${item.q}</h3>`;
            
            const ul = document.createElement('ul');
            ul.className = 'options';
            item.options.forEach((opt, optIndex) => {
                const li = document.createElement('li');
                li.innerHTML = `<label><input type="radio" name="q${index}" value="${optIndex}"> ${opt}</label>`;
                ul.appendChild(li);
            });
            qDiv.appendChild(ul);

            const btn = document.createElement('button');
            btn.innerText = 'Submit Answer';
            const feedback = document.createElement('div');
            feedback.className = 'feedback';

            btn.onclick = () => {
                const selected = document.querySelector(`input[name="q${index}"]:checked`);
                if (!selected) {
                    alert('Please select an option');
                    return;
                }
                const isCorrect = parseInt(selected.value) === item.ans;
                feedback.style.display = 'block';
                if (isCorrect) {
                    feedback.className = 'feedback correct';
                    feedback.innerHTML = `<strong>Correct!</strong> ${item.exp}`;
                } else {
                    feedback.className = 'feedback incorrect';
                    feedback.innerHTML = `<strong>Incorrect.</strong> The correct answer was: <em>${item.options[item.ans]}</em>.<br><br><strong>Motivation:</strong> ${item.exp}`;
                }
                btn.disabled = true; // prevent re-submitting
            };

            qDiv.appendChild(btn);
            qDiv.appendChild(feedback);
            container.appendChild(qDiv);
        });
    </script>
</body>
</html>

```