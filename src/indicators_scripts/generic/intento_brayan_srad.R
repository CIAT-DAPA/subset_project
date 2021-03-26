#Radiacion Solar 
#JR - BM -FC

g=gc();rm(list=ls())
require(lubridate); require(dplyr); require(raster); require(tidyverse)
root <- "//dapadfs.cgiarad.org/workspace_cluster_13/GATES/"
base_1 <- readRDS("//dapadfs.cgiarad.org/workspace_cluster_9/CWR_pre-breeding/Project_TRUST/Input_data/base/AgMerra_template.RDS")
base_2 <- raster(paste0(root,"raster/indicators/dryDays/monthly/dry_days_1981_1.asc"))

#Cargar datos de agmerra. 
tmax_a <- readRDS("//dapadfs.cgiarad.org/workspace_cluster_13/GATES/rds/agmerra/tmax/tmax_filtered_oceania.rds")
tmax_a$bean_coordinates <- NULL
tmax_a <- tmax_a[,-(4:733)]

tmin_a <- readRDS("//dapadfs.cgiarad.org/workspace_cluster_13/GATES/rds/agmerra/tmin/tmin_filtered_oceania.rds")
tmin_a$bean_coordinates <- NULL
tmin_a <- tmin_a[,-(4:733)]

srad_a <- readRDS("//dapadfs.cgiarad.org/workspace_cluster_13/GATES/rds/agmerra/srad/srad_filtered_oceania.rds")
srad_a$bean_coordinates <- NULL
srad_a <- srad_a[,-(4:733)]


prec_a <- readRDS("//dapadfs.cgiarad.org/workspace_cluster_13/GATES/rds/agmerra/prec/prec_Oceania.rds")
prec_a$bean_coordinates <- NULL
prec_a <- prec_a[,-(2:1097)]
xy <- as.data.frame(raster::xyFromCell(base_1, prec_a$cellID))
prec <- cbind(prec_a$cellID, xy, prec_a[,-1])
prec_a <- prec
colnames(prec_a) <- colnames(tmin_a)
rm(prec, xy); g=gc();rm(g)

prec_a <- dplyr::filter(prec_a, cellID %in% srad_a$cellID)
tmax_a <- dplyr::filter(tmax_a, cellID %in% prec_a$cellID)
tmin_a <- dplyr::filter(tmin_a, cellID %in% prec_a$cellID)
srad_a <- dplyr::filter(srad_a, cellID %in% prec_a$cellID)

#Trasformar datos al formato que necesito de AGMERRA
i=1
X <- lapply(1:nrow(prec_a), function(i){
  tmax_ag <- tmax_a[i,]
  tmax_ag <- tmax_ag %>% gather(key = Date, value = Value, -(cellID:lat))
  
  tmin_ag <- tmin_a[i,]
  tmin_ag <- tmin_ag %>% gather(key = Date, value = Value, -(cellID:lat))
  
  srad_ag <- srad_a[i,]
  srad_ag <- srad_ag %>% gather(key = Date, value = Value, -(cellID:lat))
  
  prec_ag <- prec_a[i,]
  prec_ag <- prec_ag %>% gather(key = Date, value = Value, -(cellID:lat))
  
  wth <- data.frame(DATE= tmax_ag$Date, SRAD = srad_ag$Value, TMAX= tmax_ag$Value , TMIN = tmin_ag$Value, RAIN=prec_ag$Value )
})

saveRDS(wth, "//dapadfs.cgiarad.org/workspace_cluster_13/GATES/rds/srad_calc/X.rds")


x <- wth[,c("DATE","SRAD","RAIN")]
x$month <- lubridate::month(as.Date(x$DATE)) 
x <- data.frame(date=x$DATE, prate=x$RAIN, srad=x$SRAD, x$month)
names(x) <- c("date","prate","srad","month")

############CARGAR DATOS DE CHIRTS 
cell <- cellFromXY(base_2,c(113.625, -24.122))

chirps <- readRDS("//dapadfs.cgiarad.org/workspace_cluster_13/GATES/rds/chirps/Oceania_chirps_1983.rds")
cellID <- cellFromXY(base_2 , chirps[,1:2])
chirps <- cbind(cellID, chirps)
names  <- colnames(chirps)
names  <- gsub("y_", "",names)
names    <- gsub('\\_', '-', names)
colnames(chirps) <- names
chirps <- dplyr::filter(chirps,cellID %in% cell)
chirps <- chirps %>% gather(key = Date, value = Value, -(cellID:y))
tail(chirps)
###############################################

