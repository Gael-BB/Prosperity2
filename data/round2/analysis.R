library(readr)
#data = read_delim("prices_round_2_day_1.csv", delim = ";", escape_double = FALSE, trim_ws = TRUE)

day_n1 = read_delim("prices_round_2_day_-1.csv", delim = ";", escape_double = FALSE, trim_ws = TRUE)
day_0 = read_delim("prices_round_2_day_0.csv", delim = ";", escape_double = FALSE, trim_ws = TRUE)
day_1 = read_delim("prices_round_2_day_1.csv", delim = ";", escape_double = FALSE, trim_ws = TRUE)
data = rbind(day_n1, day_0, day_1)

days_without_sun = c(0)
for (i in 2:nrow(data)){
  if (data[i,"SUNLIGHT"] < 2555){
    days_without_sun[i] = days_without_sun[i-1] + 1
  }
  else{
    days_without_sun[i] = 0
  }
}
data$days_without_sun = days_without_sun

humidity_range
for (i in 1:nrow(data)){
  
}



X = data[c("TRANSPORT_FEES", "EXPORT_TARIFF", "IMPORT_TARIFF", "SUNLIGHT", "HUMIDITY")]
Y = data$ORCHIDS
Y = Y - c(NA, head(Y, -1))

model = lm(Y ~ ., data = X)
summary(model)

#=====================================================
#  END OF TRAINING
#=====================================================
data = read_delim("prices_round_2_day_-1.csv", delim = ";", escape_double = FALSE, trim_ws = TRUE)

X = data[c("TRANSPORT_FEES", "EXPORT_TARIFF", "IMPORT_TARIFF", "SUNLIGHT", "HUMIDITY")]
Y = data$ORCHIDS
Y = Y - c(NA, head(Y, -1))

predicted_values = predict(model, X)

plot(Y, col="blue", type="l")
lines(predicted_values, col="red")