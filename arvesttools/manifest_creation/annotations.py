import os
import iiif_prezi3

def _get_canvas_annotation_annotation_page(manifest, canvas_idx):
    if manifest.items[0].annotations == None:
        annotation_page = iiif_prezi3.AnnotationPage(id = "https://placeholder.com/canvas/1/annotation/1")
    else:
        annotation_page = manifest.items[0].annotations[0]
    return annotation_page

def add_textual_annotation(manifest, canvas_idx = 0, **kwargs):
    """
    kwargs:
    - linked_manifest
    - text_content
    - xywh
    - t
    - motivation (default commenting, can be tagging)
    """
    ap = _get_canvas_annotation_annotation_page(manifest, canvas_idx)

    annotation_idx = len(ap.items) + 1

    id = f"https://placeholder.com/canvas/{canvas_idx + 1}/annotation/1/{annotation_idx}"
    if kwargs.get("linked_manifest", None) != None:
        id = f"{id}#{kwargs.get('linked_manifest')}"

    target = "https://placeholder.com/canvas/1"

    if kwargs.get("xywh", None) != None:
        pos = kwargs.get("xywh")
        target = f"{target}#xywh={pos['x']},{pos['y']},{pos['w']},{pos['h']}"
        if kwargs.get("t", None) != None:
            t = kwargs.get("t")
            target = f"{target}&t={t['start']},{t['end']}"
    elif kwargs.get("t", None) != None:
        t = kwargs.get("t")
        target = f"{target}#t={t['start']},{t['end']}"

    body = {
        "type" : "TextualBody",
        "format" : "text/html",
        "value" : kwargs.get("text_content", f"<p>Annotation {annotation_idx}</p>")
    }

    ap.items.append(iiif_prezi3.Annotation(
        id = id,
        motivation = kwargs.get("motivation", "commenting"),
        target = target,
        body = body
    ))

    manifest.items[canvas_idx].annotations = [ap]
    return manifest