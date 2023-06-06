###########################################################################################################################################
# This is the driver program is to showcase the capability to classify various documents (such as aadhaar cards, pan cards, driving licence # and other id's) using the combination of pytesseract and regular expression.Segerate aadhaar cards and non-aadhaar cards into seperate 
# folder and then mask the first EIGHT numbers of all aadhaar cards. 
###########################################################################################################################################

import pandas as pd
from tkinter import * 
from PIL import ImageTk, Image  
import numpy as np
import tkinter as tk
from tkinter import Tk, Frame, Label, Button, filedialog, messagebox
import os 
import PIL
from PIL import ImageTk, Image
import cv2
import matplotlib.pyplot as plt
import math
import datetime
import time
import pytesseract
from pdf2image import convert_from_path
from imutils import resize
import re
import shutil
import warnings
warnings.filterwarnings('ignore')

from MaskAadhaar import *

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
path = 'C:/Users/sriha/Desktop/'
os.chdir(path)

###################################
# Routine to identify the file Type 
###################################
def check_filetype(filename):
    global image_file_types
    image_file_types = ['.jpeg','.jpg','.png'] 
    if os.path.splitext(filename)[-1].lower() == '.pdf':
        return 'pdf'
    elif os.path.splitext(filename)[-1].lower() in image_file_types:
        return os.path.splitext(filename)[-1].lower()
    else:
        return 'Unknown'

########################################################
# Routine to identify the num pattern in Aadhaar and pan
########################################################
def num_pattern(text):
    pan_num   = re.findall(r'[a-z]{5}[0-9]{4}[a-z]',text)
    adhr_num  = re.findall((r'\d{4} ?\d{4} ?\d{4}'),text)
    
    if pan_num != [] and adhr_num != []:
        return 'Unkown'
    elif pan_num != []:
        return 'PanCard'
    elif adhr_num != []:
        return 'AadhaarCard'
    else:
        return 'Unkown'

###############################
# Routine to check word pattern
############################### 
def words_pattern(text):
    adhr_pattern_short_words = ['government','male','female','dob']
    adhr_pattern_long_words  = ['unique','identification','authority','address:','d/o','c/o']
    pan_pattern_words        = ['income', 'tax', 'permanent', 'account']
    Driving_licence_words    = ['indian','union','driving','licence','department','transport','state','issued','valid','sign','owner','post','holder']
    posidex_id_card          = ['posidex','ptpl','emp','id']
    
    adhr_short_words     =  [x in text.split() for x in adhr_pattern_short_words ]
    adhr_long_words      =  [x in text.split() for x in adhr_pattern_long_words]
    pan_words            =  [x in text.split() for x in pan_pattern_words]
    Dl_words             =  [x in text.split() for x in   Driving_licence_words]
    psx_id_words         =  [x in text.split() for x in  posidex_id_card] 

    
    # Count the number of True values in each condition
    counts = [sum(adhr_short_words), sum(adhr_long_words), sum(pan_words), sum(Dl_words),sum(psx_id_words )]
   
    
    # Get the index of the condition with the most True values
    max_index = counts.index(max(counts))
    
    
    if max_index == 0:
        return 'AadhaarShort'
    elif max_index == 1:
        return 'Aadhaarback'
    elif max_index == 2:
        return 'PanCard'
    elif max_index == 3:
        return 'Driving_licence'
    elif max_index == 4:
        return 'Posidex_ID'
    else:
        return 'Unknown'

###############################
# Routine to classify the image
############################### 
def classify_documents(img):

    # resize image
    img      = resize(img, width = 500)
    img_mode = Image.fromarray(img)
    img      = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img_mode.mode == 'RGB' else img
    
    ret, simpleimg    = cv2.threshold(img,127,255,cv2.THRESH_BINARY) 
    ret, truncatedimg = cv2.threshold(img, 125, 255, cv2.THRESH_TRUNC)
   
    simth_text     = pytesseract.image_to_string(simpleimg,lang='eng',config='--psm 11')
    truncth_text   = pytesseract.image_to_string(truncatedimg,lang='eng',config='--psm 11')
    grey_text      = pytesseract.image_to_string(img,lang='eng',config='--psm 6')
    text2          = pytesseract.image_to_string(truncatedimg,lang='eng',config='--psm 6')
    final_text     =  text2+grey_text+truncth_text+simth_text 
    final_text     =  final_text.lower()
 
    #Check Pan Identification Conditions
    num_check  =num_pattern(final_text)
    word_check = words_pattern(final_text)
   
    if num_check == 'PanCard' or word_check == 'PanCard' :
        return 'PanCard'
    if num_check == 'AadhaarCard' and img.shape[0]>img.shape[1]:
        return 'Long Aadhaar'
    if num_check == 'AadhaarCard' and  word_check == 'AadhaarShort':
        return 'Aadhaar Card'
    if num_check == 'AadhaarCard' and  word_check == 'Aadhaarback':
        return 'Aadhaar Card'
    if word_check == 'Driving_licence':
        return 'Driving licence'
    if word_check == 'Posidex_ID':
        return 'Posidex ID'
    else:
        return 'Unknown'


