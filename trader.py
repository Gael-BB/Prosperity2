from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import numpy as np
from math import erf
import jsonpickle

# back tester command: & 'c:\Users\Gael Work\AppData\Roaming\Python\Python312\Scripts\prosperity2bt.exe' trader.py 1
class Trader:
    # GENERAL FUNCTIONS
    def calculate_weighted_mid_price(self, order_depth):
        if len(order_depth.sell_orders) == 0 or len(order_depth.buy_orders) == 0:
            return None
        
        total_price = 0
        total_volume = 0
        for ask_price, ask_volume in list(order_depth.sell_orders.items()):
            total_price -= ask_price * ask_volume
            total_volume -= ask_volume
        
        for bid_price, bid_volume in list(order_depth.buy_orders.items()):
            total_price += bid_price * bid_volume
            total_volume += bid_volume
        
        return total_price / total_volume
    
    def calculate_exponential_ma(self, data, order_depth):
        mid_price = self.calculate_weighted_mid_price(order_depth)
        
        if data['ema'] == -1:
            data['ema'] = mid_price
            print("Initialized starfruit exponential moving average.")
            return data, False
        
        data['ema'] = data['smoothing_factor'] * mid_price + (1 - data['smoothing_factor']) * data['ema']
        return data, True
    
    def calculate_regression(self, prices, coef, intercept):
        predicted = round(prices[-1] * (1 + np.dot(np.array(prices), np.array(coef)) + intercept))
        print(f"Current price: {prices[-1]}. Predicted price: {predicted}")
        return predicted
    # END OF GENERAL FUNCTIONS

    # START OF GIFTS BASKET FUNCTIONS
    def gift_basket_calculate_target_position(self, traderData):
        premium_prices = np.array(traderData['INGREDIENTS']['last_basket_prices']) - np.array(traderData['INGREDIENTS']['last_ingredients_prices'])
        premium_mean = np.mean(premium_prices)
        premium_std = np.std(premium_prices - premium_mean)
        print(f"Mean: {premium_mean}. Std: {premium_std}.")
        if premium_std == 0:
            return 0
        # IDK if this should be multiplied by -1 or not
        return -erf((premium_prices[-1] - premium_mean) / premium_std) * traderData['GIFT_BASKET']['max_position']
    
    # END OF GIFTS BASKET FUNCTIONS

    def run(self, state: TradingState):
        result = {}
        conversions = 0
        if state.timestamp == 0:
            # ALL VARIABLES THAT NEED STORAGE GO HERE
            traderData = {}

            # Amethysts Data
            amethysts_data = {'max_position': 20}
            traderData['AMETHYSTS'] = amethysts_data

            # Starfuit Data
            starfruit_data = {'max_position': 20, 'ema': -1}
            ema_period = 4
            starfruit_data['smoothing_factor'] = 1 / (ema_period + 1)
            traderData['STARFRUIT'] = starfruit_data

            # Orchids Data
            orchids_data = {'max_position': 100}
            traderData['ORCHIDS'] = orchids_data

            # Chocolate Data
            chocolate_data = {'max_position': 250}
            traderData['CHOCOLATE'] = chocolate_data

            # Strawberries Data
            strawberries_data = {'max_position': 350}
            traderData['STRAWBERRIES'] = strawberries_data

            # Roses Data
            roses_data = {'max_position': 60}
            traderData['ROSES'] = roses_data

            # Gift Basket Data
            gift_basket_data = {'max_position': 60}
            traderData['GIFT_BASKET'] = gift_basket_data

            # Ingredients Data
            ingredients_data = {'last_basket_prices': [], 'last_ingredients_prices': [0]}
            traderData['INGREDIENTS'] = ingredients_data
        else:
            traderData = jsonpickle.decode(state.traderData)

        products = ['AMETHYSTS', 'STARFRUIT', 'ORCHIDS', 'CHOCOLATE', 'STRAWBERRIES', 'ROSES', 'GIFT_BASKET']
        for product in products: #['CHOCOLATE', 'STRAWBERRIES', 'ROSES', 'GIFT_BASKET']:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            data = traderData[product]
            position = state.position.get(product, 0)
            max_position = data['max_position']
            
            match(product):
                case "AMETHYSTS":
                    acceptable_price = 10000
                    orders.append(Order(product, acceptable_price-2, max_position - position))
                    orders.append(Order(product, acceptable_price+2, -max_position - position))
                
                case "STARFRUIT":
                    data, tradable = self.calculate_exponential_ma(data, order_depth)
                    if tradable:
                        acceptable_price = round(data['ema'])
                        orders.append(Order(product, acceptable_price-2, max_position - position))
                        orders.append(Order(product, acceptable_price+2, -max_position - position))

                case "ORCHIDS":
                    conversions = -position
                    observations = state.observations.conversionObservations['ORCHIDS']
                    international_ask = observations.askPrice + observations.transportFees + observations.importTariff
                    best_bid = list(order_depth.buy_orders.keys())[0]
                    orders.append(Order(product, int(max(np.ceil(international_ask), best_bid + 2)), -max_position - position))
                
                case "CHOCOLATE" | "STRAWBERRIES" | "ROSES":
                    product_multiplier = {'CHOCOLATE': 4, 'STRAWBERRIES': 6, 'ROSES': 1}
                    traderData['INGREDIENTS']['last_ingredients_prices'][-1] += self.calculate_weighted_mid_price(order_depth) * product_multiplier[product]
                    #TODO: Find a way to make money off these products
                
                case "GIFT_BASKET":
                    traderData['INGREDIENTS']['last_basket_prices'].append(self.calculate_weighted_mid_price(order_depth))
                    
                    target_position = int(round(self.gift_basket_calculate_target_position(traderData)))
                    best_bid, best_ask = list(order_depth.buy_orders.keys())[0], list(order_depth.sell_orders.keys())[0]
                    
                    # Experiment with multiplier at the end of order_price
                    order_price = (best_ask + best_bid) / 2  +  (position - target_position) / data['max_position'] * (best_ask - best_bid) * 2

                    # NOT ENOUGH TRADES BEING EXECUTED
                    if target_position > 0:
                        orders.append(Order(product, round(order_price), target_position - position))
                    else:
                        orders.append(Order(product, round(order_price), -target_position - position))

                    print(f"Target position: {target_position}. Current position: {position}.")
                    
                    # Needed to provide entry for next iteration
                    traderData['INGREDIENTS']['last_ingredients_prices'].append(0)
                           
            # Don't modify anything below this comment
            traderData[product] = data
            result[product] = orders
        # Notice the indentation    
        traderData = jsonpickle.encode(traderData)
        return result, conversions, traderData