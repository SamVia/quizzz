## Foundational Cryptographic Algorithms and Techniques

### Basic Terminology

* **Plaintext (P):** The original message in clear text.


* **Ciphertext (C):** The coded (encrypted or enciphered) message.


* **Cipher/Algorithm:** The technique utilized to transform plaintext into ciphertext.


* **Key:** The information used within a cipher to generate the ciphertext and to recover the plaintext.


* **Encipher (Encrypt):** The process of converting plaintext to ciphertext.


* **Decipher (Decrypt):** The process of recovering plaintext from ciphertext.


* **Cryptography:** The study of encryption principles and methods.


* **Cryptanalysis:** The study of principles and methods used to decipher ciphertext without knowing the key.


* **Cryptology:** The comprehensive field encompassing both cryptography and cryptanalysis.



### Principles & Security

* **Kerckhoffs' Principle:** A cryptosystem's strength relies on the keys being kept secret, managed by trusted systems, and being of adequate length. The secrecy of the encryption and decryption algorithms is not important; algorithms should be public to allow for widespread analysis and identification of weaknesses.


* **Brute Force Attack:** Involves attempting all possible keys $K$ from the key space $T$ to decrypt ciphertext. It requires a number of trials equal to $T \sim 2^{Nbit}$. This attack assumes known properties of the plaintext to verify decryption success.


* **Key Length Recommendations:** Key length is a compromise between efficiency and security.


* *Symmetric:* 40 (low), 80, 128, 256 (high).


* *Asymmetric (RSA, DSA):* 512 (low), 1024, 2048, 4096 (high).


* *Asymmetric (ECC):* 80 (low), 160, 256, 512 (high).




* **XOR Function ($\oplus$):** An ideal "confusion" operator available on all CPUs. If the input is random (50:50 probability of 0 or 1), the output is equally random. It is the inverse of itself: if $A \oplus B = Z$, then $Z \oplus B = A$. Properties: $A \oplus 0 = A$, $A \oplus 1 = A'$, $A \oplus A = 0$, $A \oplus A' = 1$.



### Symmetric Cryptography

* Utilizes a single key, $K$, shared securely between the sender and receiver.


* Formulas: $C = enc(K, P)$ or $C = \{P\}K$, and $P = dec(K, C) = enc^{-1}(K, C)$.


* Low computational load, primarily used for data encryption.


* **Key Distribution Issue:** To connect $N$ parties, $N \times (N-1) / 2$ keys are required, causing scaling issues (e.g., 100 users = 4950 keys).



#### Block Algorithms

* Divides data into fixed-length blocks (typically 64 or 128 bits), processed one at a time. Secret keys may be reused.


* **DES (Data Encryption Standard):** 64-bit block, 56-bit key (+8 parity bits). Standard FIPS 46/2. Designed for hardware efficiency using XOR, shift, and permutation. Obsolete; its 56-bit key was broken via brute force in 22 hours in 1999.


* **Double DES & Meet-in-the-Middle Attack:** Double encryption is vulnerable to a known-plaintext attack allowing key discovery in at most $2^{N+1}$ attempts.


* *Hypothesis:* Known $P$ and $C$ where $C = enc(K_2, enc(K_1, P))$.


* *Action:* Compute $2^N$ values $X_i = enc(K_i, P)$ and $2^N$ values $Y_j = dec(K_j, C)$. Search for matches where $X_i = Y_j$.




* **Triple DES (3DES/TDES):** Applies DES three times, typically in EDE (Encrypt-Decrypt-Encrypt) mode for backward compatibility. Uses 2 keys (112-bit strength) or 3 keys (168-bit strength).


* **AES (Advanced Encryption Standard / Rijndael):** Replaced DES. Key lengths: 128, 192, or 256 bits. Block size: 128 bits. Standardized as FIPS-197 in 2001.


* **Other Block Ciphers:** IDEA (128-bit key, 64-bit block), RC2, Blowfish, CAST-128, RC5.



#### Block Cipher Modes of Operation

* **ECB (Electronic Code Book):**
* *Encrypt:* $C_i = enc(K, P_i)$.


* *Decrypt:* $P_i = enc^{-1}(K, C_i)$.


* *Pros/Cons:* Fast parallel execution, no error propagation. However, block swapping goes undetected, and identical plaintext blocks produce identical ciphertext blocks, making it vulnerable to known-plaintext attacks.




