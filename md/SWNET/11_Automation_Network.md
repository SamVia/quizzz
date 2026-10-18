## Network Automation Principles and Use Cases

* **Core Principles:** Network automation relies on a unified API (such as a protocol) and unified configuration (such as data models) across different vendors.


* **Data Stores:** It utilizes multiple configuration data stores, specifically candidate, running, and startup.


* **Operations:** Automation ensures transactional configuration changes and includes configuration testing and validation.


* **Initial Device Configuration:** Automation avoids the need to configure each new network box individually.


* **Template Customization:** Configuring a device is not simply copying a file; it often involves customizing a template with fresh parameters, such as unused IP addresses.


* **Configuration Deployment:** Automation enables deploying configuration updates for a service across many devices simultaneously, eliminating the need to target each device individually.


* **Workflow Automation:** Multiple network configurations can be combined to create custom workflows. These workflows leverage one or more "playbooks" and can integrate events that include system and application changes.



## Network Automation Solutions and Recipes

* **Cloud-Derived Solutions (DevOps Tools):** These are configuration management solutions widely used by the DevOps community. Leading tools include Puppet, Chef, Ansible, and Salt. They enable the execution of generic commands on remote devices, such as customizing a virtual machine's configuration upon booting.


* **Network-Oriented Solutions:** These solutions rely on standard protocols and models like NETCONF and YANG.


* **SDN-Derived Solutions:** These utilize Software-Defined Networking controllers like ONOS and OpenDayLight.


* **Proprietary Solutions:** Vendor-specific platforms, such as Cisco NSO, provide tailored automation capabilities.



## Ansible Fundamentals

* **Architecture:** Ansible is an open-source, agentless automation tool.


* **Agentless Advantage:** It eliminates the necessity to deploy and manage agents on target devices. While agents are easily installed on servers, it is difficult or often impossible to install them on network devices like routers and switches. This agentless nature makes Ansible a preferred choice for network administrators.


* **Execution Method:** It exploits the terminal (e.g., "ssh") to send commands to a remote device. Ansible can also be used to invoke NETCONF commands on a remote host or router.


* **First Requirement (Compulsory):** Ansible requires SSH support to log into remote devices and execute commands. It can execute CLI commands or interact with native device APIs such as NETCONF, Arista eAPI, and Cisco onePK.


* **Second Requirement (Very Welcome):** Ansible highly benefits from Python support on the target. It logs into the device, sends a Python module over SSH, executes it, and then removes it. Optionally, the Python module can be kept on the device.


* **Core Ingredients:** Ansible recipes are typically built using Ansible, Python, YAML, and Jinja.


* **Idempotency:** Ansible scripts are idempotent, meaning they can be run multiple times safely. Running an Ansible Playbook multiple times will return the exact same result with no errors.



## YAML (YAML Ain't Markup Language)

* **Definition:** Originally standing for "Yet Another Markup Language," it was renamed to "YAML Ain't Markup Language". It is a human-readable data serialization language commonly used for configuration files.


* **Structure and Alternatives:** Whitespace indentation denotes structure, and common signs (like `:` and `-`) specify elements. YAML is the most human-friendly alternative to XML (which is more formal and derived from SGML) and JSON (which uses braces and brackets instead of indentation).


* **Comments:** Comments in YAML start with the `#` symbol.


```yaml
# debug: false
verbose: true # This flag sets 'verbose' to true

```


* **Key-Value Pairs:** YAML stores data as an unordered map containing keys and associated values. Each pair uses the format `key: value`.


```yaml
minecraft-tag: 'minecraft'
cancelled-tag: 'cancelled'
delay: 120 # This is a number

```


* **Nested Key-Value Pairs:** The value associated with a key can be another map of key-value pairs. The value on the parent line is omitted, and the nested pairs are written on following lines. These nested pairs must be prefixed with at least one more SPACE character than the parent key.


```yaml
alice:
  name: Alice Red
  job: Developer
  skills:
    python: basic
    perl: advanced

```


* **Structured Items:** YAML considers lines prefixed with more spaces than the parent key to be contained inside it. All lines must be prefixed with the exact same amount of spaces to belong to the same structure.


