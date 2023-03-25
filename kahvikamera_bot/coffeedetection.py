
import cv2
import os
import numpy as np
from typing import Tuple, Optional
from tensorflow import lite # Voi myös käyttää sitä toista tensorflow-runtime kirjastoa raspilla
from PIL import Image
from loguru import logger

coffee_color = np.array([15,15,15])
black = np.array([0,0,0])

kahvipannu_loc = os.path.join(os.getcwd(),"resurssit\\kahvipannumustavalko2.png")
AI_loc = os.path.join(os.getcwd(),"kahviAI.tflite")

ai_interpreter = lite.Interpreter(model_path=AI_loc)
ai_interpreter.allocate_tensors()
input_details = ai_interpreter.get_input_details()
output_details = ai_interpreter.get_output_details()
_, height, width, _ = input_details[0]['shape']

params = cv2.SimpleBlobDetector_Params()
params.minArea = 100

kahvipannu = cv2.imread(kahvipannu_loc,0)

class CoffeeFileNotFound(Exception):
    ...


def ClassifyImage(image : Image, top_k=1):
    np_array= np.expand_dims(np.float32(np.asarray(image)), axis=0)
    ai_interpreter.set_tensor(input_details[0]['index'], np_array)

    ai_interpreter.invoke()

    predictions = ai_interpreter.get_tensor(output_details[0]['index'])[0]
    if predictions[0] > 0.5:
        return True, predictions[0]*100
    else:
        return False, 100-(predictions[0]*100)

def CheckIfImageHasCoffeeAI(image_path : str) -> Tuple[bool, Optional[float]]:
    #print(f"Analysoidaan kuvaa.... {image_path}")
    try:
        image = Image.open(image_path).convert('RGB').resize((width, height))
        id, prob = ClassifyImage(image)
    except Exception as e:
        logger.exception(e)
        return False, 100.0
    return id, round(prob,3)

def CheckIfImageHasCoffee(image_path : str, showimage = False, print_val = False) -> bool:
    """Se metodi mikä oikeasti katsoo onko siellä kahvia vai ei"""
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