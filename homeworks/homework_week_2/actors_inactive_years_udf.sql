-- Create a Python UDF to compute inactive years based on an array of active years
CREATE OR REPLACE FUNCTION javierchiesa.get_inactive_years(active_years ARRAY) 
RETURNS ARRAY
LANGUAGE PYTHON
HANDLER = 'get_inactive_years'
RUNTIME_VERSION = '3.11'
AS
$$
def get_inactive_years(active_years):
    if not active_years:
        return []  -- ⬅️ If input is empty, return an empty list

    active_years = list(set(int(y) for y in active_years))  -- ⬅️ Remove duplicates and ensure integers
    min_year = min(active_years)
    max_year = max(active_years)

    full_range = set(range(min_year, max_year + 1))  -- ⬅️ Generate all years from first to last film

    inactive_years = sorted(full_range - set(active_years))  -- ⬅️ Find missing years
    return inactive_years
$$;


-- Step 1: De-duplicate the dataset by actor and year
WITH deduped AS (
    SELECT 
        actor_id,
        actor,
        year
    FROM bootcamp.actor_films
    GROUP BY ALL
    ORDER BY actor_id, year
),

-- Step 2: Aggregate all active years into an array per actor
combined AS (
    SELECT 
        actor_id,
        actor,
        ARRAY_AGG(year) AS active_years  -- ⬅️ Collect all years the actor made a film
    FROM deduped
    GROUP BY actor_id, actor
)

-- Step 3: Apply the Python UDF to compute the list of missing years
SELECT 
    actor_id,
    actor,
    get_inactive_years(active_years) AS inactive_years  -- ⬅️ Call the UDF to get inactive years
FROM combined;
