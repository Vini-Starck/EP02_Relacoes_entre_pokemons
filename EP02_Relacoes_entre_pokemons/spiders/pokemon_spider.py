import scrapy
import re

class PokemonScraper(scrapy.Spider):
    name = 'pokemon'
    allowed_domains = ["pokemondb.net"]
    start_urls = ["https://pokemondb.net/pokedex/all"]

    def __init__(self, *args, **kwargs):
        super(PokemonScraper, self).__init__(*args, **kwargs)
        self.pokemon_data = []  # Lista para armazenar os dados dos Pokémons

    def parse(self, response):
        # Seleciona todos os Pokémon na tabela da página inicial
        pokemons = response.css('#pokedex > tbody > tr')
        
        for pokemon in pokemons:
            link = pokemon.css("td.cell-name > a::attr(href)").get()
            if link:
                yield response.follow(link, self.parse_pokemon)

    def parse_pokemon(self, response):
        # Extrai as informações básicas do Pokémon
        pokemon_name = response.css('#main > h1::text').get()
        pokemon_id = response.css('.vitals-table > tbody > tr:contains("National №") > td strong::text').get()
        height = response.css('.vitals-table > tbody > tr:contains("Height") > td::text').get()
        weight = response.css('.vitals-table > tbody > tr:contains("Weight") > td::text').get()
        types = response.css('.vitals-table > tbody > tr:contains("Type") > td a::text').getall()

        # Limpeza de dados de altura e peso
        height = self.clean_height(height)
        weight = self.clean_weight(weight)

        # Remove duplicatas de tipos
        types = list(set(types))

        # Extrai as fraquezas (Type Defenses)
        weaknesses = []
        defense_tables = response.css('.type-table-pokedex')
        for table in defense_tables:
            rows = table.css('tr')
            types_row = rows[0]
            effectiveness_row = rows[1]
            for i, cell in enumerate(effectiveness_row.css('td')):
                effectiveness = cell.css('::text').get()
                if effectiveness:
                    effectiveness = effectiveness.strip()
                    if effectiveness == '2' or effectiveness == '4':
                        type_name = types_row.css('th a::attr(title)')[i].get()
                        if type_name:
                            weaknesses.append(type_name)

        # Remove duplicatas de fraquezas
        weaknesses = list(set(weaknesses))

        # Captura a evolução completa (cadeia de evoluções) sem duplicatas
        evolutions = self.get_evolutions(response)

        # Converte o pokemon_id para inteiro (caso não seja None ou esteja vazio)
        if pokemon_id:
            pokemon_id = int(pokemon_id.strip())  # Converte para inteiro
        
        # Filtra para garantir que só os Pokémons da primeira geração (ID <= 151) sejam coletados
        if pokemon_id and pokemon_id <= 151:
            # Adiciona as informações do Pokémon na lista de dados
            pokemon_data = {
                'pokemon_name': pokemon_name,
                'pokemon_id': pokemon_id,  # Agora como inteiro
                'height': height,  # Agora com o valor limpo
                'weight': weight,  # Agora com o valor limpo
                'types': types,  # Tipos sem duplicatas
                'weaknesses': weaknesses,  # Fraquezas sem duplicatas
                'evolutions': evolutions,  # Cadeia completa de evoluções
            }

            self.pokemon_data.append(pokemon_data)

    def get_evolutions(self, response):
        """Obtém a cadeia de evoluções do Pokémon removendo duplicatas."""
        evolutions = []
        evolution_section = response.css('div.infocard-list-evo')
        
        if evolution_section:
            evo_cards = evolution_section.css('div.infocard')

            for evo_card in evo_cards:
                evo_name = evo_card.css('.ent-name::text').get()
                if evo_name and evo_name not in evolutions:
                    evolutions.append(evo_name)

        # Se não houver evoluções, retorna None ou uma lista vazia
        return evolutions if evolutions else None

    def close(self, reason):
        """Este método será chamado quando o spider terminar de rodar."""
        # Ordena os dados por pokemon_id antes de escrever no arquivo JSON
        self.pokemon_data.sort(key=lambda x: x['pokemon_id'])  # Ordena pela chave 'pokemon_id'

        # Grava os dados ordenados no arquivo JSON
        with open('pokemons_sorted.json', 'w') as f:
            import json
            json.dump(self.pokemon_data, f, indent=4)

    def clean_height(self, height):
        """Limpa e formata a altura para apresentar apenas o valor em metros"""
        if height:
            match = re.search(r"(\d+(\.\d+)?)\s*m", height)
            if match:
                return match.group(1)  # Retorna apenas o valor numérico da altura
        return None

    def clean_weight(self, weight):
        """Limpa e formata o peso para apresentar apenas o valor em quilos"""
        if weight:
            match = re.search(r"(\d+(\.\d+)?)\s*kg", weight)
            if match:
                return match.group(1)  # Retorna apenas o valor numérico do peso
        return None
