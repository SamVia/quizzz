## 1. Environment and Initial Setup

The environment for exploring Software-Defined Networking (SDN) is pre-configured in the 'ONOS' CrownLabs Virtual Machine.

* **ONOS Cluster Reset**: Activating the "Setup ONOS Cluster" desktop icon resets the cluster to its initial state, opening the ONOS Command Line Interface (CLI) upon completion.


* **ONOS Web GUI**: Accessible via the "ONOS GUI" desktop icon. The default credentials are user `"onos"` and password `"rocks"`.


* **Virtual Network Topology**: The exercises utilize a spine-leaf physical topology. This specific topology consists of two spine switches and four leaf switches, with five hosts connected to each individual leaf.


* **Mininet Operations**: The network is created by double-clicking the "Spine Leaf Topology" desktop icon. To destroy the network, type `Ctrl-D` or `exit` within the Mininet prompt.



## 2. ONOS Graphical User Interface (GUI) Controls

The ONOS GUI provides a comprehensive set of hotkeys for interacting with the network visualization, accessible by pressing the Slash (`/`) key to pull up the Quick Help cheat sheet overlay pane.

* **`\`**: Show / hide Quick Help


* **`/`**: Show / hide Quick Help


* **`Esc`**: Dismiss dialog or cancel selections


* **`T`**: Toggle theme


* **`I`**: Toggle ONOS instances panel


* **`O`**: Toggle ONOS summary panel


* **`D`**: Disable / enable details panel


* **`H`**: Toggle host visibility


* **`M`**: Toggle offline visibility


* **`P`**: Toggle port highlighting


* **`Dash`**: Show bad links


* **`B`**: Toggle background geo map


* **`G`**: Select background geo map


* **`S`**: Toggle sprite layer


* **`X`**: Reset node locations


* **`Z`**: Toggle oblique view (experimental)


* **`N`**: Cycle node layers


* **`L`**: Cycle device labels


* **`Shift-L`**: Cycle host labels


* **`U`**: Unpin node (hover mouse over)


* **`R`**: Reset pan / zoom


* **`E`**: Equalize mastership roles (forces mastership re-balancing, dividing devices roughly equally between nodes)


* **`Dot`**: Toggle Toolbar


* **`Q`**: Cancel traffic monitoring


* **`A`**: Monitor all traffic


* **`F`**: Show device link flows


* **`V`**: Show all related intents (shows paths provisioned by intents passing through the currently selected node)


* **`L-arrow`**: Show previous related intent


* **`R-arrow`**: Show next related intent


* **`W`**: Monitor traffic of selected intent



**Mouse Interactions:**

* **click**: Select the item and show details


* **shift-click**: Toggle selection state


* **drag**: Reposition (and pin) device / host


* **cmd-scroll**: Zoom in / out


* **cmd-drag**: Pan



## 3. ONOS Command Line Interface (CLI)

The ONOS CLI allows for deep inspection and configuration of the network state, offering autocompletion by pressing the `<TAB>` key. Use `help onos` for an exhaustive list of commands, or `[cmd] --help` for specific command details.

### 3.1 Initial ONOS Startup Trace

```text
Waiting for onos-1 startup...
Waiting for onos-2 startup...
Waiting for onos-3 startup...
Activating OpenFlow and ProxyARP applications...
Activated org.onosproject.openflow
Activated org.onosproject.proxyarp
Welcome to Open Network Operating System (ONOS)!

