# Library App

Εφαρμογή δανεισμού βιβλίων μιας μικρής βιβλιοθήκης, γραμμένη σε Python με Flask.
Φτιάχτηκε για εκπαιδευτικούς σκοπούς, με αρχιτεκτονική MVC, μοτίβο DAO, αρχές SOLID και tests.

## Τι κάνει

- **Επισκέπτης**, εγγραφή και σύνδεση
- **Χρήστης**, διαθέσιμα βιβλία, δανεισμός, επιστροφή, ιστορικό
- **Διαχειριστής**, διαχείριση βιβλίων και χρηστών

Κανόνες της βιβλιοθήκης, έως 3 βιβλία ανά χρήστη, προθεσμία 14 ημέρες, δεν διαγράφεται βιβλίο ή χρήστης με δανεισμούς.

## Εγκατάσταση

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Σε Mac ή Linux η ενεργοποίηση γίνεται με `source venv/bin/activate`.

## Πρώτη εκτέλεση

```
python create_admin.py
python seed_books.py
python app.py
```

Η εφαρμογή ανοίγει στο http://127.0.0.1:5000

## Tests

```
pytest -v
```

## Δομή

| Φάκελος | Στρώμα | Ευθύνη |
|---|---|---|
| `models/` | Model | Οι κλάσεις Book, User, Loan |
| `dao/` | DAO | Όλο το SQL |
| `services/` | Service | Οι κανόνες της βιβλιοθήκης |
| `controllers/` | Controller | Τα routes του Flask |
| `templates/` | View | Οι σελίδες HTML |
| `tests/` | | Τα tests με pytest |

Περισσότερα στο [DESIGN.md](DESIGN.md).