import os
import sys
from threading import Thread
from telegram.ext import Updater,CommandHandler,MessageHandler,Filters,InlineQueryHandler, BaseFilter, CallbackQueryHandler, ConversationHandler
import logging
from telegram import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardMarkup, ReplyKeyboardRemove
import telegram
import re
import datetime
import requests
import json
import pytz 

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

# bot configuration
PORT = os.environ.get('PORT')
TOKEN = ""
NAME = ""

# default reply setup
introtext = 'Hi there SMUgger!!! I can estimate how full study spots are, just answer some questions for me!\n\nFeel free to /restart anytime should you want to start over!'
whichschooltext = 'Which building do you want to study at?'
whichleveltext = 'Which floor are you on?'
forecastlevel = 'Which floor do you want to study at?'
holdonahbrosis = 'Hold on ah Bro/Sis let me compute in my brain first'
looksfulltext = 'Oh no! Seems like {} {} is quite full. Would you like me to suggest elsewhere in {}?\n\nIf you would like me to stop, send "End"'
alternativesuggestiontext = 'Ok! I will let you know of another place in {}. Wait ah!'
end = "Happy studying!\nIf you need my help again, feel free to /start me!"
askday = "Which day do you want to forecast?"
asktime = "What time of the day do you want to forecast? Enter in HH:MM in 24hours format."
feedback1text = "Thank you for using our bot, please rate your experience from 1 to 5.\n\n5 being the most satisfactory and 1 being the least satisfactory."
feedback2text = "Do give us some feedback on how we can improve our bot."

# keyboard setup
keyboards = {
    "location_keyboard" :[["Connexion"], ['KGC'], ['LKS Library'],['SIS'], ['SOA'], ['SOB'],['SOE/SOSS'],['SOL']],
    "functions" : [['Show current crowd level', "Forecast crowds"], ["Floor plan", "Crash GSR"], ["Submit feedback"]],
    "level_keyboard" : [['Level 5'], ['Level 4'], ['Level 3'], ['Level 2'], ["Level B1"]],
    "suggest_keyboard" : [["Find me alternatives!"], ["End"]],
    "day_keyboard" : [["Mon", "Tue", "Wed", "Thur", "Fri"]],
    "rating": [["1", "2", "3", "4", "5"]]
}

CHOOSE_FUNCTION, ASKDAY, ASKTIME, ASKSCHOOL, ASKLEVEL, ALTERNATIVE, FEEDBACK1, FEEDBACK2 = range(8)

# define functions for requests to flask 
# baseurl = 'http://127.0.0.1:5000/'
baseurl = 'https://fabcrowdlevel.herokuapp.com/'
getinfourl = 'https://fabstudyareainfo.herokuapp.com/'
feedbackurl = 'https://fabfeedback.herokuapp.com/'
forecasturl = "https://fabforecast.herokuapp.com/"

def getcrowdlevel(school, level):
    url = baseurl + "GetCrowdLevel/"
    local_tz = pytz.timezone('Asia/Singapore')
    currentDT = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz)
    timestamp = currentDT.strftime("%H:%M:%S")
    mintime = currentDT - datetime.timedelta(minutes = 10)
    timestamplb = mintime.strftime("%H:%M:%S")
    params = {"school":school, "level":level, "timestamp":timestamp, "lb":timestamplb}
    print(params)
    r = requests.get(url, json=params)
    print(r.text)
    return r 

def getalternatives(school, level):
    url = baseurl + "GetAlternatives/"
    local_tz = pytz.timezone('Asia/Singapore')
    currentDT = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz)
    timestamp = currentDT.strftime("%H:%M:%S")
    mintime = currentDT - datetime.timedelta(minutes = 10)
    timestamplb = mintime.strftime("%H:%M:%S")
    params = {"school":school, "level":level, "timestamp":timestamp, "lb":timestamplb}
    print(params)
    r = requests.get(url, json=params)
    print(r.text)
    return r 

def getimage(school, level):
    url = getinfourl + "getImage/"
    params = {"school":school, "level":level}
    print(params)
    r = requests.get(url, json=params)
    print(r.text)
    return r

def createuser(telegramID):
    url  = feedbackurl + "createuser/"
    params = {"telegramID": telegramID}
    r = requests.post(url, json=params)
    return r

