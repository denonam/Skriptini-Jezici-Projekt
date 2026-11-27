# Evidencija rada – faza 1

Server s bazom podataka (SQLite) i korisnicima (zaposlenici i poslodavac).

## Pokretanje

```
pip install -r requirements.txt
python server.py
```

Zatim u pregledniku otvoriti http://127.0.0.1:8000/docs i isprobati zahtjeve.

## API

| Metoda | Putanja | Opis |
|---|---|---|
| GET | /korisnici | svi korisnici (može `?uloga=zaposlenik`) |
| GET | /korisnici/{id} | jedan korisnik |
| POST | /korisnici | dodaj korisnika (ime, email, uloga) |
| DELETE | /korisnici/{id} | obriši korisnika |
