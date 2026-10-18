## Data Transparency and Encoding

* **Data Transparency**: Protocols must ensure that data are correctly transferred despite the heterogeneity of systems. This transparency is obtained by properly encoding (marshalling) and decoding (unmarshalling) data according to a protocol at the middleware level.


* **Types of Codes**: Codes are defined so that the receiver can separate, validate, and decode messages.


* **Binary Codes**: Send data as raw bits/bytes (e.g., `0110011101...`).


* **Character-Oriented Codes**: Send data as readable text characters (e.g., HTTP `GET` requests).




* **HTTP Encoding Example**: HTTP utilizes a character-oriented solution. Initially, the code is plain ASCII, and the code used in the message body is communicated and negotiated in the HTTP header.


```http
Content-type: application/json; charset=utf-8
Content-encoding: gzip
Content-length: 22456

```




## Abstract Syntaxes and Standard Codes

* Applications typically exploit standard ways for system-independent data representation.


* **Binary solutions**: ASN.1, XDR, Protocol Buffers.


* **Character-oriented solutions**: XML, JSON, YAML.




* **Components of a Standard Code**:
1. A language to define abstract data types (abstract syntax).


2. "Neutral" (system-independent) data representations for any abstract data type defined by the language.


3. A mechanism to correctly separate, validate, and decode data. This may require the receiver to know the data type in advance or to learn the type from the data itself.




* **Why use Abstract Syntaxes?**
* **Language/System Independency**: Programmers can use any programming language (e.g., Java, JavaScript, C++) while libraries automatically translate to/from the language's native data types.


* **Independency from Binary Encoding**: Different binary codes can be used for the same abstract data (e.g., ASN.1 admits different binary codes like BER and DER).


* **Specification and Validation**: They provide unambiguous specifications of interface data, allowing programmers to delegate validation to standard validators. This results in better application security, reliability, robustness, and simpler application code.





### Comparison: Application Validation vs. Abstract Syntax

* **Application-level validation (e.g., `express-validator`)**: Involves no formal specification/documentation, allows only simple checks, and "pollutes" the application code with validation logic.


```javascript
app.post('/user', [
  check('username').isEmail(), // username must be an email
  check('password').isLength({ min: 5 }) // password must be at least 5 chars long
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(422).json({ errors: errors.array() });
  }
});

```



* **Standard Validation limitations**: While powerful, abstract syntaxes are not a panacea; their expressiveness has limits, meaning some complex checks still need to be made within the application logic.



## The JSON Schema Language

* **Overview**: JSON Schema is a language based on JSON itself, where a schema is a JSON object with special meaning. It is an IETF Draft (current version is 2020-12, but the slides refer to `draft-07`).


* **Capabilities**: It is machine-readable, serializable, and can be validated.


* **Definition**: A schema defines a data type, which is a set of valid JSON values and corresponding strings.


* **Base Types**: JSON data types correspond to commonly available programming types: Primitive data (`string`, `boolean`, `number`, `null`), Arrays, and Objects.



### Schema Structure and Meta-Data

* **Structure**: A schema is represented as a JSON object `{...}` that includes meta-data and constraints on what is valid.


* `{}` (Empty object): Everything is valid.


* `true`: Everything is valid.


* `false`: Nothing is valid.




* **Core Meta-data**:
* `$schema`: The schema language version this JSON object refers to (e.g., `"[http://json-schema.org/draft-07/schema](http://json-schema.org/draft-07/schema)"`).


* `$id`: The schema identifier (e.g., `"[http://dsp.polito.it/test1schema.json](http://dsp.polito.it/test1schema.json)"`).




* **Annotation Meta-data**: `title`, `description`, `default`, `examples`.


* **Comments**: `$comment`.



## JSON Schema Constraints by Type

The `type` property defines the allowed data structure type(s) and can be an array of allowed types.

### `string` (Unicode string)

* `minLength`: Minimum string length.


* `maxLength`: Maximum string length.


* `format`: Pre-defined semantic formats including `date`, `time`, `date-time`, `email`, `hostname`, `ipv4`, `ipv6`, `iri`, `uri`, `uri-template`, `uri-reference`, `iri-reference`, `regex`.


* `pattern`: A regular expression the string must match.



### `number` (Real number) and `integer` (Integer number)

* **Rule**: There is no automatic conversion from/to strings. `"type": "number"` validates `123` but fails `"123"`. `"type": "string"` fails `123` but validates `"123"`.


* `multipleOf`: Number must be a multiple of this value.


* `minimum`: Inclusive lower bound.


* `exclusiveMinimum`: Exclusive lower bound.


* `maximum`: Inclusive upper bound.


* `exclusiveMaximum`: Exclusive upper bound.



### `object` (Collection of properties/named typed values)

* **Property Constraints**:
* `properties`: An object whose keys are property names and values are schemas specifying the type of that property.


