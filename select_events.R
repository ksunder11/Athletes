raw <- read.csv("outputs/Middle School.csv", header=TRUE, sep = ",")
raw <- raw[order(raw$nameID, raw$eventID),]

athletes <- subset(raw, select = c("event", "athlete_event", "record", "tis", "datedays", "next_PR"))
records <- athletes[which(athletes$record == "PR"),]
records <- records[records$event %in% c("800 Meters", "1600 Meters", "3200 Meters"),]

write.csv(records, "outputs3/College.csv")
