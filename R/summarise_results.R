results <- read.csv('outputs/results.csv')

mean(results$Total.money_made[startsWith(results$run_name, 'no batching')])
mean(results$Total.money_made[startsWith(results$run_name, 'batching')])
mean(results$Total.money_made[startsWith(results$run_name, 'small batching')])

mean(results$Customers.served[startsWith(results$run_name, 'no batching')])
mean(results$Customers.served[startsWith(results$run_name, 'batching')])
mean(results$Customers.served[startsWith(results$run_name, 'small batching')])

mean(results$Customers.cancelled[startsWith(results$run_name, 'no batching')])
mean(results$Customers.cancelled[startsWith(results$run_name, 'batching')])
mean(results$Customers.cancelled[startsWith(results$run_name, 'small batching')])

mean(results$Lowest.earning.taxi.per.hour[startsWith(results$run_name, 'no batching')])
mean(results$Lowest.earning.taxi.per.hour[startsWith(results$run_name, 'batching')])
mean(results$Lowest.earning.taxi.per.hour[startsWith(results$run_name, 'small batching')])

mean(results$Highest.earning.taxi.per.hour[startsWith(results$run_name, 'no batching')])
mean(results$Highest.earning.taxi.per.hour[startsWith(results$run_name, 'batching')])
mean(results$Highest.earning.taxi.per.hour[startsWith(results$run_name, 'small batching')])
