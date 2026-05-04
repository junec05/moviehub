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

    cursor.execute("SELECT COUNT(*) AS total FROM movies")
    total_movies = cursor.fetchone()["total"]

    if total_movies == 0:
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
            )
        ]

        cursor.executemany("""
            INSERT INTO movies (
                title, director, genre, duration, poster_url,
                synopsis, age_rating, cinema, showtimes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_movies)

    conn.commit()
    conn.close()