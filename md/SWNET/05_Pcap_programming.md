## Master Cheat Sheet: Packet Processing with libpcap

### Introduction to Libpcap

* **Definition**: Libpcap is an open-source C library designed to capture and send raw packets directly from a Network Interface Card (NIC).


* **Target Audience**: Primarily targets C programmers, though other languages (like Java) are supported via additional components.


* **Windows Porting**: WinPcap was the historical Windows port (developed at Politecnico di Torino), but nPcap is the modern maintained equivalent.


* **Limitations**: Network switches may filter some packets before libpcap can capture them.



### Capabilities (Do's and Don'ts)

* **What libpcap DOES**:
* Captures raw packets and supports reading traffic from physical interfaces and files.


* Filters traffic (capturing a subset of traffic) and saves filtered traffic to files.




* **What libpcap DOES NOT DO**:
* Does not parse packets (e.g., no easy access to protocol fields like `ip.src`).


* Does not visualize packet content.


* Does not support post-capture filters natively, unless data is saved to a file and reopened with a capture filter applied.





### Core Tools: tcpdump

* **Overview**: A basic command-line sniffer based on libpcap, often the only option for debugging in cloud environments. The Windows equivalent is WinDump.


* **Key Command Line Arguments**:
* `-D`: Prints the list of available network interfaces.


* `-i [interface]`: Captures traffic from the specified interface.


* `-s [snaplen]`: Captures only the first `[snaplen]` bytes of a packet. It is recommended to set this to a large number to prevent missing payload data, especially since modern NICs often implement TCP reassembly returning packets up to 64KB.


* `-n`: Disables resolving addresses into names, which speeds up capture and prevents the generation of unwanted DNS packets in the trace.


* `-r [filename]`: Reads packets from a file instead of a live NIC.


* `-w [filename]`: Saves captured packets to a file (can also be used to filter an existing file and save the output).


* **Example**: `tcpdump -i eth0 -s 10000 -w sample.cap tcp port 80`.





### Installation

* **Linux/UNIX**: Binaries (`libpcap` + `tcpdump`) are usually included in distributions. Developers need to install headers explicitly using `sudo apt install libpcap-dev`.


* **Windows**: Developers must download the library binary (DLLs), the standalone `tcpdump` executable, and the Npcap SDK from the Npcap website.



### Programming Basics & Workflow

1. **Select Interface**: List available adapters using `pcap_findalldevs()`.


2. **Open Interface**: Use `pcap_open_live()` for live capture or `pcap_open_offline()` for file reading.


3. **Compile Filter**: Use `pcap_compile()` to define and compile a BPF packet filter. This requires the pcap handle (to know the data-link type) and a filter string.


4. **Set Filter**: Inject the compiled code into the kernel using `pcap_setfilter()`.


5. **Read Packets**: Choose between polling or event-driven models.



#### Model 1: Polling

* **Implementation**: Utilizes `pcap_next_ex(fp, &header, &pkt_data)`.


* **Data Structures**:
* `fp`: The pcap handler.


* `header`: A `struct pcap_pkthdr` containing `ts` (timestamp as a `timeval` struct with seconds and microseconds), `caplen` (captured packet length), and `len` (total packet length).


* `pkt_data`: The raw packet dump (which may include Ethernet padding).





#### Model 2: Event-Driven (Callback)

* **Implementation**: Utilizes `pcap_loop(fp, 0, dispatcher_handler, NULL)` to block and dispatch packets to a user-defined callback function.


* **Callback Signature**: `void dispatcher_handler(u_char *temp1, const struct pcap_pkthdr *header, const u_char *pkt_data)`.



### Memory, Buffers & Endianness

* **Buffer Boundaries**: The libpcap user buffer resides in application space but is not directly controlled by the programmer. If a program reads beyond `header->caplen` but stays within the general buffer, no error is returned, leading to silent bugs. Processing must be strictly limited to `caplen`.


* **Offset Validation**: Always check that a calculated offset is less than the packet's captured length (e.g., `header->caplen > (etherlen + iplen + tcplen)`) before accessing data, as libpcap may only capture a truncated snapshot.


* **Endianness**: Network byte order is **Big-endian**. Intel CPUs use **Little-endian** (host-based order).


* **Conversion Functions**: Programmers must use conversion functions like `ntohs()` (Network to Host Short, for 16-bit values) to properly interpret protocol fields like `ether_type`. (Note: Windows requires `#include <winsock2.h>` for `ntohs()`).



### Filtering Syntax

BPF filtering syntax is shared across libpcap-based tools.

* `arp`, `ip`, `tcp`, `udp`: Captures only specific protocol packets.


* `host [ip_address]`: Captures traffic to/from the IP.


* `src host [ip_address]` / `dst host [ip_address]`: Directional IP filtering.


