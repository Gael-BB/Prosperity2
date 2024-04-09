# data = read.csv("prices_round_1_day_0.csv", header = TRUE, sep = ";")
# amethysts = data[data$product == "AMETHYSTS",]
# starfruit = data[data$product == "STARFRUIT",]

data = read.csv("submission1.csv", header = TRUE, sep = ";")
starfruit = data[data$product == "STARFRUIT",]
amethysts = data[data$product == "AMETHYSTS",]

range = 100:300
height = c(5020,5050)


spo
plot(starfruit$timestamp[range], starfruit$bid_price_1[range], col="blue", type ="l", ylim = height)
lines(starfruit$timestamp[range], starfruit$ask_price_1[range], col="red")

ema_function = function(x, n = 3) {
  sum = n*(n+1)/2
  weights = (1:n)/sum
  filter(x, filter = weights, method="convolution", sides=1)
}

ema = ema_function(starfruit$mid_price, 10)

lines(starfruit$timestamp[range], ema[range], col="green")
