
WELCOME='''Welcome to the ProGro Data Management System.
         This interface is designed to allow users to develop 
         detailed crop plans including planned field assignments, 
         varieties/hybrids, and inputs. To make this process
         as efficient as possible, almost all entries are
         restricted to drop-down selection boxes.
         This application is connected to a secure and 
         private cloud database. You also have the option 
         to download your data to maintain your own copies and 
         use as you wish. If you have any questions or need
         additional input options for products, crop types, and/or
         varieties, please use the link below to contact the 
         site administrator. Be sure to include detailed
         information. Thanks and Happy Farming!'''

MAIN_MENU=['Welcome',
           'Agrimet Dashboards',
           'Planning Tools',
           'Application Tools',
           'VRT Tools']
PLANNING_OPTIONS=['Assign Crops',
                  'Assign Inputs',
                  'Delete Assignment',
                  'View Crop Plan',
                  'View Input Plan',
                  'View Nutrient Plan']
APPLICATION_OPTIONS=['Log Input Application',
                     'Delete Application']
VRT_OPTIONS=['Zone Fertilizer Dashboard']
AGRIMET_OPTIONS=['Agrimet Daily Weather',
                 'Agrimet Daily Crop ET']

NUTRIENTS=['N','P','K','S','Mg','Ca','B','Cl','Mn','Fe','Cu','Zn','Mo']

DRY_UNITS=['lbs/acre','oz/acre','tons/acre']

LIQUID_UNITS=['qt/acre','gal/acre','pt/acre','oz/acre']

YEARS=[2022,2023,2024,2025]

AGRIMET_BASE_DAILY_ADDRESS='https://www.usbr.gov/pn-bin/daily.pl?list='
AGRIMET_BASE_DAILY_ET_ADDRESS='https://www.usbr.gov/pn/agrimet/chart/'

AGRIMET_STATIONS={'Rexburg, ID':'rxgi','Rigby, ID':'rgbi',
                  'Ririe, ID':'rrii','Osgood, ID':'osgi',
                  'Shelley, ID':'shli','Ashton, ID':'ahti',
                  'Terreton, ID':'trti','Monteview, ID':'mnti',
                  'Salmon, ID':'slmi','Aberdeen, ID':'abei',
                  'Arco, ID':'rrci','Blackfoot, ID':'acki',
                  'West Blackfoot, ID':'tabi','Roberts, ID':'robi',
                  'Hamer, ID':'hami','Howe, ID':'owei',
                  'Fort Hall, ID':'fthi','Hamilton, MT':'covm',
                  'Deer Lodge, MT':'drlm'}

AGRIMET_PARAMS={'Avg. Air Temp (F)':'mm','GGD':'tg',
                'Daily Precip. (inches)':'pp',
                'Avg. Soil Temp (F)':'yw',
                'Avg. Wind Speed (mph)':'ua',
                'Min. Air Temp (F)':'mn',
                'Max. Air Temp (F)':'mx'}

