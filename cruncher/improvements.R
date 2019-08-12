raw <- read.csv("processed/Youth Clubs.csv", header=TRUE, sep = ",")
raw <- raw[order(raw$nameID, raw$eventID),]

athletes <- subset(raw, select = c("name", "event", "nameID", "eventID", "athlete_event", 
                                   "record", "tis", "datedays", "next_PR", "improvement" ))
athletes <- athletes[which(athletes$record == "PR"),]

#fix improvements
events <- unique(athletes$athlete_event)
diffs <- rep(NA, nrow(athletes))

for (event in events) {
  entries <- which(athletes$athlete_event == event)
  times <- athletes[entries,]$tis
  if(length(times) > 1) {
    diffs[entries[1:(length(times) - 1)]] <- times[1:length(times) - 1] - times[2:length(times)]
  }
}
athletes$improvement <- diffs
athletes <- allathletes

df <- athletes[athletes$event == "1600 Meters",]
bins <- data.frame(time = seq(1, max(df$tis)), improvement = rep(NA, max(df$tis)))
for(i in 1:max(df$tis)) {
  entries <- df[which(df$tis >= i & df$tis < i + 1),]$next_PR
  bins[i,]$improvement <- ifelse(length(entries) > 1, median(entries), NA)
}
plot(improvement ~ time, bins[!is.na(bins$improvement),], xaxt = "n", type = "l")





#only look at events > 800m
numbers <- as.numeric(gsub("([0-9]+).*$", "\\1", allathletes$event))
athletes <- allathletes[grepl("Mile", allathletes$event) |
                       (grepl("Meters", allathletes$event) & 
                          (!is.na(numbers) & numbers >= 800)),]

# "bin" PRs and find median time to improve by 1s
athletes <- athletes[which(!is.na(athletes$improvement)),]
bins <- data.frame(time = seq(1, max(athletes$tis)), rate = rep(NA, max(athletes$tis)))
for(i in 1:max(athletes$tis)) {
  entries <- athletes[which(athletes$tis >= i - 1 & athletes$tis < i),] # all entries in this interval
  rates <- entries$next_PR / entries$improvement
  bins[i,]$rate <- median(rates, na.rm = TRUE)
}
bins2_yc <- bins[which(!is.na(bins$rate)),]
plot(rate ~ time, bins2[bins2$time <= 1200,], xaxt = "n", type = "l")
axis(1, at = seq(1, 20) * 60, labels = seq(1, 20))

bins <- bins2[bins2$rate < 300,]

plot(rate ~ time, bins[bins$time <= 1200,], xaxt = "n", type = "l")
axis(1, at = seq(1, 20) * 60, labels = seq(1, 20))
