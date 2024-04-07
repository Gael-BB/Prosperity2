data = read.csv("traderTemplate.csv", header = TRUE, sep=";")
amethyst = data[data$product == "AMETHYSTS",]
starfruit = data[data$product == "STARFRUIT",]

#plot(amethyst[amethyst$day == -2,]$bid_price_1)
#plot(starfruit[starfruit$day == -2,]$bid_price_1)

plot(amethyst$mid_price[100:140])
plot(starfruit$mid_price)
mean(amethyst$mid_price)
mean(starfruit$mid_price)
