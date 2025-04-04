import arvestapi
import os
import json
import requests

#Connection a Arvest

url = "https://api.arvest.app/auth/login"

body = {
    "mail" : "aryodeliae@gmail.com", 
    "password" :"Arvestmoon1203"
}

response = requests.post(url, json = body)

print(response.status_code)

if response.status_code == 200:
    access_token = response.json()["access_token"]

auth_header = {"Authorization" : f"Bearer {access_token}"}




#Connection via le package api 

ar = arvestapi.Arvest("aryodeliae@gmail.com", "Arvestmoon1203")
print(ar.profile.name)




#ARVEST API TEST



manifestId = "https://www.youtube.com/watch?v=osy_twtjkMs"

manifestes = ar.get_manifests()

#for i in manifestes :
#    if i.title == "Clarisse Bardiot & Jacob Hart ¬ IIIF, a Standard for Multimodal Corpora? The Building of SCENE":
#        id = i.id
#        print(id) 

api_arvest_prefix = "https://api.arvest.app"

validation = input("Y for deletre : ")

if validation == "y" :
    for i in manifestes:
        url2 = f"{api_arvest_prefix}/link-manifest-group/manifest/{i.id}"
        requests.delete(url2, headers = auth_header)
else :
    pass

# https://api.arvest.app/link-manifest-group/manifest/12