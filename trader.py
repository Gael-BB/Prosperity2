from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import numpy as np
import string

# back tester command: & 'c:\Users\Gael Work\AppData\Roaming\Python\Python312\Scripts\prosperity2bt.exe' trader.py 1
class Trader:
    # Starfuit exponential moving average variables
    starfruit_period = 4
    starfruit_smoothing_factor = 1/(starfruit_period+1)
    starfruit_ema = -1
    starfruit_past_best_ask = -1
    starfruit_past_best_bid = -1
    
    max_positions = {"AMETHYSTS": 20, "STARFRUIT": 20}

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
        return orders

    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            # Find position and max_position
            max_position = self.max_positions[product]
            try:
                position = state.position[product]
            except:
                position = 0
                print(f"Position not found for {product}. Setting to 0")

            match(product):
                case "AMETHYSTS":
                    acceptable_price = 10000
                    orders.append(Order(product, acceptable_price-2, max_position - position))
                    orders.append(Order(product, acceptable_price+2, -max_position - position))


                    # pricing_increment_positions = [0, 10, 17, 20]
                    
                    # if abs(position) == 20: print("WARNING: Amethyst is at max position.")
                    # for i in range(1, len(pricing_increment_positions)):
                    #     orders.append(Order(product, acceptable_price - (i+1), np.maximum(pricing_increment_positions[i-1], pricing_increment_positions[i] - position).item() - )
                    #     orders.append(Order(product, acceptable_price + (i+1), -1))
                
                case "STARFRUIT":
                    # Calculate Exponential Moving Average
                    if len(order_depth.sell_orders) != 0:
                        self.starfruit_past_best_ask = list(order_depth.sell_orders.items())[0][0]
                    if len(order_depth.buy_orders) != 0:
                        self.starfruit_past_best_bid = list(order_depth.buy_orders.items())[0][0]

                    if self.starfruit_past_best_ask == -1 or self.starfruit_past_best_bid == -1:
                        print("No best bid or ask for Starfruit")
                        break

                    mid_price = np.mean([self.starfruit_past_best_ask, self.starfruit_past_best_bid])
                    if self.starfruit_ema == -1:
                        self.starfruit_ema = mid_price
                    
                    self.starfruit_ema = self.starfruit_smoothing_factor * mid_price + (1 - self.starfruit_smoothing_factor) * self.starfruit_ema
                    acceptable_price = self.starfruit_ema


                    """ask_price, ask_volume = list(order_depth.sell_orders.items())[0]
                    bid_price, bid_volume = list(order_depth.buy_orders.items())[0]
                    acceptable_price = (-3.4868403 + 0.5 * (ask_price + bid_price)) + (0.0465762 * bid_price) + (-0.0438979 * bid_volume) + (-0.0458501 * ask_price) + (0.0471026 * ask_volume)"""

                    # Trade Starfruit according to it's acceptable price, product has max position of 20
                    current_orders = self.acceptable_price_trade(product, order_depth, position, 20, acceptable_price)
                    if len(current_orders) != 0:
                        orders += current_orders

            result[product] = orders
    
    
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        conversions = 1
        return result, conversions, traderData