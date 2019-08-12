x <- "Youth Clubs.csv"
f <- paste("outputs/", x, sep = "")

raw <- read.csv(f, header=TRUE, sep = ",")
print(f)

# remove outliers, DNS, DNF, etc.
athletes <- raw[grep("\\.", as.character(raw$time)),]

# convert date into total days since 1/1/2000
year <- c(athletes$date %% (10^4))
day <- c(floor((athletes$date %% (10^6)) / 10^4))
month <- c(floor((athletes$date %% (10^8)) / 10^6))
athletes$datedays = ((year - 2000) * 365) + (30 * month) + day
print("datedays done")

#convert runtime into seconds
athletes$time <- gsub("[^0-9.:]", "", as.character(athletes$time)) # remove letters
splittimes <- sapply(athletes$time, function(x) unlist(strsplit(x, "[. :]")))
time_in_seconds <- sapply(splittimes, function(x) { # convert into seconds
  time <- as.integer(x)
  time[is.na(time)] <- 0
  time_in_seconds <- ifelse(length(time) == 3, sum(time * c(60, 1, 0.01)),  sum(time * c(1, 0.01)))
})
athletes$tis <- unlist(time_in_seconds)
print("tis done")

# create IDs for event and name
athletes$nameID <- as.numeric(as.factor(athletes$name))
athletes$eventID <- as.numeric(as.factor(athletes$event))
athletes$athlete_event <- paste(as.character(athletes$nameID), as.character(athletes$eventID), sep = "-")

# order by athlete, then event, then date and ID them for future ref
athletes <- athletes[order(athletes$athlete_event, athletes$datedays),]
athletes$ID <- seq.int(nrow(athletes))
print("IDs done")

# relabel PRs (sometimes races were entered twice, or it measures SRs instead)
for(i in unique(athletes$athlete_event)) {
  events <- athletes[athletes$athlete_event == i,]
  pr <- Inf
  rec <- sapply(events$tis, function(x) {
    if (x <= pr) {
      pr <<- x
      return("PR")
    }
    else {
      return(NA)
    }
  })
  athletes[athletes$athlete_event == i,]$record <- rec
  #print(athletes[athletes$athlete_event == i,]$record)
}
print("PRs relabeled")

# find days till next PR
PRs <- athletes[which(athletes$record == "PR"),]
events <- unique(PRs$athlete_event)

athletes$next_PR <- rep(NA, nrow(athletes))
n_PR <- rep(99999, nrow(PRs))

for (event in events) {
  entries <- which(PRs$athlete_event == event)
  races <- PRs[entries,]$datedays
  n_PR[entries[1:(length(entries) - 1)]] <- ifelse(length(races) > 1, races[2:length(races)] - races[1:(length(races) - 1)], 
                                                   99999)
}
athletes[which(athletes$record == "PR"),]$next_PR <- n_PR
print("found next PRs")

# find improvement from last PR
athletes$improvement <- rep(NA, nrow(athletes))
diffs <- rep(NA, nrow(PRs))

for (event in events) {
  entries <- which(PRs$athlete_event == event)
  times <- athletes[entries,]$tis
  diffs[entries[1:length(entries)-1]] <- ifelse(length(times) > 1, times[1:length(times) - 1] - times[2:length(times)], NA)
}
athletes[which(athletes$record == "PR"),]$improvement <- diffs
print("found improvements")

output <- paste("processed/", x, sep = "")
write.csv(athletes, output)
print("wrote out file")
