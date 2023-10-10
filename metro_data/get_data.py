import platform
import os
import http.client, urllib.request, urllib.parse, urllib.error, json, time 
import pandas as pd
from PIL import ImageFont # image
from PIL import Image # image
from PIL import ImageDraw # image

### Inputs
# Station code the board will display
board_station = 'A03' # dupont circle 

# WMATA API key
api_key = open("wmata_key.txt", "r") 
WMATA_KEY = api_key.read()
headers = {
    'api_key': WMATA_KEY
    }

### Functions
# Get predictions from api
def get_preds(StationCode):

    # params
    params = { 
        'StationCodes': StationCode
        }
    try:
        conn = http.client.HTTPSConnection('api.wmata.com')
        conn.request("GET", "/StationPrediction.svc/json/GetPrediction/" + params['StationCodes'] ,"{body}", headers)
        response = conn.getresponse()
        data = response.read()
        return(json.loads(data))
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

# Control font switches between debuging on mac and raspberrypi
def get_font():
    platform_name = platform.system()
    if platform_name == 'Linux': # raspberry pi os
        font = ImageFont.truetype('FreeMono.ttf', 8)
    elif platform_name =='Darwin': # mac os
        font = ImageFont.truetype("Arial.ttf",15)
    return(font)

### Lookups
# lookup table for spelling changes. Do this so text fits on screen at 8pt font
line_lookup = {'Brnch Av' : 'BrchAv',
               'Ft.Tottn' : 'Ft.Ttn',
               'Glenmont' : 'Glnmnt',
               'Shady Gr' : 'ShdyGr',
               'NewCrltn' : 'NwCrtn',
               'Wiehle'   : 'Wiehle',
               'Largo'    : 'Largo',
               'Vienna'   : 'Vienna',
               'Grnbelt'  : 'Grnblt',
               'Hntingtn' : 'Hntngn'}

# lookup table for boarding and arriving code changes
code_lookup = {'ARR' : 'A',
               'BRD' : 'B'}

### Run program
img_output = os.getcwd() + "/board_image/preds.png"
lines_to_print = 3 # anything less than 4 will fit

# get preds
pred_data = get_preds(board_station)['Trains']
# check if data is present. If not make blank screen
if len(pred_data) == 0:
    img=Image.new("RGBA", (64,32),(0,0,0)) # mode, size, color
    draw = ImageDraw.Draw(img)
    img.save(img_output)
# if data is present, print on screen
else: 
    pred_keys = pred_data[0].keys() 
    # intialize list
    board_text = []
    destinations = []
    mins = []
    # print between 1 and 3 lines depending on number of trains
    for i in range(0,3):
        # change names based on lookup to fit nicely on the board
        if pred_data[i]['Destination'] in list(line_lookup.keys()):
            destinations.append(line_lookup[pred_data[i]['Destination']])
        # change boarding/arriving codes code to fit on board
        if pred_data[i]['Min'] in list(code_lookup.keys()):
            mins.append(code_lookup[pred_data[i]['Min']])
        # build text string
        text = pred_data[i]['Line'] + '|' + pred_data[i]['Destination']  + '|' + pred_data[i]['Min']
        # retain
        print(text)
        board_text.append(text)
    # create image through PIL
    img=Image.new("RGBA", (64,32),(0,0,0)) # mode, size, color
    draw = ImageDraw.Draw(img) # draw blank image
    draw.text((1, 0), '\n'.join(board_text) ,(255,255,255), font = get_font()) # add text to image
    draw = ImageDraw.Draw(img) # redraw image with text
    img.save(img_output) # save image