data = read.csv("traderTemplate.csv", header = TRUE, sep=";")
amethyst = data[data$product == "AMETHYSTS",]
starfruit = data[data$product == "STARFRUIT",]

#plot(amethyst[amethyst$day == -2,]$bid_price_1)
#plot(starfruit[starfruit$day == -2,]$bid_price_1)

plot(amethyst$mid_price)
plot(starfruit$mid_price)

plot(starfruit$ask_price_1)
plot(starfruit$bid_price_1)

mean(amethyst$mid_price)
mean(starfruit$mid_price)

plot(amethyst$ask_price_1)
plot(amethyst$bid_price_1)

#plot bid and ask for starfruit on same graph
plot(starfruit$ask_price_1, type = "l", col = "red")
lines(starfruit$bid_price_1, col = "blue")

# 5 point moving average of starfruit mid price
moving_average_length = 10
moving_average = filter(starfruit$mid_price, rep(1/moving_average_length, moving_average_length))

lines(moving_average, col = "green")