* `tcp and port [port]`: Captures TCP packets on a specific port.


* `ether host [MAC_address]`: Filters by MAC (format: `aa:bb:cc:dd:ee:ff`).


* `ether broadcast`: Captures Ethernet broadcast packets.


* **Boolean Operators**: `and`, `or`, `not`, and parenthesis `()` are supported.



### Caveats & Alternatives

* **Performance Caveats**: Writing good packet processing code is difficult due to strict clock-cycle limits per packet. Programmers must avoid copying memory, memory allocations, excessive pointers, and unnecessary function calls.


* **Implementation Difficulties**: Libpcap leaves low-level details (complex encapsulations, IP segmentation, TCP session handling/reassembly) entirely to the programmer. Avoid using fixed offsets in code (e.g., hardcoding byte 14 for IP headers) as it fails on edge cases like VLAN tags.


* **High-Level Alternatives**:
* **Scapy**: Python-based interactive packet manipulation library for forging, decoding, and sending packets.


* **Libtins**: High-level, multiplatform C++ network packet sniffing and crafting library.





---

### Practical Exercises

#### Exercise 1: Opening an Offline Capture File

This snippet demonstrates how to initialize the pcap handler to read from a file.

```c
#include <stdio.h>
#include <pcap.h>

int main(int argc, char **argv) {
    pcap_t *fp;
    char errbuf[PCAP_ERRBUF_SIZE];
    
    if (argc != 2) {
        printf("usage: %s filename\n\n", argv[0]);
        return -1;
    }
    
    /* Open the capture file */
    if ((fp = pcap_open_offline(argv[1], errbuf)) == NULL) {
        fprintf(stderr, "Unable to open the file %s.\n\n", argv[1]);
        return -1;
    }
    
    // ... further processing ...
    pcap_close(fp);
    return 0;
}

```

#### Exercise 2: Polling Packets and Printing a Hex Dump

This code uses `pcap_next_ex` to iterate over packets.

```c
    struct pcap_pkthdr *header;
    const u_char *pkt_data;
    int res;
    u_int i=0;
    
    /* Retrieve the packets from the file */
    while ((res = pcap_next_ex(fp, &header, &pkt_data)) >= 0) {
        /* print pkt timestamp and pkt len */
        printf("%ld:%ld (%d)\n", header->ts.tv_sec, header->ts.tv_usec, header->len);
        
        /* Print the packet */
        for (i=1; i < header->caplen + 1; i++) {
            printf("%.2x ", pkt_data[i-1]);
        }
        printf("\n\n");
    }
    
    if (res == -1) {
        printf("Error reading the packets: %s\n", pcap_geterr(fp));
    }

```

#### Exercise 3: Parsing the Ethernet Header

By mapping the raw `pkt_data` buffer to a C structure, we extract the MAC addresses.

```c
#ifdef WIN32
#include <winsock2.h>
#endif

struct ether_header {
    u_int8_t ether_dhost[6]; /* 6 bytes destination address */
    u_int8_t ether_shost[6]; /* 6 bytes source address */
    u_int16_t ether_type;    /* 2 bytes ethertype */
};

void dispatcher_handler(u_char *temp1, const struct pcap_pkthdr *header, const u_char *pkt_data) {
    struct ether_header *eptr;
    u_int16_t ethertype;
    
    /* Cast the raw packet to the ether_header structure */
    eptr = (struct ether_header *) pkt_data;
    
    printf("%02X:%02X:%02X:%02X:%02X:%02X --> %02X:%02X:%02X:%02X:%02X:%02X\n",
        eptr->ether_shost[0], eptr->ether_shost[1], eptr->ether_shost[2],
        eptr->ether_shost[3], eptr->ether_shost[4], eptr->ether_shost[5],
        eptr->ether_dhost[0], eptr->ether_dhost[1], eptr->ether_dhost[2],
        eptr->ether_dhost[3], eptr->ether_dhost[4], eptr->ether_dhost[5]);
        
    /* Convert ethertype from network to host byte order */
    ethertype = ntohs(eptr->ether_type);
    printf(" (ethertype: 0x%04x)\n\n", ethertype);
}

```

