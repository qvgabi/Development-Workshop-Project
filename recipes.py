from bs4 import BeautifulSoup, element
import time
import json
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from multiprocessing.dummy import Pool as ThreadPool
from tqdm import tqdm

start_time = time.perf_counter()

# urls range
base_url = r"https://cosylab.iiitd.edu.in/recipedb/search_recipeInfo/"
start_id = 10000
end_id = 99989

# to prettify strings
delchars = "!@#$%^&*_+-=~`{}|[]:\"\\;'<>?/\t\r\n"


# fetching and parsing html and extracting wanted info
def fetch_and_parse(url_id):
    try:
        session = requests.Session()        
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[ 502, 503, 504 ])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        response = session.get(url=(base_url + str(url_id)), headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"On request get for {url_id}: {e}")
    else:
        soup = BeautifulSoup(response.text, 'lxml')
        recipe_title = soup.find('h3', attrs={"style": "font-family: Helvetica;"})
        recipe_ingridients_table = soup.find('table', attrs={"id": "myTable"}).find_all('tr')
        recipe_instructions = soup.find('div', attrs={"id": "steps"})

        recipe_dict = create_recipe_dict(url_id=url_id, title=recipe_title,
                                         ingridients=recipe_ingridients_table,
                                         instuctions=recipe_instructions)
        return recipe_dict


def check_if_json_exists():
    if not os.path.exists('recipes.json'):
        f = open('recipes.json', 'w')
        f.write('[]')
        f.close()
        print('Created .json file')
    else:
        print('.json file exists')
        f = open('recipes.json', 'w')
        f.write('[]')
        f.close()


def create_recipe_dict(url_id: int, title: element.Tag, ingridients: list, instuctions: element.Tag) -> dict:
    recipe = {'url_id': url_id,
              'title': title.text,
              'ingridients': [],
              'instructions': instuctions.text.translate(str.maketrans('', '', delchars)).strip()}

    for ingridient_info in ingridients[1:]:
        infos = ingridient_info.find_all('td')[0:3]
        name = infos[0].text
        quantity = infos[1].text
        unit = infos[2].text

        recipe['ingridients'].append({'name': name, 'quantity': quantity, 'unit': unit})

    return recipe


def add_recipe_to_json(recipes: list):
    with open('recipes.json', "r+") as file:
        data = json.load(file)
        for recipe in recipes:
            if recipe is not None:
                data.append(recipe)
        file.seek(0)
        json.dump(data, file, indent=4)
        file.close()
        

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))
        
        
def thredpool_runner():
    task_ids = []
    
    for url_id in range(start_id, end_id+1):
        task_ids.append(url_id)
    
    chunks_for_loop = 1000
        
    for chunck in tqdm(chunker(task_ids, chunks_for_loop), desc=f"Chunks", total=(len(task_ids)//chunks_for_loop)):
        pool = ThreadPool(100)
        results = pool.map(fetch_and_parse, chunck)
        pool.close()
        pool.join()
        
        add_recipe_to_json(results)


if __name__ == "__main__":
    # self-explanatory
    check_if_json_exists()
    
    # main runner
    thredpool_runner()

    # feel the speed
    print(f"\nTime elapsed:  {time.perf_counter() - start_time}")
