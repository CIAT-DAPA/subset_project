

# Load libraries ----------------------------------------------------------
require(pacman)
pacman::p_load(raster, rgdal, rgeos, stringr, terra, tidyverse, lubridate, 
               foreach, doSNOW, doParallel, GSIF)
g <- gc(reset = TRUE)
source('./watbal.r')

# Load data ---------------------------------------------------------------
vrble <- list.files('../raster/soils/africa/CRFVOL/', full.names = T, pattern = '.tif$')
vrble <- map(.x= vrble, .f = raster)

# Parallel process --------------------------------------------------------
cores <- detectCores()
cl <- makeCluster(5)
registerDoParallel(cl)
base <- raster("//dapadfs/workspace_cluster_13/GATES/raster/indicators/dryDays/monthly/dry_days_1981_1.asc")

system.time(suelo <- foreach(i = 1:length(vrble)) %dopar% {  
  require(dplyr); require(raster)
  mylist <- list()
  r <- vrble[[i]]
  r <- raster::resample(r, base, method= "ngb") 
  df <- as.data.frame(rasterToPoints(r))
  results <- df
  mylist[[i]] <- results
})

stopCluster(cl)
tabla <- do.call(cbind, suelo)
tabla$year <- NULL
tabla <- tabla[,c(1, 2, 3, 6, 9, 12, 15)]
cellID <- cellFromXY(base, tabla[,1:2])
tabla$cellID <- cellID
names(tabla) <- c('x', 'y', 'dpt_0', 'dpt_15', 'dpt_30', 'dpt_60', 'dpt_100', 'cellID')
tabla <- tabla %>% gather(depth, value, -cellID, -x, -y)
tabla$depth <- parse_number(tabla$depth)

saveRDS(tabla, file = '../rds/soils/crfvol.rds')

# Load resample data ------------------------------------------------------
fls <- list.files('../rds/soils', full.names = TRUE, pattern = '.rds')
tbl <- map(.x = fls, .f = readRDS)
tbl <- map(.x = tbl, .f = as_tibble)
nms <- basename(fls)
nms <- gsub('.rds', '', nms)
for(i in 1:length(tbl)){
  names(tbl[[i]]) <- c('lon', 'lat', 'cellID', 'depth', nms[i])
  print('Done!')
}

# Join all the tables into only one
tbl <- tbl %>% purrr::reduce(inner_join, by = c('cellID', 'lon', 'lat', 'depth'))
names(tbl) <- c('lon', 'lat', 'cellID', 'depth', 'BLD', 'CEC', 'CLYPPT', 'CRFVOL', 'ORCDRC', 'PHIHOX', 'SLTPPT', 'SNDPPT')

saveRDS(object = tbl, file = '../rds/soils/soils.rds')

tbl <- readRDS(file = '../rds/soils/soils.rds')
source('watbal.R')

# Calculating hor
BLDf <- ifelse(is.na(tbl$BLD), mean(tbl$BLD, na.rm=TRUE), tbl$BLD) 
hor <- cbind(tbl, AWCPTF(tbl$SNDPPT, tbl$SLTPPT, 
                         tbl$CLYPPT, tbl$ORCDRC, BLD=BLDf*1000, tbl$CEC, 
                         tbl$PHIHOX, h1=-10, h2=-20, h3=-33))

# Now calculate the ASW in mm for each soil horizon
hor$tetaFC <- hor$WWP + hor$AWCh3 #volumetric water content at field capacity (fraction)
hor$AWSat <- hor$tetaS - hor$tetaFC

# Soilcap for a 60cm rooting depth
# Minval and maxval are in cm, asw values per depth are in %
hor <- hor %>% rename(LHDICM = depth)
ids <- unique(hor$cellID)
n <- length(ids)

cl <- makeCluster(20)
registerDoSNOW(cl)

scp <- foreach(k = 1:n, .verbose = TRUE) %dopar% {
  
  require(pacman)
  pacman::p_load(raster, rgdal, rgeos, stringr, terra, tidyverse, lubridate, 
                 foreach, doSNOW, doParallel, GSIF)
  source('./watbal.r')
  
  sub <- hor %>% filter(cellID == ids[k])
  scp <- soilcap_calc(x=sub$AWCh3, y=sub$LHDICM, rdepth=60, minval=45, maxval=100)
  ssat <- soilcap_calc(x=sub$AWSat, y=sub$LHDICM, rdepth=60, minval=45, maxval=100)
  return(list(scp, ssat))
  
}

scp <- readRDS(file = '../rds/test_scp.rds')
ssat <- sapply(1:length(scp), function(k) scp[[k]][[2]])
scp <- sapply(1:length(scp), function(k) scp[[k]][[1]])

crd <- tbl %>% distinct(cellID, lon, lat)
scp <- cbind(crd, scp = scp, ssat = ssat) %>% as_tibble()
rm(ssat)

saveRDS(object = scp, file = '../rds/soils/scp_ssat.rds')

# Load climate ------------------------------------------------------------
list.files('//dapadfs/workspace_cluster_13/GATES/rds/chirts')


# Run water balance -------------------------------------------------------
wtbal <- watbal_wrapper(wth, scp, ssat)





