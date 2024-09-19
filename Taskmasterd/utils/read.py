from utils.CheckConfig.CheckConfig import CheckConfig
import yaml

def read_confs():
    with open('configs/test_taskmasterd.yaml') as conf_file:
            readed = yaml.safe_load(conf_file)
    check_config = CheckConfig()
    err_list = check_config.run(readed)
    if err_list:
        print("error found in config.")
        readed = {}
    return readed, err_list

    # ERROR: CANT_REREAD: invalid literal for int() with base 10: '2ss' in section 'program:teste' (file: '/etc/supervisor/conf.d/teste.conf')