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

        num_man = 0
        manifestes = ar.get_manifests()

        for i in manifestes :
            num_man = num_man + 1
            if i.title == f"manifest_essai{num_man}.json":
                print(titre)
                i.update_title(titre)