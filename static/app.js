let currentUser = null;
let allMovies = [];
let favoriteIds = [];

const moviesContainer = document.getElementById("moviesContainer");
const favoritesContainer = document.getElementById("favoritesContainer");
const adminPanel = document.getElementById("adminPanel");
const userInfo = document.getElementById("userInfo");
const headerButtons = document.getElementById("headerButtons");
const filterType = document.getElementById("filterType");
const cinemaFilterBox = document.getElementById("cinemaFilterBox");
const cinemaFilter = document.getElementById("cinemaFilter");
const dateFilterBox = document.getElementById("dateFilterBox");
const dateFilter = document.getElementById("dateFilter");
const clearFiltersBtn = document.getElementById("clearFiltersBtn");

const movieForm = document.getElementById("movieForm");
const cancelEditBtn = document.getElementById("cancelEditBtn");

const loginModal = document.getElementById("loginModal");
const registerModal = document.getElementById("registerModal");

const navButtons = document.querySelectorAll(".nav-btn");
const contentSections = document.querySelectorAll(".content-section");

navButtons.forEach(button => {
    button.addEventListener("click", () => {
        showSection(button.dataset.section);
    });
});

function showSection(sectionId) {
    navButtons.forEach(btn => btn.classList.remove("active"));
    contentSections.forEach(section => section.classList.add("hidden"));

    document.querySelector(`[data-section="${sectionId}"]`).classList.add("active");
    document.getElementById(sectionId).classList.remove("hidden");
}

document.getElementById("openLoginBtn").addEventListener("click", () => {
    loginModal.classList.remove("hidden");
});

document.getElementById("openRegisterBtn").addEventListener("click", () => {
    registerModal.classList.remove("hidden");
});

document.getElementById("closeLoginBtn").addEventListener("click", () => {
    loginModal.classList.add("hidden");
});

document.getElementById("closeRegisterBtn").addEventListener("click", () => {
    registerModal.classList.add("hidden");
});

cancelEditBtn.addEventListener("click", resetMovieForm);

document.getElementById("loginForm").addEventListener("submit", loginUser);
document.getElementById("registerForm").addEventListener("submit", registerUser);
movieForm.addEventListener("submit", saveMovie);

filterType.addEventListener("change", () => {
    updateFilterVisibility();
    applyMovieFilters();
});

cinemaFilter.addEventListener("change", applyMovieFilters);
dateFilter.addEventListener("change", applyMovieFilters);
clearFiltersBtn.addEventListener("click", clearMovieFilters);

async function apiFetch(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json"
        },
        ...options
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Ha ocurrido un error");
    }

    return data;
}

async function loadSession() {
    try {
        const data = await apiFetch("/api/me");

        if (data.authenticated) {
            currentUser = data.user;
        } else {
            currentUser = null;
        }

        updateUIByUser();
    } catch (error) {
        alert(error.message);
    }
}

function updateUIByUser() {
    if (!currentUser) {
        userInfo.textContent = "No has iniciado sesión.";
        adminPanel.classList.add("hidden");

        headerButtons.innerHTML = `
            <button id="openLoginBtn">Iniciar sesión</button>
            <button id="openRegisterBtn" class="secondary">Registrarse</button>
        `;

        document.getElementById("openLoginBtn").addEventListener("click", () => {
            loginModal.classList.remove("hidden");
        });

        document.getElementById("openRegisterBtn").addEventListener("click", () => {
            registerModal.classList.remove("hidden");
        });
    } else {
        userInfo.textContent = `Sesión iniciada como ${currentUser.username} (${currentUser.role})`;

        headerButtons.innerHTML = `
            <button id="logoutBtn" class="secondary">Cerrar sesión</button>
        `;

        document.getElementById("logoutBtn").addEventListener("click", logoutUser);

        if (currentUser.role === "admin") {
            adminPanel.classList.remove("hidden");
        } else {
            adminPanel.classList.add("hidden");
            loadFavorites();
        }
    }

    renderMovies();
}

async function registerUser(event) {
    event.preventDefault();

    const payload = {
        username: document.getElementById("registerUsername").value,
        email: document.getElementById("registerEmail").value,
        password: document.getElementById("registerPassword").value
    };

    try {
        const data = await apiFetch("/api/register", {
            method: "POST",
            body: JSON.stringify(payload)
        });

        alert(data.message);
        document.getElementById("registerForm").reset();
        registerModal.classList.add("hidden");
    } catch (error) {
        alert(error.message);
    }
}

async function loginUser(event) {
    event.preventDefault();

    const payload = {
        username: document.getElementById("loginUsername").value,
        password: document.getElementById("loginPassword").value
    };

    try {
        const data = await apiFetch("/api/login", {
            method: "POST",
            body: JSON.stringify(payload)
        });

        currentUser = data.user;
        document.getElementById("loginForm").reset();
        loginModal.classList.add("hidden");
        updateUIByUser();
        showSection("cuentaSection");
    } catch (error) {
        alert(error.message);
    }
}

