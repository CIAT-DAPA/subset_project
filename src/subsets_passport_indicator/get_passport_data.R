#' Get the authorization code to login to Genesys
#'

login_genesys <- function(){
  #setup production environment
  genesysr::setup_production()
  
  #login to get the authorization code
  genesysr::user_login()
}


#' Get accession passport data by crop
#' @param crop a vector of crop names
#'
#' @return dataframe

get_passport_data <- function(crop){
  
  require(dplyr)
  
  #fields to get from Genesys
  fields <- c("accessionName",
              "accessionNumber",
              "available",
              "coll.collDate",
              "countryOfOrigin.code3",
              "countryOfOrigin.name",
              "countryOfOrigin.region.name",
              "crop.name",
              "doi",
              "geo.elevation",
              "geo.latitude",
              "geo.longitude",
              "id",
              "institute.acronym",
              "institute.code",
              "institute.fullName",
              "mlsStatus",
              "sampStat",
              "taxonomy.genus",
              "taxonomy.spAuthor",
              "taxonomy.species",
              "taxonomy.subtAuthor",
              "taxonomy.subtaxa",
              "taxonomy.taxonName"
  )
  
  #standardize names
  std_names <- c("accession_name",
                 "accession_number",
                 "available",
                 "coll_date",
                 "country_of_origin_code3",
                 "country_of_origin_name",
                 "country_of_origin_region_name",
                 "crop_name",
                 "doi",
                 "elevation",
                 "latitude",
                 "longitude",
                 "id",
                 "institute_acronym",
                 "institute_code",
                 "institute_full_name",
                 "mls_status",
                 "samp_stat",
                 "taxonomy_genus",
                 "taxonomy_sp_author",
                 "taxonomy_species",
                 "taxonomy_subt_author",
                 "taxonomy_subtaxa",
                 "taxonomy_taxon_name"
  )
  
  accessions <- genesysr::get_accessions(list(crop = crop), fields = fields)
  
  #keep just columns included in fields
  accessions <- accessions %>% dplyr::select(any_of(fields))
  
  #modify accessions column names
  for (i in 1:length(fields)) { 
    colnames(accessions)[which(names(accessions) == fields[i])] <- std_names[i]
  }
  
  accessions
  
}