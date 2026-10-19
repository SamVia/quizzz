## Master Cheat Sheet: Authentication Techniques, Protocols, and Architectures

### 1. Fundamentals of Identity and Authentication

* **Identification (Recognition):** The process of establishing an identity from available information, answering the question "Who are you?". An example is matching a tested fingerprint against a database to find a user.


* **Authentication (AuthN / AuthC):** The process of verifying evidence to corroborate an asserted (claimed) identity, answering "Are you who you claim to be?". For example, checking if an asserted username and fingerprint pair matches a stored template at a verifier.


* **Scope:** Authentication applies to human beings (user authentication) as well as software components or hardware elements interacting via software. It is distinct from, but related to, authorization (AuthZ).



### 2. Authentication Factors and Risks

Authentication relies on single or combined factors (Multi-Factor Authentication, MFA).

* **Knowledge:** Something only the user knows (e.g., static password, PIN).


* *Risks:* Storage, demonstration, and transmission vulnerabilities.




* **Ownership:** Something only the user possesses, often called an 'authenticator' (e.g., hardware token, smart card, smartphone).


* *Risks:* Theft, cloning, unauthorized usage, and risks to the authenticator itself.




* **Inherence (Biometrics):** Something the user is (e.g., fingerprint).


* *Risks:* Counterfeiting and privacy concerns. Compromised biometric data cannot be replaced, which is a major problem. It should only be used for local authentication to unlock a secret or device.





### 3. Digital Authentication Model (NIST SP800.63B)

The NIST framework defines several distinct but interacting entities (which may be separated or collapsed together):

* **CSP (Credential Service Provider):** Enrolls the applicant, verifies attributes, and issues the user credential and authenticator.


* **Subscriber:** The user who has successfully enrolled and received an authenticator.


* **Claimant:** The entity asserting an identity and proving possession of the authenticator.


* **Verifier:** Executes the authentication protocol to verify the claimant's valid authenticator and credential.


* **Relying Party (RP):** Requests or receives an authentication assertion from the Verifier to assess the user's identity and attributes for an authenticated session.


* **Credential:** An object (e.g., an X.509 certificate) that binds an authenticator to a subscriber via an ID.



### 4. Password-Based Authentication

* **Cleartext Transmissions ($f=I$):** The client transmits the password in cleartext, and the server verifies it. The server must know all passwords in cleartext, making the system highly vulnerable to sniffing and replay attacks without a secure channel.


* **Hash Transmissions ($f=\text{hash}$):** The client transmits the cleartext password; the server computes the digest and checks it against a stored digest $H_{UID}$. Subject to replay and dictionary attacks.


* **Risks & Attacks:** Password storage vulnerabilities (server-side cleartext or unprotected digests), password guessing (especially offline against hash lists), sniffing, database attacks, enumeration, capture via server spoofing (MITM), and phishing.


* **Dictionary Attacks:** Attackers pre-compute a database of hashes for common dictionary words.


```text
for (each Word in Dictionary) do
  store (DB, Word, hash(Word))

```


* **The Salt Defense:** To counter dictionary and rainbow table attacks, servers generate a random, unpredictable, long "salt" unique to each user ($salt_{UID}$). The password hash is computed as $HP_{UID} = h(\text{pwd} \ \vert{}\vert{} \ salt_{UID})$. This requires an attacker to pre-compute a database for every possible salt, rendering the attack computationally infeasible.


* **Linux Implementation Example:** Linux passwords moved from `/etc/passwd` (world-readable) to `/etc/shadow` (system readable only). They are stored in the format `$id$salt$hashedpwd`. The ID defines the hash function (e.g., $1 = \text{MD5}$, $5 = \text{SHA-256}$, $6 = \text{SHA-512}$, $y = \text{yescrypt}$).



### 5. Challenge-Response Authentication (CRA)

A challenge (usually a random nonce to prevent replay attacks) is sent to the claimant, who computes a response using a secret and a non-invertible function $f$.

* **Symmetric CRA:** Both client and verifier share a secret key $K_{ID}$. The claimant calculates $\text{response} = f(K_{ID}, \text{challenge})$. Hashes (SHA-2) or HMACs (used in TLS) are common for $f$. The Verifier must know $K_{ID}$ in cleartext, though protocols like SCRAM solve this by using hashed passwords at the verifier.


