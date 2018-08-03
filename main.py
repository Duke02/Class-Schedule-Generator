from ics import Calendar, Event
from datetime import datetime, timedelta
from pytz import timezone

# If dt has already been localized, don't do anything.
# Otherwise, localize the given datetime to Central US time.
def localTimeToUTC(dt):
    if dt.tzinfo is not None:
        return dt # We assume it's already been through this process.
    centralDT = timezone("US/Central").localize(dt)
    return centralDT

# Format the given datetime to Calendar date time format.
def dateTimeToICS(datetime):
    return datetime.strftime("%Y%m%d %H:%M:%S")

# Format the given ics time from Calendar date time format to python datetime format.
def ICSToDateTime(icsTime):
    return datetime.strptime(icsTime, "%Y%m%d %H:%M:%S")

# Get the next weekday from the week, converted to local time.
def nextWeekday(d, weekday):
    daysAhead = weekday - d.weekday()
    if daysAhead <= 0: # Target day already happened this week
        daysAhead += 7
    return localTimeToUTC(d + timedelta(daysAhead))

# Get all the datetimes for the course throughout the semester.
def getAllDTs(startOfClass, endOfClass, endOfSemester, daysOfClass):
    # Get starting and end of time for class.
    output = [(localTimeToUTC(startOfClass), localTimeToUTC(endOfClass))]
    nextDT = localTimeToUTC(startOfClass)
    # While we're not at the end of the semester
    while nextDT.month is not endOfSemester.month or nextDT.day <= endOfSemester.day:
        # For each day of class in the week,
        for weekday in daysOfClass:
            # Get the next date of class for that week.
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
    startOfSemester = str(input("When is the start of the semester? Format: YYYY-mm-dd"))
    endOfSemester = str(input("When is the end of the semester? Format: YYYY-mm-dd"))
    continueStatement = "Would you like to continue? (y/n)"
    while shouldContinue:
        events = makeClass(c, datetime.strptime(startOfSemester, "%Y-%m-%d"), datetime.strptime(endOfSemester, "%Y-%m-%d"))
        for e in events:
            c.events.append(e)
        shouldContinue = input(continueStatement)[0] is 'y' or input(continueStatement)[0] == 'y'
    with open('uahClasses.ics', 'w') as f:
        f.writelines(c)


if __name__ == "__main__":
    main()
