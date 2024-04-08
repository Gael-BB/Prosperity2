data = read.csv("prices_round_1_day_-2.csv", header = TRUE, sep = ";")
starfruit = data[data$product == "STARFRUIT",]
plot(starfruit$mid_price, type = "l", col="blue")
