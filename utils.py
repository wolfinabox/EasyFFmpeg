#========================================================#
# Easy FFmpeg - An FFmpeg wrapper application, by wolfinabox
# v0.2
# This software uses libraries from the FFmpeg project under the LGPLv2.1
#========================================================#
from pyparsing import Word,nums,CaselessLiteral,ParseException
from subprocess import Popen,PIPE,STDOUT
from json import loads
def ask(question,options=None,default=None,validator=None):
    """
    Ask a question to the user, and return the answer once valid.\n
    `question` The question to ask\n
    `options` A list, or None if any input is valid\n
    `default` The default option to choose. Is selected if user passes no input and.\n
    `validator` A function to check the user's input, if `options` is None\n
    Example output:\n
    What would you like to do?>\n
    1>  Play again\n
    2>  Check options\n
    [3]>Quit
    """

    spacing='  'if default is not None and options is not None else ' '
    answer=None
    while answer is None:
        print(question)
        #If options given
        if options is not None:
            for i,option in enumerate(options):
                is_default=(default is not None and ((is_int(default) and default==i) or (isinstance(default,str) and (default.lower()==option.lower()))))
                print((f'[{i+1}]' if is_default else f'{i+1}')+'>'+('' if is_default else spacing)+option)
        #Get input
        answer=input('> ')
        #Check input
        #Check options, if given
        if options is not None:
            #Check if no input given and default
            if not answer.strip() and default is not None:
                if is_int(default):
                    return options[default]
                else: return default
            
            #If they wrote it by input
            if answer.lower() in map(str.lower,map(str,options)):
                return answer

            #If they chose the number
            if is_int(answer) and int(answer)-1 in range(0,len(options)):
                return options[int(answer)-1]
        #If no options
        elif validator is not None:
            if answer is None and default is not None:
                return default
            if validator(answer):
                return answer
        elif validator is None and options is None:
            if answer is None:
                return default
            return answer
        answer=None

def is_int(s:str):
    """
    Return whether or not the str `s` is an int.
    """
    try:
        int(s)
        return True
    except ValueError:
        return False

def askYN(question:str,default='')->bool:
    """
    Asks the user a yes/no question until a valid input is given.\n
    <question> : The question to ask\n
    <default>  : A default option to give
    """
    default=default.strip().lower()
    response='0'
    qText=(question+(' ['+default.lower().strip()+']') if default and default[0] in ('y','n') else question)+': '
    while response[0] not in ('y','n'):
        response=input(qText).strip().lower()
        if not response or response.isspace():
                response=default if default in ('y','n') else '0'

    return response[0]=='y'

def convert_size_to_bytes(size_str:str):
    """
    Converts a size string (eg: "12gb") to bytes.
    """
    multipliers={"kb":1000,"mb":1000000,"gb":1000000000,"tb":1000000000000} #god help whoever converts a tb file
    expr=Word(nums+','+'.').setParseAction(lambda toks:float(toks[0])).setResultsName('size')+(CaselessLiteral('kb')^ CaselessLiteral('mb') ^ CaselessLiteral('gb') ^ CaselessLiteral('tb')).setParseAction(lambda toks:multipliers[toks[0]]).setResultsName('mult')
    result=None
    try:
        result=expr.parseString(size_str.replace(',',''))
    except ParseException:
        return None
    return result.size*result.mult

def is_executable()->bool:
    """
    Determine if the current script is packaged as an executable\n
    (EG: If packed into a .exe with PyInstaller)\n
    returns : True/False, if the script is an executable
    """
    import sys
    return getattr(sys,'frozen',False)

def script_dir()->str:
    """
    Get the path to the current script's directory, whether running as an executable or in an interpreter.\n
    returns : A string containing the path to the script directory.
    """
    from os import path
    import sys
    return path.dirname(sys.executable) if is_executable() else path.dirname(path.realpath(sys.argv[0]))

def local_path(dir_name:str)->str:
    """
    Get the absolute path to a local file/directory __MEIPASS or .), whether running as an executable or in an interpreter.\n
    returns : A string containing the path to the local file/directory
    """
    from os import path
    import sys
    return path.join(sys._MEIPASS, dir_name) if is_executable() else path.join(script_dir(),dir_name)

def get_video_info(filename:str,ffprobe:str):
    """
    Get the video info from a video file.\n
    Returns a JSON object
    """
    command = [ffprobe,
            "-loglevel",  "quiet",
            "-print_format", "json",
             "-show_format",
             "-show_streams",
             filename
             ]
    pipe = Popen(command, stdout=PIPE, stderr=STDOUT)
    out, err = pipe.communicate()
    return loads(out)