from iiif_prezi3 import Manifest, AnnotationPage, Annotation, ResourceItem, config
import json
import os
import arvestapi
from arvesttools.md_parser import recuperation, extraction_duration, extraction_colonne, extraction_metadonne


def md_to_manifest(markdown_folder, manifest_folder, mail, password) :


    ar = arvestapi.Arvest(mail, password)

    num_fichier = 0

    nbr = os.listdir(markdown_folder)
    md_count = 0
    for i in nbr :
        md_count += 1

    for i in range(md_count): 

        num_fichier = num_fichier +1 

        chemin = os.path.join(markdown_folder, f"Manifest_{num_fichier}.md")

        #Extraction des informations pour les Canvas

        Recuperation = recuperation(['## Canavses'],['@@@c'], chemin)
        link = extraction_colonne("Source", Recuperation)
        durations = extraction_duration(Recuperation, 2, 3)

        Recuperation_titres = recuperation(['## Manifest metadata'],['@@@m'], chemin)
        titre = extraction_metadonne("Title", Recuperation_titres)

        num = 0

        #Géneration du manifeste

        config.configs['helpers.auto_fields.AutoLang'].auto_lang = "en"
        base_url = "http://127.0.0.1:5500"
        manifest = Manifest(id=f"{base_url}/manifest_{num_fichier}.json", label=titre)

        #Creation du des Canvas 

        Recuperation.pop(0)

        for i in link:
            num = num + 1
            canvas = manifest.make_canvas(id=f"{base_url}/canvas{num}")
            anno_body = ResourceItem(id=link[int(f"{num-1}")],
                            type="Video",
                            format="video/MPG")

            anno_page = AnnotationPage(id=f"{base_url}/canvas/page")
            anno = Annotation(id=f"{base_url}/canvas/page/annotation",
                        motivation="painting",
                        body=anno_body,
                        target=canvas.id)

            hwd = {"height": 113, "width": 200, "duration":durations[int(f"{num-1}")][2]}
            anno_body.set_hwd(**hwd)
            canvas.set_hwd(**hwd)

            anno_page.add_item(anno)
            canvas.add_item(anno_page)

        #Export manifest en .json 

        nom_manifest = f"manifest_essai{num_fichier}.json"
        manifest_path = os.path.join(manifest_folder, nom_manifest)

        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest.dict(), f, ensure_ascii=False, indent=2)

                #Upload Arvest

        new_manifest = ar.add_manifest(path = manifest_path)

        manifestes = ar.get_manifests()
        new_manifest.update_title(titre)
        print(new_manifest.title)



        
def metadata_update(markdown_folder, manifest_folder, mail, password):

  ar = arvestapi.Arvest(mail, password)
  print(ar.profile.name)

  #Ouverture du markdown

  num_fichier = 0
  nbr = os.listdir(markdown_folder)
  md_count = 0
  for i in nbr :
      md_count += 1

  for i in range(md_count): 

    num_fichier = num_fichier +1 

    chemin = os.path.join(markdown_folder, f"Manifest_{num_fichier}.md")

    Contenu_canvas = recuperation(['## Manifest metadata'],['## Canavses'], chemin)

    titre = extraction_metadonne("Title", Contenu_canvas)
    speaker = extraction_metadonne("Speaker", Contenu_canvas)
    description = extraction_metadonne("Description", Contenu_canvas)
    place = extraction_metadonne("Place", Contenu_canvas)   
    tag = extraction_metadonne("tag", Contenu_canvas)

    #Recuperation du manifest

    manifestes = ar.get_manifests()

    for item in manifestes:
      if item.title == titre:
        contenu = item.get_content()
        id = item.id

    manifeste = ar.get_manifest(id)


    url = contenu["items"][0]["items"][0]["items"][0]["body"]["id"]


    metadonnee = [
        {"label":"Title","value":f"{titre}"},
        {"label":"Speaker","value":f"{speaker}"},
        {"label":"Description","value":f"{description}"},
        {"label":"Place","value":f"{place}"},
        {"label":"URL","value":f"{url}"},
        {"label":"Tag","value":f"{tag}"}
        ]

    contenu["metadata"] = metadonnee


    #Export du manifest en .json

    nom_manifest = f"{titre}.json"

    manifest_path = os.path.join(manifest_folder, nom_manifest)

    #with open( manifest_path, 'w', encoding='utf-8') as f:
    #    json.dump(contenu, f, ensure_ascii=False, indent=2)

    #Update du manifeste

    manifeste.update_content(contenu)
    print(manifeste.get_content())
    print("_________________________________")



