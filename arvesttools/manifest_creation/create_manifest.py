"""
TODO:
- Tetras seems to force youtube manifests to be 2654.8672566371683 * 1500
- Local file manifests have no thumbnails
- MAke the append to canvas recursive

this whole scirpt is fucking heinous needs a refactor
"""

import iiif_prezi3
import mimetypes
from jhutils.local_files import get_image_info, get_audio_info, get_video_info
import jhutils.online_files
import re
import os
import uuid
import shutil

def media_to_manifest(arvest_media_item, **kwargs) -> iiif_prezi3.Manifest:
    """
    Give a arvest_media_item instance and return a iiif_prezi3 Manifest.
    
    kwargs
    - url_prefix
    - file_name
    - manifest_label
    """

    if isinstance(arvest_media_item, str):
        if os.path.isfile(arvest_media_item):
            return _media_to_manifest_local_file(arvest_media_item, **kwargs)
        else:
            temp_folder = os.path.join(os.getcwd(), str(uuid.uuid4()))
            if os.path.isdir(temp_folder) == False:
                os.makedirs(temp_folder)
            dl_location = jhutils.online_files.download(arvest_media_item, dir = temp_folder)
            ret = _media_to_manifest_local_file(dl_location, **kwargs)
            ret.items[0].items[0].items[0].body.id = arvest_media_item
            shutil.rmtree(temp_folder)
            return ret
    else:
        return _media_to_manifest_arvest_media_item(arvest_media_item, **kwargs)
    
def _media_to_manifest_arvest_media_item(arvest_media_item, **kwargs) -> iiif_prezi3.Manifest:
    ret = iiif_prezi3.Manifest(
        id = f"{kwargs.get('url_prefix', 'https://placeholder.com')}/{kwargs.get('file_name', 'manifest.json')}",
        label = kwargs.get("manifest_label", {"en" : [f"{arvest_media_item.title}"]})
    )

    thumb_object = media_item_to_thumbnail(arvest_media_item)
    ret.thumbnail = thumb_object

    canvas = media_to_canvas(arvest_media_item, **kwargs)
    canvas.thumbnail = thumb_object

    ret = append_canvas_to_manifest(ret, canvas)

    return ret

def _media_to_manifest_local_file(local_file, **kwargs) -> iiif_prezi3.Manifest:
    file_name = os.path.splitext(os.path.basename(local_file))[0]
    
    ret = iiif_prezi3.Manifest(
        id = f"{kwargs.get('url_prefix', 'https://placeholder.com')}/{kwargs.get('file_name', 'manifest.json')}",
        label = kwargs.get("manifest_label", {"en" : [f"{file_name}"]})
    )

    # thumb_object = media_item_to_thumbnail(local_file)
    # ret.thumbnail = thumb_object

    canvas = media_to_canvas_local_file(local_file, **kwargs)
    # canvas.thumbnail = thumb_object

    ret = append_canvas_to_manifest(ret, canvas)

    return ret

def append_canvas_to_manifest(manifest, canvas):
    index = len(manifest.items) + 1

    "https://placeholder.com/canvas/&&CANVAS-INDEX/page/1/1"


    if "&&CANVAS-INDEX" in canvas.id:
        canvas.id = canvas.id.replace("&&CANVAS-INDEX", str(index))
        canvas.items[0].id = canvas.items[0].id.replace("&&CANVAS-INDEX", str(index))
        canvas.items[0].items[0].id = canvas.items[0].items[0].id.replace("&&CANVAS-INDEX", str(index))
        canvas.items[0].items[0].target = canvas.items[0].items[0].target.replace("&&CANVAS-INDEX", str(index))
    elif "https://placeholder.com/canvas/" in canvas.id:
        # original_id = canvas.id
        original_ap_id = canvas.items[0].id
        # original_annotation_id = canvas.items[0].items[0].id
        # original_annotation_target = canvas.items[0].items[0].target

        original_index = original_ap_id.split("https://placeholder.com/canvas/")[1].split("/")[0]
        replace_string = f"https://placeholder.com/canvas/{original_index}"
        replace_new = f"https://placeholder.com/canvas/{index}"

        canvas.id = canvas.id.replace(replace_string, replace_new)
        canvas.items[0].id = canvas.items[0].id.replace(replace_string, replace_new)
        canvas.items[0].items[0].id = canvas.items[0].items[0].id.replace(replace_string, replace_new)
        canvas.items[0].items[0].target = canvas.items[0].items[0].target.replace(replace_string, replace_new)

    manifest.items.append(canvas)

    return manifest

