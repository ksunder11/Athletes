phrase <- c("This is testing to see if I actually have written to the new file")
write.csv(phrase, 'phrase_output.csv')

numbers <- c(84, 23, 51, 97)
names <- c("asdf", "wqer", "gsdf", "fghj")
ID <- c(1, 2, 3, 4)
df <- data.frame(ID, names, numbers)
write.csv(df, 'df_output.csv')
