###################################################################################################################################
# Application to scrape and extract aadhaar number from image files using Tesseract, and mask the first 8 letters
###################################################################################################################################
import pytesseract
from pytesseract import Output
from PIL import *
import cv2
import os
import re
import pathlib

import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import numpy as np
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

path = 'C:/Users/sriha/Desktop/Aadhar_cards/'
#os.chdir(path)

########################################################
# Routine to add spaces between the aadhaar number words
########################################################
def addSpace(adhNum):
    
    [adhNum[i:i+3] for i in range(0, len(adhNum), 4)]
    adhNum = ' '.join([adhNum[i:i+4] for i in range(0, len(adhNum), 4)])

    return(adhNum)

########################################################
# Routine to add spaces between the aadhaar number words
########################################################
def get_number(image):
    
    global adhNumErr
    global df
    
    cols          = ['Image','Number']
    lst           = []
    adhNumErr     = []
    
    try:
        img    = cv2.imread(path+image)
        text   = pytesseract.image_to_string(img) 
        
        if text == '':
            text   = pytesseract.image_to_string(img,config='--psm 6')
        text   = text.split('\n')

        r      = re.compile(r'^[\d/</$/\s][0-9/\s][0-9][0-9/\s][\s/-][0-9][0-9][0-9][0-9][\s]')
        text   = list(filter(r.match, text))
        adhNum = (re.sub("[^0-9]", " ", str(text[0])))
        adhNum = re.sub(r'\s+', '', adhNum)
        
        
        if len(adhNum) == 12:
            adhNum   = addSpace(adhNum)
            adhNum   = adhNum[-4:].rjust(len(adhNum), "*")
            pos = 4
            adhNum   = adhNum[:pos] + ' ' + adhNum[pos+1:]
            pos = 9
            adhNum   = adhNum[:pos] + ' ' + adhNum[pos+1:]           
            adhNumErr = ''    
        else:
            adhNumErr = 'Error'
            
    except Exception as e:
        adhNumErr = 'Error'
        adhNum    = 0
        text      = ''
        return (adhNum,text,adhNumErr)

    text = re.sub(r"[^a-zA-Z0-9]+", ' ', text[0]).strip()
    
    return (adhNum,text,adhNumErr)

######################################################
# Function to  mask first two words of Aadhaar Numbers
######################################################