tmax_ch <- readRDS("//dapadfs.cgiarad.org/workspace_cluster_13/GATES/rds/chirts/Tmax_Oceania_chirts_1983.rds")
cellID <- cellFromXY(base_2 , tmax_ch[,1:2])
tmax_ch <- cbind(cellID, tmax_ch)
names  <- colnames(tmax_ch)
names  <- gsub("y_", "",names)
names    <- gsub('\\_', '-', names)
colnames(tmax_ch) <- names
tmax_ch <- dplyr::filter(tmax_ch,cellID %in% cell)
tmax_ch <- tmax_ch %>% gather(key = Date, value = Value, -(cellID:y))
tail(tmax_ch)
##############################################
tmin_ch <- readRDS("//dapadfs.cgiarad.org/workspace_cluster_13/GATES/rds/chirts/Tmin_Oceania_chirts_1983.rds")
cellID <- cellFromXY(base_2 , tmin_ch[,1:2])
tmin_ch <- cbind(cellID, tmin_ch)
names  <- colnames(tmin_ch)
names  <- gsub("y_", "",names)
names    <- gsub('\\_', '-', names)
colnames(tmin_ch) <- names
tmin_ch <- dplyr::filter(tmin_ch,cellID %in% cell)

tmin_ch <- tmin_ch %>% gather(key = Date, value = Value, -(cellID:y))
tail(tmin_ch)

########
wth <- data.frame(DATE= tmin_ch$Date, RAIN=(chirps$Value)/10,TMIN = tmin_ch$Value,TMAX= tmax_ch$Value)
saveRDS(wth, "//dapadfs.cgiarad.org/workspace_cluster_13/GATES/rds/srad_calc/Y.rds")


y <- wth[,c("DATE","RAIN","TMIN","TMAX")]
y$year <- lubridate::year(as.Date(y$DATE))

y <- data.frame(date= y$DATE , prec=y$RAIN, tasmin= y$TMIN, tasmax= y$TMAX, year=y$year)
colnames(y)<- c("date","prec","tasmin","tasmax","year")
source("//dapadfs.cgiarad.org/workspace_cluster_13/GATES/codes/watbal/wgen_srad.R")

z<- x
x <- x[1:365,]
yr = 1983
y$date <- as.character(y$date)
x$date <- as.character(x$date)
yi <- y[which(y$year == yr),]
yi$year <- NULL
srad <- wgen_srad(x,yi,yr,lon=113.625,lat=-24.122)
srad_all <- rbind(srad_all, srad)

#now calculate radiation, per year
#lat=27.398; lon=-81.940
yr = 1983
srad_all <- data.frame()
for (yr in unique(y$year)) {
  #yr <- unique(y$year)[1]
  cat(yr,"\n")
  yi <- y[which(y$year == yr),]
  yi$year <- NULL
  srad <- wgen_srad(x,yi,yr,lon=113.625,lat=-24.125)
  srad_all <- rbind(srad_all, srad)
}

#now compare the estimated and the original one
par(mar=c(5,5,1,1))
plot(srad_all$srad[1:365], ty='l', ylab="Solar radiation [MJ / day]", xlab="Day of year")
lines(wth$SRAD[1:365], col='red')
legend(x=250,y=28,lty=c(1,1),cex=0.75,col=c("black","red"),legend=c("estimated","original"))

#x-y scatterplot
plot(srad_all$srad[1:365], wth$SRAD[1:365], xlab='Estimated srad [MJ/day]', ylab='Observed srad [MJ/day]')
abline(0,1)

#correlation test
cor.test(srad_all$srad[1:365], wth$SRAD[1:365])

#########################################################################################################################

#Radiacion Solar 
#JR - BM -FC

g=gc();rm(list=ls())
require(lubridate); require(dplyr); require(raster); require(tidyverse)
root <- "//dapadfs.cgiarad.org/workspace_cluster_13/GATES/"
base_1 <- readRDS("//dapadfs.cgiarad.org/workspace_cluster_9/CWR_pre-breeding/Project_TRUST/Input_data/base/AgMerra_template.RDS")
base_2 <- raster(paste0(root,"raster/indicators/dryDays/monthly/dry_days_1981_1.asc"))

