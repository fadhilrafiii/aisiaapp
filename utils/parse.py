import re


def parse_s3_path(url):
    return re.sub(" ", "+", url)


def get_s3_file_endpoint(path):
    splitted_path = path.split(".com/")

    return splitted_path[1]
