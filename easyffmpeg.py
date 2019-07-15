#========================================================#
# Easy FFmpeg - An FFmpeg wrapper application, by wolfinabox
# v0.2
# This software uses libraries from the FFmpeg project under the LGPLv2.1
#========================================================#
from argparse import ArgumentParser
from commands import *
from utils import ask, local_path
from shlex import split as shplit
from os import path, name

# Globals
#========================================================#
commands = {"FLV to MP4": FLVtoMP4, "Compress to Size": CompressToSize,'Remove Audio':RemoveAudio}
resources_dir = local_path('resources')
ffmpeg_exe = path.join(resources_dir, 'ffmpeg.exe')
ffprobe_exe = path.join(resources_dir, 'ffprobe.exe')

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
parser.add_argument("-a", "--arguments",
                    help="Additional arguments for FFMpeg command. Varies per command", action="store", default=None)

# Setup
#========================================================#
print('<<Easy FFmpeg v0.2, by wolfinabox>>')
print('<<This software uses libraries from the FFmpeg project under the LGPLv2.1>>')
if name != 'nt':
    print('Sorry, this application currently only supports Windows.')
    input('Press return to exit...')
    exit(-1)

if not path.exists(ffmpeg_exe) or not path.exists(ffprobe_exe):
    print('Could not find FFmpeg or FFPlay executables. If you are running this script from source,\n\
        create a ./resources directory, and place the executables there. If you are running this \n\
        from a release executable, try a new release from https://github.com/wolfinabox/EasyFFmpeg/releases,\n\
        or post an issue https://github.com/wolfinabox/EasyFFmpeg/issues.')
    input('Press return to exit...')
    exit(-1)

args = vars(parser.parse_args())
files = args.pop('files')
if args['debug']:
    print(f'Resource folder: "{local_path("")}"')
# Check if invalid command
if args['command'] is not None and args['command'] not in commands:
    parser.print_help()
    input('Press return to exit...')
    exit()

# Get options not specified from command line from input
if args['command'] is None:
    args['command'] = ask('Command to run?', options=list(commands.keys()))
if not files:
    files = shplit(
        ask("Files to process? (Please surround each in \"quotes\")"))

command_runner: FFMpegCommand = commands[args['command']](
    args['command'], ffmpeg_exe)
# If additional arguments needed
if command_runner.requires_additional_arguments:
    # If args not supplied, ask
    if args['arguments'] is None or (command_runner.additional_arguments_validator is not None and not command_runner.additional_arguments_validator(args['arguments'])):
        args['arguments'] = ask(command_runner.additional_arguments_help,
                                options=command_runner.additional_arguments_options,
                                validator=command_runner.additional_arguments_validator)
    # If they are supplied, validate

# Run the command
command_runner.run(files, options=args, ffprobe_exe=ffprobe_exe)
print('All done!')
input('Press return to exit...')