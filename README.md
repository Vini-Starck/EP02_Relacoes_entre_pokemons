Executar o scraper de pokemon (pokemon_spider.py) que armazena as informações do pokemon em pokemons.json

Após o armazenamento, é possível executar o arquivo insert_pokemon_graph.py:

O arquivo se conecta com o banco Neo4J, e insere os devidos  nós e relacionamentos no banco.

Após a inserção dos dados no banco, executamos o arquivo query_pokemon_graph.py que nos retorna as consultas feitas
