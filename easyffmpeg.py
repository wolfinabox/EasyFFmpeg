#========================================================#
# Easy FFmpeg - An FFmpeg wrapper application, by wolfinabox
# v0.4
# This software uses libraries from the FFmpeg project under the LGPLv2.1
#========================================================#
from argparse import ArgumentParser
from commands import *
from utils import ask, local_path,started_from_gui,Colors
from shlex import split as shplit
from os import path, name,remove,cpu_count

# Globals
#========================================================#
resources_dir = local_path('resources')
ffmpeg_exe = path.join(resources_dir, path.join('win','ffmpeg.exe') if name=='nt' else path.join('linux','ffmpeg'))
ffprobe_exe = path.join(resources_dir, path.join('win','ffprobe.exe') if name=='nt' else path.join('linux','ffprobe'))
threads=cpu_count()
# Arguments
#========================================================#
parser = ArgumentParser(description='Simply run popular FFMpeg commands.')
parser.add_argument("files", help="File(s) to process",
                    nargs="*", default=None)
#parser.add_argument("-s","--skip",help="Skip confirmations",action="store_true")
parser.add_argument(
    "-d", "--debug", help="Show debug output", action="store_true")
parser.add_argument("-c", "--command", help=', '.join(
    f'"{command}"' for command in commands), action="store", default=None)
parser.add_argument("-t","--threads",help="Number of threads for FFmpeg to use (default all)",action="store",default=None)
parser.add_argument("-a", "--arguments",
                    help="Additional arguments for FFMpeg command. Varies per command", action="store", default=None)

# Setup
#========================================================#
print(f'{Colors.INFO}<<Easy FFmpeg v0.4, by wolfinabox>>')
print(f'{Colors.INFO}<<This software uses libraries from the FFmpeg project under the LGPLv2.1>>')
# if name != 'nt':
#     print('Sorry, this application currently only supports Windows.')
#     input('Press return to exit...')
#     exit(-1)


args = vars(parser.parse_args())
files = args.pop('files')

if args['debug']:
    print(f'{Colors.DEBUG}Resource folder: "{resources_dir}"')

if not path.exists(ffmpeg_exe) or not path.exists(ffprobe_exe):
    print({Colors.ERROR}+'Could not find FFmpeg or FFPlay executables. If you are running this script from source,\n\
        create a ./resources/win directory if on windows, or ./resources/linux directory, and place the executables there.\n\
        If you are running this from a release executable, try a new release from https://github.com/wolfinabox/EasyFFmpeg/releases,\n\
        or post an issue https://github.com/wolfinabox/EasyFFmpeg/issues.')

    if started_from_gui(): input_color_supported(f'{Colors.ASK}Press return to exit...')
    exit(-1)

# Check if invalid command
if args['command'] is not None and args['command'] not in commands:
    parser.print_help()
    if started_from_gui(): input_color_supported(f'{Colors.ASK}Press return to exit...')
    exit()

# Get options not specified from command line from input
if args['command'] is None:
    args['command'] = ask(f'{Colors.ASK}Command to run?', options=list(commands.keys()))
if not files:
    files = shplit(
        ask(f'{Colors.ASK}Files to process? (Please surround each in "quotes")'))
args['threads']=threads if (args['threads'] is None or args['threads']>threads) else args['threads']

command_runner: FFMpegCommand = commands[args['command']](
    args['command'], ffmpeg_exe,options=args)
# If additional arguments needed
if command_runner.requires_additional_arguments:
    # If args not supplied, ask
    if args['arguments'] is None or (command_runner.additional_arguments_validator is not None and not command_runner.additional_arguments_validator(args['arguments'])):
        args['arguments'] = ask(Colors.ASK+command_runner.additional_arguments_help,
                                options=command_runner.additional_arguments_options,
                                validator=command_runner.additional_arguments_validator)
    # If they are supplied, validate

# Run the command
print(f'Running "{args["command"]}" on {len(files)} file{"s" if len(files)>1 else ""}...'+'\n')
if args['debug']:
    print(f'{Colors.DEBUG}Running FFmpeg with {args["threads"]} threads')
for file in files:
    result_file=command_runner.run(file, ffprobe_exe=ffprobe_exe)
    if result_file: print(f'{Colors.INFO}Done! Saved to "{result_file}"')


print(f'{Colors.INFO}All done!')
if askYN(f'{Colors.ASK}Delete original files?','n'):
    for file in files:
        if exists(file):
            remove(file)
        
if started_from_gui(): input_color_supported(f'{Colors.ASK}Press return to exit...')
print(Colors.RESET,end='')