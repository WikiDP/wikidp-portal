"""Controllers and helper functions for Wikimedia API calls."""

import json
from urllib import request as urllib_request


def get_image_url_from_title(title):
    """Convert image title to the url location of that file it describes."""
    # TO DO: Url's do not work with non-ascii characters
    #    For example, the title of the image for Q267193 [Submlime Text]
    #    is "Скриншот sublime text 2.png"
    title = title.replace(" ", "_")
    url = "https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&titles=File:%s&format=json"%(title)
    try:
        url = urllib_request.urlopen(url)
        base = json.loads(url.read().decode())["query"]["pages"]
        # Return just the first item
        for item in base:
            out = base[item]["imageinfo"][0]["url"]
            break
        return out
    except Exception:
        return "https://commons.wikimedia.org/wiki/File:"+title
