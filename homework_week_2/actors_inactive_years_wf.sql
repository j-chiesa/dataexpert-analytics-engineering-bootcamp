-- Step 1: Get the global minimum and maximum year across the dataset
WITH year_range AS (
    SELECT 
        MIN(year) AS min_year,
        MAX(year) AS max_year
    FROM bootcamp.actor_films
),

-- Step 2: Generate a sequence of all years between the global min and max
year_sequence AS (
    SELECT min_year + SEQ4() AS year
    FROM year_range,
        TABLE(GENERATOR(ROWCOUNT => max_year - min_year + 1))  -- Efficiently generates rows from 0 to (max - min)
),

-- Step 3: Get the min and max year of film activity for each actor
actor_min_max_year AS (
    SELECT 
        actor_id,
        actor,
        MIN(year) AS min_year,
        MAX(year) AS max_year
    FROM bootcamp.actor_films
    GROUP BY actor_id, actor
),

-- Step 4: For each actor, generate all years between their first and last film
actor_year AS (
    SELECT 
        ay.actor_id,
        ay.actor,
        ys.year
    FROM actor_min_max_year ay
    JOIN year_sequence ys ON ys.year BETWEEN ay.min_year AND ay.max_year -- Cross join to pair each actor with each year
    WHERE ay.min_year <= ys.year AND ys.year <= ay.max_year  -- Keep only the actor's active range
),

-- Step 5: Check which of those years had actual film activity and which didn't
actor_inactive_years AS (
    SELECT 
        ay.actor_id,
        ay.actor,
        ay.year AS year_seq,  -- Expected year (in sequence)
        af.year  -- Actual film year (if any)
    FROM actor_year ay
    LEFT JOIN bootcamp.actor_films af 
        ON ay.actor_id = af.actor_id AND ay.year = af.year  -- Match actor-year pairs
    GROUP BY ALL
    ORDER BY actor_id, ay.year
)

-- Step 6: Final output: for each actor, return an array of years where no film was made
SELECT 
    actor_id,
    actor,
    ARRAY_AGG(
        CASE
            WHEN year IS NOT NULL THEN NULL  -- If a film exists for that year, skip it
            ELSE year_seq  -- If not, include it as an inactive year
        END
    ) AS inactive_years
FROM actor_inactive_years
GROUP BY actor_id, actor;
