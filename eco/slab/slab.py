from ..utilities.config import Namespace, Configuration
from ..aliases import NamespaceCollection
import pyttsx3
from ..utilities.path_alias import PathAlias
import os

_eco_lazy_init = False

config = Configuration(
    "/photonics/home/gac-slab/config/eco/slab_config_eco.json", name="slab_config"
)

path_aliases = PathAlias()

namespace = Namespace(
    name="slab", root_module=__name__, alias_namespace=NamespaceCollection().slab
)
namespace.alias_namespace.data = []

# Adding stuff that might be relevant for stuff configured below (e.g. config)


namespace.append_obj(
    "set_global_memory_dir",
    "~/eco/memory",
    module_name="eco.elements.memory",
    name="path_memory",
)

namespace.append_obj(
    "DataApi",
    name="archiver",
    module_name="eco.dbase.archiver",
    pv_pulse_id="SARES20-CVME-01-EVR0:RX-PULSEID",
    add_to_cnf=True,
    lazy=False,
)

#namespace.append_obj(
#    "BerninaEnv",
#    name="env_log",
#    module_name="eco.fel.atmosphere",
#    lazy=True,
#)

# adding all stuff from the config components the "old" way of configuring.
# whatever is added, it is available by the configured name in this module
# afterwards, and can be used immediately, e.g. as input argument for the next thing.

# Adding stuff the "new" way

## Utilities

namespace.append_obj(
    "Run_Table2",
    name="run_table",
    module_name="eco.utilities.runtable",
    exp_id= config["pgroup"],
    folder_id= "1DpbE8al9__P2sYkzdE0ZJsmTOGTzxVx5",
    exp_path= f"/sf/slab/data/{config['pgroup']}/res/run_table/",
    devices= "slab",
    keydf_fname= "/photonics/home/gac-slab/config/eco/run_table/gspread_keys.pkl",
    cred_fname= "/photonics/home/gac-slab/config/eco/run_table/pandas_push",
    gsheet_key_path= "/photonics/home/gac-slab/config/eco/run_table/run_table_gsheet_keys", 
    lazy=True,
)


############## experiment specific #############

# try to append pgroup folder to path !!!!! This caused eco to run in a timeout without error traceback !!!!!
try:
    import sys
    from ..utilities import TimeoutPath
    if ~TimeoutPath(f'/sf/slab/data/{config["pgroup"]}/res/').exists():
        print(
            "Could not access experiment folder, could be due to more systematic file system failure!"
        )
except:
    print("Did not succed to touch prgoup")


#### pgroup specific appending, might be temporary at this location ####