```

### 3.2 Basic Inspection Commands

**`devices`**: Lists all devices currently known in the system. Output attributes include `id`, `available` (boolean indicating if the device is up), `role` (e.g., MASTER, STANDBY), `type`, `mfr`, `hw`, `sw`, `driver`, `channelId`, `managementAddress`, `name`, and `protocol`.

```text
onos> devices
id=of:0000000000000001, available=true, local-status=connected 41m31s ago, role=
STANDBY, type=SWITCH, mfr=Nicira, Inc., hw=Open vSwitch, sw=2.5.2, serial=None,
driver=ovs, channelId=172.17.0.1:38710, locType=geo, managementAddress=172.17.0.1,
name=Spine-1, protocol=OF_13
id=of:0000000000000002, available=true, local-status=connected 41m31s ago, role=
STANDBY, type=SWITCH, mfr=Nicira, Inc., hw=Open vSwitch, sw=2.5.2, serial=None,
driver=ovs, channelId=172.17.0.1:38728, locType=geo, managementAddress=172.17.0.1,
name=Spine-2, protocol=OF_13
id=of:000000000000000b, available=true, local-status=connected 41m31s ago, role=
STANDBY, type=SWITCH, mfr=Nicira, Inc., hw=Open vSwitch, sw=2.5.2, serial=None,
driver=ovs, channelId=172.17.0.1:38702, locType=geo, managementAddress=172.17.0.1,
name=Leaf-1, protocol=OF_13
id=of:000000000000000c, available=true, local-status=connected 41m31s ago, role=
MASTER, type=SWITCH, mfr=Nicira, Inc., hw=Open vSwitch, sw=2.5.2, serial=None,
driver=ovs, channelId=172.17.0.1:38730, locType=geo, managementAddress=172.17.0.1,
name=Leaf-2, protocol=OF_13
id=of:000000000000000d, available=true, local-status=connected 41m31s ago, role=
MASTER, type=SWITCH, mfr=Nicira, Inc., hw=Open vSwitch, sw=2.5.2, serial=None,
driver=ovs, channelId=172.17.0.1:38720, locType=geo, managementAddress=172.17.0.1,
name=Leaf-3, protocol=OF_13
id=of:000000000000000e, available=true, local-status=connected 41m31s ago, role=
STANDBY, type=SWITCH, mfr=Nicira, Inc., hw=Open vSwitch, sw=2.5.2, serial=None,
driver=ovs, channelId=172.17.0.1:38716, locType=geo, managementAddress=172.17.0.1,
name=Leaf-4, protocol=OF_13

```

**`links`**: Lists discovered links formatted as source device-port pair to destination device-port pair, indicating if the `type` is a `DIRECT` connection.

```text
onos> links
src=of:0000000000000001/1, dst=of:000000000000000b/1, type=DIRECT, state=ACTIVE, expected=false
src=of:0000000000000001/2, dst=of:000000000000000c/1, type=DIRECT, state=ACTIVE, expected=false
src=of:0000000000000001/3, dst=of:000000000000000d/1, type=DIRECT, state=ACTIVE, expected=false
src=of:0000000000000001/4, dst=of:000000000000000e/1, type=DIRECT, state=ACTIVE, expected=false
src=of:0000000000000002/1, dst=of:000000000000000b/2, type=DIRECT, state=ACTIVE, expected=false
src=of:0000000000000002/2, dst=of:000000000000000c/2, type=DIRECT, state=ACTIVE, expected=false

```

**`hosts`**: Lists hosts currently in the system, displaying their `id`, MAC addresses, locations (attached device/port), VLAN, IP addresses, and configuration status.

```text
onos> hosts
id=00:00:00:00:00:01/None, mac=00:00:00:00:00:01, locations=[of:000000000000000b/3], vlan=None, ip(s)=[10.0.0.1], provider=of:org.onosproject.provider.host, configured=false
id=00:00:00:00:00:02/None, mac=00:00:00:00:00:02, locations=[of:000000000000000b/4], vlan=None, ip(s)=[10.0.0.2], provider=of:org.onosproject.provider.host, configured=false
id=00:00:00:00:00:03/None, mac=00:00:00:00:00:03, locations=[of:000000000000000b/5], vlan=None, ip(s)=[10.0.0.3], provider=of:org.onosproject.provider.host, configured=false
id=00:00:00:00:00:04/None, mac=00:00:00:00:00:04, locations=[of:000000000000000b/6], vlan=None, ip(s)=[10.0.0.4], provider=of:org.onosproject.provider.host, configured=false
id=00:00:00:00:00:05/None, mac=00:00:00:00:00:05, locations=[of:000000000000000b/7], vlan=None, ip(s)=[10.0.0.5], provider=of:org.onosproject.provider.host, configured=false
id=00:00:00:00:00:06/None, mac=00:00:00:00:00:06, locations=[of:000000000000000c/3], vlan=None, ip(s)=[10.0.0.6], provider=of:org.onosproject.provider.host, configured=false
id=00:00:00:00:00:07/None, mac=00:00:00:00:00:07, locations=[of:000000000000000c/4], vlan=None, ip(s)=[10.0.0.7], provider=of:org.onosproject.provider.host, configured=false

```

**`paths [src-device] [dst-device]`**: Computes and lists all shortest paths between two specified device nodes, displaying the route and path cost.

```text
onos> paths of:000000000000000e of:000000000000000b
of:000000000000000e/2-of:0000000000000002/4==>of:0000000000000002/1-of:000000000000000b/2; cost=2.0
of:000000000000000e/1-of:0000000000000001/4==>of:0000000000000001/1-of:000000000000000b/1; cost=2.0