# ### GUI ##

# In[3]:


def classify_mask():
    root = Tk()
    root.geometry('+%d+%d'%(500,10))
    root.iconbitmap(r'C:\Users\sriha\Documents\My_Data\Work_Documents\Posidex\Video_KYC\Demo\psx.ico')
    Psx_img = ImageTk.PhotoImage(Image.open('C:/Users/sriha/Documents/My_Data/Work_Documents/Posidex/Identify_Name/psx.png'))  
    root.title('Document Masking')
        
    header = Frame(root, width=900, height=190, bg="white")
    header.grid(columnspan=3, rowspan=2, row=0)

    head_title = Label(root, text="Document  Classification  And  Number  Masking", bg='#FFFFFF', fg='#004488',font=('Poppins', 20, "bold"))
    head_title.place(x=225, y=100)

    head_title_2 = Label(root,text = "POSIDEX",bg ='#FFFFFF',fg= '#004488', font = ('sans-serif',34,"bold") )
    head_title_2.place(x=0,y=139, height=38)
    
    pos_logo = Label(root, image=Psx_img)
    pos_logo.place(x=0, y=1)

    time = Label(root, text=f"{'{0:%d-%m-%Y %H:%M %p}'.format(datetime.datetime.now())}", bg='#FFFFFF',fg='#004488',font=('Poppins', 12, "bold"))
    time.place(x=735, y=-1)

    main_content = Frame(root, highlightbackground="#f80", highlightcolor="#f80", highlightthickness=2, width=900,height=300, bg="#048")
    main_content.grid(columnspan=3, rowspan=2, row=2)

    image_display = Label(root)
    image_display.place(x=100, y=400)

    def open_folder():
        foldername = filedialog.askdirectory(initialdir=os.getcwd(), title="Select folder")
        
        if os.path.exists('Aadhar_cards'):
            destination_folder = path+'Aadhar_cards'
            os.path.join(path+'Aadhar_cards')
            filesToRemove = [os.path.join(destination_folder,f) for f in os.listdir(destination_folder)]
            for f in filesToRemove:
                os.remove(f) 
        if os.path.exists('Other_cards'):
            destination_folder = path+'Other_cards'
            os.path.join(path+'Other_cards')
            filesToRemove = [os.path.join(destination_folder,f) for f in os.listdir(destination_folder)]
            for f in filesToRemove:
                os.remove(f) 
        
        classify_folder(foldername)

    def classify_folder(foldername):
        num_cards = 0
        start_time = datetime.datetime.now()
        for filename in os.listdir(foldername):
            filepath = os.path.join(foldername, filename)
            classify_file(filepath)
            num_cards += 1
        end_time = datetime.datetime.now()

        messagebox.showinfo("Document ", f"Classification completed for {num_cards} cards.")

    def classify_file(filename):
        
        file_type = check_filetype(filename)
        if file_type in image_file_types:
            img = cv2.imread(filename)
            classification = classify_documents(img)

            if classification in ['Aadhaar Card', 'Long Aadhaar']:
                destination_folder = 'Aadhar_cards'
            else:
                destination_folder = 'Other_cards'
                
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            
            destination_path = os.path.join(destination_folder, os.path.basename(filename))
            shutil.copy(filename, destination_path)
            Masking_button['state'] = NORMAL
        else:
            print("Unknown file type")

    def Clear():
        root.destroy()
        start()

    def execute():
        mask()
        root.destroy()
        
    def Exit():
        root.destroy()

    Masking_button = Button(root, text="Document Masking", command=execute,font=('Poppins', 15),relief=RAISED,bd = 6,bg ='#FFFFFF',fg= '#004488')
    Masking_button.place(x=500, y=225)

    upload_folder_button = Button(root, text="Select Folder", command=open_folder, font=('Poppins', 15),relief=RAISED,bd = 6,bg ='#FFFFFF',fg= '#004488')
    upload_folder_button.place(x=50, y=225)

    clear = Button(root, text='Clear', command=Clear, font=('Poppins', 15),relief=RAISED,bd = 6,bg ='#FFFFFF',fg= '#004488')
    clear.place(x=50, y=370)

    exit = Button(root, text='Exit', command=Exit, font=('Poppins', 15),relief=RAISED,bd = 6,bg ='#FFFFFF',fg= '#004488')
    exit.place(x=500, y=370)
    exit.config(height=1, width=5)

    Masking_button['state'] = DISABLED
    root.mainloop()

classify_mask()

