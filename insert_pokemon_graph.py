from neo4j import GraphDatabase
import json

# Conexão com o Neo4j
uri = ""
username = "neo4j"
password = ""

driver = GraphDatabase.driver(uri, auth=(username, password))
session = driver.session()

# Função para criar os nós de Pokémon
def create_pokemon_nodes(pokemon_data):
    for pokemon in pokemon_data:
        pokemon_name = pokemon['pokemon_name']
        pokemon_id = pokemon['pokemon_id']  # Agora já é um inteiro
        weight = float(pokemon['weight']) if pokemon.get('weight') else None
        height = float(pokemon['height']) if pokemon.get('height') else None
        types = pokemon['types']
        weaknesses = pokemon['weaknesses']
        evolutions = pokemon.get('evolutions', [])

        # Criar nó Pokémon
        session.run("""
            MERGE (p:Pokemon {id: $id, name: $name})
            SET p.weight = $weight, p.height = $height
            """, id=pokemon_id, name=pokemon_name, weight=weight, height=height)

# Função para criar nós de tipo
def create_type_nodes():
    types = ["Normal", "Water", "Fire", "Grass", "Electric", "Ice", "Fighting", "Poison", "Ground", 
             "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"]
    
    for pokemon_type in types:
        session.run("""
            MERGE (t:Type {name: $type})
            """, type=pokemon_type)

# Função para criar relacionamentos de tipo
def create_type_relationships(pokemon_data):
    for pokemon in pokemon_data:
        pokemon_id = pokemon['pokemon_id']
        types = pokemon['types']
        
        for pokemon_type in types:
            session.run("""
                MATCH (p:Pokemon {id: $id})
                MATCH (t:Type {name: $type})
                MERGE (p)-[:HAS_TYPE]->(t)
                """, id=pokemon_id, type=pokemon_type)

# Função para criar relacionamentos de fraqueza
def create_weakness_relationships(pokemon_data):
    for pokemon in pokemon_data:
        pokemon_id = pokemon['pokemon_id']
        weaknesses = pokemon['weaknesses']
        
        for weakness in weaknesses:
            session.run("""
                MATCH (p:Pokemon {id: $id})
                MATCH (w:Type {name: $weakness})
                MERGE (p)-[:WEAK_TO]->(w)
                """, id=pokemon_id, weakness=weakness)

# Função para criar relacionamentos de evolução
def create_evolution_relationships(pokemon_data):
    for pokemon in pokemon_data:
        pokemon_name = pokemon['pokemon_name']
        evolutions = pokemon.get('evolutions', [])
        
        if evolutions:
            for i in range(len(evolutions) - 1):
                current_pokemon = evolutions[i]
                next_pokemon = evolutions[i + 1]
                session.run("""
                    MERGE (p1:Pokemon {name: $current_name})
                    MERGE (p2:Pokemon {name: $next_name})
                    MERGE (p1)-[:EVOLVES_TO]->(p2)
                    """, current_name=current_pokemon, next_name=next_pokemon)

# Carregar dados JSON
with open('pokemons_sorted.json', 'r') as f:
    pokemon_data = json.load(f)

# Executar a função para criar nós de Pokémon
create_pokemon_nodes(pokemon_data)
print("Nós de pokémons criados com sucesso.")

# Criar os nós de tipo
create_type_nodes()
print("Nós de tipos criados com sucesso.")

# Criar os relacionamentos de tipo
create_type_relationships(pokemon_data)
print("Relacionamentos de tipo criados com sucesso.")

# Criar os relacionamentos de fraqueza
create_weakness_relationships(pokemon_data)
print("Relacionamentos de fraqueza criados com sucesso.")

# Criar os relacionamentos de evolução
create_evolution_relationships(pokemon_data)
print("Relacionamentos de evolução criados com sucesso.")

# Fechar sessão
session.close()
driver.close()
