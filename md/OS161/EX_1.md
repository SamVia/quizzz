## Master Cheat Sheet: Esercizi Risolti su OS161

**Nota Generale:** Il documento include volutamente commenti relativi a correzioni di esami precedenti e indicazioni di errori frequenti commessi dagli studenti.

---

### Practical Exercises

#### Esercizio 1: Allineamento e Definizione delle Regioni di Memoria (`as_define_region`)
Questo esercizio analizza il funzionamento della funzione `as_define_region` nel file `dumbvm.c`.

**Parametri Ricevuti:**
* `as` (indirizzo spazio): `0x80048720` 
* `vaddr` (indirizzo virtuale): `0x412370` 
* `sz` (dimensione decimale): `4128` 

**Costanti di Sistema:**
* `PAGE_SIZE`: `4096` 
* `PAGE_FRAME`: `0xfffff000` 

**Codice Originale:**
```c
int as_define_region(struct addrspace *as, vaddr_t vaddr, size_t sz, int readable, int writeable, int executable) {
    size_t npages;
    /* Align the region. First, the base... */
    sz += vaddr & ~(vaddr_t)PAGE_FRAME;
    vaddr &= PAGE_FRAME;
    /* ...and now the length. */
    sz = (sz + PAGE_SIZE - 1) & PAGE_FRAME;
    npages = sz / PAGE_SIZE;
}
```
*[Nota: Il codice esatto riportato nel testo presenta alcune abbreviazioni di sintassi come `sz += vaddr & (vaddr t) PAGE FRAME;`, `vaddr & PAGE _FRAME;`, e `SZ = (sz + PAGE SIZE 1) & PAGE FRAME;` ma le operazioni matematiche svolte indicano il comportamento standard di allineamento.]*

**Calcolo Matematico Passo-Passo:**
* Conversione costanti iniziali: $4096 = 0\times1000$ , e $4128 = 0\times1020$.
* Calcolo del disallineamento della base (`sz`): $0\times1020 += 0\times412370$ & 0x000FFF.
* Nuova dimensione (`sz`): $z \leftarrow 0\times1020 + 0\times370 = 0\times1390$.
* Allineamento della base (`vaddr`): 0x412370 & 0xFFF000  $\rightarrow$ vaddr $\leftarrow$ $0\times412000$.
* Allineamento della lunghezza (`sz`): sz $\leftarrow$ ($0\times1390 + 0xEE$) & 0xFFF000 $= 0\times2000$.
* Calcolo pagine necessarie (`npages`): npages < 0x2000 / 0x1000 = 2.

**Caso Limite - Frammentazione Interna:**
* **Domanda:** Se `sz` fosse inferiore a una singola pagina (es. 4090), Ã¨ possibile ottenere `npages` = 2? 
* **Risposta:** SÃ¬, Ã¨ possibile. Il segmento viene allineato a un multiplo di pagina sia all'inizio che alla fine. In questo caso si verifica frammentazione interna sia sulla prima che sull'ultima pagina.
* **Trace Matematico del Caso Limite:** Con 4090 = 0xFFA , `sz` assumerebbe inizialmente il valore $0xFFA + 0\times370 = 0\times126A$ , e successivamente verrebbe arrotondato a $0\times2000$ (richiedendo quindi 2 pagine).

---

#### Esercizio 2: Allocazione Memoria Fisica (`getfreeppages`)
Analisi della funzione `getfreeppages` per l'allocazione di `npages` pagine contigue di memoria fisica.

**Analisi della Politica di Allocazione Originale:**
* **Quale politica implementa la funzione originale?** Nessuna tra best-fit, worst-fit o first-fit.
* **PerchÃ© non Ã¨ First-fit:** Le iterazioni del ciclo `for` non si fermano alla prima soluzione trovata.
* **PerchÃ© non Ã¨ Best-fit o Worst-fit:** Non vi Ã¨ alcuna ricerca o gestione di una variabile di minimo o massimo.
* **Comportamento reale ("Last-fit"):** La soluzione ritornata Ã¨ semplicemente l'ultima tra quelle valide trovate nell'iterazione. (Errore frequente: confonderla con la first-fit ).

