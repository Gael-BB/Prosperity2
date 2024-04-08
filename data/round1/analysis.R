data = read.csv("prices_round_1_day_0.csv", header = TRUE, sep = ";")
max(data[data$product == 'AMETHYSTS',]$bid_price_1)
min(data[data$product == 'AMETHYSTS',]$ask_price_1)

data2 = read.csv("submission1.csv", header = TRUE, sep = ";")
max(data2[data2$product == 'AMETHYSTS',]$bid_price_2)
min(data2[data2$product == 'AMETHYSTS',]$ask_price_2)





starfruit = data[data$product == "STARFRUIT",]
plot(starfruit$mid_price, type = "l", col="blue")

data_trades = data = read.csv("trades_round_1_day_0_nn.csv", header = TRUE, sep = ";")