```

**`log:tail`**: Monitors the system logger to view outputs from running applications.

### 3.3 Application Management Commands

**`apps -a -s`**: Displays currently active applications.

```text
onos> apps -a -s
*  26 org.onosproject.optical-model        1.15.0   Optical Network Model
*  28 org.onosproject.openflow-base        1.15.0   OpenFlow Base Provider
*  29 org.onosproject.lldpprovider         1.15.0   LLDP Link Provider
*  31 org.onosproject.hostprovider         1.15.0   Host Location Provider
*  33 org.onosproject.drivers              1.15.0   Default Drivers
*  66 org.onosproject.openflow             1.15.0   OpenFlow Provider Suite
* 142 org.onosproject.layout               1.15.0   UI Auto-Layout
* 145 org.onosproject.proxyarp             1.15.0   Proxy ARP/NDP

```

**`app activate [app-name]`**: Activates an application dynamically. The `org.onosproject` prefix can be omitted (e.g., `app activate fwd`).
**`app deactivate [app-name]`**: Deactivates a running application, prompting it to withdraw any flows it has installed.
**`flows -s`**: Checks the flows currently installed on the data-plane by applications.

## 4. Reactive Forwarding vs. Intents

### 4.1 Reactive Forwarding

The Reactive Forwarding application (`org.onosproject.fwd`) is a built-in sample app that installs flows in response to every miss packet that arrives at the controller. When deactivated, endpoints (e.g., `h11` and `h41`) cannot reach each other via ICMP ping because no forwarding flows exist on the data-plane.

```text
mininet> h11 ping h41
PING 10.0.0.16 (10.0.0.16) 56(84) bytes of data.
64 bytes from 10.0.0.16: icmp_seq=1 ttl=64 time=39.6 ms
64 bytes from 10.0.0.16: icmp_seq=2 ttl=64 time=0.263 ms
64 bytes from 10.0.0.16: icmp_seq=3 ttl=64 time=0.058 ms
64 bytes from 10.0.0.16: icmp_seq=4 ttl=64 time=0.061 ms
64 bytes from 10.0.0.16: icmp_seq=5 ttl=64 time=0.065 ms

```

### 4.2 Network Intents

An Intent is an immutable model object detailing an application's request to the ONOS core to alter network behavior.

* **Advantage over explicit flows**: Intents inherently track the state of the network and will automatically reconfigure themselves to satisfy the requested intention.


* **Failure Handling**: If a link goes down, the intent framework attempts to reroute flows onto an alternative path. If no alternative path exists, the intent enters a `failed` state until a path becomes available again.


* **`add-host-intent [mac1/vlan] [mac2/vlan]`**: Submits a Host-to-Host intent to provision a path between two end-station hosts.



```text
onos> add-host-intent 00:00:00:00:00:01/None 00:00:00:00:00:10/None
Host to Host intent submitted:
HostToHostIntent{id=0x0, key=0x0, appId=DefaultApplicationId{id=2, name=org.onosproject.cli}, priority=100, resources=[00:00:00:00:00:01/None, 00:00:00:00:00:10/None], selector=DefaultTrafficSelector{criteria=[]}, treatment=DefaultTrafficTreatment{immediate=[NOACTION], deferred=[], transition=None, meter=[], cleared=false, statTrigger=null, metadata=null}, constraints=[LinkTypeConstraint{inclusive=false, types=[OPTICAL]}], resourceGroup=null, one=00:00:00:00:00:01/None, two=00:00:00:00:00:10/None}

```

* **`intents`**: Displays the current status of all intents, revealing details such as State (e.g., `INSTALLED`), Key, Intent type, Resources, and Constraints.



```text
onos> intents
Id: 0x0
State: INSTALLED
Key: 0x0
Intent type: HostToHostIntent
Application Id: org.onosproject.cli
Resources: [00:00:00:00:00:01/None, 00:00:00:00:00:10/None]
Treatment: [NOACTION]
Constraints: [LinkTypeConstraint{inclusive=false, types=[OPTICAL]}]
Source host: 00:00:00:00:00:01/None
Destination host: 00:00:00:00:00:10/None

```

## 5. Custom Application Development

ONOS allows developers to build custom applications utilizing Maven archetypes.

### 5.1 Project Generation & Compilation

To generate an ONOS template application using the `onos-create-app` tool, the ONOS API version must be specified via environment variables.

```bash
$ export ONOS_POM_VERSION=1.9.0
$ onos-create-app app org.foo foo-app 1.0-SNAPSHOT org.foo.app
$ cd foo-app
$ mvn clean install

