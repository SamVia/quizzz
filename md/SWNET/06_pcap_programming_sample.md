Di seguito sono riportati i due elaborati richiesti, generati elaborando interamente i file forniti e traducendo le relative spiegazioni in lingua italiana come richiesto dalle direttive di sistema per i prompt contenenti file allegati.

## Deliverable 1: Master Cheat Sheet – Programmazione con Libpcap

### 1. Introduzione alla Cattura dei Pacchetti (Packet Capture)

* I programmi di analisi dei pacchetti (packet analyzers) o "sniffer" intercettano il traffico che transita su una rete.


* Nelle reti basate su Ethernet, la scheda di rete genera un interrupt quando l'indirizzo MAC di destinazione di un frame ricevuto corrisponde al proprio.


* Il driver della scheda di rete inserisce un timestamp nei dati ricevuti, li copia dal buffer della scheda alla memoria in "kernel space" e determina il tipo di pacchetto esaminando il campo *ethertype*.


* I driver di rete, quando è in esecuzione uno sniffer, inviano anche una copia di qualsiasi pacchetto (in entrata o in uscita) a una sezione del kernel chiamata "packet filter" (filtro dei pacchetti).


* L'utilizzo delle funzionalità di cattura dei pacchetti generalmente richiede privilegi di amministratore a causa dei rischi legati alla sicurezza.



### 2. Architettura della Libreria Libpcap

* Libpcap è una libreria open source che offre un'interfaccia ad alto livello (API) indipendente dalla piattaforma per i sistemi di cattura di rete.


* È stata creata nel 1994 da McCanne, Leres e Jacobson, ricercatori del Lawrence Berkeley National Laboratory dell'Università della California a Berkeley.


* L'obiettivo principale era eliminare la necessità di moduli di cattura pacchetti dipendenti dal sistema operativo per ogni applicazione.


* L'API di libpcap è progettata per linguaggi C e C++, ma possiede wrapper per Perl, Python, Java, C# o Ruby.


* L'architettura alla base dei filtri dei pacchetti in molti sistemi operativi moderni è il BSD Packet Filter (BPF).


* Attualmente, libpcap è manutenuta dal Tcpdump Group ed è il nucleo di strumenti famosi come `tcpdump`, `dsniff`, `kismet`, `snort` o `ettercap`.



### 3. API di Libpcap: Strutture e Costanti Fondamentali

La costante per la dimensione del buffer di errore è `PCAP_ERRBUF_SIZE`, correntemente definita a 256 byte.

```c
struct pcap_pkthdr {
    struct timeval ts;     /* Timestamp of capture */
    bpf_u_int32 caplen;    /* Number of bytes that were stored */
    bpf_u_int32 len;       /* Total length of the packet */
};

```

* **Nota:** `caplen` indica i byte effettivamente salvati; ha di solito lo stesso valore di `len` tranne quando la dimensione del pacchetto supera il valore di `snaplen` definito in configurazione.



### 4. API di Libpcap: Funzioni Principali

* `char *pcap_lookupdev(char *errbuf)`: Restituisce un puntatore a una stringa contenente il nome del primo dispositivo di rete idoneo alla cattura dei pacchetti.


* `pcap_t *pcap_open_live(const char *device, int snaplen, int promisc, int to_ms, char *errbuf)`: Apre l'interfaccia di rete e restituisce un gestore di tipo `pcap_t`.


* `snaplen`: Il numero massimo di byte da catturare (tipicamente 65535 per contenere pacchetti completi).


* `promisc`: Imposta la modalità promiscua se diverso da 0 (0 indica la modalità non-promiscua).


* `to_ms`: Definisce quanti millisecondi il kernel deve attendere prima di copiare le informazioni catturate nello spazio utente (es. tcpdump usa 1000, dsniff 512, ettercap 0 su Linux o 10 su altri OS).




* `const u_char *pcap_next(pcap_t *p, struct pcap_pkthdr *h)`: Prende il gestore di interfaccia e restituisce il primo pacchetto in arrivo all'interfaccia di rete.


* `int pcap_loop(pcap_t *p, int cnt, pcap_handler callback, u_char *user)`: Raccoglie i pacchetti e li passa alla funzione di callback finché non vengono catturati `cnt` pacchetti; un valore negativo di `cnt` fa sì che ritorni solo in caso di errore.


