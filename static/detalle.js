async function apiFetch(url) {
    const response = await fetch(url);
    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Ha ocurrido un error");
    }

    return data;
}

async function loadMovieDetail() {
    const params = new URLSearchParams(window.location.search);
    const movieId = params.get("id");

    const detailContainer = document.getElementById("movieDetailContainer");

    if (!movieId) {
        detailContainer.innerHTML = "<p>No se ha indicado ninguna película.</p>";
        return;
    }

    try {
        const movies = await apiFetch("/api/movies");
        const movie = movies.find(m => m.id == movieId);

        if (!movie) {
            detailContainer.innerHTML = "<p>Película no encontrada.</p>";
            return;
        }

        detailContainer.innerHTML = `
            <div class="movie-detail">
                <img src="${movie.poster_url}" alt="${movie.title}" class="detail-img">

                <div class="detail-info">
                    <h2>${movie.title}</h2>

                    <p><strong>Director:</strong> ${movie.director}</p>
                    <p><strong>Género:</strong> ${movie.genre}</p>
                    <p><strong>Duración:</strong> ${movie.duration} min</p>
                    <p><strong>Edad recomendada:</strong> ${movie.age_rating}</p>
                    <p><strong>Cine:</strong> ${movie.cinema}</p>
                    <p><strong>Horarios:</strong> ${movie.showtimes}</p>
                    <p><strong>Sinopsis:</strong> ${movie.synopsis}</p>
                </div>
            </div>
        `;
    } catch (error) {
        detailContainer.innerHTML = `<p>${error.message}</p>`;
    }
}

loadMovieDetail();