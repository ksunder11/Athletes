raw <- read.csv("processed/College.csv", header=TRUE, sep = ",")
raw <- raw[order(raw$nameID, raw$eventID),]

athletes <- subset(raw, select = c("event", "athlete_event", 
                                   "record", "tis", "datedays", "next_PR", "improvement" ))
records <- athletes[which(athletes$record == "PR" & !is.na(athletes$improvement)),]
records <- records[records$event == "1600 Meters",]

bins <- data.frame(time = seq(1, max(records$tis)), improvement = rep(NA, max(records$tis)))
for(i in 1:max(records$tis)) {
  entries <- records[which(records$tis >= i & records$tis < i + 1),]$next_PR
  bins[i,]$improvement <- median(entries) #ifelse(length(entries) > 1, median(entries), NA)
}
plot(improvement ~ time, bins[!is.na(bins$improvement),], type = "l",
     xlab = "Race Time (s)", ylab = "Days for 1s Improvement")