def media_to_canvas(arvest_media_item, **kwargs) -> iiif_prezi3.Canvas:
    """
    Give a arvest media item and return a iiif_prezi3 Canvas.
    Returns &&CANVAS-INDEX instead of the actual index (use `append_canvas_to_manifest()`)

    kwargs:
    - url_prefix
    - label
    """
    ret = iiif_prezi3.Canvas(
        id = f"{kwargs.get('url_prefix', 'https://placeholder.com')}/canvas/&&CANVAS-INDEX",
        label = kwargs.get("manifest_label", {"en" : [f"{arvest_media_item.title}"]})
    )

    media_type = _get_media_type(arvest_media_item.get_full_url())
    
    if media_type == "audio" or media_type == "video" or media_type == "image":
        media_info = _get_media_info(arvest_media_item.get_full_url())
    else:
        media_info = _get_media_info_streaming(arvest_media_item.get_full_url())

    if media_type == "image" or media_type == "video" or media_type == "youtube" or media_type == "peertube":
        ret.width = media_info["width"]
        ret.height = media_info["height"]
    if media_type == "audio" or media_type == "video" or media_type == "youtube" or media_type == "peertube":
        ret.duration = media_info["duration"]

    annotation_page = iiif_prezi3.AnnotationPage(id = "https://placeholder.com/canvas/&&CANVAS-INDEX/page/1")
    media_annotation_element = iiif_prezi3.Annotation(
        id = "https://placeholder.com/canvas/&&CANVAS-INDEX/page/1/1",
        motivation = "painting",
        target = "https://placeholder.com/canvas/&&CANVAS-INDEX"
    )
    
    if media_type == "youtube" or media_type == "peertube":
        body = {
            "id" : arvest_media_item.get_full_url(),
            "type" : "Video",
            "format" : "video/mpg"
        }
    else:
        mime_type, encoding = mimetypes.guess_type(arvest_media_item.get_full_url())
        body = {
            "id" : arvest_media_item.get_full_url(),
            "type" : mime_type.split("/")[0].capitalize(),
            "format" : mime_type
        }

    if media_type == "image" or media_type == "video" or media_type == "youtube" or media_type == "peertube":
        body["width"] = media_info["width"]
        body["height"] = media_info["height"]
    if media_type == "audio" or media_type == "video" or media_type == "youtube" or media_type == "peertube":
        body["duration"] = media_info["duration"]

    if media_type == "image" or media_type == "video" or media_type == "youtube" or media_type == "peertube":
        media_annotation_element.target = media_annotation_element.target + f"#xywh=0,0,{media_info['width']},{media_info['height']}"
        if media_type == "video" or media_type == "youtube" or media_type == "peertube":
            media_annotation_element.target = media_annotation_element.target + f"&t=0,{media_info['duration']}"
    if media_type == "audio":
        media_annotation_element.target = media_annotation_element.target + f"#t=0,{media_info['duration']}"

    media_annotation_element.body = body
    annotation_page.items.append(media_annotation_element)
    ret.items.append(annotation_page)

    return ret

def media_to_canvas_local_file(local_file, **kwargs) -> iiif_prezi3.Canvas:
    """
    Give a arvest media item and return a iiif_prezi3 Canvas.
    Returns &&CANVAS-INDEX instead of the actual index (use `append_canvas_to_manifest()`)

    kwargs:
    - url_prefix
    - label
    """
    file_name = os.path.splitext(os.path.basename(local_file))[0]

    ret = iiif_prezi3.Canvas(
        id = f"{kwargs.get('url_prefix', 'https://placeholder.com')}/canvas/&&CANVAS-INDEX",
        label = kwargs.get("manifest_label", {"en" : [f"{os.path.basename(local_file)}"]})
    )

    media_type = _get_media_type(local_file)
    
    if media_type == "audio" or media_type == "video" or media_type == "image":
        media_info = _get_media_info(local_file)
    else:
        media_info = _get_media_info_streaming(local_file)

    if media_type == "image" or media_type == "video" or media_type == "youtube" or media_type == "peertube":
        ret.width = media_info["width"]
        ret.height = media_info["height"]
    if media_type == "audio" or media_type == "video" or media_type == "youtube" or media_type == "peertube":
        ret.duration = media_info["duration"]

    annotation_page = iiif_prezi3.AnnotationPage(id = "https://placeholder.com/canvas/&&CANVAS-INDEX/page/1")
    media_annotation_element = iiif_prezi3.Annotation(
        id = "https://placeholder.com/canvas/&&CANVAS-INDEX/page/1/1",
        motivation = "painting",
        target = "https://placeholder.com/canvas/&&CANVAS-INDEX"
    )
    
    if media_type == "youtube" or media_type == "peertube":
        body = {
            "id" : f"https://placeholder.com/{local_file}",
            "type" : "Video",
            "format" : "video/mpg"
        }
    else:
        mime_type, encoding = mimetypes.guess_type(local_file)
        body = {
            "id" : f"https://placeholder.com/{local_file}",
            "type" : mime_type.split("/")[0].capitalize(),
            "format" : mime_type
        }

    if media_type == "image" or media_type == "video" or media_type == "youtube" or media_type == "peertube":
        body["width"] = media_info["width"]
        body["height"] = media_info["height"]
    if media_type == "audio" or media_type == "video" or media_type == "youtube" or media_type == "peertube":
        body["duration"] = media_info["duration"]

    if media_type == "image" or media_type == "video" or media_type == "youtube" or media_type == "peertube":
        media_annotation_element.target = media_annotation_element.target + f"#xywh=0,0,{media_info['width']},{media_info['height']}"
        if media_type == "video" or media_type == "youtube" or media_type == "peertube":
            media_annotation_element.target = media_annotation_element.target + f"&t=0,{media_info['duration']}"
    if media_type == "audio":
        media_annotation_element.target = media_annotation_element.target + f"#t=0,{media_info['duration']}"

    media_annotation_element.body = body
    annotation_page.items.append(media_annotation_element)
    ret.items.append(annotation_page)

    return ret

