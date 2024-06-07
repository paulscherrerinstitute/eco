from ..utilities.config import Namespace, Configuration
from ..aliases import NamespaceCollection
import pyttsx3
from ..utilities.path_alias import PathAlias
import os
from pathlib import Path
import shutil
from eco.elements.adj_obj import AdjustableObject
from eco.elements.adjustable import AdjustableFS

### set pgroup from user input ###
exp_path = Path("/sf/slab/exp/")
exps = [[p.stem, p.resolve().stem] for p in exp_path.glob("*")]
idx = ''
input_message = "Select the pgroup of the experiment:\n"
for index, (expname, pgroup) in enumerate(exps):
    input_message += f'{index:2}) {expname:10} ({pgroup})\n'
input_message += 'Your choice:'
while idx not in range(len(exps)):
    try:
        idx = int(input(input_message))
    except:
        continue
print(f'Selected experiment: {exps[idx][0]} {(exps[idx][1])}')
pgroup = exps[idx][1]

os.sys.path.insert(0,"/sf/slab/config/src/python/py_scilog")
_eco_lazy_init = False

cfg_path = Path(f"/sf/slab/config/eco/{pgroup}_slab_config_eco.json")
if not cfg_path.exists():
    shutil.copy2("/sf/slab/config/eco/slab_config_eco.json", cfg_path.as_posix())
_config = AdjustableFS(
    cfg_path.as_posix(), name="_config"
)

path_aliases = PathAlias()
namespace = Namespace(
    name="slab", root_module=__name__, alias_namespace=NamespaceCollection().slab
)
namespace.alias_namespace.data = []
namespace.append_obj(AdjustableObject, _config, name="config")
# Adding stuff that might be relevant for stuff configured below (e.g. config)
config.pgroup(pgroup)

namespace.append_obj(
    "set_global_memory_dir",
    "/sf/slab/config/eco/memory",
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
    lazy=True,
)

#f"/sf/bernina/data/{config['pgroup']}/res/",
namespace.append_obj(
    "Slab_Ioxos_Daq",
    name="daq",
    module_name="eco.acquisition.ioxos_slab",
    default_file_path=f'/sf/slab/data/{config.pgroup()}/res/',
    #default_file_path=f'/sf/slab/config/eco/test_acq/',
    ioxos=ioxos,
    lazy=True,
)


## Utilities
namespace.append_obj(
    "Run_Table2",
    name="run_table",
    module_name="eco.utilities.runtable",
    exp_id= config.pgroup(),
    folder_id= "1n10Sfib-P9xqUhIQ0UuYUEkb_DpY3pcd",
    exp_path= f"/sf/slab/data/{config.pgroup()}/res/run_table/",
    #exp_path= f"/sf/slab/config/eco/test_acq/",
    devices= "slab",
    keydf_fname= "/sf/slab/config/eco/run_table/gspread_keys.pkl",
    cred_fname= "/sf/slab/config/eco/run_table/pandas_push",
    gsheet_key_path= "/sf/slab/config/eco/run_table/run_table_gsheet_keys", 
    lazy=True,
)


namespace.append_obj(
    "Lakeshore_331",
    pvname = "SLAB-LLS-UNIT1",
    name = "cryostat_janis",
    module_name="eco.devices_general.temperature_controllers",
    lazy=True,
)
   
namespace.append_obj(
    "Env_Sensors",
    name="env_sensors",
    module_name="eco.sample_env.environment_sensors",
    lazy=True,
)

## 800pp setup stages
namespace.append_obj(
    "SmaractStreamdevice",
    pvname = f"SLAB-LMTS-LAM11",
    accuracy=1e-3,
    name="delay_800pp_stg",
    module_name="eco.devices_general.motors",
    offset_file=f"/sf/slab/config/eco/reference_values/smaract_delay_800pp_stg",
    lazy=True,
)
namespace.append_obj(
    "DelayTime",
    module_name="eco.loptics.bernina_laser",
    stage=delay_800pp_stg,
    name="delay_800pp",
)
namespace.append_obj(
    "MotorRecord",
    module_name="eco.devices_general.motors",
    pvname="SLAB-LMOT-M002:MOT",
    name="rotation_wp",
    lazy=True,
)


## Mid-IR setup stages
namespace.append_obj(
    "MotorRecord",
    module_name="eco.devices_general.motors",
    pvname="SLAB-LMOT-M001:MOT",
    name="delay_mirpp_stg",
    lazy=True,
)
namespace.append_obj(
    "DelayTime",
    module_name="eco.loptics.bernina_laser",
    stage=delay_mirpp_stg,
    name="delay_mirpp",
)

## Other stages

namespace.append_obj(
    "MotorRecord",
    module_name="eco.devices_general.motors",
    pvname="SLAB-LMOT-M003:MOT",
    name="rotation_micos_1",
    lazy=True,
)
namespace.append_obj(
    "MotorRecord",
    module_name="eco.devices_general.motors",
    pvname="SLAB-LMOT-M004:MOT",
    name="rotation_micos_2",
    lazy=True,
)



## Scan callback functions

def _message_end_scan(scan):
    e = pyttsx3.init()
    e.say(f"Finished run {scan.run_number}.")
    e.runAndWait()
    e.stop()


callbacks_start_scan = []
callbacks_end_scan = []

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
    #scan_info_dir="/sf/slab/config/eco/test_acq/scan_info",
    scan_info_dir=f"/sf/slab/data/{config.pgroup()}/res/scan_info",
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