```

### 5.2 Application Deployment

The compiled application `.oar` file is uploaded and installed into a running ONOS instance via the REST API using the `onos-app` tool. Appending an exclamation mark (`!`) to the `install` parameter immediately activates the application upon installation.

```bash
$ onos-app 172.17.0.5 install! target/foo-app-1.0-SNAPSHOT.oar

```

### 5.3 ONOS Application Lifecycle and Core Services

Applications define their lifecycle behaviors inside `src/main/java/org/foo/app/AppComponent.java` using `@Activate` and `@Deactivate` annotated methods.
ONOS exposes the `DeviceService` to interact with network devices regardless of their specific southbound interfaces. It offers two main APIs for port metrics: `PortStatistics` (total values) and `PortDeltaStatistics` (values bounded to the delta between two probe intervals).

## 6. Practical Exercises

### Exercise 1: Demonstrating Intent Re-routing

1. Ensure the Reactive Forwarding application is deactivated (`app deactivate fwd`).


2. Provision an intent between hosts `h11` (10.0.0.1) and `h41` (10.0.0.16):


```text
onos> add-host-intent 00:00:00:00:00:01/None 00:00:00:00:00:10/None

```


3. Visualize the intent in the GUI by selecting `Leaf-1` and pressing `V`.


4. Sever the active link between `Spine-2` (s2) and `Leaf-1` (s11) via the Mininet prompt:


```text
mininet> link s2 s11 down

```


5. Observe the GUI: The intent service detects the topology event and provisions connectivity over an alternate path (through the other spine switch) automatically.



### Exercise 2: Building a Port Statistics Application

1. Generate the base `foo-app` archetype, compile it, and delete the `test/` folder to prevent Maven from attempting to run tests on uncompleted code.


2. Implement the full `AppComponent.java` logic below to query `PortDeltaStatistics` using a scheduled timer task:



```java
package org.foo.app;

import org.apache.felix.scr.annotations.Activate;
import org.apache.felix.scr.annotations.Component;
import org.apache.felix.scr.annotations.Deactivate;
import org.apache.felix.scr.annotations.Service;
import org.apache.felix.scr.annotations.Reference;
import org.apache.felix.scr.annotations.ReferenceCardinality;
import org.onosproject.net.device.DeviceService;
import org.onosproject.net.Device;
import org.onosproject.net.DeviceId;
import org.onosproject.net.device.PortStatistics;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.List;
import java.util.TimerTask;
import java.util.Timer;

@Component(immediate = true)
public class AppComponent {

    private final Logger log = LoggerFactory.getLogger(getClass());
    private final String DEVICE = "of:0000000000000002";
    private final int PORT = 3;
    private final int PERIOD = 3;
    private PortStatsReaderTask readerTask;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    protected DeviceService deviceService;

    @Activate
    protected void activate() {
        final Device device = deviceService.getDevice(DeviceId.deviceId(DEVICE));
        log.info("Creating stats reader for port " + PORT + " on device " + device.id());
        readerTask = new PortStatsReaderTask();
        readerTask.period = PERIOD;
        readerTask.device = device;
        readerTask.port = PORT;
        readerTask.schedule();
        log.info("Started");
    }

    @Deactivate
    protected void deactivate() {
        readerTask.timer.cancel();
        log.info("Stopped");
    }

    public class PortStatsReaderTask {
        class Task extends TimerTask {
            @Override
            public void run() {
                List<PortStatistics> portStatisticsList = deviceService.getPortDeltaStatistics(device.id());
                PortStatistics portStats = portStatisticsList.get(port);
                if (portStats != null) {
                    log.info("Port " + port + " on device " + device.id() + " has received " + portStats.bytesReceived() + " bytes");
                }
            }
        }
        
        private long period;
        private Device device;
        private int port;
        private Timer timer = new Timer();
        
        public void schedule() {
            this.timer.schedule(new Task(), 0, period * 1000);
        }
    }
}

```

3. Compile and deploy via `onos-app ... reinstall!`.


4. Open the log stream via `log:tail` to verify output.


5. Generate background traffic inside Mininet using `iperf` to observe dynamic statistic changes:


```text
mininet> bgIperf h11 h41

