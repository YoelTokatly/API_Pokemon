import requests
import pandas as pd
import random as rd
import json
import sqlite3



class pokemon_game:

    def main(BASE_URL):
        user_answer = input(' would like to draw a Pokémon? (y/n)')
        if user_answer in 'y':
            pokemon_game.drew_a_card(BASE_URL)
        



    def drew_a_card(BASE_URL):
        ENDPOINT = "pokemon/"
        data = pokemon_game.api_get(BASE_URL,ENDPOINT)
        data= data['results']
        df_data = pd.DataFrame(data)
        rndom_pok = df_data.sample(n=1).iloc[0].to_dict() 
        # check if exist in db
        conn = sqlite3.connect('pokemon2.db')
        query_df = pd.read_sql_query("SELECT * FROM pokemons",conn )

        if rndom_pok['name'] in query_df['name']:
            print("pokemon alredy in data base")
        else:
            print("pokemon not in data base")
            pokemon_data = pokemon_game.api_get(rndom_pok['url'],"")
        
            print( '=='*30)
            print(f'id {pokemon_data['id']}')
            print(f'name: {pokemon_data['name']}')
            print(f'height: {pokemon_data['height']}')
            print(f'weight: {pokemon_data['weight']}')
            print(f'order: {pokemon_data['order']} ')
            print(f'base_experience: {pokemon_data['base_experience']}')
            print( '=='*30)
            # Save to database
            pokemon_game.save_to_database(pokemon_data)

    def save_to_database(pokemon_data):
        # Connect to database
        conn = sqlite3.connect('pokemon2.db')
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pokemons (
            id INTEGER PRIMARY KEY,
            name TEXT,
            height INTEGER,
            weight INTEGER,
            base_experience INTEGER,
            pokemon_order INTEGER
        )
        ''')
        
        # Insert data
        cursor.execute('''
        INSERT OR REPLACE INTO pokemons (id, name, height, weight, base_experience, pokemon_order)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            pokemon_data['id'],
            pokemon_data['name'],
            pokemon_data['height'],
            pokemon_data['weight'],
            pokemon_data['base_experience'],
            pokemon_data['order']
        ))
        
        # Commit and close
        conn.commit()
        conn.close()
        print("Pokemon saved to database!")


    

    
    def api_get(BASE_URL,ENDPOINT):
        response = requests.get(f'{BASE_URL}{ENDPOINT}?limit=10')
        print(response)     
        data = response.json()
        return data
        




if __name__ == "__main__":
    BASE_URL="https://pokeapi.co/api/v2/"
    # CATEGORY = "gender"
    pokemon_game.main(BASE_URL)