def md_to_anotation(markdown_folder, manifest_folder, mail, password) :


    ar = arvestapi.Arvest(mail, password)

    print("upload yours anotations...")

    num_fichier = 0

    nbr = os.listdir(markdown_folder)
    md_count = 0
    for i in nbr :
            md_count += 1

    for i in range(md_count): 

        num_fichier = num_fichier +1 

        chemin = os.path.join(markdown_folder, f"Manifest_{num_fichier}.md")

        #Extraction des informations pour les Canvas

        Recuperation_titres = recuperation(['## Manifest metadata'],['@@@m'], chemin)
        titre = extraction_metadonne("Title", Recuperation_titres)

        manifestes = ar.get_manifests()

        for item in manifestes:
                if item.title == titre:
                    contenu = item.get_content()
                    #manifeste = item
                    ident = item.id

        manifeste = ar.get_manifest(ident)


        #Extraction des informations pour les Canvas

        Recuperation = recuperation(['## Text Annotations'],['@@@ta'], chemin)
        annot = extraction_colonne("Contenu", Recuperation)
        durations = extraction_duration(Recuperation, 1, 2)


        #Transformation des url en lien cliquable 


        for i in annot :
                if i.find("https") > 0 :
                    wa = annot.index(i)
                    a = i.index("https")
                    b = len(i)
                    url1 = (i[a:b])
                    if url1.find(" ") > 0:
                            j = url1.index(" ")
                            url2 = (url1[0:j])
                            url3 = f"<a href=\"{url2}\">{url2}</a>"
                            y = i.replace(url1,url3)
                            annot[wa] = y
                    else :
                            url2 = f"<a href=\"{url1}\">{url1}</a>"
                            y = i.replace(url1,url2)
                            annot[wa] = y


        #Creation d'une base d'annotation 

        base_url = "http://127.0.0.1:5500"
        canvas_id = contenu["items"][0]["id"]

        manifest = Manifest(id=f"{base_url}/manifest_essai2.json",
                label={"en": ["Scott"]})
        canvas = manifest.make_canvas_from_iiif(url="https://iiif.io/api/image/3.0/example/reference/918ecd18c2592080851777620de9bcb5-gottingen",
                                        id=canvas_id)

        num = 0

        #Création des annotations

        for ligne in durations:
                num = num +1
   
                anno = canvas.make_annotation(id=f"{base_url}/annotation/p{num}-comment",
                            motivation="commenting",
                            body={"type": "TextualBody",
                                    "language": "en",
                                    "format": "text/plain",
                                    "value": f"{annot[num-1]}"},
                            target=canvas.id + f"#t={durations[num-1][0]},{durations[num-1][1]}",
                            anno_page_id=f"{base_url}/page/p1/1")

                rag = canvas.json(indent=2)

                raga = json.loads(rag)

                if num == 1 :
                        contenu["items"][0]["annotations"] = raga["annotations"]
                if num > 1 : 
                        contenu["items"][0]["annotations"][0]["items"] = raga["annotations"][0]["items"]

        #Export vers un fichier json 

        nom_manifest = "test_annotation.json"

        manifest_path = os.path.join(manifest_folder, nom_manifest)

        with open( manifest_path, 'w', encoding='utf-8') as f:
                json.dump(contenu, f, ensure_ascii=False, indent=2)


        #Upload sur Arvest

        manifeste.update_content(contenu)
        print(titre)

    print("your manifest was successfully annotated !")
            