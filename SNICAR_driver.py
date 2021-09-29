
#####################################################################
################# BioSNICAR_GO DRIVER SCRIPT ########################

# This script is used to configure the 2-stream radiative transfer
# model BioSNICAR_GO. Here variable values are defined, the model called
# and the results plotted.

# NB. Setting Mie = 1, GO = 0 and algal impurities = 0 is equivalent to
# running the original SNICAR model of Flanner et al. (2007, 2009)

# NB: if using only granular layers, recommend using the faster Toon et al
# tridiagonal matix solver (by setting TOON = True), however this will not
# include any specular reflection components. If solid ice layers are
# included in the ice/snow column, the ADDING-DOUBLING solver must be used
# (i.e. ADD_DOUBLE = True).

# glacier algae MAC files are provided in units of m2/cell, which requires
# a unit conversion that is not applied to the other LAPS. The conversion
# is selectivlely applid by indexing to the last element in the LAP
# lists, meaning glacier algae must always be the final LAP, even if more
# LAPs are added in future.

# Author: Joseph Cook, June 2021

######################
######################################################################


from SNICAR_feeder import snicar_feeder
import matplotlib.pyplot as plt
import numpy as np
import collections as c

######################################
## 1) Initialize inputs of the model
######################################

inputs = c.namedtuple('inputs',['dir_base',\
    'rf_ice', 'incoming_i', 'DIRECT', 'layer_type',\
    'APRX_TYP', 'DELTA', 'solzen', 'TOON', 'ADD_DOUBLE', 'R_sfc', 'dz', 'rho_layers', 'grain_rds',\
    'side_length', 'depth', 'rwater', 'nbr_lyr', 'nbr_aer', 'grain_shp', 'shp_fctr', 'grain_ar', 'GA_units',\
    'Cfactor','mss_cnc_soot1', 'mss_cnc_soot2', 'mss_cnc_brwnC1', 'mss_cnc_brwnC2', 'mss_cnc_dust1',\
    'mss_cnc_dust2', 'mss_cnc_dust3', 'mss_cnc_dust4', 'mss_cnc_dust5', 'mss_cnc_ash1', 'mss_cnc_ash2',\
    'mss_cnc_ash3', 'mss_cnc_ash4', 'mss_cnc_ash5', 'mss_cnc_ash_st_helens', 'mss_cnc_Skiles_dust1', 'mss_cnc_Skiles_dust2',\
    'mss_cnc_Skiles_dust3', 'mss_cnc_Skiles_dust4', 'mss_cnc_Skiles_dust5', 'mss_cnc_GreenlandCentral1',\
    'mss_cnc_GreenlandCentral2', 'mss_cnc_GreenlandCentral3', 'mss_cnc_GreenlandCentral4',\
    'mss_cnc_GreenlandCentral5', 'mss_cnc_Cook_Greenland_dust_L', 'mss_cnc_Cook_Greenland_dust_C',\
    'mss_cnc_Cook_Greenland_dust_H', 'mss_cnc_snw_alg', 'mss_cnc_glacier_algae', 'FILE_soot1',\
    'FILE_soot2', 'FILE_brwnC1', 'FILE_brwnC2', 'FILE_dust1', 'FILE_dust2', 'FILE_dust3', 'FILE_dust4', 'FILE_dust5',\
    'FILE_ash1', 'FILE_ash2', 'FILE_ash3', 'FILE_ash4', 'FILE_ash5', 'FILE_ash_st_helens', 'FILE_Skiles_dust1', 'FILE_Skiles_dust2',\
    'FILE_Skiles_dust3', 'FILE_Skiles_dust4', 'FILE_Skiles_dust5', 'FILE_GreenlandCentral1',\
    'FILE_GreenlandCentral2', 'FILE_GreenlandCentral3', 'FILE_GreenlandCentral4', 'FILE_GreenlandCentral5',\
    'FILE_Cook_Greenland_dust_L', 'FILE_Cook_Greenland_dust_C', 'FILE_Cook_Greenland_dust_H', 'FILE_snw_alg', 'FILE_glacier_algae',\
    'tau', 'g', 'SSA', 'mu_not', 'nbr_wvl', 'wvl', 'Fs', 'Fd', 'L_snw', 'flx_slr'])