* La funzione di callback deve avere la firma esatta: `void function_name(u_char *userarg, const struct pcap_pkthdr *pkthdr, const u_char *packet);`.


* `int pcap_dispatch(pcap_t *p, int cnt, pcap_handler callback, u_char *user)`: Simile a `pcap_loop`, ma ritorna quando scade il timeout `to_ms` specificato in precedenza.


* `int pcap_datalink(pcap_t *p)`: Restituisce il tipo di link layer del dispositivo in analisi (libpcap ne distingue oltre 180).



### 5. Livelli OSI: Tipi di Dati, Offset e Protocolli

| Data Link Type | Pcap Alias | Offset (in bytes) |
| --- | --- | --- |
| Ethernet 10/100/1000 Mbs | `DLT_EN10MB` | 14 |
| Wi-Fi 802.11 | `DLT_IEEE802_11` | 22 |
| FDDI | `DLT_FDDI` | 21 |
| PPPoE | `DLT_PPP_ETHER` | 14 (Ethernet) + 6 (PPP) = 20 |
| BSD Loopback | `DLT_NULL` | 4 |
| Point to Point (Dial-up) | `DLT_PPP` | *[non specificato]* |
| <br><br> |  |  |

| Network Layer Protocol | Ethertype Value |
| --- | --- |
| IPv4 | `0x0800` |
| IPv6 | `0x86DD` |
| ARP | `0x0806` |
| RARP | `0x8035` |
| AppleTalk over Ethernet (EtherTalk) | `0x809B` |
| Point-to-Point Protocol (PPP) | `0x880B` |
| PPPoE Discovery Stage | `0x8863` |
| PPPoE Session Stage | `0x8864` |
| SNMP | `0x814C` |
| <br><br> |  |

| Protocol | Value (Hex) | RFC |
| --- | --- | --- |
| ICMP | `0x01` | RFC 792 |
| IGMP | `0x02` | RFC 3376 |
| TCP | `0x06` | RFC 793 |
| Exterior Gateway Protocol | `0x08` | RFC 888 |
| UDP | `0x11` | RFC 768 |
| IPv6 Routing Header | `0x2B` | RFC 1883 |
| IPv6 Fragment Header | `0x2C` | RFC 1883 |
| ICMP for IPv6 | `0x3A` | RFC 1883 |
| <br><br> |  |  |

### 6. Analisi dei Pacchetti Malformati e Controllo Errori

* Controllare l'intera dimensione del pacchetto (es. pacchetti ARP su Ethernet devono essere 14 + 28 = 42 byte; scartare lunghezze diverse evita "segmentation fault" rumorosi).


* Verificare i checksum IP e TCP, poiché checksum errati implicano pacchetti contenenti "spazzatura" (garbage).


* Verificare la codifica in quanto protocolli come HTTP o SMTP sono orientati al testo, a differenza di Ethernet o TCP/IP che usano formati binari.


* Convertire sempre il valore esadecimale letto nel byte order di rete nell'ordine corretto tramite la funzione `ntohs()`.



### 7. Gestione dei Filtri (BPF)

* L'impostazione di un filtro si compone di tre passaggi: costruzione dell'espressione, compilazione in un programma BPF, e applicazione del filtro.


* **Costruzione ESPRESSIONI Esempio:**
* `src host 192.168.1.77`: pacchetti provenienti dall'IP specificato.


* `dst port 80`: pacchetti destinati alla porta TCP/UDP 80.


* `not tcp`: qualsiasi pacchetto che non utilizza il protocollo TCP.


* `tcp[13] == 0x02 and (dst port 22 or dst port 23)`: pacchetti TCP con il flag SYN impostato verso le porte 22 o 23.


* `icmp[icmptype] == icmp-echoreply or icmp[icmptype] == icmp-echo`: richieste o risposte di ping ICMP.


* `ether dst 00:00:09:c1:0e:82`: frame Ethernet destinati all'indirizzo MAC specificato.


* `ip[8] == 5`: pacchetti con valore IP TTL pari a 5.




* `int pcap_compile(pcap_t *p, struct bpf_program *fp, char *str, int optimize, bpf_uint32 netmask)`: Compila l'espressione di filtro puntata da `str` in codice BPF.