**ComplessitÃ  e Design dell'Algoritmo:**
* L'algoritmo di base opera in tempo `O(nRamFrames)` e controlla la lunghezza su tutte le caselle intermedie di un intervallo.
* Per la *Worst-fit*, basterebbe aggiungere la gestione di una variabile `max` ad ogni iterazione.
* Per la *Best-fit*, il confronto con il minimo provvisorio deve avvenire **solo** al termine di un intervallo (es. controllando `i+1`).
* Sono accettabili soluzioni `O(nRamFrames*npages)` con doppia iterazione.
* **Soluzione non accettabile:** L'uso di un vettore aggiuntivo precaricato con le lunghezze degli intervalli, a causa dei costi di memoria e di aggiornamento costante ad ogni allocazione/deallocazione (vanificando i vantaggi della bitmap). Sposta semplicemente il problema senza risolverlo. Le risposte fornite "a parole" non sono valutate: serve codice in C.

**Codice Modificato per First-fit e Best-fit:** 

**Implementazione First-fit:** 
```c
/* Variante con uscita non strutturata */
if (i-first+1 >= np) {
    found = first;
    break;
}
```
*[In alternativa, variante con uscita strutturata: aggiungere `&& found<0` alla condizione del ciclo `for`: `for (i=0, first=found=-1; i<nRamFrames && found<0; i++)`] *

**Implementazione Best-fit:** 
```c
int min;
/* se Ã¨ l'ultimo frame di un intervallo */
if (i==nRamFrames-1 || !freeRamFrames[i+1]) {
    /* se la dimensione va bene */
    if (i-first+1 >= np) {
        /* se batte il minimo provvisorio */
        if (found<0 || i-first+1 < min) {
            found = first;
            min = i-first+1;
        }
    }
}
```
*[Nota: Le condizioni precedenti possono essere combinate in un unico `if` con operatore AND]* 

---

#### Esercizio 3: Gestione delle System Call (`syscall()`)
* **La variabile `callno`:** Rappresenta il selettore della system call da effettuare, e viene usato in uno switch (`case`) all'interno della `syscall()`. Il valore gli viene assegnato (`tf->tf_v0`) dalla routine che gestisce la trap e chiama `mips_trap->syscall`.
* **Gestione del valore di ritorno e di stato (Trapframe registers):** Le istruzioni alla fine della funzione `syscall()` gestiscono lo stato di ritorno e gli errori modificando i registri del processore (salvati nel trapframe).
    * Il registro `v0` riceve il valore di ritorno o, in caso di errore, il codice di errore.
    * Il registro `a3` indica l'esito: successo (0) o errore (1).

**Flusso Logico di Ritorno:** 
```c
if (err) {
    tf->tf_v0 = err;
    /* In a3 viene ritornato lo stato errore (1) */
    tf->tf_a3 = 1;
} else {
    /* In v0 viene posto il valore di ritorno della system call */
    tf->tf_v0 = retval;
    /* In a3 viene ritornato lo stato successo (0) */
    tf->tf_a3 = 0;
}
```

---

#### Esercizio 4: Gestione dei Lock in OS161
* **Definizione di Owner (Proprietario):** Il thread "owner" del lock **non** Ã¨ quello che lo ha creato. L'owner Ã¨ esclusivamente il thread che ha chiamato `lock_acquire` sul lock specifico e che **ha effettivamente superato l'attesa** (acquisendolo), non un thread ancora in attesa.

**Correzione dei Bug nel Codice di Sincronizzazione:** 

**Bug 1: `lock_do_i_hold`** 
* **Errore:** La funzione esegue un `return true;` senza prima rilasciare lo spinlock.
* **Correzione:** Utilizzare una variabile booleana d'appoggio `ret`.
```c
bool lock_do_i_hold(struct lock *lock) {
    bool ret;
    spinlock_acquire(&lock->lk_lock);
    ret = lock->lk_owner == curthread;
    spinlock_release(&lock->lk_lock);
    return ret;
}
```
**