* **Lists:** Lists store a collection of ordered values. Values are not associated with a key, but rather with a positional index based on their specified order. Each item is identified by a dash `-` and must be preceded by the same amount of spaces (at least as many as the parent key).


* **Complex Structures:** YAML supports Maps inside Maps, Lists inside Maps, and Maps inside Lists.


```yaml
mylist2:
  - first item
  - second item
  - key1: value1
    key2: value2

```



## Jinja2 Templating

* **Definition:** Jinja2 is a template engine designed for use with Python. It is similar to Django and is capable of handling Python-like expressions.


* **Variables and Expressions:** Parts of the template marked with `{{ }}` denote variables and expressions. This syntax is used for simple variable replacement, such as a hostname or an IP address octet.


* **Control Structures:** More complex replacement and expansion are achieved using Python-style `for` loops wrapped in `{% %}` syntax.


```jinja2
hostname {{ name }}
interface Loopback0
 ip address 10.0.0.{{ id }} 255.255.255.255

{% for vlan, name in vlans.items() %}
vlan {{ vlan }}
 name {{ name }}
{% endfor %}

```


* **Execution Workflow:** To process a Jinja2 template, a Python script must load the Jinja runtime module, load the template, and invoke the proper action (like "render"). The "render" action replaces and expands the template with variables read from a YAML file, producing a new object that can be printed or manipulated further.



## Ansible Playbooks and Inventories

* **Hierarchy:** An Ansible automation run is defined in a Playbook. A Playbook contains one or more Plays, and each Play contains one or more Tasks.


```yaml
- name: install and start apache
  hosts: webservers
  user: root
  tasks:
    - name: install httpd
      yum: name=httpd state=latest
    - name: start httpd
      service: name=httpd state=running

```


* **Inventories:** Ansible operates against multiple systems simultaneously by selecting target systems from an inventory file. This file is usually saved at `/etc/ansible/hosts`.


* **Hosts and Groups:** A "host" is a remote machine managed by Ansible. Hosts can have individual variables assigned to them and can be organized into bracketed groups (e.g., `[controller]`, `[compute]`). Each host is identified by an IP address or domain name, and optionally a port number for non-default SSH ports.


```ini
[controller]
192.168.206.130

[compute]
192.168.206.131
192.168.206.132

```


* **Execution Commands:** Playbooks are executed from the terminal using the `ansible-playbook` command.
`$ ansible-playbook ntp.yaml`


* **Ad-Hoc Commands:** Single actions can be executed using the `ansible` command without a playbook.
`$ ansible controller -m apt -a "pkg=ntp"`



## Practical Exercises

### Scenario 1: Generating Cisco IOS Configurations using Jinja2 and Python

**Objective:** Create customized configuration files for a set of Cisco routers by merging a Jinja2 template with device-specific data stored in YAML.

**Step 1: Define the Data (YAML)**


Create a file named `yaml_data.yml` containing the specific IP, VLAN, and OSPF parameters.

```yaml
id: 1
name: R1

vlans:
  10: users
  20: voice
  30: management

ospf:
  - network: 10.0.1.0 0.0.0.255
    area: 0
  - network: 10.0.2.0 0.0.0.255
    area: 2
  - network: 10.1.1.0 0.0.0.255
    area: 0

```

**Step 2: Create the Skeleton (Jinja2)**


Create a file named `template.jnj` using variable replacements and for-loops.

```jinja2
hostname {{ name }}
interface Loopback0
 ip address 10.0.0.{{ id }} 255.255.255.255

{% for vlan, name in vlans.items() %}
vlan {{ vlan }}
 name {{ name }}
{% endfor %}

router ospf 1
 router-id 10.0.0.{{ id }}
 auto-cost reference-bandwidth 10000

{% for networks in ospf %}
 network {{ networks.network }} \
  area {{ networks.area }}
{% endfor %}

```

**Step 3: Render the Configuration (Python)**


Write a Python script to load the data and template, then render the final text.

```python
# Import necessary functions from Jinja2 module
from jinja2 import Environment, FileSystemLoader
# Import YAML module
import yaml

# Load data from YAML into Python dictionary
config_data = yaml.load(open('./data_files/yaml_data.yml'))

# Load Jinja2 template
env = Environment (loader = FileSystemLoader('./templates'),
                   trim_blocks=True, lstrip_blocks=True)
template = env.get_template('template.jnj')

# Render the template with data and print the output
print(template.render (config_data))

```

