from datetime import date, datetime, time
from urllib.parse import quote_plus
import requests
import calendar
from flask import Flask, render_template, json, redirect, request, jsonify

app = Flask(__name__)

beaches = (
    "240160",
    "240140",
    "240151",
    "220050",
    '270170',
    '270170',
    '240265',
    '250260',
    '250512',
    '260380',
    '250900',
    '280640',
    '280680',
    '280570',
    '280975',
    '281050',
    '281140',
    '280080',
    '280825',
    '280820',
    '270460',
    '270470',
    '280710',
    '270300',
    '270440',
    '270480',
    '270310',
    '270380',
    '270200',
    '270500',
    '250510',
    '260740',
    '240150')

def lows(data, dootoo):
    """
    reduces data to only low tides below MLW
    """
    data = [item for item in data["predictions"] if item["type"] == "L" and float(item["v"]) < 2.83]

    for item in data:
        tide_datetime = datetime.fromisoformat(item["t"])
        day = tide_datetime.day

        item["dawn"] = dootoo["results"][day-1]["dawn"]
        item["dusk"] = dootoo["results"][day-1]["dusk"]
        item["date"] = tide_datetime.strftime('%a, %b %d %Y, %I:%M %p')

        del item["type"]

    data[:] = [item for item in data if datetime.strptime(item["dawn"], '%I:%M:%S %p').time() < \
            datetime.fromisoformat(item["t"]).time() < \
            datetime.strptime(item["dusk"], '%I:%M:%S %p').time()]

    return data

def days(month, year):
    """
    returns number of last day of month
    """
    lengths = {
        1:31,2: None,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31
    }
    endday = lengths[int(month)]

    if not endday:
        if int(year) % 4:
            endday = 28
        else:
            endday = 29

    return endday


def tide_request(month, year):
    """
    creates an api request string for tides of passed month and year
    """

    end_day = days(month, year)

    begin_date = year + month + "01"
    end_date = year + month + str(end_day)

    request = 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date='+begin_date+'&end_date=' + end_date + '&station=9447130&product=predictions&datum=MLLW&time_zone=lst_ldt&interval=hilo&units=english&application=test&format=json'
    return request

def sunlight_request(month, year):
    """
    creates an api request string for sunlight of passed month and year
    example: https://api.sunrisesunset.io/json?lat=38.907192&lng=-77.036873&timezone=UTC&date_start=1990-05-01&date_end=1990-07-01
    """

    end_day = days(month, year)

    begin_date = "-".join([year, month, "01"])
    end_date = "-".join([year, month, str(end_day)])

    request = 'https://api.sunrisesunset.io/json?lat=47.6061&lng=-122.3328&date_start='+begin_date+'&date_end='+end_date
    return request

def oyster_request(date: datetime):
    """
    creates an api request string to find beaches in set that are open
    translates year to current year to facilitate searching
    example: https://fortress.wa.gov/doh/arcgis2/arcgis/rest/services/Biotoxin/Biotoxin_v4/MapServer/6/query?where=GISDB.SDE.ShellfishBeaches.BIDN+IN+%28270480%2C+270310%2C+270380%2C+270200%2C+270500%2C+250510%2C+260740%2C+240150%29+AND+%28%28Ostartdate+%3C+TIMESTAMP+%272023-05-05+17%3A30%3A00%27+AND+TIMESTAMP+%272023-05-05+17%3A30%3A00%27+%3C+Oenddate%29+OR+%28Ostartdate+%3C+TIMESTAMP+%272024-05-05+17%3A30%3A00%27+AND+TIMESTAMP+%272024-05-05+17%3A30%3A00%27+%3C+Oenddate%29%29&outFields=*&returnGeometry=false&f=json
    GISDB.SDE.ShellfishBeaches.BIDN IN (270480, 270310, 270380, 270200, 270500, 250510, 260740, 240150) AND ((Ostartdate < TIMESTAMP '2023-05-05 17:30:00' AND TIMESTAMP '2023-05-05 17:30:00' < Oenddate) OR (Ostartdate < TIMESTAMP '2024-05-05 17:30:00' AND TIMESTAMP '2024-05-05 17:30:00' < Oenddate))
    """
    # date format yyyy-mm-dd hh:mm
    date = date.replace(year=datetime.now().year)   # data in system is based on current year
    new_date = date.replace(year=date.year+1)       # some seasons start in one year and end in the next

    beach_query = "GISDB.SDE.ShellfishBeaches.BIDN IN (" + ", ".join(beaches) + ") AND "
    date_query = "((Ostartdate < TIMESTAMP '" + date.strftime('%Y-%m-%d %H:%M') + "' AND TIMESTAMP '" + date.strftime('%Y-%m-%d %H:%M') + "' < Oenddate) OR "
    new_date_query = "(Ostartdate < TIMESTAMP '" + new_date.strftime('%Y-%m-%d %H:%M') + "' AND TIMESTAMP '" + new_date.strftime('%Y-%m-%d %H:%M') + "' < Oenddate))"

    combined_query = beach_query + date_query + new_date_query

    request = "https://fortress.wa.gov/doh/arcgis2/arcgis/rest/services/Biotoxin/Biotoxin_v4/MapServer/6/query?where=" + quote_plus(combined_query, safe='') + "&outFields=*&returnGeometry=false&f=json"

    return request

