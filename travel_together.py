import requests
import datetime
import sys
import webbrowser

scyscanner_key = input('Scyscanner API key: ')
weather_key = input('Weather API key: ')

def sightseeing(cities,cityCode,scyscanner_key):
    sights = dict()
    print("Sights of " + cities[cityCode].capitalize() + ":")
    url = "https://geocoding-by-api-ninjas.p.rapidapi.com/v1/geocoding"
    querystring = {"city":cities[cityCode].capitalize()}
    headers = {
    	"X-RapidAPI-Key": scyscanner_key,
    	"X-RapidAPI-Host": "geocoding-by-api-ninjas.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    re = response.json()

    url = "https://opentripmap-places-v1.p.rapidapi.com/en/places/radius"
    querystring = {"radius":"500","lon":str(re[0]['longitude']),"lat":str(re[0]['latitude']),"rate":3}
    headers = {
    	"X-RapidAPI-Key": "60781e5352msh702035f83523cfep19daa5jsn924e64defedc",
    	"X-RapidAPI-Host": "opentripmap-places-v1.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    re2 = response.json()
    for thing in re2['features']:
        if thing['properties']['kinds'].split(",")[0] in sights:
            sights[thing['properties']['kinds'].split(",")[0]].append(thing['properties']['name'])
        else:
            sights[thing['properties']['kinds'].split(",")[0]] = [thing['properties']['name']]
    for key in sights:
        print(key.upper())
        print(sights[key])
        print("\n")
        
        

url = "https://skyscanner-api.p.rapidapi.com/v3e/flights/live/search/synced"

origins = 2
minCommonDays = 2
people = [1,1]
origin = ["SKG","ATH"] # Example origins
direct = [True, True]
destinations = [["WAW", "BUD", "CIA", "ZAG", "BTS", "DUS"], ["BUD", "CIA", "ZAG", "WAW", "BTS", "DUS"]] # Example destinations
cities = dict()
cities["WAW"] = 'warsaw'
cities["BUD"] = "budapest"
cities["CIA"] = "rome"
cities["ZAG"] = "zagreb"
cities["BTS"] = "bratislava"
cities["DUS"] = "dusseldorf"

countries = dict()
countries["warsaw"] = 'poland'
countries["budapest"] = "hungary"
countries["rome"] = "italy"
countries["zagreb"] = "croatia"
countries["bratislava"] = "slovakia"
countries["dusseldorf"] = "germany"

earliestDate = ["2024-11-15","2024-11-15"] # Example dates
earliestDateSpelled = []
for eD in earliestDate:
    earliestDateSpelled.append(eD.split("-"))
maxDaysAfter = [2,2] 
stays = [[3,4,5],[3,4,5]]

goodFlights = []
prices = []
dateList = []
destinationsList = []
mins = []
weathers = []
topPicksInfo = set()

botchedAttempts = 0
expectedRequests = 0
retries = 3
for i in range(origins):
    expectedRequests += len(destinations[i]) * (maxDaysAfter[i] + 1) * len(stays[i])
 
    
print("The number of expected requests is " + str(expectedRequests) + ".")
print("The maximum nubmer of requests with this query is " + str(expectedRequests * retries) + ".")
cont = input("Do you wish to continue? If so, type '1': \n")

if cont == "1":
    queries = 1
    print("Your query is being processed.")
    
    if origins > 1:
        combos = []
        combAbsPrices = []
        combRelPrices = []
    
    for i in range(origins):
        goodFlights.append([])
        prices.append([])
        dateList.append([])
        destinationsList.append([])
        
        for day in range(maxDaysAfter[i]+1):
            dateGo = str(datetime.datetime(int(earliestDateSpelled[i][0]),int(earliestDateSpelled[i][1]),int(earliestDateSpelled[i][2])) + datetime.timedelta(days=day))[:10]
            goDate = dateGo.split("-")
            startDate = datetime.datetime(int(goDate[0]),int(goDate[1]),int(goDate[2]))
            for stay in stays[i]:
                dateReturn = str(startDate + datetime.timedelta(days=stay))[:10]
                returnDate = dateReturn.split("-")      
                for destination in destinations[i]:
                    print("Progress: " + str(100*queries/expectedRequests)[:5] + "%")
                    queries += 1
                    
                    itineraries = dict()
                    legs = dict()
                    cheapFlightsList = []
                    directFlightIds = []
                    
                    payload = { "query": {
                    		"market": "GR",
                    		"locale": "en-GB",
                    		"currency": "EUR",
                    		"queryLegs": [
                    			{
                    				"originPlaceId": { "iata": origin[i] },
                    				"destinationPlaceId": { "iata": destination },
                    				"date": {
                     					"year": int(goDate[0]),
                     					"month": int(goDate[1]),
                     					"day": int(goDate[2])
                    				}
                    			},
                                {
                    				"originPlaceId": { "iata": destination },
                    				"destinationPlaceId": { "iata": origin[i] },
                    				"date": {
                    					"year": int(returnDate[0]),
                    					"month": int(returnDate[1]),
                    					"day": int(returnDate[2])
                    				}
                    			}
                    		],
                    		"cabinClass": "CABIN_CLASS_ECONOMY",
                    		"adults": people[i],
                    	} }
                    headers = {
                    	"content-type": "application/json",
                    	"X-RapidAPI-Key": "60781e5352msh702035f83523cfep19daa5jsn924e64defedc",
                    	"X-RapidAPI-Host": "skyscanner-api.p.rapidapi.com"
                    }
                    
                    for tries in range(retries):
                        try:
                            response = requests.post(url, json=payload, headers=headers)
                            js = response.json()
                            for attribute, value in js['content']['results']['legs'].items():
                                legs[attribute] = value
                            for attribute, value in js['content']['results']['itineraries'].items():
                                itineraries[attribute] = value
                            break
                        except:
                            botchedAttempts += 1
                            continue
                        
                    try:
                        cheapFlightsList.extend(js['content']['sortingOptions']['cheapest'])
                    except:
                        raise Exception("Something is wrong at the moment, try again later.")
                    
                    flightIds = []
                    for flight in cheapFlightsList:
                        flightIds.append(flight['itineraryId'])
                    
                    for key in flightIds:
                        keys = key.split("|")
                        if ~direct[i] or (legs[keys[0]]['stopCount'] == 0 and legs[keys[1]]['stopCount'] == 0):
                            directFlightIds.append(key)
                    
                            
                    for key in directFlightIds[:10]:
                        keys = key.split("|")
                        info = []
                        dateTime = legs[keys[0]]['departureDateTime']
                        sDate = datetime.date(dateTime['year'], dateTime['month'], dateTime['day'])
                        goodDateTimeGo = str(dateTime['year']) + '-' + str(dateTime['month']) + '-' + str(dateTime['day']) + ', ' + str(dateTime['hour']) + ':' + str(dateTime['minute'])  
                        info.append('From: ' + origin[i])
                        info.append('To: ' + destination)
                        info.append(goodDateTimeGo)
                        info.append(str(legs[keys[0]]['durationInMinutes']) + ' minutes')
                        dateTime = legs[keys[1]]['departureDateTime']
                        eDate = datetime.date(dateTime['year'], dateTime['month'], dateTime['day'])
                        goodDateTimeReturn = str(dateTime['year']) + '-' + str(dateTime['month']) + '-' + str(dateTime['day']) + ', ' + str(dateTime['hour']) + ':' + str(dateTime['minute'])  
                        info.append('From: ' + destination)
                        info.append('To: ' + origin[i])
                        info.append(goodDateTimeReturn)
                        info.append(str(legs[keys[1]]['durationInMinutes']) + ' minutes')
                        info.append(itineraries[key]['pricingOptions'][0]['price']['amount'] + ' euro')
                        goodFlights[i].append(info)
                        prices[i].append(float(itineraries[key]['pricingOptions'][0]['price']['amount']))
                        dates = []
                        while sDate <= eDate:
                            dates.append(sDate.isoformat())
                            sDate += datetime.timedelta(days=1)
                        dateList[i].append(dates)
                        destinationsList[i].append(destination)
                        
        mins.append(min(prices[i]))
        prices[i], goodFlights[i], dateList[i], destinationsList[i] = (list(t) for t in zip(*sorted(zip(prices[i], goodFlights[i], dateList[i], destinationsList[i]))))    
      
    if origins == 2:
        for i in range(len(prices[0])):
            for j in range(len(prices[1])):
                if cities[destinationsList[0][i]] == cities[destinationsList[1][j]] and len(set(dateList[0][i]).intersection(set(dateList[1][j]))) >= minCommonDays:
                    combAbsPrices.append(prices[0][i] + prices[1][j])
                    combRelPrices.append(prices[0][i]/mins[0]*people[0] + prices[1][j]/mins[1]*people[1]/sum(people))
          
        minRel = min(combRelPrices)
        for i in range(len(prices[0])):
            for j in range(len(prices[1])):
                if cities[destinationsList[0][i]] == cities[destinationsList[1][j]] and len(set(dateList[0][i]).intersection(set(dateList[1][j]))) >= minCommonDays:
                    tempLen = len(combos)
                    combRelPrices[tempLen] /= minRel
                    combos.append([goodFlights[0][i], goodFlights[1][j], 'Total price: ' + str(combAbsPrices[tempLen]) + ' euro', 'Average multiple of minimum: ' + str(combRelPrices[tempLen])])
                    
        combAbsPrices, combRelPrices, combos = (list(t) for t in zip(*sorted(zip(combAbsPrices, combRelPrices, combos))))  
        absBest = combos
        
        combRelPrices, combAbsPrices, combos = (list(t) for t in zip(*sorted(zip(combRelPrices, combAbsPrices, combos)))) 
        relBest = combos
        
        topPicks = [absBest[0],absBest[1],absBest[2],relBest[0],relBest[1],relBest[2]]
        
        for pick in topPicks:
            parts = pick[0][2].split(",")[0].split("-")
            year = parts[0]
            month = parts[1]
            if len(month) == 1:
                month = "0" + month
            day = parts[2]
            if len(day) == 1:
                day = "0" + day
            dateGo1 = year + "-" + month + "-" + day
            date1 = datetime.date(int(year),int(month),int(day))
            parts = pick[1][2].split(",")[0].split("-")
            year = parts[0]
            month = parts[1]
            if len(month) == 1:
                month = "0" + month
            day = parts[2]
            if len(day) == 1:
                day = "0" + day
            dateGo2 = year + "-" + month + "-" + day
            date2 = datetime.date(int(year),int(month),int(day))
            if date1 < date2:
                dateGo = dateGo1
            else:
                dateGo = dateGo2
            
            parts = pick[0][6].split(",")[0].split("-")
            year = parts[0]
            month = parts[1]
            if len(month) == 1:
                month = "0" + month
            day = parts[2]
            if len(day) == 1:
                day = "0" + day
            dateRet1 = year + "-" + month + "-" + day
            date1 = datetime.date(int(year),int(month),int(day))
            parts = pick[1][6].split(",")[0].split("-")
            year = parts[0]
            month = parts[1]
            if len(month) == 1:
                month = "0" + month
            day = parts[2]
            if len(day) == 1:
                day = "0" + day
            dateRet2 = year + "-" + month + "-" + day
            date2 = datetime.date(int(year),int(month),int(day))
            if date1 > date2:
                dateRet = dateRet1
            else:
                dateRet = dateRet2
            topPicksInfo.add(cities[pick[0][1][4:]] + '-' + countries[cities[pick[0][1][4:]]] + '!' + dateGo + '!' + dateRet)
                
            response = requests.request("GET", "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"+cities[pick[0][1][4:]]+"/" + dateGo + "/" + dateRet + "?unitGroup=metric&key="+weather_key+"&contentType=json")
            if response.status_code!=200:
              print('Unexpected Status code: ', response.status_code)
              sys.exit()  
            jsonData = response.json()
            weather = []
            for day in jsonData["days"]:
                weather.append(day["datetime"] + ": " + " Weather: " + day["conditions"] + " Min temperature: " + str(day["tempmin"]) + " Max temperature: " + str(day["tempmax"]))
            weathers.append(weather)
        
        print('Absolute top 3:')
        print(["1: ", absBest[0]])
        for condition in weathers[0]:
            print(condition)
        print("\n")
        sightseeing(cities,absBest[0][0][1][4:],scyscanner_key)
        print("\n")
        
        print(["2: ", absBest[1]])
        for condition in weathers[1]:
            print(condition )
        print("\n")
        sightseeing(cities,absBest[1][0][1][4:],scyscanner_key)
        print("\n")
        
        print(["3: ", absBest[2]])
        for condition in weathers[2]:
            print(condition)
        print("\n")
        sightseeing(cities,absBest[2][0][1][4:],scyscanner_key)
        print("\n")
        
        
        print('Relative top 3:')
        print(["1: ", relBest[0]])
        for condition in weathers[3]:
            print(condition)
        print("\n")
        sightseeing(cities,relBest[0][0][1][4:],scyscanner_key)
        print("\n")
        
        print(["2: ", relBest[1]])
        for condition in weathers[4]:
            print(condition)
        print("\n")
        sightseeing(cities,relBest[1][0][1][4:],scyscanner_key)
        print("\n")
        
        print(["3: ", relBest[2]])
        for condition in weathers[5]:
            print(condition)
        print("\n")
        sightseeing(cities,relBest[2][0][1][4:],scyscanner_key)
        
        for pick in topPicksInfo:
            pickList = pick.split("!")
            webbrowser.open('https://www.bandsintown.com/c/' + pickList[0] + '/choose-dates/genre/all-genres?calendarTrigger=false&date=' + pickList[1] + 'T00%3A00%3A00%2C' + pickList[2] + 'T23%3A00%3A00', new=2)
            webbrowser.open('https://traveltables.com/country/' + pickList[0].split("-")[1] + '/city/' + pickList[0].split("-")[0] + '/cost-of-living/', new=2)
        
        
    print("Failed requests: " + str(botchedAttempts))
    print("Total requests: " + str(expectedRequests + botchedAttempts))
    

else:
    print("Please review the parameters of your query and try again.")
            
    

        
    