### Scenario 2: Configuring NTP via NETCONF using Ansible

**Objective:** Use Ansible to push a NETCONF XML payload to a device to set an NTP server, and another task to wipe the NTP configuration.

**Step 1: Define the Ansible Playbook**
Create an Ansible YAML configuration leveraging the `netconf_config` module.

```yaml
- name: set ntp server in the device
  netconf_config:
    host: 10.0.0.1
    username: admin
    password: admin
    xml: |
      <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
        <system xmlns="urn:ietf:params:xml:ns:yang:ietf-system">
          <ntp>
            <enabled>true</enabled>
            <server>
              <name>ntp1</name>
              <udp><address>127.0.0.1</address></udp>
            </server>
          </ntp>
        </system>
      </config>

- name: wipe ntp configuration
  netconf_config:
    host: 10.0.0.1
    username: admin
    password: admin
    xml: |
      <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
        <system xmlns="urn:ietf:params:xml:ns:yang:ietf-system">
          <ntp>
            <enabled>false</enabled>
            <server operation="remove">
              <name>ntp1</name>
            </server>
          </ntp>
        </system>
      </config>

```

---

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Automation & System Programming Quiz</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; color: #2c3e50; }
        .question-container { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; display: none; }
        .question-container.active { display: block; }
        .options { list-style-type: none; padding: 0; }
        .options li { background: #e9ecef; margin: 10px 0; padding: 12px; border-radius: 5px; cursor: pointer; transition: background 0.3s ease; }
        .options li:hover { background: #d3d9df; }
        .options li.selected { background: #3498db; color: #fff; }
        .btn-container { display: flex; justify-content: space-between; margin-top: 20px; }
        button { padding: 10px 20px; border: none; border-radius: 5px; background: #2ecc71; color: white; cursor: pointer; font-size: 16px; }
        button:disabled { background: #95a5a6; cursor: not-allowed; }
        .feedback { margin-top: 20px; padding: 15px; border-radius: 5px; display: none; }
        .feedback.correct { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .feedback.incorrect { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .progress { text-align: center; margin-bottom: 20px; font-weight: bold; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 10px; border-radius: 5px; overflow-x: auto; }
        code { font-family: Consolas, Monaco, monospace; }
    </style>
</head>
<body>

    <h1>Network Automation Master Quiz</h1>
    <div class="progress" id="progressIndicator">Question 1 of 20</div>

    <div id="quiz-body"></div>

    <script>
        const questions = [
            {
                question: "According to network automation principles, which data stores are utilized for multiple configuration changes?",
                options: [
                    "Active, Standby, and Backup",
                    "Candidate, Running, and Startup",
                    "Primary, Secondary, and Tertiary",
                    "Volatile, Non-volatile, and Flash"
                ],
                correct: 1,
                explanation: "Network automation principles involve utilizing multiple configuration data stores, specifically the candidate, running, and startup data stores[cite: 2]."
            },
            {
                question: "Which of the following configuration management solutions is classified as 'Proprietary'?",
                options: [
                    "Ansible",
                    "ONOS",
                    "Cisco NSO",
                    "Puppet"
                ],
                correct: 2,
                explanation: "Cisco NSO is identified as a proprietary solution, whereas Puppet and Ansible are DevOps tools, and ONOS is an SDN-derived solution[cite: 4]."
            },
            {
                question: "What is a primary advantage of Ansible being 'agentless' for network automation?",
                options: [
                    "It natively supports the C++ programming language.",
                    "It bypasses firewalls using proprietary routing protocols.",
                    "It eliminates the necessity to deploy and manage agents, which is often impossible on network devices like routers and switches.",
                    "It requires no configuration files or templates to operate."
                ],
                correct: 2,
                explanation: "Ansible eliminates the necessity to deploy and manage agents. While installing agents on a server is easy, it is often difficult or impossible to do so on network devices[cite: 8]."
            },
            {
                question: "What is the compulsory first requirement for Ansible to communicate with remote devices?",
                options: [
                    "A running REST API",
                    "Support for SSH",
                    "An active NETCONF subscription",
                    "Python installed natively"
                ],
                correct: 1,
                explanation: "The first compulsory requirement for Ansible is support for SSH. It uses SSH to log into remote devices and execute commands[cite: 9]."
            },
            {
                question: "How does Ansible optionally utilize Python on a target node?",
                options: [
                    "It converts the Ansible playbook into a compiled Python binary locally before sending.",
                    "It requires the user to manually write Python scripts on the router console.",
                    "It logs into the device, sends a Python module over SSH, executes it, and then removes it.",
                    "It uses Python to establish the SSH connection."
                ],
                correct: 2,
                explanation: "A very welcome requirement for Ansible is Python support: Ansible logs into the device, sends a Python module over SSH, executes it, and then removes it (though optionally, it can be kept)[cite: 9]."
            },
            {
                question: "What does the acronym YAML originally stand for, and what was it renamed to?",
                options: [
                    "Yet Another Markup Language -> YAML Ain't Markup Language",
                    "Young Application Markup Language -> YAML Automated Machine Language",
                    "Yielding Advanced Markup Logic -> Yielding Advanced Module Language",
                    "Yet Another Machine Language -> YAML Ain't Machine Language"
                ],
                correct: 0,
                explanation: "YAML originally stood for 'Yet Another Markup Language', and was later renamed to 'YAML Ain't Markup Language'[cite: 11]."
            },
            {
                question: "In YAML syntax, how are single-line comments denoted?",
                options: [
                    "// This is a comment",
                    "/* This is a comment */",
                    "<!-- This is a comment -->",
                    "# This is a comment"
                ],
                correct: 3,
                explanation: "In YAML, comments start with the '#' sign[cite: 12]."
            },
            {
                question: "Which of the following accurately describes how nested key-value pairs are formatted in YAML?",
                options: [
                    "They must be enclosed in curly braces { }.",
                    "They must be prefixed with at least one more space character than the parent key.",
                    "They must be indented using exactly one Tab character.",
                    "They are separated by semicolons on the same line."
                ],
                correct: 1,
                explanation: "To create nested key-value pairs in YAML, the value is omitted on the parent line, and the following lines must be prefixed with at least one more SPACE character than the key[cite: 13]."
            },
            {
                question: "How does YAML represent an ordered list?",
                options: [
                    "By numbering items sequentially (1., 2., 3.).",
                    "By separating items with commas inside square brackets [ ].",
                    "By identifying each item with a dash sign '-', preceded by the same amount of spaces.",
                    "By using the <list> tag."
                ],
                correct: 2,
                explanation: "In a YAML list, each item is identified by the dash sign '-', with each one preceded by the same amount of spaces prefixing them[cite: 15]."
            },
            {
                question: "What is Jinja2 in the context of network automation recipes?",
                options: [
                    "A Python package used exclusively for secure SSH transfers.",
                    "A template engine designed to be used with Python, capable of handling Python-like expressions.",
                    "A proprietary Cisco protocol for routing configurations.",
                    "A YAML validation linter."
                ],
                correct: 1,
                explanation: "Jinja2 is a template engine designed to be used with Python, similar to Django, and is able to handle Python-like expressions[cite: 16]."
            },
            {
                question: "When writing a Jinja2 template, what syntax is used to define simple variable replacements (e.g., extracting a hostname)?",
                options: [
                    "${ hostname }",
                    "{{ hostname }}",
                    "<% hostname %>",
                    "[[ hostname ]]"
                ],
                correct: 1,
                explanation: "Parts of a Jinja2 template marked with `{{ }}` denote variables and expressions used for simple replacements[cite: 18]."
            },
            {
                question: "Review the following Jinja2 snippet:\n<code>{% for vlan, name in vlans.items() %}\nvlan {{ vlan }}\n name {{ name }}\n{% endfor %}</code>\nWhat does this code accomplish?",
                options: [
                    "It statically creates exactly one VLAN based on the first item in the YAML file.",
                    "It creates an infinite loop that crashes the Python script.",
                    "It iterates over a dictionary named 'vlans', extracting and printing the key and value for each entry.",
                    "It prompts the user in the CLI to manually input a vlan ID and name."
                ],
                correct: 2,
                explanation: "The `{% for ... %}` syntax is used for complex replacement and expansion via Python loops. This specific loop iterates through the items of the 'vlans' dictionary, substituting the variables into the template text[cite: 18]."
            },
            {
                question: "In the standard Python script workflow to generate configurations, what happens after `yaml.load()` and `env.get_template()` are called?",
                options: [
                    "The `template.render()` action is invoked to expand the template with the YAML variables.",
                    "The `ansible-playbook` command is natively executed by Jinja.",
                    "The Python script automatically opens an SSH tunnel.",
                    "The YAML file is deleted from the filesystem."
                ],
                correct: 0,
                explanation: "In the workflow, after the Jinja2 template is loaded, the proper action (e.g., 'render') is invoked on the template, replacing/expanding it with variables read from the YAML file[cite: 16, 20]."
            },
            {
                question: "What is the structural hierarchy inside an Ansible configuration file?",
                options: [
                    "Task -> Playbook -> Play",
                    "Play -> Task -> Playbook",
                    "Playbook -> Play -> Tasks",
                    "Tasks -> Plays -> Modules"
                ],
                correct: 2,
                explanation: "An Ansible configuration is structured as a Playbook, which contains Plays, which in turn contain Tasks[cite: 22]."
            },
            {
                question: "Where is the default Ansible inventory file typically saved, and what is its purpose?",
                options: [
                    "<code>/etc/ansible/hosts</code>; it selects portions of systems (hosts and groups) to execute against.",
                    "<code>/var/log/ansible.log</code>; it records the output of previous playbook runs.",
                    "<code>/usr/bin/ansible</code>; it stores the compiled Python binaries.",
                    "<code>/etc/ssh/sshd_config</code>; it manages the SSH port configurations for remote hosts."
                ],
                correct: 0,
                explanation: "Ansible selects portions of systems listed in its inventory file, which is usually saved in `/etc/ansible/hosts`. Hosts can be organized in groups[cite: 24]."
            },
            {
                question: "What command is used to run a complete Ansible playbook from the terminal?",
                options: [
                    "<code>ansible-run ntp.yaml</code>",
                    "<code>python ntp.yaml</code>",
                    "<code>ansible ntp.yaml</code>",
                    "<code>ansible-playbook ntp.yaml</code>"
                ],
                correct: 3,
                explanation: "To execute a playbook, the `ansible-playbook` command is used, for example: `$ ansible-playbook ntp.yaml`[cite: 25]."
            },
            {
                question: "If an Ansible playbook is run multiple times on the same remote device, what is the expected outcome?",
                options: [
                    "The device configuration will duplicate elements, causing a crash.",
                    "The playbook will return an error stating the resources already exist.",
                    "Ansible will return exactly the same result with no errors, because scripts are idempotent.",
                    "The target device will reboot immediately."
                ],
                correct: 2,
                explanation: "Ansible scripts are idempotent, meaning they can be run safely multiple times. Running the playbook multiple times returns exactly the same result with no errors[cite: 26]."
            },
            {
                question: "Review the following ad-hoc Ansible command:\n<code>$ ansible controller -m apt -a \"pkg=ntp\"</code>\nWhat does this command do?",
                options: [
                    "It runs a single action using the Ansible command-line tool, equivalent to a task ensuring the ntp package is installed via apt.",
                    "It creates a new inventory group named 'controller'.",
                    "It deletes the 'ntp' package from all hosts.",
                    "It triggers a python script named 'apt.py'."
                ],
                correct: 0,
                explanation: "The `ansible` command can run a single action. This specific command corresponds to the task of ensuring the ntp package is installed using the `apt` module[cite: 26]."
            },
            {
                question: "When using the Ansible <code>netconf_config</code> module, how is the configuration payload structured?",
                options: [
                    "As a pure JSON object containing system parameters.",
                    "As an XML block defined within the playbook (e.g., <code>&lt;config&gt;...&lt;/config&gt;</code>).",
                    "As a series of CLI commands like 'config t'.",
                    "As a Jinja2 loop directly inside the target router's memory."
                ],
                correct: 1,
                explanation: "In an Ansible playbook using `netconf_config`, the payload is formatted under the `xml:` key as an XML block wrapped in `<config>` and `<system>` tags."
            },
            {
                question: "In the provided Ansible NETCONF example to wipe NTP configuration, what attribute is added to the server tag?",
                options: [
                    "<code>action=\"delete\"</code>",
                    "<code>operation=\"remove\"</code>",
                    "<code>state=\"absent\"</code>",
                    "<code>mode=\"purge\"</code>"
                ],
                correct: 1,
                explanation: "To wipe the NTP configuration, the NETCONF XML payload includes `<server operation=\"remove\">` around the server name tag."
            }
        ];

        let currentQuestion = 0;
        let selectedOption = null;

        const bodyDiv = document.getElementById('quiz-body');
        const progressIndicator = document.getElementById('progressIndicator');

        function renderQuestion() {
            bodyDiv.innerHTML = '';
            const q = questions[currentQuestion];
            progressIndicator.innerText = `Question ${currentQuestion + 1} of ${questions.length}`;

            const container = document.createElement('div');
            container.className = 'question-container active';

            const questionText = document.createElement('h3');
            questionText.innerHTML = q.question;
            container.appendChild(questionText);

            const optionsList = document.createElement('ul');
            optionsList.className = 'options';

            q.options.forEach((opt, index) => {
                const li = document.createElement('li');
                li.innerHTML = opt;
                li.onclick = () => selectOption(li, index);
                optionsList.appendChild(li);
            });
            container.appendChild(optionsList);

            const feedback = document.createElement('div');
            feedback.className = 'feedback';
            feedback.id = 'feedback-box';
            container.appendChild(feedback);

            const btnContainer = document.createElement('div');
            btnContainer.className = 'btn-container';

            const submitBtn = document.createElement('button');
            submitBtn.innerText = 'Submit';
            submitBtn.id = 'submit-btn';
            submitBtn.disabled = true;
            submitBtn.onclick = () => checkAnswer(submitBtn);

            const nextBtn = document.createElement('button');
            nextBtn.innerText = 'Next Question';
            nextBtn.style.display = 'none';
            nextBtn.id = 'next-btn';
            nextBtn.onclick = () => goNext();

            btnContainer.appendChild(submitBtn);
            btnContainer.appendChild(nextBtn);
            container.appendChild(btnContainer);

            bodyDiv.appendChild(container);
            selectedOption = null;
        }

        function selectOption(liElement, index) {
            const allOptions = document.querySelectorAll('.options li');
            allOptions.forEach(li => li.classList.remove('selected'));
            liElement.classList.add('selected');
            selectedOption = index;
            document.getElementById('submit-btn').disabled = false;
        }

        function checkAnswer(submitBtn) {
            submitBtn.style.display = 'none';
            const allOptions = document.querySelectorAll('.options li');
            allOptions.forEach(li => li.style.pointerEvents = 'none'); 

            const feedback = document.getElementById('feedback-box');
            feedback.style.display = 'block';

            const q = questions[currentQuestion];

            if (selectedOption === q.correct) {
                feedback.className = 'feedback correct';
                feedback.innerHTML = `<strong>Correct!</strong> <p>Motivation/Explanation: ${q.explanation}</p>`;
                allOptions[selectedOption].style.backgroundColor = '#2ecc71';
                allOptions[selectedOption].style.color = '#fff';
            } else {
                feedback.className = 'feedback incorrect';
                feedback.innerHTML = `<strong>Incorrect.</strong> <p>Motivation/Explanation: ${q.explanation}</p>`;
                allOptions[selectedOption].style.backgroundColor = '#e74c3c';
                allOptions[selectedOption].style.color = '#fff';
                allOptions[q.correct].style.backgroundColor = '#2ecc71';
                allOptions[q.correct].style.color = '#fff';
            }

            document.getElementById('next-btn').style.display = 'inline-block';
            
            if (currentQuestion === questions.length - 1) {
                document.getElementById('next-btn').innerText = 'Finish Quiz';
            }
        }

        function goNext() {
            if (currentQuestion < questions.length - 1) {
                currentQuestion++;
                renderQuestion();
            } else {
                bodyDiv.innerHTML = '<div class="question-container active" style="text-align:center;"><h2>Quiz Completed!</h2><p>You have reviewed all 20 network automation questions.</p></div>';
                progressIndicator.style.display = 'none';
            }
        }

        window.onload = renderQuestion;
    </script>
</body>
</html>

```