# Evidencija rada - faza 1: server s bazom podataka i korisnicima
# Pokretanje: python server.py  ->  http://127.0.0.1:8000/docs

import sqlite3

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

BAZA = "evidencija.db"
app = FastAPI(title="Evidencija rada")


def spoji():
    veza = sqlite3.connect(BAZA)
    veza.row_factory = sqlite3.Row  # da redovi izgledaju kao rjecnik
    return veza


def napravi_bazu():
    with spoji() as veza:
        veza.executescript("""
            CREATE TABLE IF NOT EXISTS korisnici (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ime TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                uloga TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS projekti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                naziv TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS unosi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                korisnik_id INTEGER REFERENCES korisnici(id),
                projekt_id INTEGER REFERENCES projekti(id),
                opis TEXT,
                pocetak TEXT,
                kraj TEXT
            );
        """)
        # probni korisnici, samo ako je baza prazna
        if veza.execute("SELECT COUNT(*) FROM korisnici").fetchone()[0] == 0:
            veza.executemany("INSERT INTO korisnici (ime, email, uloga) VALUES (?, ?, ?)", [
                ("Ana Horvat", "ana.horvat@tvrtka.hr", "poslodavac"),
                ("Ivan Kovac", "ivan.kovac@tvrtka.hr", "zaposlenik"),
                ("Marija Babic", "marija.babic@tvrtka.hr", "zaposlenik"),
                ("Luka Novak", "luka.novak@tvrtka.hr", "zaposlenik"),
            ])


class Korisnik(BaseModel):
    ime: str
    email: str
    uloga: str  # "zaposlenik" ili "poslodavac"


@app.get("/korisnici")
def svi_korisnici(uloga: str | None = None):
    with spoji() as veza:
        if uloga:
            redovi = veza.execute("SELECT * FROM korisnici WHERE uloga = ?", (uloga,)).fetchall()
        else:
            redovi = veza.execute("SELECT * FROM korisnici").fetchall()
    return [dict(r) for r in redovi]


@app.get("/korisnici/{id}")
def jedan_korisnik(id: int):
    with spoji() as veza:
        red = veza.execute("SELECT * FROM korisnici WHERE id = ?", (id,)).fetchone()
    if red is None:
        raise HTTPException(404, "Korisnik ne postoji")
    return dict(red)


@app.post("/korisnici", status_code=201)
def dodaj_korisnika(k: Korisnik):
    if k.uloga not in ("zaposlenik", "poslodavac"):
        raise HTTPException(400, "Uloga mora biti zaposlenik ili poslodavac")
    try:
        with spoji() as veza:
            kursor = veza.execute("INSERT INTO korisnici (ime, email, uloga) VALUES (?, ?, ?)",
                                  (k.ime, k.email, k.uloga))
    except sqlite3.IntegrityError:
        raise HTTPException(400, "Korisnik s tim emailom vec postoji")
    return {"id": kursor.lastrowid, "ime": k.ime, "email": k.email, "uloga": k.uloga}


@app.delete("/korisnici/{id}")
def obrisi_korisnika(id: int):
    with spoji() as veza:
        obrisano = veza.execute("DELETE FROM korisnici WHERE id = ?", (id,)).rowcount
    if obrisano == 0:
        raise HTTPException(404, "Korisnik ne postoji")
    return {"poruka": "Korisnik obrisan"}


napravi_bazu()

if __name__ == "__main__":
    uvicorn.run(app)
