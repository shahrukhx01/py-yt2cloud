from googlesearch import search
import shutil
import re
from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template
from flask import request
import eyed3
import tldextract
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

app = Flask(__name__)

# to search
def init():
    query = "{} {} mp3"
    sources = ["pendujatt","djpunjab","mr-jatt","djyoungster","djjohal"]
    return (sources,query)

def google_search(query,sources,text):
    results=[]
    for i,v in enumerate(sources):
        q = query.format(text,v)

        for j in search(q, tld="com", num=2, stop=2, pause=2):
            results.append(j)
    return results


def download_mp3(url,text):
    from os import system
    system('wget "{}" -O {}.mp3'.format(url,text))

"""
saves audio track to Google drive
"""
gauth = None
drive= None
@app.route('/auth', methods=['GET'])
def auth():

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
    return "credentials loaded."


def authorize_drive():
    print('connecting to Google drive...')
    gauth = GoogleAuth()
    gauth.DEFAULT_SETTINGS['client_config_file'] = "client_secrets.json"
    gauth.LoadCredentialsFile("mycreds.txt")
    return GoogleDrive(gauth)
    print('connected to GDrive!')


def save_to_gDrive(dest_file):
    print('uploading file to drive...')
    drive = authorize_drive()
    track = drive.CreateFile({'parents': [{'id': '1L-CZ9qzt28CszD9S5i2Pws4SXXJRQaE7'}]})
    track.SetContentFile(dest_file)
    track.Upload()
    print('file has been uploaded to drive!')
    clean_up(dest_file)

"""
removes files from disk
"""
def clean_up(file_name):
    os.remove(file_name)
    print("{} Removed!".format(file_name))

def update_metadata(title):
    try:
        audiofile = eyed3.load('{}.mp3'.format(title))
        artist = title.split(' - ')[1]
        audiofile.tag.title= audiofile.tag._getTitle().split(' (')[0]
        audiofile.tag._setArtist(artist)
        audiofile.tag.album= audiofile.tag._getAlbum().split(' (')[0]
        audiofile.tag.save()
    except:
        pass

@app.route('/yt2cloud', methods=['POST'])
def yt2cloud():
    content = request.get_json(silent=True)
    print(content)
    text= content['text']
    dllink= None
    print('Initializing...')
    sources,query= init()
    print('searching on google...')
    links= google_search(query,sources,text)
    print('generating download link...')
    dllink= parse_lnks(links,text)
    print('downloading song...')
    download_mp3(dllink,re.escape(text))
    print('updating metadata...')
    update_metadata(text)
    print('initializing gdrive...')
    save_to_gDrive('{}.mp3'.format(text))
    return 'your song ({}) has been uploaded to Google drive!'.format(dllink)

@app.route('/')
def webprint():
    return render_template('index.html')

def parse_lnks(links,text):
    dllink= None
    for i,v in enumerate(links):
        dllink= generate_dllink(text,v)
        if dllink!= None:
            break
    return dllink


def generate_dllink(text,url):
    protocol = url.split(':')[0]
    url_parsed= tldextract.extract(url)
    base= "{}://{}.{}/".format(protocol,url_parsed.domain,url_parsed.suffix)
    html_content = requests.get(url).text

    # Parse the html content
    soup = BeautifulSoup(html_content, "lxml")
    dllink= None
    for a in soup.find_all('a', href= True): #text=re.compile('320 Kbps', re.IGNORECASE)
        try:
            if (('/320/' in a['href']) or '/320k-dtlch/' in a['href']) and '.mp3' in a['href']: #re.search("*.\/320\/.*", a['href']):
                print(a['href'])
                if a['href'][:4] !='http':
                    dllink= base+a['href']
                else:
                    dllink= a['href']
        except:
            continue
    print(url,dllink)
    return dllink



if __name__ == '__main__':
    app.run()
