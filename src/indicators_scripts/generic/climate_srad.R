
### Brayan Mora Argoti 
### Extraccion radiacion solar 
### Junio - 2 
g=gc();rm(list=ls())
srad <- function(continente,year){
  require(pacman)
  p_load(raster, rgdal, rgeos, stringr, tidyverse, lubridate,foreach, doSNOW, doParallel, GSIF)
  
  root <- "//dapadfs/Workspace_cluster_2/SubsettingTool/"
  base <- raster(paste0(root,"Inputs/raster_base_complete.asc"))  
  
  fls <- "//dapadfs/workspace_cluster_9/CWR_pre-breeding/Project_TRUST/Input_data/_current_climate/agmerra_srad/"
  fls <- list.files(path = fls, pattern = continente, full.names = T)
  
  df  <- readRDS(fls)
  nms <- as.character(seq(as.Date(paste0(year,'-01-01')),as.Date(paste0(year,'-12-31')),by = 1))
  nms1 <- c("lon","lat",nms)
  df1 <- select(df, as.character(nms1))
  cor <- df1[,1:2]
  
  cores <- detectCores()
  cl <- makeCluster(7)
  registerDoParallel(cl)
  
  climate <-  foreach(i=3:ncol(df1)) %dopar%{#
    require(pacman)
    pacman::p_load(raster, rgdal, rgeos, stringr, tidyverse, lubridate, 
                   foreach, doSNOW, doParallel, GSIF)
    mylist <- list()
    
    r <- cbind(cor, df1[, i])
    r <- rasterFromXYZ(r)
    r <- resample(r, base)
    pts <- as.data.frame(rasterToPoints(r))
    
    cellID <- cellFromXY(base, pts[,1:2])
    pts <- cbind(cellID,pts) 
    pts$x <- NULL
    pts$y <- NULL
    mylist[[i]] <- pts
  }
  stopCluster(cl)
  clima <- Reduce(function(...) merge(..., by= "cellID", all.x= T),climate )
  colnames(clima) <- c("cellID", nms)
  saveRDS(clima, paste0(root, "Inputs/srad/srad_",continente,"_",year,".rds"))
}

year <- 1983:2010
lapply(1:length(year) , function(i){
  cat(paste0("Procesing year ::: " ,year[i], "\n" ))
  srad(continente= "america",year= year[i]) 
})
