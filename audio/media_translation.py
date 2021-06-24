from google.cloud import translate


def translate_text(source, target, text="hello", project_id="ttsproject-1622791296381"):
    """Translating Text."""

    client = translate.TranslationServiceClient()

    location = "global"

    parent = f"projects/{project_id}/locations/{location}"

    # Detail on supported types can be found here:
    # https://cloud.google.com/translate/docs/supported-formats
    response = client.translate_text(
        request={
            "parent": parent,
            "contents": [text],
            "mime_type": "text/plain",  # mime types: text/plain, text/html
            "source_language_code": source,
            "target_language_code": target,
        }
    )

    # Display the translation for each input text provided
    return "".join([translation.translated_text for translation in response.translations])


