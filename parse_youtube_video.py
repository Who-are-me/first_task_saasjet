import sys
import time

import get_url
import cv2
import os
import json
import requests
import re


from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


# support global values
csv_structure_of_main_dataset = ("item,path_to_video,path_to_folder_with_images,youtube_video_id,url,"
                                 "title,views,create_date,description,likes,dislikes,rating,deleted,tags,"
                                 "channel_name,channel_id,path_to_caption,path_screen_caption_table,"
                                 "caption_in_frame_json,fps,duration\n")
csv_structure_of_caption_table = "path_to_video,path_to_screen,caption\n"

prefix_caption = "CAPTION_"
prefix_screen_caption_table = "SCREEN_CAPTION_TABLE_"
prefix_to_main_dataset = "DATASET_"

# chrome options
# service = Service(executable_path=r'/usr/bin/google-chrome')
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
# temporal web driver
tmp_driver = webdriver.Chrome(
    # service=service,
    options=chrome_options)


# FIXME check if exist subtitle and lang
def get_subtitle(video_id, lang="en", debug=False):
    if debug:
        print(f"DEBUG: Download subtitle in video_id {video_id}")

    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        o_transcript = transcripts.find_transcript(language_codes=[lang, 'en'])

        if o_transcript.language_code == lang:
            return YouTubeTranscriptApi.get_transcript(video_id, [lang])
        else:
            return ""
    except Exception as e:
        print(f"ERROR IN get_subtitle(), exception {e}\n OR video dont have '{lang}' language!")

    return ""


def delete_file_extension(file):
    return file.split('.', 1)[0]