* `int pcap_lookupnet(const char *device, bpf_uint32 *netp, bpf_uint32 *maskp, char *errbuf)`: Determina la maschera di rete.


* `int pcap_setfilter(pcap_t *p, struct bpf_program *fp)`: Inserisce e applica il programma BPF compilato nel kernel.



---

### 8. Esercitazioni Pratiche (Tracce Verbatim, Istruzioni e Snippet)

#### A. Lettura di un Capture Dump File Locale

Istruzioni per l'ambiente Linux da terminale:

```bash
# Compile in Linux with:
gcc readfile.c -lpcap -o readfile

# Run the program with the capture dump as first parameter, e.g.,
./readfile packet_trace.dump

# You can use 'tcpdump' to create another packet trace:
sudo tcpdump -w filename.dump

```

Il file allegato (readfile.c) apre un capture dump locale estraendo metadati e payload, riportato qui fedelmente:

```c
// Standard C include file for I/O functions
#include <stdio.h>

// Include files for libpcap functions
#include <pcap.h>

#define LINE_LEN 16

int main(int argc, char **argv)
{
    pcap_t *fp;
    char errbuf[PCAP_ERRBUF_SIZE];
    struct pcap_pkthdr *header;
    const u_char *pkt_data;
    u_int i=0;
    int res;
	
    if (argc != 2)
    {	
        printf("Usage: %s filename\n\n", argv[0]);
        return -1;
    }
	
    /* Open the capture file */
    /* Parameters: name of the file to open, error buffer */
    if ((fp = pcap_open_offline(argv[1], errbuf)) == NULL)
    {
        fprintf(stderr,"Unable to open file %s.\n\n", argv[1]);
        return -1;
    }
	
    /* Retrieve packets from the file */
    while((res = pcap_next_ex(fp, &header, &pkt_data)) >= 0)
    {
        /* print pkt timestamp and pkt len */
        printf("%ld:%ld (%d)\n", header->ts.tv_sec, header->ts.tv_usec, header->len);
		
        /* Print the packet */
        for (i=0; i < header->caplen; i++)
        {
            printf("%.2x ", pkt_data[i]);

            if ( ((i+1) % LINE_LEN) == 0)
               printf("\n");
        }
		
        printf("\n\n");
    }
	
    if (res == -1)
        printf("Error reading the packets: %s\n", pcap_geterr(fp));
	
    pcap_close(fp);
    return 0;
}

```

Traccia esadecimale di Esempio di traffico intercettato (estratti Raw Payload Capture):

```text
ÔÃ²¡            î       ìDGDZ *   *   ÿÿÿÿÿÿ  # ”¼            # ”¼‚À Q      ‚À PìDGøZ <   <     # ”¼  °ýÒs            °ýÒs‚À P  # ”¼‚À Q                  ìDG[ J   J     °ýÒs  # ”¼  E  <1ø  €   ‚À Q‚À P  LÐ   ‹abcdefghijklmnopqrstuvwabcdefghiìDG±[ J   J     # ”¼  °ýÒs  E  <äR  € 0M‚À P‚À Q  TÐ   ‹abcdefghijklmnopqrstuvwabcdefghiíDG e J   J     °ýÒs  # ”¼  E  <1ù  €   ‚À Q‚À P  LÏ   ŒabcdefghijklmnopqrstuvwabcdefghiíDGÌe J   J     # ”¼  °ýÒs  E  <äS  € 0L‚À P‚À Q  TÏ   ŒabcdefghijklmnopqrstuvwabcdefghiîDG m J   J     °ýÒs  # ”¼  E  <1û  €   ‚À Q‚À P  LÎ    abcdefghijklmnopqrstuvwabcdefghiîDGÊm J   J     # ”¼  °ýÒs  E  <äT  € 0K‚À P‚À Q  TÎ    abcdefghijklmnopqrstuvwabcdefghiïDG u J   J     °ýÒs  # ”¼  E  <1þ  €   ‚À Q‚À P  LÍ   ŽabcdefghijklmnopqrstuvwabcdefghiïDGÖu J   J     # ”¼  °ýÒs  E  <äU  € 0J‚À P‚À Q  TÍ   Žabcdefghijklmnopqrstuvwabcdefghi

```

#### B. Costruzione di uno Sniffer Base Live

