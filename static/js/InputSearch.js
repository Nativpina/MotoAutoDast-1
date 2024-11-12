document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('search-button');
    const resultsContainer = document.createElement('div');
    resultsContainer.id = 'results-container';
    document.body.appendChild(resultsContainer);

    const fetchResults = (query) => {
        if (query.trim() === '') {
            resultsContainer.innerHTML = '';
            return;
        }

        fetch(`/buscar/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                resultsContainer.innerHTML = '';
                if (data.length > 0) {
                    data.forEach(product => {
                        const productCard = `
                            <div class="product-card">
                                <img src="${product.imagen || '/static/images/default.png'}" alt="${product.nombre_producto}">
                                <h4>${product.nombre_producto}</h4>
                                <p>${product.descripcion}</p>
                                <span>Precio: $${product.costo}</span>
                            </div>
                        `;
                        resultsContainer.innerHTML += productCard;
                    });
                } else {
                    resultsContainer.innerHTML = '<p>No se encontraron productos.</p>';
                }
            })
            .catch(error => console.error('Error fetching products:', error));
    };

    searchInput.addEventListener('input', (e) => {
        fetchResults(e.target.value);
    });

    searchButton.addEventListener('click', () => {
        fetchResults(searchInput.value);
    });
});
