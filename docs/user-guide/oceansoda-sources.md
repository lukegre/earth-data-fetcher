# Example Data Sources

These are data sources that I use for the OceanSODA-ETHZv2 product

```yaml

chl_cci:
    metadata:
        title: 'ESA Ocean Colour Climate Change Initiative (OC-CCI): Level 4 Analysis
            product, version 6.0'
        version: v6.0
    storage_options:
        cache_storage: ../data/chl_esa_cci/chl/v6.0/{t:%Y}/ESACCI-OC-L3S-CHLOR_A-MERGED-8D_DAILY_4km_GEO_PML_OCx-{t:%Y%m%d}-fv6.0.nc
    url: https://rsg.pml.ac.uk/thredds/dodsC/CCI_ALL-v6.0-8DAY
    variables:
        chlor_a: chl_cci
        chlor_a_log10_bias: chl_cci_log10_bias
        chlor_a_log10_rmsd: chl_cci_log10_rmsd

soda:
    metadata:
        info: https://soda.umd.edu/
        spatial_resolution: 0.5 degrees
        temporal_resolution: 5 days
        title: Simple Ocean Data Assimilation (SODA) v3.15.2
        version: v3.15.2
    storage_options:
        cache_storage: ../data/soda/v3.15.2/{t:%Y}/
        same_names: true
    time:
        end: 2020-12-31
        freq: 5D
        start: 1980-01-03
        start_doy: none
    url: filecache::http://dsrs.atmos.umd.edu/DATA/soda3.15.2/REGRIDED/ocean/soda3.15.2_5dy_ocean_reg_{t:%Y_%m_%d}.nc

ssh_duacs_cmems:
    metadata:
        doi: https://doi.org/10.25423/CMEMS-SEALEVEL-GLO-001
        spatial_resolution: 0.125 degrees
        temporal_resolution: 1 day
        title: CMEMS Sea Level Anomaly (SLA) product
        version: 2020
    storage_options:
        cache_storage: ../data/ssh_duacs/{t:%Y}/cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.125deg_P1D_{t:%Y%m%d}.nc
        same_names: true
    time:
        end: 2024-06-30
        freq: 1D
        start: 1993-01-01
    url: cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.125deg_P1D
    variables:
        adt: ssh_adt
        sla: ssh_sla

sst_cci_cdr:
    metadata:
        doi: https://dx.doi.org/10.5285/4a9654136a7148e39b7feb56f8bb02d2
        processing_level: 4
        spatial_resolution: 0.05 degrees
        temporal_resolution: 1 day
        title: 'ESA Sea Surface Temperature Climate Change Initiative (SST_cci): Level
            4 Analysis product, version 3.0'
        version: v3.0.1
    storage_options:
        cache_storage: ../data/sst_esa_cci/v3.0.1/{t:%Y}/
        same_names: true
    time:
        end: 2024-06-30
        freq: 1D
        start: 1982-01-01
    url: filecache::https://dap.ceda.ac.uk/neodc/eocis/data/global_and_regional/sea_surface_temperature/CDR_v3/Analysis/L4/v3.0.1/{t:%Y}/{t:%m}/{t:%d}/*L4_GHRSST-SSTdepth-OSTIA*.nc
    variables:
        analysed_sst: sst_cci
        analysed_sst_uncertainty: sst_cci_uncertainty
        sea_ice_fraction: ice_cci

sst_oisst:
    metadata:
        citation: null
        doi: https://doi.org/10.25921/RE9P-PT57
        spatial_resolution: 0.25 degrees
        temporal_resolution: 1 day
        title: NOAA Optimum Interpolation Sea Surface Temperature (OISST) v2.1
        version: v2.1
    storage_options:
        cache_storage: ../data/sst_noaa_oisst/v2.1/{t:%Y}/
        same_names: true
    time:
        end: 2024-12-31
        freq: 1D
        start: 2024-07-01
    url: filecache::https://www.ncei.noaa.gov/data/sea-surface-temperature-optimum-interpolation/v2.1/access/avhrr/{t:%Y%m}/oisst-avhrr-v02r01.{t:%Y%m%d}.nc


sss_cci:
    url: filecache::https://dap.ceda.ac.uk/neodc/esacci/sea_surface_salinity/data/v04.41/GLOBALv4.41/7days/{t:%Y}/ESACCI-SEASURFACESALINITY-L4-SSS-GLOBAL-MERGED_OI_7DAY_RUNNINGMEAN_DAILY_0.25deg-{t:%Y%m%d}-fv4.41.nc
    storage_options:
        cache_storage: ../data/sss_esacci_smos/v04.41/{t:%Y}/
        same_names: true
    metadata: 
        citation_info: https://catalogue.ceda.ac.uk/uuid/0d0f4a942a144d9cab9263de3949a5d6/
        spatial_resolution: 0.25 degrees
        temporal_resolution: daily as 7 day rolling mean
        title: "ESA Sea Surface Salinity Climate Change Initiative (Sea_Surface_Salinity_cci): Weekly sea surface salinity product on a global grid, v04.41, for 2010 to 2022"
        version: v4.41
    time: 
        start: 2010-01-01
        end: 2022-10-30
        freq: 1D


chl_globcolour:
    url: filecache::https://s3.waw3-1.cloudferro.com/mdl-native-16/native/OCEANCOLOUR_GLO_BGC_L4_MY_009_104/cmems_obs-oc_glo_bgc-plankton_my_l4-gapfree-multi-4km_P1D_202311/{t:%Y}/{t:%m}/{t:%Y%m%d}_cmems_obs-oc_glo_bgc-plankton_my_l4-gapfree-multi-4km_P1D.nc
    storage_options:
        cache_storage: ../data/chl_cmems_globcolour/cmems_obs-oc_glo_bgc-plankton_my_l4-gapfree-multi-4km_P1D/{t:%Y}/
        same_names: true
    metadata:
        doi: https://doi.org/10.48670/moi-00281
        spatial_resolution: 4 km
        temporal_resolution: 1 day
        title: Global Ocean Colour (Copernicus-GlobColour), Bio-Geo-Chemical, L4 (monthly and interpolated) from Satellite Observations
    time:  # 1 Sep 1997 to 14 Jan 2025
        start: 1997-09-01
        end: 2025-01-01
        freq: 1D
    variables:
        CHL: chl_globcolour
        CHL_uncertainty: chl_globcolour_uncert
        flags: chl_globcolour_flags
```