async function logoutUser() {
    try {
        const data = await apiFetch("/api/logout", {
            method: "POST"
        });

        alert(data.message);
        currentUser = null;
        favoriteIds = [];
        favoritesContainer.innerHTML = "";
        updateUIByUser();
        showSection("inicioSection");
    } catch (error) {
        alert(error.message);
    }
}

async function loadMovies() {
    try {
        allMovies = await apiFetch("/api/movies");
        fillCinemaFilter();
        renderMovies();
    } catch (error) {
        alert(error.message);
    }
}

function renderMovies(moviesToRender = null) {
    moviesContainer.innerHTML = "";

    const movies = moviesToRender || allMovies;

    if (movies.length === 0) {
        moviesContainer.innerHTML = "<p>No hay películas disponibles con esos filtros.</p>";
        return;
    }

    movies.forEach(movie => {
        const card = document.createElement("div");
        card.className = "movie-card";

        const isFavorite = favoriteIds.includes(movie.id);

        card.innerHTML = `
            <img src="${movie.poster_url}" alt="${movie.title}">

            <h3>${movie.title}</h3>

            <p><strong>Director:</strong> ${movie.director}</p>
            <p><strong>Género:</strong> ${movie.genre}</p>
            <p><strong>Duración:</strong> ${movie.duration} min</p>
            <p><strong>Edad recomendada:</strong> ${movie.age_rating}</p>
            <p><strong>Cine:</strong> ${movie.cinema}</p>
            <p><strong>Horarios:</strong> ${movie.showtimes}</p>
            <p><strong>Sinopsis:</strong> ${movie.synopsis}</p>

            ${renderButtons(movie, isFavorite)}
        `;

        moviesContainer.appendChild(card);
    });

    assignDynamicButtons();
}

function fillCinemaFilter() {
    cinemaFilter.innerHTML = `<option value="">Selecciona un cine</option>`;

    const cinemas = [...new Set(allMovies.map(movie => movie.cinema))]
        .filter(cinema => cinema && cinema.trim() !== "")
        .sort();

    cinemas.forEach(cinema => {
        const option = document.createElement("option");
        option.value = cinema;
        option.textContent = cinema;
        cinemaFilter.appendChild(option);
    });
}

function updateFilterVisibility() {
    const selectedFilter = filterType.value;

    cinemaFilterBox.classList.add("hidden");
    dateFilterBox.classList.add("hidden");

    if (selectedFilter === "cinema") {
        cinemaFilterBox.classList.remove("hidden");
        dateFilter.value = "";
    }

    if (selectedFilter === "date") {
        dateFilterBox.classList.remove("hidden");
        cinemaFilter.value = "";
    }

    if (selectedFilter === "both") {
        cinemaFilterBox.classList.remove("hidden");
        dateFilterBox.classList.remove("hidden");
    }

    if (selectedFilter === "none") {
        cinemaFilter.value = "";
        dateFilter.value = "";
        renderMovies();
    }
}

function applyMovieFilters() {
    const selectedFilter = filterType.value;
    const selectedCinema = cinemaFilter.value;
    const selectedDate = dateFilter.value;

    let filteredMovies = allMovies;

    if ((selectedFilter === "cinema" || selectedFilter === "both") && selectedCinema !== "") {
        filteredMovies = filteredMovies.filter(movie => movie.cinema === selectedCinema);
    }

    if ((selectedFilter === "date" || selectedFilter === "both") && selectedDate !== "") {
        filteredMovies = filteredMovies.filter(movie => movieHasDate(movie, selectedDate));
    }

    renderMovies(filteredMovies);
}

function movieHasDate(movie, selectedDate) {
    if (!movie.showtimes) {
        return false;
    }

    const formattedDate = formatDateToSpanish(selectedDate);

    return movie.showtimes.includes(formattedDate);
}

function formatDateToSpanish(dateValue) {
    const parts = dateValue.split("-");

    if (parts.length !== 3) {
        return dateValue;
    }

    const year = parts[0];
    const month = parts[1];
    const day = parts[2];

    return `${day}/${month}/${year}`;
}

function clearMovieFilters() {
    filterType.value = "none";
    cinemaFilter.value = "";
    dateFilter.value = "";

    cinemaFilterBox.classList.add("hidden");
    dateFilterBox.classList.add("hidden");

    renderMovies();
}

function renderButtons(movie, isFavorite) {
    if (!currentUser) {
        return `<button disabled>Inicia sesión para interactuar</button>`;
    }

    if (currentUser.role === "admin") {
        return `
            <button class="edit-btn" data-id="${movie.id}">Editar</button>
            <button class="delete-btn danger" data-id="${movie.id}">Eliminar</button>
        `;
    }

    return isFavorite
        ? `<button class="remove-favorite-btn secondary" data-id="${movie.id}">Quitar de favoritos</button>`
        : `<button class="favorite-btn" data-id="${movie.id}">Añadir a favoritos</button>`;
}

function assignDynamicButtons() {
    document.querySelectorAll(".edit-btn").forEach(button => {
        button.addEventListener("click", () => editMovie(button.dataset.id));
    });

    document.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", () => deleteMovie(button.dataset.id));
    });

    document.querySelectorAll(".favorite-btn").forEach(button => {
        button.addEventListener("click", () => addFavorite(button.dataset.id));
    });

    document.querySelectorAll(".remove-favorite-btn").forEach(button => {
        button.addEventListener("click", () => removeFavorite(button.dataset.id));
    });
}

