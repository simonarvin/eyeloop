from os import system, name

tab="       "
linebreak="\n{}{}\n".format(tab,30*"_")
version="0.1"
journal     ="Journal article:    [link]"
git         ="Git:                https://github.com/simonarvin/eyeloop"

def clear() -> None:

    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

def logo(label="") -> None:
    logo=r"""
                                >> {}

     ___      ___       __   __   __
    |__  \ / |__  |    /  \ /  \ |__)
    |___  |  |___ |___ \__/ \__/ |

                                  v{}
                                           """.format(label,version)
    return logo
def welcome(label="") -> None:
    clear()
    msg=r"""
    {}
    Developed by Simon Arvin
    Yonehara Laboratory
    Danish Research Institute of
    Translational Neuroscience (DANDRITE)

    {}
    {}{}""".format(logo(label),git, journal,linebreak)
    print(msg)

def help() -> None:
    msg="""
    Puptrack user-guide (help; manual)
        This brief user-guide describes how to get Puptrack running,
        step by step. In addition, it lists client commands and command
        line arguments. It does not describe how to utilize it to its
        full extent. For this, refer to the journal article (--journal).

    Step-by-step:

    Client commands:

    Command line arguments:
    """
    print(msg)
