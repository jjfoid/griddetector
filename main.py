from machine import Pin
from machine import RTC
import time
import ntptime
import network
import telegram
import dtek

#----------------------
#Settings
#----------------------
#The token of your telegram bot obtained from the Bot Father
BOT_TOKEN = ''
#The ID of the chat/channel your bot must send messages to
BOT_CHAT_ID = ''
#Your personal ID to get notifications from bot
BOT_OWNER_ID = ''
#ntp hostname. Default is 'pool.ntp.org', but it has some limitations.
#So it's recommended to use custom (for example, provided by your router)
ntptime.host = 'pool.ntp.org'
#Difference in seconds between GMT and your Time Zone as native ntptime lib returns time in GMT
TZ=10800
#GPIO pin to monitor, 22 by default, but you need to change it to your actual pin
GPIO_Pin = 22



#----------------------
#Check if WiFi connection is established (in boot.py)
#----------------------
wl = network.WLAN(network.STA_IF)
while not wl.isconnected() and wl.status() >= 0:
    time.sleep(0.1)

#----------------------
#Initial RTC sync with NTP
#----------------------
year, month, day, hour, minute, second, weekday, yearday = time.localtime(ntptime.time()+TZ)
RTC().datetime((year, month, day, 0, hour, minute, second, 0))

#----------------------
#Init Bot
#----------------------
bot = telegram.bot(BOT_TOKEN)

#----------------------
#Init DTEK shutdowns schedule
#----------------------
schedule = dtek.schedule()

#----------------------
#Init GPIO
#----------------------
button = Pin(GPIO_Pin, Pin.IN, Pin.PULL_UP)

#----------------------
#Main logic
#----------------------

#Create strings with the timestamp
def PrintableTimestamp():
    year, month, day, hour, minute, second, weekday, yearday = time.localtime()
    Dateandtime = "{}\\.{:02d}\\.{:02d} __{:02d}:{:02d}:{:02d}__"
    return Dateandtime.format(year, month, day, hour, minute, second)

#Store last Grid state change in unixtime in the separate file to be able to restore it after the reboot
def StoreLastStateChange(timestamp):
    f = open('laststatechange', 'w')
    f.write(str(timestamp))
    f.close()

#Calculate delta between last Grid state change and actual event
def StatesTimeDelta():
    Delta=NewStateChange-LastStateChange
    DeltaHr=round(Delta/3600)
    DeltaMin=round((Delta-DeltaHr*3600)/60)
    DeltaSec=round(Delta-DeltaHr*3600-DeltaMin*60)
    if DeltaMin < 0:
        DeltaHr=DeltaHr-1
        DeltaMin=DeltaMin+60
    if DeltaSec < 0:
        DeltaMin=DeltaMin-1
        DeltaSec=DeltaSec+60
    DeltaString = "{:02d} г {:02d} хв {:02d} сек"
    return DeltaString.format(DeltaHr, DeltaMin, DeltaSec)

#Send message to the chat/channel about Grid state change
def GridStateChange(Message):
    bot.send_get(BOT_CHAT_ID, Message)

#Handler to process the Grid ON/OFF event
def PowerEventHandler (pin):
        if button.value(): # Grid electricity ON
            global GridState
            if not GridState: #If it was OFF before (we really need this additional check to mitigate contact bounces or electromagnetic interferences)
                global NewStateChange
                global LastStateChange
                NewStateChange=time.time()
                year, month, day, hour, minute, second, weekday, yearday = time.localtime()
                GridStateChange(PrintableTimestamp()\
                                + '%0A\U0001F7E2Світло з\'явилося%0A'\
                                + u"\u23F1" + 'Його не було '\
                                + StatesTimeDelta()\
                                + schedule.get_grid_off(weekday, hour)\
                                + schedule.get_grid_gray(weekday, hour))
                GridState = True
                LastStateChange=NewStateChange
                StoreLastStateChange(LastStateChange)
        else: # Grid electricity OFF
            global GridState
            if GridState: #if it was ON before (we really need this additional check to mitigate contact bounces or electromagnetic interferences)
                global NewStateChange
                global LastStateChange
                NewStateChange=time.time()
                year, month, day, hour, minute, second, weekday, yearday = time.localtime()
                GridStateChange(PrintableTimestamp()\
                                + '%0A\U0001F534Світло зникло%0A'\
                                + u"\u23F1" + 'Воно було '\
                                + StatesTimeDelta()\
                                + schedule.get_grid_on(weekday, hour)\
                                + schedule.get_grid_gray(weekday, hour))
                GridState = False
                LastStateChange=NewStateChange
                StoreLastStateChange(LastStateChange)

#----------------------
#Check initial state
#----------------------
if button.value():
    GridState = True
    #GridStateChange(PrintableTimestamp() + u"%0A\u26A1"\
    #                + 'Детектор увімкнено\\.%0A\U0001F7E2 Поточний статус \\- *Є світло*\\!'\
    #                + schedule.get_grid_off(weekday, hour)\
    #                + schedule.get_grid_gray(weekday, hour))
else:
    GridState = False
    #GridStateChange(PrintableTimestamp() + u"%0A\u26A1"\
    #                + 'Детектор увімкнено\\.%0A\U0001F534 Поточний статус \\- *Немає світла*\\!'\
    #                + schedule.get_grid_on(weekday, hour)\
    #                + schedule.get_grid_gray(weekday, hour))

#----------------------
#Init last state change
#----------------------
with open('laststatechange', "r") as f:
    LastStateChange = int(f.read())

#----------------------
#Set handler for Grid State changes
#----------------------
button.irq(handler=PowerEventHandler, trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING)

#----------------------
#Send message to the owner that everything is fine
#----------------------
bot.send_get(BOT_OWNER_ID, PrintableTimestamp()+' Bot started') #Send some diag data

#----------------------
#Init Schedule posting
#----------------------
datetime = time.localtime()
#Set desired time for the first posting after the script start.
#Please note that only the schedule for the current day can be posted
SchedulePostTime=(datetime[0], datetime[1],datetime[2], 23, 59, 59, 0, 0)
SchedulePostTime=time.mktime(SchedulePostTime) # type: ignore
TimeTillPost = SchedulePostTime - time.time()
if TimeTillPost > 0: #If the planned time is bigger than now
    time.sleep(TimeTillPost+1)
else: #If it in the past - we should wait till tomorrow
    time.sleep(24*60*60 + TimeTillPost + 1)

#----------------------
#The main loop
#----------------------
try:
    while True:
        year, month, day, hour, minute, second, weekday, yearday = time.localtime(ntptime.time()+TZ)
        RTC().datetime((year, month, day, 0, hour, minute, second, 0))

        datetime = time.localtime()
        GridStateChange(schedule.get_day_schedule(datetime[6], datetime[1],datetime[2]))
        #Sleep for 24 hrs
        time.sleep(24*60*60)
        pass
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    time.sleep(0)