#Cargar datos de agmerra. 
tmax_a <- readRDS("//dapadfs.cgiarad.org/workspace_cluster_13/GATES/rds/agmerra/tmax/tmax_filtered_oceania.rds")
tmax_a$bean_coordinates <- NULL
tmax_a <- tmax_a[,-(4:733)]

tmin_a <- readRDS("//dapadfs.cgiarad.org/workspace_cluster_13/GATES/rds/agmerra/tmin/tmin_filtered_oceania.rds")
tmin_a$bean_coordinates <- NULL
tmin_a <- tmin_a[,-(4:733)]

srad_a <- readRDS("//dapadfs.cgiarad.org/workspace_cluster_13/GATES/rds/agmerra/srad/srad_filtered_oceania.rds")
srad_a$bean_coordinates <- NULL
srad_a <- srad_a[,-(4:733)]


prec_a <- readRDS("//dapadfs.cgiarad.org/workspace_cluster_13/GATES/rds/agmerra/prec/prec_Oceania.rds")
prec_a$bean_coordinates <- NULL
prec_a <- prec_a[,-(2:1097)]
xy <- as.data.frame(raster::xyFromCell(base_1, prec_a$cellID))
prec <- cbind(prec_a$cellID, xy, prec_a[,-1])
prec_a <- prec
colnames(prec_a) <- colnames(tmin_a)
rm(prec, xy); g=gc();rm(g)

prec_a <- dplyr::filter(prec_a, cellID %in% srad_a$cellID)
tmax_a <- dplyr::filter(tmax_a, cellID %in% prec_a$cellID)
tmin_a <- dplyr::filter(tmin_a, cellID %in% prec_a$cellID)
srad_a <- dplyr::filter(srad_a, cellID %in% prec_a$cellID)

#Trasformar datos al formato que necesito de AGMERRA
i=1
X <- lapply(1:nrow(prec_a), function(i){
  tmax_ag <- tmax_a[i,]
  tmax_ag <- tmax_ag %>% gather(key = Date, value = Value, -(cellID:lat))
  
  tmin_ag <- tmin_a[i,]
  tmin_ag <- tmin_ag %>% gather(key = Date, value = Value, -(cellID:lat))
  
  srad_ag <- srad_a[i,]
  srad_ag <- srad_ag %>% gather(key = Date, value = Value, -(cellID:lat))
  
  prec_ag <- prec_a[i,]
  prec_ag <- prec_ag %>% gather(key = Date, value = Value, -(cellID:lat))
  
  wth <- data.frame(DATE= tmax_ag$Date, SRAD = srad_ag$Value, TMAX= tmax_ag$Value , TMIN = tmin_ag$Value, RAIN=prec_ag$Value )
})
x <- wth[,c("DATE","SRAD","RAIN")]
x$month <- lubridate::month(as.Date(x$DATE)) 
x <- data.frame(date=x$DATE, prate=x$RAIN, srad=x$SRAD, x$month)
names(x) <- c("date","prate","srad","month")

y <- wth[,c("DATE","RAIN","TMIN","TMAX")]
y$year <- lubridate::year(as.Date(y$DATE))

y <- data.frame(date= y$DATE , prec=y$RAIN, tasmin= y$TMIN, tasmax= y$TMAX, year=y$year)
colnames(y)<- c("date","prec","tasmin","tasmax","year")
source("//dapadfs.cgiarad.org/workspace_cluster_13/GATES/codes/watbal/wgen_srad.R")

srad_all <- data.frame()
for (yr in unique(y$year)) {
  #yr <- unique(y$year)[1]
  cat(yr,"\n")
  yi <- y[which(y$year == yr),]
  yi$year <- NULL
  srad <- wgen_srad(x,yi,yr,lon=113.625,lat=-24.125)
  srad_all <- rbind(srad_all, srad)
}

#now compare the estimated and the original one
par(mar=c(5,5,1,1))
plot(srad_all$srad[1:365], ty='l', ylab="Solar radiation [MJ / day]", xlab="Day of year")
lines(wth$SRAD[1:365], col='red')
legend(x=250,y=28,lty=c(1,1),cex=0.75,col=c("black","red"),legend=c("estimated","original"))

#x-y scatterplot
plot(srad_all$srad[1:365], wth$SRAD[1:365], xlab='Estimated srad [MJ/day]', ylab='Observed srad [MJ/day]')
abline(0,1)




