async function saveMovie(event) {
    event.preventDefault();

    const movieId = document.getElementById("movieId").value;

    const payload = {
        title: document.getElementById("title").value,
        director: document.getElementById("director").value,
        genre: document.getElementById("genre").value,
        duration: document.getElementById("duration").value,
        poster_url: document.getElementById("poster_url").value,
        synopsis: document.getElementById("synopsis").value,
        age_rating: document.getElementById("age_rating").value,
        cinema: document.getElementById("cinema").value,
        showtimes: document.getElementById("showtimes").value
    };

    try {
        if (movieId) {
            await apiFetch(`/api/movies/${movieId}`, {
                method: "PUT",
                body: JSON.stringify(payload)
            });
            alert("Película actualizada correctamente");
        } else {
            await apiFetch("/api/movies", {
                method: "POST",
                body: JSON.stringify(payload)
            });
            alert("Película creada correctamente");
        }

        resetMovieForm();
        await loadMovies();
    } catch (error) {
        alert(error.message);
    }
}

function editMovie(movieId) {
    const movie = allMovies.find(m => m.id == movieId);

    if (!movie) {
        return;
    }

    document.getElementById("movieId").value = movie.id;
    document.getElementById("title").value = movie.title;
    document.getElementById("director").value = movie.director;
    document.getElementById("genre").value = movie.genre;
    document.getElementById("duration").value = movie.duration;
    document.getElementById("poster_url").value = movie.poster_url;
    document.getElementById("synopsis").value = movie.synopsis;
    document.getElementById("age_rating").value = movie.age_rating;
    document.getElementById("cinema").value = movie.cinema;
    document.getElementById("showtimes").value = movie.showtimes;

    cancelEditBtn.classList.remove("hidden");
    showSection("adminSection");
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetMovieForm() {
    movieForm.reset();
    document.getElementById("movieId").value = "";
    cancelEditBtn.classList.add("hidden");
}

async function deleteMovie(movieId) {
    const confirmed = confirm("¿Seguro que quieres eliminar esta película?");
    if (!confirmed) {
        return;
    }

    try {
        await apiFetch(`/api/movies/${movieId}`, {
            method: "DELETE"
        });

        alert("Película eliminada correctamente");
        await loadMovies();
    } catch (error) {
        alert(error.message);
    }
}

async function loadFavorites() {
    if (!currentUser || currentUser.role !== "user") {
        return;
    }

    try {
        const favorites = await apiFetch("/api/favorites");
        favoriteIds = favorites.map(movie => movie.id);
        renderFavorites(favorites);
        renderMovies();
    } catch (error) {
        alert(error.message);
    }
}

function renderFavorites(favorites) {
    favoritesContainer.innerHTML = "";

    if (favorites.length === 0) {
        favoritesContainer.innerHTML = "<p>No tienes películas en favoritos.</p>";
        return;
    }

    favorites.forEach(movie => {
        const card = document.createElement("div");
        card.className = "favorite-card";

        card.innerHTML = `
            <img src="${movie.poster_url}" alt="${movie.title}" class="favorite-img">

            <div class="favorite-info">
                <h3>
                    <a href="#" class="movie-link" data-id="${movie.id}">
                        ${movie.title}
                    </a>
                </h3>

                <button class="danger remove-favorite-btn" data-id="${movie.id}">
                    Quitar de favoritos
                </button>
            </div>
        `;

        favoritesContainer.appendChild(card);
    });

    assignDynamicButtons();

    document.querySelectorAll(".movie-link").forEach(link => {
        link.addEventListener("click", event => {
            event.preventDefault();
            showMovieDetail(link.dataset.id);
        });
    });
}
function showMovieDetail(movieId) {
    const movie = allMovies.find(m => m.id == movieId);

    if (!movie) {
        alert("Película no encontrada");
        return;
    }

    const detailContainer = document.getElementById("movieDetailContainer");

    detailContainer.innerHTML = `
        <div class="movie-detail-box">
            <button class="danger close-detail-btn" onclick="closeMovieDetail()">
                Cerrar
            </button>

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
        </div>
    `;

    detailContainer.classList.remove("hidden");
}
function closeMovieDetail() {
    const detailContainer = document.getElementById("movieDetailContainer");
    detailContainer.innerHTML = "";
    detailContainer.classList.add("hidden");
}

async function addFavorite(movieId) {
    try {
        await apiFetch(`/api/favorites/${movieId}`, {
            method: "POST"
        });

        await loadFavorites();
    } catch (error) {
        alert(error.message);
    }
}

async function removeFavorite(movieId) {
    try {
        await apiFetch(`/api/favorites/${movieId}`, {
            method: "DELETE"
        });

        await loadFavorites();
    } catch (error) {
        alert(error.message);
    }
}

async function initApp() {
    showSection("inicioSection");
    await loadSession();
    await loadMovies();
}

initApp();