* **CBC (Cipher Block Chaining):**
* *Encrypt:* $C_i = enc(K, P_i \oplus C_{i-1})$. Requires an Initialization Vector $C_0 = IV$ (random, unpredictable, size of block).


* *Decrypt:* $P_i = enc^{-1}(K, C_i) \oplus C_{i-1}$.


* *Pros/Cons:* Resists swapping and known-plaintext attacks. However, transmission errors propagate to two decrypted blocks, execution is sequential (slow), and it is malleable (flipping IV bits flips plaintext bits).




* **Padding:** Used when data size is not a multiple of block size.


* *Techniques:* Null bytes, 1 bit followed by 0s, length byte followed by nulls, TLS uses bytes with value L (e.g., 0x03 0x03 0x03), IPsec uses progressive numbers. Padding must always be applied even if the message is an exact multiple to avoid interpretation errors.




* **CTS (Ciphertext Stealing):** Permits block algorithms without padding by utilizing bytes from the second-to-last block to fill the final partial block.


* **CTR (Counter Mode):**
* Requires a random nonce and a counter combined via a function.


* *Pros/Cons:* Allows parallel execution, requires no padding, allows random direct access. However, canceling an entire group causes desynchronization for all subsequent groups.


* *Code Implementation Snippet (C-style):*
```c
for (x=0; x<data_size; x++)
    ctext[x] = ptext[x] ^ MostSignificantByte(enc(k, nonce || x));
```[cite: 30]


