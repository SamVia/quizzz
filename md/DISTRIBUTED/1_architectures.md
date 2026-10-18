## Distributed System (DS): Definitions and Core Concepts

* **Wikipedia Definition**: A computing system whose components are located on different networked computers, which communicate and coordinate their actions.


* **Tanenbaum Definition**: A collection of autonomous computing elements that appears to its users as a single coherent system.


* **Computing Elements**: DSs include mainframes, small devices, and elements like processes or threads. For simplicity, these are referred to as a **process** or **node**.


* **Examples**: The Internet, Internet-based applications, IOT, Sensor networks, Cloud-based systems. Most modern applications are distributed.



### DS Main Characterizing Properties

* **Autonomy**: Implies the system is asynchronous (no global clock), concurrent, heterogeneous (spanning different hardware, OS, programming languages, and locations), and prone to partial failure.


* **Networked Interconnection & Geographical Dispersion**: Implies communications take a long or variable time, can fail, and expose a large attack surface for malicious intruders.


* **Security Issues**: Relevant concerns include unauthorized access (eavesdropping, impersonation, spoofing) and disruption of intended behavior (man-in-the-middle, replay, Denial of Service (DOS), code vulnerability exploits).



## Communication Time and Performance

* Each distributed interaction requires **processing time + communication time**.


* Processing time is orders of magnitude less than communication time.


* **Round Trip Time (RTT)**:
* LAN: ~1ms.


* Internet/WAN: ~100ms.





### Transmission Times

The minimum transmission times based on line type are:

* **10Mbps**: 0.05ms (64-bytes), 1.2ms (1500-bytes), 800ms (1Mbyte).


* **100Mbps**: 0.005ms (64-bytes), 0.1ms (1500-bytes), 80ms (1Mbyte).


* **1Gbps**: 0.5us (64-bytes), 0.01ms (1500-bytes), 8ms (1Mbyte).



### Minimum Time for Typical Interactions

* One-way notification datagram: $0.5 \times \text{RTT}$.


* Opening TCP connection + sending notification: $1.5 \times \text{RTT}$.


* UDP request/response: $1 \times \text{RTT}$.


* Opening TCP connection + performing request/response: $2 \times \text{RTT}$.



## DS Main General Requirements

* **Distribution Transparency**: Hiding internal details such as data/computation locations, replication status, and internal storage mechanisms from the user. This is never fully achievable due to latency and failures, creating a transparency vs. performance tradeoff.


* **Dynamic Membership**: The ability to add or remove processes dynamically, requiring processes to locate each other at runtime.


* **Security**: Ensuring confidentiality (no unauthorized access) and integrity/availability (no interference with system behavior).


* **Scalability**: The extent to which a system adapts to increased dimensions without significant performance loss. Types include Size, Geographical, and Administrative. Main challenges are resource limitations and distance-dependent latency/reliability.


* **Openness**: The extent to which a system offers components that can be used by or integrated into other systems, relying on standard protocols and APIs.



## Middleware

* **Definition**: A software layer between applications and the operating system that solves distributed software requirements.


* **OSI Layers**: Relevant OSI layers for DS programmers are the application-oriented layers (5, 6, 7).


* **Functions**: Provides business-unaware services for coordination/communication, hiding network communication, heterogeneity, and security issues.


* **Examples**: Web browsers, database drivers.


* **Non-Examples**: Airline reservation systems (business-aware).


* **Services Provided**: Interaction services (session management, deadlock avoidance), application access (DB access, distributed objects), and management (directory, security).


* **Frameworks**: Middleware components are combined into frameworks like Oracle Java EE, Microsoft .NET, Java Spring, and Amazon AWS.



## Design Goals and Scaling Strategies

* **Design Goals**: Limit interactions to optimize performance, reuse middleware, and build applications relying strictly on APIs for information hiding.


* **Scaling Up**: Improving the capacity of individual elements (e.g., more powerful CPUs).


* **Scaling Out**: Modifying system architecture (e.g., increasing the number of deployed machines).


* **Scaling Out Techniques**:
* **Partitioning and Work Distribution**: Splitting work across processes (e.g., DNS, the Web).


* **Replication**: Replicating processes/data (e.g., caching, web server clustering).


* **Communication Latencies Hiding**: Using asynchronous communication and processing data where it is located.





## Classification of DS Architectures

### Client-Server (C/S) Centralized Architectures

* **Model**: Based on message exchange (client sends request, server sends response). Roles apply to a single interaction; a process can act as both simultaneously.


* **Traits**: Resources are centrally managed in servers, enabling clear role separation. Servers can become bottlenecks or single points of failure.


* **Vertical Distribution (Tiers)**:
* **Logical Tiers**: User interface, processing (logic), and data.


* **2-tier Architectures**: Split into one client tier (front end) and one server tier (back end). Variations include Remote Presentation, Distributed Presentation, Distributed Transaction, Remote Data, and Distributed Data.


* **3-tier & Multi-tier**: Introduces an intermediate physical tier (middle machine) for workload balancing, filtering, or protocol conversion. Examples include Web Gateways (client -> web server -> database) and Legacy Access. Architectures can scale to 4-tiers (client, web, business, data).





### Peer-to-Peer (P2P) Decentralized Architectures

* **Model**: All processes are identical peers playing both client and server roles. Resources are decentralized and replicated. Provides cheap reliability but makes security and control difficult.


* **Horizontal Distribution**: Peers execute identical tasks on partitioned or replicated data sets.


* **Overlay Networks**: Virtual channels mapping connections between peers.


* **Structured**: Built with deterministic, regular topology (e.g., ring, tree). Example: **Chord**, which uses a distributed hash table on a ring topology taking $O(\log(N))$ time for routing.


* **Unstructured**: Peers connect randomly. Reached via flooding or random walks.


* **Hierarchical & Hybrid**: Includes weak-peers connected to super-peers (e.g., Skype overlay network) or mixes P2P with C/S (e.g., BitTorrent uses seed swarms with search/tracker servers).





## Distributed System Abstractions

### Core Abstractions

* **Remote Procedure Calls (RPC)**: Temporally and referentially coupled direct interactions.


* **Message-Oriented Middleware (MOM)**: Temporally decoupled. Includes mailbox-based and event-based systems.


* **Shared Persistent Data**: Referentially decoupled (e.g., Databases, Blockchains, Tuple Spaces).



### Higher-Level Abstractions

* **Distributed Object Systems**: Objects live on multiple networked hosts but are utilized as if local via RPC. Examples: Java RMI, OMG CORBA.


* **Distributed Services**: Larger grain, autonomous, long-living entities (e.g., SOA, Web services).


* **Distributed Resources**: Data entities with states operated on via CRUD (e.g., REST, HTTP).


* **Publish-Subscribe**: C/S paradigm achieving referential decoupling. Publishers generate events, subscribers express interest, and a message broker (centralized like MQTT, decentralized like DDS, or cloud-based like Amazon SNS) routes notifications.


* **Message Queues (MQ)**: Asynchronous interaction where messages are queued until dequeued. Examples: Java Message Service (JMS), Advanced Message Queueing Protocol (AMQP - RabbitMQ), Apache Kafka.



### Lower-Level Communication Abstractions

* **Sockets**: Generic primitives requiring user-defined protocols on top.


* **TCP/IP Sockets**: De-facto standard for layer 4-3-2 access.


* **WebSockets**: Interface for TCP-based full-duplex channels over standard HTTP-compatible protocols.