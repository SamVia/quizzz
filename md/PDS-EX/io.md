
# Cheat Sheet Master: Programmazione di Sistema - Gestione File System e I/O

---

## 1. Operazioni di Base sul File System

In un file system che permette l'accesso concorrente di più processi allo stesso file, il Sistema Operativo (OS) deve svolgere operazioni specifiche per le chiamate di sistema `open()` e `close()`.

### La system call `open()`
La funzione `open()` riceve come parametro il nome del file, lo apre nella modalità richiesta e restituisce il file descriptor (oppure handle/puntatore, a seconda dell'OS). I passaggi eseguiti dall'OS sono:
* Il nome del file viene cercato utilizzando la struttura dati basata sui direttori (situata in memoria e/o su disco).
* In caso di successo, la ricerca ritorna il File Control Block (FCB). Questo viene copiato nella *system-wide open-file table* (se non era già presente, altrimenti si usa quello esistente).
* Viene creata una nuova entry nella *per-process open-file table* (che fa riferimento al FCB presente nella tabella system-wide).
* Viene ritornato il puntatore/handle o indice (file descriptor) di questa entry.

### La system call `close()`
La funzione `close()` chiude il file eliminando le entry relative nelle tabelle dei file aperti, quando queste non sono più utili. I passaggi sono:
* Viene cancellata la entry corrispondente nella *per-process open-file table*.
* Viene decrementato il contatore dei riferimenti nella *system-wide open-file table*.
* Se il contatore dei riferimenti diventa 0, l'entry viene cancellata anche dalla tabella system-wide.

---

## 2. Strutture Dati per la Gestione dei File (`read` e `write`)

Per realizzare operazioni di `read()` e/o `write()`, il sistema deve accedere a due tabelle fondamentali che contengono in memoria tutte le informazioni per gestire correttamente i file. Entrambe sono necessarie perché un file può essere aperto contemporaneamente più volte, in modalità diverse, sia da thread dello stesso processo sia da processi differenti.

### Per-Process Open-File Table
* **Contenuto:** Include informazioni specifiche del processo, come il puntatore alla posizione di lettura/scrittura nel file e la modalità di accesso (es. sola lettura, scrittura).

### System-Wide Open-File Table
* **Contenuto:** Contiene informazioni condivise (comuni), tra cui una copia del File Control Block (FCB) e le eventuali primitive per gestire e sincronizzare gli accessi condivisi.
* **Utilizzo per I/O:** Vi si accede, tra le altre cose, per effettuare la conversione dall'indirizzo logico all'interno del file all'indirizzo fisico (numero di blocco e offset nel blocco).

---

## 3. Gestione della Memoria e Buffer di Kernel

Quando i dati vengono trasferiti tra disco e memoria utente (es. tramite `read(fd, addr, size)`), spesso transitano prima per un buffer di kernel. 

### Vantaggi del Buffer di Kernel
* **Disaccoppiamento:** Disaccoppia il lavoro sulla memoria USER rispetto all'accesso a disco. 
* **Swapping/Paginazione Ottimizzata:** Permette di fare swap out di un intero processo utente in attesa di I/O (o della pagina coinvolta), poiché il buffer user non viene "bloccato" durante l'attesa fisica del disco.
* **Funzione di Cache:** Il buffer kernel può essere riempito in anticipo per evitare che il processo vada in stato di attesa di I/O.
* **Attenzione ai Privilegi:** Il vantaggio **NON** è quello di evitare al processo user di fare l'I/O. Il processo USER non ne ha comunque i privilegi. L'I/O viene sempre effettuato da una system call tramite un driver di KERNEL, che lavorerà sul buffer kernel anziché bloccare la memoria utente.

### Indipendenza dalla Paginazione
In un sistema con paginazione, i parametri di una system call (come la `read()`) non sono vincolati dall'architettura hardware sottostante:
* Il parametro `size` è arbitrario, poiché la `read` è una funzione a livello user e non ha dipendenza diretta dalle strategie di paginazione.
* L'indirizzo di partenza `addr` non è necessariamente allineato a un inizio di pagina.

---

## 4. Tecniche di Buffering Avanzate: Doppio Buffer e Pipelining

### Doppio Buffer tra Kernel e User
* **Funzionamento:** Realizza una concorrenza di tipo pipelining. Si può trasferire da memoria kernel a memoria user e, contemporaneamente, da disco a memoria kernel.
* Mentre un buffer (kernel) è coinvolto nel trasferimento da disco, l'altro buffer (user), se caricato in precedenza, trasferisce dati alla destinazione. Dopo ogni operazione, i ruoli dei buffer si scambiano.

### Doppio Buffer di Kernel (Solo Kernel)
* **Funzionamento:** Mentre un buffer viene scritto, l'altro (riempito in precedenza) può essere letto in parallelo. 
* **Vantaggio:** Permette il pipelining. Con un buffer singolo, chi scrive o chi legge deve obbligatoriamente attendere il completamento dell'operazione dell'altro attore.

---

## 5. Sincronizzazione: I/O Sincrono vs Asincrono

Le operazioni di I/O possono essere classificate in base a come il processo attende i dati.

* **I/O Bloccante (Sincrono):** Sono equivalenti. Il processo che richiede l'I/O ne attende il completamento, mettendosi in stato di *wait*.
* **I/O Non Bloccante:** Permette al processo di proseguire immediatamente.
* **I/O Asincrono:** È di fatto non bloccante, ma aggiunge tecniche per gestire il completamento successivo dell'I/O. Tali tecniche sono:
    1.  Funzioni di wait (dipendenti dall'OS) per attendere l'I/O al momento del bisogno.
    2.  Funzioni di tipo "callback" (scritte dall'utente), richiamate in modo automatico dal sistema al completamento dell'I/O.
* **Vantaggio dell'Asincrono:** Concorrenza. Il processo può eseguire altre istruzioni (non dipendenti dai dati in transito) mentre l'I/O è in corso.
* **Uso dei dati:** Il processo non può utilizzare i dati coinvolti durante l'I/O. Se ha bisogno di farlo, deve sincronizzarsi (e aspettare) tramite l'operazione di wait relativa a quell'I/O asincrono.

### Driver: Polling vs. Interrupt
* Realizzare una system call in modo sincrono o asincrono può essere fatto indipendentemente con driver che lavorano sia in polling che ad interrupt.
* Polling e interrupt sono modalità interne ai moduli del Kernel (driver) per gestire un dispositivo fisico, e sono trasparenti al processo user.
* Il polling risulta generalmente meno efficiente dell'interrupt (con rare eccezioni).

---

## 6. Accesso alla Memoria: DMA vs I/O Programmato

### Cos'è il "Cycle Stealing"
In un trasferimento Direct Memory Access (DMA), il "cycle stealing" è la sottrazione (con conseguente attesa per la CPU) di cicli di BUS alla CPU, mentre il DMA ha il controllo dei BUS per accedere alla RAM.

### Vantaggi del DMA
1.  I dati passano "direttamente" tra il dispositivo di I/O e la RAM senza transitare per la CPU (risparmiando un numero doppio di operazioni).
2.  Mentre avviene il trasferimento DMA, la CPU è libera di fare altro, aumentando il grado di multiprogrammazione.

---

## 7. Esercizi Pratici e Dimostrazioni Matematiche

### Esercizio A: Calcolo del Transito sul Bus Dati (Buffer Doppio vs Singolo)
**Scenario:** Si vuole leggere sequenzialmente un file da 200KB su disco usando il DMA. Quanti Byte passano complessivamente sul bus dati nei due casi (singolo e doppio buffer)? Il doppio buffer dimezza il numero di byte trasferiti? 

**Soluzione Step-by-Step:**
1.  Il doppio buffer **non** dimezza i byte trasferiti. Velocizza solo le operazioni tramite parallelismo. Il numero di byte gestiti è identico.
2.  **Passaggio 1 (Disco -> Buffer Kernel):** I dati passano una volta sul bus durante il trasferimento in DMA. Transito: $200\text{KB}$.
3.  **Passaggio 2 (Buffer Kernel -> Memoria User):** Questa è una copia RAM-RAM gestita dalla CPU (indirizzi diversi). I dati passano **due volte** sul bus: dalla RAM alla CPU (lettura), e dalla CPU alla RAM (scrittura). Transito: $2 * 200\text{KB}$.
4.  **Totale:** La formula finale del transito complessivo sul bus è:
    $$200\text{KB} + 2 * 200\text{KB} = 600\text{KB}$$ 

*Eccezione (Nota Hardware):* Se si utilizzasse un DMA controller di tipo *fetch-and-deposit*, la copia RAM-RAM potrebbe avvenire con un solo passaggio sul bus (in due cicli: uno di lettura, uno di scrittura), gestendo unitariamente le operazioni RAM-RAM.

### Esercizio B: Calcolo del Transito sul Bus Dati (DMA vs I/O Programmato)
**Scenario:** Immaginando di dover trasferire 40KB di dati da disco a memoria RAM, quanti Byte transitano sul bus dati della RAM nei due casi (trasferimento in DMA e IO programmato)? 

**Soluzione Step-by-Step:**
1.  **Caso DMA:** I dati passano direttamente tra I/O e RAM. Transito complessivo = $40\text{KB}$.
2.  **Caso I/O Programmato:** I dati devono forzatamente passare attraverso la CPU prima di arrivare alla RAM. Passano quindi due volte sul bus (I/O -> CPU, CPU -> RAM). Transito complessivo = $80\text{KB}$.
