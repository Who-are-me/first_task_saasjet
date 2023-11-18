import get_url
import parse_youtube_video as pv
import os
import re


def test_parse_video():
    # pv.download_video_by_url("https://youtu.be/56zKeunsNvA")
    pv.download_video_by_url("https://www.youtube.com/watch?v=G6XYsNA_yU8")

    try:
        with open("captions.txt", "w") as file:
            file.write(''.join(str(e) for e in pv.get_subtitle("I3YwaqBqRnY", lang='uk')))
    except Exception as e:
        print(e)

    pv.get_images_from_video("Funny animals - Funny cats and dogs - Funny animal videos 2023🤣.mp4",
                          folder=os.path.join(os.getcwd(), "fps"),
                          name="fps",
                          max_images=30 * 10,
                          delay=1 / 30)


def test_get_image_with_subtitle_by_url(url, caption_lang='en', silent=False):
    pv.get_images_from_url(url, folder=os.path.join(os.getcwd(), "fps_test"),
                           name="fps", max_images=1000, delay=1,
                           file_name_subtitle=True, subtitle_lang=caption_lang, silent=silent)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # test_get_image_with_subtitle_by_url("https://youtu.be/pJJI7cP8aNo")
    # test_get_image_with_subtitle_by_url("https://youtu.be/8aR77s9RLck", caption_lang='en', silent=True)
    # test_parse_video()
    pv.get_dataset_by_request(request='cats', count=3, delay=1)
    # print(f"---> {len(get_url.get_urls_of_youtube_request(['cats'], count=77, debug=True))}")
    pass
