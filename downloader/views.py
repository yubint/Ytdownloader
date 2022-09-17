from distutils.log import error
from http import server
from http.client import HTTPResponse

import os
import shutil

from django.shortcuts import render
from django.http import HttpResponse

import pytube


# creating bunch of variables for paths used
def video_dir():
    return r'C:\Users\Anupam\Django\Video'

def zip_dir():
    return r'C:\Users\Anupam\Django\Playlist'


# Create your views here.

#main home section for videos download
def mainapp(request):
    return render(request,"downloader/mainapp.html")
    
# returns a list of videos in a playlist
def video_list(playlist_link):

    playlist = pytube.contrib.playlist.Playlist(playlist_link)
    # creates an object playlist of the given playlist class in pytube

    video_in_playlist_list = playlist.video_urls
    # gets the list of video urls in the playlist

    return video_in_playlist_list

# returns the name of the playlist with given link
def get_playlist_name(playlist_link):

    playlist = pytube.contrib.playlist.Playlist(playlist_link)
    # creates an object playlist of the given playlist class in pytube

    return playlist.title



# download individual videos from pytube ,return them as
# httpresponse with correct name and delete the file from server
def download(url,return_name:bool = True):

    # creates a Youtube object of the video
    youtube_video = pytube.YouTube(url)

    # if resolution=="720p":
    youtube_stream = youtube_video.streams.get_by_itag(22)
        # Creates a Stream object of the Youtube Object
    # elif resolution=="1080p":
    #     youtube_stream = youtube_video.streams.get_by_itag(137)


    video_name=youtube_stream.default_filename


    file_location=video_dir()

    #downloads the video on the location file_location with the name video_name
    youtube_stream.download(file_location,video_name)

    #read the file  to a variable video_data
    with open(file_location+"/"+video_name,"rb") as server_video:
        video_data=server_video.read()


    response=HttpResponse(video_data, headers={
        'Content-Type':'mp4',
        'Content-Disposition':f'attachment; filename={video_name}'
    })

    #removes  returns the response only when no argument is passed,
    # if any argument is passed it doesn't remove the file
    if return_name==1:
        

        return video_name



# downloads the youtube videos in a playlist given a link
def playlist_downloader(request,playlist_link):

    # trying for the code to run
    try:
        playlist_name=get_playlist_name(playlist_link)

        # creating variables for paths of video and zip file
        video_directory=video_dir()
        zip_directory=zip_dir()

        current_directory_django=os.getcwd()

        os.chdir(zip_directory)

        # creates a list of videos in the playlist using video_list function
        v_list = video_list(playlist_link)

        # downloads each of the video in the v_list
        for video in v_list:
            download(video,0)

        # creates an zip file of all those videos
        shutil.make_archive(f'{playlist_name}','zip',video_directory)

        # opens the zip file and reads it onto a file playlist_zip
        with open(zip_directory+f'/{playlist_name}.zip','rb') as playlist_file:
            playlist_zip=playlist_file.read()

        # remove the zip files and video file from the server

        os.remove(zip_directory+f'/{playlist_name}.zip')

        video_in_server_list=os.listdir(video_directory)

        for video in video_in_server_list:
            os.remove(video_directory+'/'+video)

        os.chdir(current_directory_django)

        response=HttpResponse(playlist_zip,headers={
            'Content-Type':'zip',
            'Content-Disposition':f'attachment ; filename="{playlist_name}.zip"'
        })
        return response

    # KEYERROR is raised when the link cannot be accessed 
    except KeyError:
        error_message='The Given playlist link cannot be accessed'
        solution_list=['Check if the playlist is Private','Check if the link is correct','Check if the playlist Exists']
        solution_dict={
            'error':error_message,
            'solutions':solution_list
        }


        return render(request,'downloader/error.html',solution_dict)


def any_downloader(request):
    link=request.GET.get('url')

    # checking if the link is youtube link or not
    if "youtu" in link:
        #checkig if link is playlist or video
        if "playlist" in link:
            return playlist_downloader(request,link)
        else:

            file_location=video_dir()

            video_name=download(link)

            #read the file  to a variable video_data
            with open(file_location+"/"+video_name,"rb") as server_video:
                video_data=server_video.read()

            os.remove(file_location+"/"+video_name)

            response=HttpResponse(video_data, headers={
            'Content-Type':'video/mp4',
            'Content-Disposition':f'attachment; filename={video_name}'
            })

            return response
    
    # if it's not a youtube link
    else:
        solutions=['Please enter a Youtube Link']
        error_message='Given link is not a youtube link'
        error_dict={
            'error':error_message,
            'solutions':solutions
        }

        return render(request,'downloader/error.html',error_dict)
            