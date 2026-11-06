"""Γεμίζει τη βάση με δοκιμαστικά δεδομένα.

Δημιουργεί τον διαχειριστή, 10 χρήστες και 50 βιβλία.
Μπορεί να τρέξει πολλές φορές, ό,τι υπάρχει ήδη παραλείπεται.
"""

from app import create_app
from models.user import User
from services.errors import ServiceError

ADMIN = ("Διαχειριστής", "admin@library.gr", "admin123")

USERS_PASSWORD = "123456"

USERS = [
    ("Μαρία Παπαδοπούλου", "maria@example.com"),
    ("Γιώργος Νικολάου", "giorgos@example.com"),
    ("Ελένη Γεωργίου", "eleni@example.com"),
    ("Νίκος Δημητρίου", "nikos@example.com"),
    ("Κατερίνα Ιωάννου", "katerina@example.com"),
    ("Δημήτρης Κωνσταντίνου", "dimitris@example.com"),
    ("Σοφία Αθανασίου", "sofia@example.com"),
    ("Κώστας Βασιλείου", "kostas@example.com"),
    ("Άννα Χριστοδούλου", "anna@example.com"),
    ("Παναγιώτης Αντωνίου", "panagiotis@example.com"),
]

BOOKS = [
    ("Ο Μικρός Πρίγκιπας", "Antoine de Saint-Exupéry", "1943", "978-1"),
    ("1984", "George Orwell", "1949", "978-2"),
    ("Η Αλίκη στη Χώρα των Θαυμάτων", "Lewis Carroll", "1865", "978-3"),
    ("Ο Άρχοντας των Δαχτυλιδιών", "J.R.R. Tolkien", "1954", "978-4"),
    ("Ζορμπάς", "Νίκος Καζαντζάκης", "1946", "978-5"),
    ("Ο Καπετάν Μιχάλης", "Νίκος Καζαντζάκης", "1953", "978-6"),
    ("Ο Χριστός Ξανασταυρώνεται", "Νίκος Καζαντζάκης", "1948", "978-7"),
    ("Η Φόνισσα", "Αλέξανδρος Παπαδιαμάντης", "1903", "978-8"),
    ("Οι Έμποροι των Εθνών", "Αλέξανδρος Παπαδιαμάντης", "1882", "978-9"),
    ("Η Πάπισσα Ιωάννα", "Εμμανουήλ Ροΐδης", "1866", "978-10"),
    ("Το Τρίτο Στεφάνι", "Κώστας Ταχτσής", "1962", "978-11"),
    ("Λεωνής", "Γιώργος Θεοτοκάς", "1940", "978-12"),
    ("Αργώ", "Γιώργος Θεοτοκάς", "1933", "978-13"),
    ("Ματωμένα Χώματα", "Διδώ Σωτηρίου", "1962", "978-14"),
    ("Η Ζωή εν Τάφω", "Στρατής Μυριβήλης", "1924", "978-15"),
    ("Η Δασκάλα με τα Χρυσά Μάτια", "Στρατής Μυριβήλης", "1933", "978-16"),
    ("Το Νησί", "Victoria Hislop", "2005", "978-17"),
    ("Ο Θείος Πέτρος και η Εικασία του Γκόλντμπαχ", "Απόστολος Δοξιάδης", "1992", "978-18"),
    ("Τα Ψηλά Βουνά", "Ζαχαρίας Παπαντωνίου", "1918", "978-19"),
    ("Ο Γύρος του Κόσμου σε 80 Ημέρες", "Jules Verne", "1872", "978-20"),
    ("20.000 Λεύγες κάτω από τη Θάλασσα", "Jules Verne", "1870", "978-21"),
    ("Το Νησί των Θησαυρών", "Robert Louis Stevenson", "1883", "978-22"),
    ("Οι Άθλιοι", "Victor Hugo", "1862", "978-23"),
    ("Η Παναγία των Παρισίων", "Victor Hugo", "1831", "978-24"),
    ("Ο Κόμης Μοντεχρήστος", "Alexandre Dumas", "1844", "978-25"),
    ("Οι Τρεις Σωματοφύλακες", "Alexandre Dumas", "1844", "978-26"),
    ("Έγκλημα και Τιμωρία", "Φιόντορ Ντοστογιέφσκι", "1866", "978-27"),
    ("Οι Αδελφοί Καραμαζόφ", "Φιόντορ Ντοστογιέφσκι", "1880", "978-28"),
    ("Πόλεμος και Ειρήνη", "Λέων Τολστόι", "1869", "978-29"),
    ("Άννα Καρένινα", "Λέων Τολστόι", "1878", "978-30"),
    ("Περηφάνια και Προκατάληψη", "Jane Austen", "1813", "978-31"),
    ("Ανεμοδαρμένα Ύψη", "Emily Brontë", "1847", "978-32"),
    ("Τζέιν Έιρ", "Charlotte Brontë", "1847", "978-33"),
    ("Όλιβερ Τουίστ", "Charles Dickens", "1838", "978-34"),
    ("Μεγάλες Προσδοκίες", "Charles Dickens", "1861", "978-35"),
    ("Φρανκενστάιν", "Mary Shelley", "1818", "978-36"),
    ("Δράκουλας", "Bram Stoker", "1897", "978-37"),
    ("Μόμπι Ντικ", "Herman Melville", "1851", "978-38"),
    ("Ο Γέρος και η Θάλασσα", "Ernest Hemingway", "1952", "978-39"),
    ("Ο Μεγάλος Γκάτσμπι", "F. Scott Fitzgerald", "1925", "978-40"),
    ("Σκότωσε τον Κοτσύφι", "Harper Lee", "1960", "978-41"),
    ("Η Φάρμα των Ζώων", "George Orwell", "1945", "978-42"),
    ("Θαυμαστός Καινούργιος Κόσμος", "Aldous Huxley", "1932", "978-43"),
    ("Φαρενάιτ 451", "Ray Bradbury", "1953", "978-44"),
    ("Ο Φύλακας στη Σίκαλη", "J.D. Salinger", "1951", "978-45"),
    ("Εκατό Χρόνια Μοναξιά", "Gabriel García Márquez", "1967", "978-46"),
    ("Ο Αλχημιστής", "Paulo Coelho", "1988", "978-47"),
    ("Το Χόμπιτ", "J.R.R. Tolkien", "1937", "978-48"),
    ("Η Μεταμόρφωση", "Franz Kafka", "1915", "978-49"),
    ("Ο Ξένος", "Albert Camus", "1942", "978-50"),
]


