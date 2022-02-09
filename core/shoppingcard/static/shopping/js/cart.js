let updateBtns = document.getElementsByClassName('update-cart')

for (let i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        let productId = this.dataset.product
        let action = this.dataset.action
        console.log('productID: ', productId, 'action: ', action);
        console.log('Usuario: ', user);
        if (user === 'AnonymousUser') {
            console.log('Usuario no logueado');
        } else {
            updateUserPedido(productId, action)
        }
    })
}

function updateUserPedido(productId, action) {
    console.log('Usuario esta logeado');

    let url = '/shopping/update_item'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action })
    })
        .then((response) => {
            return response.json()
        })
        .then((data) => {
            console.log('data:', data)
            location.reload()
        })
}