```c
/* Simple Sniffer */
/* To compile: gcc simplesniffer.c -o simplesniffer -lpcap */

#include <pcap.h>
#include <string.h>
#include <stdlib.h>

#define MAXBYTES2CAPTURE 2048

void processPacket(u_char *arg, const struct pcap_pkthdr* pkthdr, const u_char * packet)
{
    int i=0, *counter = (int *)arg;
    printf("Packet Count: %d\n", ++(*counter));
    printf("Received Packet Size: %d\n", pkthdr->len);
    printf("Payload:\n");
    for (i=0; i<pkthdr->len; i++) {
        if (isprint(packet[i]))
            printf("%c ", packet[i]);
        else
            printf(". ");
        if( (i%16 == 0 && i!=0) || i==pkthdr->len-1 )
            printf("\n");
    }
    return;
}

int main()
{
    int i=0, count=0;
    pcap_t *descr = NULL;
    char errbuf[PCAP_ERRBUF_SIZE], *device=NULL;
    memset(errbuf,0,PCAP_ERRBUF_SIZE);

    /* Get the name of the first device suitable for capture */
    device = pcap_lookupdev(errbuf);
    printf("Opening device %s\n", device);

    /* Open device in promiscuous mode */
    descr = pcap_open_live(device, MAXBYTES2CAPTURE, 1, 512, errbuf);

    /* Loop forever & call processPacket() for every received packet */
    pcap_loop(descr, -1, processPacket, (u_char *)&count);

    return 0;
}

```

#### C. Costruzione di un ARP Sniffer Live con Filtri BPF

```c
/* Simple ARP Sniffer. To compile: gcc arpsniffer.c -o arpsniff -lpcap */
/* Run as root! */
#include <pcap.h>
#include <stdlib.h>
#include <string.h>

/* ARP Header, (assuming Ethernet+IPv4) */
#define ARP_REQUEST 1
#define ARP_REPLY 2
typedef struct arphdr {
    u_int16_t htype; /* Hardware Type */
    u_int16_t ptype; /* Protocol Type */
    u_char hlen;     /* Hardware Address Length */
    u_char plen;     /* Protocol Address Length */
    u_int16_t oper;  /* Operation Code */
    u_char sha[6];   /* Sender hardware address */
    u_char spa[4];   /* Sender IP address */
    u_char tha[6];   /* Target hardware address */
    u_char tpa[4];   /* Target IP address */
} arphdr_t;

#define MAXBYTES2CAPTURE 2048

int main(int argc, char *argv[])
{
    int i=0;
    bpf_u_int32 netaddr=0, mask=0; /* To Store network address and netmask */
    struct bpf_program filter;     /* Place to store the BPF filter program */
    char errbuf[PCAP_ERRBUF_SIZE]; /* Error buffer */
    pcap_t *descr = NULL;          /* Network interface handler */
    struct pcap_pkthdr pkthdr;     /* Packet information (timestamp,size...) */
    const unsigned char *packet=NULL; /* Received raw data */
    arphdr_t *arpheader = NULL;    /* Pointer to the ARP header */

    memset(errbuf,0,PCAP_ERRBUF_SIZE);

    if (argc != 2){
        printf("USAGE: arpsniffer <interface>\n");
        exit(1);
    }

    /* Open network device for packet capture */
    descr = pcap_open_live(argv[1], MAXBYTES2CAPTURE, 0, 512, errbuf);

    /* Look up info from the capture device. */
    pcap_lookupnet(argv[1], &netaddr, &mask, errbuf);

    /* Compiles the filter expression into a BPF filter program */
    pcap_compile(descr, &filter, "arp", 1, mask);

    /* Load the filter program into the packet capture device. */
    pcap_setfilter(descr, &filter);

    while (1){
        packet = pcap_next(descr, &pkthdr); /* Get one packet */
        arpheader = (struct arphdr *)(packet+14); /* Point to the ARP header */

        printf("\n\nReceived Packet Size: %d bytes\n", pkthdr.len);
        printf("Hardware type: %s\n", (ntohs(arpheader->htype) == 1) ? "Ethernet" : "Unknown");
        printf("Protocol type: %s\n", (ntohs(arpheader->ptype) == 0x0800) ? "IPv4" : "Unknown");
        printf("Operation: %s\n", (ntohs(arpheader->oper) == ARP_REQUEST)? "ARP Request" : "ARP Reply");

        /* If is Ethernet and IPv4, print packet contents */
        if (ntohs(arpheader->htype) == 1 && ntohs(arpheader->ptype) == 0x0800){
            printf("Sender MAC: ");
            for(i=0; i<6; i++) printf("%02X:", arpheader->sha[i]);
            printf("\nSender IP: ");
            for(i=0; i<4; i++) printf("%d.", arpheader->spa[i]);
            printf("\nTarget MAC: ");
            for(i=0; i<6; i++) printf("%02X:", arpheader->tha[i]);
            printf("\nTarget IP: ");
            for(i=0; i<4; i++) printf("%d.", arpheader->tpa[i]);
            printf("\n");
        }
    }
    return 0;
}

```

