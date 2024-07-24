import json

schedule = {0: [[00, 04], [09, 13], [18, 22]],              #Monday
            1: [[03, 07], [12, 16], [21, 24]],              #Tuesday
            2: [[00, 01], [06, 10], [15, 19]],              #Wednesday
            3: [[00, 04], [09, 13], [18, 22]],              #Thursday
            4: [[03, 07], [12, 16], [21, 24]],              #Friday
            5: [[00, 01], [06, 10], [15, 19]],              #Saturday
            6: [[00, 03], [06, 09], [12, 15], [18, 21]]}    #Sunday

with open('schedule_off.json', 'w') as f:
    f.write(json.dumps(schedule))

schedule = {0: [[07, 09], [16, 18]],                     #Monday
            1: [[01, 03], [10, 12], [19, 21]],           #Tuesday
            2: [[04, 06], [13, 15], [22, 24]],           #Wednesday
            3: [[07, 09], [16, 18]],                     #Thursday
            4: [[01, 03], [10, 12], [19, 21]],           #Friday
            5: [[04, 06], [13, 15], [22, 24]],           #Saturday
            6: [[04, 06], [10, 12], [16, 18], [22, 24]]} #Sunday
    
with open('schedule_on.json', 'w') as f:
    f.write(json.dumps(schedule))

schedule = {0: [[04, 07], [13, 16], [22, 24]],           #Monday
            1: [[00, 01], [07, 10], [16, 19]],           #Tuesday
            2: [[01, 04], [10, 13], [19, 22]],           #Wednesday
            3: [[04, 07], [13, 16], [22, 24]],           #Thursday
            4: [[00, 01], [07, 10], [16, 19]],           #Friday
            5: [[01, 04], [10, 13], [19, 22]],           #Saturday
            6: [[03, 04], [09, 10], [15, 16], [21, 22]]} #Sunday

with open('schedule_gray.json', 'w') as f:
    f.write(json.dumps(schedule))