def postfeedback(update, rating, feedback, school, level):
    url = feedbackurl + "PostFeedback/"
    params = {"telegramID":update.effective_user.id, "rating":rating, "feedback":feedback, "school":school, "level":level}
    print(params)
    r = requests.post(url, json=params)
    print(r.text)
    return r

def getforecast(time, school, level):
    url = forecasturl + "GetForecast/"
    time_obj = datetime.datetime.strptime(time, '%H:%M')
    mintime = time_obj - datetime.timedelta(minutes = 10)
    timestamplb = mintime.strftime("%H:%M")
    params = {"school":school, "level":level, "time":time, "lb":timestamplb}
    print(params)
    r = requests.get(url, json=params)
    print(r.text)
    return r 

def getgsr(school):
    url = baseurl + "GetGSRs/"
    local_tz = pytz.timezone('Asia/Singapore')
    currentDT = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz)
    timestamp = currentDT.strftime("%H:%M:%S")
    mintime = currentDT - datetime.timedelta(minutes = 10)
    timestamplb = mintime.strftime("%H:%M:%S")
    params = {"school":school, "timestamp":timestamp, "lb":timestamplb}
    print(params)
    r = requests.get(url, json=params)
    print(r.text)
    return r

# command handlers
def stop_and_restart():
    """Gracefully stop the Updater and replace the current process with a new one"""
    updater.stop()
    s.execl(sys.executable, sys.executable, *sys.argv)

def reset(update, context):
    update.message.reply_text('Bot is restarting...')
    Thread(target=stop_and_restart).start()

def start(update, context):
    context.user_data["forecast"] = None
    context.user_data["school"] = None 
    context.user_data["level"] = None 
    context.user_data["f_day"] = None 
    context.user_data["f_time"] = None
    context.user_data["getinfo"] = None
    context.user_data["rating"] = None
    context.user_data["crash"] = None
    context.user_data["fb"] = None 

    update.message.reply_text(introtext)
    
    update.message.reply_text("What would you like me to do?", 
    reply_markup=ReplyKeyboardMarkup(keyboards["functions"], 
    resize_keyboard=True, one_time_keyboard=True))

    return CHOOSE_FUNCTION

def restart(update, context):
    context.user_data["forecast"] = None
    context.user_data["school"] = None 
    context.user_data["level"] = None 
    context.user_data["f_day"] = None 
    context.user_data["f_time"] = None
    context.user_data["getinfo"] = None
    context.user_data["rating"] = None
    context.user_data["crash"] = None
    context.user_data["fb"] = None 
    update.message.reply_text(introtext)
    
    update.message.reply_text("What would you like me to do?", 
    reply_markup=ReplyKeyboardMarkup(keyboards["functions"], 
    resize_keyboard=True, one_time_keyboard=True))
    
    return CHOOSE_FUNCTION

def stop(update, context):
    context.user_data["forecast"] = None
    context.user_data["school"] = None 
    context.user_data["level"] = None 
    context.user_data["f_day"] = None 
    context.user_data["f_time"] = None
    context.user_data["getinfo"] = None
    context.user_data["rating"] = None
    context.user_data["crash"] = None
    context.user_data["fb"] = None 
    update.message.reply_text(end)
    return ConversationHandler.END

# message handlers

# selecting which function you want to use
def decidefunction(update, context):
    if update.message.text == "Show current crowd level":
        update.message.reply_text(whichschooltext, 
        reply_markup=ReplyKeyboardMarkup(keyboards["location_keyboard"], 
        resize_keyboard=True, one_time_keyboard=True))
        return ASKSCHOOL
    elif update.message.text == "Forecast crowds":
        context.user_data["forecast"] = True 
        update.message.reply_text(askday,
        reply_markup=ReplyKeyboardMarkup(keyboards["day_keyboard"],
        resize_keyboard=True, one_time_keyboard=True))
        return ASKDAY
    elif update.message.text == "Floor plan":
        context.user_data["getinfo"] = True 
        update.message.reply_text(whichschooltext,
        reply_markup=ReplyKeyboardMarkup(keyboards["location_keyboard"],
        resize_keyboard=True, one_time_keyboard=True))
        return ASKSCHOOL
    elif update.message.text == "Crash GSR":
        context.user_data["crash"] = True
        update.message.reply_text(whichschooltext,
        reply_markup=ReplyKeyboardMarkup(keyboards["location_keyboard"],
        resize_keyboard=True, one_time_keyboard=True))
        return ASKSCHOOL
    elif update.message.text == "Submit feedback":
        context.user_data["fb"] = True
        update.message.reply_text("Please rate our bot from 1 to 5\n\n5 being the most satisfactory and 1 being the least satisfactory.",
        reply_markup=ReplyKeyboardMarkup(keyboards["rating"],
        resize_keyboard=True, one_time_keyboard=True))
        return FEEDBACK1