##############################
## 2) Set working directory 
##############################

# set dir_base to the location of the BioSNICAR_GO_PY folder
inputs.dir_base = '/home/joe/Code/BioSNICAR_GO_PY/'
savepath = inputs.dir_base # base path for saving figures

################################
## 3) Choose plot/print options
################################

show_figs = False # toggle to display spectral albedo figure
save_figs = True # toggle to save spectral albedo figure to file
print_BBA = True # toggle to print broadband albedo to terminal
print_band_ratios = False # toggle to print various band ratios to terminal
smooth = False # apply optional smoothing function (Savitzky-Golay filter)
window_size = 9 # if applying smoothing filter, define window size
poly_order = 3 # if applying smoothing filter, define order of polynomial

#######################################
## 4) RADIATIVE TRANSFER CONFIGURATION
#######################################

inputs.DIRECT   = 1       # 1= Direct-beam incident flux, 0= Diffuse incident flux
inputs.APRX_TYP = 1        # 1= Eddington, 2= Quadrature, 3= Hemispheric Mean
inputs.DELTA    = 1        # 1= Apply Delta approximation, 0= No delta
inputs.solzen   = 50      # if DIRECT give solar zenith angle between 0 and 89 degrees (from 0 = nadir, 90 = horizon)

# CHOOSE ATMOSPHERIC PROFILE for surface-incident flux:
#    0 = mid-latitude winter
#    1 = mid-latitude summer
#    2 = sub-Arctic winter
#    3 = sub-Arctic summer
#    4 = Summit,Greenland (sub-Arctic summer, surface pressure of 796hPa)
#    5 = High Mountain (summer, surface pressure of 556 hPa)
#    6 = Top-of-atmosphere
# NOTE that clear-sky spectral fluxes are loaded when direct_beam=1,
# and cloudy-sky spectral fluxes are loaded when direct_beam=0
inputs.incoming_i = 2

###############################################################
## 4) SET UP ICE/SNOW LAYERS
# For granular layers only, choose TOON
# For granular layers + Fresnel layers below, choose ADD_DOUBLE
###############################################################

inputs.TOON = False # toggle Toon et al tridiagonal matrix solver
inputs.ADD_DOUBLE = True # toggle adding-doubling solver

inputs.dz = [10, 10] # thickness of each vertical layer (unit = m)
inputs.nbr_lyr = len(inputs.dz)  # number of snow layers
inputs.layer_type = [0,0] # Fresnel layers for the ADD_DOUBLE option, set all to 0 for the TOON option
inputs.rho_layers = [700, 700] # density of each layer (unit = kg m-3) 
inputs.nbr_wvl=480 
#inputs.R_sfc = np.array([0.1 for i in range(inputs.nbr_wvl)]) # reflectance of underlying surface - set across all wavelengths
inputs.R_sfc = np.genfromtxt('./Data/rain_polished_ice_spectrum.csv', delimiter = 'csv') # import underlying ice from file

###############################################################################
## 5) SET UP OPTICAL & PHYSICAL PROPERTIES OF SNOW/ICE GRAINS
# For hexagonal plates or columns of any size choose GeometricOptics
# For sphere, spheroids, koch snowflake with optional water coating choose Mie
###############################################################################

inputs.rf_ice = 2 # define source of ice refractive index data. 0 = Warren 1984, 1 = Warren 2008, 2 = Picard 2016

# Ice grain shape can be 0 = sphere, 1 = spheroid, 2 = hexagonal plate, 3 = koch snowflake, 4 = hexagonal prisms
# For 0,1,2,3:
inputs.grain_shp =[0,0] # grain shape(He et al. 2016, 2017)
inputs.grain_rds = [130,130] # effective grain radius of snow/bubbly ice (becomes bubble rds when layer_type==1)
inputs.rwater = [0, 0] # radius of optional liquid water coating

