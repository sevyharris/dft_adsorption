# Sevy Harris
# 2021-11-26
# This is the main file to control all jobs


import os
import sys
import logging
import yaml

# input variables - ask Lance for access to dftinputgen

# surface element
# adsorbate name
# surface site
# DFT functional
# energy cutoffs
# k pts sampling
# vacuum between unit cells
# force convergence

# TODO check for restart


pseudos_dir = '/home/harris.se/espresso/pseudos'  # TODO handle this with environment variable
BASEDIR = '/scratch/harris.se/espresso/copper111/co2/'
os.makedirs(BASEDIR, exist_ok=True)

############################################################################
# Set up logging
logfile = os.path.join(BASEDIR, 'DFT_ADSORPTION.log')
if os.path.exists(logfile):
    os.rename(logfile, os.path.join(BASEDIR, 'DFT_ADSORPTION.log.old'))

logfile_handle = logging.FileHandler(logfile)
stdout_handle = logging.StreamHandler(sys.stdout)
logging.basicConfig(
    format='%(asctime)s\t%(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logfile_handle, stdout_handle]
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.info('Starting DFT Adsorption Calculation')


############################################################################
# Save settings
settings_file = os.path.join(BASEDIR, 'dft_adsorption_settings.yaml')
logger.info(f'Creating setting file {settings_file}')
settings = {
    'metal': 'Cu',
    'crystal_structure': 'fcc',
    'lattice_constant_guess': 3.6,
    'adsorbate': 'CO2',
    'site': 'top',
    'dft_functional': 'default',
    'pseudopotentials': {
        'Cu': 'Cu.pbe-dn-kjpaw_psl.1.0.0.UPF',
        'C': 'C.pbe-n-kjpaw_psl.1.0.0.UPF',
        'O': 'O.pbe-n-kjpaw_psl.1.0.0.UPF', 
    },
    'ecutwfc': 50,
    'ecutrho': 500,
    'kpts_bulk': (4, 4, 4),
    'kpts_slab': (4, 4, 1),
    'kpts_ads': None,
    'forc_conv_thr': 0.001,
    'forc_conv_N': 0,
    'vacuum_ads': 7.5,
}
# TODO mpi settings
logger.info(f'Settings:\n{settings}')
with open(settings_file, 'w') as f:
    yaml.dump(settings, f)


############################################################################
# Step 1. Compute Bulk Lattice Constant
logger.info('1. Compute bulk lattice constant')
os.makedirs(os.path.join(BASEDIR, 's1_bulk'), exist_ok=True)
# TODO check for completed job file
# TODO copy base relax.py and fill in settings
# TODO move this to a separate job
from ase.build import bulk
from ase.calculators.espresso import Espresso
metal = settings['metal']
cu_bulk = bulk(settings['metal'],
               crystalstructure=settings['crystal_structure'],
               a=settings['lattice_constant_guess'],
               cubic=True
)
espresso_settings = {
    'control': {
        'calculation': 'vc-relax',
        'forc_conv_thr': settings['forc_conv_thr'],  # 0.001
    },
    'system': {
        'occupations': 'smearing',  # required for metals
        'degauss': 0.1,
        'ecutwfc': settings['ecutwfc'],  # 50
        'ecutrho': settings['ecutrho'],  # 500
    },
    'ions': {
        'ion_dynamics': 'bfgs'
    },
    'cell': {
        'cell_dynamics': 'bfgs',
        'press': 0.0,
        'press_conv_thr': 0.5,
    }
}

bulk_calc = Espresso(pseudopotentials=settings['pseudopotentials'],
                     tstress=True,
                     tprnfor=True,
                     kpts=settings['kpts_bulk'],
                     pseudo_dir=pseudos_dir,
                     input_data=espresso_settings)
cu_bulk.calc = bulk_calc
cu_bulk.get_potential_energy()

############################################################################
# Step 2. Compute Adsorbate Geometry
logger.info('2. Compute Adsorbate Geometry')
os.makedirs(os.path.join(BASEDIR, 's2_adsorbate'), exist_ok=True)


############################################################################
# Step 3. Compute Slab Geometry
# Depends on 1
logger.info('3. Compute Slab Geometry')
os.makedirs(os.path.join(BASEDIR, 's3_slab'), exist_ok=True)


############################################################################
# Step 4. Place Adsorbate
# Depends on 2 and 3
logger.info('4. Place Adsorbate')
os.makedirs(os.path.join(BASEDIR, 's4_ads_height'), exist_ok=True)


############################################################################
# Step 5. Compute System Geometry
# Depends on 4
logger.info('5. Compute System Geometry')
os.makedirs(os.path.join(BASEDIR, 's5_system'), exist_ok=True)