AGRIMET_CROP_CODES={'ETr':'REFERENCE EVAPOTRANSPIRATION (KIMBERLY-PENMAN ALFALFA REFERENCE)',
                    'ALFM':'ALFALFA (MEAN)',
                    'ALFN':'ALFALFA (NEW PLANT)',
                    'ALFP':'ALFALFA (PEAK)',
                    'APPL':'APPLES',
                    'ASPA':'ASPARAGUS',
                    'BEAN':'DRY BEANS',
                    'BEET':'SUGAR BEETS',
                    'BLGR':'BLUEGRASS SEED',
                    'BLUB':'BLUEBERRIES',
                    'BROC':'BROCCOLI',
                    'CABG':'CABBAGE',
                    'CGRP':'CONCORD GRAPES',
                    'CHRY':'CHERRIES',
                    'CRAN':'CRANBERRIES',
                    'CRTS':'CARROT SEED',
                    'FCRN':'FIELD CORN',
                    'GARL':'GARLIC',
                    'GRSD':'GRASS SEED',
                    'HAYP':'FESCUE GRASS HAY (PEAK DAILY CONSUMPTIVE USE FOR MATURE GRASS HAY)',
                    'HAYM':'FESCUE GRASS HAY (MEAN ANNUAL USE WITH 3 SEASONAL CUTTINGS)',
                    'HOPS':'HOPS',
                    'LAWN':'LAWN',
                    'LILY':'EASTER LILIES',
                    'MELN':'MELONS',
                    'NMNT':'NEW MINT',
                    'ONYN':'ONION',
                    'ORCH':'ORCHARDS',
                    'PAST':'PASTURE',
                    'PEAR':'PEARS',
                    'PEAS':'PEAS',
                    'PECH':'PEACHES',
                    'POP1':'FIRST YEAR POPLAR TREES',
                    'POP2':'SECOND YEAR POPLAR TREES',
                    'POP3':'THIRD YEAR + POPLAR TREES',
                    'POTA':'POTATOES',
                    'POTS':'POTATOES (SHEPODY)',
                    'PPMT':'PEPPERMINT',
                    'RAPE':'RAPESEED (CANOLA)',
                    'SAFL':'SAFFLOWER',
                    'SPMT':'SPEARMINT',
                    'SBAR':'SPRING BARLEY',
                    'SBRY':'STRAWBERRY',
                    'SCRN':'SWEET CORN',
                    'SGRN':'SPRING GRAIN',
                    'SPMT':'SPEARMINT',
                    'TBER':'TRAILING BERRIES',
                    'WGRN':'WINTER GRAIN',
                    'WGRP':'WINE GRAPE'}
                  
SOIL_LAB_KEY={'tx_am':'Texas A&M AgriLife Extension',
              'next_level':'Next Level Ag, LLC'}

LAB_DATA_COLS={'tx_am':['pH',
                        'Conductivity (umho/cm)',
                        'NO3N (ppm)','P (ppm)',
                        'K (ppm)','Ca (ppm)',
                        'Mg (ppm)','S (ppm)',
                        'Na (ppm)'],
               'next_level':['Total NO3 (lbs)',
                             'P-Olsen (ppm)',
                             'K (ppm)','S (ppm)',
                             'pH','OM (%)',
                             'Soluble Salts (dS/m)',
                             'CEC (meq/100g)',
                             'Ca (ppm)','Mg (ppm)', 
                             'Zn (ppm)','Mn (ppm)', 
                             'Fe (ppm)','Cu (ppm)', 
                             'B (ppm)','Na (ppm)']}

LAB_DATA_MAPS={'tx_am':{'Sample ID':'Zone',
                        'Cond':'Conductivity (umho/cm)',
                        'NO3N':'NO3N (ppm)',
                        'P':'P (ppm)',
                        'K':'K (ppm)',
                        'Ca':'Ca (ppm)',
                        'Mg':'Mg (ppm)',
                        'S':'S (ppm)',
                        'Na':'Na (ppm)'},
               'next_level':{'Zone ID/Grid':'Zone',
                             'OM':'OM (%)',
                             'Total N':'Total NO3 (lbs)',
                             'P-Olsen':'P-Olsen (ppm)',
                             'K':'K (ppm)',
                             'Ca':'Ca (ppm)',
                             'Mg':'Mg (ppm)',
                             'Zn':'Zn (ppm)',
                             'Mn':'Mn (ppm)',
                             'Fe':'Fe (ppm)',
                             'Al':'Al (ppm)',
                             'Mo':'Mo (ppm)',
                             'Cu':'Cu (ppm)',
                             'B':'B (ppm)',
                             'S':'S (ppm)',
                             'S lbs':'S (lbs)',
                             'Na':'Na (ppm)',
                             'Cl':'Cl (ppm)',
                             'CEC':'CEC (meq/100g)'}}
