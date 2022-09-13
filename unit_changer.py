import time
import json
import os
from fractions import Fraction

start_time = time.perf_counter()


def read_json(name: str):
    with open(name, "r+") as file:
        data = json.load(file)
    return data


def save_json(name, data):
    if not os.path.exists(name):
        f = open(name, 'w')
        f.close()
        print('Created .json file')

    with open(name, "r+") as file:
        json.dump(data, file, indent=4)
        file.close()


def change_quantities_to_float(recipes):
    for recipe in recipes:
        for i in range(len(recipe['ingridients'])):
            recipe['ingridients'][i]['quantity'] = change_string_to_float(recipe['ingridients'][i]['quantity'])
    return recipes


def change_string_to_float(item: str):
    try:
        item = float(item)
    except ValueError:
        if has_only_numbers(item):
            item = 1.
        elif item == 'shells 1':
            item = 1.0
        elif has_to_taste(item):
            item = delete_to_taste(item)
            try:
                item = float(item)
            except ValueError:
                if has_fraction(item):
                    item = fraction_to_float(item)
                else:
                    item = .0
        elif has_dash(item):
            item = take_before_dash(item)
            if has_fraction(item):
                item = fraction_to_float(item)
            else:
                try:
                    item = float(item)
                except ValueError:
                    item = .0
        elif has_fraction(item):
            item = fraction_to_float(item)
        elif has_space(item):
            item = before_space_to_float(item)
        else:
            item = .0
    if item == 0.0:
        print('YAAAAAAAAASSSSS')
    return item


def has_only_numbers(input_string: str):
    return not any(char.isdigit() for char in input_string)


def has_dash(input_string: str):
    return '-' in input_string


def take_before_dash(input_string: str):
    return input_string.rpartition('-')[0]


def has_fraction(input_string: str):
    return '/' in input_string


def fraction_to_float(input_string: str):
    try:
        return float(sum(Fraction(s) for s in input_string.split()))
    except ValueError:
        return 'None'


def has_space(input_string: str):
    return ' ' in input_string


def before_space_to_float(input_string: str):
    try:
        return float(input_string.rpartition(' ')[0])
    except ValueError:
        return 'None'


def has_to_taste(input_string: str):
    return (' to taste' in input_string)


def delete_to_taste(input_string: str):
    return str.lower(input_string).rpartition(' to taste')[0]


if __name__ == "__main__":
    recipes = read_json('recipes_final.json')
    recipes = change_quantities_to_float(recipes)
    save_json('new_recipes.json', recipes)
    
    # feel the speed
    print(f"\ntime elapsed:  {time.perf_counter() - start_time}")
