from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import numpy as np
import jsonpickle

# back tester command: & 'c:\Users\Gael Work\AppData\Roaming\Python\Python312\Scripts\prosperity2bt.exe' trader.py 1
class Trader:
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


    def starfruit_calculate_exponential_ma(self, data, order_depth):
        mid_price = self.calculate_weighted_mid_price(order_depth)
        
        if mid_price == None:
            print("WARNING: No mid price available.")
            return data, False
        
        if data['ema'] == -1:
            data['ema'] = mid_price
            print("Initialized exponential moving average.")
            return data, False
        
        data['ema'] = data['smoothing_factor'] * mid_price + (1 - data['smoothing_factor']) * data['ema']
        return data, True
    
    def starfruit_calculatet_linear_regression(self, data, order_depth):
        total_ask_volume = 0
        total_bid_volume = 0

        for ask in list(order_depth.sell_orders.items()): total_ask_volume += ask[1]
        for bid in list(order_depth.buy_orders.items()): total_bid_volume += bid[1]
        
        if len(order_depth.sell_orders) != 0: best_ask = list(order_depth.sell_orders.items())[0][0]
        else: best_ask = data['past_best_ask']

        if len(order_depth.buy_orders) != 0: best_bid = list(order_depth.buy_orders.items())[0][0]
        else: best_bid = data['past_best_bid']

        pct_change = -4.700e-5 + (best_ask / data['past_best_ask'] - 1) * -1.878e-01 + total_ask_volume * 2.207e-05 + (best_bid / data['past_best_bid'] - 1) * -2.022e-01 + total_bid_volume * -2.028e-05
        data['regression'] = (1 + pct_change) * (best_ask + best_bid) / 2

        data['past_best_ask'] = best_ask
        data['past_best_bid'] = best_bid
        
        if data['past_best_ask']== -1 or data['past_best_bid'] == -1:
            print("WARNING: Missing best ask or bid values!")
            return data, False
        
        return data, True
        

    def run(self, state: TradingState):
        result = {}
        if state.timestamp == 0:
            # ALL VARIABLES THAT NEED STORAGE GO HERE
            traderData = {}

            # Amethysts Data
            amethysts_data = {'max_position': 20}
            traderData['AMETHYSTS'] = amethysts_data

            # Starfuit Data
            starfruit_data = {'max_position': 20, 'past_best_ask': -1, 'past_best_bid': -1, 'ema-period': 4, 'ema': -1, 'regression': -1}
            starfruit_data['smoothing_factor'] = 1 / (starfruit_data['ema-period'] + 1)
            traderData['STARFRUIT'] = starfruit_data
        else:
            traderData = jsonpickle.decode(state.traderData)

        for product in state.order_depths:
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
                    data, tradable = self.starfruit_calculate_exponential_ma(data, order_depth)
                    acceptable_price = data['ema']

                    # data, tradable = self.starfruit_calculatet_linear_regression(data, order_depth)
                    # acceptable_price = data['regression']

                    if tradable:
                        orders.append(Order(product, int(round(acceptable_price))-2, max_position - position))
                        orders.append(Order(product, int(round(acceptable_price))+2, -max_position - position))
            
            
            
            # Don't modify anything below this comment
            traderData[product] = data
            result[product] = orders
        # Notice the indentation    
        traderData = jsonpickle.encode(traderData)
        conversions = 1
        return result, conversions, traderData