* **Asymmetric CRA:** The strongest mechanism, requiring no secret storage at the verifier.


* *Method A:* The claimant signs a challenge $C$ with their private key $Kpri.ID$.


* *Method B:* The verifier encrypts a nonce $R$ with the claimant's public key; the claimant decrypts it with their private key to reveal $R$.


* *Drawbacks:* Computationally slower, relies on PKI (Public Key Infrastructure) requiring trusted roots and revocation lists, and the list of valid users must be protected for integrity.





### 6. One-Time Passwords (OTP)

A password valid for only one authentication run, neutralizing sniffing attacks.

* **Time-Based OTP (TOTP):** The password depends on time $t$ and a secret $S_{ID}$.


* Requires clock synchronization (via NTP or mobile networks) and tracks time-shifts.


* Verification requires a time-slot window: $X == p(ID,t) \ \vert{}\vert{} \ X == p(ID,t-1) \ \vert{}\vert{} \ X == p(ID,t+1)$.


* *RSA SecurID:* A proprietary hardware/software token implementation of TOTP that generates a 60-second token-code. Users transmit `user, PIN, token-code`. The verifier (ACE server) checks the token against $TC_{-1}$, $TC_{0}$, and $TC_{+1}$.


* *TOTP Standard (RFC-6238):* Calculates counter based on elapsed time steps.
$C = \lfloor (T - T0) / TS \rfloor$
Where $T0$ is the Unix epoch, $T$ is the current unix time, and $TS$ is the time step (default 30 seconds).




* **Event-Based OTP (HOTP):** A new password is generated via a monotonic integer counter $C$ and secret $K$.


* Accommodates desynchronization if the user accidentally presses the button multiple times.


* *HOTP Standard (RFC-4226):* Uses SHA1 by default.
$HOTP(K,C) = sel(HMAC\text{-}h(K,C)) \ \& \ 0x7FFFFFFF$
$HOTP\text{-}code = HOTP(K,C) \pmod{10^N}$




* **Out-of-Band (OOB) OTP:** The server generates the OTP and transmits it to the user via an alternate channel (e.g., SMS to a mobile phone).



### 7. Biometric Authentication Systems

* **Characteristics:** Measures physical traits (fingerprint, face, iris, hand geometry, retina), behavioral traits (gait, typing rhythm, mouse patterns), or mixed traits (voice).


* **Errors:**
* **False Acceptance Rate (FAR):** An imposter's sample is wrongly declared a match.


* **False Rejection Rate (FRR):** A legitimate user's sample is wrongly rejected (due to wounds, emotions, etc.).


* These rates overlap and depend on a tuned acceptance threshold based on security needs.




* **Drawbacks:** Intrusive technologies cause "Big Brother" privacy syndrome; compromised data cannot be replaced; high development costs due to a lack of standard APIs.



### 8. FIDO (Fast IDEntity Online)

An industry standard creating a passwordless (biometric) or strong 2nd-factor user experience using personal devices capable of asymmetric cryptography.

* **Components:** UAF (Universal Authentication Framework), U2F (Universal 2nd Factor), and ASM (Authenticator-Specific Module). FIDO 2.0 incorporates the W3C Web Authentication JS API (WebAuthn) and CTAP (Client to Authenticator Protocol) to interface platforms with roaming authenticators via USB, Bluetooth, or NFC.


* **Security & Privacy:** Uses asymmetric cryptography with no shared secrets on the server. Biometric data never leaves the local device. Phishing is prevented because the authentication response signs the Relying Party's specific identity. Privacy is maintained through strict non-linkability: a unique key-pair is generated for every registration, preventing cross-service or cross-account tracking.



---

### Practical Exercises

**Exercise 1: Password Verification with Salt**

1. **Scenario:** The Verifier receives `UID = "alice"` and `pwd = "myP@ssw0rd"`.


2. **Lookup:** The server queries its database for "alice" and retrieves her stored digest $HP_{UID}$ and specific salt $salt_{UID}$.


3. **Computation:** The server calculates the hash of the provided password combined with the stored salt: $HP^{\prime} = h(\text{"myP@ssw0rd"} \ \vert{}\vert{} \ salt_{UID})$.


4. **Validation:** The server evaluates `if (HP' == HPUID)`. If true, authentication succeeds; otherwise, it fails.



**Exercise 2: Desynchronization Handling in Event-Based OTP**

