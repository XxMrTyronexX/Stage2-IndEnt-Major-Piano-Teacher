#imports for GUI
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *

#imports for system functions (time checking, file reading)
from datetime import datetime
import time
import sys
import os

#import to read and interperate MIDI files
import pretty_midi

#import to control LED strip
from rpi_ws281x import *


app = QApplication(sys.argv)

#making a variable which represents the window
window = QWidget() 

#setting the window title, coordinates, size and background
window.setWindowTitle("Music Selector") 
window.move(0,0)
window.setFixedSize(800,480)
window.setStyleSheet("background: #b3cde0;") 

#making a variable to store the flags that i would like to assign to the window (to get rid of the border) and assigning it
flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
window.setWindowFlags(flags)

#making a variable to represent a grid layout (that I will assign to the window when i finish adding widgets to it)
grid = QGridLayout()

#creating a global dictionary with empty values which will be used to store widgets (so they can be accessed from anywhere in the document
widgets = {
        "button": [],
        "begin_button": [],
        "back_button": [],
        "refresh_button": [],
        "logo": [],
        "small_logo": [],
        "list_of_songs": [],
        "song_info": [],
        "playback_speed": [],
        "spacer": [],
        "rewind_button": [],
        "fast_forward_button": [],
        "pause_button": [],
        "rewind_icon": [],
        "fast_forward_icon": [],
        "pause_icon": [],
        "time_of_song": [],
        "back_button_frame3": []
        }

song_information = {
        "directory": [],
        "selected_song_directory": [],
        "selected_playback_speed": [],
        "selected_song_minutes": [],
        "selected_song_seconds": [],
        "full_time": [],
        "selected_playback_minutes": [],
        "selected_playback_seconds": [],
        "midi_data_of_selected_song": [],
        "note_pitch": [],
        "note_start": [],
        "note_end": [],
        "note_played": [],
        "note_stopped": [],
        "start_time": [0],
        "time_elapsed": [0],
        "is_paused": [],
        "time_paused": [0],
        "time_played": [0]
        }

#creating a timer - a special kind of loop which runs in the background so we can do other things while it runs (makes use of multithreading)
song_timer = QTimer()

#setting variables to store the information about the LED strip
LED_COUNT      = 144      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 65     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

#Creating an object used to represent my LED lights and giving it information about the LED lights (specified above)
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

#this has to run before any commands are made to the LED lights
strip.begin()

#making a function that sets up the first page
def frame1():
	#setting image location and size
	image = QPixmap("logo.png").scaled(700, 700, QtCore.Qt.KeepAspectRatio)
	
	#making a variable with an empty label assigned to it
	logo = QLabel()
	
	#pointing the label inside of the logo variable to the direction of the image's logation
	logo.setPixmap(image)
	
	#setting the position of the logo
	logo.setStyleSheet("margin-bottom: 120px;")
	logo.setAlignment(QtCore.Qt.AlignCenter)

        #appending the logo widget to a global dictionary so we can access it outside of the function
	widgets["logo"].append(logo)
	
	
	#adds the widget to the gui (widget, start row, start column, end row, end column), getting it from the dictionary instead of locally so we can edit it from other functions
	grid.addWidget(widgets["logo"][0], 0, 0, 2, 0)
	
	
	#Creating the button and assigning it to a variable called button
	button = QPushButton("Select from song Midi")
	
	#On hover, the mouse will change to a pointing icon
	button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        #runs a function to move to the next page
	button.clicked.connect(show_frame2)
	
	#setting the css properties (changing the way it looks)
	button.setStyleSheet(
		"*{border: 4px solid '#1261A0';" +
		#"background: '#3895D3';" +
		"border-radius: 45px;" +
		"font-size: 35px;" +
                "background: '#dbe7f0';" +
		"font-family: Arial, Helvetica, sans-serif;" +
		"color: 'black';" +
		"padding: 30px 0;" +
		"margin: 100px 50px;}" +
		"*:hover{background: '#3895D3';}"
		)
	
        #appending to a global dictionary
	widgets["button"].append(button)
	
	#adding the logo to the grid
	grid.addWidget(widgets["button"][0], 1, 0, 3, 0)

	
