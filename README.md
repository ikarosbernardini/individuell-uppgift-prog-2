# Dagens elpris

Ett enkelt Flask‑projekt som hämtar och visar elpriser för de svenska elområdena (SE1–SE4) via [elprisetjustnu.se](https://www.elprisetjustnu.se/).  
Användaren kan se aktuella priser, söka på ett specifikt datum och område, samt få en tabell med tim- eller kvartpriser beroende på datum.

---

## Kom igång

1. Klona projektet
Instruktioner

För att köra projektet lokalt behöver du först klona repot och gå in i projektmappen:

git clone https://github.com/ikarosbernardini/individuell-uppgift-prog-2.git

cd individuell-uppgift-prog-2

2. Skapa sedan en virtuell miljö och aktivera den:

python3 -m venv venv

source venv/bin/activate # Linux/Mac venv\Scripts\activate # Windows

3. Installera alla beroenden från requirements.txt:

pip install -r requirements.txt

4. Gå därefter in i application-mappen och starta appen:

cd application

flask --app app run

5. Öppna sedan i webbläsaren:

http://127.0.0.1:5000


***Källor***

Jag har använt mig av samma gränssnitt som mitt andra projekt : https://github.com/ikarosbernardini/grupp-uppgift-prog-2 och en del funktioner så som leafly kartan och liknande.

Samt följande API:er och hemsidor :
El api : https://www.elprisetjustnu.se/api/v1/prices/
Kart api : https://leafletjs.com/
Geolocation HTML : https://www.w3schools.com/html/html5_geolocation.asp
HTML strukturering : https://getbootstrap.com/
Jinja strukturering : https://jinja.palletsprojects.com/en/stable/templates/
Flask quickstart : https://flask.palletsprojects.com/en/stable/quickstart/

Även använt mig utav Copilot och ollama : qwen3-coder:480b-cloud




- Ikaros Bernardini
