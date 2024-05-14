# IMC Trading Competition Prosperity 2
This repository shows our code for the IMC Trading Competition Prosperity2. We placed top 1% out of 10,000 teams in a team of 4. The competition consisted of using algorithms to trade virtual products in a simulated market. The competition had 5 rounds. A probability and game theory brain teaser was given in each round.

In each round, a new product or mechanic was added. We were given data for 3 virtual trading days for the new products. The objective was to make a strategy from the data and submit the code before the end of the round. At the end of each round, our algorithms were evaluated and our balances were updated.

# Round 1
**Introduced products:** AMETHYSTS and STARFRUIT.

Amethyst's price was very stable, it always stayed around 10,000 units. The best results came from simply placing buy orders at 9998 and sell orders at 10002.

Starfruit's price was periodic, although it did move a bit. We used an exponential moving average to calculate a fair price. We then placed buy orders below the fair price and sell orders above the fair price.

# Round 2
**Introduced product:** ORCHIDS.

**Introduced mechanics:** Ability to buy/sell orchids with another market with import, transport, and export taxes. Ability to measure sunlight and humidity.

Sunlight and humidity were said to affect the orchid's price significantly. Through thorough analysis and regressions, we found that humidity and sunlight did not have any effect on the price. We concluded that it served as a distraction.

We found that the prices of orchids were significantly lower in the other market. There were a lot of arbitrage opportunities. Our strategy concluded in placing sell orders above the price of importing and buying orchids and importing to bring our position back from negative to neutral in the next time step.

# Round 3
**Introduced products:** CHOCOLATE, STRAWBERRIES, ROSES, GIFT_BASKET.

We were told a gift basket consisted of 6 strawberries, 4 chocolate bars, and 1 rose. By subtracting the price of the components from the price of the gift basket, we could calculate the price of the premium of the basket. We then decided to implement a pair trading algorithm, by trading when the z score of the price of the premium was above or below a certain threshold.

The mean and variance varied significantly in the past data for each trading day. We decided to not trade for the first 1% of a trading day to calculate the mean and variance of the premium price. We then calculated the premium dynamically throughout the trading day.

This strategy worked quite well for the gift baskets but wasn't consistent enough for the other products.

# Round 4
**Introduced products:** COCONUT, COCONUT_COUPON.

Coconut coupon was an option for the coconut product. By using the Black Scholes model, we were able to find the fair price of the coconut coupon. We then placed buy orders below the fair price and sell orders above the fair price.

Coconut was quite volatile, and consequently coconut coupon as well. To stay market-neutral, we used delta hedging.

# Round 5
Introduced mechanics: Ability to view past trades of simulated virtual traders.

We tried various strategies, using the positions and/or the past trades of different traders without success. We then decided to not change our strategy for this round.
