#This class implements schedule logic
#Schedules must be prepared as jsons using the following structure and code:
#schedule = {0: [[00, 04], [09, 13], [18, 22]],              #Monday
#            1: [[03, 07], [12, 16], [21, 24]],              #Tuesday
#            2: [[00, 01], [06, 10], [15, 19]],              #Wednesday
#            3: [[00, 04], [09, 13], [18, 22]],              #Thursday
#            4: [[03, 07], [12, 16], [21, 24]],              #Friday
#            5: [[00, 01], [06, 10], [15, 19]],              #Saturday
#            6: [[00, 03], [06, 09], [12, 15], [18, 21]]}    #Sunday
#with open('schedule_off.json', 'w') as f:
#    f.write(json.dumps(schedule))
#The schedule for your location can be found here:
#https://www.dtek-krem.com.ua/ua/shutdowns
#The file export_jsons.py is included in this repo to help you to generate jsons

import json

class schedule:
    
    def __init__(self):
        with open('schedule_off.json') as f:
            self.schedule_off = json.load(f)
        with open('schedule_on.json') as f:
            self.schedule_on = json.load(f)
        with open('schedule_gray.json') as f:
            self.schedule_gray = json.load(f)

    def get_grid_off(self, today, hour):
        if today == 6:
            tomorrow='0'
        else:
            tomorrow=str(today+1)
        today=str(today)
        output = "%0A\U0001F5D3Наступне планове відключення *{:02d}:00 \\- {:02d}:00*"
        for periods in self.schedule_off[today]:
            #To check if current hour < than the start of the upcoming shutdown period.
            #If yes - the next period will start today, let's select it.
            if (hour < periods[0]):
                #if this period starts before midnight and ends after,
                #then return the whole period
                if periods[1]==24 and self.schedule_off[tomorrow][0][0]==0:
                    return output.format(periods[0],self.schedule_off[tomorrow][0][1])
                #Otherwise period ends today, return it
                return output.format(periods[0],periods[1])
        #If no upcoming ranges for the same day were found,
        #then we can make a conclusion that we are inside this period already, or right after it.
        #In case we are inside the period - let's check its transition over midnight
        #(because transition is not smooth in terms of the specified intervals).
        #If period starts today and ends tomorrow, then we are inside this period now,
        #and need to select the next one.
        if max(self.schedule_off[today])[1]==24 and self.schedule_off[tomorrow][0][0]==0:
            return output.format(self.schedule_off[tomorrow][1][0],self.schedule_off[tomorrow][1][1])
        #Otherwise select the first available period in the next day
        return output.format(self.schedule_off[tomorrow][0][0],self.schedule_off[tomorrow][0][1])

    def get_grid_on(self, today, hour):
        if today == 6:
            tomorrow='0'
        else:
            tomorrow=str(today+1)
        today=str(today)
        output = "%0A\U0001F5D3Наступне гарантоване вікно: *{:02d}:00 \\- {:02d}:00*"
        for periods in self.schedule_on[today]:
            #To check if current hour < than the start of the upcoming ON period.
            #If yes - the next period will start today, let's select it.
            if (hour < periods[0]):
                #if this period starts before midnight and ends after,
                #then return the whole period
                if periods[1]==24 and self.schedule_on[tomorrow][0][0]==0:
                    return output.format(periods[0],self.schedule_on[tomorrow][0][1])
                #Otherwise period ends today, return it
                return output.format(periods[0],periods[1])
        #If no upcoming ranges for the same day were found,
        #then we can make a conclusion that we are inside this period already, or right after it.
        #In case we are inside the period - let's check its transition over midnight
        #(because transition is not smooth in terms of the specified intervals).
        #If period starts today and ends tomorrow, then we are inside this period now,
        #and need to select the next one.
        if max(self.schedule_on[today])[1]==24 and self.schedule_on[tomorrow][0][0]==0:
            return output.format(self.schedule_on[tomorrow][1][0],self.schedule_on[tomorrow][1][1])
        #Otherwise select the first available period in the next day
        return output.format(self.schedule_on[tomorrow][0][0],self.schedule_on[tomorrow][0][1])

    def get_grid_gray(self, today, hour):
        if today == 6:
            tomorrow='0'
        else:
            tomorrow=str(today+1)
        today=str(today)
        output = "%0A\U0001F5D3Сіра зона: *{:02d}:00 \\- {:02d}:00*"
        for periods in self.schedule_gray[today]:
            #To check if current hour < than the end of the upcoming gray zone period.
            #If yes - then select it.
            if (hour < periods[1]):
                #if this period starts before midnight and ends after,
                #then return the whole period
                if periods[1]==24 and self.schedule_gray[tomorrow][0][0]==0:
                    return output.format(periods[0],self.schedule_gray[tomorrow][0][1])
                #Otherwise period ends today, return it
                return output.format(periods[0],periods[1])
        #If no suitable ranges for the same day were found,
        #then we can make a conclusion that no more Gray Zones are expected today.
        #Let's return the tomorrow's first one.
        return output.format(self.schedule_gray[tomorrow][0][0],self.schedule_gray[tomorrow][0][1])

    #The following method is not used yet. For future implementations
    def store_schedules(self, schedule_off, schedule_on, schedule_gray):
        self.schedule_off=schedule_off
        self.schedule_on=schedule_on
        self.schedule_gray=schedule_gray
        with open('schedule_off.json', 'w') as f:
            f.write(json.dumps(schedule_off))
        with open('schedule_on.json', 'w') as f:
            f.write(json.dumps(schedule_on))
        with open('schedule_gray.json', 'w') as f:
            f.write(json.dumps(schedule_gray))

    #Scheduled notifications about planned outages today
    def get_day_schedule(self, today, month, day):
        if today == 6:
            tomorrow='0'
        else:
            tomorrow=str(today+1)
        today=str(today)
        output = "Відключення на сьогодні, {:02d}\\.{:02d}:%0A"
        item = "{:02d}:00 \\- {:02d}:00%0A"
        for periods in self.schedule_off[today]:
            #if this period starts before midnight and ends after,
            #then return the whole period
            if periods[1]==24 and self.schedule_off[tomorrow][0][0] == 0:
                output = output + self.respective_emoji(periods[0]) + item.format(periods[0], self.schedule_off[tomorrow][0][1])
            else:
                output = output + self.respective_emoji(periods[0]) + item.format(periods[0], periods[1])
        return output.format(day, month)
    
    def respective_emoji(self, hour):
        emojis = "🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛🕐🕑🕒🕓🕔🕕🕖🕗🕘🕙🕚🕛"
        return emojis[hour]
