install.packages('ROCR')
library(ROCR)
setwd('/Users/Thoughtworker/Programming/Kaggle/avsc/data')
predictions <- read.csv('predictions.csv', header=F)
labels <- read.csv('labels.csv', header=F)
pred <- prediction(predictions$V2, labels$V2)
perf <- performance(pred, measure = "tpr", x.measure = "fpr") 
plot(perf, col=rainbow(10))
abline(0,1)
performance(pred, measure = "auc") 