def maskAadhaar(img,words,image,number,type):
    
    global cordErr
    global cords
    
    font        = cv2.FONT_HERSHEY_TRIPLEX
    fontScale1  = 0.75
    fontScale2  = 0.55
    fontColor   = (0,0,0)
    lineType    = 2
    configOpts  = ['','--psm 6','--psm 4','--psm 11','--psm 12']
    
    for i in range(len(configOpts)):
        
        temp  = []
        cords = []
        text  = pytesseract.image_to_data(img, lang='eng', config =configOpts[i], output_type=Output.DICT)

        # Get the locations of first two words of aadhaar number from the image

        subtext = text['text']
        n_boxes = len(text['level'])
        lst_    = []

        for i in range(len(subtext)):

            if (subtext[i]==words[0]):
                row      = {'Image':image,'Number':words[0], 'Position':0,'Location':i}      
                lst_.append(row)
                temp.append(words[0])

            if (subtext[i]==words[1]):
                row     = {'Image':image,'Number':words[1], 'Position':1,'Location':i}          
                lst_.append(row)
                temp.append(words[1])

        address = pd.DataFrame(lst_, columns=['Image','Number','Position','Location'])
        
        if (((type =='S') and (len(address)==2)) or ((type =='L') and (len(address)==4))):
            break
    
    ###################################################################################################
    # Get the coordinates of the aadhaar number from the image based on the identified address location
    ###################################################################################################
    if (temp != []):  
        
        lst_ = []
    
        if (len(address) <= 2):            
            for i in range(n_boxes):
                if (i==address['Location'][0]) or (i==address['Location'][1]):
                    cords.append((text['left'][i], text['top'][i], text['width'][i], text['height'][i]))
                        
        if (len(address) == 3) and (type == '2P'):
            new_row = {'Image':image, 'Number':number}  
            lst_.append(new_row)
                        
        if (len(address) == 3) and (type != '2P'):
            for i in range(n_boxes):
                if (i==address['Location'][0]) or (i==address['Location'][1]) or (i==address['Location'][2]):
                    cords.append((text['left'][i], text['top'][i], text['width'][i], text['height'][i]))

            #####################################################
            # Create the missing 4th coordinate for each image
            ######################################################     
            
            if address['Position'][2] == 1:
                new_y   = cords[2][1] + cords[0][1] - cords[1][1]
                new_x   = cords[2][0] - 39
            else:
                new_y   = cords[2][1] + cords[1][1] - cords[0][1]
                new_x   = cords[2][0] + 39

            cords.append((new_x,new_y,0,0))

        #if (len(address) == 4) and (type == '2P'):
        #    new_row = {'Image':image, 'Number':number}  
        #    lst_.append(new_row)
        #    #cordErr = cordErr.append(new_row, ignore_index=True)
         
        if (len(address) == 4):
            
            #print('INSIDE')
            
            if (type != '2P'):
                for i in range(n_boxes):
                    if (i==address['Location'][0]) or (i==address['Location'][1]) or (i==address['Location'][2]) or (i==address['Location'][3]):
                        cords.append((text['left'][i], text['top'][i], text['width'][i], text['height'][i]))
           
            if (type == '2P'):
                new_row = {'Image':image, 'Number':number}                           
                #cordErr = cordErr.append(new_row, ignore_index=True)
                lst_.append(new_row)

        #if (len(address) == 3) and (type != '2P'):
        #    for i in range(n_boxes):
        #        if (i==address['Location'][0]) or (i==address['Location'][1]) or (i==address['Location'][2]) or (i==address['Location'][3]):
        #            cords.append((text['left'][i], text['top'][i], text['width'][i], text['height'][i]))
        
        if (len(address) == 5) and (type == '2P'):
            for i in range(n_boxes):
                if (i==address['Location'][0]) or (i==address['Location'][1]) or (i==address['Location'][2]) or (i==address['Location'][3]) or (i==address['Location'][4]):
                    cords.append((text['left'][i], text['top'][i], text['width'][i], text['height'][i]))
            
            findCordFor = 0
            NumCount    = Counter(address['Number'])
            cords       = []
            
            ################################### 
            # Identify which of word is missing
            ################################### 
            
            if (NumCount[words[0]] < NumCount[words[1]]):
                findCordFor = words[0]
                pos = 0
                
            if (NumCount[words[0]] > NumCount[words[1]]):
                findCordFor = words[1]
                pos = 1
                
            ###################################
            # Create the missing 6th coordinate  
            ###################################   

            if ((findCordFor == words[0]) and (findCordFor != 0)):
                found = address.set_index('Number').index.get_loc(findCordFor)
                
                if found[0] == True:  # Checking locations 0,2,4
                    if found[2] != True:
                        loc = 2
                    else:
                        if found[4] != True:
                            loc = 4
                else:
                    loc = 0
                    
                new_row = {'Image':image, 'Number':findCordFor, 'Position':pos, 'Location':address['Location'][loc]-1}                           
                lst_.append(new_row)
                
            if ((findCordFor == words[1]) and (findCordFor != 0)):
                found = address.set_index('Number').index.get_loc(findCordFor)
                
                if found[1] == True:  # Checking Locations 1,3,5
                    if found[3] != True:
                        loc = 3
                    else:
                        loc = 5
                else:
                    loc = 1
                 
                new_row = {'Image':image, 'Number':findCordFor, 'Position':pos, 'Location':address['Location'][loc-1]+1}                           
                lst_.append(new_row)
                
            #address = address.append(new_row, ignore_index=True)
            address = pd.DataFrame(lst_, columns=['Image','Number','Position','Location'])
            address = address.sort_values('Location')
            address = address.reset_index(drop=True)

        if (len(address) == 6) and (type == '2P'):
            for i in range(n_boxes):
                if (i==address['Location'][0]) or (i==address['Location'][1]) or (i==address['Location'][2]) or (i==address['Location'][3]) or (i==address['Location'][4]) or (i==address['Location'][5]):
                    cords.append((text['left'][i], text['top'][i], text['width'][i], text['height'][i]))

        ##########################################
        # Set the font,color and size for masking    coco
        ##########################################
        
        if ((len(address) == 2) and (type != '2P')):
            font     = cv2.FONT_HERSHEY_TRIPLEX
            lineType = 4
            fontScale  = 0.4
            fontColor   = (0,0,0)
            thickness   = 5
            
            cords1   = (cords[0][0],cords[0][1]+5)  # adjust the height to overwrite mask char
            cords2   = (cords[1][0],cords[1][1]+5)  # adjust the height to overwrite mask char
           
            cv2.putText(img, 'XXXX', cords1, font, fontScale, fontColor, thickness, lineType)
            cv2.putText(img, 'XXXX', cords2, font, fontScale, fontColor, thickness, lineType)
            
            if (type != '2P'):
                cv2.imwrite(path +'Mask_'+image,img)



        if (((len(address) == 3) or (len(address) == 4)) and (type != '2P')): # coco
            
            #font     = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
            lineType = 15
            font        = cv2.FONT_HERSHEY_TRIPLEX
            fontScale1  = 2.75
            fontScale2  = 2.0
            fontColor   = (0,0,0)
            lineType2   = 10

                     
            cords1   = (cords[0][0],cords[0][1]+56)  # adjust the height to overwrite mask char
            cords2   = (cords[1][0],cords[1][1]+56)  # adjust the height to overwrite mask char
            cords3   = (cords[2][0],cords[2][1]+36)  # adjust the width to overwrite mask char
            cords4   = (cords[3][0],cords[3][1]+36)  # adjust the width to overwrite mask char
           
            cv2.putText(img, 'XXXX', cords1, font, fontScale1, fontColor, lineType)
            cv2.putText(img, 'XXXX', cords2, font, fontScale1, fontColor, lineType)
            cv2.putText(img, 'XXXX', cords3, font, fontScale2, fontColor, lineType2)
            cv2.putText(img, 'XXXX', cords4, font, fontScale2, fontColor, lineType2)
            
            if (type != '2P'):
                cv2.imwrite(path +'Mask_'+image,img)
            else:
                new_row = {'Image':image, 'Number':number}                                
                lst_.append(new_row)
                #cordErr = cordErr.append(new_row, ignore_index=True)
                
        if (len(address) == 6):
            #font     = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
            #lineType = 4
            cords1   = (cords[0][0],cords[0][1]+17)  # adjust the height to overwrite mask char
            cords2   = (cords[1][0],cords[1][1]+17)  # adjust the height to overwrite mask char
            cords3   = (cords[2][0],cords[2][1]+13)  # adjust the width to overwrite mask char
            cords4   = (cords[3][0],cords[3][1]+13)  # adjust the width to overwrite mask char
            cords5   = (cords[4][0],cords[4][1]+13)  # adjust the width to overwrite mask char
            cords6   = (cords[5][0],cords[5][1]+13)  # adjust the width to overwrite mask char
            cv2.putText(img, 'XXXX', cords1, font, fontScale1, fontColor, lineType)
            cv2.putText(img, 'XXXX', cords2, font, fontScale1, fontColor, lineType)
            cv2.putText(img, 'XXXX', cords3, font, fontScale2, fontColor, lineType)
            cv2.putText(img, 'XXXX', cords4, font, fontScale2, fontColor, lineType)
            cv2.putText(img, 'XXXX', cords5, font, fontScale2, fontColor, lineType)
            cv2.putText(img, 'XXXX', cords6, font, fontScale2, fontColor, lineType)
            cv2.imwrite(path +'Mask_'+image,img)
            
    
    else:
        lst_    = []
        new_row = {'Image':image, 'Number':number}      
        lst_.append(new_row)
        
    cordErr = pd.DataFrame(lst_, columns=['Image','Number'])
    return(cordErr)


############
# Main Logic
############

def mask():
        
    for track in os.scandir(path):
        if track.is_file():
            img                   = cv2.imread(path+track.name)           
            img                   = cv2.resize(img, (310, 200)) if (track.name[0] == 'S')  else cv2.resize(img, (1300, 2700))
            adhNum,text,adhNumErr = get_number(track.name)
            if (adhNumErr != 'Error'):
                temp                  = [text]
                split_nums            = temp[0].split()
                words                 = [(num_str) for num_str in split_nums]
                cordErr               = maskAadhaar(img,words,track.name,text,track.name[0])

#mask()