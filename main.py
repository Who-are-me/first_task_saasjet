import get_url
import parse_youtube_video as pv

# FIXME of project
# 1 wrap comma in csv files
# TODO of project
# 1 add scrape items
# 2 rewrite file structure
# 3 rewrite to OOP
# 4 add SQLite3


if __name__ == '__main__':
    print(
        pv.get_dataset_by_request(
            request_list=['funny cats short video'],
            count=2,
            delay=1,
            max_images=100,
            save_caption=True,
            save_screen_caption_table=True,
            save_json_caption_in_time=True,
        )
    )
