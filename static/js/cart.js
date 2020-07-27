// Add to Cart button funcitonality

var updateButtons = document.getElementsByClassName("update-cart");

for (var i = 0; i < updateButtons.length; i++) {
  updateButtons[i].addEventListener("click", function () {
    var productID = this.dataset.product;
    var action = this.dataset.action;

    //check is user is logged in or anon

    if (user == "AnonymousUser") {
      addCookieItem(productID, action);
    } else {
      updateUserOrder(productID, action);
    }
  });
}

// update guest user's cart data

function addCookieItem(productID, action) {
  // logic if product is added
  if (action == "add") {
    if (cart[productID] == undefined) {
      cart[productID] = { quantity: 1 };
    } else {
      cart[productID]["quantity"] += 1;
    }
  }

  if (action == "remove") {
    cart[productID]["quantity"] -= 1;

    if (cart[productID]["quantity"] <= 0) {
      delete cart[productID];
    }
  }
  console.log("Cart: ", cart);
  document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";
  location.reload();
}

//update Logged in user's cart data

function updateUserOrder(productID, action) {
  var url = "/update_item/";
  // send post request with data of product to be added
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ productID: productID, action: action }),
  });

  location.reload();
}
