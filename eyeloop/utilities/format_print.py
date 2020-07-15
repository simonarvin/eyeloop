from os import system, name

import eyeloop.config as config

tab = "       "
linebreak = "\n{}{}\n".format(tab, 30 * "_")

journal = "doi:                  10.1101/2020.07.03.186387"
git = "repo:                 https://github.com/simonarvin/eyeloop"


def clear() -> None:
    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def logo(label="") -> None:
    logo = r"""
                                >> {}

     ___      ___       __   __   __
    |__  \ / |__  |    /  \ /  \ |__)
    |___  |  |___ |___ \__/ \__/ |

                                  v{}
                                           """.format(label, config.version)
    return logo


def welcome(label="") -> None:
    clear()
    msg = r"""
    {}
    Developed by Simon Arvin
    Yonehara Laboratory
    Danish Research Institute of
    Translational Neuroscience (DANDRITE)

    {}
    {}{}""".format(logo(label), git, journal, linebreak)
    print(msg)