class DecideFunctionFilter(BaseFilter):
    def filter(self, message):
        return message.text is not None and message.text in ['Show current crowd level', "Forecast crowds", "Floor plan", "Crash GSR", "Submit feedback"]
decidefunctionfilter = DecideFunctionFilter()

# handle school selected
def schoolhandler(update, context):
    if update.message.text != "SIS":
        update.message.reply_text("This bot is still currently in beta testing. Functions for locations other than SIS are not implemeneted yet!\n\nPlease select SIS",
        reply_markup=ReplyKeyboardMarkup(keyboards["location_keyboard"], 
        resize_keyboard=True, one_time_keyboard=True))
        return None
    context.user_data["school"] = update.message.text
    if context.user_data["forecast"]:
        update.message.reply_text(forecastlevel,
        reply_markup=ReplyKeyboardMarkup(keyboards["level_keyboard"], 
        resize_keyboard=True, 
        one_time_keyboard=True))
        return ASKLEVEL
    elif context.user_data["crash"]:
        update.message.reply_text("Wait ah, give me a moment to find empty GSRs!")
        r = getgsr(context.user_data["school"])
        if r.status_code == 200 and r.json() == []:
            update.message.reply_text("There are currently no empty GSRs available!")
            update.message.reply_text(feedback1text,    
            reply_markup=ReplyKeyboardMarkup(keyboards["rating"],
            resize_keyboard=True, one_time_keyboard=True))
            return FEEDBACK1

        result = r.json()        
        gsrresult = ["🌈Here are the results!!!"]
        gsrresult.append("The following GSRs are currently empty!\n")
        l = []
        for i in result:
            if i not in gsrresult:
                gsrresult.append(i)
                if "GSR 3-" in i:
                    if "L3" not in l:
                        l.append("L3")
                elif "GSR 2-" in i:
                    if "L2" not in l:
                        l.append("L2")
        t = "\n".join(gsrresult)
        update.message.reply_text(t)
        for i in l:
            u = getimage(context.user_data["school"], i)
            if u.status_code == 200 and u.json() != {}:
                imageurl = u.json()
                update.message.reply_photo(photo=imageurl, caption="Here is the floor plan for {} {}!".format(context.user_data["school"], i))
        update.message.reply_text(feedback1text,    
        reply_markup=ReplyKeyboardMarkup(keyboards["rating"],
        resize_keyboard=True, one_time_keyboard=True))
        return FEEDBACK1
    update.message.reply_text(whichleveltext, 
    reply_markup=ReplyKeyboardMarkup(keyboards["level_keyboard"], 
    resize_keyboard=True, 
    one_time_keyboard=True))
    return ASKLEVEL

class SchoolFilter(BaseFilter):
    def filter(self,message):
        l = ["Connexion", 'KGC', 'LKS Library', 'SIS', 'SOA', 'SOB','SOE/SOSS','SOL']
        return message.text is not None and message.text in l 
schoolfilter = SchoolFilter()