def _get_media_info(media_url):
    if os.path.isfile(media_url):
        mime_type, encoding = mimetypes.guess_type(media_url)
        file_type = mime_type.split("/")[0]
        if file_type == "image":
            info = get_image_info(media_url)
        elif file_type == "video":
            info = get_video_info(media_url)
        elif file_type == "audio":
            info = get_audio_info(media_url)
        return info
    else:
        temp_folder = os.path.join(os.getcwd(), str(uuid.uuid4()))
        if os.path.isdir(temp_folder) == False:
            os.makedirs(temp_folder)
        dl_location = jhutils.online_files.download(media_url, dir = temp_folder)
        mime_type, encoding = mimetypes.guess_type(dl_location)
        file_type = mime_type.split("/")[0]
        if file_type == "image":
            info = get_image_info(dl_location)
        elif file_type == "video":
            info = get_video_info(dl_location)
        elif file_type == "audio":
            info = get_audio_info(dl_location)
        shutil.rmtree(temp_folder)
        return info

def _get_media_info_streaming(media_url):
    return jhutils.online_files.get_online_video_info(media_url)

def _get_media_type(media_url):
    """
    Possible types:
    - image
    - audio
    - video
    - youtube
    - peertube
    """
    if _is_youtube_video_regex(media_url):
        return "youtube"
    elif _is_peertube_video_regex(media_url):
        return "peertube"
    else:
        mime_type, encoding = mimetypes.guess_type(media_url)
        return mime_type.split("/")[0]

def _is_youtube_video_regex(url):
    YOUTUBE_VIDEO_REGEX = re.compile(
        r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
    )
    return bool(YOUTUBE_VIDEO_REGEX.match(url))

def _is_peertube_video_regex(url):
    PEERTUBE_REGEX_1 = re.compile(
        r'https?://[^/]+/videos/watch/[\w\-]+'
    )
    PEERTUBE_REGEX_2 = re.compile(
        r'https?://[^/]+/w/[\w\-]+'
    )
    PEERTUBE_REGEX_3 = re.compile(
        r'https?://[^/]+/videos/embed/[\w\-]+'
    )

    return bool(PEERTUBE_REGEX_1.match(url) or PEERTUBE_REGEX_2.match(url) or PEERTUBE_REGEX_3.match(url))

def media_item_to_thumbnail(arvest_media_item):
    thumb_url = arvest_media_item.thumbnail_url
    if thumb_url != None:
        temp_folder = os.path.join(os.getcwd(), str(uuid.uuid4()))
        if os.path.isdir(temp_folder) == False:
            os.makedirs(temp_folder)

        dl_location = jhutils.online_files.download(thumb_url, dir = temp_folder)
        thumb_info = get_image_info(dl_location)
        mime_type, encoding = mimetypes.guess_type(dl_location)

        # Create a thumbnail object:
        thumb_object = {
            "id" : thumb_url,
            "type" : mime_type.split("/")[0].capitalize(),
            "format" : mime_type,
            "width" : thumb_info["width"],
            "height" : thumb_info["height"]
        }

        shutil.rmtree(temp_folder)

        return thumb_object
    else:
        return None