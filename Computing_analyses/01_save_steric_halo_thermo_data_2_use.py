import os,sys
import numpy as np
import xarray as xr
import zarr

# took 2h49 min to execute
dir_sc = "/work/scratch-pw3/stajouri"
dir_work = "/gws/nopw/j04/isotipic/stajouri/PhD/Jean_Zay_DIRWORK/uor98hu"

# chunk_size = {"x":133,"y":320}

# ---------------------------------- weight for the GMSL calculation -----------------------------------------------
diri = "/gws/nopw/j04/isotipic/stajouri/PhD/Jean_Zay_DIRWORK/uor98hu/"
mesh_hgr = xr.open_dataset(diri+'eORCA025.L75_domain_cfg_closed_seas_greenland.nc').squeeze()
tmask = mesh_hgr.top_level
e1t = mesh_hgr.e1t.fillna(0)
e2t = mesh_hgr.e2t.fillna(0)

# constructing the weight
bt = e1t * e2t # area of each cell
# getting the weights to be applied to every grid cell
# masking the land cells
oceanArea = bt * tmask  #tmask : 1 on ocean, 0 on land
totalOceanArea = oceanArea.sum()
Weight = oceanArea / totalOceanArea
# Persist weight once to avoid recomputation in loops
Weight = Weight.persist()


for nexp in ["EAI", "EGAI"]:
    print(nexp)
    # load sea ice mask to apply
    SIMSK_E = xr.open_zarr(dir_work+"/ETUDE3/ENS_VAR_BUDGET/raw_data/raw_data/"+nexp+"/"+nexp+"_SIMASK15_E1980_2018.zarr").SIMASK15_E #  Sea ice mask
    sum_simsk = SIMSK_E.sum(('ens','time_counter'))
    # si_mask = (sum_simsk.where(sum_simsk==390,0)/390)
    si_mask = xr.where(sum_simsk == 390, 1, 0).persist()


    for COMP in ['STERIC','THERMO', 'HALO']:
        print(COMP)

        for dep in ["50m", "100m", "300m", "700m", "2000m", "bottom"]: 
            print(dep)
            dir_data = dir_sc + "/raw_STERIC_THERMO_HALO/"+nexp+"/"+COMP+"/"+dep+"/"

            sosteric = xr.open_zarr(dir_data+nexp+"1y_steric_0_"+dep+"_1980_2018.zarr").sosteric * si_mask
            print("step GMSL")

            # calculating the GMSL
            mean_E_GMSL = (sosteric * Weight).sum(('x','y'))
            STERIC_E_corr = sosteric  - mean_E_GMSL
            
            # retrieving the ensemble mean time mean at each point
            print("step tmean")

            tmean_E = STERIC_E_corr.mean('year').mean('ens')
            
            STERIC_E_corr_shifted = STERIC_E_corr - tmean_E 
    
            # save in scratch
            print("step saving")

            diro = dir_sc + "/STERIC_THERMO_HALO_2use/"+nexp+"/"+COMP+"/"
            STERIC_E_corr_shifted.to_dataset(name=COMP+"_E").to_zarr(diro+COMP+"_0_"+dep+"_2use_1980_2018.zarr", mode='w', zarr_version=2)