# handle level seleced. main function for getting crowd levels and floor plan
def levelhandler(update, context):
    update.message.reply_text(holdonahbrosis)
    telegramID = update.effective_user.id
    r = createuser(telegramID)

    level = update.message.text
    if "B1" not in level:
        context.user_data["level"] = level.replace("evel ", "")
    else:
        context.user_data["level"] = level.replace("Level ", "")

    if context.user_data["forecast"] != True and context.user_data["getinfo"] != True:
        # get live crowd level
        suggest = True
        r = getcrowdlevel(context.user_data["school"], context.user_data["level"])
        if r.json() == {} and r.status_code==200:
            update.message.reply_text("This bot is still currently in beta testing. This part of the function is not implemented yet. Please try again.",
            reply_markup=ReplyKeyboardMarkup(keyboards["level_keyboard"], 
            resize_keyboard=True, 
            one_time_keyboard=True))
            return None
        results = r.json()
        threshold = 0
        crowdlevelresult = ["🌈Here are the results!!!"]
        crowdlevelresult.append("The current occupancy of {} {} study areas are as follows:\n".format(context.user_data["school"], context.user_data["level"]))
        for k, v in results.items():
            s = "{}: {}/{} ({}%)".format(k, str(v["current"]), str(v["max"]), str(round(v["percentage"],1)))
            if v["percentage"] > 100:
                s += " ‼This area is experiencing a surge in crowds‼"
            crowdlevelresult.append(s)
            if v["percentage"] >= 70:
                threshold += 1
        if len(results) == 1:
            if threshold == len(results):
                suggest = True
        else:
            if threshold == len(results) - 1: # check if most study areas are crowded on the specified level
                suggest = True
        t = "\n".join(crowdlevelresult)
        update.message.reply_text(t)
        imageurl = getimage(context.user_data["school"], context.user_data["level"]).json()
        update.message.reply_photo(photo=imageurl, caption="Here is the floor plan for {} {}!".format(context.user_data["school"], context.user_data["level"]))

        if suggest == True:
            update.message.reply_text(looksfulltext.format(context.user_data["school"], context.user_data["level"], context.user_data["school"]),
            reply_markup=ReplyKeyboardMarkup(keyboards["suggest_keyboard"],
            resize_keyboard=True, one_time_keyboard=True))
            return ALTERNATIVE
        update.message.reply_text(feedback1text,    
        reply_markup=ReplyKeyboardMarkup(keyboards["rating"],
        resize_keyboard=True, one_time_keyboard=True))
        return FEEDBACK1

    # get forcasted crowds 
    elif context.user_data["forecast"] == True and context.user_data["getinfo"] != True:
        r = getforecast(context.user_data["f_time"], context.user_data["school"], context.user_data["level"])
        if r.json() == {} and r.status_code==200:
            update.message.reply_text("This bot is still currently in beta testing. This part of the function is not implemented yet. Please try again.",
            reply_markup=ReplyKeyboardMarkup(keyboards["level_keyboard"], 
            resize_keyboard=True, 
            one_time_keyboard=True))         
            return None
        results = r.json()
        forecastresult = ["🌈Here are the results!!!"]
        forecastresult.append("The predicted occupancy rates of {} {} on {} at {} are as follows:\n".format(context.user_data["school"], context.user_data["level"], context.user_data["f_day"], context.user_data["f_time"]))

        for k, v in results.items():
            s = "{}: {}/{} ({}%)".format(k, str(v["current"]), str(v["max"]), str(round(v["percentage"],1)))
            if v["percentage"] > 100:
                s += " ‼This area might experience a surge in crowds‼"
            forecastresult.append(s)
        t = "\n".join(forecastresult)
        update.message.reply_text(t)
        imageurl = getimage(context.user_data["school"], context.user_data["level"]).json()
        update.message.reply_photo(photo=imageurl, caption="Here is the floor plan for {} {}!".format(context.user_data["school"], context.user_data["level"]))

        update.message.reply_text(feedback1text,    
        reply_markup=ReplyKeyboardMarkup(keyboards["rating"],
        resize_keyboard=True, one_time_keyboard=True))
        return FEEDBACK1

    # get floorplan
    elif context.user_data["forecast"] != True and context.user_data["getinfo"] == True:
        r = getimage(context.user_data["school"], context.user_data["level"])
        if r.status_code != 200:
            update.message.reply_text("This bot is still currently in beta testing. This part of the function is not implemented yet. Please try again.",
            reply_markup=ReplyKeyboardMarkup(keyboards["level_keyboard"], 
            resize_keyboard=True, 
            one_time_keyboard=True))         
            return None
        imageurl = r.json()
        update.message.reply_photo(photo=imageurl, caption="Here is the floor plan for {} {}!".format(context.user_data["school"], context.user_data["level"]))
        update.message.reply_text(feedback1text,    
        reply_markup=ReplyKeyboardMarkup(keyboards["rating"],
        resize_keyboard=True, one_time_keyboard=True))
        return FEEDBACK1

class LevelFilter(BaseFilter):
    def filter(self, message):
        return message.text is not None and message.text in ['Level 5', 'Level 4', 'Level 3', 'Level 2', "Level B1"]
levelfilter = LevelFilter()

