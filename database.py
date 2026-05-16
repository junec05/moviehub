import os
import sqlite3
from werkzeug.security import generate_password_hash
from config import DATABASE_DIR, DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    os.makedirs(DATABASE_DIR, exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            director TEXT NOT NULL,
            genre TEXT NOT NULL,
            duration INTEGER NOT NULL,
            poster_url TEXT,
            synopsis TEXT NOT NULL,
            age_rating TEXT NOT NULL,
            cinema TEXT NOT NULL,
            showtimes TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS screenings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            cinema TEXT NOT NULL,
            screening_date TEXT NOT NULL,
            screening_time TEXT NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            UNIQUE(user_id, movie_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    admin_user = cursor.fetchone()

    if admin_user is None:
        cursor.execute("""
            INSERT INTO users (username, email, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            "admin",
            "admin@moviehub.com",
            generate_password_hash("admin123"),
            "admin"
        ))

    sample_movies = [
        (
            "Dune: Parte Dos",
            "Denis Villeneuve",
            "Ciencia ficción",
            166,
            "https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg",
            "Paul Atreides se une a los Fremen mientras busca venganza y trata de evitar un futuro terrible.",
            "12",
            "Cines Bilbao Centro",
            "15/05/2026 - 17:00, 20:00, 22:30"
        ),
        (
            "Inside Out 2",
            "Kelsey Mann",
            "Animación",
            96,
            "https://image.tmdb.org/t/p/w500/vpnVM9B6NMmQpWeZvzLvDESb2QY.jpg",
            "Riley entra en la adolescencia y aparecen nuevas emociones que alteran por completo su mundo interior.",
            "TP",
            "Yelmo Megapark",
            "15/04/2026 - 16:30, 18:30, 20:30"
        ),
        (
            "Oppenheimer",
            "Christopher Nolan",
            "Drama",
            180,
            "https://image.tmdb.org/t/p/w500/ptpr0kGAckfQkJeJIt8st5dglvd.jpg",
            "La historia del científico J. Robert Oppenheimer y el desarrollo de la bomba atómica.",
            "16",
            "Multicines Bilbao",
            "15/04/2026 - 19:00, 22:15"
        ),
        (
            "Interstellar",
            "Christopher Nolan",
            "Ciencia ficción",
            169,
            "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
            "Un grupo de astronautas viaja a través de un agujero de gusano para buscar un nuevo hogar para la humanidad.",
            "12",
            "Cines Bilbao Centro",
            "16/04/2026 - 18:00, 21:30"
        ),
        (
            "Barbie",
            "Greta Gerwig",
            "Comedia",
            114,
            "https://image.tmdb.org/t/p/w500/iuFNMS8U5cb6xfzi51Dbkovj7vM.jpg",
            "Barbie abandona Barbieland para viajar al mundo real y descubrir quién quiere ser realmente.",
            "7",
            "Yelmo Megapark",
            "16/04/2026 - 17:15, 20:00"
        ),
        (
            "Spider-Man: Cruzando el multiverso",
            "Joaquim Dos Santos, Kemp Powers, Justin K. Thompson",
            "Animación",
            140,
            "https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg",
            "Miles Morales se adentra en el multiverso y conoce a otros Spider-Man con formas distintas de entender su misión.",
            "7",
            "Cines Bilbao Centro",
            "17/04/2026 - 16:30, 19:30, 22:00"
        ),
        (
            "El señor de los anillos: La comunidad del anillo",
            "Peter Jackson",
            "Fantasía",
            178,
            "https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",
            "Frodo Bolsón inicia un viaje para destruir el Anillo Único y evitar que caiga en manos de Sauron.",
            "12",
            "Multicines Bilbao",
            "17/04/2026 - 17:00, 21:00"
        ),
        (
            "The Batman",
            "Matt Reeves",
            "Acción",
            176,
            "https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg",
            "Batman investiga una serie de crímenes en Gotham mientras descubre la corrupción que rodea a la ciudad.",
            "12",
            "Yelmo Megapark",
            "18/04/2026 - 18:00, 21:30"
        ),
        (
            "Coco",
            "Lee Unkrich",
            "Animación",
            105,
            "https://image.tmdb.org/t/p/w500/gGEsBPAijhVUFoiNpgZXqRVWJt2.jpg",
            "Miguel viaja al mundo de los muertos para descubrir la verdad sobre su familia y su pasión por la música.",
            "TP",
            "Cines Bilbao Centro",
            "18/04/2026 - 16:00, 18:15"
        ),
        (
            "Avatar: El sentido del agua",
            "James Cameron",
            "Ciencia ficción",
            192,
            "https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg",
            "Jake Sully vive con su familia en Pandora, pero una antigua amenaza les obliga a buscar refugio junto a otro clan.",
            "12",
            "Multicines Bilbao",
            "19/04/2026 - 17:30, 21:00"
        )
    ]

    for movie in sample_movies:
        title = movie[0]

        cursor.execute("SELECT id FROM movies WHERE title = ?", (title,))
        existing_movie = cursor.fetchone()

        if existing_movie is None:
            cursor.execute("""
                INSERT INTO movies (
                    title, director, genre, duration, poster_url,
                    synopsis, age_rating, cinema, showtimes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, movie)
    sample_screenings = [
        ("Dune: Parte Dos", "Cines Bilbao Centro", "2026-05-15", "17:00"),
        ("Dune: Parte Dos", "Cines Bilbao Centro", "2026-05-15", "20:00"),
        ("Dune: Parte Dos", "Multicines Bilbao", "2026-05-16", "22:30"),

        ("Inside Out 2", "Yelmo Megapark", "2026-04-15", "14:00"),
        ("Inside Out 2", "Yelmo Megapark", "2026-04-15", "16:30"),
        ("Inside Out 2", "Yelmo Megapark", "2026-04-15", "18:30"),
        ("Inside Out 2", "Cines Bilbao Centro", "2026-04-15", "20:30"),
        ("Inside Out 2", "Multicines Bilbao", "2026-04-16", "17:00"),

        ("Oppenheimer", "Multicines Bilbao", "2026-04-15", "19:00"),
        ("Oppenheimer", "Multicines Bilbao", "2026-04-15", "22:15"),
        ("Oppenheimer", "Cines Bilbao Centro", "2026-04-16", "20:00"),

        ("Interstellar", "Cines Bilbao Centro", "2026-04-16", "18:00"),
        ("Interstellar", "Cines Bilbao Centro", "2026-04-16", "21:30"),
        ("Interstellar", "Yelmo Megapark", "2026-04-17", "19:00"),

        ("Barbie", "Yelmo Megapark", "2026-04-16", "17:15"),
        ("Barbie", "Yelmo Megapark", "2026-04-16", "20:00"),
        ("Barbie", "Multicines Bilbao", "2026-04-17", "18:00"),

        ("Spider-Man: Cruzando el multiverso", "Cines Bilbao Centro", "2026-04-17", "16:30"),
        ("Spider-Man: Cruzando el multiverso", "Cines Bilbao Centro", "2026-04-17", "19:30"),
        ("Spider-Man: Cruzando el multiverso", "Cines Bilbao Centro", "2026-04-17", "22:00"),

        ("El señor de los anillos: La comunidad del anillo", "Multicines Bilbao", "2026-04-17", "17:00"),
        ("El señor de los anillos: La comunidad del anillo", "Multicines Bilbao", "2026-04-17", "21:00"),

        ("The Batman", "Yelmo Megapark", "2026-04-18", "18:00"),
        ("The Batman", "Yelmo Megapark", "2026-04-18", "21:30"),

        ("Coco", "Cines Bilbao Centro", "2026-04-18", "16:00"),
        ("Coco", "Cines Bilbao Centro", "2026-04-18", "18:15"),

        ("Avatar: El sentido del agua", "Multicines Bilbao", "2026-04-19", "17:30"),
        ("Avatar: El sentido del agua", "Multicines Bilbao", "2026-04-19", "21:00")
    ]

    for title, cinema, screening_date, screening_time in sample_screenings:
        cursor.execute("SELECT id FROM movies WHERE title = ?", (title,))
        movie = cursor.fetchone()

        if movie is not None:
            movie_id = movie["id"]

            cursor.execute("""
                SELECT id FROM screenings
                WHERE movie_id = ?
                AND cinema = ?
                AND screening_date = ?
                AND screening_time = ?
            """, (movie_id, cinema, screening_date, screening_time))

            existing_screening = cursor.fetchone()

            if existing_screening is None:
                cursor.execute("""
                    INSERT INTO screenings (
                        movie_id,
                        cinema,
                        screening_date,
                        screening_time
                    )
                    VALUES (?, ?, ?, ?)
                """, (
                    movie_id,
                    cinema,
                    screening_date,
                    screening_time
                ))
    conn.commit()
    conn.close()
