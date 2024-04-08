from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import numpy as np
import string
class Trader:
    past_starfruit_length = 4 #optimal value for tutorial round (bearish market) #TODO Figure out value
    past_starfruit = np.array([-1] * past_starfruit_length)

    def buy_max_best_ask(self, product, best_ask, best_ask_amount, position, max_position) -> Order:
        amount = np.minimum(max_position - position, int(-best_ask_amount)).item() # Notice best_ask_amount is negative
        print("BUY", str(amount) + "x", best_ask)
        return Order(product, best_ask, amount)
    
    def sell_max_best_bid(self, product, best_bid, best_bid_amount, position, max_position) -> Order:
        amount = np.minimum(max_position + position, int(best_bid_amount)).item() # Notice position is negative
        print("SELL", str(amount) + "x", best_bid)
        return Order(product, best_bid, -amount)

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
            print(state.order_depths)
            print(product)

            print(order_depth)

            match(product):
                case "AMETHYSTS":
                    acceptable_price = 10000
                    print("Acceptable price : " + str(acceptable_price))
                    print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
            
                    if len(order_depth.sell_orders) != 0:
                        best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                        if int(best_ask) < acceptable_price:
                            orders.append(self.buy_max_best_ask(product, best_ask, best_ask_amount, position, 20))
            
                    if len(order_depth.buy_orders) != 0:
                        best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                        if int(best_bid) > acceptable_price:
                            orders.append(self.sell_max_best_bid(product, best_bid, best_bid_amount, position, 20))
                
                case "STARFRUIT":
                    if len(order_depth.sell_orders) != 0:
                        best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    else:
                        best_ask, best_ask_amount = self.past_starfruit[0], 0
                    
                    if len(order_depth.buy_orders) != 0:
                        best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    else:
                        best_bid, best_bid_amount = self.past_starfruit[0], 0

                    self.past_starfruit = np.roll(self.past_starfruit, 1)
                    self.past_starfruit[0] = np.mean([best_ask, best_bid])
                    acceptable_price = np.mean(self.past_starfruit)

                    if self.past_starfruit[self.past_starfruit_length-1] != -1:

                        if len(order_depth.sell_orders) != 0:
                            if int(best_ask) < acceptable_price:
                                orders.append(self.buy_max_best_ask(product, best_ask, best_ask_amount, position, 20))
            
                        if len(order_depth.buy_orders) != 0:
                            if int(best_bid) > acceptable_price:
                                orders.append(self.sell_max_best_bid(product, best_bid, best_bid_amount, position, 20))

            result[product] = orders
    
    
        traderData = "SAMPLE" # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.
        conversions = 1
        return result, conversions, traderData