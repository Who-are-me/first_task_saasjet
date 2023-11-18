import get_url
from youtube_transcript_api import YouTubeTranscriptApi
# import urllib
# from bs4 import BeautifulSoup
from pytube import YouTube
import cv2
import os
import glob
import pandas as pd


def get_subtitle(video_id, lang="en", debug=False):
    if debug:
        print(f"Download subtitle in video_id {video_id}")

    return YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])


# TODO add get subtitles in time
def get_subtitle_in_time(subtitle: list, time: int):
    if len(subtitle) <= 0:
        return None

    result = ""

    for it in range(len(subtitle)):
        if subtitle[it].get('start') < time and subtitle[it].get('start') + subtitle[it].get('duration') > time:
            result = subtitle[it].get('text')
            break

    return result


# TODO implement me! get desctiptions
def get_description(url: str):
    return "Template description"


# FIXME dont work correct -> https://www.youtube.com/watch?v=DBzGJ1V5L34&pp=ygUEY2F0cw%3D%3
def get_youtube_id_by_url(string: str):
    return string.split("?t=", 0)[0][-11:]


def download_video_by_url(url, path=None, max_duration=10):
    file_name = "undefined_file"

    try:
        yt = YouTube(url)
        duration = yt.length
        if duration < max_duration * 60 * 1000:
            yt = yt.streams.filter(file_extension='mp4').first()
            out_file = yt.download(path)
            file_name = out_file.split("\\")[-1]
            print(f"Downloaded {file_name} correctly!")
        else:
            print(f"Video {url} too long")
    except Exception as exc:
        print(f"Download of {url} did not work because of {exc}...")

    return file_name


def max_label(name, folder):
    '''Look at a folder and check the files with pattern "name_###.jpg" to extract the
    largest label present.'''

    path_pattern = os.path.join(folder, name + "_*.jpg")
    existing_files = glob.glob(path_pattern)
    if not existing_files:
        biggest_label = 0
    else:
        existing_labels = map(lambda s: int(s.split('_')[-1].split('.')[0]), existing_files)
        biggest_label = max(existing_labels)
    return biggest_label


def get_images_from_video(video, folder=None, delay=30, name="file", max_images=20, silent=False, captions=None):
    vidcap = cv2.VideoCapture(video)
    count = 0
    num_images = 0

    if not silent:
        print(f"Video {video}")

    if not folder:
        folder = os.getcwd()

    if not os.path.exists(folder):
        os.makedirs(folder)

    label = max_label(name, folder)
    success = True
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))

    while success and num_images < max_images:
        success, image = vidcap.read()
        num_images += 1
        label += 1
        file_name = str(label) + "_|" + (name if captions is None else get_subtitle_in_time(captions, delay * num_images - delay)) + "|" + ".jpg"
        path = os.path.join(folder, file_name)

        try:
            cv2.imwrite(path, image)
            if cv2.imread(path) is None:
                os.remove(path)
            else:
                if not silent:
                    print(f'Image successfully written at {path}')
        except:
            print(f"Image is NOT written at {path}")

        count += delay * fps
        vidcap.set(1, count)

    return vidcap.getBackendName()


def get_images_from_url(url, folder=None, delay=30, name="file", max_images=20,
                        file_name_subtitle=False, subtitle_lang="en", silent=False):
    captions = None

    if not silent:
        print(f"Url {url}")

    if file_name_subtitle:
        captions = get_subtitle(get_youtube_id_by_url(url), subtitle_lang)

    if not silent:
        print(f"Start of get image from video")
    file_name = download_video_by_url(url)
    get_images_from_video(file_name,
                          folder=folder,
                          delay=delay,
                          name=name,
                          max_images=max_images,
                          silent=silent,
                          captions=captions)

    if not silent:
        print(f"End of get image from url {url}")

    return file_name


def extract_images_from_word(text="", delete_video=False, image_delay=30,
                             num_urls=10, max_images=20, name="extraction_images", max_duration=15, silent=False, do_download=True):

    if not os.path.exists(name):
        os.mkdir(name)

    # urls = get_urls(text, num_urls)
    urls = get_url.get_urls_of_youtube_channel(text)

    if do_download:
        for url in urls:
            download_video_by_url(url, max_duration=max_duration)

    for i, video in enumerate(glob.glob("*.mp4")):
        get_images_from_video(video, folder=name, delay=image_delay, name=name, max_images=max_images, silent=silent)
        if delete_video:
            os.remove(video)

    pass


# TODO implement this function of analyse video to csv string
# TODO skip age restricted
def get_analyse_video(url: str, folder=None, max_images=100, delay=1):
    result = ','
    file_name = get_images_from_url(url=url, max_images=max_images, folder=folder)
    youtube_id = get_youtube_id_by_url(url)
    # FIXME delete file extended
    title = file_name[::-1].split('/', 1)[0][::-1]
    description = get_description(url)

    return result.join([file_name, youtube_id, url, title, description]) + "\n"


# TODO implement this function of get dataset
def get_dataset_by_request(request: str, count: int = 10, file_name="dataset.csv", folder=None, max_images=100, delay=1):
    urls = get_url.get_urls_of_youtube_request([request], count=count)
    file = None
    csv_structure = ",file_name,yid,url,title,description\n"

    # open or create file
    try:
        if not os.path.exists(os.path.join(os.getcwd(), file_name)):
            file = open(file_name, 'a+')
            file.write(csv_structure)
        else:
            file = open(file_name, 'a+')
    except Exception as e:
        print(f"Error {e}")
    finally:
        for url in urls:
            file.write(get_analyse_video(url=url, folder=folder, max_images=max_images, delay=delay))

    return True


############################
# some code for testing file
############################
# st = get_subtitle("TrKMA7SYXfg", 'ru', debug=False)
# print(st)
# print(st[0].get('start'))
# print(st[0])
# print(type(st[1]))
# print(st[0:3])
# print(type(st))
# test one creenshot by one fps
# print(get_url.get_urls_of_youtube_channel("@uahuy"))
# extract_images_from_word("@uahuy", do_download=False)
# print(YouTubeTranscriptApi.get_transcript("TrKMA7SYXfg", languages=['ru']))