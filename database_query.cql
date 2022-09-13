CALL apoc.load.json("/Users/julia/.Neo4jDesktop/relate-data/dbmss/dbms-8fde46ba-8bd5-4ada-b98b-8ba69a8028d5/import/test_food.json") YIELD value 
UNWIND keys(value) AS key
MERGE (i: Nutrient {name: value[key].name})

MATCH (n)
DETACH DELETE n

CALL apoc.load.json("/Users/julia/.Neo4jDesktop/relate-data/dbmss/dbms-8fde46ba-8bd5-4ada-b98b-8ba69a8028d5/import/test_food.json") YIELD value 
UNWIND keys(value) AS key
MERGE (i: Nutrient {name: value[key].name,
                    protein: value[key].Protein.Amount,
                    carbohydrate: value[key]["Carbohydrate, by difference"].Amount,
                    fat: value[key]["Total lipid (fat)"].Amount,
                    energy: value[key].Energy.Amount})

{"url_id": 10000, 
"title": "Sweet Honey French Bread", 
"ingridients": [
    {"name": "water", "quantity": 0.75, "unit": "cup", "grams": 180.0}, 
    {"name": "honey", "quantity": 2.0, "unit": "teaspoons", "grams": 40.0}, 
    {"name": "olive oil", "quantity": 2.0, "unit": "teaspoons", "grams": 28.0}, 
    {"name": "salt pork", "quantity": 0.6666666666666666, "unit": "teaspoon", "grams": 0.0}, 
    {"name": "white sauce gravy", "quantity": 0.6666666666666666, "unit": "teaspoon", "grams": 0.0}, 
    {"name": "bread flour", "quantity": 2.0, "unit": "cups", "grams": 0.0}, 
    {"name": "active yeast", "quantity": 1.5, "unit": "teaspoons", "grams": 0.0}, 
    {"name": "honey", "quantity": 1.0, "unit": "tablespoon", "grams": 20.0}], 
"instructions": "1.Add to your bread machine per manufacturer instructions. While bread is baking, drizzle with honey if desired."}

CALL apoc.load.json("/Users/julia/.Neo4jDesktop/relate-data/dbmss/dbms-8fde46ba-8bd5-4ada-b98b-8ba69a8028d5/import/recipes_clean.json") YIELD value 
UNWIND keys(value) AS key
MERGE (j: Recipe {name: value.title,
                  instructions: value.instructions})
WITH j, value 
MERGE(i: Nutrient {name: value.ingridients.name})
MERGE (i) - [:INGRIDIENT_OF] -> (j)                 



CALL apoc.load.json("/Users/julia/.Neo4jDesktop/relate-data/dbmss/dbms-8fde46ba-8bd5-4ada-b98b-8ba69a8028d5/import/recipes_clean.json") YIELD value 
unwind keys(value) AS  it
MERGE (j: Recipe {name: it.title,
                  instructions: it.instructions})
Foreach(ingrid in it.ingridients | Merge(i: Nutrient {name: ingrid.name,}) Merge(r)-[:CONSIST_OF]->(ingrid))
return r




CALL apoc.load.json("/Users/julia/.Neo4jDesktop/relate-data/dbmss/dbms-8fde46ba-8bd5-4ada-b98b-8ba69a8028d5/import/recipes.json") YIELD value 
unwind keys(value) AS  it
MERGE (j: Recipe {name: value.title,
                  instructions: value.instructions})
foreach(ingrid in value.ingridients | Merge(i: Nutrient {name: ingrid.name})  Merge(j)-[:CONSIST_OF {amount: ingrid.grams}]->(i))
return j




CALL apoc.load.json("/Users/julia/.Neo4jDesktop/relate-data/dbmss/dbms-8fde46ba-8bd5-4ada-b98b-8ba69a8028d5/import/recipes.json") YIELD value 
unwind keys(value) AS  it
MERGE (j: Recipe {name: value.title,
                  instructions: value.instructions})
foreach(ingrid in value.ingridients | Merge(i: Nutrient {name: ingrid.name})  Merge(j)-[:CONSIST_OF {amount: ingrid.grams}]->(i))
return j



CALL apoc.load.json("/Users/julia/.Neo4jDesktop/relate-data/dbmss/dbms-8fde46ba-8bd5-4ada-b98b-8ba69a8028d5/import/recipes_clean.json") YIELD value 
unwind keys(value) AS  it
MERGE (j: Recipe {name: value.title,
                  instructions: value.instructions})
foreach(ingrid in value.ingridients | Merge(i: Nutrient {name: ingrid.name})  Merge(j)-[:CONSIST_OF]->(i))
return j