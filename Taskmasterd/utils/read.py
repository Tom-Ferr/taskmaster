from utils.CheckConfig.CheckConfig import CheckConfig
from utils.insert_logs import insert_logs
import yaml

def read_confs(confs):
    with open('configs/test_taskmasterd.yaml') as conf_file:
            readed = yaml.safe_load(conf_file)
    check_config = CheckConfig()
    err_list = check_config.run(readed)
    if err_list:
        for err in err_list:
            insert_logs("ERRO", f"error were found in the configuration file: {err.error_text}.", confs)
        readed = {}
    return readed, err_list