```



---

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Software-Defined Networking Quiz</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; }
        h1 { text-align: center; color: #2c3e50; }
        .question-card { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .question-title { font-weight: bold; margin-bottom: 15px; font-size: 1.1em; }
        .options-list { list-style-type: none; padding: 0; }
        .option-item { margin-bottom: 10px; }
        label { cursor: pointer; display: flex; align-items: baseline; }
        input[type="radio"] { margin-right: 10px; }
        .feedback { display: none; margin-top: 15px; padding: 15px; border-radius: 5px; font-size: 0.95em; }
        .feedback.correct { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .feedback.incorrect { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .submit-btn { background-color: #007bff; color: white; border: none; padding: 12px 25px; font-size: 1em; border-radius: 5px; cursor: pointer; display: block; width: 100%; margin-top: 20px; }
        .submit-btn:hover { background-color: #0056b3; }
        .explanation-title { font-weight: bold; margin-bottom: 5px; }
        .score-display { text-align: center; font-size: 1.5em; font-weight: bold; margin-top: 30px; display: none; padding: 20px; background: #e9ecef; border-radius: 8px; }
    </style>
</head>
<body>

    <h1>ONOS & SDN Concepts Quiz</h1>
    <form id="quizForm">
        <div id="questions-container"></div>
        <button type="button" class="submit-btn" onclick="submitQuiz()">Submit Quiz</button>
    </form>
    <div id="scoreDisplay" class="score-display"></div>

    <script>
        const quizData = [
            {
                q: "What are the default login credentials for the ONOS Web GUI?",
                options: ["user: admin, password: password", "user: onos, password: rocks", "user: root, password: sdn", "user: onos, password: admin"],
                ans: 1,
                explanation: "The default credentials for the ONOS Web GUI are user 'onos' with password 'rocks'[cite: 3]."
            },
            {
                q: "What physical network topology is utilized for the Mininet virtual network in this tutorial?",
                options: ["Ring topology", "Star topology", "Spine-leaf topology", "Mesh topology"],
                ans: 2,
                explanation: "The network is comprised of a spine-leaf physical topology, specifically using two spine switches and four leaf switches[cite: 3]."
            },
            {
                q: "In the ONOS GUI, which key must be pressed to force mastership re-balancing among nodes?",
                options: ["M key", "R key", "B key", "E key"],
                ans: 3,
                explanation: "To force mastership re-balancing from the GUI, you press the E key, dividing devices roughly equally between nodes[cite: 4, 13]."
            },
            {
                q: "Which ONOS CLI command computes all the shortest paths between two specified device nodes?",
                options: ["routes", "links", "paths", "topology"],
                ans: 2,
                explanation: "The `paths` command takes two arguments (devices) and computes all the shortest paths between them[cite: 6]."
            },
            {
                q: "What is the primary function of the built-in Reactive Forwarding (fwd) application?",
                options: ["To compute BGP routes", "To block unauthorized access", "To monitor link health", "To install flows in response to miss packets"],
                ans: 3,
                explanation: "Reactive Forwarding is a simple application that installs flows in response to every miss packet that arrives at the controller[cite: 6]."
            },
            {
                q: "What happens when you deactivate the Reactive Forwarding app?",
                options: ["The ONOS core crashes", "It withdraws any flows it has installed", "It leaves flows in the data-plane indefinitely", "It switches to proactive mode"],
                ans: 1,
                explanation: "Before stopping itself, the reactive forwarding application automatically withdraws any flows it has previously installed[cite: 7]."
            },
            {
                q: "What is a major advantage of using Intents over explicitly using flow entries?",
                options: ["Intents track network state and reconfigure automatically", "Intents execute faster in the dataplane", "Intents bypass the SDN controller", "Intents do not require applications"],
                ans: 0,
                explanation: "One major advantage of using intents over simply using flow entries is that intents track the state of the network and reconfigure themselves to satisfy the intention (e.g., rerouting if a link fails)[cite: 7]."
            },
            {
                q: "What happens to an Intent if a link goes down and there are NO alternative paths available?",
                options: ["It converts into a flow", "It enters the failed state", "It crashes the controller", "It stays in the INSTALLED state"],
                ans: 1,
                explanation: "If there is no alternative path, the intent enters the failed state and remains there until a path becomes available[cite: 7]."
            },
            {
                q: "Which command provisions an Intent-based path between two specific end-stations?",
                options: ["add-host-intent", "create-flow-intent", "provision-path", "host-connect"],
                ans: 0,
                explanation: "The `add-host-intent` command provisions a host-to-host intent between two end-stations using their MAC addresses[cite: 8]."
            },
            {
                q: "Which key visualizes paths provisioned by intents that pass through a selected node in the GUI?",
                options: ["I key", "V key", "P key", "T key"],
                ans: 1,
                explanation: "Pressing the V key while a node is selected shows paths provisioned by intents that pass through that specific node[cite: 8, 13]."
            },
            {
                q: "What tool is used to generate an ONOS template application?",
                options: ["onos-app-builder", "onos-create-app", "mvn-onos-archetype", "onos-gen"],
                ans: 1,
                explanation: "The `onos-create-app` tool relies on Maven archetypes to generate a base ONOS application[cite: 9]."
            },
            {
                q: "Which environment variable must be exported to indicate the ONOS API version for building applications?",
                options: ["ONOS_API_VERSION", "ONOS_POM_VERSION", "MAVEN_ONOS_VERSION", "ONOS_VERSION_BUILD"],
                ans: 1,
                explanation: "You must export the `ONOS_POM_VERSION` environment variable to indicate the desired version of the ONOS API[cite: 9]."
            },
            {
                q: "What happens when you append an exclamation mark (!) to the install parameter when deploying an app (e.g., `install!`)?",
                options: ["It forces an overwrite of an existing app", "It clears the application logs", "It activates the application immediately after installation", "It bypasses Maven verification"],
                ans: 2,
                explanation: "By using the exclamation mark with the install parameter (e.g., `install!`), the application is activated immediately after being installed[cite: 10]."
            },
            {
                q: "Which ONOS service abstracts attached devices regardless of their southbound interface?",
                options: ["TopologyService", "NodeService", "FlowService", "DeviceService"],
                ans: 3,
                explanation: "The `DeviceService` abstracts devices attached to ONOS, irrespective of the particular southbound interface used[cite: 10]."
            },
            {
                q: "Which Java methods in an ONOS application component are invoked at the start and end of the application's lifecycle?",
                options: ["start() and stop()", "init() and destroy()", "activate() and deactivate()", "setup() and teardown()"],
                ans: 2,
                explanation: "The AppComponent class features `activate()` and `deactivate()` methods invoked respectively at the start and end of the ONOS app life-cycle[cite: 10]."
            },
            {
                q: "Which DeviceService API is specifically bounded to retrieve metrics reflecting the difference between two probe intervals?",
                options: ["PortStatistics", "PortDeltaStatistics", "IntervalStatistics", "DeviceDeltaStats"],
                ans: 1,
                explanation: "The `DeviceService` offers two APIs; data retrieved through `PortDeltaStatistics` is bounded to the delta between two probe intervals[cite: 11]."
            },
            {
                q: "Which command generates background traffic between two hosts within the Mininet prompt?",
                options: ["generateTraffic", "pingAll", "iperf-test", "bgIperf"],
                ans: 3,
                explanation: "You can generate some background traffic between two hosts by using the `bgIperf` tool inside Mininet (e.g., `bgIperf h11 h41`)[cite: 13]."
            },
            {
                q: "What does pressing the Slash (/) key do in the ONOS GUI?",
                options: ["Opens the command line terminal", "Pulls up the Quick Help cheat sheet overlay pane", "Refreshes the topology graph", "Logs the user out"],
                ans: 1,
                explanation: "You can pull up the GUI's cheat sheet at anytime by pressing the Slash (/) to get the Quick Help overlay pane[cite: 13]."
            },
            {
                q: "What command lists all hosts currently detected in the system along with their VLAN and IP information?",
                options: ["hosts", "endpoints", "network-devices", "show-nodes"],
                ans: 0,
                explanation: "The `hosts` command lists hosts, displaying their IDs, MAC addresses, locations, VLANs, and IPs[cite: 5, 6]."
            },
            {
                q: "Which class is extended to create a task for periodically fetching port statistics in the custom application code?",
                options: ["Runnable", "TimerTask", "Thread", "ScheduledService"],
                ans: 1,
                explanation: "The task is automated by declaring a class that extends `java.util.TimerTask` to periodically check statistics[cite: 11, 14]."
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
                    feedbackTitle.innerText = "Correct!";
                } else {
                    feedbackDiv.className = "feedback incorrect";
                    feedbackTitle.innerText = "Incorrect.";
                }
                feedbackText.innerHTML = `<strong>Explanation:</strong> ${item.explanation}`;
            });

            const scoreDisplay = document.getElementById("scoreDisplay");
            scoreDisplay.style.display = "block";
            scoreDisplay.innerText = `You scored ${score} out of ${quizData.length}!`;
            scoreDisplay.scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>

```