#### D. TCP RST Attack Tool

```c
/* Simple TCP RST Attack tool */
/* To compile: gcc tcp_resetter.c -o tcpresetter -lpcap */

#define _BSD_SOURCE
#include <netinet/ip.h>  /* Internet Protocol */
#define __FAVOR_BSD
#include <netinet/tcp.h> /* Transmission Control Protocol */
#include <pcap.h>        /* Libpcap */
#include <string.h>      /* String operations */
#include <stdlib.h>      /* Standard library definitions */

#define MAXBYTES2CAPTURE 2048

int TCP_RST_send(u_int32_t seq, u_int32_t ack, unsigned long src_ip, unsigned long dst_ip, u_int16_t src_prt, u_int16_t dst_prt, u_int16_t win)
{
    /* This function crafts a custom TCP/IP packet with the RST flag set
       and sends it through a raw socket. Check
       http://www.programming-pcap.aldabaknocking.com/ for the full example. */
    return 0;
}

int main(int argc, char *argv[])
{
    int count=0;
    bpf_u_int32 netaddr=0, mask=0;
    pcap_t *descr = NULL;
    struct bpf_program filter;
    struct ip *iphdr = NULL;
    struct tcphdr *tcphdr = NULL;
    struct pcap_pkthdr pkthdr;
    const unsigned char *packet = NULL;
    char errbuf[PCAP_ERRBUF_SIZE];
    memset(errbuf,0,PCAP_ERRBUF_SIZE);

    if (argc != 2){
        printf("USAGE: tcpresetter <interface>\n");
        exit(1);
    }

    /* Open network device for packet capture */
    descr = pcap_open_live(argv[1], MAXBYTES2CAPTURE, 1, 512, errbuf);

    /* Look up info from the capture device */
    pcap_lookupnet(argv[1], &netaddr, &mask, errbuf);

    /* Compiles the filter expression: Packets with ACK or PSH-ACK flags set */
    pcap_compile(descr, &filter, "(tcp[13] == 0x10) or (tcp[13] == 0x18)", 1, mask);

    /* Load the filter program into the packet capture device. */
    pcap_setfilter(descr, &filter);

    while (1){
        packet = pcap_next(descr, &pkthdr);
        iphdr = (struct ip *)(packet+14); /* Assuming is Ethernet! */
        tcphdr = (struct tcphdr *)(packet+14+20); /* Assuming no IP options! */

        printf("\nReceived Packet %d:\n", ++count);
        printf("ACK: %u\n", ntohl(tcphdr->th_ack));
        printf("SEQ: %u\n", ntohl(tcphdr->th_seq));
        printf("DST IP: %s\n", inet_ntoa(iphdr->ip_dst));
        printf("SRC IP: %s\n", inet_ntoa(iphdr->ip_src));
        printf("SRC PORT: %d\n", ntohs(tcphdr->th_sport));
        printf("DST PORT: %d\n", ntohs(tcphdr->th_dport));

        TCP_RST_send(ntohl(tcphdr->th_ack), 0, iphdr->ip_dst.s_addr, iphdr->ip_src.s_addr, tcphdr->th_dport, tcphdr->th_sport, 0);
    }
    return 0;
}

```

---

## Deliverable 2: The Interactive HTML Quiz

