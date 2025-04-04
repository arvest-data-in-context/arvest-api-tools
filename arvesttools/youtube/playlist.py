from iiif_prezi3 import Manifest, AnnotationPage, Annotation, ResourceItem, config
import json
import os
import arvestapi
from googleapiclient.discovery import build
import requests
import isodate


#Recuperation de la playliste via l'API Youtube


def get_playlist_videos(playlist_id, youtube):
    videos = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_title = item['snippet']['title']
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            videos.append((video_title, video_url))

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return videos


#Recuperation durée de la video

def get_video_duration(api_key, video_id):

    url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails&id={video_id}&key={api_key}"
    response = requests.get(url)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        data = response.json()
        duration = data['items'][0]['contentDetails']['duration']
        duration_in_seconds = isodate.parse_duration(duration).total_seconds()
        return duration_in_seconds
    else:
        print(f"Erreur lors de la requête à l'API YouTube: {response.status_code}")
        return None


#Generation du manifest playlist(API KEY, liste_video, )

def playlist(api_key, liste_video, manifest_folder, mail, password):
    num = 0
    liste_nom_tempo = []
    ar = arvestapi.Arvest(mail, password)

    for vid in liste_video : 

        num = num + 1

        video_id = vid["url"].replace("https://www.youtube.com/watch?v=", "")
        duration = get_video_duration(api_key, video_id)

        config.configs['helpers.auto_fields.AutoLang'].auto_lang = "en"
        base_url = "https://iiif.io/api/cookbook/recipe/0003-mvm-video"
        manifest = Manifest(id=f"{base_url}/manifest.json", label="Video Example 3")

        canvas = manifest.make_canvas(id=f"{base_url}/canvas")
        anno_body = ResourceItem(id=vid["url"],
                            type="Video",
                            format="video/MPG")

        anno_page = AnnotationPage(id=f"{base_url}/canvas/page")
        anno = Annotation(id=f"{base_url}/canvas/page/annotation",
                    motivation="painting",
                    body=anno_body,
                    target=canvas.id)

        hwd = {"height": 113, "width": 200, "duration":duration}
        anno_body.set_hwd(**hwd)
        canvas.set_hwd(**hwd)

        anno_page.add_item(anno)
        canvas.add_item(anno_page)


        nom_manifest = f"manifest_essai{num}.json"

        manifest_path = os.path.join(manifest_folder, nom_manifest)

        with open( manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest.dict(), f, ensure_ascii=False, indent=2)

        
        #Upload du manifest sur Arvest

        new_manifest = ar.add_manifest(path = manifest_path)

    #Correction nom manifestes 

    num = 0
    manifestes = ar.get_manifests()

    for i in manifestes :
            num = num + 1
            if i.title == f"manifest_essai{num}.json":
                print(liste_video[int(f"{num-1}")]["titre"])
                i.update_title(liste_video[int(f"{num-1}")]["titre"])