def clam_request(date: datetime):
    """
    creates an api request string to find beaches in set that are open during clam season
    translates year to current year to facilitate searching
    example: https://fortress.wa.gov/doh/arcgis2/arcgis/rest/services/Biotoxin/Biotoxin_v4/MapServer/6/query?where=GISDB.SDE.ShellfishBeaches.BIDN+IN+%28270480%2C+270310%2C+270380%2C+270200%2C+270500%2C+250510%2C+260740%2C+240150%29+AND+%28%28Cstartdate+%3C+TIMESTAMP+%272023-05-05+17%3A30%3A00%27+AND+TIMESTAMP+%272023-05-05+17%3A30%3A00%27+%3C+Cenddate%29+OR+%28Ostartdate+%3C+TIMESTAMP+%272024-05-05+17%3A30%3A00%27+AND+TIMESTAMP+%272024-05-05+17%3A30%3A00%27+%3C+Cenddate%29%29&outFields=*&returnGeometry=false&f=json
    GISDB.SDE.ShellfishBeaches.BIDN IN (270480, 270310, 270380, 270200, 270500, 250510, 260740, 240150) AND ((Cstartdate < TIMESTAMP '2023-05-05 17:30:00' AND TIMESTAMP '2023-05-05 17:30:00' < Cenddate) OR (Cstartdate < TIMESTAMP '2024-05-05 17:30:00' AND TIMESTAMP '2024-05-05 17:30:00' < Cenddate))
    """
    # date format yyyy-mm-dd hh:mm
    date = date.replace(year=datetime.now().year)   # data in system is based on current year
    new_date = date.replace(year=date.year+1)       # some seasons start in one year and end in the next

    beach_query = "GISDB.SDE.ShellfishBeaches.BIDN IN (" + ", ".join(beaches) + ") AND "
    date_query = "((Cstartdate < TIMESTAMP '" + date.strftime('%Y-%m-%d %H:%M') + "' AND TIMESTAMP '" + date.strftime('%Y-%m-%d %H:%M') + "' < Cenddate) OR "
    new_date_query = "(Cstartdate < TIMESTAMP '" + new_date.strftime('%Y-%m-%d %H:%M') + "' AND TIMESTAMP '" + new_date.strftime('%Y-%m-%d %H:%M') + "' < Cenddate))"

    combined_query = beach_query + date_query + new_date_query

    request = "https://fortress.wa.gov/doh/arcgis2/arcgis/rest/services/Biotoxin/Biotoxin_v4/MapServer/6/query?where=" + quote_plus(combined_query, safe='') + "&outFields=*&returnGeometry=false&f=json"

    return request


def beach_request():
    """
    creates an api request string to find beaches in set that are open
    translates year to current year to facilitate searching
    example: https://fortress.wa.gov/doh/arcgis2/arcgis/rest/services/Biotoxin/Biotoxin_v4/MapServer/6/query?where=GISDB.SDE.ShellfishBeaches.BIDN+IN+%28270480%2C+270310%2C+270380%2C+270200%2C+270500%2C+250510%2C+260740%2C+240150%29+AND+%28%28Ostartdate+%3C+TIMESTAMP+%272023-05-05+17%3A30%3A00%27+AND+TIMESTAMP+%272023-05-05+17%3A30%3A00%27+%3C+Oenddate%29+OR+%28Ostartdate+%3C+TIMESTAMP+%272024-05-05+17%3A30%3A00%27+AND+TIMESTAMP+%272024-05-05+17%3A30%3A00%27+%3C+Oenddate%29%29&outFields=*&returnGeometry=false&f=json
    GISDB.SDE.ShellfishBeaches.BIDN IN (270480, 270310, 270380, 270200, 270500, 250510, 260740, 240150) AND ((Ostartdate < TIMESTAMP '2023-05-05 17:30:00' AND TIMESTAMP '2023-05-05 17:30:00' < Oenddate) OR (Ostartdate < TIMESTAMP '2024-05-05 17:30:00' AND TIMESTAMP '2024-05-05 17:30:00' < Oenddate))
    """

    beach_query = "GISDB.SDE.ShellfishBeaches.BIDN IN (" + ", ".join(beaches) + ")"


    request = "https://fortress.wa.gov/doh/arcgis2/arcgis/rest/services/Biotoxin/Biotoxin_v4/MapServer/6/query?where=" + quote_plus(beach_query, safe='') + "&outFields=*&returnGeometry=false&f=json"

    return request


