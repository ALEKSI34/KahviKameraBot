from kahvikamera_bot.coffeedetection import CheckIfImageHasCoffeeAI
import os
from pathlib import Path

Falses = Path("Imagepool/EiKahvia").absolute()
Trues = Path("Imagepool/OnKahvia").absolute()

def test():
    ffpos=0
    tfpos=0

    print("Testi: Pannussa ei ole kahvia")
    ImagePaths = os.listdir(Falses)
    print(f"Kuvia : {len(ImagePaths)}")
    for image in ImagePaths:
        id, prob = CheckIfImageHasCoffeeAI(os.path.join(Falses,image))
        if id != False: 
            ffpos += 1
            print(f"{image} {id} - prob {prob}")
    if ffpos == 0:
        print("100% Tarkka?!!?")

    ImagePaths = os.listdir(Trues)
    print("Testi: Pannussa on kahvia")
    print(f"Kuvia : {len(ImagePaths)}")
    for image in ImagePaths:
        id, prob = CheckIfImageHasCoffeeAI(os.path.join(Trues,image))
        if id != True:
            tfpos += 1
            print(f"{image} :{id} - prob {prob}")
    if tfpos == 0:
        print("100% Tarkka?!!?")


if __name__ == "__main__":
    test()