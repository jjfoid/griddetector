import network

ssid = '' #Put your WiFi SSID (AP name) here
password = '' #Your WiFi Password
network.hostname("") #Hostname for your device

wl = network.WLAN(network.STA_IF)

if not wl.isconnected():
	wl.active(True)
	wl.connect(ssid, password)
	while not wl.isconnected():
		pass
import webrepl
webrepl.start()