#sets up frame 2selected_playback_speed
def frame2():

    #creating objects
    image = QPixmap("logo.png").scaled(130, 130, QtCore.Qt.KeepAspectRatio)
    logo = QLabel()
    logo.setPixmap(image)
    list_of_songs = QListWidget()
    playback_speed = QComboBox()
    begin_button = QPushButton("Begin")
    refresh_button = QPushButton("Refresh")
    back_button = QPushButton("Back")
    song_info = QLabel("<strong>Song Name: <br><br><br>Duration: <br><br><br>File Size: <br><br><br>Creation Date:<strong>")
    spacer = QLabel("")
    
    #setting the css properties (changing the way it looks)
    list_of_songs.setStyleSheet(
        "*{border: 2px solid 'black';" +
	"background: '#FFFFFF';" +
	"border-radius: 0px;" +
	"font-size: 20px;" +
	"font-family: Arial, Helvetica, sans-serif;" +
	"color: 'black';" +
	"padding: 0px 0px;" +
	"margin: 0px 0px;" +
        "margin-right: 0px;}"
	)
    list_of_songs.setWordWrap(True)

    song_info.setStyleSheet(
        "*{border-radius: 0px;" +
	"font-size: 20px;" +
	#"font-family: Arial, Helvetica, sans-serif;" +
        #"font-weight: bold;" +
	"color: 'black';" +
	"padding: 0px;" +
        "margin-top: 40px;" +
        "margin-right: 0px;}"
	)
    song_info.setAlignment(QtCore.Qt.AlignTop)
    song_info.setWordWrap(True)
    
    begin_button.setStyleSheet(
		"*{border: 2px solid '#1261A0';" +
                "background: '#dbe7f0';" +
                "border-radius: 10px;" +
		"font-size: 20px;" +
		"font-family: Arial, Helvetica, sans-serif;" +
		"color: 'black';" +
                "padding: 5px 30px;" +
		"margin: 20px 20px;}" +
                "*:hover{background: '#3895D3';}"
		)

    refresh_button.setStyleSheet(
		"*{border: 2px solid '#1261A0';" +
                "background: '#dbe7f0';" +
                "border-radius: 10px;" +
		"font-size: 15px;" +
		"font-family: Arial, Helvetica, sans-serif;" +
		"color: 'black';" +
                "margin-left: 30px;" +
                "margin-right: 0px;" +
                "padding: 5px 0;}" +
                "*:hover{background: '#3895D3';}"
		)

    back_button.setStyleSheet(
		"*{border: 2px solid '#1261A0';" +
                "background: '#dbe7f0';" +
                "border-radius: 10px;" +
		"font-size: 15px;" +
		"font-family: Arial, Helvetica, sans-serif;" +
		"color: 'black';" +
                "margin-left: 10px;" +
                "margin-right: 40px;" +
                "padding: 5px 25px;}" +
                "*:hover{background: '#3895D3';}"
		)

    logo.setAlignment(QtCore.Qt.AlignRight)
    
    playback_speed.addItem("1x Speed", 1)
    playback_speed.addItem("0.9x Speed", 0.9)
    playback_speed.addItem("0.8x Speed", 0.8)
    playback_speed.addItem("0.7x Speed", 0.7)
    playback_speed.addItem("0.6x Speed", 0.6)
    playback_speed.addItem("0.5x Speed", 0.5)
    playback_speed.addItem("0.4x Speed", 0.4)
    playback_speed.addItem("0.3x Speed", 0.3)
    playback_speed.addItem("0.2x Speed", 0.2)
    playback_speed.addItem("0.1x Speed", 0.1)
    playback_speed.setStyleSheet(
		"*{background: '#dbe7f0';" +
                "padding: 1px;" +
		"font-size: 15px;" +
		"font-family: Arial, Helvetica, sans-serif;}"
		)

    #this has to be done after adding the list items (i dont know why)
    playback_speed.setEditable(True)
    playback_speed.lineEdit().setAlignment(QtCore.Qt.AlignCenter)
    playback_speed.setCurrentIndex(-1)
    playback_speed.setCurrentText("Select Playback Speed")
    playback_speed.lineEdit().setReadOnly(True)
    
    spacer.setStyleSheet("margin: 0px 110px;")

    #setting the functions for each widget
    begin_button.clicked.connect(show_frame3)
    refresh_button.clicked.connect(refresh_songs)
    back_button.clicked.connect(show_frame1)
    list_of_songs.itemClicked.connect(extract_selected_song)
    playback_speed.currentIndexChanged.connect(lambda:store_selected_playback_speed(playback_speed.currentData()))
    
    
    #adding placeholder text
    """playback_speed.setEditable(True)
    playback_speed.setCurrentIndex(-1)
    playback_speed.setCurrentText("Playback Speed")"""
    
    #assigning objects to the global dictionary
    widgets["list_of_songs"].append(list_of_songs)
    widgets["small_logo"].append(logo)
    widgets["song_info"].append(song_info)
    widgets["playback_speed"].append(playback_speed)
    widgets["begin_button"].append(begin_button)
    widgets["back_button"].append(back_button)
    widgets["refresh_button"].append(refresh_button)
    widgets["spacer"].append(spacer)
    
    #runs a method which lists all MIDI files on the usbs plugged into the pi
    refresh_songs()
    
    #adds the widgets to the gui (widget, start row, start column, end row, end column)
    grid.addWidget(widgets["list_of_songs"][0], 0, 0, 0, 1)
    grid.addWidget(widgets["small_logo"][0], 0, 3)
    grid.addWidget(widgets["song_info"][0], 0, 1, 0, 3)
    grid.addWidget(widgets["playback_speed"][0], 6, 2)
    grid.addWidget(widgets["begin_button"][0], 7, 2)
    grid.addWidget(widgets["back_button"][0], 8, 1)
    grid.addWidget(widgets["spacer"][0], 8, 2)
    grid.addWidget(widgets["refresh_button"][0], 8, 3)

    #IMPORTANT NOTE: what ever gets added to the grid last is on top if they overlap

