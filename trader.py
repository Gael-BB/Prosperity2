from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import numpy as np
from math import erf
import jsonpickle

# back tester command: & 'c:\Users\Gael Work\AppData\Roaming\Python\Python312\Scripts\prosperity2bt.exe' trader.py 1
class Trader:
    # GLOBAL CONSTANTS (not variables, due to AWS Lambda Bugs)
    products = ['AMETHYSTS', 'STARFRUIT', 'ORCHIDS', 'CHOCOLATE', 'STRAWBERRIES', 'ROSES', 'GIFT_BASKET', 'COCONUT_COUPON', 'COCONUT']
    max_positions = {'AMETHYSTS': 20, 'STARFRUIT': 20, 'ORCHIDS': 100, 'CHOCOLATE': 250, 'STRAWBERRIES': 350, 'ROSES': 60, 'GIFT_BASKET': 60, 'COCONUT': 300, 'COCONUT_COUPON': 600}
    coupon_historic_mean = 637.63
    coupon_scaling_factor = 16.19259

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
            return data, False
        
        data['ema'] = data['smoothing_factor'] * mid_price + (1 - data['smoothing_factor']) * data['ema']
        return data, True
    
    def calculate_regression(self, prices, coef, intercept):
        predicted = round(prices[-1] * (1 + np.dot(np.array(prices), np.array(coef)) + intercept))
        print(f"Current price: {prices[-1]}. Predicted price: {predicted}")
        return predicted
    
    def calculate_target_position(self, data, max_position):
        if data['n'] < 100:
            return 0, False
        
        mean = data['sum_x'] / data['n']
        std = np.sqrt(data['sum_x_squared'] / data['n'] - mean ** 2)
        if std == 0:
            return 0, False
        return -erf((data['x'] - mean) / std) * max_position, True
    # END OF GENERAL FUNCTIONS
    
    # START OF GIFTS BASKET AND INGREDIENTS FUNCTIONS
    def ingredients_buy(self, state, traderData, result):
        for prod in ['CHOCOLATE', 'ROSES', 'STRAWBERRIES']:
            best_ask = list(state.order_depths[prod].sell_orders.keys())[0]
            max_position = self.max_positions[prod]
            position = state.position.get(prod, 0)
            result[prod] = [Order(prod, best_ask, max_position - position)]
        return result
    
    def ingredients_sell(self, state, traderData, result):
        for prod in ['CHOCOLATE', 'ROSES', 'STRAWBERRIES']:
            best_bid = list(state.order_depths[prod].buy_orders.keys())[0]
            max_position = self.max_positions[prod]
            position = state.position.get(prod, 0)
            result[prod] = [Order(prod, best_bid, -max_position - position)]
        return result
    # END OF GIFTS BASKET FUNCTIONS

    # START OF COCONUTS FUNCTIONS
    def calculate_black_scholes(self, S, sigma = 0.05652, T = 1, r = 0, K = 10000):
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return S * erf(d1) - K * np.exp(-r * T) * erf(d2)
    # END OF COCONUTS FUNCTIONS

    def run(self, state: TradingState):
        result = {}
        conversions = 0
        if state.timestamp == 0:
            # ALL VARIABLES THAT NEED STORAGE GO HERE
            traderData = {}

            # Starfuit EMA Data
            ema_period = 4
            traderData['STARFRUIT'] = {'ema': -1, 'smoothing_factor':  1 / (ema_period + 1)}

            # Ingredients Data
            traderData['INGREDIENTS'] = {'last_basket_price': 0, 'last_ingredients_price': 0, 'n': 0, 'x': 0, 'sum_x': 0, 'sum_x_squared': 0}

            # Coconuts Data
            ema_period = 4
            traderData['COCONUT'] = {'last_product_price': 0, 'last_coupon_price': 0}

        else:
            traderData = jsonpickle.decode(state.traderData)

        for product in ['COCONUT_COUPON', 'COCONUT']:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            position = state.position.get(product, 0)
            max_position = self.max_positions[product]
            
            print(f"")
            match(product):
                case "AMETHYSTS":
                    acceptable_price = 10000
                    orders.append(Order(product, acceptable_price-2, max_position - position))
                    orders.append(Order(product, acceptable_price+2, -max_position - position))
                
                case "STARFRUIT":
                    traderData['STARFRUIT'], tradable = self.calculate_exponential_ma(traderData['STARFRUIT'], order_depth)
                    if tradable:
                        acceptable_price = round(traderData['STARFRUIT']['ema'])
                        orders.append(Order(product, acceptable_price-2, max_position - position))
                        orders.append(Order(product, acceptable_price+2, -max_position - position))

                case "ORCHIDS":
                    conversions = -position
                    observations = state.observations.conversionObservations['ORCHIDS']
                    international_ask = observations.askPrice + observations.transportFees + observations.importTariff
                    best_bid = list(order_depth.buy_orders.keys())[0]
                    orders.append(Order(product, int(max(np.ceil(international_ask), best_bid + 2)), -max_position))
                
                case "CHOCOLATE" | "STRAWBERRIES" | "ROSES":
                    product_multiplier = {'CHOCOLATE': 4, 'STRAWBERRIES': 6, 'ROSES': 1}
                    traderData['INGREDIENTS']['last_ingredients_price'] += self.calculate_weighted_mid_price(order_depth) * product_multiplier[product]
                
                case "GIFT_BASKET":
                    traderData['INGREDIENTS']['last_basket_price'] = self.calculate_weighted_mid_price(order_depth)
                    
                    traderData['INGREDIENTS']['n'] += 1
                    traderData['INGREDIENTS']['x'] = traderData['INGREDIENTS']['last_basket_price'] - traderData['INGREDIENTS']['last_ingredients_price']
                    traderData['INGREDIENTS']['sum_x'] += traderData['INGREDIENTS']['x']
                    traderData['INGREDIENTS']['sum_x_squared'] += traderData['INGREDIENTS']['x'] ** 2
 
                    target_position, tradable = self.calculate_target_position(traderData['INGREDIENTS'], self.max_positions['GIFT_BASKET'])
                    best_bid, best_ask = list(order_depth.buy_orders.keys())[0], list(order_depth.sell_orders.keys())[0]
                    
                    if tradable:
                        # JUST GIFT BASKET
                        #  (0, 179)  (2, 196)  (4, 198)  (6, 218)  (8, 223)
                        # (10, 236) (12, 234) (14, 243) (16, 249) (18, 252)
                        # (20, 248) (22, 237) (24, 235) (26, 241) (28, 251)
                        # (30, 254) (32, 253) (34, 251) (36, 246) (38, 233)
                        # (40, 248) (42, 259) (44, 279) (46, 299) (48, 292)
                        # (50, 262) (52, 225) (54, 179) (56, 167) (58, 181)
                        # BASKET WITH INGREDIENTS
                        # (40, 269) (42, 289) (44, 324) (46, 342) (48, 344)
                        # (50, 305) (52, 225) (54, 172) (56, 127) (58, 121)
                        # (45, 346) (47, 343) (49, 321)
                        # Good plateau from 45 to 49.
                        # Drop off after 49 very steep, choose 46 threshold.
                        # All ingredients make profit on average, include them.
                        threshold_target_position = 46
                        if target_position < -threshold_target_position:
                            orders.append(Order(product, best_bid, -max_position - position))
                            #result = self.ingredients_buy(state, traderData, result)
                        elif target_position > threshold_target_position:
                            orders.append(Order(product, best_ask, max_position - position))
                            #result = self.ingredients_sell(state, traderData, result)

                    # Needed to provide entry for next iteration
                    traderData['INGREDIENTS']['last_ingredients_price'] = 0

                case 'COCONUT_COUPON':
                    traderData['COCONUT']['last_coupon_price'] = self.calculate_weighted_mid_price(state.order_depths['COCONUT_COUPON'])
                    traderData['COCONUT']['last_product_price'] = self.calculate_weighted_mid_price(state.order_depths['COCONUT'])
                    if traderData['COCONUT']['last_coupon_price'] == None or traderData['COCONUT']['last_product_price'] == None:
                        break
                    black_scholes_price = (self.calculate_black_scholes(traderData['COCONUT']['last_product_price'])
                                           - self.coupon_historic_mean) * self.coupon_scaling_factor + self.coupon_historic_mean
                    print(f"COUPON PRICE: {traderData['COCONUT']['last_coupon_price']}. BLACK SCHOLES: {black_scholes_price}.")
                    if traderData['COCONUT']['last_coupon_price'] > black_scholes_price:
                        orders.append(Order(product, list(state.order_depths['COCONUT_COUPON'].buy_orders.keys())[0], -max_position - position))
                    else:
                        orders.append(Order(product, list(state.order_depths['COCONUT_COUPON'].sell_orders.keys())[0], max_position - position))

                case 'COCONUT':
                    pass
                           
            # Don't modify anything below this comment
            result[product] = orders
        # Notice the indentation    
        traderData = jsonpickle.encode(traderData)
        return result, conversions, traderData