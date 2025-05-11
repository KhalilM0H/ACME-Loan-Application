async function fetchBooks() {
    const response = await fetch('/api/books');
    const data = await response.json();
    
    const bookList = document.getElementById('bookList');
    bookList.innerHTML = "";
    const bookSelect = document.getElementById('bookSelect');
    bookSelect.innerHTML = "";

    data.books.forEach(book => {
        let li = document.createElement('li');
        li.textContent = `${book.title} (${book.publication_year})`;
        bookList.appendChild(li);

        let option = document.createElement('option');
        option.value = book.book_id;
        option.textContent = book.title;
        bookSelect.appendChild(option);
    });
}

async function addBook() {
    const title = document.getElementById('title').value;
    const publication_year = document.getElementById('publication_year').value;

    const response = await fetch('/api/add_book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, publication_year })
    });

    const data = await response.json();
    alert(data.message);
    fetchBooks();
}

async function addReview() {
    const book_id = document.getElementById('bookSelect').value;
    const user = document.getElementById('user').value;
    const rating = document.getElementById('rating').value;
    const comment = document.getElementById('comment').value;

    const response = await fetch('/api/add_review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ book_id, user, rating, comment })
    });

    const data = await response.json();
    alert(data.message);
    fetchReviews();
}

async function fetchReviews() {
    const response = await fetch('/api/reviews');
    const data = await response.json();
    
    const reviewList = document.getElementById('reviewList');
    reviewList.innerHTML = "";

    data.reviews.forEach(review => {
        let li = document.createElement('li');
        li.textContent = `${review.book_title} - ${review.user} rated ${review.rating}/5 - "${review.comment}"`;
        reviewList.appendChild(li);
    });
}

document.addEventListener("DOMContentLoaded", fetchBooks);