def create_admin(app):
    name, email, password = ADMIN
    try:
        app.user_service.create(name, email, password, User.ROLE_ADMIN)
        print("Διαχειριστής δημιουργήθηκε,", email)
        return 1
    except ServiceError as error:
        print("Διαχειριστής παραλείφθηκε,", error)
        return 0


def create_users(app):
    created = 0
    for name, email in USERS:
        try:
            app.user_service.register(name, email, USERS_PASSWORD)
            created += 1
        except ServiceError as error:
            print("Χρήστης παραλείφθηκε,", email, "-", error)
    return created


def create_books(app):
    created = 0
    for title, author, year, isbn in BOOKS:
        try:
            app.book_service.create(title, author, year, isbn)
            created += 1
        except ServiceError as error:
            print("Βιβλίο παραλείφθηκε,", title, "-", error)
    return created


def main():
    app = create_app()

    admins = create_admin(app)
    users = create_users(app)
    books = create_books(app)

    print()
    print("Νέοι διαχειριστές", admins)
    print("Νέοι χρήστες     ", users)
    print("Νέα βιβλία       ", books)
    print()
    print("Σύνολο στη βάση,", len(app.user_service.list_all()), "χρήστες και",
          len(app.book_service.list_all()), "βιβλία")
    print()
    print("Σύνδεση admin    ", ADMIN[1], "/", ADMIN[2])
    print("Σύνδεση χρηστών  ", "π.χ. maria@example.com /", USERS_PASSWORD)


if __name__ == "__main__":
    main()