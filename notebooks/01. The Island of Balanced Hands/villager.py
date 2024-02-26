from utils import is_surplus, is_deficit, default_round

class Villager:
    def __init__(self, id, product, inventory):
        """ 
        Creates a villager based on units consumed per person per week.
        Inventory will be initialized with negative values as initially a villager will be in deficit of those values
        """
        self.id = id
        self.product = product
        self.inventory = inventory

    def __str__(self):
        return f'{str(self.id)}:{self.product}'

    def __repr__(self):
        return self.__str__()

    def add_product(self, product, units):
        """ updates villager's inventory by giving units of a product to them """
        self.inventory[product] += default_round(units)

    def remove_product(self, product, units):
        """ updates villager's inventory by taking units of a product from them """
        self.inventory[product] -= default_round(units)
        
    def set_product(self, product, units):
        """ updates villager's inventory by setting product to given units """
        self.inventory[product] = default_round(units)

    def has_product(self, product, min_units):
        """ checks if the villager has sufficient units of product """
        return self.inventory[product] >= min_units

    def can_sell(self):
        """ returns list of product surplus in inventory that villager wants to sell """
        return list(filter(lambda product: is_surplus(self.inventory[product]), self.inventory))

    def can_buy(self):
        """ returns list of product deficit in inventory that villager wants to buy """
        return list(filter(lambda product: is_deficit(self.inventory[product]), self.inventory))
    

    def has_product_to_sell(self):
        return len(self.can_sell()) > 0

    def has_product_to_buy(self):
        return len(self.can_buy()) > 0

    def get_product_to_exchange(self, units_produced_per_hour):
        """ villager decides product_to_exchange based on maximum product he can take by giving product_to_exchange """ 
        product_to_exchange = None
        hours_to_exchange = None
        for sellable_product in self.can_sell():
            if hours_to_exchange is None or hours_to_exchange < units_produced_per_hour[sellable_product] * self.inventory[sellable_product]:
                hours_to_exchange = units_produced_per_hour[sellable_product] * self.inventory[sellable_product]
                product_to_exchange = sellable_product
        return product_to_exchange