# ❄️ Snowflake — Day 2

> This lecture explains how complex data types are modeled in Iceberg and Snowflake, how to choose between them based on structure and compression, and how to implement external functions and API access safely.

---

| Iceberg     | Snowflake   | Comments                                                                               | Example (Iceberg)                                               | Example (Snowflake)                                                                 |
|-------------|-------------|----------------------------------------------------------------------------------------|------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| **Array**   | **Array**   | An array is a list of elements of the same or different types.                        | `array<string>` Example: `['apple', 'banana', 'cherry']`        | `ARRAY` Example: `ARRAY_CONSTRUCT('apple', 'banana', 'cherry')`                     |
| **Map**     | **Map**     | A map stores key-value pairs, similar to a Python dictionary.                         | `map<string, int>` Example: `{'apple': 1, 'banana': 2}`          | `OBJECT` as Map (or `MAP`) Example: `OBJECT_CONSTRUCT('apple', 1, 'banana', 2)`      |
| **Struct**  | **Object**  | Groups multiple fields under one entity.                                              | `struct<first_name:string, last_name:string, age:int>` Example: `{'first_name': 'John', 'last_name': 'Doe', 'age': 30}` | `OBJECT` Example: `OBJECT_CONSTRUCT('first_name', 'John', 'last_name', 'Doe', 'age', 30)` |
| **Anything**| **Variant** | Field can store any type. Iceberg requires strict typing.                             | Iceberg **does not** support dynamic type.                       | `VARIANT` Example: `ARRAY_CONSTRUCT('text', 42, OBJECT_CONSTRUCT('key', 'value'), TRUE)` |

---

## 🔄 Complex Data Types in Snowflake

### Array

- Good for **ordinal** data (e.g. calendar, ranking)
- Enables compression through position-based encoding
- Snowflake: `ARRAY[VARIANT]` → more flexible
- Example: Airbnb used arrays to store nightly prices per listing

### Object

Objects can be:

- **Semi-structured**: like JSON → keys = strings, values = variants
- **Structured**: like Iceberg structs → defined keys and types

> More defined = better compression.

- Max size in Snowflake: **16MB**
- Iceberg supports bigger objects, up to **65,000 keys**

**Use cases:**

- Use **semi-structured** for fast-evolving models
- Use **structured** for performance and compression
- Nest rarely used or related columns

> Airbnb reduced a 97-column table to 7 by nesting and grouping columns

### Map

- Iceberg: less flexible — must be `MAP<VARCHAR, ANY>`
- Use only **one nesting level**
- Good for **changing schemas** without ALTER
- Better compression than semi-structured

### Variant

- Snowflake's chameleon type
- Supports any structure: arrays, objects, scalars

---

## 📉 The Compression Hierarchy

- More structure → better compression:
  - Structured Objects
  - Map
  - Semi-structured Objects
  - Variant

---

## 💪 User Defined Functions (UDFs)

- Custom logic in SQL with Java, Python, JS, Scala

### UDF vs UDAF vs UDTF

- **UDF** → One row in, one out (e.g. `LOWER()`)
- **UDAF** → Many rows in, one out (e.g. `SUM()`)
- **UDTF** → One/many rows in, many out (e.g. stats summary)

**Use cases:**

- Complex logic (e.g. streaks, data gaps)
- External libraries (e.g. OpenAI integration)

---

## 🚨 External API Calls

> Snowflake discourages data from leaving the warehouse (e.g. July breach).

### Steps to call an external API:

1. **Add a network rule**
```sql
CREATE OR REPLACE NETWORK RULE openai_api_access
MODE = EGRESS
TYPE = HOST_PORT
VALUE_LIST = ('api.openai.com');
```

2. **Create a secret**
```sql
CREATE OR REPLACE SECRET openai_api_key
	TYPE = GENERIC_STRING
	SECRET_STRING = 'super-secret-key-shhhh'
```

3. **Create an external access integration**
```sql
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION openai_integration
ALLOWED_NETWORK_RULES = (openai_api_access)
ALLOWED_AUTHENTICATION_SECRETS = (openai_api_key)
ENABLED = TRUE;
```

4. **Create your function**
```sql
CREATE OR REPLACE FUNCTION openai_completion(system_prompt VARCHAR, user_prompt VARCHAR)
RETURNS STRING
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
HANDLER = 'openai_udf'
PACKAGES = ('openai')
EXTERNAL_ACCESS_INTEGRATIONS = (openai_integration)
SECRETS = ('api_key' = openai_api_key)
AS
$$
def openai_udf(system_prompt, user_prompt):
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini"
        messages=messages,
        temperature=0.1
    )

    assistant_reply = response.choices[0].message.content
    return assistant_reply
$$;
```