# FIXME work with youtube shorts
# TODO check tags, description
def get_youtube_data_by_url(url: str):
    print(f"DEBUG: get_youtube_data_by_url({url})")

    if url is None:
        return None

    tmp_driver.get(url)
    tmp_driver.implicitly_wait(15)

    title = str(tmp_driver.find_element(By.XPATH, '//*[@id="title"]/h1/yt-formatted-string').text)
    # click on expand description
    tmp_driver.find_element(By.XPATH, '//*[@id="expand"]').click()

    description = str(tmp_driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[4]/div[1]/div/ytd-text-inline-expander/yt-attributed-string').text)
    print("DESCRIPTION: " + description)
    channel_name = tmp_driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[1]/ytd-video-owner-renderer/div[1]/ytd-channel-name/div/div/yt-formatted-string/a').text
    channel_id = tmp_driver.find_element(By.XPATH, '/html/body/ytd-app/div[1]/ytd-page-manager/ytd-watch-flexy/div[5]/div[1]/div/div[2]/ytd-watch-metadata/div/div[2]/div[1]/ytd-video-owner-renderer/div[1]/ytd-channel-name/div/div/yt-formatted-string/a').get_attribute('href')
    request_likes = requests.get(f'https://returnyoutubedislikeapi.com/votes?videoId={get_youtube_id_by_url(url)}').json()

    views = str(request_likes['viewCount'])
    create_date = str(request_likes['dateCreated'])
    likes = str(request_likes['likes'])
    dislikes = str(request_likes['dislikes'])
    rating = str(request_likes['rating'])
    deleted = str(request_likes['deleted'])

    # FIXME => don't correct work '#jujutsukaisen#bocchitherock'
    tags = [ t for t in description.split() if t.startswith('s') ]
    print("CHANNEL_ID: " + str(channel_id))
    channel_id = channel_id.split("@",1)[1]
    print("CHANNEL_ID: " + str(channel_id))
    print("TAGS LIST: " + str(tags))
    tags = ' '.join(tags)
    print("TAGS: " + tags)

    return title, views, create_date, description, likes, dislikes, rating, deleted, tags, channel_name, channel_id


def get_subtitle_in_time(subtitle: list, time: int):
    if subtitle is None:
        return None

    if len(subtitle) <= 0:
        return None

    result = ""

    for it in range(len(subtitle)):
        if (subtitle[it].get('start') < time) and (subtitle[it].get('start') + subtitle[it].get('duration') > time):
            result = subtitle[it].get('text')
            break

    return result


def get_youtube_id_by_url(string: str):
    if string is None:
        return None

    result = string.split("?t=", 0)[0]
    result = result.split("&pp=", 1)[0]
    result = result.split("&list=", 1)[0][-11:]

    return result

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


# TODO test me
def max_label(folder):
    biggest_label = 0

    while True:
        if os.path.exists(os.path.join(folder, str(biggest_label + 1) + "_file.jpg")):
            biggest_label += 1
        else:
            break

    return biggest_label


def get_images_from_video(video, folder_of_images=None, folder=None, delay=30,
                          name="file", max_images=20, debug=False, captions=None):
    screenshot = cv2.VideoCapture(video)
    fps = screenshot.get(5)
    fps = fps if fps != 0 else 30

    if debug:
        print(f"FPS: {fps}")

    duration = int(screenshot.get(cv2.CAP_PROP_FRAME_COUNT)) / fps
    count = 0
    num_images = 0
    caption_in_frame = dict()

    if debug:
        print(f"----get_image_from_video({video}, {folder_of_images}, {folder}, {delay}, "
              f"{name}, {max_images}, {debug}, {captions})----")

    if not os.path.exists(folder):
        os.makedirs(folder)

    if folder_of_images is not None and not os.path.exists(os.path.join(folder, folder_of_images)):
        os.makedirs(os.path.join(folder, folder_of_images))

    label = max_label(folder_of_images)
    success = True
    fps = int(screenshot.get(5))

    while success and num_images < max_images:
        success, image = screenshot.read()
        num_images += 1
        label += 1
        file_name = str(label) + '_' + name + ".jpg"

        if folder_of_images is not None:
            path = os.path.join(os.path.join(folder, folder_of_images), file_name)
        else:
            path = os.path.join(folder, file_name)

        try:
            cv2.imwrite(path, image)

            if cv2.imread(path) is None:
                os.remove(path)
            else:
                if debug:
                    print(f'Image successfully written at {path}')
                caption_in_frame[file_name] = get_subtitle_in_time(captions, delay * num_images - delay)
        except Exception as e:
            print(f"Image is NOT written at {path}. \nOr End of video Exception {e}")

        count += delay * fps
        screenshot.set(1, count)

    # screenshot.getBackendName(),
    return caption_in_frame, fps, duration


def get_images_from_url(url, folder=None, delay=1, name="file", max_images=20,
                        caption_language="en", debug=False):
    if url is None:
        print("ERROR: url is None, skip parse", sys.stderr)
        return None

    if debug:
        print(f"----get_images_from_url({url}, {folder}, {delay}, {name}, "
              f"{max_images}, {caption_language}, {debug})----")

    path_to_video = download_video_by_url(url, path=folder)
    path_to_folder_with_images = os.path.join(
        folder,
        # gets title of video
        "IMAGES_" + delete_file_extension(path_to_video[::-1].split('/', 1)[0][::-1])
    )
    # dont_used,
    caption_in_frame, fps, duration = get_images_from_video(path_to_video,
                                                        folder_of_images=path_to_folder_with_images,
                                                        folder=folder,
                                                        delay=delay,
                                                        name=name,
                                                        max_images=max_images,
                                                        debug=debug,
                                                        captions=get_subtitle(get_youtube_id_by_url(url), lang=caption_language))

    return path_to_video, path_to_folder_with_images, caption_in_frame, fps, duration



# TODO implement this function of analyse video to csv string
# TODO skip age restricted
# FIXME check is None
def get_analyse_video(url: str, item:int = 1, folder=None, save_caption=True, save_screen_caption_table=True,
                      save_json_caption_in_time=True, name_of_images='file', max_images:int = 100,
                      delay: int = 1):
    if url is None:
        return None

    title, views, create_date, description, likes, dislikes, rating, deleted, tags, channel_name, channel_id = get_youtube_data_by_url(url)

    path_to_video, path_to_folder_with_image, caption_in_frame, fps, duration = get_images_from_url(
        url=url,
        name=name_of_images,
        max_images=max_images,
        folder=folder,
        delay=delay,
        debug=True)
    youtube_video_id = get_youtube_id_by_url(url)

    # save caption as file
    if save_caption:
        path_to_caption = os.path.join(folder, prefix_caption + title + ".txt")

        with open(path_to_caption, 'w') as file:
            #          list to str separate of ' '
            file.write(' '.join(str(line) for line in get_subtitle(get_youtube_id_by_url(url))))
            file.close()
    else:
        path_to_caption = "None"

    # save screen caption table
    if save_screen_caption_table:
        path_screen_caption_table = os.path.join(folder, prefix_screen_caption_table + title + ".csv")

        with open(path_screen_caption_table, 'w') as file:
            file.write(csv_structure_of_caption_table)

            for key, value in caption_in_frame.items():
                file.write(f"{path_to_video},{path_to_folder_with_image}/{key},{value}\n")

            file.close()
    else:
        path_screen_caption_table = "None"


    return ','.join([
        str(item),
        str(path_to_video),
        path_to_folder_with_image,
        youtube_video_id,
        url,
        title,
        views,
        create_date,
        '"' + str(description).replace('\n', ' ') + '"',
        likes,
        dislikes,
        rating,
        deleted,
        tags,
        channel_name,
        channel_id,
        path_to_caption,
        path_screen_caption_table,
        '"' + str(json.dumps(caption_in_frame)) if save_json_caption_in_time else str("None") + '"',
        str(fps),
        str(duration)
    ]) + "\n"


def get_dataset_by_request(request_list: list, count: int = 10, name_of_dataset="DATASET.csv",
                           folder=None, max_images=100, delay=1, save_caption=True,
                           save_screen_caption_table=True, save_json_caption_in_time=True):
    for request in request_list:
        urls = get_url.get_urls_of_youtube_request([request], count=count, debug=True)
        file = os.path.join(name_of_dataset)

        if not folder:
            folder = os.path.join(prefix_to_main_dataset + request)

        try:
            if not os.path.exists(os.path.join(os.getcwd(), folder)):
                os.makedirs(os.path.join(os.getcwd(), folder))

            if not os.path.exists(os.path.join(os.getcwd(), folder, name_of_dataset)):
                file = open(os.path.join(folder, name_of_dataset), 'a+')
                file.write(csv_structure_of_main_dataset)
            else:
                file = open(os.path.join(folder, name_of_dataset), 'a+')
        except Exception as e:
            print(f"Catch exception {e}")
        finally:
            item = 1

            for url in urls:
                if url is not None:
                    analyse_result = get_analyse_video(
                        item=item,
                        url=url,
                        folder=os.path.join(os.getcwd(), folder),
                        max_images=max_images,
                        delay=delay,
                        save_caption=save_caption,
                        save_screen_caption_table=save_screen_caption_table,
                        save_json_caption_in_time=save_json_caption_in_time,
                    )
                    file.write(analyse_result)
                    item += 1
                else:
                    print("WARNING: skip, because is url None!", sys.stderr)

    return True


############################
# some code for testing file
############################

# st = get_subtitle("TrKMA7SYXfg", 'en', debug=True)
# print(st)
# print(st[0].get('start'))
# print(st[0])
# print(type(st[1]))
# print(st[0:3])
# print(type(st))
# test one screenshot by one fps
# print(get_url.get_urls_of_youtube_channel("@uahuy"))
# extract_images_from_word("@uahuy", do_download=False)
# print(YouTubeTranscriptApi.get_transcript("TrKMA7SYXfg", languages=['ru']))
# print(get_youtube_title_by_url("https://www.youtube.com/watch?v=DORZA_S7f9w"))
# print(get_youtube_title_by_url("https://youtu.be/b6wAYwOKgRY"))
# print(get_youtube_title_by_url("https://youtu.be/DORZA_S7f9w"))
# print(max_label(os.path.join(os.getcwd(), 'DATASET_israil shorts', 'IMAGES_Video of Israel’s Iron Dome missile malfunctioning  AJ shorts')))
# get_images_from_video(os.path.join(os.getcwd(), 'DATASET_israil shorts', 'Video of Israel’s Iron Dome missile malfunctioning  AJ shorts.mp4'),
#                       folder_of_images=os.path.join(os.getcwd(), 'DATASET_israil shorts', 'IMAGES_Video of Israel’s Iron Dome missile malfunctioning  AJ shorts'),
#                       folder=os.path.join(os.getcwd(), 'DATASET_israil shorts'),
#                       debug=True,
#                       delay=1
#                       )
# get_youtube_data_by_url('https://www.youtube.com/watch?v=UVjzNRwo9Qc')
