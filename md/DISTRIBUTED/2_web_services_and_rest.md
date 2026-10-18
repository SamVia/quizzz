Here is the master cheat sheet for the "02-WebServicesAndREST.pdf" lecture. I’ve captured every architectural constraint, interaction model, HTTP method matrix, and practical scenario exactly as presented.

## Distributed Services

* **Definition**: An abstraction similar to distributed objects, but with key differences.


* **Differences from Distributed Objects**:
* Services have a larger grain than objects.


* Services are autonomous and long-living entities.


* Services may be made available for use by different clients from different organizations.


* Services enable service composition.





## Service Oriented Architecture (SOA)

* **Core Concept**: Software organized as a set of services.


* **Interfaces**: Services are provided through interfaces that are published, automatically discoverable, and machine-readable.


* **Service Characteristics**:
* Described by a contract made of one or more interfaces.


* Implemented by a single instance that is always available.


* Coarse-grained.


* Loosely coupled.


* Interactions occur via typically asynchronous message exchanges.




* **SOA Architectural Roles & Operations**:
* **Service Provider**: Publishes the service to a locator.


* **Service Locator (Broker)**: Maintains the registry of services.


* **Service Requestor (Client)**: Finds the service via the locator and binds to the provider.





## Web Services (Web APIs)

* **Definition**: Distributed services based on the web (HTTP).


* **Architectural Flavors**: SOA-based (standard or SOAP) web services, and RESTful web services.


* **Web Service Scenarios**:
* **SaaS (Software as a Service)**: Software components made available through the network where a vendor sells usage and manages maintenance internally.


* **Whole Applications**: An entire information system process made available as a web service.


* **Service Integration**: Combining services to create added-value new services (e.g., a travel booking service composed of hotel, flight, and train booking services).


* **Web services marketplace**.




* **Web Service Life Cycle**:
* **Build**: Service design, interface specification, and implementation (or linkage to existing implementations).


* **Deployment**: Installation in the target run-time environment and publishing.


* **Management**: Maintenance of the service.


* **Decommissioning**: Dismissal of the service.





### SOA-based Web Services (SOAP/Standard)

* **Theoretical Model**:
* The Service Provider uses UDDI (SOAP) to **publish** a WSDL to a Registry (Service Locator).


* The Service Requestor uses UDDI (SOAP) to **find** the service.


* The Service Requestor uses SOAP to **bind** directly with the Service Provider.




* **Actual Simplified Model**:
* The Service Requestor executes an HTTP GET to the Service Provider to retrieve the WSDL.


* The Service Requestor then uses SOAP to **bind** with the Service Provider.





### RESTful Web Services

* **Basic Interaction**: The Service Requestor binds directly to the Service Provider using standard HTTP.



---

## The REST Architectural Style

* **Definition**: REpresentational State Transfer (REST) is a way for architecting distributed systems through a set of constraints.


* **Origins**: Introduced by Roy Fielding in his 2000 PhD thesis; implemented concretely by the HTTP protocol and the web.


* **Core Principle**: Based on a typed request/response messaging protocol (like HTTP) that follows five primary constraints.



### The 5 REST Constraints

1. **Client-Server**:
* Ensures separation of roles, creating simplicity.


* Helps with scalability and security.


* Allows servers and clients to be kept simple and evolve independently, even across different organizational domains.




2. **Stateless Interaction Protocol**:
* Session state is kept entirely on the client side.


* Improves visibility and monitoring.


* Improves reliability by simplifying recovery from partial failures.


* Helps with scalability because servers do not need to store session information.


* *Practical Note*: In the actual web, this constraint is not always fully satisfied, as servers often hold session state information.




3. **Protocol Enables Caching**:
* Responses can be labeled as cacheable or non-cacheable.


* Cacheable responses are stored by clients, avoiding redundant interactions.


* Improves network efficiency, scalability, and user-perceived performance (latency).




4. **Fixed (Uniform) Interface**:
* Obtained by setting additional constraints on interface organization.


* Applies a uniform interface across all servers.


* Leads to improved simplicity and observability/openness.




5. **Layered Topology**:
* Corresponds to enabling multi-tier architectures via vertical layering (each layer interacts only with adjacent layers).


* Provides improved simplicity and the possibility to dynamically add functions (like proxy caches or load balancers) which can further improve scalability.





---

## Uniform Interface Details: Resources

* **Key Abstraction**: Server interfaces are resource-oriented.


* **Resource Properties**:
* A concept or information item with time-varying state.


* Identified by a URI.


* Has zero or more representations of different media types.


* Operated on by a fixed set of possible operations (resource methods).


* The protocol allows transferring these representations with metadata.




* **Interaction Rule**: When a client requests an operation, a representation of the resource (current/past/future) may be transferred, but the *actual resource itself is never transferred*; it remains on the server side pointed to by the URI.


* **Example**: Turin Polytechnic (URI `[http://www.polito.it](http://www.polito.it)`) can be represented as an HTML page (`text/html`) or a JPEG picture (`image/jpeg`).



## Operations on Resources (HTTP Methods)

* The fixed HTTP interface offers CRUD (Create, Read, Update, Delete) operations predefined by the protocol.


* Semantics depend on the requested method, request body, request headers (control metadata), and target URL (including query string).


* Results are communicated via the response status code, body, and headers.


* **Parameters**: `POST` and `PUT` carry parameters in their body; `GET` and `DELETE` have no body and carry parameters in the query string.


