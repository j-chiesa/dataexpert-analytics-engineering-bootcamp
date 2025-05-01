# ❄️ Snowflake — Day 2

> This lab dives into using **UDFs for complex logic**, comparing **declarative vs imperative programming** in SQL, and how to safely call **external APIs** in Snowflake.

---

## 🧠 UDFs (User Defined Functions)
> 🏀 **Goal**: Number of players who had 5+ consecutive seasons scoring > 20 pts per game.

### Declarative Programming
```sql
WITH lagged AS (
    SELECT 
        *,
        LAG(pts, 1) OVER (PARTITION BY player_name ORDER BY season) AS pts_last_season
    FROM bootcamp.nba_player_seasons
),
changed AS (
    SELECT 
        *,
        CASE 
            WHEN pts > 20 AND pts_last_season > 20 THEN 0
            ELSE 1
        END AS streak_changed
    FROM lagged
),
identified AS (
    SELECT 
        *,
        SUM(streak_changed) OVER (PARTITION BY player_name ORDER BY season) AS streak_identifier
    FROM changed
)
SELECT 
    player_name, 
    streak_identifier, 
    MIN(season) AS start_season,
    MAX(season) AS end_season,
    COUNT(1) AS num_seasons
FROM identified 
GROUP BY player_name, streak_identifier
HAVING COUNT(1) > 4;
```

📌 Powerful but verbose — becomes complex for multiple metrics.

---

### Imperative Programming with Python UDF

```sql
CREATE OR REPLACE FUNCTION get_longest_streak_javierchiesa(v ARRAY, c VARCHAR, threshold REAL)
RETURNS INTEGER
LANGUAGE PYTHON
HANDLER = 'get_longest_streak'
RUNTIME_VERSION = '3.11'
AS 
$$
def get_longest_streak(v, c, threshold):
    max_streak = 0
    current_streak = 0
    for value in v:
        if value[c.upper()] > threshold:
            current_streak += 1
        else:
            current_streak = 0
        max_streak = max(max_streak, current_streak)
    return max_streak
$$;
```

```sql
WITH sorted AS (
    SELECT *
    FROM bootcamp.nba_player_seasons 
    ORDER BY player_name, season
),
combined AS (
    SELECT 
        player_name,
        ARRAY_AGG(OBJECT_CONSTRUCT(*)) AS v
    FROM sorted
    GROUP BY 1
)
SELECT 
    player_name,
    get_longest_streak_javierchiesa(v, 'pts', 20) AS longest_consecutive_20_pts
FROM combined
WHERE longest_consecutive_20_pts > 4
ORDER BY 2 DESC;
```

✅ Reusable, concise, scalable across multiple streak types.

```sql
WITH sorted AS (
    SELECT *
    FROM bootcamp.nba_player_seasons 
    ORDER BY player_name, season
),
combined AS (
    SELECT 
        player_name,
        ARRAY_AGG(OBJECT_CONSTRUCT(*)) AS v
    FROM sorted
    GROUP BY 1
)
SELECT 
    player_name,
    get_longest_streak_javierchiesa(v, 'pts', 20) AS longest_consecutive_20_pts,
    get_longest_streak_javierchiesa(v, 'reb', 10) AS longest_consecutive_10_reb,
    get_longest_streak_javierchiesa(v, 'ast', 10) AS longest_consecutive_10_ast
FROM combined
ORDER BY 2 DESC;
```

---

## 🌐 External APIs

> Integrating OpenAI API in Snowflake using external access integration.

### Network + Secret + Integration + Function
```sql
CREATE OR REPLACE NETWORK RULE openai_api_access
MODE = EGRESS
TYPE = HOST_PORT
VALUE_LIST = ('api.openai.com');

CREATE OR REPLACE SECRET openai_api_key
TYPE = GENERIC_STRING
SECRET_STRING = 'secret_string';

CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION openai_integration
ALLOWED_NETWORK_RULES = (openai_api_access)
ALLOWED_AUTHENTICATION_SECRETS = (openai_api_key)
ENABLED = TRUE;

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
from openai import OpenAI
import _snowflake

client = OpenAI(api_key='api_key')

def openai_udf(system_prompt, user_prompt):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.1
    )
    return response.choices[0].message.content
$$;
```

### Example: JSON Response Parsing
```sql
WITH extracted AS (
    SELECT
        PARSE_JSON(openai_completion(
            'You are a social media expert looking to categorize content',
            'Please categorize this content: <content> The engineer who asks a stupid question looks dumb for a second. The engineer who doesn\'t ask stupid questions looks dumb for a lifetime #softwareengineering </content> return the following keys in json format: category, virality score, and funniness score. Do not return markdown only return JSON'
        )) AS extracted_data
    FROM bootcamp.linkedin_shares
    LIMIT 1
)
SELECT 
    extracted_data:category,
    extracted_data:funniness_score,
    extracted_data:virality_score,
    *
FROM extracted;
```

📌 Great use case for semi-structured types: `VARIANT` with `PARSE_JSON()`.
