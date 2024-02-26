import copy
from utils import load_csv, default_round
from tabulate import tabulate
from random import randrange
from villager import Villager
from market import Market

class Simulator:
    def __init__(self, data, population, work_hours):
        self.data = data
        self.population = population
        self.work_hours = work_hours
        self.units_produced_per_hour = self.get_units_produced_per_hour()
        self.village = self.create_village()
        self.exchange_rate = self.get_exchange_rate()
        self.weeks = []

    def get_producer_distribution(self):
        """ defines number of producers for a product based on population and producers_percent """
        producer_distribution = {}
        for row in self.data:
            producer_distribution[row['product']] = round((self.population * float(row['producers_percent']))/100)
        return producer_distribution

    def get_units_produced_per_hour(self):
        """ returns units_produced_per_hour from data """
        units_produced_per_hour = {}
        for row in self.data:
            units_produced_per_hour[row['product']] = float(row['units_produced_per_hour'])
        return units_produced_per_hour

    def create_village(self):
        """ 
        Creates a village by adding villagers based on producer_distribution.
        Initially each villager will get units equivalent of production_rate times work_hours of their product
        """
        producer_distribution = self.get_producer_distribution()
        village = []
        id = 0
        for product in producer_distribution:
            for producers in range(producer_distribution[product]):
                villager = Villager(id, product, self.create_inventory())
                village.append(villager)
                id += 1
        return village

    def execute_week(self):
        """ simulates a week by resetting villager's inventory adding week's produce to villagers and then executing the market """
        for villager in self.village:
            villager.inventory = self.create_inventory()
            villager.add_product(villager.product, self.units_produced_per_hour[villager.product] * self.work_hours)
        market = Market(self.village, self.exchange_rate, self.units_produced_per_hour)
        market.execute()
        self.weeks.append({'village': copy.deepcopy(self.village), 'transactions': market.transactions})

    @staticmethod
    def print_village(village):
        """ Prints inventory of all the villagers """
        village_data = []
        for villager in village:
            formatted_villager = vars(villager) | villager.inventory
            formatted_villager.pop('inventory', None)
            village_data.append(formatted_villager)

        print(tabulate(village_data, headers='keys', tablefmt='fancy_grid'))

    def get_exchange_rate(self):
        """ creates two dimensional table of exchange rates between the produces """
        exchange_rate = {}
        for product1 in self.units_produced_per_hour:
            product1_exchange_rates = {}
            for product2 in self.units_produced_per_hour:
                product1_exchange_rates[product2] = self.units_produced_per_hour[product2]/self.units_produced_per_hour[product1]
            exchange_rate[product1] = product1_exchange_rates
        return exchange_rate

    def print_exchange_rate(self):
        """ Prints exchange rate table for 1 unit of product on y-axis get number of units of product on x-axis """
        exchange_rate_table = []
        for product in self.exchange_rate:
            exchange_rate_table.append({'↓ 1 unit \\ gets →':product} | self.exchange_rate[product])  
        print(tabulate(exchange_rate_table, headers='keys', tablefmt='fancy_grid'))

    def create_inventory(self):
        inventory = {}
        for row in self.data:
            inventory[row['product']] = -1 * default_round(float(row['units_consumed_pppw']))
        return inventory

