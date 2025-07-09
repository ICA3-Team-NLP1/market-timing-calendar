import io
import os
import json


def load_json_file(filename):
    """
    json 파일 로드 함수
    """
    if os.path.exists(filename):
        with io.open(filename, "r") as json_file:
            data = json.load(json_file)
        return data
    return None
