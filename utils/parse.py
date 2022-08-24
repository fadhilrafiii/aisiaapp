import re


def parse_s3_path(url):
    return re.sub(" ", "+", url)


def get_s3_file_endpoint(path):
    splitted_path = path.split(".com/")

    return splitted_path[1]


def parse_annotations(annotations):
    for annotation in annotations:
        annotation["xmin"] = annotation['box'][0]
        annotation["ymin"] = annotation['box'][1]
        annotation["xmax"] = annotation['box'][2]
        annotation["ymax"] = annotation['box'][3]

    return annotations
