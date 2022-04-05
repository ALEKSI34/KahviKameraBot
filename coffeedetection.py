
import cv2
import os
import numpy as np


coffee_color = np.array([15,15,15])
black = np.array([0,0,0])

kahvipannu_loc = "kahvipannumustavalko2.png"

params = cv2.SimpleBlobDetector_Params()
params.minArea = 100

kahvipannu = cv2.imread(kahvipannu_loc,0)

class CoffeeFileNotFound(Exception):
    def __init__(self, message : str) -> None:
        super().__init__()


def CheckIfImageHasCoffee(image_path : str, showimage = False, print_val = False):
    original = cv2.imread(image_path)
    image = cv2.imread(image_path,0)
    edges = cv2.Canny(image,20,200)
    try:
        mask = cv2.inRange(original, black, coffee_color)
    except cv2.error as e:
        raise CoffeeFileNotFound("Either the pattern or the source file wasn't found. Check paths etc.")

    alpha = 0.5
    beta = (1.0 - alpha)
    dst = np.uint8(alpha*(edges)+beta*(mask))


    w = kahvipannu.shape[0]
    h = kahvipannu.shape[1]
    res = cv2.matchTemplate(dst,kahvipannu,cv2.TM_CCOEFF_NORMED)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    if print_val:
        print(max_val)

    if max_val > 0.47:
        top_left = max_loc

        bottom_right = (top_left[0] + w, top_left[1] + h)
        if showimage:    
            cv2.rectangle(dst,top_left, bottom_right, 255, 2)
            cv2.imshow("Result", np.hstack((image,dst)))
            cv2.waitKey(0)
        return True
    else:
        return False



def colortest():
    Count = 0
    Correct = 0
    Fault = 0
    HasCoffee = False
    for image in os.listdir("Imagepool"):
        Count += 1
        HasCoffee = CheckIfImageHasCoffee(str("Imagepool/"+image))
        if "kahvia" in image:
            if HasCoffee:
                #print("OIKEA VASTAUS")
                Correct += 1
            else:
                print("Olisi pitänyt sanoa on kahvia")
                p = CheckIfImageHasCoffee(str("Imagepool/"+image),True,True)
                print(str(image))
                if not "ExpectPos" in image:
                    os.rename(str("Imagepool/"+image),"Imagepool/ExpectPos_"+image)
                Fault += 1
        else:
            if HasCoffee:
                print("False positive")
                p = CheckIfImageHasCoffee(str("Imagepool/"+image),True,True)
                print(str(image))
                if not "falsepos" in image:
                    os.rename(str("Imagepool/"+image),"Imagepool/falsepos_"+image)
                Fault += 1
            else:
                #print("Hyvä botti!")
                Correct += 1
    print("Kahvikuvia oli yhteensä: " + str(Count))
    print("Kuvista oikein koodi arvasi: " + str(Correct))
    print("Vääriä: "+ str(Fault))


if __name__ == "__main__":
    HasCoffee = CheckIfImageHasCoffee("Kissakoira.jpg")
    #colortest()