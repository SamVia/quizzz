## Master Cheat Sheet: OS161 Synchronization Primitives

### 1. Background & The Critical-Section Problem
* **Concurrent programming and synchronization:** Involves coordinating access to shared resources among multiple processes or threads.
* **Common Problems:**
    * Race conditions.
    * Deadlocks.
    * Resource starvation.
* **Solutions:** Synchronization primitives such as locks, barriers, and semaphores.
* **Critical Section Definition:** A part of a program that cannot be executed by more than one process or thread at a given time due to shared resources (like variables, tables, or files).
* **General Process Structure ($P_i$):**
    ```c
    do {
        entry section
        critical section
        exit section
        remainder section
    } while (true);
    ```
    

#### Requirements for a Valid Solution
A solution to the Critical-Section problem must meet three guarantees (assuming processes execute at a nonzero speed, with no assumptions about their relative speeds):
1.  **Mutual Exclusion:** If process $P_i$ is executing its critical section, no other processes can be executing their critical sections concurrently.
2.  **Progress:** If no process is in its critical section, and some processes wish to enter, the selection of the next process to enter cannot be postponed indefinitely.
3.  **Bounded Waiting:** A bound must exist on the number of times other processes are allowed to enter their critical sections after a process makes a request to enter and before that request is granted.

#### OS Kernel Handling
* **Preemptive Kernel:** Allows a process to be preempted even while running in kernel mode. Single core preemptive systems allow preemption in kernel mode.
* **Non-preemptive Kernel:** A process runs until it exits kernel mode, blocks, or voluntarily yields the CPU. This approach is essentially free of race conditions on a single core.
* **Multicore:** Parallel processing is always possible, regardless of preemption policies.

---

### 2. Peterson's Solution
* **Overview:** A software-based, two-process algorithmic description for solving the critical-section problem. It assumes load and store machine-language instructions are atomic (uninterruptible).
* **Variables:**
    * `int turn;` indicates whose turn it is to enter the critical section.
    * `boolean flag[2];` indicates if a process is ready to enter. `flag[i] = true` implies $P_i$ is ready.
* **Algorithm for Process $P_i$:**
    ```c
    while (true) {
        flag[i] = true;
        turn = j;
        while (flag[j] && turn == j)
            ; /* busy wait */
        /* critical section */
        flag[i] = false;
        /* remainder section */
    }
    ```
    
* **Proof of Concept:** Mutual exclusion is preserved because $P_i$ enters only if `flag[j] == false` or `turn == i`. Progress and bounded-waiting are also satisfied.
* **Modern Architecture Failure:** Petersonâ€™s solution is **not guaranteed to work** on modern systems. Processors and compilers may reorder operations that have no explicit dependencies to improve performance. In a multithreaded environment, instruction reordering can produce inconsistent results, allowing both processes to enter the critical section at the same time.

---

### 3. Hardware Support for Synchronization
Modern machines provide atomic (non-interruptible) hardware instructions to implement critical section code.

#### Uniprocessor Strategy
* Could simply disable interrupts so running code executes without preemption.
* **Limitation:** Generally too inefficient on multiprocessor systems; OS designs relying on this are not broadly scalable.

#### Memory Barriers
* **Memory Models:** Guarantees a computer architecture makes to programs.
    * *Strongly ordered:* Memory modification by one processor is immediately visible to all.
    * *Weakly ordered:* Memory modification might not be immediately visible.
