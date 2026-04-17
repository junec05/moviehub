from functools import wraps
from flask import Flask, jsonify, request, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

from config import SECRET_KEY
from database import get_connection, init_database

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["SECRET_KEY"] = SECRET_KEY


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Debes iniciar sesión"}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Debes iniciar sesión"}), 401

        if session.get("role") != "admin":
            return jsonify({"error": "No tienes permisos de administrador"}), 403

        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def serve_index():
    return send_from_directory("static", "index.html")


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not username or not email or not password:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        return jsonify({"error": "El usuario o el email ya existen"}), 400

    hashed_password = generate_password_hash(password)

    cursor.execute("""
        INSERT INTO users (username, email, password, role)
        VALUES (?, ?, ?, ?)
    """, (username, email, hashed_password, "user"))

    conn.commit()
    conn.close()

    return jsonify({"message": "Usuario registrado correctamente"}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "Debes introducir usuario y contraseña"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user is None or not check_password_hash(user["password"], password):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]

    return jsonify({
        "message": "Inicio de sesión correcto",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"]
        }
    })


@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Sesión cerrada correctamente"})


@app.route("/api/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"authenticated": False})

    return jsonify({
        "authenticated": True,
        "user": {
            "id": session["user_id"],
            "username": session["username"],
            "role": session["role"]
        }
    })


@app.route("/api/movies", methods=["GET"])
def get_movies():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies ORDER BY id DESC")
    movies = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return jsonify(movies)


@app.route("/api/movies/<int:movie_id>", methods=["GET"])
def get_movie(movie_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()

    conn.close()

    if movie is None:
        return jsonify({"error": "Película no encontrada"}), 404

    return jsonify(dict(movie))


@app.route("/api/movies", methods=["POST"])
@admin_required
def create_movie():
    data = request.get_json()

    required_fields = [
        "title", "director", "genre", "duration",
        "synopsis", "age_rating", "cinema", "showtimes"
    ]

    for field in required_fields:
        if str(data.get(field, "")).strip() == "":
            return jsonify({"error": f"El campo '{field}' es obligatorio"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO movies (
            title, director, genre, duration, poster_url,
            synopsis, age_rating, cinema, showtimes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["title"].strip(),
        data["director"].strip(),
        data["genre"].strip(),
        int(data["duration"]),
        data.get("poster_url", "").strip(),
        data["synopsis"].strip(),
        data["age_rating"].strip(),
        data["cinema"].strip(),
        data["showtimes"].strip()
    ))

    conn.commit()
    movie_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Película creada correctamente",
        "movie_id": movie_id
    }), 201


@app.route("/api/movies/<int:movie_id>", methods=["PUT"])
@admin_required
def update_movie(movie_id):
    data = request.get_json()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()

    if movie is None:
        conn.close()
        return jsonify({"error": "Película no encontrada"}), 404

    required_fields = [
        "title", "director", "genre", "duration",
        "synopsis", "age_rating", "cinema", "showtimes"
    ]

    for field in required_fields:
        if str(data.get(field, "")).strip() == "":
            conn.close()
            return jsonify({"error": f"El campo '{field}' es obligatorio"}), 400

    cursor.execute("""
        UPDATE movies
        SET title = ?, director = ?, genre = ?, duration = ?, poster_url = ?,
            synopsis = ?, age_rating = ?, cinema = ?, showtimes = ?
        WHERE id = ?
    """, (
        data["title"].strip(),
        data["director"].strip(),
        data["genre"].strip(),
        int(data["duration"]),
        data.get("poster_url", "").strip(),
        data["synopsis"].strip(),
        data["age_rating"].strip(),
        data["cinema"].strip(),
        data["showtimes"].strip(),
        movie_id
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Película actualizada correctamente"})


@app.route("/api/movies/<int:movie_id>", methods=["DELETE"])
@admin_required
def delete_movie(movie_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()

    if movie is None:
        conn.close()
        return jsonify({"error": "Película no encontrada"}), 404

    cursor.execute("DELETE FROM favorites WHERE movie_id = ?", (movie_id,))
    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))

    conn.commit()
    conn.close()

    return jsonify({"message": "Película eliminada correctamente"})


@app.route("/api/favorites", methods=["GET"])
@login_required
def get_favorites():
    user_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT movies.*
        FROM favorites
        INNER JOIN movies ON favorites.movie_id = movies.id
        WHERE favorites.user_id = ?
        ORDER BY favorites.id DESC
    """, (user_id,))

    favorites = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(favorites)


@app.route("/api/favorites/<int:movie_id>", methods=["POST"])
@login_required
def add_favorite(movie_id):
    user_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM movies WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()

    if movie is None:
        conn.close()
        return jsonify({"error": "Película no encontrada"}), 404

    cursor.execute("""
        SELECT id FROM favorites
        WHERE user_id = ? AND movie_id = ?
    """, (user_id, movie_id))
    favorite = cursor.fetchone()

    if favorite:
        conn.close()
        return jsonify({"error": "La película ya está en favoritos"}), 400

    cursor.execute("""
        INSERT INTO favorites (user_id, movie_id)
        VALUES (?, ?)
    """, (user_id, movie_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Película añadida a favoritos"}), 201


@app.route("/api/favorites/<int:movie_id>", methods=["DELETE"])
@login_required
def remove_favorite(movie_id):
    user_id = session["user_id"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM favorites
        WHERE user_id = ? AND movie_id = ?
    """, (user_id, movie_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Película eliminada de favoritos"})


if __name__ == "__main__":
    init_database()
    app.run(debug=True)