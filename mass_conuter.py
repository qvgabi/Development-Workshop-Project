import time
from jellyfish import damerau_levenshtein_distance, jaro_similarity, jaro_winkler_similarity
from unit_changer import *
import pandas as pd
from tqdm import tqdm
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet

stop_words = set(stopwords.words("english"))

start_time = time.perf_counter()


def name_match_stats(name, names_dictionary):
    best_match_l = {"name": names_dictionary[0], "score": damerau_levenshtein_distance(name, names_dictionary[0])}
    best_match_j = {"name": names_dictionary[0], "score": jaro_similarity(name, names_dictionary[0])}
    best_match_jw = {"name": names_dictionary[0], "score": jaro_winkler_similarity(name, names_dictionary[0])}
        
    for ith_name in names_dictionary:
        damlev = damerau_levenshtein_distance(name, ith_name)
        jaro = jaro_similarity(name, ith_name)
        jaro_wink = jaro_winkler_similarity(name, ith_name)
        
        if best_match_l["score"] > damlev:
            best_match_l["score"] = damlev
            best_match_l["name"] = ith_name
        
        if best_match_j["score"] < jaro:
            best_match_j["score"] = jaro
            best_match_j["name"] = ith_name
            
        if best_match_jw["score"] < jaro_wink:
            best_match_jw["score"] = jaro_wink
            best_match_jw["name"] = ith_name
             
    # print(f"Name to match: {name}\n")    
    # print(f"Best match using damerau_levenshtein_distance: {best_match_l}")
    # print(f"Best match using jaro_similarity: {best_match_j}")
    # print(f"Best match using jaro_winkler_similarity: {best_match_jw}")
    
    return_stats = {"name": name, "best_damlev": best_match_l["name"], "best_damlev_score": best_match_l["score"],
                    "best_jaro": best_match_j["name"], "best_jaro_score": best_match_j["score"],
                    "best_jaro_wink": best_match_jw["name"], "best_jaro_wink_score": best_match_jw["score"]}
    
    return return_stats


def match_two_namelists(nameslist_one, namelist_two, threshold=0.75):
    names_matches = []
    
    for name in tqdm(nameslist_one, desc="Matched names"):
        match = name_match_stats(name, namelist_two)
        
        if match["best_jaro_score"] > threshold and match["best_jaro_wink_score"] > threshold:
            names_matches.append(match)
    
    return names_matches


def save_dic_as_csv(dict, filename):
    df = pd.DataFrame(dict)
    df.to_csv(filename + ".csv")
    

def save_all_matches_csv():
    names_foodcentral = list(read_json('data/unique_names_foodcentral.json'))
    names_recipes = list(read_json('data/unique_names_recipes.json'))
    
    names_matches = match_two_namelists(names_recipes, names_foodcentral, threshold=0.84)
    save_dic_as_csv(names_matches, "data/names_matches2")
    
    units_foodcentral = list(read_json('data/unique_units_foodcentral.json'))
    units_recipes = list(read_json('data/unique_units_recipes.json'))
    
    unit_matches = match_two_namelists(units_recipes, units_foodcentral, threshold=0.84)
    save_dic_as_csv(unit_matches, "data/units_matches2")


def name_clean(name):
    cleaned_name = []
    
    for word in word_tokenize(name):
        if word.casefold() not in stop_words:
            word_temp = word.casefold()
            syns = wordnet.synsets(word_temp, pos = wordnet.NOUN)

            for syn in syns:
                if 'food' in syn.lexname():
                    cleaned_name.append(word)
                    break

    cleaned_name = " ".join(cleaned_name)
    
    return cleaned_name


def name_clean_quantity(name):
    cleaned_name = []
    
    name_no_symbols = name.lower().replace(r"(", "").replace(r")", "")
    name_no_numbers = re.sub(r'\d+', '', name_no_symbols)
    
    for word in word_tokenize(name_no_numbers):
        cleaned_name.append(word)

    cleaned_name = " ".join(cleaned_name)
    cleaned_name = cleaned_name.split(",")[0]
    
    return cleaned_name


def clean_foodcentral_for_matching():
    try:
        os.remove("data/foodcentral_clean.json")
    except OSError:
        pass

    foodcentral = read_json("data/foodcentral.json")
    
    data = {}
    
    for ingridient in tqdm(foodcentral["SurveyFoods"], desc="Cleaning foodcentral data"):
        portions = []
        
        for portion in ingridient["foodPortions"]:
            if portion["portionDescription"] != "" and portion["portionDescription"] != "Quantity not specified":
                portion_data = {}
                portion_data["gram_weight"] = portion["gramWeight"]
                portion_data["description"] = name_clean_quantity(portion["portionDescription"])
                portions.append(portion_data)
    
        if portions:
            description = name_clean(ingridient["description"].lower().replace(r",", "").replace(r"(", "").replace(r")", ""))
            
            if description not in data.keys():
                data[description] = portions
            elif len(portions) > len(data[description]):
                data[description] = portions
                    
    save_json("data/foodcentral_clean.json", data)


def name_match(name, names_dictionary, threshold=0.75):
    name = name_clean(name)
    
    best_match = jaro_winkler_similarity(name, names_dictionary[0])
    if jaro_winkler_similarity(name, names_dictionary[0]) > threshold:
        best_name = names_dictionary[0]
    else:
        best_name = ""
    
    for ith_name in names_dictionary:
        if best_match < jaro_winkler_similarity(name, ith_name) and jaro_winkler_similarity(name, ith_name) > threshold:
            best_match = jaro_winkler_similarity(name, ith_name)
            best_name = ith_name
    
    return best_name


def ingridient_match():
    foodcentral = read_json("data/foodcentral_clean.json")
    recipes = read_json("data/new_recipes.json")
    
    names_to_match = list(foodcentral.keys())
    
    updated_data = {}
    
    for recipe in tqdm(recipes, desc="Matching names"):
        for ingridient in recipe["ingridients"]:
            # print(f"{ingridient['name']} matched: {name_match(ingridient['name'], names_to_match)}")
            updated_data[ingridient['name']] = name_match(ingridient['name'], names_to_match)
        # print("\n")
    
    save_json("data/matched_names.json", updated_data)


def compute_mass(threshold=0.70):
    matched_names = read_json("data/matched_names.json")
    foodcentral = read_json("data/foodcentral_clean.json")
    recipes = read_json("data/new_recipes.json")

    for recipe in tqdm(recipes, desc="Computing ingridients weights"):
        for ingridient in recipe["ingridients"]:
            possible_units = foodcentral[matched_names[ingridient['name']]]
            
            best_unit_score = jaro_winkler_similarity(ingridient["unit"], possible_units[0]["description"])
            
            if jaro_winkler_similarity(ingridient["unit"], possible_units[0]["description"]) > threshold:
                best_unit_mass = possible_units[0]["gram_weight"] 
            else:
                best_unit_mass = 0
            
            for unit in possible_units:
                if best_unit_score < jaro_winkler_similarity(ingridient["unit"], unit["description"]) and jaro_winkler_similarity(ingridient["unit"], unit["description"]) > threshold:
                    best_unit_score = jaro_winkler_similarity(ingridient["unit"], unit["description"])
                    best_unit_mass = unit["gram_weight"]
                
            ingridient["grams"] = ingridient["quantity"] * best_unit_mass
        
    save_json("data/recipes_with_mass.json", recipes)
    

if __name__ == "__main__":
    clean_foodcentral_for_matching()
    ingridient_match()
    compute_mass()
    
    # feel the speed
    print(f"\nTime elapsed:  {time.perf_counter() - start_time}s")
