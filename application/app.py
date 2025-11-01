from flask import Flask, render_template, request, make_response
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

@app.route("/")
def index():
    today = datetime.now().date()
    year = request.cookies.get("last_year", str(today.year))
    month = request.cookies.get("last_month", str(today.month).zfill(2))
    day = request.cookies.get("last_day", str(today.day).zfill(2))
    area = request.cookies.get("last_area", "SE3") 

    # Hämta nu-priser för SE1–SE4
    areas = ["SE1", "SE2", "SE3", "SE4"]
    prices_now = {}
    stockholm_tz = pytz.timezone("Europe/Stockholm")
    now_local = datetime.now(stockholm_tz)
    current_hour = now_local.replace(minute=0, second=0, microsecond=0)

    for a in areas:
        url = f"https://www.elprisetjustnu.se/api/v1/prices/{year}/{month}-{day}_{a}.json"
        r = requests.get(url)
        if r.status_code == 200:
            d = pd.DataFrame(r.json())
            d["time_start"] = pd.to_datetime(d["time_start"], errors="coerce").dt.tz_convert(stockholm_tz)
            row = d[d["time_start"] == current_hour]
            if not row.empty:
                prices_now[a] = float(row.iloc[0]["SEK_per_kWh"])
            else:
                before = d[d["time_start"] <= current_hour].sort_values("time_start")
                prices_now[a] = float(before.iloc[-1]["SEK_per_kWh"]) if not before.empty else None
        else:
            prices_now[a] = None

    # Rendera startsidan (utan tabell)
    return render_template(
        "index.html",
        year=year, month=month, day=day, area=area,
        se1=prices_now.get("SE1"),
        se2=prices_now.get("SE2"),
        se3=prices_now.get("SE3"),
        se4=prices_now.get("SE4"),
    ) # Rendera sidan utan tabell och med live rutor



@app.route("/priser", methods=["GET", "POST"])
def el_api():
    year = request.form.get("year")
    month = request.form.get("month")
    day = request.form.get("day")
    area = request.form.get("area") 

    try:
        selected_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date() # Validera datum
    except ValueError:
        return render_template("incorrect-date.html"), 400

    # Bestäm rubrik beroende på datum
    if selected_date >= datetime(2025, 10, 1).date(): # från och med 1 okt 2025 är det kvartpriser
        table_title = "Kvartpriser (kr/kWh)" # ändrat från timpriser till kvartpriser
    else:
        table_title = "Timpriser (kr/kWh)" # ändrat från kvartpriser till timpriser

    min_date = datetime(2022, 11, 1).date() # tillåter från och med 1 nov 2022
    max_date = datetime.now().date() + timedelta(days=1) # tillåter nästa dag

    if selected_date < min_date:
        return render_template("low-date.html"), 400 # Fel för för gamla datum
    if selected_date > max_date:
        return render_template("high-date.html"), 400 # Fel för framtida datum

    # Säkerställ rätt format
    month = month.zfill(2) # fyller på med nolla om det behövs
    day = day.zfill(2) # används ifall användaren skriver in t.ex. 3 istället för 03

    el_url = f"https://www.elprisetjustnu.se/api/v1/prices/{year}/{month}-{day}_{area}.json"
    response = requests.get(el_url)
    if response.status_code != 200: 
        return render_template("api-error.html"), 502 # Fel vid API-anrop

    data = response.json()
    df = pd.DataFrame(data)
    df["time_start"] = pd.to_datetime(df["time_start"], errors="coerce").dt.strftime("%H:%M")

    # Lägg till enhet i kolumnen
    df["SEK_per_kWh"] = df["SEK_per_kWh"].round(5).astype(str) + " kr/kWh"

    # Byter namn på kolumnerna efter egen preferens
    df.rename(columns={
        "time_start": "Tid",
        "SEK_per_kWh": "Pris (kr/kWh)"
    }, inplace=True)

    table_data = df.to_html(
        columns=["Tid", "Pris (kr/kWh)"],
        classes="table table-striped table-bordered",
        index=False,
        justify="left"
    )

    # “Live” rutor: hämta samma datum för SE1–SE4 och plocka aktuell timme
    areas = ["SE1", "SE2", "SE3", "SE4"] # lista över elområden
    prices_now = {} # dictionary för att lagra priserna
    stockholm_tz = pytz.timezone("Europe/Stockholm") # Tidszon
    now_local = datetime.now(stockholm_tz) # Lokal tid
    current_hour = now_local.replace(minute=0, second=0, microsecond=0) # Aktuell timme

    for a in areas:
        url = f"https://www.elprisetjustnu.se/api/v1/prices/{year}/{month}-{day}_{a}.json" # Hämta prisdata
        r = requests.get(url) #
        if r.status_code == 200: 
            d = pd.DataFrame(r.json())
            d["time_start"] = pd.to_datetime(d["time_start"], errors="coerce").dt.tz_convert(stockholm_tz) # Konvertera till lokal tid
            row = d[d["time_start"] == current_hour]
            if not row.empty:
                prices_now[a] = float(row.iloc[0]["SEK_per_kWh"]) # Hämta priset för aktuell timme
            else:
                before = d[d["time_start"] <= current_hour].sort_values("time_start") # Felhantering
                prices_now[a] = float(before.iloc[-1]["SEK_per_kWh"]) if not before.empty else None # Felhantering
        else:
            prices_now[a] = None # Felhantering

    resp = make_response(render_template(
        "elpriser.html",
        price=table_data,
        year=year,
        month=month,
        day=day,
        area=area,
        se1=prices_now.get("SE1"),
        se2=prices_now.get("SE2"),
        se3=prices_now.get("SE3"),
        se4=prices_now.get("SE4"),
        table_title=table_title
    ))
    # sätt cookies för senaste sökning
    resp.set_cookie("last_year", year, max_age=60*60*24*30)   # 30 dagar
    resp.set_cookie("last_month", month, max_age=60*60*24*30)
    resp.set_cookie("last_day", day, max_age=60*60*24*30)
    resp.set_cookie("last_area", area, max_age=60*60*24*30)
    return resp # Rendera sidan med tabell och "live" rutor



@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
