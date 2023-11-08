import parse_youtube_video as pv
import os


def test_parse_video():
    pv.download_video_by_url("https://youtu.be/56zKeunsNvA")

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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test_parse_video()
