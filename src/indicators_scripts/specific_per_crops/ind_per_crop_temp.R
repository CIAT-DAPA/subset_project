g=gc(); rm(list=ls())

pre_crop <- function(crop, continent, year,thr_max, thr_min,opt_max, opt_min,type){
  require(pacman)
  p_load(raster,tidyr,lubridate,tidyverse,dplyr,compiler)
  
  root <- "//dapadfs/workspace_cluster_13/GATES"
  root1 <- "//dapadfs/Workspace_cluster_2/SubsettingTool/"
  
  base <- raster(paste0(root1,"Inputs/raster_base_complete.asc")) 
  tmax <- readRDS(paste0(root,"/rds/chirts/Tmax_",continent,"_chirts_",year,".rds"))
  tmin <- readRDS(paste0(root,"/rds/chirts/Tmin_",continent,"_chirts_",year,".rds"))
  tmax$"NA" <- NULL
  tmin$"NA" <- NULL
  
  cell_tmax <- cellFromXY(base, tmax[,1:2])
  tmax<- cbind(cell_tmax, tmax)
  
  cell_tmin <- cellFromXY(base, tmin[,1:2])
  tmin<- cbind(cell_tmin, tmin)
  
  
  tmax <- dplyr::filter(tmax,cell_tmax %in% tmin$cell_tmin )
  tmin <- dplyr::filter(tmin,cell_tmin %in% tmax$cell_tmax )
  
  tmax$cell_tmax <- NULL
  tmin$cell_tmin <- NULL
  
  rm(cell_tmax,cell_tmin)
  
  if(ncol(tmax) == ncol(tmin)){
    tmean <- (tmax[,3:ncol(tmax)] + tmin[,3:ncol(tmin)]) *0.5
    tmean <- cbind(tmax[,1:2], tmean)
    cellID <- cellFromXY(base, tmean[,1:2])
    tmean <- cbind(cellID, tmean)
    rm(cellID)
  }else{
    if(ncol(tmax) > ncol(tmin)){
      tmax <- tmax[,-62]
    }else{
      tmin <- tmin[,-62] 
    }
    tmean <- (tmax[,3:ncol(tmax)] + tmin[,3:ncol(tmin)]) *0.5
    tmean <- cbind(tmax[,1:2], tmean)
    cellID <- cellFromXY(base, tmean[,1:2])
    tmean <- cbind(cellID, tmean)
    rm(cellID)
  }
  
  cellID <- tmean$cellID
  tmax <- cbind(cellID,tmax)
  tmin <- cbind(cellID,tmin)
  rm(cellID)
  
  ### Bases de datos de cultivos
  cat(paste0("cultivos Mapspam------>",crop,"\n"))
  mapspam  <- readRDS(paste0(root1,"Inputs/crop_area/",crop,"_",tolower(continent),".rds"))
  
  rm(mapspam, oce, cell)
  
  ### Filtro de base de clima con base mapspam 
  tmean_o <- dplyr::filter(tmean, cellID %in% mapspam$cellID)
  tmax_o <- dplyr::filter(tmax , cellID %in% mapspam$cellID)
  tmin_o <- dplyr::filter(tmin , cellID %in% mapspam$cellID)
  rm(tmax,tmin,tmean)
  ### Ahora si a cargar la base de calendario 
  
  library(doSNOW) ; library(foreach) ; library(parallel); library(doParallel)
  cores<- detectCores();cl<- makeCluster(5);registerDoParallel(cl) 
  
  cat("Calcular Indicadores")
  
  indexes <- foreach(i=1:nrow(tmean_o)) %dopar%{ 
    suppressMessages(library(tidyverse))
    suppressMessages(library(compiler))
    mylist <- list()
   
    # Just one pixel
    time.serie <- tmean_o[i, 1:(ncol(tmean_o)-3)]
    nms <- gsub("y_", "",colnames(time.serie[,-c(1:3)]))
    nms <- gsub('\\_', '-', nms)
    nms <- c('cellID',"x", "y", nms)
    colnames(time.serie) <- nms
    
    time.serie2 <- tmax_o[i, 1:(ncol(tmax_o)-3)]
    nms <- gsub("y_", "",colnames(time.serie2[,-c(1:3)]))
    nms <- gsub('\\_', '-', nms)
    nms <- c('cellID',"x", "y", nms)
    colnames(time.serie2) <- nms
    
    time.serie3 <- tmin_o[i, 1:(ncol(tmin_o)-3)]
    nms <- gsub("y_", "",colnames(time.serie3[,-c(1:3)]))
    nms <- gsub('\\_', '-', nms)
    nms <- c('cellID',"x", "y", nms)
    colnames(time.serie3) <- nms
    
    
      X <- time.serie  
      X <- X %>% gather(key = Date, value = Value, -(cellID:y))
      X$Year <- lubridate::year(as.Date(X$Date))
      X$Month <- lubridate::month(as.Date(X$Date))
      
      Y <- time.serie2
      Y <- Y %>% gather(key = Date, value = Value, -(cellID:y))
      Y$Year <- lubridate::year(as.Date(Y$Date))
      Y$Month<- lubridate::month(as.Date(Y$Date))
      
      Z <- time.serie3
      Z <- Z %>% gather(key = Date, value = Value, -(cellID:y))
      Z$Year <- lubridate::year(as.Date(Z$Date))
      Z$Month <- lubridate::month(as.Date(Z$Date))
      
      # X Tmean 
      #Y Tmax
      #Z  Tmin
      
      ### Heat Stress
      days_heat <- Y %>% dplyr::group_by(Month) %>% summarise(heat = sum(Value > thr_max))
      days_heat <- days_heat %>% as.data.frame
      names(days_heat)[2] <- "Value"; days_heat$Variable <- "days_heat"
      
      ##### Cold Stress
      
      days_cold <- Z %>% dplyr::group_by(Month) %>% summarise(heat = sum(Value < thr_min))
      days_cold <- days_cold %>% as.data.frame
      names(days_cold)[2] <- "Value"; days_cold$Variable <- "days_cold"
      
      #### Optimo 
      
      days_optm<- X %>% dplyr::group_by(Month) %>% summarise(heat = sum(Value > opt_min & Value < opt_max ))
      days_optm <- days_optm %>% as.data.frame
      names(days_optm)[2] <- "Value"; days_optm$Variable <- "days_optm"
      
      
      results<- data.frame(cellID= unique(X$cellID),rbind(days_heat, days_cold, days_optm))
      mylist[[i]] <- results
    }
  stopCluster(cl)
  df <- do.call(rbind, indexes)
  saveRDS(df, paste0(root1,"output/ind_per_crop/",crop,"/",type,"/ind_",type,"_",continent,"_",year,".rds"))
  }


year <- 1983:2016

lapply(1:length(year), function(i){
  cat(paste0("Procesando year : ", year[i], "\n"))
  pre_crop(crop = "yams", continent ="Oceania", year = year[i] ,thr_max=40, 
           thr_min= 20, opt_max=34 , opt_min=25 ,type= "temp")
})