```





#### Stream Algorithms

* Operate on a stream of data (one bit or byte at a time) without division into blocks. Requires a random keystream derived from a secret seed, which must never be reused.


* **Algorithms:** RC4, SEAL (older); Salsa20, ChaCha20 (modern).


* **ChaCha20 & Salsa20:** Invented by D.J. Bernstein. Uses 128 or 256-bit keys and a 32-bit ARX (add-rotate-xor) base operation. The base function generates a 512-bit keystream block: $f(Key256, Nonce64, Counter64)$.


* **RFC-8439 (IETF Modification):** IETF modified ChaCha20 to use a 96-bit nonce and a 32-bit counter, introducing a 256 GB encryption limit.



### Asymmetric Cryptography

* Uses key pairs: a private key ($Kpri$) kept secret, and a public key ($Kpub$) distributed widely. Used for key distribution and digital signatures. High processing load.


* **RSA (Rivest-Shamir-Adleman):** Security is based on the computational difficulty of factoring large numbers.


* *Key Generation:*
1. Choose large random primes $P, Q$. Compute modulus $N = P \cdot Q$.


2. Compute $PHI = (P-1)(Q-1)$.


3. Select public exponent $E$ such that $1 < E < PHI$ and $gcd(E, PHI) = 1$.


4. Calculate private exponent $D = E^{-1} \mod PHI$.


5. Public key = $(N, E)$, Private key = $(N, D)$.




* *Operation:* Encrypt $c = p^E \mod N$. Decrypt $p' = c^D \mod N$.


* *Encoding:* Raw RSA is deterministic and vulnerable to mathematical attacks. Messages must be encoded, typically using PKCS#1 v1.5.




* **DSA (Digital Signature Algorithm):** Security based on discrete logarithms. Used only for digital signatures.


* **Diffie-Hellman (DH):** Key agreement protocol resistant to sniffing, but vulnerable to Man-in-the-Middle (MITM) attacks without pre-authentication.


* *Process:* Parties agree on large prime $p$ and generator $g$.


* Alice picks secret $x$, sends $X = g^x \mod p$.


* Bob picks secret $y$, sends $Y = g^y \mod p$.


* Shared Key $K_{AB} = Y^x \mod p = X^y \mod p = g^{xy} \mod p$.




* **Elliptic Curve Cryptography (ECC):** Executes operations on a 2D elliptic curve. The discrete logarithm problem on curves is more complex, allowing for shorter keys ($\sim 1/10$ the size of RSA keys). Variants include ECDSA, ECDH, ECMQV, and ECIES.



### Hash Functions & Message Integrity

* **Message Digest:** A fixed-length summary of a message calculated via a one-way cryptographic hash function $md = h(m)$.


* **Ideal Properties:** Fast computation, hard to invert, and highly collision-resistant (changing one bit unpredictable alters the output).


* **Collisions & Birthday Paradox:** A collision occurs when $h(m1) = h(m2)$ for $m1 \neq m2$. The probability of aliasing is $P_A \propto 1/2^N$. Due to the birthday paradox, a hash function producing an $N$-bit digest is insecure when more than $2^{N/2}$ digests are generated, as collision probability reaches 50%.


* **Algorithms:**
* *Obsolete/Broken:* MD2, MD4, MD5, SHA-1 (broken in 2005; collisions found in $2^{69}$ operations).


* *SHA-2:* SHA-224, SHA-256 (32-bit word, pairs with AES-128), SHA-384, SHA-512 (64-bit word, pairs with AES-256).


* *SHA-3 (Keccak):* Winner of NIST competition. Elegant design, high hardware performance.




* **Key Derivation Functions (KDF):** Used to convert weak user passwords into strong random cryptographic keys.


* Formula: $K = KDF(P, S, I)$ where $P$ is password, $S$ is salt, $I$ is iteration count.


* *PBKDF2:* Generates derived key $DK = PBKDF(PRF, PWD, Salt, C, dkLen)$.





### Authenticated Encryption & MACs

* **MAC (Message Authentication Code):** Guarantees integrity and authentication by calculating a digest on both data and a secret key.


* **HMAC:** RFC-2104. Uses a base hash function $H$.
* Formula: $HMAC = H(K' \oplus opad \vert{}\vert{} H(K' \oplus ipad \vert{}\vert{} data))$.




* **CBC-MAC:** Exploits symmetric encryption in CBC mode with $IV=0$, taking the last block as the MAC. Secure only for fixed-length messages.


* **Combining Integrity and Secrecy:**
* *Authenticate-and-Encrypt (A&E):* $enc(K_1, p) \vert{}\vert{} mac(K_2, p)$. (e.g., SSH). Insecure unless single step.


* *Authenticate-then-Encrypt (AtE):* $enc(K_1, p \vert{}\vert{} mac(K_2, p))$. (e.g., SSL/TLS).


* *Encrypt-then-Authenticate (EtA):* $enc(K_1, p) \vert{}\vert{} mac(K_2, enc(K_1, p))$. (e.g., IPsec). Most secure mode.




* **Authenticated Encryption (AE / AEAD):** One operation providing confidentiality and integrity with one key, preventing chosen-ciphertext attacks.


* *GCM (Galois/Counter Mode):* $AEAD$ mode utilizing a 128-bit block algorithm, taking Key, IV, Plaintext, and Associated Data (A).


* *CCM:* Counter-mode with CBC-MAC.





### Digital Signatures & PKI

* **Digital Signature:** Asymmetric encryption of a message digest using the sender's private key. Provides data authentication, integrity, and non-repudiation.


* **Public Key Certificate:** A data structure binding a public key to attributes (identity, IP), digitally signed by a Certification Authority (CA).


* *Format:* X.509v3 is widely used. Contains version, serial number, signature algorithm, issuer, validity, subject, public key info, and CA digital signature.




* **Revocation:** Certificates can be revoked before expiration.


* *CRL (Certificate Revocation List):* Signed list of revoked certificates.


* *OCSP (On-line Certificate Status Protocol):* Server response indicating real-time status.




* **Validation Chain:** Verifying Alice's certificate requires the public key of CA1, which is verified by the certificate of CA2, up to a trusted root CA in the software's trusted list.



### Modern Standards (CNSA)

* **CNSA Suite (2018):** Mandates AES-256 (CTR or GCM), SHA-384, ECDH/ECMQV/ECDSA on curve P-384. Legacy allowed: DH-3072, RSA-3072.


* **CNSA 2.0 (2022 - Post-Quantum):** Introduces algorithms resistant to quantum computing.
* *Key Agreement:* CRYSTALS-Kyber (ML-KEM-1024).
* *Digital Signature:* CRYSTALS-Dilithium (ML-DSA-87).
* *Firmware Signing:* XMSS and LMS.



---

### Practical Exercises

**Exercise 1: RSA Key Generation and Encryption**
*Scenario:* Generate a tiny RSA keypair and encrypt the number $p=4$.

1. **Choose Primes:** Let $P = 3$, $Q = 11$.
2. **Calculate Modulus $N$:** 
$$N = 3 \times 11 = 33$$


3. **Calculate $PHI$:** 
$$PHI = (3-1)(11-1) = 2 \times 10 = 20$$


4. **Choose Public Exponent $E$:** Must be relatively prime to 20. Let $E = 3$.
5. **Calculate Private Exponent $D$:** Must satisfy $E \times D \equiv 1 \pmod{20}$.
* $3 \times 7 = 21 \equiv 1 \pmod{20}$. Therefore, $D = 7$.


6. **Keys:** Public key is $(33, 3)$. Private key is $(33, 7)$.
7. **Encrypt Plaintext $p=4$:** 
$$C = 4^3 \pmod{33} = 64 \pmod{33} = 31$$


8. **Decrypt Ciphertext $C=31$:** 
$$P' = 31^7 \pmod{33}$$


* $31^2 = 961 \pmod{33} = 4$
* $31^4 = 4^2 \pmod{33} = 16$
* $31^7 = 31^4 \times 31^2 \times 31^1 = 16 \times 4 \times 31 = 64 \times 31 = 1984$
* $1984 \pmod{33} = 4$. Decryption is successful.



**Exercise 2: Diffie-Hellman Key Exchange**
*Scenario:* Alice and Bob establish a shared secret.

1. **Public Parameters:** Prime $p = 23$, Generator $g = 5$.
2. **Alice's Action:** Chooses secret $x = 4$. Computes $X = 5^4 \pmod{23}$.
* $5^2 = 25 \pmod{23} = 2$.
* $5^4 = 2^2 \pmod{23} = 4$. Alice sends $X=4$ to Bob.


3. **Bob's Action:** Chooses secret $y = 3$. Computes $Y = 5^3 \pmod{23}$.
* $5^3 = 125 \pmod{23} = 10$. Bob sends $Y=10$ to Alice.


4. **Shared Secret Generation:**
* Alice computes $K = Y^x \pmod{23} = 10^4 \pmod{23}$.
* $10^2 = 100 \pmod{23} = 8$. $10^4 = 8^2 = 64 \pmod{23} = 18$.


* Bob computes $K = X^y \pmod{23} = 4^3 \pmod{23}$.
* $4^3 = 64 \pmod{23} = 18$. The shared secret $K_{AB}$ is 18.





---

### Deliverable 2: Interactive HTML Quiz

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cryptography & System Programming Quiz</title>
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; line-height: 1.6; padding: 20px; }
    .quiz-container { max-width: 800px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    h1 { text-align: center; color: #2c3e50; }
    .question-block { margin-bottom: 25px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
    .question-text { font-weight: bold; margin-bottom: 10px; font-size: 1.1em; }
    .options { list-style-type: none; padding: 0; }
    .options li { margin-bottom: 8px; }
    .options label { cursor: pointer; display: flex; align-items: center; }
    .options input { margin-right: 10px; }
    .submit-btn { display: block; width: 100%; padding: 12px; background-color: #3498db; color: white; border: none; border-radius: 4px; font-size: 1.1em; cursor: pointer; margin-top: 20px; }
    .submit-btn:hover { background-color: #2980b9; }
    .feedback { display: none; margin-top: 15px; padding: 15px; border-radius: 4px; }
    .correct-fb { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .incorrect-fb { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    code { background-color: #f1f1f1; padding: 2px 4px; border-radius: 3px; font-family: Consolas, monospace; }
</style>
</head>
<body>

<div class="quiz-container">
    <h1>Cryptography Master Quiz</h1>
    <form id="cryptoQuiz">
        
        <!-- Q1 -->
        <div class="question-block" id="q1-block">
            <div class="question-text">1. According to Kerckhoffs' principle, the strength of a cryptosystem relies on what remaining secret?</div>
            <ul class="options">
                <li><label><input type="radio" name="q1" value="a"> The encryption algorithm</label></li>
                <li><label><input type="radio" name="q1" value="b"> The keys</label></li>
                <li><label><input type="radio" name="q1" value="c"> The decryption algorithm</label></li>
                <li><label><input type="radio" name="q1" value="d"> The padding mechanism</label></li>
            </ul>
            <div class="feedback" id="q1-feedback"></div>
        </div>

        <!-- Q2 -->
        <div class="question-block" id="q2-block">
            <div class="question-text">2. How many attempts does a meet-in-the-middle attack require to discover the key in a Double DES implementation utilizing N-bit keys?</div>
            <ul class="options">
                <li><label><input type="radio" name="q2" value="a"> 2^(2N)</label></li>
                <li><label><input type="radio" name="q2" value="b"> 2^N</label></li>
                <li><label><input type="radio" name="q2" value="c"> 2^(N+1)</label></li>
                <li><label><input type="radio" name="q2" value="d"> 2^(N/2)</label></li>
            </ul>
            <div class="feedback" id="q2-feedback"></div>
        </div>

        <!-- Q3 -->
        <div class="question-block" id="q3-block">
            <div class="question-text">3. Which of the following AES configurations was formally chosen as the winner in the NIST competition (FIPS-197)?</div>
            <ul class="options">
                <li><label><input type="radio" name="q3" value="a"> 64-bit block; 128-bit key</label></li>
                <li><label><input type="radio" name="q3" value="b"> 128-bit block; 128/192/256-bit key</label></li>
                <li><label><input type="radio" name="q3" value="c"> 256-bit block; 128/192/256-bit key</label></li>
                <li><label><input type="radio" name="q3" value="d"> 128-bit block; 56-bit key</label></li>
            </ul>
            <div class="feedback" id="q3-feedback"></div>
        </div>

        <!-- Q4 -->
        <div class="question-block" id="q4-block">
            <div class="question-text">4. What is a critical vulnerability of the Electronic Code Book (ECB) mode of operation?</div>
            <ul class="options">
                <li><label><input type="radio" name="q4" value="a"> It causes extensive error propagation across the entire stream.</label></li>
                <li><label><input type="radio" name="q4" value="b"> It cannot process data in parallel.</label></li>
                <li><label><input type="radio" name="q4" value="c"> Identical plaintext blocks produce identical ciphertext blocks.</label></li>
                <li><label><input type="radio" name="q4" value="d"> It strictly requires an unpredictable Initialization Vector (IV).</label></li>
            </ul>
            <div class="feedback" id="q4-feedback"></div>
        </div>

        <!-- Q5 -->
        <div class="question-block" id="q5-block">
            <div class="question-text">5. In Cipher Block Chaining (CBC) mode, what is the formula to encrypt the i-th block?</div>
            <ul class="options">
                <li><label><input type="radio" name="q5" value="a"> C_i = enc(K, P_i)</label></li>
                <li><label><input type="radio" name="q5" value="b"> C_i = enc(K, P_i XOR C_{i-1})</label></li>
                <li><label><input type="radio" name="q5" value="c"> C_i = enc(K, P_i) XOR C_{i-1}</label></li>
                <li><label><input type="radio" name="q5" value="d"> C_i = P_i XOR enc(K, C_{i-1})</label></li>
            </ul>
            <div class="feedback" id="q5-feedback"></div>
        </div>

        <!-- Q6 -->
        <div class="question-block" id="q6-block">
            <div class="question-text">6. How does Ciphertext Stealing (CTS) handle data sizes that are not multiples of the block algorithm?</div>
            <ul class="options">
                <li><label><input type="radio" name="q6" value="a"> It adds null bytes (0x00) until the block is filled.</label></li>
                <li><label><input type="radio" name="q6" value="b"> It streams the final bytes using ChaCha20.</label></li>
                <li><label><input type="radio" name="q6" value="c"> It fills the last partial block with bytes from the second-to-last block.</label></li>
                <li><label><input type="radio" name="q6" value="d"> It truncates the final ciphertext block.</label></li>
            </ul>
            <div class="feedback" id="q6-feedback"></div>
        </div>

        <!-- Q7 -->
        <div class="question-block" id="q7-block">
            <div class="question-text">7. In CTR mode, what happens if an attacker cancels an entire group/block during transmission?</div>
            <ul class="options">
                <li><label><input type="radio" name="q7" value="a"> Only the canceled block decrypts erroneously.</label></li>
                <li><label><input type="radio" name="q7" value="b"> It causes desynchronization, and all subsequent groups decrypt erroneously.</label></li>
                <li><label><input type="radio" name="q7" value="c"> The IV corrects the synchronization error.</label></li>
                <li><label><input type="radio" name="q7" value="d"> The algorithm falls back to ECB mode automatically.</label></li>
            </ul>
            <div class="feedback" id="q7-feedback"></div>
        </div>

        <!-- Q8 -->
        <div class="question-block" id="q8-block">
            <div class="question-text">8. What encryption limit is imposed by the IETF's modification of ChaCha20 (RFC-8439) utilizing a 32-bit counter?</div>
            <ul class="options">
                <li><label><input type="radio" name="q8" value="a"> 256 MB</label></li>
                <li><label><input type="radio" name="q8" value="b"> 256 GB</label></li>
                <li><label><input type="radio" name="q8" value="c"> 64 TB</label></li>
                <li><label><input type="radio" name="q8" value="d"> Infinite</label></li>
            </ul>
            <div class="feedback" id="q8-feedback"></div>
        </div>

        <!-- Q9 -->
        <div class="question-block" id="q9-block">
            <div class="question-text">9. If an organization has 100 users relying purely on symmetric cryptography for secure 1-to-1 communication, how many distinct keys must be managed?</div>
            <ul class="options">
                <li><label><input type="radio" name="q9" value="a"> 100</label></li>
                <li><label><input type="radio" name="q9" value="b"> 200</label></li>
                <li><label><input type="radio" name="q9" value="c"> 4950</label></li>
                <li><label><input type="radio" name="q9" value="d"> 10000</label></li>
            </ul>
            <div class="feedback" id="q9-feedback"></div>
        </div>

        <!-- Q10 -->
        <div class="question-block" id="q10-block">
            <div class="question-text">10. During RSA Key Generation, how is the private exponent (D) calculated?</div>
            <ul class="options">
                <li><label><input type="radio" name="q10" value="a"> D = E^-1 mod PHI</label></li>
                <li><label><input type="radio" name="q10" value="b"> D = P * Q</label></li>
                <li><label><input type="radio" name="q10" value="c"> D = (P-1)(Q-1)</label></li>
                <li><label><input type="radio" name="q10" value="d"> D = P^E mod N</label></li>
            </ul>
            <div class="feedback" id="q10-feedback"></div>
        </div>

        <!-- Q11 -->
        <div class="question-block" id="q11-block">
            <div class="question-text">11. Why is raw RSA encryption virtually never used directly on messages?</div>
            <ul class="options">
                <li><label><input type="radio" name="q11" value="a"> It requires too much padding.</label></li>
                <li><label><input type="radio" name="q11" value="b"> It is deterministic, making identical messages produce identical ciphertexts.</label></li>
                <li><label><input type="radio" name="q11" value="c"> Hardware cannot process modulo math quickly.</label></li>
                <li><label><input type="radio" name="q11" value="d"> It is a stream cipher rather than a block cipher.</label></li>
            </ul>
            <div class="feedback" id="q11-feedback"></div>
        </div>

        <!-- Q12 -->
        <div class="question-block" id="q12-block">
            <div class="question-text">12. What specific vulnerability exists in the basic Diffie-Hellman key exchange if certificates are not used?</div>
            <ul class="options">
                <li><label><input type="radio" name="q12" value="a"> Brute force on the generator (g).</label></li>
                <li><label><input type="radio" name="q12" value="b"> Padding oracle attacks.</label></li>
                <li><label><input type="radio" name="q12" value="c"> Man-in-the-Middle (MITM) attacks.</label></li>
                <li><label><input type="radio" name="q12" value="d"> Hash collisions.</label></li>
            </ul>
            <div class="feedback" id="q12-feedback"></div>
        </div>

        <!-- Q13 -->
        <div class="question-block" id="q13-block">
            <div class="question-text">13. In hash functions, what is a "collision"?</div>
            <ul class="options">
                <li><label><input type="radio" name="q13" value="a"> When a hash function cannot process an input due to size.</label></li>
                <li><label><input type="radio" name="q13" value="b"> When an attacker recovers the original message from the digest.</label></li>
                <li><label><input type="radio" name="q13" value="c"> When two different messages output the identical hash value.</label></li>
                <li><label><input type="radio" name="q13" value="d"> When a symmetric key matches a public key.</label></li>
            </ul>
            <div class="feedback" id="q13-feedback"></div>
        </div>

        <!-- Q14 -->
        <div class="question-block" id="q14-block">
            <div class="question-text">14. Due to the birthday paradox, a hash function generating an N-bit digest becomes statistically vulnerable to collision discovery after approximately how many operations?</div>
            <ul class="options">
                <li><label><input type="radio" name="q14" value="a"> 2^N</label></li>
                <li><label><input type="radio" name="q14" value="b"> 2^(N/2)</label></li>
                <li><label><input type="radio" name="q14" value="c"> N^2</label></li>
                <li><label><input type="radio" name="q14" value="d"> 2^(N-1)</label></li>
            </ul>
            <div class="feedback" id="q14-feedback"></div>
        </div>

        <!-- Q15 -->
        <div class="question-block" id="q15-block">
            <div class="question-text">15. Which cryptographic algorithm was selected as the winner of the SHA-3 competition?</div>
            <ul class="options">
                <li><label><input type="radio" name="q15" value="a"> Skein</label></li>
                <li><label><input type="radio" name="q15" value="b"> BLAKE</label></li>
                <li><label><input type="radio" name="q15" value="c"> Keccak</label></li>
                <li><label><input type="radio" name="q15" value="d"> Grøstl</label></li>
            </ul>
            <div class="feedback" id="q15-feedback"></div>
        </div>

        <!-- Q16 -->
        <div class="question-block" id="q16-block">
            <div class="question-text">16. What is the primary purpose of a Key Derivation Function (KDF) like PBKDF2?</div>
            <ul class="options">
                <li><label><input type="radio" name="q16" value="a"> To encrypt data rapidly on IoT devices.</label></li>
                <li><label><input type="radio" name="q16" value="b"> To transform a guessable password/passphrase into a strong, random cryptographic key.</label></li>
                <li><label><input type="radio" name="q16" value="c"> To digitally sign documents using a private key.</label></li>
                <li><label><input type="radio" name="q16" value="d"> To verify the revocation status of an X.509 certificate.</label></li>
            </ul>
            <div class="feedback" id="q16-feedback"></div>
        </div>

        <!-- Q17 -->
        <div class="question-block" id="q17-block">
            <div class="question-text">17. What padding bytes are utilized within the HMAC construction according to RFC-2104?</div>
            <ul class="options">
                <li><label><input type="radio" name="q17" value="a"> 0x00 and 0xFF</label></li>
                <li><label><input type="radio" name="q17" value="b"> 0x36 (ipad) and 0x5C (opad)</label></li>
                <li><label><input type="radio" name="q17" value="c"> Progressive values (0x01, 0x02)</label></li>
                <li><label><input type="radio" name="q17" value="d"> Random nonces</label></li>
            </ul>
            <div class="feedback" id="q17-feedback"></div>
        </div>

        <!-- Q18 -->
        <div class="question-block" id="q18-block">
            <div class="question-text">18. When combining message integrity and secrecy, which implementation schema is considered the most secure (used by IPsec)?</div>
            <ul class="options">
                <li><label><input type="radio" name="q18" value="a"> Authenticate-and-Encrypt (A&E)</label></li>
                <li><label><input type="radio" name="q18" value="b"> Authenticate-then-Encrypt (AtE)</label></li>
                <li><label><input type="radio" name="q18" value="c"> Encrypt-then-Authenticate (EtA)</label></li>
                <li><label><input type="radio" name="q18" value="d"> They are all equally secure.</label></li>
            </ul>
            <div class="feedback" id="q18-feedback"></div>
        </div>

        <!-- Q19 -->
        <div class="question-block" id="q19-block">
            <div class="question-text">19. In the context of Public-Key Infrastructure (PKI), what is a CRL?</div>
            <ul class="options">
                <li><label><input type="radio" name="q19" value="a"> Certificate Registration Link</label></li>
                <li><label><input type="radio" name="q19" value="b"> Certificate Revocation List</label></li>
                <li><label><input type="radio" name="q19" value="c"> Cryptographic Rotation Ledger</label></li>
                <li><label><input type="radio" name="q19" value="d"> Certification Root Locator</label></li>
            </ul>
            <div class="feedback" id="q19-feedback"></div>
        </div>

        <!-- Q20 -->
        <div class="question-block" id="q20-block">
            <div class="question-text">20. Which algorithm is recommended by the CNSA 2.0 (2022) for Post-Quantum digital signatures?</div>
            <ul class="options">
                <li><label><input type="radio" name="q20" value="a"> ECDSA on curve P-384</label></li>
                <li><label><input type="radio" name="q20" value="b"> RSA-3072</label></li>
                <li><label><input type="radio" name="q20" value="c"> CRYSTALS-Dilithium (ML-DSA-87)</label></li>
                <li><label><input type="radio" name="q20" value="d"> CRYSTALS-Kyber (ML-KEM-1024)</label></li>
            </ul>
            <div class="feedback" id="q20-feedback"></div>
        </div>

        <button type="button" class="submit-btn" onclick="gradeQuiz()">Submit Quiz</button>
    </form>
</div>

<script>
    const answers = {
        q1: { correct: 'b', explanation: 'Kerckhoffs\' Principle states that cryptosystem strength relies on keys being kept secret, not the algorithms[cite: 5].' },
        q2: { correct: 'c', explanation: 'Double application of encryption is subject to a meet-in-the-middle attack allowing key discovery in at most 2^(N+1) attempts[cite: 12].' },
        q3: { correct: 'b', explanation: 'AES (Rijndael) was chosen utilizing a 128-bit block size and keys of 128, 192, or 256 bits[cite: 15].' },
        q4: { correct: 'c', explanation: 'ECB is vulnerable to known-plaintext attacks because identical plaintext blocks encrypt to identical ciphertext blocks[cite: 18].' },
        q5: { correct: 'b', explanation: 'In CBC mode, the plaintext block is XORed with the previous ciphertext block before encryption: C_i = enc(K, P_i XOR C_{i-1})[cite: 19].' },
        q6: { correct: 'c', explanation: 'CTS permits block algorithms without padding by filling the last partial block with bytes stolen from the second-to-last block[cite: 25].' },
        q7: { correct: 'b', explanation: 'A major con of CTR mode is that cancellation of one entire group causes desynchronization, decrypting all subsequent groups erroneously[cite: 29].' },
        q8: { correct: 'b', explanation: 'IETF RFC-8439 modified ChaCha20 to use a 32-bit counter, resulting in a 256 GB limit (2^32 64-byte blocks)[cite: 34].' },
        q9: { correct: 'c', explanation: 'Symmetric cryptography requires N*(N-1)/2 keys for a full mesh. For 100 users: 100*99/2 = 4950 keys[cite: 36].' },
        q10: { correct: 'a', explanation: 'During RSA generation, the private exponent D is calculated as the modular inverse of E: D = E^-1 mod PHI[cite: 41].' },
        q11: { correct: 'b', explanation: 'Raw RSA is deterministic; the same message encrypted twice yields identical ciphertext, making padding/encoding (like PKCS#1 v1.5) necessary[cite: 43].' },
        q12: { correct: 'c', explanation: 'Without authentication (like certificates), Diffie-Hellman cannot prove identity, making it completely vulnerable to Man-in-the-Middle attacks[cite: 51].' },
        q13: { correct: 'c', explanation: 'A collision occurs in a hash function when two different messages (m1 and m2) produce the exact same hash value (h(m1) = h(m2))[cite: 65].' },
        q14: { correct: 'b', explanation: 'Due to the birthday paradox, a hash function is generally insecure after 2^(N/2) operations, at which point collision probability reaches ~50%[cite: 70].' },
        q15: { correct: 'c', explanation: 'Keccak was chosen as the winner of the NIST SHA-3 competition on October 2, 2012[cite: 73].' },
        q16: { correct: 'b', explanation: 'A KDF like PBKDF2 iterates a cryptographic hash over a password/passphrase and a salt to generate a strong derived key (DK)[cite: 75].' },
        q17: { correct: 'b', explanation: 'RFC-2104 defines HMAC using two internal padding values: ipad (0x36) and opad (0x5C) repeated B times[cite: 81].' },
        q18: { correct: 'c', explanation: 'Encrypt-then-Authenticate (EtA) is considered the most secure mode and is used by IPsec, as it avoids decryption if the MAC is wrong[cite: 85].' },
        q19: { correct: 'b', explanation: 'CRL stands for Certificate Revocation List, which is a list of revoked certificates signed by the CA[cite: 105].' },
        q20: { correct: 'c', explanation: 'CNSA 2.0 (2022) introduces CRYSTALS-Dilithium (ML-DSA-87) as the post-quantum standard for digital signatures.' }
    };

    function gradeQuiz() {
        for (let i = 1; i <= 20; i++) {
            const qId = 'q' + i;
            const options = document.getElementsByName(qId);
            let selected = null;
            
            for (const opt of options) {
                if (opt.checked) {
                    selected = opt.value;
                    break;
                }
            }

            const feedbackDiv = document.getElementById(qId + '-feedback');
            feedbackDiv.style.display = 'block';

            if (selected === answers[qId].correct) {
                feedbackDiv.className = 'feedback correct-fb';
                feedbackDiv.innerHTML = '<strong>Correct!</strong> ' + answers[qId].explanation;
            } else {
                feedbackDiv.className = 'feedback incorrect-fb';
                const ansText = selected ? 'Incorrect.' : 'No answer selected.';
                feedbackDiv.innerHTML = '<strong>' + ansText + '</strong> ' + answers[qId].explanation;
            }
        }
    }
</script>
</body>
</html>

```