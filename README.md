# RECEPTLÅDAN

En plattform där man kan söka och läsa recept, skapa ett konto och logga in för att kunna skapa egna recept. 

### Funktioner
Startsidan listar alla recept i fallande ordning, senaste receptet först. Informationen på korten i varje recept hämtas ifrån databasen.
![Home page](/static/assets/index.png)

<br>

** Bedo, lägg till här! **
<br>
![Sign up](/static/assets/sign_up.png)

<br>

** Bedo, lägg till här! **
<br>
![Sign in](/static/assets/sign_in.png)

<br>

Här kan man lägga till sina recept, när ett recept är skapat läggs informationen i en databas. När användaren trycker på "Lägg upp!" så rensas formuläret för att man enkelt ska kunna lägga upp flera recept efter varandra.
![Add recipe](/static/assets/add_recipe.png)
![Add recipe](/static/assets/add_recipe2.png)

<br>

När man klickar sig in på ett specifikt recept hamnar man på detaljsidan. Informationen här hämtas ifrån databasen. Här kan man också radera sitt recept. 
![Recipe detail](/static/assets/recipe_detail.png)

---
### Docker & Azure

Vi har skapat en image i Docker som vi sedan har lagt som en containerinstans i Azure.
<br>

![Azure](/static/assets/Azure.png)
![Azure](/static/assets/Azure2.png)
![Azure](/static/assets/Azure3.png)

---

### Framtida möjliga implementationer

Om vi skulle fortsätta utveckla denna site hade vi gärna lagt till nedan funktioner: 
- Färdigställa möjligheten att leta recept i kategorier eller genom sökfältet.
- Lägga till egen bild.
- Något typ av betygsystem där man kan ange antal stjärnor för ett recept man har testat. 
- Möjlighet att kommentera recept man har testat.
- Vi vill också att man ska kunna redigera sina recept.

---

### Använda program
- Python
- HTML
- CSS
- JavaScript
- Flask
- Jinja
- Bootstrap

---
### Källor

Flask web forms:
<br>
https://www.digitalocean.com/community/tutorials/how-to-use-web-forms-in-a-flask-application

Hjälpmedel till struktur:
<br>
Codemy.com Flask-Fridays.

Skicka bild till databas:
<br>
https://wtforms.readthedocs.io/en/2.3.x/fields/