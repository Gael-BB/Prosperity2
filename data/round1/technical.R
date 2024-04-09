data = read.csv("prices_round_1_day_0.csv", header = TRUE, sep = ";")
starfruit = data[data$product == 'STARFRUIT',]

starfruit$spread_1 <- starfruit$ask_price_1 - starfruit$bid_price_1
starfruit$volume_imbalance_1 <- starfruit$bid_volume_1 - starfruit$ask_volume_1
starfruit$wap_bid <- (starfruit$bid_price_1 * starfruit$bid_volume_1 + 
                        starfruit$bid_price_2 * starfruit$bid_volume_2 + 
                        starfruit$bid_price_3 * starfruit$bid_volume_3) / 
  (starfruit$bid_volume_1 + starfruit$bid_volume_2 + starfruit$bid_volume_3)
starfruit$wap_ask <- (starfruit$ask_price_1 * starfruit$ask_volume_1 + 
                        starfruit$ask_price_2 * starfruit$ask_volume_2 + 
                        starfruit$ask_price_3 * starfruit$ask_volume_3) / 
  (starfruit$ask_volume_1 + starfruit$ask_volume_2 + starfruit$ask_volume_3)

library(ggplot2)

# Assuming the dataframe has a time or sequence column called 'time_seq'
# If not, you might use row numbers or another appropriate index

ggplot(data = starfruit, aes(x = timestamp)) + 
  geom_line(aes(y = mid_price, color = "Mid Price")) +
  geom_line(aes(y = spread_1 * 100, color = "Spread x100")) + # Multiplying by 10 for visualization purposes
  geom_line(aes(y = volume_imbalance_1 * 100, color = "Volume Imbalance x100")) + # Dividing by 100 for visualization purposes
  scale_color_manual("", 
                     breaks = c("Mid Price", "Spread x100", "Volume Imbalance x100"),
                     values = c("Mid Price" = "blue", "Spread x100" = "red", "Volume Imbalance x100" = "green")) +
  theme_minimal() +
  labs(title = "Market Indicators over Time",
       y = "Mid Price",
       x = "Time") +
  scale_y_continuous(sec.axis = sec_axis(~., name = "Scaled Indicators")) +
  theme(legend.position = "bottom")

# Note: Adjust the scaling factors (*10, /100) according to your actual data to make the plot readable.


