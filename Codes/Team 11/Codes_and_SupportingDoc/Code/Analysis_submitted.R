library(csv)
#c_T2 <- read.csv("C:/Users/599542/Downloads/labeled_trajectory/T2.csv")
#View(c_T2)

#reading the files (CHANGE names and # of files)
#Orange=366
#Green=751
#red=636

i=1
filenames = paste("T",i,sep="")
links = paste("C:/Users/599542/Downloads/labeled_trajectory/red_poly/",filenames,".csv",sep="")
c_temp=read.csv(links[i]) 
c_temp1 = cbind(i,c_temp)
c_t = c_temp1

for (i in 2:636) {
  filenames[i] = paste("T",i,sep="")
  links[i] = paste("C:/Users/599542/Downloads/labeled_trajectory/red_poly/",filenames[i],".csv",sep="")

  c_temp=read.csv(links[i]) 
  c_temp1 = cbind(i,c_temp)
  
  c_t = rbind(c_t,c_temp1)
  }

#removing missing values
c_t_spare=c_t

c_t = c_t[complete.cases(c_t), ]


#Split by lanes (CHANGE names)
unique(c_t$lane)

c_S=split(c_t, c_t$lane)

rc_L1 = subset(c_S$`1`)
rc_L2 = subset(c_S$`2`)
rc_L3 = subset(c_S$`3`)
rc_L2 = subset(c_S$`4`)
rc_L3 = subset(c_S$`5`)

remove(c_S)

#Plot trajoctries (CHANGE names)
library(ggplot2)

ggplot(rc_L3, aes(time, distance,colour=i)) + 
  geom_line(aes(group = i)) +
  ggtitle("Red polygon, L3")

ggsave("RedL3_updated.png")


#After pre-processign
#Create a matrix for the vehicles whose speed <= 4.5 Km/hr (CHANGE names)

x=rc_L1


s_temp=which(x$speed<=4.5)
y=cbind(x$i[s_temp],x$time[s_temp],x$lat[s_temp],x$lon[s_temp],x$distance[s_temp])

plot(y[,2],y[,5])
#finding max Q length for each lane and spillback
#Q[max length,Lane,timestamp,lat start, long start, lat end, long end]
#Q = matrix(nrow = 10, ncol = 7) ## pre-allocate storage
#rows - 1:Green Lane 1, 5: Green Lane 5, 6: Orange Lane 1, 8: Red Lane 1, 10: Red Lane 3
lane=6

b=which(y[,5] > 0)
p=which(y[,5]==min(y[,5][b]))
t_temp=which(y[,1]==y[p[1]])
Qperiodstart=min(y[,2][t_temp])
Qperiodend=max(y[,2][t_temp])
p_temp=which(y[,2] >= Qperiodstart & y[,2] <= Qperiodend)


Qrow=c(max(x$distance) - min(y[,5]),
      lane,
      y[,2][p[1]],
      y[,3][y[,5]==max(y[,5][p_temp])][1],
      y[,4][y[,5]==max(y[,5][p_temp])][1],
      y[,3][p[1]],
      y[,4][p[1]])
Qrow

Q[lane,]=Qrow
Q

#finding Spilback for each Q in each lane 
#Logic: if there is at least a car stopped behind the last car in the queue and
#the queue is at least 15m away upstream the polygon (length of heavy vehicle)
#Spill[Lane,timestamp]

#Change
c=0
Spillr = matrix(nrow = 1000, ncol = 2) ## pre-allocate storage

#Change
x=rc_L3


s_temp=which(x$speed<=4.5)
y=cbind(x$i[s_temp],x$time[s_temp],x$lat[s_temp],x$lon[s_temp],x$distance[s_temp])

plot(y[,2],y[,5])


#CHANGE
lane=3

Sp=which(y[,5] <= 15 & y[,5] > 0)
St_temp=unique(y[,1][Sp])
Spp=which(y[,5] < 0)

ID_PH=0
for (e in 1:length(St_temp)) {
  time_range=range(y[,2][y[,1]==St_temp[e]])
  tt_temp=which(y[,2][Spp] >= time_range[1] & y[,2][Spp] <= time_range[2])
  ID_temp=unique(y[,1][tt_temp])
  if (any(ID_temp %in% ID_PH)){
    }else{
      c=c+1
    Spillr[c,] = c(lane,time_range[2])
  }
  ID_PH=ID_temp
}
  
  
Spillr






#The end


#------------------------------------------------------------