1. **Scenario:** A user's hardware token has been accidentally pressed twice while in their pocket. The server expects counter $C = 10$, but the user's device is now at $C = 12$. The user inputs the generated OTP $X$.


2. **Server Check:** The verifier receives $X$ and evaluates an authentication window:


* $X == p(ID, 10)$? (Fails)
* $X == p(ID, 11)$? (Fails)
* $X == p(ID, 12)$? (Succeeds)


3. **Result:** Authentication succeeds, and the server resynchronizes its expected counter for the user to $13$.



---

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Authentication & Security Systems Quiz</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: auto; padding: 20px; background-color: #f4f4f9; }
        .question-card { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h3 { margin-top: 0; }
        .options { margin-bottom: 15px; }
        .options label { display: block; margin-bottom: 8px; cursor: pointer; }
        button { background: #0056b3; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #004494; }
        .feedback { display: none; padding: 15px; margin-top: 15px; border-radius: 5px; }
        .correct { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .incorrect { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>

    <h1>Authentication Systems Expert Quiz</h1>
    <p>Test your knowledge on authentication techniques, protocols, and FIDO standards.</p>

    <div id="quiz-container"></div>
    <button onclick="submitQuiz()">Submit Answers</button>

    <script>
        const quizData = [
            {
                question: "1. According to the foundational definitions, what specific question does 'Identification' answer?",
                options: ["Are you who you claim to be?", "Who are you?", "What are your privileges?", "Can you access this resource?"],
                answer: 1,
                explanation: "Identification establishes an identity from available information, providing an answer for 'Who are you?', whereas authentication answers 'Are you who you claim to be?'"
            },
            {
                question: "2. Which of the following represents an 'Inherence' authentication factor?",
                options: ["A static password", "A smart card", "A fingerprint", "A physical token"],
                answer: 2,
                explanation: "Inherence refers to 'something the user is', which includes biometric characteristics such as fingerprints, facial patterns, or retinal blood vessel patterns."
            },
            {
                question: "3. In the NIST SP800.63B digital authentication model, which entity verifies and stores associated attributes and issues the user credential?",
                options: ["The Relying Party", "The Verifier", "The Claimant", "The Credential Service Provider (CSP)"],
                answer: 3,
                explanation: "The Credential Service Provider (CSP) is responsible for enrolling the user, verifying attributes, and issuing the credential and authenticator."
            },
            {
                question: "4. Why is using a biometric factor considered highly risky if it is compromised?",
                options: ["It requires heavy server processing", "It cannot be replaced", "It relies on network time protocol", "It requires asymmetric cryptography"],
                answer: 1,
                explanation: "Biometric characteristics cannot be replaced when compromised (e.g., you cannot change your fingerprint if stolen), which is why they are primarily recommended only for local authentication."
            },
            {
                question: "5. What is the primary purpose of a 'salt' in password-based authentication?",
                options: ["To encrypt the network transmission", "To enforce password length requirements", "To introduce an unpredictable variation that counters dictionary and rainbow table attacks", "To synchronize the client and server clocks"],
                answer: 2,
                explanation: "A salt is a long, random variation added to the password before hashing. It forces attackers to pre-compute a dictionary for every possible salt, making dictionary and rainbow table attacks nearly impossible."
            },
            {
                question: "6. In Linux systems, passwords migrated from /etc/passwd to /etc/shadow. How does modern Linux denote the specific hash function used (e.g., SHA-512) in the shadow file?",
                options: ["Using the crypt() prefix", "Using the $id$ parameter in the password string", "Using a separate lookup database", "By dynamically padding the string length"],
                answer: 1,
                explanation: "Linux stores passwords in the form '$id$salt$hashedpwd', where the 'id' specifies the hash function used (e.g., 6 for SHA-512)."
            },
            {
                question: "7. In a symmetric Challenge-Response Authentication (CRA) system, what is a major vulnerability regarding the Verifier?",
                options: ["The Verifier must maintain a PKI certificate", "The Verifier relies entirely on the Relying Party", "The Verifier must know the shared secret key in cleartext", "The Verifier must generate an encrypted nonce"],
                answer: 2,
                explanation: "Symmetric CRA requires the Verifier to store the shared secret key ($K_{ID}$) in cleartext, creating a vulnerability against database attacks unless mitigations like SCRAM are used."
            },
            {
                question: "8. An asymmetric Challenge-Response Authentication mechanism requires the claimant to do what to prove their identity?",
                options: ["Send an SMS back to the server", "Calculate an HMAC over a counter", "Sign the challenge using their private key or decrypt a nonce", "Provide a fingerprint match to the Verifier"],
                answer: 2,
                explanation: "In asymmetric CRA, the claimant responds to a challenge by signing it with their private key, or by decrypting a random nonce encrypted by the Verifier using the claimant's public key."
            },
            {
                question: "9. Why does Time-based OTP (TOTP) require an 'authentication window' at the Verifier?",
                options: ["To prevent brute-force dictionary attacks", "To accommodate slight clock desynchronizations between client and server", "To allow multiple users to authenticate at once", "To process biometric data algorithms"],
                answer: 1,
                explanation: "Because clocks may not be perfectly synchronized, the Verifier accepts passwords generated in the current time slot, as well as the immediate previous or next slots ($X==p(ID,t) \vert{}\vert{} X==p(ID,t-1) \vert{}\vert{} X==p(ID,t+1)$)."
            },
            {
                question: "10. Which OTP method directly resolves the issue of temporal windows preventing frequent (multiple per minute) authentications?",
                options: ["Event-based OTP (HOTP)", "OOB OTP", "RSA SecurID", "Time-based OTP with smaller intervals"],
                answer: 0,
                explanation: "Event-based OTP generates a new password on demand based on a monotonic counter, allowing for frequent authentication runs without being locked out by a fixed time slot."
            },
            {
                question: "11. Look at the HOTP formula: HOTP(K,C) = sel(HMAC-h(K,C)) & 0x7FFFFFFF. Why is the 0x7FFFFFFF bitmask applied?",
                options: ["To pad the number to 6 digits", "To extract exactly 4 bytes", "To set the most significant bit (MSB) to 0, avoiding signed integer interpretation problems", "To encrypt the counter data"],
                answer: 2,
                explanation: "The bitmask 0x7FFFFFFF sets the most significant bit to 0, ensuring the extracted binary value is always interpreted as a positive integer."
            },
            {
                question: "12. In biometric systems, what does the False Rejection Rate (FRR) represent?",
                options: ["An imposter successfully authenticating", "A legitimate user's sample failing to match their own template", "The speed at which a system processes fingerprints", "The inability of the system to capture behavioral traits"],
                answer: 1,
                explanation: "FRR occurs when a legitimate user is incorrectly denied access, for instance due to variable biological characteristics like a wounded finger or an emotion-altered voice."
            },
            {
                question: "13. You are designing an authentication architecture where biometric data must be verified. Under the FIDO standard, where is this biometric verification performed?",
                options: ["On the FIDO backend server", "On the Relying Party application server", "Strictly locally on the user device", "Within the Credential Service Provider's database"],
                answer: 2,
                explanation: "In FIDO architecture, biometric data is used purely as a local authentication method to unlock cryptographic keys on the device. The biometric data never leaves the user device."
            },
            {
                question: "14. How does the FIDO standard specifically prevent phishing attacks?",
                options: ["By relying on hardware tokens that cannot be lost", "By utilizing asymmetric cryptography where the authentication response signs the specific Relying Party's identity", "By enforcing 8-character minimum passwords", "By generating complex CAPTCHAs"],
                answer: 1,
                explanation: "FIDO prevents phishing because the generated authentication response is a digital signature over various data, including the precise identity of the Relying Party. A response generated for a fake site cannot be reused on the real site."
            },
            {
                question: "15. What ensures non-linkability (privacy) among different services used by the same user in the FIDO standard?",
                options: ["A unified, global private key stored in the cloud", "Frequent password changes enforced by the protocol", "The generation of a new, unique key-pair for every registration", "Anonymizing the user's IP address during registration"],
                answer: 2,
                explanation: "FIDO generates a new, unique key-pair for each individual service and account during registration, ensuring that different services cannot link a user's accounts together."
            },
            {
                question: "16. In the RSA SecurID architecture, what is the 'duress code'?",
                options: ["An emergency password to unlock the database", "A special PIN used to generate an alarm if the user is forced to authenticate under threat", "The counter tracking consecutive login failures", "The 12-bit salt prefix for the token"],
                answer: 1,
                explanation: "The duress code is a specific PIN the user can enter to successfully authenticate while simultaneously alerting the system administrators that they are operating under coercion or threat."
            },
            {
                question: "17. Which protocol in FIDO 2.0 connects the local platform (like a laptop) to roaming authenticators (like USB, NFC, or Bluetooth devices)?",
                options: ["UAF", "ASM", "CTAP (Client to Authenticator Protocol)", "WebAuthn JS API"],
                answer: 2,
                explanation: "CTAP (Client to Authenticator Protocol) is the standard in FIDO 2.0 that allows browsers and operating systems to communicate with external/roaming authenticators over USB, Bluetooth, or NFC."
            },
            {
                question: "18. A Google Authenticator instance calculates a TOTP code. If the default TS (time step) parameter is strictly followed, how often does the counter C increment?",
                options: ["Every 10 seconds", "Every 30 seconds", "Every 60 seconds", "Every 120 seconds"],
                answer: 1,
                explanation: "According to the RFC-6238 standard and Google Authenticator defaults, the time step (TS) is 30 seconds, so the counter increments every 30 seconds from the Unix epoch."
            },
            {
                question: "19. Which of the following is a primary risk of Multi-Factor Authentication (MFA) when using a PIN to protect an authenticator?",
                options: ["The biometric algorithm may degrade over time", "A weak locking mechanism with no protection against multiple guess attempts could expose the OTP generation", "The server must store the private key", "OOB transmissions block network traffic"],
                answer: 1,
                explanation: "A major risk when protecting an authenticator with a PIN is if the lock mechanism is weak or lacks protection against multiple unlock attempts, making brute-forcing the PIN viable."
            },
            {
                question: "20. What is a significant drawback of asymmetric Challenge-Response Authentication compared to symmetric CRA?",
                options: ["It requires the Verifier to store cleartext passwords", "It is computationally slower and heavily relies on Public Key Infrastructure (PKI) management", "It is vulnerable to standard dictionary attacks", "It only supports hardware tokens"],
                answer: 1,
                explanation: "Asymmetric CRA provides the strongest security but is slower than symmetric hashing/encryption and requires dealing with PKI issues, such as trusted roots and revocation lists."
            }
        ];

        const container = document.getElementById('quiz-container');

        quizData.forEach((q, index) => {
            const card = document.createElement('div');
            card.className = 'question-card';
            
            const questionText = document.createElement('h3');
            questionText.innerText = q.question;
            card.appendChild(questionText);

            const optionsDiv = document.createElement('div');
            optionsDiv.className = 'options';
            
            q.options.forEach((opt, optIndex) => {
                const label = document.createElement('label');
                const radio = document.createElement('input');
                radio.type = 'radio';
                radio.name = 'q' + index;
                radio.value = optIndex;
                
                label.appendChild(radio);
                label.appendChild(document.createTextNode(' ' + opt));
                optionsDiv.appendChild(label);
            });
            card.appendChild(optionsDiv);

            const feedbackDiv = document.createElement('div');
            feedbackDiv.id = 'feedback-' + index;
            feedbackDiv.className = 'feedback';
            card.appendChild(feedbackDiv);

            container.appendChild(card);
        });

        function submitQuiz() {
            quizData.forEach((q, index) => {
                const selected = document.querySelector(`input[name="q${index}"]:checked`);
                const feedbackDiv = document.getElementById('feedback-' + index);
                
                if (selected) {
                    const selectedValue = parseInt(selected.value);
                    if (selectedValue === q.answer) {
                        feedbackDiv.className = 'feedback correct';
                        feedbackDiv.innerHTML = `<strong>Correct!</strong> <br><br><em>Motivation/Explanation:</em> ${q.explanation}`;
                    } else {
                        feedbackDiv.className = 'feedback incorrect';
                        feedbackDiv.innerHTML = `<strong>Incorrect.</strong> <br><br><em>Motivation/Explanation:</em> ${q.explanation}`;
                    }
                    feedbackDiv.style.display = 'block';
                } else {
                    feedbackDiv.className = 'feedback incorrect';
                    feedbackDiv.innerHTML = `<strong>No answer selected.</strong> <br><br><em>Motivation/Explanation:</em> ${q.explanation}`;
                    feedbackDiv.style.display = 'block';
                }
            });
        }
    </script>
</body>
</html>

```