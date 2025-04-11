import os
import csv

racine = os.getcwd()

def recuperation(debut, fin, chemin):
    ma_liste = []
    numdebut = 0
    numfin = 0
    num_recolte = 0

    f = open(chemin, encoding='utf-8')
    csv_read = csv.reader(f)
    for ligne in csv_read: 
        numdebut = numdebut + 1
        if ligne == debut:
            break
    f.close()

    f = open(chemin, encoding='utf-8')
    csv_read = csv.reader(f)
    for ligne in csv_read: 
        numfin = numfin + 1
        if ligne == fin:
            break
    f.close()

    f = open(chemin, encoding='utf-8')
    csv_read = csv.reader(f)
    for ligne in csv_read: 
        num_recolte = num_recolte + 1
        if num_recolte > numdebut and num_recolte < numfin-1:
            ma_liste.append(ligne)
    f.close()

    sortie = []

    for line in ma_liste:
        i = str(line).split("|")
        sortie.append(i)

    return sortie 

def extraction_colonne(colonne, recuperation):
    num_ligne = 0
    resultat = []
    for liste in recuperation:
        num_ligne = num_ligne + 1
        for item in liste :
            if item == colonne:
                wa = liste.index(colonne)
        if num_ligne > 2 :
            resultat.append(liste[int(f"{wa}")])
    return resultat


def extraction_data(colonne, url, recuperation):
    for liste in recuperation:
        for item in liste :
            if item == colonne:
                wa = liste.index(colonne)
            if item == url: 
                resultat = (liste[int(f"{wa}")])
    return resultat

def sec_convert(time):
    i = str(time).split(":")
    h = int(i[0]) * 3600
    m = int(i[1]) * 60
    s = int(i[2])
    resultat = h + m + s 
    return resultat

def extraction_duration(recuperation, start, end):
    num_ligne = 0
    resultat = []
    for liste in recuperation:
        num_ligne = num_ligne + 1
        if num_ligne > 2 :
            #Extraction des timecode de la signe en seconde
            timers = []
            timer1 = sec_convert(liste[start])
            timers.append(timer1)
            timer2 = sec_convert(liste[end])
            timers.append(timer2)
            duration = timer2 - timer1
            timers.append(duration)
            resultat.append(timers)
    return resultat


def extraction_metadonne(target, recuperation):
  for liste in recuperation:
    for item in liste :
      if item == target:
        wa = liste.index(target) + 1
        resultat = liste[int(f"{wa}")]
  return resultat


# Fabricateur de markdown