```html
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz: Programmazione con Libpcap e Packet Capture</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; background-color: #f4f6f9; }
        h1 { text-align: center; color: #2c3e50; }
        .question-card { background: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .question-title { font-weight: bold; margin-bottom: 15px; font-size: 1.1em; color: #34495e; }
        .options-list { list-style-type: none; padding: 0; }
        .option-item { margin-bottom: 10px; background: #f8f9fa; border-radius: 5px; border: 1px solid #e9ecef; transition: background 0.2s; }
        .option-item:hover { background: #e9ecef; }
        label { cursor: pointer; display: flex; align-items: baseline; padding: 10px; }
        input[type="radio"] { margin-right: 10px; }
        .feedback { display: none; margin-top: 15px; padding: 15px; border-radius: 5px; font-size: 0.95em; line-height: 1.5; }
        .feedback.correct { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .feedback.incorrect { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .submit-btn { background-color: #007bff; color: white; border: none; padding: 15px 25px; font-size: 1.2em; border-radius: 5px; cursor: pointer; display: block; width: 100%; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,123,255,0.2); }
        .submit-btn:hover { background-color: #0056b3; }
        .explanation-title { font-weight: bold; margin-bottom: 5px; }
        .score-display { text-align: center; font-size: 1.5em; font-weight: bold; margin-top: 30px; display: none; padding: 20px; background: #ffffff; border: 1px solid #dee2e6; border-radius: 8px; color: #2c3e50; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
</head>
<body>

    <h1>Quiz Interattivo: Libpcap</h1>
    <form id="quizForm">
        <div id="questions-container"></div>
        <button type="button" class="submit-btn" onclick="submitQuiz()">Invia Risposte</button>
    </form>
    <div id="scoreDisplay" class="score-display"></div>

    <script>
        const quizData = [
            {
                q: "In che anno è stata creata la libreria libpcap?",
                options: ["1989", "1994", "1999", "2002"],
                ans: 1,
                explanation: "Libpcap è stata creata nel 1994 dai ricercatori del Lawrence Berkeley National Laboratory[cite: 19]."
            },
            {
                q: "Qual è il gruppo che attualmente si occupa della manutenzione di libpcap?",
                options: ["L'Università della California a Berkeley", "Il gruppo Nmap", "Il Tcpdump Group", "La fondazione GNU"],
                ans: 2,
                explanation: "Oggi, libpcap è mantenuta ed aggiornata dal Tcpdump Group[cite: 19]."
            },
            {
                q: "Quale stringa di comando esegue correttamente la compilazione del file 'readfile.c' in ambiente Linux utilizzando libpcap?",
                options: ["gcc readfile.c -o readfile", "gcc readfile.c -lpcap -o readfile", "make readfile.c libpcap", "gcc readfile.c -l pcap -o pcap"],
                ans: 1,
                explanation: "Il comando corretto per compilare il codice in Linux con le librerie pcap è: gcc readfile.c -lpcap -o readfile[cite: 17]."
            },
            {
                q: "Quale utilità a riga di comando viene citata per creare dei file packet trace (es. file .dump)?",
                options: ["Wireshark", "dsniff", "tcpdump", "ettercap"],
                ans: 2,
                explanation: "Viene suggerito l'uso di 'tcpdump' per creare un nuovo packet trace con il comando 'sudo tcpdump -w filename.dump'[cite: 17]."
            },
            {
                q: "A quale valore intero è predefinito il parametro 'PCAP_ERRBUF_SIZE' all'interno della libreria?",
                options: ["64", "128", "256", "512"],
                ans: 2,
                explanation: "Il parametro PCAP_ERRBUF_SIZE è attualmente definito come 256 byte[cite: 20]."
            },
            {
                q: "Quale funzione restituisce un puntatore alla stringa contenente il nome del primo dispositivo di rete adatto alla cattura?",
                options: ["pcap_lookupdev()", "pcap_findalldevs()", "pcap_open_live()", "pcap_get_device()"],
                ans: 0,
                explanation: "La funzione char *pcap_lookupdev(char *errbuf) restituisce il nome del primo dispositivo di rete adatto per intercettare i pacchetti[cite: 19]."
            },
            {
                q: "Nella funzione 'pcap_open_live()', qual è lo scopo del parametro 'snaplen'?",
                options: ["Gestire il timeout in caso di inattività di cattura", "Definire la modalità promiscua", "Indicare il numero massimo di byte da catturare per pacchetto", "Impostare l'offset del livello datalink"],
                ans: 2,
                explanation: "Il parametro 'snaplen' indica il numero massimo di byte da catturare; un valore di 65535 è raccomandato per mantenere pacchetti completi di qualsiasi rete[cite: 20]."
            },
            {
                q: "Quanto imposta 'tcpdump' come valore di default per il timeout 'to_ms' in pcap_open_live() per permettere al kernel di copiare le informazioni?",
                options: ["0 ms", "10 ms", "512 ms", "1000 ms"],
                ans: 3,
                explanation: "Lo strumento tcpdump utilizza di default un valore di 1000 per il timeout to_ms[cite: 20]."
            },
            {
                q: "Se la funzione 'pcap_loop()' viene richiamata passando un valore negativo al parametro 'cnt', cosa succede?",
                options: ["Restituisce un errore di compilazione", "Esegue la cattura iterativa all'infinito e ritorna solo in caso di errore", "Raccoglie pacchetti finchè non scade il timeout to_ms", "Intercetta i pacchetti ma omette i loro payload"],
                ans: 1,
                explanation: "Un valore negativo per cnt causa il ritorno della funzione pcap_loop() solamente in presenza di un errore[cite: 21]."
            },
            {
                q: "All'interno della struct 'pcap_pkthdr', cosa indica specificatamente il parametro 'caplen'?",
                options: ["L'orario di cattura in millisecondi", "La lunghezza totale nativa del frame Ethernet", "Il numero di byte che sono stati effettivamente salvati", "L'offset prima dell'header IPv4"],
                ans: 2,
                explanation: "Il membro 'caplen' della struttura indica il numero di byte memorizzati. Questo valore è normalmente uguale a 'len' a meno che la dimensione reale del pacchetto superi lo 'snaplen'[cite: 20, 21]."
            },
            {
                q: "A quale funzione di callback devono essere inviati i pacchetti elaborati da 'pcap_loop()'?",
                options: ["pcap_handler callback", "pcap_setfilter()", "pcap_next()", "pcap_compile()"],
                ans: 0,
                explanation: "pcap_loop non restituisce direttamente i pacchetti al main; al contrario, chiama iterativamente una funzione definita dall'utente (di tipo pcap_handler callback) ad ogni pacchetto catturato[cite: 21]."
            },
            {
                q: "Se l'analisi di pcap_datalink() restituisce una topologia di tipo 'DLT_IEEE802_11', qual è l'offset in byte che il parser deve saltare per arrivare ai livelli successivi?",
                options: ["4", "14", "21", "22"],
                ans: 3,
                explanation: "In base alla Tabella 1, il Data Link Type per il Wi-Fi (DLT_IEEE802_11) ha un Offset pari a 22 byte[cite: 23]."
            },
            {
                q: "Qual è il valore standard del campo 'ethertype' per definire un protocollo IPv4?",
                options: ["0x0806", "0x0800", "0x86DD", "0x8864"],
                ans: 1,
                explanation: "Secondo la Tabella 2, il valore esadecimale dell'ethertype per incapsulare il protocollo Internet Protocol Version 4 (IPv4) è 0x0800[cite: 23]."
            },
            {
                q: "Qual è il valore standard del campo 'ethertype' indicante una risoluzione ARP?",
                options: ["0x0800", "0x86DD", "0x8035", "0x0806"],
                ans: 3,
                explanation: "La Tabella 2 indica che il valore ethertype per l'Address Resolution Protocol (ARP) è 0x0806[cite: 23]."
            },
            {
                q: "Nel Transport Layer Protocol, a quale valore esadecimale corrisponde il protocollo TCP?",
                options: ["0x01", "0x06", "0x11", "0x3A"],
                ans: 1,
                explanation: "Il Transmission Control Protocol (TCP), definito all'interno della RFC 793, ha il valore esadecimale 0x06 (Tabella 3)[cite: 23]."
            },
            {
                q: "Perché è imperativo utilizzare una funzione come 'ntohs()' prima di processare il campo ethertype ricevuto dalla libreria?",
                options: ["Per decrittare i pacchetti in caso di SSL", "Per evitare un kernel panic", "Per convertire il valore dal byte order di rete al byte order nativo dell'host locale", "Per estrapolare l'indirizzo MAC di destinazione in testo ASCII"],
                ans: 2,
                explanation: "Quando si processano tali valori, occorre ricordare che vengono ricevuti nel formato di rete (network byte order), ed è necessario convertirli nello schema dell'host richiamando la funzione ntohs()[cite: 23]."
            },
            {
                q: "Quale comando converte/compila un'espressione di filtro stringa (BPF) affinché il kernel la comprenda nativamente?",
                options: ["pcap_setfilter", "pcap_lookupnet", "pcap_compile", "pcap_loop"],
                ans: 2,
                explanation: "La funzione int pcap_compile() compila un'espressione testuale in un codice o programma BPF in modo che il kernel sia capace di comprenderlo[cite: 25]."
            },
            {
                q: "Se voglio installare un programma filtro BPF appena compilato sul dispositivo di acquisizione dei pacchetti, quale comando devo usare?",
                options: ["pcap_dispatch", "pcap_setfilter", "bpf_program", "pcap_next"],
                ans: 1,
                explanation: "La funzione int pcap_setfilter() si occupa di installare e caricare attivamente il programma BPF all'interno del kernel per l'interfaccia prescelta[cite: 25]."
            },
            {
                q: "Cosa isola il seguente filtro BPF: 'tcp[13] == 0x02 and (dst port 22 or dst port 23)'?",
                options: ["I pacchetti UDP destinati alle porte Telnet o SSH", "Tutti i pacchetti senza flag SYN destinati sulla porta 80", "Pacchetti TCP con flag SYN attivati e come porta di destinazione SSH (22) o Telnet (23)", "Pacchetti che contengono nel payload le parole '22' o '23'"],
                ans: 2,
                explanation: "L'esempio mostra che questo filtro BPF seleziona i pacchetti TCP aventi il flag SYN attivato (valore all'offset 13 dell'header TCP corrispondente a 0x02) e con destinazione le porte 22 o 23[cite: 25]."
            },
            {
                q: "Secondo le istruzioni relative ai pacchetti malformati, quanti byte di lunghezza deve avere esplicitamente un pacchetto ARP valido per evitare crash durante l'analisi in ambiente Ethernet?",
                options: ["20 bytes", "34 bytes", "42 bytes", "64 bytes"],
                ans: 2,
                explanation: "Quando si riceve un pacchetto ARP nativo all'interno di una rete Ethernet, i pacchetti con lunghezze differenti rispetto alla somma degli header (14 byte di DLT e 28 byte di ARP, per un totale pari a 42 byte) devono essere scartati precauzionalmente per scongiurare memory faults[cite: 23, 24]."
            }
        ];

        const container = document.getElementById("questions-container");

        quizData.forEach((item, index) => {
            const card = document.createElement("div");
            card.className = "question-card";
            
            let optionsHtml = item.options.map((opt, i) => `
                <li class="option-item">
                    <label>
                        <input type="radio" name="q${index}" value="${i}">
                        ${opt}
                    </label>
                </li>
            `).join('');

            card.innerHTML = `
                <div class="question-title">${index + 1}. ${item.q}</div>
                <ul class="options-list">${optionsHtml}</ul>
                <div id="feedback-${index}" class="feedback">
                    <div class="explanation-title" id="feedback-title-${index}"></div>
                    <div id="feedback-text-${index}"></div>
                </div>
            `;
            container.appendChild(card);
        });

        function submitQuiz() {
            let score = 0;
            quizData.forEach((item, index) => {
                const selected = document.querySelector(`input[name="q${index}"]:checked`);
                const feedbackDiv = document.getElementById(`feedback-${index}`);
                const feedbackTitle = document.getElementById(`feedback-title-${index}`);
                const feedbackText = document.getElementById(`feedback-text-${index}`);
                
                feedbackDiv.style.display = "block";
                
                if (selected && parseInt(selected.value) === item.ans) {
                    score++;
                    feedbackDiv.className = "feedback correct";
                    feedbackTitle.innerText = "Corretto!";
                } else {
                    feedbackDiv.className = "feedback incorrect";
                    feedbackTitle.innerText = "Sbagliato.";
                }
                feedbackText.innerHTML = `<strong>Spiegazione:</strong> ${item.explanation}`;
            });

            const scoreDisplay = document.getElementById("scoreDisplay");
            scoreDisplay.style.display = "block";
            scoreDisplay.innerText = `Punteggio totale: ${score} su ${quizData.length}!`;
            scoreDisplay.scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>

```