from ecoinvent_interface import EcoinventRelease, EcoinventProcess, Settings, ReleaseType
#LOGIN
my_settings = Settings(username="precon13329", password="Dtm_2024")

#download VERSIONE
#release = EcoinventRelease(my_settings)
#release.list_versions2()
#release.list_system_models2("3.10")
#release.get_release(version='3.10', system_model='cutoff', release_type=ReleaseType.ecospold)

#Set VERSIONE
ep = EcoinventProcess(my_settings)
ep.set_release(version="3.10", system_model="cutoff")

ep.select_process(dataset_id="2")


ep.get_basic_info()

from ecoinvent_interface import ProcessFileType
from pathlib import Path
ep.get_file(file_type=ProcessFileType.lcia, directory=Path.cwd())

