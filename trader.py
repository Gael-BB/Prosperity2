from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import numpy as np
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
    # END OF GENERAL FUNCTIONS

    # START OF STARFRUIT FUNCTIONS
    def starfruit_calculate_exponential_ma(self, data, order_depth):
        mid_price = self.calculate_weighted_mid_price(order_depth)
        
        if mid_price == None:
            print("WARNING: No mid price available.")
            return data, False
        
        if data['ema'] == -1:
            data['ema'] = mid_price
            print("Initialized starfruit exponential moving average.")
            return data, False
        
        data['ema'] = data['smoothing_factor'] * mid_price + (1 - data['smoothing_factor']) * data['ema']
        return data, True
    # END OF STARFRUIT FUNCTIONS

    # START OF GIFTS BASKET FUNCTIONS
    def gift_basket_calculate_z_score(self, traderData):
        choco, straw = traderData['CHOCOLATE']['last_prices'][-1], traderData['STRAWBERRIES']['last_prices'][-1]
        rose, basket = traderData['ROSES']['last_prices'][-1], traderData['GIFT_BASKET']['last_prices'][-1]
        
        ingredients_price = 4 * choco + 6 * straw + rose
        return (basket - ingredients_price - traderData['GIFT_BASKET']['premium']) / traderData['GIFT_BASKET']['sd']

    def gift_basket_calculate_premium_and_sd(self, traderData):
        basket = traderData['GIFT_BASKET']['last_prices']
        if len(basket) < 10:
            return traderData
        
        choco, straw, rose = traderData['CHOCOLATE']['last_prices'], traderData['STRAWBERRIES']['last_prices'], traderData['ROSES']['last_prices']
        basket, choco, straw, rose = np.array(basket), np.array(choco), np.array(straw), np.array(rose)
        ingredient_prices = 4 * choco + 6 * straw + rose
        traderData['GIFT_BASKET']['premium'] = np.mean(basket - ingredient_prices)
        traderData['GIFT_BASKET']['sd'] = np.std(basket - ingredient_prices - traderData['GIFT_BASKET']['premium'])
        return traderData

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
            chocolate_data = {'max_position': 250, 'last_prices': []}
            traderData['CHOCOLATE'] = chocolate_data

            # Strawberries Data
            strawberries_data = {'max_position': 350, 'last_prices': []}
            traderData['STRAWBERRIES'] = strawberries_data

            # Roses Data
            roses_data = {'max_position': 60, 'last_prices': []}
            traderData['ROSES'] = roses_data

            # Gift Basket Data
            gift_basket_data = {'max_position': 60, 'last_prices':[], 'premium': 379.4905, 'sd': 76.4231}
            traderData['GIFT_BASKET'] = gift_basket_data
        else:
            traderData = jsonpickle.decode(state.traderData)

        basket_item_counter = 0
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            data = traderData[product]
            position = state.position.get(product, 0)
            max_position = data['max_position']
            
            match(product):
                # case "AMETHYSTS":
                    # acceptable_price = 10000
                    # orders.append(Order(product, acceptable_price-1, max_position - position))
                    # orders.append(Order(product, acceptable_price+1, -max_position - position))
                
                # case "STARFRUIT":
                    # data, tradable = self.starfruit_calculate_exponential_ma(data, order_depth)
                    # if tradable:
                    #     acceptable_price = round(data['ema'])
                    #     orders.append(Order(product, acceptable_price-2, max_position - position))
                    #     orders.append(Order(product, acceptable_price+2, -max_position - position))

                # case "ORCHIDS":
                    # conversions = -position
                    # observations = state.observations.conversionObservations['ORCHIDS']
                    # international_ask = observations.askPrice + observations.transportFees + observations.importTariff
                    # orders.append(Order(product, round(international_ask + 1), -max_position - position))
                
                case "CHOCOLATE" | "STRAWBERRIES" | "ROSES" | "GIFT_BASKET":
                    basket_item_counter += 1
                    data['last_prices'].append(self.calculate_weighted_mid_price(order_depth))

                    if basket_item_counter == 4:
                        traderData[product] = data
                        traderData = self.gift_basket_calculate_premium_and_sd(traderData)
                        z_score = self.gift_basket_calculate_z_score(traderData)
                        print(f"Z-Score: {z_score}")

                        ingredients = ['CHOCOLATE', 'STRAWBERRIES', 'ROSES']
                        if z_score >= 1.5:
                            result['GIFT_BASKET'] = [ Order('GIFT_BASKET', round(traderData['GIFT_BASKET']['last_prices'][-1]) + 1, traderData['GIFT_BASKET']['max_position'] - state.position.get('GIFT_BASKET', 0)) ]
                            for i in ingredients:
                               result[i] = [ Order(i, round(traderData[i]['last_prices'][-1]) - 1, -traderData[i]['max_position'] - state.position.get(i, 0)) ]

                        if z_score <= -1.5:
                            result['GIFT_BASKET'] = [ Order('GIFT_BASKET', round(traderData['GIFT_BASKET']['last_prices'][-1]) - 1, -traderData['GIFT_BASKET']['max_position'] - state.position.get('GIFT_BASKET', 0)) ]
                            for i in ingredients:
                                result[i] = [ Order(i, round(traderData[i]['last_prices'][-1]) + 1, traderData[i]['max_position'] - state.position.get(i, 0)) ]
                           
                                

            # Don't modify anything below this comment
            traderData[product] = data
            result[product] = orders
        # Notice the indentation    
        traderData = jsonpickle.encode(traderData)
        return result, conversions, traderData