import subprocess
import moviepy.editor as mp
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from flask import Flask
from flask import request

app = Flask(__name__)

prefix = 'seek_'
dest_ext = '.mp3'
src_ext = '.mp4'

"""
fetches video track from Youtube
"""

def get_video(id):
    try:
        stdout = subprocess.check_output("python3 music_bot.py {}".format(id), shell = True)
        logs = stdout.decode("utf-8").split('\n')
        file_name= None
        for index,val in enumerate(logs):
            if id in val and prefix in val:
               file_name = val.split(prefix)[1].split('.mp4')[0]
        return file_name
    except:
        print ("Unexpected error:", sys.exc_info()[0])
        raise
"""
removes files from disk
"""
def clean_up(file_name):
    os.remove(file_name)
    print("{} Removed!".format(file_name))

"""
saves audio track to Google drive
"""

gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)
#gauth.LoadClientConfigFile("client_secret_447233534603-845n7mk8mnc4ht5lv9cbnag9gs7djng8.apps.googleusercontent.com.json")

def save_to_gDrive(dest_file):
    #drive = GoogleDrive(gauth)

    track = drive.CreateFile({'parents': [{'id': '1L-CZ9qzt28CszD9S5i2Pws4SXXJRQaE7'}]})
    track.SetContentFile(dest_file)
    track.Upload()
    print('file has been uploaded to drive.')
    clean_up(dest_file)
    #drive.CreateFile({'id':textfile['id']}).GetContentFile('eng.txt')

"""
Main route
"""
@app.route('/yt2cloud', methods=['GET', 'POST'])
def index():
    content = request.get_json(silent=True)
    id = content['url'].split('v=')[1]
    dest_file = process_video(id)
    save_to_gDrive(dest_file)
    return "Hello, World!"
"""
converts video files to audio.
"""
def process_video(id):

    file_name= get_video(id)
    src_file = "{}{}{}".format(prefix,file_name,src_ext)
    dest_file= "{}{}".format(file_name,dest_ext)

    clip = mp.VideoFileClip(src_file)
    clean_up(src_file)
    clip.audio.write_audiofile(dest_file)
    print('audio file written to disk')
    return dest_file

    """
    do some more code here...
    """

    clean_up(dest_file)


"""
Main method
"""

if __name__ == '__main__':
    app.run()