# getalternatives when level is crowded
def alternativeshandler(update, context):
    if update.message.text == "End":
        update.message.reply_text(feedback1text,    
        reply_markup=ReplyKeyboardMarkup(keyboards["rating"],
        resize_keyboard=True, one_time_keyboard=True))
        return FEEDBACK1 

    update.message.reply_text(alternativesuggestiontext.format(context.user_data["school"]))
    r = getalternatives(context.user_data["school"], context.user_data["level"])
    if r.status_code==200 and r.json()=={}:
        update.message.reply_text("This bot is still currently in beta testing. This part of the function is not implemented yet. Please try again.")        
        return ConversationHandler.END 
    results = r.json()
    alternativeresult = ["🌈Here are the results!!!"]
    alternativeresult.append("Here are the top 3 most empty study areas in {}:\n".format(context.user_data["school"]))
    areasforimage = []
    for i in results:
        alternativeresult.append("{}: {}/{} ({}%)".format(i[0], i[1]["current"], i[1]["max"], round(i[1]["percentage"],1)))
        area = i[0].split(" ")
        area = (area[0], area[1])
        if area not in areasforimage:
            areasforimage.append(area)
    t = "\n".join(alternativeresult)
    update.message.reply_text(t)
    for i in areasforimage:
        imageurl = getimage(i[0], i[1]).json()
        update.message.reply_photo(photo=imageurl, caption="Here is the floor plan for {} {}!".format(i[0], i[1]))
    update.message.reply_text(feedback1text,
    reply_markup=ReplyKeyboardMarkup(keyboards["rating"],
    resize_keyboard=True, one_time_keyboard=True))
    return FEEDBACK1

class AlternativeFilter(BaseFilter):
    def filter(self, message):
        return message.text is not None and message.text in ["Find me alternatives!", "End"]
alternativefilter = AlternativeFilter()

# gather feedback rating
def feedback1(update, context):
    context.user_data["rating"] = int(update.message.text)
    update.message.reply_text("Thank you for your rating!\n\n"+feedback2text, reply_markup=ReplyKeyboardRemove())
    return FEEDBACK2

class Feedback1Filter(BaseFilter):
    def filter(self, message):
        try:
            text = int(message.text)
        except Exception as e:
            return False
        return message.text is not None and text in range(1,6)
feedback1filter = Feedback1Filter()

# gather feedback text
def feedback2(update,context):
    feedback = update.message.text 
    if context.user_data["school"] is None:
        context.user_data["school"] = "-"
    if context.user_data["level"] is None:
        context.user_data["level"] = "-"
    if feedback is None:
        placeholder_feedback = "-"
        r = postfeedback(update, context.user_data["rating"], placeholder_feedback, context.user_data["school"], context.user_data["level"])
        if r.status_code == 201:
            update.message.reply_text("Thank you for your feedback!\nHope to see you again!\n\nType /start to start the bot again")
        else:
            update.message.reply_text("Oops, an error occured! Please try submitting your feedback again.")
            return None
        return ConversationHandler.END
    r = postfeedback(update, context.user_data["rating"], feedback, context.user_data["school"], context.user_data["level"])
    if r.status_code == 201:
        update.message.reply_text("Thank you for your feedback!\nHope to see you again!\n\nType /start to start the bot again")
        return ConversationHandler.END
    else:
        update.message.reply_text("Oops, an error occured! Please try submitting your feedback again.")
        return None

class Feedback2Filter(BaseFilter):
    def filter(self, message):
        c = ["/start", "/restart", "/stop"]
        return message.text is not None and message.text not in c
feedback2filter = Feedback2Filter()

# for forecasting: handle day
def dayhandler(update, context):
    answer = update.message.text
    day_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    day = [d for d in day_list if answer in d]
    if day == []:
        update.message.reply_text("Weekend forecasting not implemented yet.\n\nPlease try again.",
        reply_markup=ReplyKeyboardMarkup(keyboards["day_keyboard"],
        resize_keyboard=True, one_time_keyboard=True))
        return None
    context.user_data["f_day"] = day[0]
    update.message.reply_text(asktime, reply_markup=ReplyKeyboardRemove())
    return ASKTIME

class DayFilter(BaseFilter):
    def filter(self, message):
        return message.text is not None and message.text in ["Mon", "Tue", "Wed", "Thur", "Fri"]
dayfilter = DayFilter()

# for forecasting: handle time
def timehandler(update, context):
    context.user_data["f_time"] = update.message.text
    update.message.reply_text(whichschooltext, 
    reply_markup=ReplyKeyboardMarkup(keyboards["location_keyboard"], 
    resize_keyboard=True, one_time_keyboard=True))
    return ASKSCHOOL