---

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Libpcap Interactive Quiz</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; line-height: 1.6; }
        .question { margin-bottom: 20px; padding: 15px; border: 1px solid #ccc; border-radius: 5px; }
        .options { list-style-type: none; padding: 0; }
        .options li { margin-bottom: 10px; }
        button { padding: 10px 15px; background-color: #007BFF; color: white; border: none; border-radius: 3px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .feedback { margin-top: 10px; font-weight: bold; display: none; padding: 10px; border-radius: 4px; }
        .correct { background-color: #d4edda; color: #155724; }
        .incorrect { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>

    <h1>Libpcap Concept Quiz</h1>
    <form id="quizForm">
        <div id="quiz-container"></div>
        <button type="submit">Submit Quiz</button>
    </form>

    <script>
        const questions = [
            {
                q: "1. What is the primary purpose of libpcap?",
                options: ["Visualizing packet content", "Capturing and sending raw packets from a NIC", "Automatically parsing HTTP requests", "Providing a GUI for packet analysis"],
                answer: 1,
                explanation: "Libpcap is an open-source C library that allows users to capture and send raw packets from a Network Interface Card (NIC)[cite: 2]."
            },
            {
                q: "2. Which of the following is NOT a capability of libpcap?",
                options: ["Capturing raw packets", "Filtering traffic", "Parsing protocol fields (e.g., ip.src)", "Reading traffic from a file"],
                answer: 2,
                explanation: "Libpcap does NOT parse packets to provide easy access to protocol fields; this logic must be implemented by the programmer[cite: 3]."
            },
            {
                q: "3. What is the modern Windows equivalent/port of libpcap?",
                options: ["WinPcap", "nPcap", "WinDump", "Libtins"],
                answer: 1,
                explanation: "nPcap took over as the Windows port when WinPcap ceased to be maintained[cite: 2]."
            },
            {
                q: "4. What command-line flag in tcpdump is used to prevent the resolution of IP addresses into hostnames?",
                options: ["-D", "-i", "-s", "-n"],
                answer: 3,
                explanation: "The '-n' flag tells tcpdump not to resolve addresses into names, which speeds up capture and avoids generating DNS packets[cite: 5]."
            },
            {
                q: "5. Why should the snaplen (-s) flag in tcpdump be set to a large number?",
                options: ["To increase CPU usage", "To capture only the Ethernet header", "To ensure all payload data is captured, compensating for NIC TCP reassembly", "To filter out UDP traffic"],
                answer: 2,
                explanation: "Setting snaplen to a large number ensures all payload gets captured, as modern NICs often implement TCP reassembly and return very large packets (up to 64KB)[cite: 5]."
            },
            {
                q: "6. Which Ubuntu/Debian package must a developer install to compile libpcap programs?",
                options: ["tcpdump-dev", "winpcap-sdk", "libpcap-dev", "scapy"],
                answer: 2,
                explanation: "Developers need to explicitly install the required headers, which are often in a package called libpcap-dev (e.g., `sudo apt install libpcap-dev`)[cite: 6]."
            },
            {
                q: "7. Which function is required to compile a BPF filter string into kernel-injectable code?",
                options: ["pcap_setfilter()", "pcap_compile()", "pcap_next_ex()", "pcap_loop()"],
                answer: 1,
                explanation: "The pcap_compile() function is used to define and compile a BPF packet filter before it can be set[cite: 10]."
            },
            {
                q: "8. In the polling model, what is the primary function used to read packets?",
                options: ["pcap_open_live()", "pcap_next_ex()", "pcap_loop()", "pcap_dispatch()"],
                answer: 1,
                explanation: "pcap_next_ex() is the most common function for reading packets in a polling model[cite: 11]."
            },
            {
                q: "9. What happens if a programmer reads data past the `header->caplen` boundary but stays within the libpcap application buffer?",
                options: ["A segmentation fault occurs instantly", "Libpcap throws a buffer overflow exception", "No errors are returned, leading to silent logic bugs", "The kernel automatically truncates the read"],
                answer: 2,
                explanation: "If a user reads data beyond the packet boundaries (caplen) but stays within the buffer boundaries, no errors are returned, meaning the code will silently fail or read garbage data[cite: 12]."
            },
            {
                q: "10. In the event-driven programming model, which function initiates the blocking loop that waits for packets?",
                options: ["pcap_next_ex()", "pcap_setfilter()", "pcap_loop()", "dispatcher_handler()"],
                answer: 2,
                explanation: "pcap_loop() sets the event handler and stops the thread in a blocking call, automatically triggering the callback function when packets arrive[cite: 13]."
            },
            {
                q: "11. The `struct pcap_pkthdr` contains which of the following variables?",
                options: ["ip_src and ip_dst", "tv_sec, caplen, and len", "ether_type and ether_shost", "snaplen and errbuf"],
                answer: 1,
                explanation: "The `struct pcap_pkthdr` contains the timestamp (`struct timeval ts`), the captured packet length (`caplen`), and the total packet length (`len`)[cite: 11]."
            },
            {
                q: "12. What does the `ntohs()` function do?",
                options: ["Allocates memory for a network host", "Converts a 16-bit integer from network byte order to host byte order", "Translates hostnames to IP addresses", "Converts a 32-bit integer from host byte order to network byte order"],
                answer: 1,
                explanation: "ntohs() converts a value (like the 16-bit ethertype) from network byte order (Big-endian) to the host byte order (e.g., Little-endian for Intel CPUs)[cite: 16, 17]."
            },
            {
                q: "13. What endianness does Network Byte Order use?",
                options: ["Little-endian", "Big-endian", "Host-endian", "Middle-endian"],
                answer: 1,
                explanation: "Network byte order (raw packet data) uses Big-endian representation[cite: 17]."
            },
            {
                q: "14. Which BPF filter captures only packets originating from the IP 10.0.0.1?",
                options: ["host 10.0.0.1", "dst host 10.0.0.1", "src host 10.0.0.1", "ip src 10.0.0.1"],
                answer: 2,
                explanation: "The filter `src host [ip_address]` captures all the packets coming from the given IP host[cite: 22]."
            },
            {
                q: "15. How should a MAC address be formatted in a BPF filter string (e.g., `ether host <MAC>`)?",
                options: ["aa-bb-cc-dd-ee-ff", "aa:bb:cc:dd:ee:ff", "aabb.ccdd.eeff", "AA:BB:CC:DD:EE:FF"],
                answer: 1,
                explanation: "The MAC address must be written as aa:bb:cc:dd:ee:ff[cite: 22]."
            },
            {
                q: "16. Why is it considered bad practice to use fixed offsets (like `&pkt_data[14]`) to parse the IP header?",
                options: ["It causes an immediate syntax error in C", "It fails to account for complexities like VLAN tags", "The Ethernet header is always 20 bytes", "It skips the BPF filter entirely"],
                answer: 1,
                explanation: "Although fixed offsets might work in trivial cases, they fail to support packet variations such as VLANs or IP options[cite: 19]."
            },
            {
                q: "17. What is the safest way to ensure you are not accessing truncated payload data when parsing a protocol?",
                options: ["Always check if `header->caplen > (expected_headers_length)`", "Always assume TCP payloads end with a `\\0` character", "Use `ntohs()` on the payload", "Check if `header->len` equals `1500`"],
                answer: 0,
                explanation: "Correct code always checks against the captured length (`header->caplen`) because libpcap may capture only a snapshot of the packet, preventing buffer overflow bugs when accessing subsequent data[cite: 20]."
            },
            {
                q: "18. Which of the following should be AVOIDED to ensure high performance in packet processing?",
                options: ["Checking packet bounds", "Using bitwise operations", "Memory allocations and function calls", "Defining static C structures for headers"],
                answer: 2,
                explanation: "Because efficiency matters when you only have a few clock cycles per packet, programmers should avoid copying memory, memory allocations, pointers, and function calls[cite: 24]."
            },
            {
                q: "19. Which Python-based library provides a high-level alternative to libpcap for interactive packet manipulation?",
                options: ["Libtins", "Scapy", "Npcap", "WinDump"],
                answer: 1,
                explanation: "Scapy is a powerful interactive packet manipulation library written in Python[cite: 25]."
            },
            {
                q: "20. What protocol does the filter `arp` isolate?",
                options: ["Advanced Routing Protocol", "Address Resolution Protocol", "Any Routing Protocol", "Active Resource Protocol"],
                answer: 1,
                explanation: "The `arp` filter isolates ARP (Address Resolution Protocol) packets. The text states: 'Capture only ARP packets'[cite: 22]."
            }
        ];

        const container = document.getElementById("quiz-container");

        questions.forEach((q, index) => {
            const questionDiv = document.createElement("div");
            questionDiv.classList.add("question");
            
            let optionsHTML = "";
            q.options.forEach((opt, optIndex) => {
                optionsHTML += `
                    <li>
                        <label>
                            <input type="radio" name="q${index}" value="${optIndex}" required>
                            ${opt}
                        </label>
                    </li>
                `;
            });

            questionDiv.innerHTML = `
                <h3>${q.q}</h3>
                <ul class="options">${optionsHTML}</ul>
                <div id="feedback-${index}" class="feedback"></div>
            `;
            container.appendChild(questionDiv);
        });

        document.getElementById("quizForm").addEventListener("submit", function(e) {
            e.preventDefault();
            
            questions.forEach((q, index) => {
                const selected = document.querySelector(`input[name="q${index}"]:checked`).value;
                const feedbackDiv = document.getElementById(`feedback-${index}`);
                
                feedbackDiv.style.display = "block";
                
                if (parseInt(selected) === q.answer) {
                    feedbackDiv.textContent = "Correct! Motivation: " + q.explanation;
                    feedbackDiv.className = "feedback correct";
                } else {
                    feedbackDiv.textContent = "Incorrect. Motivation: " + q.explanation;
                    feedbackDiv.className = "feedback incorrect";
                }
            });
        });
    </script>
</body>
</html>

```