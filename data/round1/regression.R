day_n2 = read.csv("prices_round_1_day_-2.csv", header = TRUE, sep = ";")
day_n1 = read.csv("prices_round_1_day_-1.csv", header = TRUE, sep = ";")
day_0 = read.csv("prices_round_1_day_0.csv", header = TRUE, sep = ";")

df = rbind(day_n2, day_n1, day_0)
df = df[df$product == 'STARFRUIT',]

# Target
mid_price_change = df$mid_price / c(NA, head(df$mid_price, -1)) - 1

# Price based features
ask_price_change = df$ask_price_1 / c(NA, head(df$ask_price_1, -1)) - 1
bid_price_change = df$bid_price_1 / c(NA, head(df$bid_price_1, -1)) - 1
bid_ask_spread =  df$ask_price_1 - df$bid_price_1

# Volume based features
total_bid_volume = rowSums(df[,c("bid_volume_1", "bid_volume_2", "bid_volume_3")], na.rm = TRUE)
total_ask_volume = rowSums(df[,c("ask_volume_1", "ask_volume_2", "ask_volume_3")], na.rm = TRUE)
volume_imbalance = total_ask_volume - total_bid_volume

X = data.frame(ask_price_change, bid_price_change, bid_ask_spread, volume_imbalance)[-1:-2,]
Y = c(NA, head(mid_price_change, -1))[-1:-2]

model = lm(Y ~ ., data = X)
summary(model)

library(glmnet)

set.seed(123) # For reproducibility
cv.fit <- cv.glmnet(as.matrix(X), Y, alpha = 1)

# Look at the coefficients
coef(cv.fit, s = "lambda.min") # Coefficients at the lambda that gives minimum mean cross-validated error