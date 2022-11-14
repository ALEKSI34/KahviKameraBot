
__app_name__ = "kahvikamera-bot"
__database_name__ = "wikifeet.db"
__tokenfile__ = "token.txt"
__admin_file__ = "admins.txt"


# Täähän ei siis oo paras tapa mitata että onko käyttäjä admin vai ei, mutta käyttäjät on idiootteja, eikä minua kiinnosta opettaa ihmisille miten vuoden kahden päästä lisätään uusia admineita.
# Uusia admineitahan sitten lisätään lisäämällä nimi admins.txt filuun. Formaatissa @Nimi
__kahvikamera_admins__ = []
with open(__admin_file__) as af: # Lueskellaan adminit
    for line in af:
        __kahvikamera_admins__.append(line)
    af.close()
