#========================================================#
# Easy FFmpeg - An FFmpeg wrapper application, by wolfinabox
# v0.2
# This software uses libraries from the FFmpeg project under the LGPLv2.1
#========================================================#
from utils import *
from os.path import exists, splitext, split, join, basename

from subprocess import call, DEVNULL
from math import floor, ceil


class FFMpegCommand():
    """
    Base class for an FFMpeg command dispatcher
    """

    def __init__(self, command: str, ffmpeg_exe: str):
        self.command = command
        self.ffmpeg_exe = ffmpeg_exe
        self.allowed_filetypes = None
        self.ffmpeg_comand = None
        self.requires_additional_arguments = False
        self.additional_arguments_help = ""
        self.additional_arguments_options = None
        self.additional_arguments_validator = None

    def run(self, files: list, options: dict = None, **kwargs):
        """
        Run the FFMpeg command\n
        `files` The file(s) to operate on\n
        `options` Options retrieved from the program's arguments.\n
        `kwargs` Other objects needed for specific FFMpeg commands
        """
        raise NotImplementedError


class FLVtoMP4(FFMpegCommand):
    def __init__(self, command, ffmpeg_exe):
        super().__init__(command, ffmpeg_exe)
        self.allowed_filetypes = ['flv']
        self.ffmpeg_comand = '{0} -v error -stats -i "{1}" -c copy -copyts "{2}" -y'

    def run(self, files, options=None, **kwargs):
        new_files = []
        for file in files:
            if not exists(file):
                print(f'File "{file}" does not exist. Ignoring...')
                continue
            filetype = splitext(file)[1][1:]
            if filetype not in self.allowed_filetypes:
                print(
                    f'File type "{filetype}" not supported with command "{self.command}". Ignoring...')
                continue
            new_filename = f'{splitext(file)[0]}.mp4'
            full_command = self.ffmpeg_comand.format(
                self.ffmpeg_exe, file, new_filename)
            print(f'Processing file "{file}"...')
            call(
                full_command, stdout=DEVNULL if not options['debug'] else None, stderr=DEVNULL if not options['debug'] else None)
            print(f'Done! Saved to "{splitext(file)[0]}.mp4"')
            new_files.append(new_filename)
        return new_files


class CompressToSize(FFMpegCommand):
    def __init__(self, command, ffmpeg_exe):
        super().__init__(command, ffmpeg_exe)
        self.allowed_filetypes = ['mp4', 'mov', 'mkv']
        self.ffmpeg_comand = '{0} -v error -stats -i "{1}"  -vcodec libx264 -b {3} -minrate {3} -maxrate {3} -bufsize {3} "{2}" -y'
        self.requires_additional_arguments = True
        self.additional_arguments_help = "Size to compress to? (eg: 12.5mb)"
        self.additional_arguments_validator = lambda s: convert_size_to_bytes(
            s) is not None

    def run(self, files, options=None, **kwargs):
        desired_size = convert_size_to_bytes(options['arguments'])
        new_files = []
        for file in files:
            if not exists(file):
                print(f'File "{file}" does not exist. Ignoring...')
                continue
            filetype = splitext(file)[1][1:]
            if filetype not in self.allowed_filetypes:
                print(
                    f'File type "{filetype}" not supported with command "{self.command}". Ignoring...')
                continue
            # Calculations
            video_info = get_video_info(file, kwargs['ffprobe_exe'])
            # Check size
            if desired_size > int(video_info['format']['size']):
                print(
                    f'Desired size greater than original file size for "{basename(file)}"')
                if not askYN('Process anyway?', default='n'):
                    continue

            # video length in seconds
            length = ceil(float(video_info['format']['duration']))

            new_bitrate = floor((desired_size*8)/length)

            new_filename = join(split(file)[0], ('compressed_'+split(file)[1]))
            full_command = self.ffmpeg_comand.format(
                self.ffmpeg_exe, file, new_filename, new_bitrate)
            print(f'Processing file "{basename(file)}"...')
            call(
                full_command, stdout=DEVNULL if not options['debug'] else None, stderr=DEVNULL if not options['debug'] else None)
            print(f'Done! Saved to "{new_filename}"')
            new_files.append(new_filename)
        return new_files



class RemoveAudio(FFMpegCommand):
    def __init__(self, command, ffmpeg_exe):
        super().__init__(command, ffmpeg_exe)
        self.allowed_filetypes = ['flv','mp4','mkv','mov']
        self.ffmpeg_comand = '{0} -v error -stats -i "{1}" -c copy -copyts -an "{2}" -y'

    def run(self, files, options=None, **kwargs):
        new_files = []
        for file in files:
            if not exists(file):
                print(f'File "{file}" does not exist. Ignoring...')
                continue
            filetype = splitext(file)[1][1:]
            if filetype not in self.allowed_filetypes:
                print(
                    f'File type "{filetype}" not supported with command "{self.command}". Ignoring...')
                continue
            new_filename = join(split(file)[0], ('noaudio_'+split(file)[1]))
            full_command = self.ffmpeg_comand.format(
                self.ffmpeg_exe, file, new_filename)
            print(f'Processing file "{file}"...')
            call(
                full_command, stdout=DEVNULL if not options['debug'] else None, stderr=DEVNULL if not options['debug'] else None)
            print(f'Done! Saved to "{new_filename}')
            new_files.append(new_filename)
        return new_files