* **Common Status Codes**: `200 OK`, `201 Created`, `304 Not modified`, `400 Bad request`, `500 Internal server error`.



### HTTP Methods Mapping Table

| Operation | HTTP Request | HTTP Response (if no error) |
| --- | --- | --- |
| **Create** (new resource under `res` or send data for processing) | `POST res` (resource/data representation in body) | URL of new resource created and/or result of processing (in body).

 |
| **Read** (resource `res`) | `GET res` (no body) | Representation of the current state of `res` (in the body).

 |
| **Update** (replace state of `res` with a new one; can create `res`) | `PUT res` (new resource representation in the body) | Description of executed operation (200, 201, or 204 status code).

 |
| **Delete** (resource `res`) | `DELETE res` | [No specific response body detailed, implied standard status code].

 |
| **Read Meta** (read info without transferring representation) | `HEAD res` (no body) | Same as GET but without the body (only headers sent).

 |
| **Read Supported Methods** | `OPTIONS res` (no body) | List of supported methods in the `Allow` header and possibly in the body.

 |
| **Test Connection** (loopback testing / echo) | `TRACE res` | The received request is returned in the body.

 |
| **Partially Update** (apply a patch to `res`) | `PATCH res` (patch to be applied in the body) | Description of executed operation (200, 201, or 204 status code).

 |

### Implied Features of HTTP Methods Matrix

| HTTP method | CRUD operations | Idempotent | Safe | Request body | Cacheable response |
| --- | --- | --- | --- | --- | --- |
| **POST** | C | no | no | yes | (no)

 |
| **GET** | R | yes | yes | no | yes

 |
| **PUT** | U, C | yes | no | yes | no

 |
| **DELETE** | D | yes | no | no | no

 |
| **HEAD** | R | yes | yes | no | yes

 |
| **OPTIONS** | R | yes | yes | no | no

 |
| **TRACE** | - | yes | yes | yes | no

 |
| **PATCH** | U, C | no | no | yes | no

 |

---

## Practical Scenarios & Expressiveness

* RESTful web services are semantically as expressive as SOAP web services, but their style is the exact opposite.


* **REST Style**: Few fixed operations, many resources (constrained).


* **SOAP Style**: Few fixed resources, many operations.



### Practical Exercise 1: A Collection of Items (Courses)

* **Concept**: `courses` represents the collection; `courses/xx` represents a single course.


* `POST courses`: Create a new course with given representation, add to collection, return its URI.


* `GET courses`: Read whole collection.


* `GET courses/xx`: Read only course xx.


* `GET courses?year=1`: Read only first-year courses.


* `PUT courses`: Update whole collection with given representation.


* `PUT courses/xx`: Update only course xx.


* `DELETE courses`: Delete whole collection.


* `DELETE courses/xx`: Delete only course xx.



### Practical Exercise 2: A Distributed Counter

* **Scenario**: A service keeping a counter shared by clients allowing read, increment (by a value), and reset to 0.


* **Design**: A single fixed resource `count` whose state is the current integer value.


* **Mapping**:
* `GET count`: Read the counter value.


* `PUT count` (with `0` as body): Reset the counter to 0.


* `POST count` (with value as body): Increment the counter by the value.





### Practical Exercise 3: The Pizza Shop Service

* **Scenario**: Customers read menus and submit orders; pizza makers process orders.


* **Resources**:
* `menu`: The pizza types and toppings.


* `submittedOrders`: Orders submitted but not yet consumed.


* `consumedOrders`: Already consumed orders.




* **Mapping**:
* `GET menu`: Read the menu.


* `POST submittedOrders` (with Order element as body): Submit an order. *Side effect*: order is added to `submittedOrders`.


* `POST consumedOrders` (with empty body): Consume the next order. *Side effect*: oldest order moves from `submittedOrders` to `consumedOrders`. The response includes the Order.





---

## Service Descriptions & Architecture Models

### Machine-Readable Descriptions

There is no globally accepted standard yet, but main initiatives include:

* **WADL** (Web Application Description Language): Describes resources and their admitted methods/parameters.


* **WSDL 2.0** (with HTTP binding): A standard but more limited (e.g., no description of resources); not fully REST-compliant.


* **SWAGGER (OpenAPI Specification)**: Complete description of resources, operations, parameters, and types. Supported by major SW vendors and is becoming a de-facto standard.


* **Google API Discovery Documents**.



### HATEOAS (Hypermedia As The Engine Of Application State)

* **Concept**: A RESTful web service should operate like a traditional web application.


* **Rules**:
* Interactions are completely stateless (no client-related state on server).


* State information is represented by hyperlinks (conveyed in requests/responses) and stored in the client.


* State changes occur strictly by following hyperlinks.


* Clients never "build" hyperlinks, they only follow the ones included in responses.


* A client only needs to know the URL of the main resource.


* Unlike traditional web apps, the self-describing applications must be machine-intelligible.





### Richardson Maturity Model

Ranks web services based on their compliance with REST constraints:

* **Level 0 (No REST)**: Single resource, HTTP used purely as transport ("tunneling").


* **Level 1 (Resources)**: Multiple resources corresponding to different application entities.


* **Level 2 (HTTP verbs)**: Operations are represented strictly by means of HTTP verbs.


* **Level 3 (Hypermedia controls)**: Hyperlinks are included in responses alongside self-describing features (e.g., options).