from configparser import SafeConfigParser
import os
configfile="config.ini"



config_parser = SafeConfigParser()
config_parser.read(configfile)
if os.name=="nt": #means this program is running on windows
    if os.getlogin()=="g.chauveau":
        config_parser.set("filesystem", "passerelle_path", config_parser["filesystem"]["passerelle_path_windows"])
    else:
        config_parser.set("filesystem", "passerelle_path", config_parser["filesystem"]["passerelle_path_windows"])
elif os.name=='posix': #means this program is running on linux
    if os.getlogin()=="guillaume":
        config_parser.set("filesystem", "passerelle_path", config_parser["filesystem"]["passerelle_path_linux_guillaume"])
    else:
        config_parser.set("filesystem", "passerelle_path", config_parser["filesystem"]["passerelle_path_linux"])
else :
    print("Unknown OS")