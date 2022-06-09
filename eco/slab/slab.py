from ..utilities.config import Namespace, Configuration
from ..aliases import NamespaceCollection
import pyttsx3
from ..utilities.path_alias import PathAlias
import os

os.sys.path.insert(0,"/sf/slab/config/src/python/py_scilog")
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
    "/photonics/home/gac-slab/config/eco/memory",
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

namespace.append_obj(
    "Slab_Ioxos",
    name="ioxos",
    module_name="eco.acquisition.ioxos_slab",
    pvbase="SLAB-LSCP1-ESB1",
    lazy=False,
)

#f"/sf/bernina/data/{config['pgroup']}/res/",
namespace.append_obj(
    "Slab_Ioxos_Daq",
    name="daq",
    module_name="eco.acquisition.ioxos_slab",
    default_file_path='/photonics/home/gac-slab/test/',
    ioxos=ioxos,
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


## Scan callback functions

def _message_end_scan(scan):
    e = pyttsx3.init()
    e.say(f"Finished run {scan.run_number}.")
    e.runAndWait()
    e.stop()


#def _copy_scan_info_to_raw(scan, daq=daq):
#    run_number = daq.get_last_run_number()
#    pgroup = daq.pgroup
#    print(f"Copying info file to run {run_number} to the raw directory of {pgroup}.")
#    response = daq.append_aux(
#        scan.scan_info_filename, pgroup=pgroup, run_number=run_number
#    )
#    print(f"Status: {response.json()['status']} Message: {response.json()['message']}")


callbacks_start_scan = []
callbacks_end_scan = [_message_end_scan]

elog=None
def _create_metadata_structure_start_scan(scan, run_table=run_table, elog=elog):
    runname = os.path.basename(scan.fina).split(".")[0]
    runno = int(runname.split("run")[1].split("_")[0])
    metadata = {
        "type": "scan",
        "name": runname.split("_", 1)[1],
        "scan_info_file": scan.scan_info_filename,
    }
    for n, adj in enumerate(scan.adjustables):
        nname = None
        nId = None
        if hasattr(adj, "Id"):
            nId = adj.Id
        if hasattr(adj, "name"):
            nname = adj.name

        metadata.update(
            {
                f"scan_motor_{n}": nname,
                f"from_motor_{n}": scan.values_todo[0][n],
                f"to_motor_{n}": scan.values_todo[-1][n],
                f"id_motor_{n}": nId,
            }
        )
    metadata.update(
        {
            "steps": len(scan.values_todo),
            "pulses_per_step": scan.pulses_per_step,
            "counters": [daq.name for daq in scan.counterCallers],
        }
    )

    try:
        try:
            metadata.update({"scan_command": get_ipython().user_ns["In"][-1]})
        except:
            print("Count not retrieve ipython scan command!")

        message_string = f'Acquisition run {runno}: {metadata["name"]}\n'
        if "scan_command" in metadata.keys():
            message_string += metadata["scan_command"] + "\n"
        message_string += metadata["scan_info_file"] + "\n"
        scan._elog_id = elog.post(
            message_string, Title=f'Run {runno}: {metadata["name"]}'
        )
        metadata.update({"elog_message_id": scan._elog_id})
        metadata.update({"elog_post_link": scan._elog._log._url + str(scan._elog_id)})
    except:
        print("elog posting failed")
    try:
        run_table.append_run(runno, metadata=metadata)
    except:
        print("WARNING: issue adding data to run table")


# <<<< Extract for run table and elog
callbacks_start_scan.append(_create_metadata_structure_start_scan)


    #scan_info_dir=f"/sf/slab/data/{config['pgroup']}/res/scan_info",
namespace.append_obj(
    "Scans",
    data_base_dir="scan_data",
    scan_info_dir="/photonics/home/gac-slab/test/scan_info",
    default_counters=[daq],
    checker=False,
    scan_directories=True,
    callbacks_start_scan=callbacks_start_scan,
    callbacks_end_scan=callbacks_end_scan,
    run_table=run_table,
    elog=elog,
    name="scans",
    module_name="eco.acquisition.scan",
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

