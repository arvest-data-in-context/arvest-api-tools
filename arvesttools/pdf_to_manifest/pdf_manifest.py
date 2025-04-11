from pdf2image import convert_from_path
import os
import arvestapi
import json
from PIL import Image
import poppler
from urllib.request import urlopen
from iiif_prezi3 import Manifest, config


def pdf2manifest(pdf_folder, img_folder, mail, password, resolution):

    #Connection a Arveste

    ar = arvestapi.Arvest(mail, password)
    print(f"Connected on Arveste as {ar.profile.name}")

    #Export des pages du pdf dans un dossier de jpeg

    dirs = os.listdir(pdf_folder)

    for i in dirs :

        print(f"Convert {i} into jpeg...")

        #Nom du dossier 
        folder_name = i.replace('.pdf', '')

        #PDF a utiliser 
        pdf_path = os.path.join(pdf_folder, f'{folder_name}.pdf')
        
        # Creation du fichier d'expotyt
        output = rf"{img_folder}\{folder_name}"
        os.mkdir(output)

        # Conversion en JPEG
        image = convert_from_path(pdf_path, resolution)

        for i, page in enumerate(image):
            output_path = os.path.join(img_folder, f'{folder_name}', f"{folder_name}_page_{i + 1}.jpeg")
            page.save(output_path, 'JPEG')


    dirs_img = os.listdir(img_folder)

    print("Upload medias on Arvest...")

    # Pour chaque sous-dossier dans le dossier image
    for i in dirs_img:
        img_sub_folder = os.path.join(img_folder, f"{i}")
        images = os.listdir(img_sub_folder)

        #Upload des images du sous-dossier
        for j in images :
            path_image = os.path.join(img_folder, f"{i}", f"{j}")
            added_media = ar.add_media(path = path_image)
            os.remove(path_image)

        os.rmdir(img_sub_folder)
    
        medias = ar.get_medias()

        nom_manifest = i


        #Géneration du manifeste

        print(f"Generate your manifest : {i}")

        config.configs['helpers.auto_fields.AutoLang'].auto_lang = "en"
        base_url = "http://127.0.0.1:5500"

        manifest = Manifest(id=f"{base_url}/diapo_{nom_manifest}.json", label=f"{nom_manifest}")


        #Décompte des media Arvest a utiliser dans le manifest

        cont = 0

        for i in medias:
            detecte_titre = i.title.count(nom_manifest)

            if detecte_titre == 1 :
                cont = cont +1


        #Extraction de la taille 

        for l in medias:
            if l.title == f"{nom_manifest}_page_1.jpeg":
                image_url = l.get_full_url()
                    
                img =Image.open(urlopen(image_url))

                widh_media, height_media = img.size

        #Creation des Canvas

        num = 0

        for h in range(cont):

            num = num + 1

            for j in medias:
                if j.title == f"{nom_manifest}_page_{int(num)}.jpeg":
                    image_url = j.get_full_url()
                
                    canvas = manifest.make_canvas(id=f"{base_url}/canvas{num}/p1", height=height_media, width=widh_media)
                    anno_page = canvas.add_image(image_url = image_url,
                                                anno_page_id=f"{base_url}/page/p1/1",
                                                anno_id=f"{base_url}/annotation/p0001-image",
                                                format=f"image/jpeg",
                                                height=widh_media,
                                                width=height_media
                                                )

        nom_manifest = f"Pdf_{nom_manifest}.json"
        manifest_path = os.path.join(os.getcwd(),"Boite a manifest", nom_manifest)

        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest.dict(), f, ensure_ascii=False, indent=2)

        #Upload du manifest sur Arvest

        new_manifest = ar.add_manifest(path = manifest_path)

        print(f"{nom_manifest} was successfully upload ! ")