class TimeFilter(BaseFilter):
    def filter(self, message):
        pattern = re.compile("^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
        return message.text is not None and bool(re.search(pattern, message.text))
timefilter = TimeFilter()

# Error handling 
def errorhandler(update, context):
    if update.message.text in ["Sat", "Sun", "Saturday", "Sunday"] and context.user_data["forecast"]:
        update.message.reply_text("This bot is still currently in beta testing. Weekend forecasting not implemented yet.\n\nPlease try again.",
        reply_markup=ReplyKeyboardMarkup(keyboards["day_keyboard"],
        resize_keyboard=True, one_time_keyboard=True))
        return None 
    update.message.reply_text("You typed something that I did not understand. Please try again!")
    return None 

class ReverseDecideFunctionFilter(BaseFilter):
    def filter(self, message):
        c = ["/start", "/restart", "/stop"]
        return message.text is None or message.text not in ['Show current crowd level', "Forecast crowds", "Floor plan", "Crash GSR, Submit feedback"] and message.text not in c
reverse_decidefunctionfilter = ReverseDecideFunctionFilter()

class ReverseDayFilter(BaseFilter):
    def filter(self, message):
        c = ["/start", "/restart", "/stop"]
        return message.text is None or message.text not in ["Mon", "Tue", "Wed", "Thur", "Fri"] and message.text not in c
reverse_dayfilter = ReverseDayFilter()

class ReverseTimeFilter(BaseFilter):
    def filter(self, message):
        c = ["/start", "/restart", "/stop"]
        pattern = re.compile("^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
        return message.text is None or not bool(re.search(pattern, message.text)) and message.text not in c
reverse_timefilter = ReverseTimeFilter()

class ReverseSchoolFilter(BaseFilter):
    def filter(self,message):
        c = ["/start", "/restart", "/stop"]
        l = ["Connexion", 'KGC', 'LKS Library', 'SIS', 'SOA', 'SOB','SOE/SOSS','SOL']
        return message.text is None or message.text not in l and message.text not in c
reverse_schoolfilter = ReverseSchoolFilter()

class ReverseLevelFilter(BaseFilter):
    def filter(self, message):
        c = ["/start", "/restart", "/stop"]
        return message.text is None or message.text not in ['Level 5', 'Level 4', 'Level 3', 'Level 2', "Level B1"] and message.text not in c
reverse_levelfilter = ReverseLevelFilter()

class ReverseAlternativeFilter(BaseFilter):
    def filter(self, message):
        c = ["/start", "/restart", "/stop"]
        return message.text is None or message.text not in ["Find me alternatives!", "End"] and message.text not in c
reverse_alternativefilter = ReverseAlternativeFilter()

class ReverseFeedback1Filter(BaseFilter):
    def filter(self, message):
        c = ["/start", "/restart", "/stop"]
        try:
            text = int(message.text)
        except Exception as e:
            return message.text not in c or message.text is None
        return message.text is None or text not in range(1,6) and message.text not in c
reverse_feedback1filter = ReverseFeedback1Filter()

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("restart", restart)],

        states={
            CHOOSE_FUNCTION: [MessageHandler(decidefunctionfilter, decidefunction), MessageHandler(reverse_decidefunctionfilter, errorhandler)],
            ASKDAY: [MessageHandler(dayfilter, dayhandler), MessageHandler(reverse_dayfilter, errorhandler)], 
            ASKTIME: [MessageHandler(timefilter, timehandler), MessageHandler(reverse_timefilter, errorhandler)],
            ASKSCHOOL: [MessageHandler(schoolfilter, schoolhandler), MessageHandler(reverse_schoolfilter, errorhandler)],
            ASKLEVEL: [MessageHandler(levelfilter, levelhandler), MessageHandler(reverse_levelfilter, errorhandler)],
            ALTERNATIVE: [MessageHandler(alternativefilter, alternativeshandler), MessageHandler(reverse_alternativefilter, errorhandler)],
            FEEDBACK1: [MessageHandler(feedback1filter, feedback1), MessageHandler(reverse_feedback1filter, errorhandler)],
            FEEDBACK2: [MessageHandler(feedback2filter, feedback2)]
        }, 

        fallbacks=[CommandHandler("stop", stop), CommandHandler("restart", restart), CommandHandler("start", start)]
    )


    dp.add_handler(conv_handler)    

    # updater.start_polling()
    # updater.idle()

    updater.start_webhook(listen="0.0.0.0",port=int(PORT),url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    updater.idle()
if __name__ == "__main__":
    main()