// if guest user and no physical product, hide shipping form
if (shipping == "False") {
  document.getElementById("shipping-info").innerHTML = "";
}

// if user logged in but physical product, hide only user info form
if (user != "AnonymousUser") {
  document.getElementById("user-info").innerHTML = "";
}

// if user logged in and no physical product, hide user info and shipping form & show payment form
if (shipping == "False" && user != "AnonymousUser") {
  document.getElementById("form-wrapper").classList.add("hidden");
  document.getElementById("payment-info").classList.remove("hidden");
}

// after name/shipping info added, hide continue button and show payment form
var form = document.getElementById("form");
// get csrf token
//csrftoken = form.getElementsByTagName("input")[0].value;

form.addEventListener("submit", (e) => {
  // don't submit initial data
  e.preventDefault();

  document.getElementById("form-button").classList.add("hidden");
  document.getElementById("payment-info").classList.remove("hidden");
});

// submit form when 'confirm purchase' clicked
document.getElementById("make-payment").addEventListener("click", (e) => {
  submitFormData();
});

function submitFormData() {
  console.log("Payment Submited");
  // create two json objects to store form data
  var userFormData = {
    user: null,
    email: null,
    total: total,
  };

  var shippingInfo = {
    address: null,
    city: null,
    state: null,
    zipcode: null,
  };
  // fill json objects with user data
  if (shipping != "False") {
    shippingInfo.address = form.address.value;
    shippingInfo.city = form.city.value;
    shippingInfo.state = form.state.value;
    shippingInfo.zipcode = form.zipcode.value;
  }

  if (user == "AnonymousUser") {
    userFormData.name = form.name.value;
    userFormData.email = form.email.value;
  }

  // send post request with data of order to view function to be submitted
  var url = "/process_order/";

  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({ form: userFormData, shipping: shippingInfo }),
  }) // extracts json data from response
    .then((response) => response.json())
    // output data on log and redirect to homepage
    .then((data) => {
      console.log("Success: ", data);
      alert("Transaction Complete");
      cart = {};
      document.cookie = "cart=" + JSON.stringify(cart) + ";domain=;path=/";
      console.log("cart reset! cart now: ", cart);

      //window.location.href = "redirect";
    });
}
