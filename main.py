import parse_youtube_video as pv
import os


def test_get_image_with_subtitle_by_url(url, caption_lang='en', silent=False):
    pv.get_images_from_url(url, folder=os.path.join(os.getcwd(), "fps_test"),
                           name="fps", max_images=1000, delay=1,
                           file_name_subtitle=True, subtitle_lang=caption_lang, silent=silent)


if __name__ == '__main__':
    # test_get_image_with_subtitle_by_url("https://youtu.be/pJJI7cP8aNo")
    # test_get_image_with_subtitle_by_url("https://youtu.be/8aR77s9RLck", caption_lang='en', silent=True)
    # test_parse_video()
    print(
        pv.get_dataset_by_request(
            requests=['computer vision'],
            count=2,
            delay=1 / 30,
            max_images=100,
        )
    )
    pass
