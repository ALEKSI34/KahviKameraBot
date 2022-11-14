# KahviKameraBot
Telegrambotti millä saa /kahvikamera komennon telegrammiin
Tähän on käytetty joku kollektiivinen 20 minuuttia aikaa niin varmasti voi jotain tehdä paremminkin.
Mutta ideanahan on toteuttaa kaikkea hauskaa telegram botilla.

## Poetry
Jotkut voi ajatella että mikähän ihme tämä oikein on, mutta tällä on oikein kiva pyöritellä kaikki kirjastot yms.
Jos sinulla ei ole poetryä niin senhän saa helposti

    pip install poetry

Ja sitten voi kirjoittaa vaan tässä repossa

    poetry install

Ja kaikki ajamiseen tarvittavat kirjastot asentuu automaagisesti.

Botti lähtee käyntiin seuraavilla komennoilla:

    poetry shell
    poetry run kahvikamera-bot

## Luotavat tiedostot

Seuraavat tiedostot pitää luoda:

token.txt -> Laita sinne sisään tg botin token eikä mitään muuta.

admins.txt -> Jokaiselle riville telegram botin adminit. Esim. @KahviKamera.
Luonnollisesti jos vaihtaa nimeä, niin botti ei enää tunnista adminiksi, mutta just sopivan helppo käyttää.
