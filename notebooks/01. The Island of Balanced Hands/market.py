from utils import pick_random_from
from IPython.display import clear_output
from tabulate import tabulate
import os

clear = lambda: os.system('clear')

class Market:
    def __init__(self, village, exchange_rate, units_produced_per_hour):
        """ Initializes the market by identifying villagers willing to sell or buy products """
        self.buyers = {}
        self.sellers = {}
        self.transactions = []
        self.exchange_rate = exchange_rate
        self.units_produced_per_hour = units_produced_per_hour
        
        buyer_products = set()
        seller_products = set()

        for villager in village:
            if villager.has_product_to_buy():
                for product in villager.can_buy():
                    self.add_buyer(product, villager)
                    buyer_products.add(product)
                
            if villager.has_product_to_sell():
                for product in villager.can_sell():
                    self.add_seller(product, villager)
                    seller_products.add(product)

        self.products = buyer_products.intersection(seller_products)
        self.market_is_open = len(self.products) > 0

    @staticmethod
    def add_villager(trader_dict, product, villager):
        """ Adds a villager to the product list in trader_dict, if product is not present the creates a new list """
        if product in trader_dict and villager not in trader_dict[product]:
            trader_dict[product].append(villager)
        else:
            trader_dict[product] = [villager]

    def add_buyer(self, product, villager):
        Market.add_villager(self.buyers, product, villager)

    def add_seller(self, product, villager):
        Market.add_villager(self.sellers, product, villager)

    @staticmethod
    def exchange(buyer, product, product_units, seller, product_to_exchange, product_to_exchange_units):
        """ Performs exchange of product of given units between traders """
        seller.remove_product(product, product_units)
        buyer.remove_product(product_to_exchange, product_to_exchange_units)
        seller.add_product(product_to_exchange, product_to_exchange_units)
        buyer.add_product(product, product_units)

    def trade(self, buyer, product, seller, product_to_exchange):
        """ Perform trade of product, product_to_exchange between buyer, seller based on minimum giving and taking capacity of each """
        buyer_giving_capacity = buyer.inventory[product_to_exchange] * self.exchange_rate[product_to_exchange][product]
        buyer_taking_capacity = -1 * buyer.inventory[product]
        seller_giving_capacity = seller.inventory[product]
        seller_taking_capacity = -1 * seller.inventory[product_to_exchange] * self.exchange_rate[product_to_exchange][product]
        if seller_taking_capacity > 0:
            product_units = min(buyer_giving_capacity, buyer_taking_capacity, seller_giving_capacity, seller_taking_capacity)
            trade_type = 'direct'
        else:
            product_units = min(buyer_giving_capacity, buyer_taking_capacity, seller_giving_capacity)
            trade_type = 'transitive'
        product_to_exchange_units = product_units * self.exchange_rate[product][product_to_exchange]
        # print(f'trade: bgc:{buyer_giving_capacity}, sgc:{seller_giving_capacity}, pu:{product_units}, peu: {product_to_exchange_units}')
        Market.exchange(buyer, product, product_units, seller, product_to_exchange, product_to_exchange_units)
        return {
            'buyer': buyer, 'product': product, 'product_units': product_units, 
            'seller': seller, 'product_to_exchange': product_to_exchange, 'product_to_exchange_units': product_to_exchange_units,
            'trade_type': trade_type, 'hours_exchanged': product_units / self.units_produced_per_hour[product]
            }
    
    def get_random_seller(self, product, product_to_exchange):
        """ finds a random seller who can give product and take product_to_exchange, if unavailable then just a random seller who can give product"""
        direct_sellers = set(self.sellers[product]).intersection(set(self.buyers[product_to_exchange]))
        # print(f'{product} - direct_sellers:{direct_sellers}, all_sellers:{self.sellers[product]}')
        return pick_random_from(direct_sellers) if len(direct_sellers) > 0 else pick_random_from(self.sellers[product])

    def execute(self):
        """ 
        Simulates the market by picking random product and then performs trading between random buyer and
        random seller. When a villager has no deficit or no surplus then the villager is removed from the buyers
        or sellers list for the product. When a product has no buyers or sellers, then the product is removed
        from the products list. Market remains open until products list is not empty.
        """
        while self.market_is_open:
            product = pick_random_from(self.products)
            buyer = pick_random_from(self.buyers[product])
            if buyer.has_product_to_sell():
                product_to_exchange = buyer.get_product_to_exchange(self.units_produced_per_hour)
                seller = self.get_random_seller(product, product_to_exchange)
                # print(f'buyer={buyer} product_to_exchange={product_to_exchange} buyer can sell {buyer.can_sell()}:{str(buyer.inventory[product_to_exchange])}, all sellers={self.sellers[product_to_exchange]}')
                transaction = self.trade(buyer, product, seller, product_to_exchange)
                self.transactions.append(transaction)
                if transaction['trade_type'] == 'transitive':
                    self.add_seller(product_to_exchange, seller)

                # print(f'transaction: {transaction}')
                # print(f'buyers[{product}]: ' + str(self.buyers[product]))
                # print(f'sellers[{product}]: ' + str(self.sellers[product]))
                # print(f'buyers[{product_to_exchange}]: ' + str(self.buyers[product_to_exchange]))
                # print(f'sellers[{product_to_exchange}]: ' + str(self.sellers[product_to_exchange]))
                # print('buyer: ' + str(buyer))
                # print('seller: ' + str(seller))

                if not product in buyer.can_buy():
                    self.buyers[product].remove(buyer)
                if not product_to_exchange in buyer.can_sell():
                    # print(f'buyer={buyer} product_to_exchange={product_to_exchange} buyer can sell {buyer.can_sell()}:{str(buyer.inventory[product_to_exchange])}, all sellers={self.sellers[product_to_exchange]}')
                    self.sellers[product_to_exchange].remove(buyer)
                if not product in seller.can_sell():
                    self.sellers[product].remove(seller)
                if not product_to_exchange in seller.can_buy() and transaction['trade_type'] == 'direct':
                    # print(f'seller={seller} product_to_exchange={product_to_exchange} seller can buy {seller.can_buy()}:{seller.inventory[product_to_exchange]}, all buyers={self.buyers[product_to_exchange]}')
                    self.buyers[product_to_exchange].remove(seller)

            else:
                print(f'Error: Buyer {str(buyer)} is broke')
                self.buyers[product].remove(buyer)
            
            remove_product = False
            remove_product_to_exchange = False
            
            if len(self.sellers[product]) == 0:
                self.sellers.pop(product, None)
                remove_product = True

            if len(self.buyers[product]) and product == 0:
                self.buyers.pop(product, None)
                remove_product = True

            if len(self.sellers[product_to_exchange]) == 0:
                self.sellers.pop(product_to_exchange, None)
                remove_product_to_exchange = True

            if len(self.buyers[product_to_exchange]) == 0:
                self.buyers.pop(product_to_exchange, None)
                remove_product_to_exchange = True

            if remove_product:
                self.products.remove(product)

            if remove_product_to_exchange:
                self.products.remove(product_to_exchange)

            self.market_is_open = len(self.products) > 0
            clear_output(wait=True)

    @staticmethod
    def print_transactions(transactions):
        print(f'{len(transactions)} transactions')
        print(tabulate(transactions, headers='keys', tablefmt='fancy_grid'))