**Bug 2: `lock_release`** 
* **Errore (Deadlock):** La funzione acquisisce lo spinlock **prima** di chiamare la funzione `lock_do_i_hold`, la quale tenterÃ  a sua volta di acquisire lo stesso identico spinlock causando un deadlock.
* **Correzione:** Spostare l'istruzione `spinlock_acquire` **dopo** la chiamata alla funzione (e alla macro `KASSERT`) `lock_do_i_hold`.

---

#### Esercizio 5: Mutua Esclusione e Semafori Multi-core
* **Mutua esclusione hardware (Interrupt):** In un sistema multi-core, non Ã¨ possibile garantire la mutua esclusione semplicemente disabilitando/riabilitando gli interrupt. Disabilitare gli interrupt agisce solo sulla CPU corrente e non impedisce ai thread o processi in esecuzione sulle altre CPU di procedere. Anche disabilitandoli globalmente sulle altre CPU, alcuni thread potrebbero giÃ  essere in esecuzione. La disabilitazione Ã¨ adatta solo ai sistemi single core.

**Analisi del Codice dei Semafori (P e V):** 

**Codice Originale:**
```c
void P(struct semaphore *sem) {
    spinlock_acquire(&sem->sem_lock);
    while (sem->sem_count == 0) {
        wchan_sleep(sem->sem_wchan, &sem->sem_lock);
    }
    sem->sem_count--;
    spinlock_release(&sem->sem_lock);
}

void V(struct semaphore *sem) {
    spinlock_acquire(&sem->sem_lock);
    sem->sem_count++;
    KASSERT(sem->sem_count > 0);
    wchan_wakeone(sem->sem_wchan, &sem->sem_lock);
    spinlock_release(&sem->sem_lock);
}
```
**

**Dettagli Architetturali e Logici:**
1.  **A cosa serve lo spinlock?** Lo spinlock Ã¨ vitale per usare i wait-channel (`wchan_sleep` e `wchan_wakeone`) e garantisce la mutua esclusione sulla condizione protetta dal semaforo (`sem->sem_count`). (Risposte puramente teoriche su cosa sia uno spinlock non sono sufficienti ).
2.  **PerchÃ© la funzione P usa un ciclo `while` invece di un `if`?** A causa della semantica **Mesa** del risveglio (in contrasto con la semantica Hoare). Non garantisce la cronologia stretta per l'esecuzione in stato `RUN` dei thread. Non esistono "risvegli spuri"; piuttosto, tra il risveglio effettuato da `V` e l'effettiva esecuzione di `P`, altri thread potrebbero alterare nuovamente la variabile di stato (`sem->sem_count`) riportandola a zero. Il risveglio rimette il thread in coda `READY`, non in `RUN` diretto.
3.  **PerchÃ© `wchan_sleep` e `wchan_wakeone` ricevono lo spinlock come parametro?**
    * `wchan_sleep`: Ha l'obbligo di rilasciare lo spinlock prima di mettere in attesa ("wait") il thread, e deve riacquisirlo subito prima di fare ritorno al chiamante.
    * `wchan_wakeone`: Non fa alcuna operazione sullo spinlock. In OS161 il parametro Ã¨ passato solo per ragioni di verifica interna (attraverso macro come `KASSERT`) per assicurare che il thread chiamante sia l'attuale owner dello spinlock per prevenire errori. (Versioni Unix/Linux della funzione non richiedono tale parametro ).
    * **Errore critico da evitare:** Lo spinlock non serve per garantire mutua esclusione dentro le funzioni `wchan_sleep`/`wchan_wakeone`, ma per verificare le precondizioni del chiamante. Ancora peggio Ã¨ pensare che un thread si metta in attesa sullo spinlock stesso (lo spinlock si usa per la mutua esclusione rapida, non per il wait-signal).
4.  **Comportamento di Wakeone:** Ãˆ impossibile che `wchan_wakeone` risvegli piÃ¹ di un thread in attesa sulla `wchan_sleep`. Sveglia garantitamente un thread solo. Per risvegliare tutti i thread, si utilizza la funzione `wchan_wakeall`.
