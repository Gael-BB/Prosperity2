from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import numpy as np
from math import erf
import jsonpickle

# back tester command: & 'c:\Users\Gael Work\AppData\Roaming\Python\Python312\Scripts\prosperity2bt.exe' trader.py 1
class Trader:
    # General Constants
    products = ['AMETHYSTS', 'STARFRUIT', 'ORCHIDS', 'GIFT_BASKET', 'CHOCOLATE', 'STRAWBERRIES', 'ROSES', 'COCONUT_COUPON', 'COCONUT']
    max_positions = {'AMETHYSTS': 20, 'STARFRUIT': 20, 'ORCHIDS': 100, 'CHOCOLATE': 250, 'STRAWBERRIES': 350, 'ROSES': 60, 'GIFT_BASKET': 60, 'COCONUT': 300, 'COCONUT_COUPON': 600}

    # Amethysts Constants
    amethysts_acceptable_price = 10000

    # Starfruit Constants
    starfruit_ema_period = 4

    # Gift Basket Constants
    gift_basket_ingredients = ['CHOCOLATE', 'STRAWBERRIES', 'ROSES']
    gift_basket_ingredient_multiplier = {'CHOCOLATE': 4, 'STRAWBERRIES': 6, 'ROSES': 1}
    basket_threshold_target_position = 46

    # Coconuts Constants
    coco_coupon_bid_ask_spread_d2 = 1.2808260275342511 / 2
    coco_sigma = 0.010201268
    coco_T = 246
    coco_r = 0
    coco_K = 10000

    # General Functions
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
    
    # Starfruit Functions
    def starfruit_calculate_exponential_ma(self, data, order_depth):
        mid_price = self.calculate_weighted_mid_price(order_depth)
        
        if data['ema'] == -1:
            data['ema'] = mid_price
            return data, False
        
        data['ema'] = data['smoothing_factor'] * mid_price + (1 - data['smoothing_factor']) * data['ema']
        return data, True

    # Gift Basket Functions
    def gift_basket_calculate_target_position(self, data):
        if data['n'] < 100:
            return 0, False
        
        mean = data['sum_x'] / data['n']
        std = np.sqrt(data['sum_x_squared'] / data['n'] - mean ** 2)
        if std == 0:
            return 0, False
        return -erf((data['x'] - mean) / std) * self.max_positions['GIFT_BASKET'], True

    # Coconuts Function
    def coconuts_calculate_black_scholes(self, S):
        sigma, T, r, K = self.coco_sigma, self.coco_T, self.coco_r, self.coco_K
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return S * 0.5 * (1 + erf(d1/np.sqrt(2))) - K * np.exp(-r * T) * 0.5 * (1 + erf(d2/np.sqrt(2)))
    
    def coconuts_calculate_delta(self, S):
        sigma, T, r, K = self.coco_sigma, self.coco_T, self.coco_r, self.coco_K
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        return 0.5 * (1 + erf(d1/np.sqrt(2)))
    
    # Main Function
    def run(self, state: TradingState):
        result = {}
        conversions = 0
        if state.timestamp == 0:
            # All variables that need to be stored between iterations should be stored in traderData
            traderData = {}

            # Starfuit EMA Data
            traderData['STARFRUIT'] = {'ema': -1, 'smoothing_factor':  1 / (self.starfruit_ema_period + 1)}

            # Gift Basket Data
            traderData['GIFT_BASKET'] = {'n': 0, 'x': 0, 'sum_x': 0, 'sum_x_squared': 0}

        else:
            traderData = jsonpickle.decode(state.traderData)

        for product in self.products:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            position = state.position.get(product, 0)
            max_position = self.max_positions[product]
            
            match(product):
                case "AMETHYSTS":
                    orders.append(Order(product, self.amethysts_acceptable_price-2, max_position - position))
                    orders.append(Order(product, self.amethysts_acceptable_price+2, -max_position - position))
                
                case "STARFRUIT":
                    traderData['STARFRUIT'], tradable = self.starfruit_calculate_exponential_ma(traderData['STARFRUIT'], order_depth)
                    if tradable:
                        orders.append(Order(product, round(traderData['STARFRUIT']['ema'])-2, max_position - position))
                        orders.append(Order(product, round(traderData['STARFRUIT']['ema'])+2, -max_position - position))

                case "ORCHIDS":
                    conversions = -position
                    observations = state.observations.conversionObservations['ORCHIDS']
                    international_ask_price = observations.askPrice + observations.transportFees + observations.importTariff
                    best_bid_price = list(order_depth.buy_orders.keys())[0]
                    orders.append(Order(product, int(max(np.ceil(international_ask_price), best_bid_price + 2)), -max_position))
                
                case "GIFT_BASKET":
                    gift_basket_price = self.calculate_weighted_mid_price(order_depth)
                    ingredients_price = 0
                    for ingredient in self.gift_basket_ingredients:
                        ingredients_price += self.calculate_weighted_mid_price(state.order_depths[ingredient]) * self.gift_basket_ingredient_multiplier[ingredient]

                    traderData['GIFT_BASKET']['n'] += 1
                    traderData['GIFT_BASKET']['x'] = gift_basket_price - ingredients_price
                    traderData['GIFT_BASKET']['sum_x'] += traderData['GIFT_BASKET']['x']
                    traderData['GIFT_BASKET']['sum_x_squared'] += traderData['GIFT_BASKET']['x'] ** 2
 
                    target_position, tradable = self.gift_basket_calculate_target_position(traderData['GIFT_BASKET'])
                    best_bid_price, best_bid_volume = list(order_depth.buy_orders.items())[0]
                    best_ask_price, best_ask_volume = list(order_depth.sell_orders.items())[0]
                    
                    if tradable:
                        if target_position < -self.basket_threshold_target_position:
                            orders.append(Order(product, best_bid_price, -max_position - position))

                        elif target_position > self.basket_threshold_target_position:
                            orders.append(Order(product, best_ask_price, max_position - position))

                case 'COCONUT_COUPON':
                    self.coconut_coupon_price = self.calculate_weighted_mid_price(state.order_depths['COCONUT_COUPON'])
                    self.coconut_price = self.calculate_weighted_mid_price(state.order_depths['COCONUT'])
                    if self.coconut_coupon_price == None or self.coconut_price == None:
                        break

                    black_scholes_price = self.coconuts_calculate_black_scholes(self.coconut_price)
                    best_bid_price, best_bid_volume = list(order_depth.buy_orders.items())[0]
                    best_ask_price, best_ask_volume = list(order_depth.sell_orders.items())[0]
                    
                    self.coco_coupon_virtual_position = position
                    if self.coconut_coupon_price > black_scholes_price + self.coco_coupon_bid_ask_spread_d2:
                        self.coco_coupon_virtual_position -= best_bid_volume
                        orders.append(Order(product, best_bid_price, -max_position - position))

                    elif self.coconut_coupon_price < black_scholes_price - self.coco_coupon_bid_ask_spread_d2:
                        self.coco_coupon_virtual_position -= best_ask_volume
                        orders.append(Order(product, best_ask_price, max_position - position))

                case 'COCONUT':
                    if self.coconut_coupon_price == None or self.coconut_price == None:
                        break

                    self.coco_coupon_virtual_position = max(-600, min(600, self.coco_coupon_virtual_position))
                    delta = self.coconuts_calculate_delta(self.coconut_price)
                    target_position = -delta * self.coco_coupon_virtual_position
                    target_position = max(-300, min(300, target_position))
                    
                    best_bid_price, best_ask_price = list(order_depth.buy_orders.keys())[0], list(order_depth.sell_orders.keys())[0]
                    if target_position - position > 0:
                        orders.append(Order(product, best_ask_price, round(target_position - position)))

                    elif target_position - position < 0:
                        orders.append(Order(product, best_bid_price, round(target_position - position)))
                           
            # Don't modify anything below this comment
            result[product] = orders
        # Notice the indentation    
        traderData = jsonpickle.encode(traderData)
        return result, conversions, traderData