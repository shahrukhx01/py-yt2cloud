from youtube_dl import YoutubeDL
import sys
import os
import subprocess

prefix = 'seek_'
if __name__ == '__main__':
    if len(sys.argv) > 1:
        ydl_opts = {
        'outtmpl': "{}%(uploader)s-%(title)s-%(id)s.%(ext)s".format(prefix),
        'getfilename': True,
        'audioquality':1
        }
        ydl = YoutubeDL(ydl_opts)
        ydl.download(sys.argv[1:])


    else:
        print("Enter list of urls to download")
        exit(0)
