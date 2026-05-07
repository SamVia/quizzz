# OS161 Master Cheat Sheet: Esercizi e Concetti Fondamentali

Questo cheat sheet riassume tutte le definizioni, i dettagli architetturali, i casi limite e il codice sorgente relativi agli esercizi pratici di OS161.

---

## 1. System Calls: `sys_exit` e `waitpid`

### Implementazione di `my_sys_exit`
* Il valore di `status` viene ricevuto come parametro dalla funzione.
* Nella funzione `syscall()`, la chiamata corrispondente al valore `SYS_exit` in `callno` deve passare il parametro attuale estraendolo dal trapframe.
* **Chiamata in `syscall()`:**
    ```c
    my_sys_exit((int)tf->tf_a0);
    ```
    

### Logica e Codice della `my_sys_exit(int status)`
La funzione `my_sys_exit` deve gestire correttamente il distacco del thread dal processo, il salvataggio dello stato e la sincronizzazione tramite condition variable.

```c
my_sys_exit (int status) { // lo stato viene ricevuto come parametro
    struct proc *p = curproc; // serve per poter accedere al processo dopo averlo
                              // staccato da curthread (curproc non piÃ¹ valido)
    p->p_status = status;     // salva lo stato di ritorno per la waitpid
    proc_remthread (curthread); // stacca il processo dal thread

    // segnala al processo che fa la waitpid (per usare cv_signal Ã¨
    // necessario possedere il relativo lock)
    lock_acquire (p->p_lock);
    cv_signal (p->p_cv, p->p_lock);
    lock_release (p->p_lock);

    // meglio NON fare as_destroy qui (lo farÃ  la proc_destroy)
    // il thread finisce qui (diventa zombie)
    thread_exit();
}
```


