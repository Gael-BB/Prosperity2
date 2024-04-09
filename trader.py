from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import numpy as np
import string

# back tester command: & 'c:\Users\Gael Work\AppData\Roaming\Python\Python312\Scripts\prosperity2bt.exe' trader.py 1
class Trader:
    past_starfruit_period = 4
    past_starfruit = np.array([-1] * past_starfruit_period)

    def acceptable_price_trade(self, product, order_depth, position, max_position, acceptable_price) -> List[Order]:
        if (abs(position) == max_position): print(f"WARNING: {product} is at position {position}.")
        orders = []
        virtual_position = position
        for ask, ask_amount in list(order_depth.sell_orders.items()):
            if ask < acceptable_price and position != max_position:
                amount = np.minimum(max_position - position, -ask_amount).item()
                print(f"Buying {product} at {ask} with {amount}x.")
                orders.append(Order(product, ask, amount))
                virtual_position += amount
            
        for bid, bid_amount in list(order_depth.buy_orders.items()):
            if bid > acceptable_price and position != -max_position:
                amount = np.minimum(max_position + position, bid_amount).item()
                print(f"Selling {product} at {bid} with {amount}x.")
                orders.append(Order(product, bid, -amount))
                virtual_position -= amount
        
        # Products that often reach max position.
        match(product):
            case "AMETHYSTS": #| "STARFRUIT":
                if virtual_position != 0:
                    print(f"Adjusting {product} at {acceptable_price} with {-virtual_position}x.")
                    orders.append(Order(product, int(np.round(acceptable_price)), -virtual_position))
        
        return orders

    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            try:
                position = state.position[product]
            except:
                position = 0
                print(f"Position not found for {product}. Setting to 0")

            match(product):
                case "AMETHYSTS":
                    acceptable_price = 10000
                    
                    # Trade Amethysts according to it's acceptable price, product has max position of 20
                    if abs(position) == 20:
                        print("MAX POSITION AMETHYST")
                    current_orders = self.acceptable_price_trade(product, order_depth, position, 20, acceptable_price)
                    if len(current_orders) != 0:
                        orders += current_orders
                
                case "STARFRUIT":
                    # Calculate Moving Average
                    if len(order_depth.sell_orders) != 0:
                        best_ask = list(order_depth.sell_orders.items())[0][0]
                    else:
                        best_ask = self.past_starfruit[0]
                    
                    if len(order_depth.buy_orders) != 0:
                        best_bid = list(order_depth.buy_orders.items())[0][0]
                    else:
                        best_bid = self.past_starfruit[0]

                    self.past_starfruit = np.roll(self.past_starfruit, 1)
                    self.past_starfruit[0] = np.mean([best_ask, best_bid])
                    acceptable_price = np.mean(self.past_starfruit)

                    # Check Moving Average is populated
                    if self.past_starfruit[self.past_starfruit_period-1] != -1:
                        # Trade Starfruit according to it's acceptable price, product has max position of 20
                        current_orders = self.acceptable_price_trade(product, order_depth, position, 20, acceptable_price)
                        if len(current_orders) != 0:
                            orders += current_orders

            result[product] = orders
    
    
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        conversions = 1
        return result, conversions, traderData