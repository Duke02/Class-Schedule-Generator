from ics import Calendar, Event
from datetime import datetime, timedelta
from pytz import timezone

def localTimeToUTC(dt):
    if dt.tzinfo is not None:
        return dt # We assume it's already been through this process.
    centralDT = timezone("US/Central").localize(dt)
    return centralDT

def dateTimeToICS(datetime):
    return datetime.strftime("%Y%m%d %H:%M:%S")

def ICSToDateTime(icsTime):
    return datetime.strptime(icsTime, "%Y%m%d %H:%M:%S")

def nextWeekday(d, weekday):
    daysAhead = weekday - d.weekday()
    if daysAhead <= 0: # Target day already happened this week
        daysAhead += 7
    return localTimeToUTC(d + timedelta(daysAhead))

def getAllDTs(startOfClass, endOfClass, endOfSemester, daysOfClass):
    output = [(localTimeToUTC(startOfClass), localTimeToUTC(endOfClass))]
    nextDT = localTimeToUTC(startOfClass)
    while nextDT.month is not endOfSemester.month or nextDT.day <= endOfSemester.day:
        for weekday in daysOfClass:
            nextDT = localTimeToUTC(nextWeekday(nextDT, weekday))
            output.append((nextDT, localTimeToUTC(datetime(nextDT.year, nextDT.month, nextDT.day, hour=endOfClass.hour, minute=endOfClass.minute))))
    return output

def makeClass(calendar, classesStartDate, classesEndDate):
    startOfSemesterDT = ""
    endOfSemesterDT = ""
    startOfSemesterICS = ""
    endOfSemesterICS = ""
    if type(classesStartDate) is str:
        startOfSemesterDT = localTimeToUTC(ICSToDateTime(classesStartDate))
        endofSemesterDT = localTimeToUTC(ICSToDateTime(classesEndDate))
        startOfSemesterICS = classesStartDate
        endOfSemesterICS = classesEndDate
    else:
        startOfSemesterDT = localTimeToUTC(classesStartDate)
        endOfSemesterDT = localTimeToUTC(classesEndDate)
        startOfSemesterICS = dateTimeToICS(localTimeToUTC(classesStartDate))
        endOfSemesterICS = dateTimeToICS(localTimeToUTC(classesEndDate))
    
    name = input("What is the class name? ")
    daysOfClassChars = input("What are the days for the class? (MTWRFSU) ")
    location = input("Where is the class held? ")
    professor = input("Who is the professor? ")
    startTime = input("When does the class start? (HH:MM) ")
    endTime = input("When does the class end? (HH:MM) ")
    
    
    days = ['M', 'T', 'W', 'R', 'F', 'S', 'U']
    weekdayOfStartOfSemester = startOfSemesterDT.weekday() % len(days)
    weekdayOfStartOfClass = 0
    for i in range(weekdayOfStartOfSemester, len(days)):
        for dayChar in daysOfClassChars:
            if days[i] is dayChar:
                weekdayOfStartOfClass = i
    weekdaysOfClassInts = []
    for dayOfClass in daysOfClassChars:
        for i in range(0, len(days)):
            if dayOfClass is days[i]:
                weekdaysOfClassInts.append(i)
    nextDT = nextWeekday(startOfSemesterDT, weekdayOfStartOfClass)
    classStart = localTimeToUTC(datetime(nextDT.year, nextDT.month, nextDT.day, hour=int(startTime[:2]), minute=int(startTime[3:])))
    classEnd = localTimeToUTC(datetime(classStart.year, classStart.month, classStart.day, hour=int(endTime[:2]), minute=int(endTime[3:])))
    
    allDTs = getAllDTs(classStart, classEnd, endOfSemesterDT, weekdaysOfClassInts)
    
    events = []
    for dates in allDTs:
        temp = Event()
        temp.name = str(name)
        temp.description = "Professor: " + str(professor)
        temp.begin = dates[0]
        temp.end = dates[1]
        temp.location = str(location)
        events.append(temp)
    
    return events
    

def main():
    c = Calendar()
    shouldContinue = True
    while shouldContinue:
        events = makeClass(c, datetime.strptime("2018-08-14", "%Y-%m-%d"), datetime.strptime("2018-12-07", "%Y-%m-%d"))
        for e in events:
            c.events.append(e)
        shouldContinue = input("Would you like to continue? (Y/N) ")[0] is 'y'
    with open('uahClasses.ics', 'w') as f:
        f.writelines(c)


if __name__ == "__main__":
    main()
