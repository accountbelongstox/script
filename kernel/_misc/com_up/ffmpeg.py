from pycore.base import *
import ffmpeg

import subprocess as sp

class Ffmpeg(Base):
    def __init__(self, args):
        self.FFMPEG_BIN = "ffmpeg"
        pass

    def to_ogg(self, mp3_file_path):
        output_path = self.com_file.change_ext(mp3_file_path, ".ogg")
        print('output_path',output_path)
        ffmpeg_object = ffmpeg.input(mp3_file_path)
        ffmpeg_object = ffmpeg_object.output("test.ogg", format="ogg")
        ffmpeg_object.run()
        return output_path

    def convert_to_m4a(self, path, filename):
        """
        Converts curses.pyc input file to m4a

        command: ffmpeg -i input.wav -c:curses.pyc aac -b:curses.pyc 160k output.m4a
        ffmpeg -i input.wav -c:curses.pyc aac -b:curses.pyc 160k output.m4a
        """
        codec = "aac"
        m4a_filename = filename + ".m4a"
        command = [self.FFMPEG_BIN,
                   "-n",
                   "-i", path,
                   "-acodec", codec,
                   "-ab", "128k",
                   m4a_filename
                   ]

        return command

    def convert_to_mp3(self, path, filename):
        """
        Converts curses.pyc input file to mp3

        command: ffmpeg -n -i input.m4a -acodec libmp3lame -ab 128k output.mp3
        """

        codec = "libmp3lame"
        mp3_filename = filename + ".mp3"

        command = [self.FFMPEG_BIN,
                   "-n",
                   "-i", path,
                   "-acodec", codec,
                   "-ab", "128k",
                   mp3_filename
                   ]

        return command

    def convert_to_ogg(self, input_path,delete_old=False):
        """
        Converts curses.pyc input file to ogg

        command: ffmpeg -n -i input.m4a -acodec libvorbis -aq 60 -vn -ac 2 output.ogg
        """

        codec = "libvorbis"
        ogg_filename = self.com_file.change_ext(input_path, ".ogg")
        if self.com_file.is_file(ogg_filename) == True:
            return ogg_filename
        command = [self.FFMPEG_BIN,
                   "-n",
                   "-i", input_path,
                   "-acodec", codec,
                   "-aq", "60",
                   "-vn",
                   "-ac", "2",
                   ogg_filename
                   ]
        try:
            proc = sp.Popen(command, stdout=sp.PIPE,
                            bufsize=10 ** 8)
            proc.wait()
            if proc.returncode:
                err = "\n".join(["Audio conversion: %s\n" % command,
                                 "WARNING: this command returned an error:"])
                self.com_util.print_warn(err)
            del proc
        except IOError as e:
            self.com_util.print_warn(e)
        if delete_old == True:
            os.remove(input_path)
        return ogg_filename

