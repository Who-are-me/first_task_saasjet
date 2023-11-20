import get_url
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import cv2
import os
import glob


# support global values
csv_structure = ",file_name,folder_with_images,yid,url,title,description,caption\n"


# FIXME check if exist subtitle and lang
def get_subtitle(video_id, lang="en", debug=False):
    if debug:
        print(f"Download subtitle in video_id {video_id}")

    # if len(YouTubeTranscriptApi.list_transcripts(video_id)) == 0:
    #     return "This video dont have caption"

    return "test caption"
    # return YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])


def delete_file_extension(file):
    return file.split('.', 1)[0]


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


def max_label(name, folder):
    path_pattern = os.path.join(folder, name + "_*.jpg")
    existing_files = glob.glob(path_pattern)
    if not existing_files:
        biggest_label = 0
    else:
        existing_labels = map(lambda s: int(s.split('_')[-1].split('.')[0]), existing_files)
        biggest_label = max(existing_labels)
    return biggest_label


def get_images_from_video(video, folder_of_images=None, folder=None, delay=30, name="file", max_images=20, silent=False, captions=None):
    vidcap = cv2.VideoCapture(video)
    count = 0
    num_images = 0

    if not silent:
        print(f"Video {video}")

    if not os.path.exists(folder):
        os.makedirs(folder)

    if folder_of_images is not None and not os.path.exists(os.path.join(folder, folder_of_images)):
        os.makedirs(os.path.join(folder, folder_of_images))

    label = max_label(name, folder)
    success = True
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))

    while success and num_images < max_images:
        success, image = vidcap.read()
        num_images += 1
        label += 1

        if captions is not None:
            file_name = str(label) + "_|" + (name if captions is None else get_subtitle_in_time(captions, delay * num_images - delay)) + "|" + ".jpg"
        else:
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
                if not silent:
                    print(f'Image successfully written at {path}')
        except Exception as e:
            print(f"Image is NOT written at {path}, or Exception {e}")

        count += delay * fps
        vidcap.set(1, count)

    return vidcap.getBackendName()


def get_images_from_url(url, folder_of_images=None, folder=None, delay=30, name="file", max_images=20,
                        file_name_subtitle=False, subtitle_lang="en", silent=False):
    captions = None

    if url is None:
        print("ERROR: url is None, skip parse")
        return None

    if not silent:
        print(f"Url {url}")

    if file_name_subtitle:
        captions = get_subtitle(get_youtube_id_by_url(url), subtitle_lang)

    if not silent:
        print(f"Start of get image from video")
    file_name = download_video_by_url(url, path=folder)
    get_images_from_video(file_name,
                          folder_of_images=folder_of_images,
                          folder=folder,
                          delay=delay,
                          name=name,
                          max_images=max_images,
                          silent=silent,
                          captions=captions)

    if not silent:
        print(f"End of get image from url {url}")

    return file_name



# TODO implement this function of analyse video to csv string
# TODO skip age restricted
# FIXME check is None
def get_analyse_video(url: str, folder_of_images=None, folder=None,
                      name_of_images='file', max_images:int = 100, delay: int = 1):
    if url is None:
        return None

    result = ','
    file_name = get_images_from_url(
        url=url,
        folder_of_images=folder_of_images,
        name=name_of_images,
        max_images=max_images,
        folder=folder,
        delay=delay,
        silent=False)
    folder_with_images = folder_of_images
    youtube_id = get_youtube_id_by_url(url)
    title = delete_file_extension(file_name[::-1].split('/', 1)[0][::-1])
    description = get_description(url)
    caption = get_subtitle(get_youtube_id_by_url(url))

    # TODO save caption as file ?
    # path_to_caption = os.path.join(folder, "CAPTION_" + title + ".txt")

    # with open(path_to_caption, 'w') as file:
    #     file.write(caption)
    #     file.close()

    return result.join([
        file_name,
        folder_with_images,
        youtube_id,
        url,
        title,
        description,
        caption
    ]) + "\n"


def get_dataset_by_request(requests: list, count: int = 10, name_of_dataset="dataset.csv", folder=None, max_images=100, delay=1):
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
                analyse_result = get_analyse_video(
                    url=url,
                    folder_of_images=os.path.join(os.getcwd(), folder, request + '_images'),
                    folder=os.path.join(os.getcwd(), folder),
                    max_images=max_images,
                    delay=delay)

                if analyse_result is not None:
                    file.write(analyse_result)
                else:
                    print("Warning: skip, because is url None!")


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