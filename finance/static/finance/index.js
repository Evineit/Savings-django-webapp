document.addEventListener('DOMContentLoaded', function() {
    const account_name = document.querySelector('#content>h2').innerHTML;
    reload_subs(account_name)
    set_buttons()
    document.querySelector('#incomesForm>form').onsubmit = function() {
        const amount = document.querySelector('#incomesForm>form>input').value;
        document.querySelector('#incomesForm>form>input').value = null;
        // Send a POST request to the URL
        let csrftoken = getCookie('csrftoken');
        fetch('/accounts/'+account_name, {
                method: 'POST',
                body: JSON.stringify({
                    type: "income",
                    amount: amount,
                }),
                headers: {
                    "X-CSRFToken": csrftoken
                },
                credentials: "include"
            })
            .then(response => {
                response.json()
                if (response.status == 201){
                    reload_balance(account_name)
                    }
            })
            // Catch any errors and log them to the console
            .catch(error => {
                console.log('Error:', error);
            });
        closeForm()
        return false
    }
    document.querySelector('#expensesForm>form').onsubmit = () => {
        const amount = document.querySelector('#expensesForm>form>input').value;
        document.querySelector('#expensesForm>form>input').value = null;
        // Send a POST request to the URL
        let csrftoken = getCookie('csrftoken');
        fetch('/accounts/'+account_name, {
                method: 'POST',
                body: JSON.stringify({
                    type: "expense",
                    amount: amount,
                }),
                headers: {
                    "X-CSRFToken": csrftoken
                },
                credentials: "include"
            })
            .then(response => {
                // response.json()
                if (response.status == 201){
                    reload_balance(account_name)
                }
            })
            // Catch any errors and log them to the console
            .catch(error => {
                console.log('Error:', error);
            });
        closeForm()
        return false
    }

    document.querySelector('#recexpensesForm>form').onsubmit = () => {
        const title = document.querySelector('#recexpensesForm>form>input[name="title"]').value;
        const amount = document.querySelector('#recexpensesForm>form>input[name="amount"]').value;
        const start_date = document.getElementById("start").value
        const schedule_type = document.getElementById("schedule_type").value
        reset_recexpense()
        // Send a POST request to the URL
        let csrftoken = getCookie('csrftoken');
        fetch('/accounts/'+account_name, {
                method: 'POST',
                body: JSON.stringify({
                    type: "rec_expense",
                    amount: amount,
                    // Change or remove
                    description: title,
                    start_date: start_date,
                    schedule_type: schedule_type,
                }),
                headers: {
                    "X-CSRFToken": csrftoken
                },
                credentials: "include"
            })
            .then(response => {
                if (response.ok){
                    response.json().then(result =>{
                        new_sub = create_sub(result.sub)
                        document.querySelector(".subs-container").prepend(new_sub)
                    })
                }
            })
            // Catch any errors and log them to the console
            .catch(error => {
                console.log('Error:', error);
            });        
        closeForm()
        return false
    }
});

function set_buttons() {
    document.querySelector('button[name="income"]').onclick = () => {
        closeForm()
        openForm("incomes")
    }
    document.querySelector('button[name="expense"]').onclick = () => {
        closeForm()
        openForm("expenses")
    }
    document.querySelector('button[name="recexpense"]').onclick = () => {
        reset_recexpense()
        closeForm()
        openForm("recexpenses")
    }
}

// The following function is from 
// https://docs.djangoproject.com/en/dev/ref/csrf/#ajax
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

function openForm(name) {
    document.getElementById(name + "Form").style.display = "block";
}

function closeForm() {
    document.querySelectorAll(".form-popup").forEach((element) => {
        element.style.display = "none"
    })
    return false
}

function reload_balance(account_name) {
    const balance = document.querySelector("#balance")
    fetch('/accounts/' + account_name)
        .then(response => response.json())
        .then(account_info => {
            balance.innerHTML = account_info.balance + "$"
        });
}

function reload_subs(account_name) {
    const subs_div = document.querySelector(".subs-container")
    subs_div.innerHTML = ''
    fetch('/recpayments/' + account_name)
        .then(response => response.json())
        .then(payments => {
            payments.forEach(payment => {
                new_sub = create_sub(payment)
                document.querySelector(".subs-container").append(new_sub)
            });
        });
}

function create_sub(payment){
    const element = document.createElement('div')
    const title = document.createElement('h6')
    const stop_button = document.createElement('button')
    element.className = "subs"
    element.dataset.id = payment.id
    stop_button.innerText = "Stop"
    stop_button.className = "btn btn-outline-danger btn-hidden"
    stop_button.addEventListener('click', () =>{
        hide_payment(element)
        stop_payment(payment.id)
    })

    title.innerHTML = `id: ${payment.id}, ${payment.description}, ${payment.amount}$, Schedule:${payment.schedule_type}
    , Next payment date: ${payment.next_date}`;
    element.append(title)
    element.append(stop_button)  
    return element  
}

function stop_payment(payment_id){
    let csrftoken = getCookie('csrftoken');
    fetch('/recpayments/'+payment_id,{
        method: 'PUT',
        body: JSON.stringify({
            action: 'stop',
            remove_last_movement: false,
        }),
        headers:{
            "X-CSRFToken": csrftoken
        }
    })
    .catch( error => {
        console.log('Error:', error);
    })
}

function hide_payment(element){
    element.style.animationPlayState = 'running'
    setTimeout(() => {
        element.remove()
    }, 3000);
}

function reset_recexpense(){
    document.querySelector('#recexpensesForm>form>input').value = null;
    document.getElementById("start").setAttribute("min", today());
    document.getElementById("start").setAttribute("value", today());
}

function today() {
    var today = new Date();
    // Maybe change for all timezones
    var dd = today.getUTCDate();
    var mm = today.getUTCMonth() + 1; //January is 0!
    var yyyy = today.getUTCFullYear();
    if (dd < 10) {
        dd = '0' + dd
    }
    if (mm < 10) {
        mm = '0' + mm
    }

    today = yyyy + '-' + mm + '-' + dd;
    return today
}