### Regole per la Sincronizzazione (`waitpid`)
* **Uso dei Lock:** Non Ã¨ possibile implementare la sincronizzazione di tipo wait-signal della `sys_waitpid` utilizzando un lock (facendo `lock_acquire` per l'attesa e `lock_release` da `sys_exit`). Un lock non puÃ² essere usato per questo scopo a causa del problema dell'ownership.
* **Scopo del Lock:** I lock servono unicamente per garantire la mutua esclusione.
* **Primitiva Corretta:** Per la logica wait-signal si devono utilizzare i semafori o le condition variable. Un lock associato a una condition variable serve solo per la mutua esclusione, non per gestire direttamente il wait-signal.

---

## 2. Gestione degli Argomenti al `main` (`argc`, `argv`)

* **NecessitÃ  di Copia:** In OS161 Ã¨ obbligatorio creare una copia degli argomenti del `main` (`argv` e `argc`) in quanto, originariamente, risiedono nella memoria kernel. AffinchÃ© il programma utente possa accedervi, devono essere portati nello spazio user.
* **Allocazione:** La copia va effettuata nella memoria user, specificamente all'inizio (indirizzi alti) dello user stack.
* **InaccessibilitÃ  dei Parametri Originali:** I parametri originali `nargs` e `args` ricevuti da funzioni come `cmd_prog` non sono sufficienti perchÃ© inaccessibili al processo user.
* **Isolamento dei Thread:** Anche qualora il processo potesse accedervi, tali dati si troverebbero nello stack di un altro thread (il kernel thread del menu). Ãˆ quindi obbligatorio duplicarli a meno di non disporre di meccanismi per garantirne l'accessibilitÃ  e la consistenza cross-thread. (Come riferimento, si veda la funzione `cmd_dispatch`, il cui vettore locale `args` viene passato a `cmd_prog`) .

---

## 3. Gestione dei File Descriptor (`open`, `close`)

* **Nessuna Ownership del Thread:** In OS161, non Ã¨ necessario associare il concetto di ownership di un file descriptor al singolo thread.
* **Chiusura Cross-Thread:** Un file puÃ² essere legittimamente chiuso da un thread diverso da quello che ha effettuato l'operazione di `open`.
* **Ownership Legata al Processo:** Il concetto di ownership esiste ma in modo indiretto ed Ã¨ legato al *processo*. Un file descriptor Ã¨ strettamente associato al contesto del processo e alla sua relativa tabella dei file aperti.

---

## 4. Spostamento Dati: `copyin`, `copyout` e `memmove`

* **Funzionamento `copyin` / `copyout`:** Queste funzioni spostano dati tra la memoria user e la memoria kernel. `copyin` ha come destinazione la memoria kernel, mentre `copyout` ha come destinazione la memoria user.
* **Gestione degli Errori:** A differenza di funzioni standard (come `memmove`), `copyin` e `copyout` gestiscono in modo consistente le eccezioni e gli errori derivanti da indirizzi o puntatori user non validi. Questo meccanismo impedisce al kernel di terminare in modo anomalo (es. crash o panic).
* **Sostituzione con `memmove`:** Sostituire una chiamata `copyin(src, dst, size);` con `memmove(dst, src, size);` Ã¨ lecito dal punto di vista dell'istruzione. Tuttavia, cosÃ¬ facendo, si perde la protezione fondamentale contro le eccezioni e gli errori di memoria.

---

## 5. Esercizi Pratici Svolti: Gestione I/O ed ELF Loading

### Errore Comune nella lettura con `VOP_READ`
* **Codice Errato:** Tentare di leggere l'header di un file ELF direttamente passando l'indirizzo di memoria a `VOP_READ` Ã¨ scorretto.
    ```c
    // ERRATO
    result = VOP_READ (v, &eh, sizeof(eh));
    ```
    
* **PerchÃ© Ã¨ errato:** La lettura richiede una strategia diversa. Bisogna prima definire l'operazione I/O da eseguire attraverso `uio_kinit` (per operazioni in memoria kernel) usando le struct `ku` e `iov`, e solo successivamente invocare `VOP_READ`.
* **Codice Corretto:**
    ```c
    uio_kinit(&iov, &ku, &eh, sizeof(eh), 0, UIO_READ);
    result = VOP_READ(v, &ku);
    ```
    

### Strutture Dati Coinvolte nell'I/O (`struct iovec` e `struct uio`)
* **Parametro `v`:** Puntatore al `vnode`, ovvero il file control block del file ELF da cui effettuare la lettura.
* **`struct iovec` (`iov`):** Contiene i dettagli della locazione di memoria. Memorizza il puntatore all'area di memoria destinazione (es. `&eh` in `load_elf`, o `vaddr` in `load_segment`) e la relativa dimensione (es. `sizeof(eh)` o `memsize`).
* **`struct uio` (`ku` / `u`):** Contiene l'intero contesto dell'operazione I/O. Include:
    * Il puntatore a uno o piÃ¹ `struct iovec`.
    * L'offset di partenza e il numero di byte da leggere nel file (`uio_resid`).
    * Le definizioni dello spazio virtuale (kernel/user) tramite flag, e il tipo di operazione R/W.

### Inizializzazione dello Spazio Kernel vs Spazio User
* **Memoria Kernel:** Prima di un'operazione di I/O, basta chiamare `uio_kinit` per predisporre e collegare automaticamente `uio` e `iovec`.
* **Memoria User:** Le due strutture vanno caricate e configurate in forma esplicita dal programmatore, in quanto per lo spazio utente non esiste una funzione equivalente a `uio_kinit`.

### Flag `uio_segflg` e `uio_space`
* **`UIO_SYSSPACE` vs `UIO_USER[I]SPACE`:**
    * Nella prima parte di `load_elf`, si usa `UIO_SYSSPACE` perchÃ© l'header del file ELF deve essere caricato in una variabile locale residente in memoria kernel.
    * Nella funzione `load_segment`, i segmenti veri e propri vengono acquisiti e scritti nelle partizioni di memoria user precedentemente allocate. Pertanto, si utilizza `UIO_USERISPACE` per il codice (istruzioni) e `UIO_USERSPACE` per i dati.
* **Configurazione di `uio_space` (Traduzione Indirizzi):**
    * Il campo `u->uio_space` fornisce le informazioni per la traduzione degli indirizzi da logici a fisici.
    * **In Spazio Kernel:** Viene impostato a `NULL`. La traduzione non necessita di strutture complesse e si risolve semplicemente sommando o sottraendo la costante `MIPS_KSEG0`.
    * **In Spazio User:** Viene impostato ad `as` (il puntatore alla struct `addrspace` del processo attivo). Questo Ã¨ fondamentale poichÃ© l'`addrspace` contiene tutte le mappature logico-fisiche necessarie per gestire l'accesso ai due segmenti e allo stack user.
