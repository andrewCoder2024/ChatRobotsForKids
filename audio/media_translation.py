# -*- coding: utf-8 -*-

import six
from google.cloud import translate_v2 as translate
import os


# os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/ChatRobotsForKids/key.json"

def translate_text(target, text="hello"):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)
    result = result["translatedText"].replace("&#39;", "'")
    return result


if __name__ == "__main__":
    print(translate_text("en", "你好，今天天气怎么样"))
    print(translate_text("zh-CN", "hello"))