# For 4:
inputs.side_length = [10000,10000] 
inputs.depth = [10000,10000]

# Shape factor = ratio of nonspherical grain effective radii to that of equal-volume sphere
### only activated when sno_shp > 1 (i.e. nonspherical)
### 0=use recommended default value (He et al. 2017)
### use user-specified value (between 0 and 1)
inputs.shp_fctr = [0,0] 

# Aspect ratio (ratio of width to length)
inputs.grain_ar = [0,0] 

#######################################
## 5) SET LAP CHARACTERISTICS
#######################################

# Define total number of different LAPs/aerosols in model
inputs.nbr_aer = 30

# define units for glacier algae MAC input file
# 0 = m2/kg
# 1 = m2/cell
inputs.GA_units = 0

# determine C_factor (can be None or a number)
# this is the concentrating factor that accounts for
# resolution difference in field samples and model layers
inputs.Cfactor = 10

# Set names of files containing the optical properties of these LAPs:
inputs.FILE_soot1  = 'mie_sot_ChC90_dns_1317.nc'
inputs.FILE_soot2  = 'miecot_slfsot_ChC90_dns_1317.nc'
inputs.FILE_brwnC1 = 'brC_Kirch_BCsd.nc'
inputs.FILE_brwnC2 = 'brC_Kirch_BCsd_slfcot.nc'
inputs.FILE_dust1  = 'dust_balkanski_central_size1.nc'
inputs.FILE_dust2  = 'dust_balkanski_central_size2.nc'
inputs.FILE_dust3  = 'dust_balkanski_central_size3.nc'
inputs.FILE_dust4  = 'dust_balkanski_central_size4.nc'
inputs.FILE_dust5 = 'dust_balkanski_central_size5.nc'
inputs.FILE_ash1  = 'volc_ash_eyja_central_size1.nc'
inputs.FILE_ash2 = 'volc_ash_eyja_central_size2.nc'
inputs.FILE_ash3 = 'volc_ash_eyja_central_size3.nc'
inputs.FILE_ash4 = 'volc_ash_eyja_central_size4.nc'
inputs.FILE_ash5 = 'volc_ash_eyja_central_size5.nc'
inputs.FILE_ash_st_helens = 'volc_ash_mtsthelens_20081011.nc'
inputs.FILE_Skiles_dust1 = 'dust_skiles_size1.nc'
inputs.FILE_Skiles_dust2 = 'dust_skiles_size2.nc'
inputs.FILE_Skiles_dust3 = 'dust_skiles_size3.nc'
inputs.FILE_Skiles_dust4 = 'dust_skiles_size4.nc'
inputs.FILE_Skiles_dust5 = 'dust_skiles_size5.nc'
inputs.FILE_GreenlandCentral1 = 'dust_greenland_central_size1.nc'
inputs.FILE_GreenlandCentral2 = 'dust_greenland_central_size2.nc'
inputs.FILE_GreenlandCentral3 = 'dust_greenland_central_size3.nc'
inputs.FILE_GreenlandCentral4 = 'dust_greenland_central_size4.nc'
inputs.FILE_GreenlandCentral5  = 'dust_greenland_central_size5.nc'
inputs.FILE_Cook_Greenland_dust_L = 'dust_greenland_Cook_LOW_20190911.nc'
inputs.FILE_Cook_Greenland_dust_C = 'dust_greenland_Cook_CENTRAL_20190911.nc'
inputs.FILE_Cook_Greenland_dust_H = 'dust_greenland_Cook_HIGH_20190911.nc'
inputs.FILE_snw_alg  = 'snw_alg_r025um_chla020_chlb025_cara150_carb140.nc'
inputs.FILE_glacier_algae = 'Cook2020_glacier_algae_4_40.nc'


# Indicate mass mixing ratios scenarios for each impurity (units: ng(species)/g(ice), or ppb)
# glacier algae in cells/mL if GA_units ==1, ppb if GA_units == 0.
# The script will loop over the different mixing scenarios


