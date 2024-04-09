data = read.csv("prices_round_1_day_-2.csv", header = TRUE, sep = ";")
# amethysts = data[data$product == "AMETHYSTS",]
starfruit = data[data$product == "STARFRUIT",]
plot(starfruit$timestamp, starfruit$mid_price, col="blue", type ="l")
plot(starfruit$timestamp, starfruit$mid_price, col="blue", type ="l")

data = read.csv("submission1.csv", header = TRUE, sep = ";")
starfruit = data[data$product == "STARFRUIT",]
amethysts = data[data$product == "AMETHYSTS",]
plot(starfruit$timestamp, starfruit$mid_price, col="blue", type ="l")
lines(starfruit$timestamp, starfruit$profit_and_loss / 25 + 5030, col="red")

plot(amethysts$timestamp, amethysts$bid_price_1)
points(amethysts$timestamp, amethysts$bid_price_2)
points(amethysts$timestamp, amethysts$bid_price_3)





amethysts = data[data$product == "AMETHYSTS",]

range = 1:1000
height = c(5020,5080)


plot(starfruit$timestamp[range], starfruit$bid_price_1[range], col="blue", type ="l", ylim = height)
lines(starfruit$timestamp[range], starfruit$ask_price_1[range], col="red")

ema_function = function(x, n = 3) {
  sum = n*(n+1)/2
  weights = (1:n)/sum
  filter(x, filter = weights, method="convolution", sides=1)
}

ema = ema_function(starfruit$mid_price, 4)

lines(starfruit$timestamp[range], ema[range], col="green")
