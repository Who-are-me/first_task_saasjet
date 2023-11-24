import parse_youtube_video as pv


if __name__ == '__main__':
    print(
        pv.get_dataset_by_request(
            requests=['memes'],
            count=1,
            delay=1,
            max_images=100,
        )
    )
