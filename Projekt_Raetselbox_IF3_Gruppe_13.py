import time

# für die Matrix verwendung
import RPi.GPIO as GPIO

# für dei RGB-LED
from rpi_ws281x import *

# für das Display
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# random
import random

global hp	# Anzahl Leben

global x 	# Farbenset
x = 1

# Klasse für das verwenden der Matrix
class ButtonMatrix():
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        # GPIO Pins fuer die Zeilen werden deklariert.
        self.rowPins = [21,20,16,12]
        # GPIO Pins fuer die Spalte werden deklariert.
        self.columnPins = [6,13,19,26]
        # Definiere Vier Inputs mit pull up Widerstaenden.
        for i in range(len(self.rowPins)):
            GPIO.setup(self.rowPins[i],GPIO.IN,pull_up_down=GPIO.PUD_UP)
        # Definiere Vier Outputs und setze sie auf high.
        for j in range(len(self.columnPins)):
            GPIO.setup(self.columnPins[j], GPIO.OUT)
            GPIO.output(self.columnPins[j], 1)
	
    def buttonHeldDown(self,pin):
        if(GPIO.input(self.rowPins[pin]) == 0):
            return True
        return False

# Öffnet Splash-Screen
def splash(disp):
	image_splash = Image.open('bameriwo.png').convert('1')	# Lade Splashscreen Bild
	disp.image(image_splash)	# lädt png Datei in Speicher
	disp.display()	# png Datei anzeigen
	time.sleep(5)	# Splash Screen wird 5 Sekunden angezeigt
	return "start"

# Öffnet Start-Screen
def start(disp, button): 
	GPIO.output(button.columnPins[0],0)		# Aktiviert Buttons der Buttonmatrix Spalte 0
	image_start = [Image.open('Start1.png').convert('1'), Image.open('Start2.png').convert('1')]    
	while(button.buttonHeldDown(0) == False | button.buttonHeldDown(1) == False):
		disp.image(image_start[0])
		disp.display()
		time.sleep(.5)
		disp.image(image_start[1])
		disp.display()
		time.sleep(.5)
    # Stellt Animation dar, wechselt im 0.5sek Takt zwischen beiden png Dateien

	if button.buttonHeldDown(1) == True:
		while(button.buttonHeldDown(1)):	# Warten auf loslassen des Knopfes
			pass
		GPIO.output(button.columnPins[0],1)		# Deaktiviert Buttons der Buttonmatrix Spalte 0
		return "optionen"
	else:
		while(button.buttonHeldDown(0)):	# Warten auf loslassen des Knopfes
			pass
		GPIO.output(button.columnPins[0],1)		# Deaktiviert Buttons der Buttonmatrix Spalte 0
		return "tutorial"

# Öffnet Option-Menü/Farbauswahl
def option(disp, button, strip):
    
	global x

	GPIO.output(button.columnPins[0],0)

	image_option = [Image.open('Optionen1.png').convert('1'), Image.open('Optionen3.png').convert('1')]

	while(button.buttonHeldDown(0) == False):
		disp.image(image_option[0])
		disp.display()

		time.sleep(.5)

		disp.image(image_option[1])
		disp.display()

		time.sleep(.5)	

	# Farbauswahl
		if button.buttonHeldDown(1) == True:
			while(button.buttonHeldDown(1)):
				pass
			# Setzt alle LEDs auf Standardfarbe Rot (Farbset Z.22 x=1 => Rot)
			for i in range(strip.numPixels()):
				strip.setPixelColor(i, Color(255,0,0))	
			strip.show()
			x = 1

		elif button.buttonHeldDown(2) == True:
			while(button.buttonHeldDown(2)):
				pass
			# Setzt alle LEDs auf Grün (Farbset Z.22 x=2 => Grün)
			for i in range(strip.numPixels()):
				strip.setPixelColor(i, Color(0,255,0))
			strip.show()
			x = 2

		elif button.buttonHeldDown(3) == True:
			while(button.buttonHeldDown(3)):
				pass
			# Setzt alle LEDs auf Blau (Farbset Z.22 x=3 => Blau)
			for i in range(strip.numPixels()):
				strip.setPixelColor(i, Color(0,0,255))
			strip.show()
			x = 3

	while(button.buttonHeldDown(0)):
		pass
	GPIO.output(button.columnPins[0],1)

	# LED Reset beim verlassen der Optionen
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, Color(0,0,0))
	strip.show()

	return "start"

# Öffnet das Tutorial, welches aus 3 Seitigen Anleitung besteht
def tutorial(disp, button):

	global hp
	hp = 3		# Setzt Anzahl Leben wieder auf max.

	GPIO.output(button.columnPins[0],0)

	image_tut =	[[Image.open('Ziel1_1.png').convert('1'), Image.open('Ziel1_2.png').convert('1')],
				[Image.open('Ziel2_1.png').convert('1'), Image.open('Ziel2_2.png').convert('1')],
				[Image.open('Ziel3_1.png').convert('1'), Image.open('Ziel3_2.png').convert('1')]]
	i = 0
	# Zeigt alle 3 Szenen nach jeweiligem Tastendruck an
	while(i < 3):
		disp.image(image_tut[i][0])
		disp.display()
		time.sleep(.5)
		disp.image(image_tut[i][1])
		disp.display()
		time.sleep(.5)
		if button.buttonHeldDown(0) == True:
			while(button.buttonHeldDown(0)):
				pass
			i+=1

	GPIO.output(button.columnPins[0],1)

	return "spiel" 

