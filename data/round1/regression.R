day_n2 = read.csv("prices_round_1_day_-2.csv", header = TRUE, sep = ";")
day_n1 = read.csv("prices_round_1_day_-1.csv", header = TRUE, sep = ";")
day_0 = read.csv("prices_round_1_day_0.csv", header = TRUE, sep = ";")

X = rbind(day_n2[day_n2$product == "STARFRUIT",], day_n1[day_n1$product == "STARFRUIT",], day_0[day_0$product == "STARFRUIT",])
#X = day_n2[day_n2$product == "STARFRUIT",]
#columns = c("bid_price_1", "bid_price_2", "bid_price_3", "bid_volume_1", "bid_volume_2", "bid_volume_3", "ask_price_1", "ask_price_2", "ask_price_3", "ask_volume_1", "ask_volume_2", "ask_volume_3")


X$total_ask_volume = rowSums(X[, c("ask_volume_1", "ask_volume_2", "ask_volume_3")], na.rm = TRUE)
X$total_bid_volume = rowSums(X[, c("bid_volume_1", "bid_volume_2", "bid_volume_3")], na.rm = TRUE)

columns = c("bid_price_1", "bid_volume_1", "ask_price_1", "ask_volume_1", "total_ask_volume", "total_bid_volume")
Y = diff(X$mid_price)
X = X[-1,columns]

model = lm(Y ~ ., data = X)
summary(model)

