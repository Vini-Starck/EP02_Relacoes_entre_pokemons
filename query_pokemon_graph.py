from neo4j import GraphDatabase

# Conexão com o Neo4j
uri = "neo4j+s://3a72becf.databases.neo4j.io"  # URL de conexão
username = "neo4j"  # Usuário
password = "0kA9wNfzfqxvpu22_1FtB7POUU0lLPsCasF3xmyHFjg"  # Senha

driver = GraphDatabase.driver(uri, auth=(username, password))
session = driver.session()

# Função para consulta: Pokémons que podem atacar Pikachu pela sua fraqueza e têm peso > 10kg
def query_pokemon_attack_pikachu():
    result = session.run("""
        MATCH (pikachu:Pokemon {name: 'Pikachu'})-[:WEAK_TO]->(w:Type)
        MATCH (attacker:Pokemon)-[:HAS_TYPE]->(w)
        WHERE attacker.weight > 10
        RETURN attacker.name AS pokemon_name, attacker.weight AS weight
    """)
    records = list(result)
    if records:
        for record in records:
            print(f"Pokemon: {record['pokemon_name']} (Peso: {record['weight']} kg)")
    else:
        print("Nenhum Pokémon encontrado com essas condições.")

# Função para consulta: Tipo mais comum de Pokémon que é atacado pelo tipo Gelo
def query_common_type_attacked_by_ice():
    result = session.run("""
        MATCH (p:Pokemon)-[:WEAK_TO]->(:Type {name: 'Ice'})
        MATCH (p)-[:HAS_TYPE]->(t:Type)
        RETURN t.name AS type, COUNT(p) AS count
        ORDER BY count DESC
        LIMIT 1
    """)
    records = list(result)
    if records:
        for record in records:
            print(f"Tipo mais comum atacado por Gelo: {record['type']} (Quantidade: {record['count']})")
    else:
        print("Nenhum tipo encontrado que seja frequentemente atacado por Gelo.")

# Função para consulta: Evoluções que dobram o peso de um Pokémon
def query_evolution_double_weight():
    result = session.run("""
        MATCH (p:Pokemon)-[:EVOLVES_TO]->(e:Pokemon)
        WHERE e.weight >= 2 * p.weight
        RETURN p.name AS pokemon_name, p.weight AS pokemon_weight, 
               e.name AS evolved_name, e.weight AS evolved_weight
    """)
    records = list(result)
    if records:
        for record in records:
            print(f"{record['pokemon_name']} (Peso: {record['pokemon_weight']} kg) evolui para "
                  f"{record['evolved_name']} (Peso: {record['evolved_weight']} kg)")
    else:
        print("Nenhuma evolução encontrada que dobre o peso do Pokémon.")

# Executar consultas
print("1. Pokémons que podem atacar Pikachu (peso > 10kg):")
query_pokemon_attack_pikachu()

print("\n2. Tipo mais comum atacado por Gelo:")
query_common_type_attacked_by_ice()

print("\n3. Evoluções que dobram o peso de um Pokémon:")
query_evolution_double_weight()

# Fechar a sessão
session.close()