inputs.mss_cnc_soot1 = [0]*len(inputs.dz)    # uncoated black carbon (Bohren and Huffman, 1983)
inputs.mss_cnc_soot2 = [0]*len(inputs.dz)    # coated black carbon (Bohren and Huffman, 1983)
inputs.mss_cnc_brwnC1 = [0]*len(inputs.dz)   # uncoated brown carbon (Kirchstetter et al. (2004).)
inputs.mss_cnc_brwnC2 = [0]*len(inputs.dz)   # sulfate-coated brown carbon (Kirchstetter et al. (2004).)
inputs.mss_cnc_dust1 = [0]*len(inputs.dz)    # dust size 1 (r=0.05-0.5um) (Balkanski et al 2007)
inputs.mss_cnc_dust2 = [0]*len(inputs.dz)    # dust size 2 (r=0.5-1.25um) (Balkanski et al 2007)
inputs.mss_cnc_dust3 = [0]*len(inputs.dz)    # dust size 3 (r=1.25-2.5um) (Balkanski et al 2007)
inputs.mss_cnc_dust4 = [0]*len(inputs.dz)    # dust size 4 (r=2.5-5.0um)  (Balkanski et al 2007)
inputs.mss_cnc_dust5 = [0]*len(inputs.dz)    # dust size 5 (r=5.0-50um)  (Balkanski et al 2007)
inputs.mss_cnc_ash1 = [0]*len(inputs.dz)    # volcanic ash size 1 (r=0.05-0.5um) (Flanner et al 2014)
inputs.mss_cnc_ash2 = [0]*len(inputs.dz)    # volcanic ash size 2 (r=0.5-1.25um) (Flanner et al 2014)
inputs.mss_cnc_ash3 = [0]*len(inputs.dz)    # volcanic ash size 3 (r=1.25-2.5um) (Flanner et al 2014)
inputs.mss_cnc_ash4 = [0]*len(inputs.dz)    # volcanic ash size 4 (r=2.5-5.0um) (Flanner et al 2014)
inputs.mss_cnc_ash5 = [0]*len(inputs.dz)    # volcanic ash size 5 (r=5.0-50um) (Flanner et al 2014)
inputs.mss_cnc_ash_st_helens = [0]*len(inputs.dz)   # ashes from Mount Saint Helen's
inputs.mss_cnc_Skiles_dust1 = [0]*len(inputs.dz)   # Colorado dust size 1 (Skiles et al 2017)
inputs.mss_cnc_Skiles_dust2 = [0]*len(inputs.dz)    # Colorado dust size 2 (Skiles et al 2017)
inputs.mss_cnc_Skiles_dust3 = [0]*len(inputs.dz)    # Colorado dust size 3 (Skiles et al 2017)
inputs.mss_cnc_Skiles_dust4 = [0]*len(inputs.dz)  # Colorado dust size 4 (Skiles et al 2017)
inputs.mss_cnc_Skiles_dust5 = [0]*len(inputs.dz)  # Colorado dust size 5 (Skiles et al 2017)
inputs.mss_cnc_GreenlandCentral1 = [0]*len(inputs.dz) # Greenland Central dust size 1 (Polashenski et al 2015)
inputs.mss_cnc_GreenlandCentral2 = [0]*len(inputs.dz) # Greenland Central dust size 2 (Polashenski et al 2015)
inputs.mss_cnc_GreenlandCentral3 = [0]*len(inputs.dz) # Greenland Central dust size 3 (Polashenski et al 2015)
inputs.mss_cnc_GreenlandCentral4 = [0]*len(inputs.dz) # Greenland Central dust size 4 (Polashenski et al 2015)
inputs.mss_cnc_GreenlandCentral5 = [0]*len(inputs.dz) # Greenland Central dust size 5 (Polashenski et al 2015)
inputs.mss_cnc_Cook_Greenland_dust_L = [0]*len(inputs.dz) # GRIS dust (Cook et al. 2019 "LOW")
inputs.mss_cnc_Cook_Greenland_dust_C = [0]*len(inputs.dz) # GRIS dust 1 (Cook et al. 2019 "mean")
inputs.mss_cnc_Cook_Greenland_dust_H = [0]*len(inputs.dz) # GRIS dust 1 (Cook et al. 2019 "HIGH")
inputs.mss_cnc_snw_alg = [0]*len(inputs.dz)    # Snow Algae (spherical, C nivalis) (Cook et al. 2017)
inputs.mss_cnc_glacier_algae = [30000,0]    # glacier algae in cells/ml or ppb depending on GA_units (Cook et al. 2020)


