import get_url
import cv2
import os
import glob
import time
import json


from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


# support global values
csv_structure = (",path_to_video,path_to_folder_with_images,"
                 "youtube_video_id,url,title,description,path_to_caption,caption_in_frame\n")


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


# FIXME dont work
def get_youtube_title_by_url(url: str):
    if url is None:
        return None

    driver = webdriver.Chrome()
    driver.get("https://www.youtube.com/")

    time.sleep(2)

    search_box = driver.find_element("name", "search_query")
    # search_box.send_keys(url + Keys.RETURN)
    search_box.send_keys(url)
    search_box.send_keys(Keys.RETURN)

    time.sleep(2)

    video_link = driver.find_element(By.CSS_SELECTOR, "#video-title")

    title = video_link.get_attribute("title")

    return title


def get_subtitle_in_time(subtitle: list, time: int):
    if len(subtitle) <= 0:
        return None

    result = ""

    for it in range(len(subtitle)):
        if subtitle[it].get('start') < time and subtitle[it].get('start') + subtitle[it].get('duration') > time:
            result = subtitle[it].get('text')
            break

    return result


# TODO implement me! get descriptions
def get_description(url: str):
    return "Template description"


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


def max_label(folder):
    path_pattern = os.path.join(folder, "*.jpg")
    existing_files = glob.glob(path_pattern)
    biggest_label = 0

    while True:
        if os.path.exists(os.path.join(folder, str(biggest_label + 1) + "_file.jpg")):
            biggest_label += 1
        else:
            break

    return biggest_label


def get_images_from_video(video, folder_of_images=None, folder=None, delay=30,
                          name="file", max_images=20, silent=False, captions=None):
    screenshot = cv2.VideoCapture(video)
    count = 0
    num_images = 0
    caption_in_frame = dict()

    if not silent:
        print(f"Video {video}")

    if not os.path.exists(folder):
        os.makedirs(folder)

    if folder_of_images is not None and not os.path.exists(os.path.join(folder, folder_of_images)):
        os.makedirs(os.path.join(folder, folder_of_images))

    label = max_label(folder_of_images)
    success = True
    fps = int(screenshot.get(cv2.CAP_PROP_FPS))

    while success and num_images < max_images:
        success, image = screenshot.read()
        num_images += 1
        label += 1
        file_name = str(label) + '_' + name + ".jpg"
        caption_in_frame[file_name] = get_subtitle_in_time(captions, delay * num_images - delay)

        if folder_of_images is not None:
            path = os.path.join(os.path.join(folder, folder_of_images), file_name)
        else:
            path = os.path.join(folder, file_name)

        try:
            cv2.imwrite(path, image)
            if cv2.imread(path) is None:
                os.remove(path)
            else:
                if not silent:
                    print(f'Image successfully written at {path}')
        except Exception as e:
            print(f"Image is NOT written at {path}, or Exception {e}")

        count += delay * fps
        screenshot.set(1, count)

    return screenshot.getBackendName(), caption_in_frame


def get_images_from_url(url, folder=None, delay=1, name="file", max_images=20,
                        caption_language="en", silent=False):
    captions = None

    if url is None:
        print("ERROR: url is None, skip parse")
        return None

    if not silent:
        print(f"Url {url}")
        print(f"Start of get image from video")

    path_to_video = download_video_by_url(url, path=folder)
    path_to_folder_with_images = os.path.join(
        folder,
        # gets title of video
        "IMAGES_" + delete_file_extension(path_to_video[::-1].split('/', 1)[0][::-1])
    )

    dont_used, caption_in_frame = get_images_from_video(path_to_video,
                          folder_of_images=path_to_folder_with_images,
                          folder=folder,
                          delay=delay,
                          name=name,
                          max_images=max_images,
                          silent=silent,
                          captions=get_subtitle(get_youtube_id_by_url(url), lang=caption_language))

    if not silent:
        print(f"End of get image from url {url}")

    return path_to_video, path_to_folder_with_images, caption_in_frame



# TODO implement this function of analyse video to csv string
# TODO skip age restricted
# FIXME check is None
def get_analyse_video(url: str, folder=None,
                      name_of_images='file', max_images:int = 100, delay: int = 1):
    if url is None:
        return None

    result = ','
    path_to_video, path_to_folder_with_image, caption_in_frame = get_images_from_url(
        url=url,
        name=name_of_images,
        max_images=max_images,
        folder=folder,
        delay=delay,
        silent=False)
    youtube_video_id = get_youtube_id_by_url(url)
    title = delete_file_extension(path_to_video[::-1].split('/', 1)[0][::-1])
    description = get_description(url)

    # TODO save caption as file ?
    path_to_caption = os.path.join(folder, "CAPTION_" + title + ".txt")

    with open(path_to_caption, 'w') as file:
        #          list to str separate of ' '
        file.write(' '.join(str(line) for line in get_subtitle(get_youtube_id_by_url(url))))
        file.close()

    return result.join([
        path_to_video,
        path_to_folder_with_image,
        youtube_video_id,
        url,
        title,
        description,
        path_to_caption,
        json.dumps(caption_in_frame)
    ]) + "\n"


def get_dataset_by_request(requests: list, count: int = 10,
                           name_of_dataset="DATASET.csv", folder=None, max_images=100, delay=1):
    prefix_to_path = "DATASET_"

    for request in requests:
        urls = get_url.get_urls_of_youtube_request([request], count=count, debug=True)
        file = os.path.join(name_of_dataset)

        if not folder:
            folder = os.path.join(prefix_to_path + request)

        try:
            if not os.path.exists(os.path.join(os.getcwd(), folder)):
                os.makedirs(os.path.join(os.getcwd(), folder))

            if not os.path.exists(os.path.join(os.getcwd(), folder, name_of_dataset)):
                file = open(os.path.join(folder, name_of_dataset), 'a+')
                file.write(csv_structure)
            else:
                file = open(os.path.join(folder, name_of_dataset), 'a+')
        except Exception as e:
            print(f"Catch exception {e}")
        finally:
            for url in urls:
                print("URL -> " + str(url))
                if url is not None:
                    analyse_result = get_analyse_video(
                        url=url,
                        folder=os.path.join(os.getcwd(), folder),
                        max_images=max_images,
                        delay=delay)
                    file.write(analyse_result)
                else:
                    print("Warning: skip, because is url None!")


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
# test one creenshot by one fps
# print(get_url.get_urls_of_youtube_channel("@uahuy"))
# extract_images_from_word("@uahuy", do_download=False)
# print(YouTubeTranscriptApi.get_transcript("TrKMA7SYXfg", languages=['ru']))
# print(get_youtube_title_by_url("https://www.youtube.com/watch?v=DORZA_S7f9w"))
# print(get_youtube_title_by_url("https://youtu.be/b6wAYwOKgRY"))
# print(get_youtube_title_by_url("https://youtu.be/DORZA_S7f9w"))
