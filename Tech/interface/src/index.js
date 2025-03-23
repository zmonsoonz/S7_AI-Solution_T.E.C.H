import './styles/styles.css';

document.addEventListener('DOMContentLoaded', function() {

    const inputFields = document.querySelectorAll('input');

    inputFields.forEach(item => {
        item.addEventListener('blur', function() {
            if (item.value.trim() === '') {
                item.classList.add('invalid'); 
            }
        });
    
        item.addEventListener('focus', function() {
            item.classList.remove('invalid'); 
        });
    
        item.addEventListener('input', function() {
            if (item.value.trim() !== '') {
                item.classList.remove('invalid'); 
            }
        });
    })
    
    const form = document.getElementById('search');
    const tickets = document.querySelector('.tickets');
    function addTicket(data) {
        if (tickets.innerHTML) {
            tickets.innerHTML = '';
        }
        // Создаем HTML-код для новой карточки билета
        const ticketHTML = `
            <article class="tickets_card">
                <div class="card_content">
                    <div class="card_info">
                        <div class="card_info_item">
                            <svg height="20" width="20" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                                <path d="M192 93.7C192 59.5 221 0 256 0c36 0 64 59.5 64 93.7l0 66.3L497.8 278.5c8.9 5.9 14.2 15.9 14.2 26.6l0 56.7c0 10.9-10.7 18.6-21.1 15.2L320 320l0 80 57.6 43.2c4 3 6.4 7.8 6.4 12.8l0 42c0 7.8-6.3 14-14 14c-1.3 0-2.6-.2-3.9-.5L256 480 145.9 511.5c-1.3 .4-2.6 .5-3.9 .5c-7.8 0-14-6.3-14-14l0-42c0-5 2.4-9.8 6.4-12.8L192 400l0-80L21.1 377C10.7 380.4 0 372.7 0 361.8l0-56.7c0-10.7 5.3-20.7 14.2-26.6L192 160l0-66.3z"/>
                            </svg>
                            <span class="city">${data.from_city}</span>
                            <span class="airport">${data.from_airport}</span>
                            <span class="time">${formatUnixToCustomDate(data.departure_time)}</span>
                        </div>
                        <div class="card_info_item">
                            <svg height="20" width="20" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                                <path d="M464 256A208 208 0 1 0 48 256a208 208 0 1 0 416 0zM0 256a256 256 0 1 1 512 0A256 256 0 1 1 0 256z"/>
                            </svg>
                            <span class="city">${data.to_city}</span>
                            <span class="airport">${data.to_airport}</span>
                            <span class="time">${formatUnixToCustomDate(data.arrival_time)}</span>
                        </div>
                    </div>
                    <div class="card_delay">
                        <div class="card_chances">Шанс переноса рейса: ${data.delay_probability}%</div>
                        <div class="card_chances">Шанс полной отмены рейса: ${data.cancellation_probability}%</div>
                    </div>
                </div>
            </article>`;
        // Вставляем HTML-код с помощью insertAdjacentHTML
        tickets.insertAdjacentHTML('beforeend', ticketHTML);
    }

    function formatUnixToCustomDate(unixTimestamp) {
        const date = new Date(unixTimestamp * 1000); 
    
        const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        const formattedDate = date.toLocaleDateString('ru-RU', options); 
    
        const hours = String(date.getHours()).padStart(2, '0'); 
        const minutes = String(date.getMinutes()).padStart(2, '0'); 
    
        return `${formattedDate} ${hours}:${minutes}`; 
    }

    const notFound = document.querySelector('.ticket_not_found');
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const data = {}
        formData.forEach((value, key) => {
            data[key] = value;
        });
        const id = `${data.surname}_${data.ticket}`;

        fetch('http://localhost:3001/flights')
            .then(response => response.json())
            .then(data => {
                const flight = data.find(item => item.id === id)
                if (flight) {
                    notFound.style.visibility = 'hidden';
                    addTicket(flight)
                } else {
                    tickets.innerHTML = '';
                    notFound.style.visibility = 'visible';
                }
            })
            .catch(error => console.error('Ошибка:', error));
    })
})

