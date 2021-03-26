# CWR pre-breeding characterising testing environments: calculating current water balance
# Authors: B. Mora & H. Achicanoy
# CIAT, 2018

# R options
g <- gc(reset = T); rm(list = ls()); options(warn = -1); options(scipen = 999)

# Load packages
suppressMessages(if(!require(raster)){install.packages('raster'); library(raster)} else {library(raster)})
suppressMessages(if(!require(ncdf4)){install.packages('ncdf4'); library(ncdf4)} else {library(ncdf4)})
suppressMessages(if(!require(maptools)){install.packages('maptools'); library(maptools)} else {library(maptools)})
suppressMessages(if(!require(rgdal)){install.packages('rgdal'); library(rgdal)} else {library(rgdal)})
suppressMessages(if(!require(tidyverse)){install.packages('tidyverse'); library(tidyverse)} else {library(tidyverse)})

root <- "//dapadfs.cgiarad.org/workspace_cluster_13/GATES"
base <- raster(paste0(root,"/raster/indicators/heat_stress/heat_crop_generic_1991_Africa.tif" ))
src <- "//dapadfs.cgiarad.org/Workspace_cluster_9/CWR_pre-breeding/Project_TRUST/Documents/scripts/cwr_pre_breeding"

calc_wat_bal <- function(year ,continent){
  
  source(paste0(src, "/00_calculating_risk_indices.R"))
  # Load climate data
  srad <- readRDS(paste0(root,"/rds/srad_calc/new/srad_",tolower(continent),year,".rds"))
  
  prec <- readRDS(paste0(root,"/rds/chirps/",continent,"_chirps_",year,".rds" ))
  prec <- as.data.frame(prec)
  cellID <- cellFromXY(base, prec[,1:2])
  prec <- cbind(cellID,prec)
  
  tmax <- readRDS(paste0(root,"/rds/chirts/Tmax_",continent,"_chirts_",year,".rds"))
  cellID <- cellFromXY(base, tmax[,1:2])
  tmax <- cbind(cellID, tmax)
  
  tmin <- readRDS(paste0(root,"/rds/chirts/Tmin_",continent,"_chirts_",year,".rds"))
  cellID <- cellFromXY(base, tmin[,1:2])
  tmin <- cbind(cellID, tmin)
  
  colnames(prec)  <- colnames(srad)
  colnames(tmax)  <- colnames(srad)
  colnames(tmin)  <- colnames(srad)
 
    pixelList <- Reduce(intersect, list(prec[,'cellID'], tmax[,'cellID'], tmin[,'cellID'], srad[,'cellID']))
  
  cat(">>> Loading soil capacity ...\n")
  if(!file.exists(paste0(root, "/rds/_soils/Soil_capacity/soil_capacity_", tolower(continent), ".rds"))){
    
    # Load soil data
    l <- raster::stack(list.files(path = paste0(root, "/rds/_soils/AWCh2"), pattern = "*.tif$", full.names = T))
    r <- resample(l, base, method = "ngb")
    rm(l)
    
    soil_data <- data.frame(raster::xyFromCell(object = base, cell = pixelList), raster::extract(x = r, y = raster::xyFromCell(object = base, cell = pixelList))); rm(r)
    names(soil_data)[1:2] <- c("lon", "lat")
    soil_data$root_depth <- 100
    soil_data <- soil_data %>% select(lon, lat, root_depth, AWCh2_M_sl1_10km_ll:AWCh2_M_sl6_10km_ll)
    
    depths <- c(25, 100, 225, 450, 800, 1500)
    colnames(soil_data)[4:ncol(soil_data)] <- paste0("d.", depths); rm(depths)
    
    # Calculate soil capacity
    soilcap_calc_mod <- function(x, minval, maxval) {
      if(!is.na(x[3])){
        rdepth <- max(c(x[3], minval)) #cross check
        rdepth <- min(c(rdepth, maxval)) #cross-check
        wc_df <- data.frame(depth = c(2.5, 10, 22.5, 45, 80, 150), wc = (x[4:9]) * .01)
        if(!rdepth %in% wc_df$depth) {
          wc_df1 <- wc_df[which(wc_df$depth < rdepth),]
          wc_df2 <- wc_df[which(wc_df$depth > rdepth),]
          y1 <- wc_df1$wc[nrow(wc_df1)]; y2 <- wc_df2$wc[1]
          x1 <- wc_df1$depth[nrow(wc_df1)]; x2 <- wc_df2$depth[1]
          ya <- (rdepth-x1)/(x2-x1) * (y2-y1) + y1
          wc_df <- rbind(wc_df1, data.frame(depth = rdepth, wc = ya), wc_df2)
        }
        wc_df <- wc_df[which(wc_df$depth <= rdepth),]
        wc_df$soilthick <- wc_df$depth - c(0,wc_df$depth[1:(nrow(wc_df)-1)])
        wc_df$soilcap <- wc_df$soilthick * wc_df$wc
        soilcp <- sum(wc_df$soilcap) * 10 # in mm
        return(soilcp)
      } else {
        soilcp <- NA
        return(soilcp)
      }
    }
    soil_data$soilcp <- apply(soil_data, 1, FUN = soilcap_calc_mod, minval = 45, maxval = 100)
    soil_data$cellID <- cellFromXY(object = base, xy = soil_data[, c("lon", "lat")])
    soil_data <- soil_data %>% select(cellID, lon, lat, root_depth, d.25:soilcp)
    saveRDS(object = soil_data, file = paste0(root, "/rds/_soils/Soil_capacity/soil_capacity_", tolower(continent), ".rds"))
    
  } else {
    
    if(file.exists(paste0(root, "/rds/_soils/Soil_capacity/soil_capacity_", tolower(continent), ".rds"))){
      soil_data <- readRDS(paste0(root, "/rds/_soils/Soil_capacity/soil_capacity_", tolower(continent), ".rds"))
    } else {
      cat(">>> Please check what happened ...\n")
    }
    
  }
  
  cat("Soil capacity cargado", "\n")
  # Calculate water balance per pixel
  daysList <- Reduce(intersect, list(colnames(tmax[,-c(1:3)]), colnames(tmin[,-c(1:3)]),
                                     colnames(prec[,-c(1:3)]), colnames(srad[,-c(1:3)])))
  
  library(doSNOW) ; library(foreach) ; library(parallel); library(doParallel)
  cores<- detectCores();cl<- makeCluster(cores-25);registerDoParallel(cl) 
  
    watbalList <- foreach(j=1:length(pixelList)) %dopar%{ 
    require(raster);require(ggplot2); require(lubridate);require(tidyverse);require(dplyr)
    if(!file.exists(paste0(root,"/rds/_soils/Water_balance/",continent,"/",year,"/cellID_",pixelList[j],".rds"))){
      
      out_all <- soil_data[which(soil_data$cellID == pixelList[j]), c('cellID', 'lon', 'lat')]
      out_all <- do.call("rbind", replicate(length(daysList), out_all, simplify = FALSE))
      out_all$SRAD <- as.numeric(srad[which(srad$cellID == pixelList[j]), match(daysList, colnames(srad))])
      out_all$TMIN <- as.numeric(tmin[which(tmin$cellID == pixelList[j]), match(daysList, colnames(tmin))])
      out_all$TMAX <- as.numeric(tmax[which(tmax$cellID == pixelList[j]), match(daysList, colnames(tmax))])
      out_all$RAIN <- as.numeric(prec[which(prec$cellID == pixelList[j]), match(daysList, colnames(prec))])
      rownames(out_all) <- daysList
      soilcp <- soil_data[which(soil_data$cellID == pixelList[j]), 'soilcp']
      watbal_loc <- watbal_wrapper(out_all = out_all, soilcp = soilcp)
      
      general_watbal <- tibble::tibble(cellID = pixelList[j])
      general_watbal <- cbind(general_watbal, raster::xyFromCell(object = base, cell = pixelList[j])) %>% as.tibble()
      colnames(general_watbal)[2:3] <- c("lon", "lat")
      general_watbal$watbal <- watbal_loc %>% list
      saveRDS(object = general_watbal, file = paste0(root, "/rds/_soils/Water_balance/",continent,"/",year,"/cellID_",pixelList[j],".rds"))
      } else {
      cat(paste0("Pixel: ", pixelList[j], " has been already processed.\n"))
    }
    
  }
  
  return(cat(">>> Process done\n"))
}

year <-  "1983":"2016"

lapply(1:length(year), function(i){
  cat(paste0("Procesando year::::",year[i],"\n"))
  calc_wat_bal(year= year[i], continent ="Africa")
})