* **Memory Barrier Instruction:** Forces any memory change to be propagated to all other processors, solving instruction reordering issues (like in Peterson's Solution).

#### Atomic Hardware Instructions
**1. test_and_set**
Executed atomically; returns the original value and sets the new value to `true`.
```c
boolean test_and_set (boolean *target) {
    boolean rv = *target;
    *target = true;
    return rv;
}
```


**2. compare_and_swap (CAS)**
Executed atomically; sets `value` to `new_value` only if the original `*value` matches the `expected` condition.
```c
int compare_and_swap(int *value, int expected, int new_value) {
    int temp = *value;
    if (*value == expected)
        *value = new_value;
    return temp;
}
```


**3. Atomic Variables**
Used for uninterrupted updates on basic data types (integers/booleans). Built using CAS.
```c
void increment(atomic int *v) {
    int temp;
    do {
        temp = *v;
    } while (temp != (compare_and_swap(v, temp, temp+1));
}
```


#### Bounded-waiting Mutual Exclusion with CAS
```c
while (true) {
    waiting[i] = true;
    key = 1;
    while (waiting[i] && key == 1)
        key = compare_and_swap(&lock, 0, 1);
    waiting[i] = false;
    /* critical section */
    j = (i + 1) % n;
    while ((j != i) && !waiting[j])
        j = (j + 1) % n;
    if (j == i)
        lock = 0;
    else
        waiting[j] = false;
    /* remainder section */
}
```


---

### 4. Mutex Locks & Spinlocks
* **Mutex Lock:** Protects a critical section via `acquire()` and `release()`. Uses a boolean variable indicating availability. Calls must be atomic.
* **Spinlocks:** A type of lock requiring "busy waiting" (spinning in a loop) if the lock is held.
    * **Pros:** Good for short delays, provides fast critical section entry.
    * **Implementations:**
        * **TAS (Test-and-Set) Spinlock:** Continuously writes to the bus, causing contention.
        * **TTAS (Test-and-Test-and-Set) Spinlock:** Optimized to loop on a local read (`test`), and only attempts write (`test-and-set`) when it appears free, reducing bus contention.

#### OS/161 Spinlock Implementation (`kern/thread/spinlock.c`)
OS/161 explicitly uses the TTAS strategy to reduce bus contention.
```c
spinlock_acquire(struct spinlock *splk) {
    ...
    while (1) {
        /* Read first before doing test-and-set */
        if (spinlock_data_get(&splk->splk_lock) != 0) {
            continue;
        }
        if (spinlock_data_testandset(&splk->splk_lock) != 0) {
            continue;
        }
        break;
    }
    ...
}
```


---

### 5. Semaphores
* **Definition:** An integer variable `S` providing sophisticated synchronization, accessed only via indivisible atomic operations `wait()` (or `P()`) and `signal()` (or `V()`).
* **Types:**
    * *Counting semaphore:* Unrestricted integer domain.
    * *Binary semaphore:* Ranges only between 0 and 1 (functions like a mutex).

#### Naive Busy-Wait Implementation
```c
wait(S) {
    while (S <= 0)
        ; // busy wait
    S--;
}
signal(S) {
    S++;
}
```


#### No Busy-Wait Implementation (Blocking)
Uses a queue. Features `block()` (places process on wait queue) and `wakeup()` (moves process to ready queue).
```c
typedef struct {
    int value;
    struct process *list;
} semaphore;

wait(semaphore *S) {
    S->value--;
    if (S->value < 0) {
        add this process to S->list;
        block();
    }
}
signal(semaphore *S) {
    S->value++;
    if (S->value <= 0) {
        remove a process P from S->list;
        wakeup(P);
    }
}
```


#### Semaphore Limitations
* Incorrect ordering can cause deadlocks (e.g., `wait(mutex)` followed by another `wait(mutex)`).
* Hard to reason about synchronization; the reason for waiting is embedded strictly inside `P()` (wait on a counter).
* Complex conditions (e.g., `if (x==0 && (y>0 || z>0))`) are difficult because checking conditions requires external mutexes, leading to a state where a thread sleeps while owning a lock, causing a **deadlock**.

---

### 6. Monitors & Condition Variables
* **Monitor:** A high-level abstract data type providing convenient process synchronization. Internal variables are only accessible by code within the procedure. Only one process may be active within the monitor at a time.
* **Condition Variables (CVs):** Abstract data types that encapsulate the pattern of releasing a lock, sleeping, and re-acquiring the lock. Internal data is a queue of waiting threads. They are **always** used together with locks.

#### Condition Variable Operations
* `cv_wait(struct cv *cv, struct lock *lock)`: Releases the lock, waits, and re-acquires the lock before returning.
* `cv_signal(struct cv *cv)`: Wakes up exactly one enqueued thread.
* `cv_broadcast(struct cv *cv)`: Wakes all enqueued threads.
* *Note:* If no one is waiting, `cv_signal` and `cv_broadcast` have no effect (unlike semaphores which store the increment).

#### Condition Variable Semantics
When process $P$ invokes `signal()` waking suspended process $Q$, they cannot run in parallel. Two main implementations exist:
1.  **Signal and Wait:** $P$ waits until $Q$ leaves the monitor or waits for another condition.
2.  **Signal and Continue:** $Q$ waits until $P$ leaves the monitor. (Most common in languages like C#, Java ).

#### Standard Usage Pattern
```c
lock_acquire(lock);
while (condition_not_true) {
    cv_wait(cond, lock);
}
// do stuff
// modify condition
cv_signal(cond); // or cv_broadcast
lock_release(lock);
```


---

### 7. OS/161 Specific Architectures (1.9x vs 2.0x)

#### OS/161 Locks
A lock in OS/161 is similar to a binary semaphore but enforces an ownership constraint: the thread that releases the lock **must** be the thread that acquired it.

#### OS/161 Thread Blocking
* `thread_sleep(const void *addr)`: Blocks calling thread on `addr`.
* `thread_wakeup(const void *addr)`: Unblocks sleeping threads on `addr`.
* *Difference from `yield()`:* `thread_yield()` makes the thread immediately ready to run again. `thread_sleep()` means the thread is blocked until explicitly woken.

#### Uniprocessor Semaphores (OS/161 1.9x Interrupt Based)
Enforces mutual exclusion by disabling timer interrupts before entering a critical section.
* Interface: `splhigh()` (disable), `spl0()` (enable), `splx(spl)` (restore state).
```c
void P(struct semaphore *sem) {
    int spl;
    assert(in_interrupt == 0); // May not block in interrupt handler
    spl = splhigh();
    while (sem->count == 0) {
        thread_sleep(sem);
    }
    sem->count--;
    splx(spl);
}
void V(struct semaphore *sem) {
    int spl = splhigh();
    sem->count++;
    thread_wakeup(sem);
    splx(spl);
}
```


#### Multicore Semaphores & Wait Channels (OS/161 2.0x)
Wait Channels (`wchan`) serve the same function as condition variables combined with spinlocks.
* **Rules:** Spinlock must be owned for a short time; nested spinlocks are not allowed. Spinlock handling is bridged into thread scheduling/switching.
* `wchan_sleep` requires the thread to hold the spinlock and not be in an interrupt.
* `wchan_wakeone` pulls a thread from the wait channel and makes it runnable.

**2.0x Semaphore Implementation:**
```c
struct semaphore {
    char *name;
    struct wchan *sem_wchan;
    struct spinlock sem_lock;
    volatile int count;
};

void P(struct semaphore *sem) {
    KASSERT(curthread->t_in_interrupt == false);
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
    wchan_wakeone(sem->sem_wchan, &sem->sem_lock);
    spinlock_release(&sem->sem_lock);
}
```


---

### 8. Practical Objectives: OS/161 LAB 3
The required tasks for LAB 3 are to implement kernel-level synchronization objects:
1.  **Locks**.
2.  **Condition Variables**.

**Implementation Strategy:**
* Look at the existing implementation of semaphores as a reference point.
* Build the new primitives using a combination of **spinlocks** and **wait channels**.


---

### Addendum: Granular Code Traces and Examples

#### 1. Java Spinlock Implementations (Pages 34-35)
While the OS/161 C implementation was covered, the lecture also provided exact Java package implementations for spinlocks using atomic booleans.

**Test-and-Set (TAS) Spinlock in Java:**
```java
package java.util.concurrent.atomic;

class TASspinlock {
    AtomicBoolean state = new AtomicBoolean(false);

    void lock() {
        while (state.getAndSet(true)) {}
    }

    void unlock() {
        state.set(false);
    }
}
```

**Test-and-Test-and-Set (TTAS) Spinlock in Java:**
```java
package java.util.concurrent.atomic;

class TTASspinlock {
    AtomicBoolean state = new AtomicBoolean(false);

    void lock() {
        while (true) {
            while (state.get()) {}
            if (!state.getAndSet(true))
                return;
        }
    }
}
```

#### 2. The "Wait on Condition" Deadlock & Fix Examples (Pages 53-57, 62-65)
The lecture walks through a specific scenario of computing and using a shared resource (`x, y, z`), demonstrating how deadlocks occur if locks are held while sleeping, and how Condition Variables solve this.

**The Deadlock Scenario (Using standard semaphores incorrectly):**
```c
/* shared state vars with some initial value */
int x,y,z;
struct lock *mylock = lock_create("Mutex");
struct semaphore *no_go = sem_create("MySem", 0);

compute_a_thing {
    lock_acquire(mylock); /* lock out others */
    x=f1(x); y=f2(y); z=f3(z);
    if (x!=0 || (y<=0 && z<=0)) V(no_go);
    lock_release(mylock); /* enable others */
}

use_a_thing {
    lock_acquire(mylock); /* lock out others */
    if (x==0 && (y>0 || z>0)) 
        P(no_go); /* DEADLOCK: sleeping while mylock is owned! */
    work(x,y,z);
    lock_release(mylock);
}
```

**The "Ugly" Manual Fix (Without Condition Variables):**
```c
use_a_thing {
    lock_acquire(mylock); 
    while (x==0 && (y>0 || z>0)) { // Must test condition again (while instead of if)
        lock_release(mylock); /* no deadlock */
        P(no_go);
        lock_acquire(mylock); /* lock for next test */
    }
    work(x,y,z);
    lock_release(mylock); 
}
```

**The Clean Fix (Using Condition Variables):**
```c
struct cv *no_go = cv_create("CondV");

compute_a_thing {
    lock_acquire(mylock);
    x=f1(x); y=f2(y); z=f3(z);
    if (x!=0 || (y<=0 && z<=0)) cv_signal(no_go); // Wakes waiting thread safely
    lock_release(mylock); 
}

use_a_thing {
    lock_acquire(mylock); 
    while (x==0 && (y>0 || z>0)) {
        cv_wait(no_go, mylock); // Atomically releases lock, sleeps, and re-acquires
    }
    work(x,y,z);
    lock_release(mylock); 
}
```

#### 3. General Usage of Condition Variables (Broadcast vs Signal) (Pages 62-63)
```c
/* Using cv_broadcast (Process P_j waking up multiple threads P_i and P_k) */
P_j {
    lock_acquire(lock);
    // modify conditions either for Pi or Pk
    cv_broadcast(cond);
    lock_release(lock);
}
```

#### 4. OS/161 Internal Wait Channel Code (Pages 67-68)
The document provides the exact internal kernel functions for how wait channels bridge spinlocks to the thread scheduler.

**`wchan_sleep` implementation:**
```c
wchan_sleep(struct wchan *wc, struct spinlock *lk) {
    /* may not sleep in an interrupt handler */
    KASSERT(!curthread->t_in_interrupt);
    /* must hold the spinlock */
    KASSERT(spinlock_do_i_hold(lk));
    /* must not hold other spinlocks */
    KASSERT(curcpu->c_spinlocks == 1);
    
    spinlock_acquire(lk);
    thread_switch(S_SLEEP, wc, lk);
}
```

**`wchan_wakeone` implementation:**
```c
wchan_wakeone(struct wchan *wc, struct spinlock *lk) {
    struct thread *target;
    KASSERT(spinlock_do_i_hold(lk));
    
    /* Grab a thread from the channel */
    target = threadlist_remhead(&wc->wc_threads);
    
    /* Note that thread_make_runnable acquires a runqueue lock while we're holding LK. 
       This is ok; all spinlocks associated with wchans must come before the runqueue locks. */
    thread_make_runnable(target, false);
}
```
## Lab3 implementation guide:
---
### Part 1: Implementing Locks
A lock is like a binary semaphore, but it requires "ownership" (the thread that releases the lock must be the one that acquired it).

**1. The Lock Structure**
Just like the semaphore on page 69, we need a wait channel, a spinlock to protect the internal state, and a way to track who holds the lock.

```c
struct lock {
    char *lk_name;
    struct wchan *lk_wchan;     // Wait channel for sleeping threads
    struct spinlock lk_lock;    // Spinlock to protect this struct
    struct thread *lk_owner;    // Tracks WHICH thread holds the lock
    volatile bool lk_held;      // Is the lock currently acquired?
};
```

**2. `lock_acquire`**
We follow the exact pattern of `P()`: grab the spinlock, check if the lock is held. If it is, sleep on the wait channel. When we wake up (or if it wasn't held), claim ownership.

```c
void lock_acquire(struct lock *lock) {
    KASSERT(lock != NULL);
    KASSERT(curthread->t_in_interrupt == false); /* may not block in interrupt */

    spinlock_acquire(&lock->lk_lock);

    // If someone else holds the lock, go to sleep
    while (lock->lk_held) {
        wchan_sleep(lock->lk_wchan, &lock->lk_lock);
    }

    // We now have the lock!
    lock->lk_held = true;
    lock->lk_owner = curthread; // Claim ownership

    spinlock_release(&lock->lk_lock);
}
```

**3. `lock_release`**
We follow the pattern of `V()`: grab the spinlock, verify we are the owner, release ownership, and wake up *one* sleeping thread.

```c
void lock_release(struct lock *lock) {
    KASSERT(lock != NULL);

    spinlock_acquire(&lock->lk_lock);

    // Enforce ownership constraint!
    KASSERT(lock->lk_owner == curthread); 

    // Release the lock
    lock->lk_owner = NULL;
    lock->lk_held = false;

    // Wake up ONE thread waiting for this lock
    wchan_wakeone(lock->lk_wchan, &lock->lk_lock);

    spinlock_release(&lock->lk_lock);
}
```

---

### Part 2: Implementing Condition Variables (CVs)
CVs don't have internal state (like a `count` or `held` boolean) because the state is managed by the external lock the user passes in. A CV is essentially just a wrapper around a wait channel.

**1. The CV Structure**
```c
struct cv {
    char *cv_name;
    struct wchan *cv_wchan;   // Where threads sleep
    struct spinlock cv_lock;  // Protects the wait channel
};
```

**2. `cv_wait`**
This is the trickiest part. The text states: `cv_wait` must release the external lock, sleep, and re-acquire the lock before returning. We must use the CV's spinlock to ensure we don't miss a wakeup signal between releasing the external lock and going to sleep.

```c
void cv_wait(struct cv *cv, struct lock *lock) {
    KASSERT(cv != NULL);
    KASSERT(lock != NULL);
    KASSERT(lock->lk_owner == curthread); // You must hold the lock to wait

    spinlock_acquire(&cv->cv_lock);

    // Release the external lock BEFORE going to sleep
    lock_release(lock);

    // Go to sleep on the CV's wait channel.
    // wchan_sleep requires us to pass the spinlock protecting the channel.
    wchan_sleep(cv->cv_wchan, &cv->cv_lock);

    spinlock_release(&cv->cv_lock);

    // When we wake up, we must RE-ACQUIRE the external lock before returning
    lock_acquire(lock);
}
```

**3. `cv_signal`**
Wake up exactly one thread.

```c
void cv_signal(struct cv *cv, struct lock *lock) {
    KASSERT(cv != NULL);
    KASSERT(lock != NULL);
    KASSERT(lock->lk_owner == curthread); // Checking ownership per page 60

    spinlock_acquire(&cv->cv_lock);
    wchan_wakeone(cv->cv_wchan, &cv->cv_lock);
    spinlock_release(&cv->cv_lock);
}
```

**4. `cv_broadcast`**
Wake up all enqueued threads. *(Note: OS/161 provides `wchan_wakeall` internally for this).*

```c
void cv_broadcast(struct cv *cv, struct lock *lock) {
    KASSERT(cv != NULL);
    KASSERT(lock != NULL);
    KASSERT(lock->lk_owner == curthread);

    spinlock_acquire(&cv->cv_lock);
    wchan_wakeall(cv->cv_wchan, &cv->cv_lock); // Wake everyone!
    spinlock_release(&cv->cv_lock);
}
```
