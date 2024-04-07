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
plot(starfruit$ask_price_1[200:350], type = "l", col = "red")
lines(starfruit$bid_price_1[200:350], col = "blue")

simple_moving_average <- function(data, window_size) {
  n <- length(data)
  # Calculate start and end indices for the loop to avoid NA values
  start_index <- ceiling(window_size / 2)
  end_index <- n - floor(window_size / 2)
  
  # Initialize the result vector
  averages <- numeric(end_index - start_index + 1)
  
  for (i in start_index:end_index) {
    averages[i - start_index + 1] <- mean(data[(i - floor(window_size / 2)):(i + floor(window_size / 2))])
  }
  
  return(averages)
}

window_size = 5  # Window size for moving average
moving_average = simple_moving_average(starfruit$mid_price, window_size)

lines(moving_average[(200-window_size):(350-window_size)], col = "green")