@app.route('/')
def root():
    return render_template("homepage.j2")

@app.route('/about')
def about():
    return render_template("about.j2")

@app.route('/rules')
def rules():
    return render_template("rules.j2")


@app.route('/beachsearch')
def beachsearch():
    
    data = requests.get(beach_request()).json()["features"]

    # return jsonify(data)

    return render_template("beachsearch.j2", data=data)

@app.route('/beachsearchdates', methods=["POST", "GET"])
def beachsearchdates():
    if request.method == "POST":
        start_raw = request.form["start"]
        end_raw = request.form["end"]
        beach = request.form["beach"]
        species = request.form["species"]

        start = int(start_raw) // 1000  # convert posix milliseconds to seconds
        end = int(end_raw) // 1000
        

        # convert start from posix to datetime and get month; in GMT but should be Pacific Time
        start = datetime.utcfromtimestamp(start).strftime('%m')
        end = datetime.utcfromtimestamp(end).strftime('%m')

        months = []     # list of months to search in string of two digit numbers, like "01"
        if int(start) > int(end):
            for i in range(int(start), 13):
                months.append(str(i).zfill(2))
            for i in range(1, int(end)+1):
                months.append(str(i).zfill(2))
        else:
            for i in range(int(start), int(end)+1):
                months.append(str(i).zfill(2))

        # dictionary of month numbers to month names
        month_names = {str(i).zfill(2): calendar.month_name[i] for i in range(1, 13)}

        species_type = "All Shellfish" if species == "1" else "Clams & Mussels"

        if species == "1":
            context = "Tides for " + species_type + " seasons at " + beach
        else:
            context = "Tides for " + species_type + " season at " + beach

        print(month_names)

        return render_template("beachsearchdates.j2", months=months, month_names=month_names, species=species, start=start_raw, end=end_raw, context=context, beach=beach)
    
    if request.method == "GET":
        return redirect("/beachsearch") 

@app.route('/beachsearchtides', methods=["POST", "GET"])
def beachsearchtides():
    if request.method == "POST":
        month = request.form["month"]
        year = request.form["year"]
        beach = request.form["beach"]
        species = request.form["species"]

        species_type = "All Shellfish" if species == "1" else "Clams & Mussels"


        data = requests.get(tide_request(month, year)).json()
        dootoo = requests.get(sunlight_request(month, year)).json()

        if species == "1":
            context = "Tides for " + species_type + " seasons at " + beach + " in " + calendar.month_name[int(month)] + " " + year
        else:
            context = "Tides for " + species_type + " season at " + beach + " in " + calendar.month_name[int(month)] + " " + year
        # return jsonify(data)
        return render_template("beachsearchtides.j2", data=lows(data, dootoo), date=calendar.month_name[int(month)] + " " + year, species=species, context=context, beach=beach)
    
    if request.method == "GET":
        return redirect("/beachsearch")


@app.route('/tidesearch')
def tidesearch():
    return render_template("tidesearch.j2")

@app.route("/tidesearchdates", methods=["POST", "GET"])
def tidesearchdates():
    if request.method == "POST":
        month = request.form["month"]
        year = request.form["year"]
        species = request.form["species"]

        data = requests.get(tide_request(month, year)).json()
        dootoo = requests.get(sunlight_request(month, year)).json()
        # return jsonify(data)
        return render_template("tidesearchdates.j2", data=lows(data, dootoo), date=calendar.month_name[int(month)] + " " + year, species=species)
    
    if request.method == "GET":
        return redirect("/tidesearch")


@app.route("/tidesearchbeaches", methods=["POST", "GET"])
def tidesearchbeaches():

    if request.method == "POST":

        date = datetime.fromisoformat(request.form["t"])
        tide = request.form["v"]
        species = request.form["species"]

        if species == "1":
            data = requests.get(oyster_request(date)).json()["features"]
            species = ", All Shellfish"
        else:
            data = requests.get(clam_request(date)).json()["features"]
            species = ", Clams & Mussels"

        context = tide + "' Tide, " + date.strftime('%A %B %d %Y at %I:%M %p') + species

        # return request.form["species"]
        # return jsonify(data)
        return render_template("tidesearchbeaches.j2", data=data, context=context)
    
    if request.method == "GET":
        return redirect("/tidesearch")

if __name__ == "__main__":

    #Start the app on port 2121, it will be different once hosted
    app.run(port=2121, host='localhost', debug=True)