##########################################################################
################## CALL FUNCTIONS AND PLOT OUTPUTS #######################
##########################################################################


###########################################################
## Error catching: invalid combinations of input variables
###########################################################

if inputs.TOON == True and inputs.ADD_DOUBLE == True:

    raise ValueError("ERROR: BOTH SOLVERS SELECTED: PLEASE CHOOSE EITHER TOON OR ADD_DOUBLE")

elif inputs.TOON == True and inputs.solzen < 40:
    
    raise ValueError("INVALID SOLAR ANGLE: solzen outside valid range for Toon solver - ue AD mode or solzen >= 40.")

elif np.sum(inputs.layer_type) < 1 and inputs.ADD_DOUBLE==True:
    # just warn user but let program continue - in some cases 
    # AD method preferable (stable over complete range of SZA)
    print("\nWARNING:")
    print("There are no solid ice layers included - you might prefer the faster matrix inversion method.")
    print("Toggle TOON=True and ADD_DOUBLE=False to use it.\n")

elif np.sum(inputs.layer_type) > 0 and inputs.TOON == True:

    raise ValueError("There are ice layers in the model - please use the adding-doubling solver")

if np.sum(inputs.mss_cnc_snw_alg) != 0:
    # remind user that snow algae optical properties have not yet been empirically validated
    print("WARNING: you are using snow algae as an impurity in the model.")
    print("the optical properties for these algae are theoretical.") 
    print("They were constructed from literature values for pigmentation, refractive indices and cell size")
    print("They have not yet been validated empirically.")

if inputs.solzen>89:
    inputs.solzen=89
    print("Surface irradiance profiles exist for a solar zenith angle < 90 degrees. Solzen set to 89.")
    
#########################################
## IF NO INPUT ERRORS --> FUNCTION CALLS
#########################################


outputs = snicar_feeder(inputs)


#########################
## PLOTTING AND PRINTING
#########################
albedo = outputs.albedo 
BBA = outputs.BBA 
wvl = outputs.wvl

if smooth:
    from scipy.signal import savgol_filter
    yhat = savgol_filter(albedo, window_size, poly_order)
    albedo = yhat

if print_band_ratios:

    I2DBA = albedo[51]/albedo[46]
    I3DBA = (albedo[46] - albedo[50]) / albedo[55]
    NDCI = ((albedo[50]-albedo[48])-(albedo[55]-albedo[48]))*((albedo[50]-albedo[48])/(albedo[55]-albedo[48]))
    MCI = (albedo[50]-albedo[46])/(albedo[50]+albedo[46])
    II = np.log(albedo[36])/np.log(albedo[66])

    print("\nINDEX VALUES")
    print("2DBA Index: ",I2DBA)
    print("3DBA index: ", I3DBA)
    print("NDCI index: ", NDCI)
    print("MCI index: ", MCI)
    print("Impurity Index: ", II)

if print_BBA:

    print('\nBROADBAND ALBEDO = ', BBA)


plt.plot(wvl, albedo)
plt.ylabel('ALBEDO'), plt.xlabel('WAVELENGTH (microns)'), plt.xlim(0.2,5),
plt.ylim(0,1), plt.axvline(x = 0.68,color='g',linestyle='dashed')

if show_figs:
    plt.show()

if save_figs:
    plt.savefig(str(savepath+"spectral_albedo.png"))