# Spiellogik
def spiel(disp, button, strip):

	global hp

	# Je nach x-Wert aus Optionen/Farbauswahl wird Menge der Herzen in vorab gewählter Farbe angezeigt
	if x == 1:
		for i in range(hp):
			strip.setPixelColor(i, Color(255,0,0))
	elif x == 2:
		for i in range(hp):
			strip.setPixelColor(i, Color(0,255,0))
	elif x == 3:
		for i in range(hp):
			strip.setPixelColor(i, Color(0,0,255))
	strip.show()

	# Erzeugt 4 Random Int Werte für Tonne
	tonne = random.sample(range(1,13), 4)
	tonne.sort()

	# Erzeugte Random Werte, in Console anzeigen
	print("Taster-Nr:" + str(tonne))

	# Lade Grafik vom Spiel
	image_spiel = Image.open('Spiel.png').convert('1')

	disp.image(image_spiel)
	disp.display()

	w = 0	# Anzahl der Hintereinander richtig gewählten Tonnen(wichtig für Win)
	pressed = []	# Liste der bereits gedrückten Knöpfe
	while True:
		# Abfrage aller Knöpfe (4x3 Matrix)
		for j in range(4):
			GPIO.output(button.columnPins[j],0)
			for i in range(3):
				if GPIO.input(button.rowPins[i]) == 0:
					while(button.buttonHeldDown(i)):
						pass
					z = 4*i+j+1		# Wert des gedrückten Knopfes 
					# Iteriert über komplette Liste
					for k in range(4):
						# Abfrage ob Schalter an gedrückter Stelle
						if tonne[k] == z:
							# Bei richtiger Auswahl oberste LED Grün
							strip.setPixelColor(7, Color(0,255,0))
							strip.show()
							# Abfrage ob Knopf bereits gedrückt
							if z in pressed:
								break
							pressed.append(z)	# Knopf wird zu Liste pressed hinzugefügt
							print("schon gedrückt: "+ str(pressed))
							w+=1
							print("Winningstreak: "+ str(w))
							# Abfrage der Gewinnbedingung
							if w == 2:
								GPIO.output(button.columnPins[j],1)
								return "win"
							break
						else:
							# Wenn gedrückter Wert nicht in Randomliste tonne
							if k == 3:
								# Bei falscher Auswahl oberste LED Rot
								strip.setPixelColor(7, Color(255,0,0))
								strip.show()
								hp -= 1		# ein Leben/Herz wird abgezogen
								print("Leben: "+ str(hp))
								strip.setPixelColor(hp, Color(0,0,0))	# Deaktiviert LED nachdem Herz verloren (3,2,1)
								strip.show()	
								if hp == 0:		#Herzen auf 0 löst lose aus
									GPIO.output(button.columnPins[j],1)
									return "lose"
								GPIO.output(button.columnPins[j],1)
								return "spiel"
			GPIO.output(button.columnPins[j],1)

# Öffnet lose		
def lose(disp, button, strip):

	# Deaktiviert alle LEDs
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, Color(0,0,0))
	strip.show()

	GPIO.output(button.columnPins[0],0)

	image_lose = [Image.open('Lose1.png').convert('1'), Image.open('Lose2.png').convert('1')]

	while(button.buttonHeldDown(0) == False):
		disp.image(image_lose[0])
		disp.display()

		time.sleep(.5)

		disp.image(image_lose[1])
		disp.display()

		time.sleep(.5)	

	if button.buttonHeldDown(0) == True:
		while(button.buttonHeldDown(0)):
			pass

		GPIO.output(button.columnPins[0],1)

		return "start"

# Öffnet win
def win(disp, button, strip):

	# Deaktiviert alle LEDs
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, Color(0,0,0))
	strip.show()

	GPIO.output(button.columnPins[0],0)

	image_win = [Image.open('Win1.png').convert('1'), Image.open('Win2.png').convert('1')]

	while(button.buttonHeldDown(0) == False):
		disp.image(image_win[0])
		disp.display()

		time.sleep(.5)

		disp.image(image_win[1])
		disp.display()

		time.sleep(.5)	
	
	if button.buttonHeldDown(0) == True:
		while(button.buttonHeldDown(0)):
			pass

		GPIO.output(button.columnPins[0],1)

		return "start"

#------------------------------------------------------------------------------------------------
# Reset-Pin
RST = 24
# Beschreibung der Größe des Displays und an welche Adresse die Bilder gesendet werden
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3D)
disp.begin()
disp.clear()
disp.display()

# Konfiguration des LED-Streifens
LED_COUNT      = 8          # Anzahl der LED-Pixel
LED_PIN        = 18         # GPIO-Pin
LED_FREQ_HZ    = 800000     # LED-Signalfrequenz       
LED_BRIGHTNESS = 55         # Helligkeit der LEDs
       
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, 10, False, LED_BRIGHTNESS, 0)
# Initialisierung des LED-Streifens
strip.begin()

# Deaktivert alle LEDs bei Programmstart
for i in range(strip.numPixels()):
	strip.setPixelColor(i, Color(0,0,0))
strip.show()

# Initialisierung der Buttonmatrix
button = ButtonMatrix()

#------------------------------------------------------------------------------------------------
# Abfrage der zu startenden Szene

szene = "bameriwo"

while(True):
	if szene == "bameriwo":
		print("splash")
		szene = splash(disp)
	elif szene == "start":
		print("start")
		szene = start(disp, button)
	elif szene == "optionen":
		print("option")
		szene = option(disp, button, strip)
	elif szene == "spiel":
		print("spiel")
		szene = spiel(disp, button, strip)
	elif szene == "tutorial":
		print("tutorial")
		szene = tutorial(disp, button)
	elif szene == "win":
		print("win")
		szene = win(disp, button, strip)
	elif szene == "lose":
		print("lose")
		szene = lose(disp, button, strip)