* `additionalProperties`: Constraints about additional properties not listed in `properties`. If missing, any additional property is valid. If specified, it can be `true` (default, valid), `false` (no additional properties valid), or a schema that any additional property must obey.


* `required`: An array of strings representing names of required properties. If missing, all properties are optional.


* `propertyNames`: A schema the property names must obey (implies the schema type is a string). If missing, all names are admitted.




* **Size Constraints**:
* `minProperties`: Minimum number of properties.


* `maxProperties`: Maximum number of properties.




* **Dependencies** (`dependencies` property):
* **Property dependencies**: If a specified property is present, other explicitly listed properties must also be present. Example: `"firstname": ["lastname"]` means if `firstname` is present, `lastname` must be too.


* **Schema dependencies**: If a specified property is present, the object schema is extended with additional constraints. Example: `"idnum": {"properties": {"age": { "type": "integer", "minimum": 10 }}}` means if `idnum` is present, the `age` property must be at least 10.





### `array` (Ordered list of typed values)

* **Size & Uniqueness**:
* `minItems`: Minimum number of items.


* `maxItems`: Maximum number of items.


* `uniqueItems`: If set to `true`, items must be unique (no duplicates).




* **Item Type Constraints**:
* `items`: If the value is a single schema (object), the array acts as a **list** where *each* item must obey the schema. If the value is an array of schema objects, the array acts as a **tuple** where items must positionally obey their corresponding schemas.


* `additionalItems`: Constrains items allowed *after* a tuple. Can be `true` (default, any allowed), `false` (none allowed), or a schema.


* `contains`: One or more items in the array must obey the provided schema.





### `boolean` (true/false) and `null` (Null value)

* There are no additional constraints for these types.


* **Rule**: No automatic conversion from/to other types. `"type": "boolean"` validates `true` but fails `"true"` and `1`. `"type": "null"` validates `null` but fails `"null"`, `0`, and `false`.



### Enumerations (`enum`)

* `enum`: Specifies the exact allowed values by enumeration using JSON syntax within an array. It can be combined with other type constraints.


```json
"sex": { "enum": ["male", "female"] }

```




## Schema Combination and Conditionals

* **Combinators**:
* `allOf`: Requires validity against *all* sub-schemas.


* `anyOf`: Requires validity against *at least one* sub-schema.


* `oneOf`: Requires validity against *exactly one* sub-schema.


* `not`: Requires *not* being valid against the schema.




* **Conditionals (`if` - `then` - `else`)**:
* If data are valid against $S_{if}$, then data must be valid against $S_{then}$.


* Else, data must be valid against $S_{else}$.




```json
{
  "if": { "type": "integer", "multipleOf": 3},
  "then": { "type": "number", "multipleOf": 5},
  "else": { "type": "number", "multipleOf": 7}
}

```




## Reusing and Extending Schemas

* **References (`$ref`)**: Schemas can be reused using URI-like references to an existing internal or external schema wherever a schema is required.


* **Internal Ref**: Uses a JSON pointer (e.g., `"$ref": "#/definitions/address"`).


* **External Ref**: Points to an external file (e.g., `"$ref": "addressschema.json"`).




* **Extending Schemas**: You achieve extension (adding constraints) by combining a referenced schema with another set of rules, typically using `allOf`.



## Practical Exercises

### Exercise: Extending a Schema

**Scenario**: Write a schema for the billing address that extends the shipping address schema by including another field (`vat` number, which is required).

**Step-by-Step Solution**:

1. Define the base `shippingAddress` as a reusable schema definition.
2. Under `billingAddress`, use `allOf` to inherit the `shippingAddress` definition.
3. In the second part of the `allOf` array, add a new constraint specifying `vat` as a string type and place `vat` in the `required` array.

```json
{
  "definitions": {
    "shippingAddress": {
      "type": "object",
      "properties": {
        "street": { "type": "string" },
        "city": { "type": "string" },
        "country": { "type": "string" }
      }
    }
  },
  "type": "object",
  "properties": {
    "shippingAddress": { "$ref": "#/definitions/shippingAddress" },
    "billingAddress": {
      "allOf": [
        { "$ref": "#/definitions/shippingAddress" },
        {
          "type": "object",
          "properties": {
            "vat": { "type": "string" }
          },
          "required": ["vat"]
        }
      ]
    }
  }
}

```

## Middleware Code Traces

### Schema Validation with Express/ajv

The following C-style (JavaScript/Node.js) code demonstrates validating an API request using JSON Schema in Express middleware:

```javascript
var { Validator, ValidationError } = require('express-json-validator-middleware');
var userSchema = JSON.parse(fs.readFileSync(schemaFileName));
var validator = new Validator({ allErrors: true });
validator.ajv.addSchema(userSchema);
var validate = validator.validate;

app.post('/user', validate({ body: userSchema }), (req, res) => {
    // Application logic here
});

// Error handler for validation errors
app.use(function(err, req, res, next) {
    if (err instanceof ValidationError) {
        res.status(400).send('Invalid request');
        next();
    } else next(err);
});

```