-- Creates a Python UDF that uses the external package 'python-Levenshtein'
-- This function calculates the Levenshtein distance between two names
CREATE OR REPLACE FUNCTION javierchiesa.get_levenshtein_distance(name_one VARCHAR, name_two VARCHAR)
RETURNS INT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('python-Levenshtein')  -- ⬅️ Declare the use of the external package
HANDLER = 'get_levenshtein_distance'
AS
$$
from Levenshtein import distance  -- ⬅️ Import the distance function from the package

def get_levenshtein_distance(name_one, name_two):
    return distance(name_one, name_two)  -- ⬅️ Return the Levenshtein distance between the two names
$$;


-- Step 1: CTE that retrieves a distinct list of actors by actor_id and name
WITH actor AS (
    SELECT actor_id, actor
    FROM bootcamp.actor_films
    GROUP BY actor_id, actor  -- ⬅️ Group by ID and name to remove duplicates
),

-- Step 2: CTE that calculates the Levenshtein distance between each pair of different actors
distance AS (
    SELECT 
        a1.actor AS actor_one,  -- ⬅️ First actor
        a2.actor AS actor_two,  -- ⬅️ Second actor
        get_levenshtein_distance(a1.actor, a2.actor) AS levenshtein_distance  -- ⬅️ Distance between both names
    FROM actor a1 
    JOIN actor a2 ON a1.actor_id != a2.actor_id  -- ⬅️ Avoid comparing an actor with themselves
)

-- Step 3: Filters only name pairs considered "similar"
SELECT *
FROM distance
WHERE levenshtein_distance <= 3;  -- ⬅️ Names with a distance of 3 or less are considered similar
