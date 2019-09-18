#========================================================#
# Easy FFmpeg - An FFmpeg wrapper application, by wolfinabox
# v0.2
# This software uses libraries from the FFmpeg project under the LGPLv2.1
#========================================================#
from utils import *
from os.path import exists, splitext, split, join, basename
from os import remove

from subprocess import call, DEVNULL
from math import floor, ceil



class FFMpegCommand():
    """
    Base class for an FFMpeg command dispatcher
    """

    def __init__(self, command: str, ffmpeg_exe: str, options: dict = None):
        self.command = command
        self.ffmpeg_exe = ffmpeg_exe
        self.allowed_filetypes = None
        self.options=options
        self.ffmpeg_command = '{0} -v error -stats -i "{1}"'+(f' -threads {self.options["threads"]} ')
        self.requires_additional_arguments = False
        self.additional_arguments_help = ""
        self.additional_arguments_options = None
        self.additional_arguments_validator = None

    def run(self, file: str, **kwargs):
        """
        Run the FFMpeg command\n
        `file` The file to operate on\n
        `options` Options retrieved from the program's arguments.\n
        `kwargs` Other objects needed for specific FFMpeg commands
        """
        raise NotImplementedError

    def check_file(self,file:str):
        """
        Validate the given file path. Default function checks if file exists, and is a type this command accepts.\n
        Returns True/False if file is valid
        """
        ...
        if not exists(file):
            print(f'File "{file}" does not exist. Ignoring...')
            return False
        filetype = splitext(file)[1][1:]
        if filetype not in self.allowed_filetypes:
            print(
                f'File type "{filetype}" not supported with command "{self.command}". Ignoring...')
            return False
        return True


class FLVtoMP4(FFMpegCommand):
    def __init__(self, command, ffmpeg_exe,options:dict=None):
        super().__init__(command, ffmpeg_exe,options)
        self.allowed_filetypes = ['flv']
        self.ffmpeg_command += '-c copy -copyts "{2}" -y'

    def run(self, file, **kwargs):
        if not self.check_file(file):return None
        new_filename = f'{splitext(file)[0]}.mp4'
        full_command = self.ffmpeg_command.format(
            self.ffmpeg_exe, file, new_filename)
        print(f'Processing file "{file}"...')
        if self.options['debug']: print(f'Running "{full_command}"')
        retcode=call(
            full_command, stdout=DEVNULL if not self.options['debug'] else None, stderr=DEVNULL if not self.options['debug'] else None,shell=True)
        if retcode!=0:
            print('Error in FFmpeg command, file not processed')
            if exists(new_filename):
                remove(new_filename)
            return None
        return new_filename


class CompressToSize(FFMpegCommand):
    def __init__(self, command, ffmpeg_exe,options:dict=None):
        super().__init__(command, ffmpeg_exe,options)
        self.allowed_filetypes = ['mp4', 'mov', 'mkv']
        self.ffmpeg_command += '-vcodec libx264 -b {3} -minrate {3} -maxrate {3} -bufsize {3} "{2}" -y'
        self.requires_additional_arguments = True
        self.additional_arguments_help = "Size to compress to? (eg: 12.5mb)"
        self.additional_arguments_validator = lambda s: convert_size_to_bytes(
            s) is not None

    def run(self, file, **kwargs):
        if not self.check_file(file):return None
        desired_size = convert_size_to_bytes(self.options['arguments'])
        # Calculations
        video_info = get_video_info(file, kwargs['ffprobe_exe'])
        # Check size
        if desired_size > int(video_info['format']['size']):
            print(
                f'Desired size greater than original file size for "{basename(file)}"')
            if not askYN('Process anyway?', default='n'):
                print(f'Ignoring "{file}"...')
                return None

        # video length in seconds
        length = ceil(float(video_info['format']['duration']))

        new_bitrate = floor((desired_size*8)/length)

        new_filename = join(split(file)[0], ('compressed_'+split(file)[1]))
        full_command = self.ffmpeg_command.format(
            self.ffmpeg_exe, file, new_filename, new_bitrate)
        print(f'Processing file "{basename(file)}"...')
        if self.options['debug']: print(f'Running "{full_command}"')

        retcode=call(
            full_command, stdout=DEVNULL if not self.options['debug'] else None, stderr=DEVNULL if not self.options['debug'] else None,shell=True)
        if retcode!=0:
            print('Error in FFmpeg command, file not processed')
            if exists(new_filename):
                remove(new_filename)
            return None
        return new_filename

class CompressCRF(FFMpegCommand):
    def __init__(self, command, ffmpeg_exe,options:dict=None):
        super().__init__(command, ffmpeg_exe,options)
        self.allowed_filetypes = ['mp4', 'mov', 'mkv']
        self.ffmpeg_command += '-vcodec libx265 -crf {3} "{2}" -y'
        self.requires_additional_arguments = True
        self.additional_arguments_help = "Quality? (around 18-24, lower value is higher quality)"
        self.additional_arguments_validator = is_int

    def run(self, file, **kwargs):
        if not self.check_file(file):return None
        new_filename = join(split(file)[0], ('compressed_'+split(file)[1]))
        full_command = self.ffmpeg_command.format(
        self.ffmpeg_exe, file, new_filename, self.options['arguments'])

        print(f'Processing file "{basename(file)}"...')
        if self.options['debug']: print(f'Running "{full_command}"')

        retcode=call(
            full_command, stdout=DEVNULL if not self.options['debug'] else None, stderr=DEVNULL if not self.options['debug'] else None,shell=True)
        if retcode!=0:
            print('Error in FFmpeg command, file not processed')
            if exists(new_filename):
                remove(new_filename)
            return None
        return new_filename

class RemoveAudio(FFMpegCommand):
    def __init__(self, command, ffmpeg_exe,options:dict=None):
        super().__init__(command, ffmpeg_exe,options)
        self.allowed_filetypes = ['flv','mp4','mkv','mov']
        self.ffmpeg_command += '-c copy -copyts -an "{2}" -y'

    def run(self, file, **kwargs):
        if not self.check_file(file):return None
        new_filename = join(split(file)[0], ('noaudio_'+split(file)[1]))
        full_command = self.ffmpeg_command.format(
            self.ffmpeg_exe, file, new_filename)+(f' -threads {self.options["threads"]}')
        print(f'Processing file "{file}"...')
        if self.options['debug']: print(f'Running "{full_command}"')
        retcode=call(
            full_command, stdout=DEVNULL if not self.options['debug'] else None, stderr=DEVNULL if not self.options['debug'] else None,shell=True)
        if retcode!=0:
            print('Error in FFmpeg command, file not processed')
            if exists(new_filename):
                remove(new_filename)
            return None
        return new_filename



commands = {"FLV to MP4": FLVtoMP4, "Compress to Size": CompressToSize,"Compress CRF":CompressCRF,'Remove Audio':RemoveAudio}