def frame3():
    
    #creating objects
    image = QPixmap("logo.png").scaled(130, 130, QtCore.Qt.KeepAspectRatio)
    logo = QLabel()
    logo.setPixmap(image)

    rewind_image = QPixmap("./buttons/rewind_icon.png").scaled(150, 150, QtCore.Qt.KeepAspectRatio)
    rewind_icon = QLabel()
    rewind_icon.setPixmap(rewind_image)

    fast_forward_image = QPixmap("./buttons/fast_forward_icon.png").scaled(150, 150, QtCore.Qt.KeepAspectRatio)
    fast_forward_icon = QLabel()
    fast_forward_icon.setPixmap(fast_forward_image)
    
    play_image = QPixmap("./buttons/play_icon.png").scaled(200, 200, QtCore.Qt.KeepAspectRatio)
    pause_icon = QLabel()
    pause_icon.setPixmap(play_image)

    #calculating the duration of the song based on the slected playback speed
    total_time = song_information["full_time"][0]/song_information["selected_playback_speed"][0]
    minutes = str(round(total_time//60))
    seconds = str(round(total_time%60))

    
    #if the seconds is 1 digit, add 0 in front of it
    if(len(seconds) == 1):
        seconds = "0" + seconds
    
    pause_button = QPushButton("Pause")
    time_of_song = QLabel("0:00 / " + minutes + ":" + seconds)

    spacer = QLabel("")
    
    back_button = QPushButton("Back")
    rewind_button = QPushButton("")
    fast_forward_button = QPushButton("")
    pause_button = QPushButton("")
    
    
    #setting css properties
    rewind_button.setStyleSheet(
	"*{background-color: rgba(255, 255, 255, 0);"
        "border-radius: 70px;" +
        "margin-right: 608px;" +
        "margin-left: 24px;" +
        "margin-top: 0px;" +
        "margin-bottom: 0px;" +
        "padding: 66px 0px;}" +
        "*:hover{background: rgba(56, 149, 211, 0.7);}"
	)

    fast_forward_button.setStyleSheet(
	"*{background-color: rgba(255, 255, 255, 0);"
        "border-radius: 70px;" +
        "margin-right: 29px;" +
        "margin-left: 105px;" +
        "margin-top: 0px;" +
        "margin-bottom: 0px;" +
        "padding: 66px 0px;}" +
        "*:hover{background: rgba(56, 149, 211, 0.7);}"
	)

    pause_button.setStyleSheet(
	"*{background-color: rgba(255, 255, 255, 0);"
        "border-radius: 0px;" +
        "margin-right: 0px;" +
        "margin-left: 127px;" +
        "margin-top: 0px;" +
        "margin-bottom: 0px;" +
        "padding: 85px 0px;}" 
	)
    
    rewind_icon.setStyleSheet(
	"*{border-radius: 73px;" +
        "margin-left: 20px;" +
        "margin-right: 0px;" +
        "margin-top: 0px;" +
	"margin-bottom: 0px}"
	)
    #rewind_icon.setAlignment(QtCore.Qt.AlignBottom)
    
    fast_forward_icon.setStyleSheet(
	"*{border-radius: 73px;" +
        "margin-left: 107px;" +
        "margin-right: 0px;" +
        "margin-top: 0px;" +
	"margin-bottom: 0px}" 
	)
    
    pause_icon.setStyleSheet(
	"*{padding: 0px 0px;" +
        "margin-left: 127px;" +
        "margin-right: 0px;" +
        "margin-top: 0px;" +
	"margin-bottom: 0px}" 
	)

    back_button.setStyleSheet(
	"*{border: 2px solid '#1261A0';" +
        "background: '#dbe7f0';" +
        "border-radius: 10px;" +
	"font-size: 15px;" +
	"font-family: Arial, Helvetica, sans-serif;" +
	"color: 'black';" +
        "margin-bottom: 405px;" +
        "margin-right: 100px;" +
        "padding: 5px 10px;}" +
        "*:hover{background: '#3895D3';}"
	)
    
    time_of_song.setStyleSheet(
        "*{border-radius: 0px;" +
	"font-size: 30px;" +
	"font-family: Arial, Helvetica, sans-serif;" +
        "font-weight: bold;" +
	"color: 'black';" +
        "margin-top: 170px;" +
        "margin-right: 0px;" +
        "margin-left: 285px;" +
        "margin-bottom: 0px;" +
	"padding: 0px;}"
	)
    time_of_song.setAlignment(QtCore.Qt.AlignCenter)

    spacer.setStyleSheet(
        "*{border-radius: 0px;" +
        "margin-top: 200px;" +
	"padding: 0px 0px;}"
	)
    
    #setting the functions for each widget
    rewind_button.clicked.connect(rewind)
    fast_forward_button.clicked.connect(fast_forward)
    pause_button.clicked.connect(play_pause)
    back_button.clicked.connect(back_from_song)
    
    #assigning objects to the global dictionary 
    widgets["rewind_button"].append(rewind_button)
    widgets["rewind_icon"].append(rewind_icon)
    widgets["fast_forward_button"].append(fast_forward_button)
    widgets["fast_forward_icon"].append(fast_forward_icon)
    widgets["pause_button"].append(pause_button)
    widgets["pause_icon"].append(pause_icon)
    widgets["time_of_song"].append(time_of_song)
    widgets["small_logo"].append(logo)
    widgets["back_button_frame3"].append(back_button)
    widgets["spacer"].append(spacer)
    song_information["selected_playback_minutes"].append(minutes)
    song_information["selected_playback_seconds"].append(seconds)

    #adding the widgets to the gui (widget, start row, start column, end row, end column)
    grid.addWidget(widgets["spacer"][0], 1, 0, 1, 2)
    grid.addWidget(widgets["time_of_song"][0], 3, 0, 3, 2)
    grid.addWidget(widgets["back_button_frame3"][0], 0, 0, 0, 1)
    grid.addWidget(widgets["rewind_icon"][0], 2, 0, 2, 0)
    grid.addWidget(widgets["rewind_button"][0], 2, 0, 2, 0)
    grid.addWidget(widgets["fast_forward_icon"][0], 2, 2, 2, 2)
    grid.addWidget(widgets["fast_forward_button"][0], 2, 2, 2, 2)
    grid.addWidget(widgets["pause_icon"][0], 2, 1, 2, 1)
    grid.addWidget(widgets["pause_button"][0], 2, 1, 2, 1)

    
    #setting up song data wtih selected directory
    midi_data = pretty_midi.PrettyMIDI(song_information["selected_song_directory"][0])#creating objects

    #midi_data = pretty_midi.PrettyMIDI("test.mid")
    
    #clearing arrays storing notes from previous song
    if song_information["note_pitch"] != []:
        song_information["note_pitch"].clear()

    if song_information["note_start"] != []:
        song_information["note_start"].clear()

    if song_information["note_end"] != []:        
        song_information["note_end"].clear()

    notes_file = open("notes.txt", "w+")
    
    #initialises a variable global to the for loop so we can use it to store how many loops have passed (to be used to calculate the loading progress percentage)
    i = 0
    
    #putting the notes into arrays stored in a dictionary and rounding the timings to 2 decimal places (10ms) and dividing it by the selected playback speed
    for instrument in midi_data.instruments:
        #print("instrument:", instrument.program)
        for note in instrument.notes:
            song_information["note_pitch"].append(note.pitch)
            song_information["note_start"].append(round(note.start/song_information["selected_playback_speed"][0], 2))
            song_information["note_end"].append(round(note.end/song_information["selected_playback_speed"][0], 2))
            
            #incraments the value and uses it as an argument in the function used to turn on the lights based on the percentage of loading
            i=i+1
            loading(i*100, len(instrument.notes)*len(midi_data.instruments))
    
    
    #makes the light flash green 3 times to tell the user that the loading has completed
    for i in range(0,4):
        for lights in range(0, LED_COUNT):
            strip.setPixelColor(lights, Color(0,255,0))
            
        time.sleep(0.1)
        strip.show()
        time.sleep(0.1)
        clear_lights_hard()
    
    """
    while True:
        timing = timing + 0.01
        timing = round(timing, 2)
        time.sleep(0.01)
        print(timing)
        
        if timing > 10.0:
            break"""

def loading(current_value, end_value):
    
    try:
        #gets the percentage of loading progress
        percentage = (current_value/end_value)*100
        
        #calculates how much percentage is left, the higher it is, then the higher the red value will be
        red_value = round(((100-percentage)/100)*255)
        
        #calculates how much percentage has passed, the higher it is, then the higher the green value will be
        green_value = round((percentage/100)*255)
        
        #turns on the percentage of lights equal to the percentage that has passed (eg: 30% has passed so 30% of the lights will turn on), the lower the percentage than the more red they'll be and the higher the percentage the more green they'll be
        for lights in range(0, round((percentage/100)*LED_COUNT)):
            strip.setPixelColor(lights, Color(red_value,green_value,0))

        strip.show()
    
    #the integers exceed the amount of integers that can be parsed to the C code used to make this python library (i think) so this ignores the error (so the program does not crash) so the program can continue
    except OverflowError:
        pass

#function which checks to see if a note needs to be played or stopped, using a  QTimer loop so it runs as a background process
def play_song():
    
    #if the start time is 0, set it to the current time
    if song_information["start_time"][0] == 0:
            song_information["start_time"][0] = round(time.time(), 2)

    #calculates the difference between the start time and the current time and rounds it to 2 decimal places
    current_time = round(time.time() - song_information["start_time"][0], 2)

    #calculating the time elapsed in minutes and seconds, and converting it to a string to show to the user
    minutes = str(round(current_time//60))
    seconds = str(round(current_time%60))

    #if the seconds is 1 digit, add 0 in front of it
    if(len(seconds) == 1):
        seconds = "0" + seconds

    #calculating the total time of the song based on the user's selected playback speed
    total_time = song_information["full_time"][0]/song_information["selected_playback_speed"][0]
    total_minutes = str(round(total_time//60))
    total_seconds = str(round(total_time%60))

    #if the seconds is 1 digit, add 0 in front of it
    if(len(total_seconds) == 1):
        total_seconds = "0" + total_seconds

    #checks to see if the current time is the same as the time from the previous loop (the code only runs every 10ms and there is no duplicate notes)
    if current_time != song_information["time_elapsed"][0]:

        song_information["time_elapsed"][0] = current_time
        
        #for the amount of entries into the note_pitch array
        for i in range(0, len(song_information["note_start"])):

            #if the current time passed is equal to the time that the note must play
            if(current_time == song_information["note_start"][i]):
                print(str(song_information["note_pitch"][i]) + " start")
                
                #telling the strip which light to turn on (which key it has to light up above) and what colour to light up as
                strip.setPixelColor(song_information["note_pitch"][i], Color(255,255,255))
                strip.show()
                
            #if the current time passed is equal to the time that the note must stop
            if(current_time == song_information["note_end"][i]):
                print(str(song_information["note_pitch"][i]) + " stop")                
                
                #telling the strip which light to turn off
                strip.setPixelColor(song_information["note_pitch"][i], Color(0,0,0))
                strip.show()

    #if the song has ended, turn off all of the lights, return to the previous screen and reset the session
    if(current_time > total_time): 
        back_from_song()
        song_timer.stop()

    #if the song has not ended, keep updating the time
    else:
        #appending a blank label to the dictionary array storing the time elapsed being shown to the user (this to combat an error that i was getting where the array would have nothing in it)    
        widgets["time_of_song"].append(QLabel(""))

        #setting the time elapsed shown on screen to the user
        widgets["time_of_song"][0].setText(minutes + ":" + seconds + " / " + total_minutes + ":" + total_seconds)
    
def clear_lights():
    #turns of each light one by one
    for lights in range(0, LED_COUNT):
        strip.setPixelColor(lights, Color(0,0,0))
        strip.show()

def clear_lights_hard():
    #turns of each light one by one
    for lights in range(0, LED_COUNT):
        strip.setPixelColor(lights, Color(0,0,0))

    strip.show()

def play_pause():

    clear_lights()
    
    #song_timer.setInterval(1000) this would set a delay between each loop
    song_timer.timeout.connect(lambda: play_song())
    
    #if there is nothing in the "is_paused" dictiornary array, set it to true
    if song_information["is_paused"] == []:
        song_information["is_paused"].append(True)

    play_image = QPixmap("./buttons/play_icon.png").scaled(200, 200, QtCore.Qt.KeepAspectRatio)
    pause_image = QPixmap("./buttons/pause_icon.png").scaled(200, 200, QtCore.Qt.KeepAspectRatio)

    #if song is currently paused
    if(song_information["is_paused"][0] == True):

        #change icon
        widgets["pause_icon"][0].setPixmap(pause_image)

        #play the song
        song_timer.start()

        #calculates the time passed since the user paused and adds it to the start time
        song_information["start_time"][0] = song_information["start_time"][0] + (round(time.time(), 2) - song_information["time_paused"][0])

        #change "is_paused" status
        song_information["is_paused"][0] = False

        
    #if song is currently playing
    elif(song_information["is_paused"][0] == False):
            
        #change icon
        widgets["pause_icon"][0].setPixmap(play_image)

        #stop the song
        song_timer.stop()

        #stores the time user paused at
        song_information["time_paused"][0] = round(time.time(), 2)

        #change "is_paused" status
        song_information["is_paused"][0] = True


def rewind():

    clear_lights_hard()
    
    #getting the total time of the song, converting it to minutes and seconds and adding a 0 in front of the seconds if it is 1 digit long
    total_time = song_information["full_time"][0]/song_information["selected_playback_speed"][0]
    total_minutes = str(round(total_time//60))
    total_seconds = str(round(total_time%60))

    if(len(total_seconds) == 1):
        total_seconds = "0" + total_seconds
        
    #if the time elapsed is less that 10 seconds, rewind to zero seconds
    if(song_information["time_elapsed"][0]<10):
        #changing the start time (so the timing in the loop is modified)
        song_information["start_time"][0] = song_information["start_time"][0] + song_information["time_elapsed"][0]

        #changing the time elapsed (so we can use it to display the time the user is skipping to if they have paused the program)
        song_information["time_elapsed"][0] = song_information["time_elapsed"][0] - song_information["time_elapsed"][0]

        #calculating the minutes and seconds of the time being skipped to
        minutes = str(round(song_information["time_elapsed"][0]//60))
        seconds = str(round(song_information["time_elapsed"][0]%60))

        #if the seconds is 1 digit, add 0 in front of it
        if(len(seconds) == 1):
            seconds = "0" + seconds

        #changing the time elapsed shown to the user
        widgets["time_of_song"][0].setText(minutes + ":" + seconds + " / " + total_minutes + ":" + total_seconds)
        
    #if the time elapsed is greater than 10 seconds, rewind by 10 seconds
    else:
            
        #changing the start time (so the timing in the loop is modified)
        song_information["start_time"][0] = song_information["start_time"][0] + 10

        #changing the time elapsed (so we can use it to display the time the user is skipping to if they have paused the program)
        song_information["time_elapsed"][0] = song_information["time_elapsed"][0] - 10

        #calculating the minutes and seconds of the time being skipped to
        minutes = str(round(song_information["time_elapsed"][0]//60))
        seconds = str(round(song_information["time_elapsed"][0]%60))

        #if the seconds is 1 digit, add 0 in front of it
        if(len(seconds) == 1):
            seconds = "0" + seconds

        #changing the time elapsed shown to the user
        widgets["time_of_song"][0].setText(minutes + ":" + seconds + " / " + total_minutes + ":" + total_seconds)

    
    #if the time elapsed is greater than the song duration (if the user has skipped too far forward) then set it to zero
    if song_information["time_elapsed"][0] < 0: song_information["time_elapsed"][0] = 0
    
def fast_forward():

    clear_lights_hard()
    
    #getting the total time of the song, converting it to minutes and seconds and adding a 0 in front of the seconds if it is 1 digit long
    total_time = song_information["full_time"][0]/song_information["selected_playback_speed"][0]
    total_minutes = str(round(total_time//60))
    total_seconds = str(round(total_time%60))

    if(len(total_seconds) == 1):
        total_seconds = "0" + total_seconds
        
    #if the song has less than 10 seconds to go, fast forward to finish time
    if(((song_information["full_time"][0]/song_information["selected_playback_speed"][0])-song_information["time_elapsed"][0])<10):

        #changing the start time (so the timing in the loop is modified)
        song_information["start_time"][0] = song_information["start_time"][0] + song_information["time_elapsed"][0]

        #changing the time elapsed (so we can use it to display the time the user is skipping to if they have paused the program)
        song_information["time_elapsed"][0] = song_information["time_elapsed"][0] + song_information["time_elapsed"][0]

        #calculating the minutes and seconds of the time being skipped to
        minutes = str(round(song_information["time_elapsed"][0]//60))
        seconds = str(round(song_information["time_elapsed"][0]%60))

        #if the seconds is 1 digit, add 0 in front of it
        if(len(seconds) == 1):
            seconds = "0" + seconds
            
        #if the time elapsed is negative (if the user has skipped too far back) then set it to zero
        if song_information["time_elapsed"][0] > total_time: song_information["time_elapsed"][0] = 0

        #changing the time elapsed shown to the user
        widgets["time_of_song"][0].setText(minutes + ":" + seconds + " / " + total_minutes + ":" + total_seconds)
        
    #if the song has more than 10 seconds to go, fast forward by 10 seconds
    else:

        #changing the start time (so the timing in the loop is modified)
        song_information["start_time"][0] = song_information["start_time"][0] - 10

        #changing the time elapsed (so we can use it to display the time the user is skipping to if they have paused the program)
        song_information["time_elapsed"][0] = song_information["time_elapsed"][0] + 10

        #calculating the minutes and seconds of the time being skipped to
        minutes = str(round(song_information["time_elapsed"][0]//60))
        seconds = str(round(song_information["time_elapsed"][0]%60))

        #if the seconds is 1 digit, add 0 in front of it
        if(len(seconds) == 1):
            seconds = "0" + seconds

        #if the time elapsed is negative (if the user has skipped too far back) then set it to zero
        if song_information["time_elapsed"][0] > total_time: song_information["time_elapsed"][0] = 0

        #changing the time elapsed shown to the user
        widgets["time_of_song"][0].setText(minutes + ":" + seconds + " / " + total_minutes + ":" + total_seconds)

#function which stores the selected playback speed
def store_selected_playback_speed(selection):

    #clearing previous selection        
    if song_information["selected_playback_speed"] != []:
        song_information["selected_playback_speed"].clear()

    #appending the current playback speed selection to a global dictionary
    song_information["selected_playback_speed"].append(selection)
        

#function to show the user information about selected song and to store it globally
def extract_selected_song():

    #getting the directory of the selected song (using the index of the selected song to find the directory stored in the song_information dictionary)
    song_directory = song_information["directory"][widgets["list_of_songs"][0].currentRow()]

    #extracting the sata from the selected song
    midi_data = pretty_midi.PrettyMIDI(song_directory)

    #converting the duration of the song to minutes and seconds (was originally in seconds)
    minutes = str(round(midi_data.get_end_time()//60))
    seconds = str(round(midi_data.get_end_time()%60))
    full_time = round(midi_data.get_end_time())

    #if there minutes of the song is already in a global dictionary, remove it
    if song_information["selected_song_minutes"] != []:
        song_information["selected_song_minutes"].clear()

    #if there seconds of the song is already in a global dictionary, remove it
    if song_information["selected_song_seconds"] != []:
        song_information["selected_song_seconds"].clear()

    if song_information["full_time"] != []:
        song_information["full_time"].clear()
        
    #append the minutes and seconds of the currently selected song to a global variable
    song_information["selected_song_minutes"].append(minutes)
    song_information["selected_song_seconds"].append(seconds)
    song_information["full_time"].append(full_time)

    #assigning the necessary values to the following variables
    song_name = widgets["list_of_songs"][0].currentItem().text()
    song_duration = song_information["selected_song_minutes"][0] + " Minutes and " + song_information["selected_song_seconds"][0] + " Seconds"
    song_file_size = str(round(os.path.getsize(song_directory)/1024, 2)) + " Kb"
    song_file_creation_date = str(datetime.fromtimestamp(os.path.getctime(song_directory)).strftime("%d-%m-%Y %H:%M:%S"))

    #showing the user basic information about the selected song
    widgets["song_info"][0].setText("<strong>Song Name: </strong>" + song_name +
                                    "<br><br><br><strong>Duration: </strong>" + song_duration +
                                    "<br><br><br><strong>File Size: </strong>" + song_file_size +
                                    "<br><br><br><strong>Creation Date: </strong>" + song_file_creation_date)

    #adding the selected directory to a dictionary to be used in the next frame
    song_information["selected_song_directory"].append(song_directory)


def refresh_songs():

    #clearing the list of songs before adding to it so there is no duplicates
    widgets["list_of_songs"][0].clear()

    #assigns a method which has a list with the root directory, sub directory, and files in each directory
    usb_directory = os.walk('/media/tyson')

    #loops through the the list and splits it into three parts
    for root, subdirectories, files in usb_directory:

        #loops through the list of files, checks if they are MIDI files and if they are, adds them to the list on frame2 and their directory to a dictionary
        for i in files:
            if i.endswith('.mid'):
                widgets["list_of_songs"][0].addItem(i[:-4])

                #change the back slash to a forward slash when using linux
                song_information["directory"].append(root + "/" + i)

            if i.endswith('.midi'):
                widgets["list_of_songs"][0].addItem(i[:-5])

                #change the back slash to a forward slash when using linux
                song_information["directory"].append(root + "/" + i)


#function that clears the widgets from the screen
def clear_widgets():
    
    #loops through dictionary of widgets
    for widget in widgets:

        #checks if each widget has a value
        if widgets[widget] != []:

            #if the widget being checked has a value, hide it
            widgets[widget][0].hide()
            
        #remove all widgets from the list    
        for i in range(0, len(widgets[widget])):
            widgets[widget].pop()


#function for the back button of frame 3
def back_from_song():

    clear_lights()
    
    #stopping the song - it will not stop on its own because it is a background process (running on another thread)
    song_timer.stop()
    
    #resetting the details for the current session
    if song_information["directory"] != []:
        song_information["directory"].clear()

    if song_information["selected_song_directory"] != []:   
        song_information["selected_song_directory"].clear()

    '''if song_information["selected_playback_speed"] != []:    
        song_information["selected_playback_speed"].clear()'''

    if song_information["selected_song_minutes"] != []:
        song_information["selected_song_minutes"].clear()

    if song_information["selected_song_seconds"] != []:
        song_information["selected_song_seconds"].clear()

    if song_information["full_time"] != []:
        song_information["full_time"][0]

    if song_information["selected_playback_seconds"] != []:
        song_information["selected_playback_seconds"].clear()

    if song_information["selected_playback_minutes"] != []:
        song_information["selected_playback_minutes"].clear()

    if song_information["midi_data_of_selected_song"] != []:
        song_information["midi_data_of_selected_song"].clear()

    if song_information["note_pitch"] != []:
        song_information["note_pitch"].clear()

    if song_information["note_start"] != []:
        song_information["note_start"].clear()

    if song_information["note_end"] != []:
        song_information["note_end"].clear()

    if song_information["note_played"] != []:
        song_information["note_played"].clear()

    if song_information["note_stopped"] != []:
        song_information["note_stopped"].clear()

    if song_information["is_paused"] != []:
        song_information["is_paused"].clear()
    
    song_information["start_time"][0] = 0
    song_information["time_elapsed"][0] = 0
    song_information["time_paused"][0] = 0
    song_information["time_played"][0] = 0

    #calling function to set up the previous page
    show_frame2()

#function to check if user has selected song and show frame 3
def show_frame3():

        #if the user has not selected a song and a playback speed, alert them of it
        if (song_information["selected_song_directory"] == []) and (widgets["playback_speed"][0].currentIndex() == -1):
            '''#declaring message box
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            #setting message for Message Box
            msg.setText("Please select a song and playback speed.")

            #setting Message box window title
            msg.setWindowTitle("Error")

            #declaring buttons on Message Box
            msg.setStandardButtons(QMessageBox.Ok)

            #start the app
            retval = msg.exec_()'''

            #flashes the LEDs red to let the user know that they selected the wrong option
            for lights in range(0, LED_COUNT):
                strip.setPixelColor(lights, Color(255,0,0))
                
            strip.show()
            time.sleep(0.5)
            clear_lights_hard()

        #if the user has not selected a song, alert them of it
        elif song_information["selected_song_directory"] == []:
            '''msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Please select a song.")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()'''
            
            #flashes the LEDs red to let the user know that they selected the wrong option
            for lights in range(0, LED_COUNT):
                strip.setPixelColor(lights, Color(255,0,0))
                
            strip.show()
            time.sleep(0.5)
            clear_lights_hard()

        #if the user has not selected a playback speed, alert them of it
        elif widgets["playback_speed"][0].currentIndex() == -1:
            '''msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Please select a playback speed.")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()'''
            
            #flashes the LEDs red to let the user know that they selected the wrong option
            for lights in range(0, LED_COUNT):
                strip.setPixelColor(lights, Color(255,0,0))
                
            strip.show()
            time.sleep(0.5)
            clear_lights_hard()

        #if the user has selected a song and a playback speed, continue to the next frame
        if (song_information["selected_song_directory"] != []) and (widgets["playback_speed"][0].currentIndex() != -1):
            clear_widgets()
            frame3()

#function to show frame 2
def show_frame2():
        clear_widgets()
        frame2()

#function to show frame 1
def show_frame1():
        clear_widgets()
        frame1()

        #removing the selections so user has to reselect when going back to frame 2
        if song_information["directory"] != []:
            song_information["directory"].pop()

        if song_information["selected_song_directory"] != []:
            song_information["selected_song_directory"].pop()

        
frame1()

#assigning the grid layout to the window after customizing it and showing the window
window.setLayout(grid)
window.show() 

#setting the function for the close button (which is not showing because the frame was removed)
sys.exit(app.exec_()) 
