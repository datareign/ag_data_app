import folium


WELCOME='''Welcome to the ProGro Data Management System.
         This interface is designed to allow users to interact
         with VRT and Agrimet climate data.
         This application is connected to a secure and 
         private cloud database. If you have any questions or need
         additional input options for products, crop types, and/or
         varieties, please use the link below to contact the 
         site administrator. Be sure to include detailed
         information. Thanks and Happy Farming!'''

MAIN_MENU=['Welcome',
           'Agrimet Dashboards',
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

BASEMAPS={'Google Satellite Hybrid':folium.TileLayer(
        tiles = 'http://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = True,
        control = True),
        'ESRI':folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True
       )}

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

AGRIMET_PARAMS={'Avg. Air Temp (F)':'mm','GDD':'tg',
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
              'next_level':'Next Level Ag, LLC',
              'midwest':'Midwest Laboratories',
              'western':'Western Laboratories',
              'waters':'Waters Agricultural Lab'}

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
                             'B (ppm)','Na (ppm)'],
               'midwest':['OM (%)','P1 (ppm)',
                          'P2 (ppm)','K (ppm)',
                          'Mg (ppm)','Ca (ppm)',
                          'Na (ppm)','pH',
                          'CEC (meq/100g)','%K',
                          '%Mg','%Ca','%H','%Na',
                          'NO3 (ppm)','S (ppm)',
                          'Zn (ppm)','Mn (ppm)',
                          'Fe (ppm)','Cu (ppm)',
                          'B (ppm)','Soluble Salts (mmhos/cm)'],
              'western':['pH','CEC','Texture',
                         'OM (%)','P (ppm)','K (ppm)',
                         'Mg (ppm)','Ca (ppm)','Na (ppm)',
                         'Lime (%)','NO3 (ppm)','S (ppm)',
                         'Zn (ppm)','Mn (ppm)','Fe (ppm)',
                         'Cu (ppm)','B (ppm)','Soluble Salts (mmhos/cm)'],
              'waters':['P (lbs/a)','K (lbs/a)','Mg (lbs/a)',
                        'Ca (lbs/a)','Zn (lbs/a)','Mn (lbs/a)',
                        'pHw','CEC','Lime','BS-K',
                        'BS-Mg','BS-Ca','BS-H']}

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
                             'CEC':'CEC (meq/100g)'},
               'midwest':{'SAMPLE ID':'Zone',
                          'OM':'OM (%)',
                          'P1':'P1 (ppm)',
                          'P2':'P2 (ppm)',
                          'K':'K (ppm)',
                          'MG':'Mg (ppm)',
                          'CA':'Ca (ppm)',
                          'NA':'Na (ppm)',
                          'PH':'pH',
                          'CEC':'CEC (meq/100g)',
                          'PERCENT K':'%K',
                          'PERCENT MG':'%Mg',
                          'PERCENT CA':'%Ca',
                          'PERCENT H':'%H',
                          'PERCENT NA':'%Na',
                          'NO3':'NO3 (ppm)',
                          'S':'S (ppm)',
                          'ZN':'Zn (ppm)',
                          'MN':'Mn (ppm)',
                          'FE':'Fe (ppm)',
                          'CU':'Cu (ppm)',
                          'B':'B (ppm)',
                          'SOL SALTS':'Soluble Salts (mmhos/cm)'},
              'western':{'Grid':'Zone',
                         '%OM':'OM (%)',
                         'P':'P (ppm)',
                         'K':'K (ppm)',
                         'Mg':'Mg (ppm)',
                         'Ca':'Ca (ppm)',
                         'Na':'Na (ppm)',
                         'Lime':'Lime (%)',
                         'NO3':'NO3 (ppm)',
                         'S':'S (ppm)',
                         'Zn':'Zn (ppm)',
                         'Mn':'Mn (ppm)',
                         'Fe':'Fe (ppm)',
                         'Cu':'Cu (ppm)',
                         'B':'B (ppm)',
                         'Salts':'Soluble Salts (mmhos/cm)'},
              'waters':{}}
