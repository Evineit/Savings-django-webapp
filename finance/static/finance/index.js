document.addEventListener('DOMContentLoaded', function() {
    reload_subs("Default")
    set_buttons()
    set_listeners()
    
});

function set_listeners(){
    let account_name = document.querySelector('#accountName').dataset.accountName;
    document.querySelector('#changeAccForm>form').onsubmit = function() {
        const new_account = document.getElementById("change_account").value
        if (new_account == account_name){
            closeForm()
            return false
        } 
        const current_name = document.querySelector('#accountName')
        current_name.innerHTML = new_account
        current_name.dataset.accountName = new_account
        set_listeners()
        reload_balance(new_account)
        reload_subs(new_account)
        closeForm()
        return false
    }

    document.querySelector('#newAccForm>form').onsubmit = function() {
        const title = document.querySelector('#newAccForm>form>input[name="title"]').value;
        const amount = document.querySelector('#newAccForm>form>input[name="amount"]').value;
        let csrftoken = getCookie('csrftoken');
        fetch('/accounts', {
            method: 'POST',
            body: JSON.stringify({
                title: title,
                amount: amount,
            }),
            headers: {
                "X-CSRFToken": csrftoken
            }
        })
        .then(response =>{
            if (response.ok){
                new_account = document.createElement('option') 
                new_account.value = title
                new_account.innerHTML = title
                document.getElementById("change_account").append(new_account) 
            }
            document.querySelector('#newAccForm>form>input[name="title"]').value = null;
            document.querySelector('#newAccForm>form>input[name="amount"]').value = null;
        })
        closeForm()
        return false
        
    }


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
                        reload_balance(account_name)
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
}

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
    document.querySelector('#acc-change').onclick = () => {
        closeForm()
        openForm("changeAcc")
    }
    document.querySelector('#acc-new').onclick = () => {
        closeForm()
        openForm("newAcc")
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
    fetch('/accounts/'+account_name+'/recpayments')
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
    const top_div = document.createElement('div')
    const bot_div = document.createElement('div')
    const title = document.createElement('h6')
    const amount = document.createElement('h6')
    const stop_button = document.createElement('button')
    const amount_button = document.createElement('button')
    element.className = "subs"
    top_div.className = "subs-top-container"
    element.dataset.id = payment.id
    title.style = "flex: 1;"
    stop_button.innerText = "Stop"
    stop_button.className = "btn btn-outline-danger btn-hidden"
    stop_button.addEventListener('click', () =>{
        hide_payment(element)
        stop_payment(payment.id)
    })
    amount_button.innerText = "Change amount"
    amount_button.className = "btn btn-outline-primary btn-hidden"
    amount_button.addEventListener('click', () =>{
        change_amount(payment.id, amount)
    })

    title.innerHTML = `id: ${payment.id}, ${payment.description}, Schedule:${payment.schedule_type}
    , Next payment date: ${payment.next_date}`;
    amount.innerHTML = `Amount:${payment.amount}$`
    top_div.append(title)
    top_div.append(amount)
    bot_div.append(amount_button)  
    bot_div.append(stop_button)  
    element.append(top_div)
    element.append(bot_div)

    return element  
}

function change_amount(payment_id, amount_elem){
    document.getElementById("amount_form").style.display = "block";
    document.querySelector('#amount_form>form').onsubmit = function() {
        const amount = document.querySelector('#amount_form>form>input').value;
        document.querySelector('#amount_form>form>input').value = null;
        let csrftoken = getCookie('csrftoken');
        fetch('/recpayments/'+payment_id,{
            method: 'PUT',
            body: JSON.stringify({
                action: 'change_amount',
                amount: amount,
            }),
            headers:{
                "X-CSRFToken": csrftoken
            }
        })
        .then( response =>{
            closeForm()
            if (response.ok){
                response.json().then(result =>{
                    amount_elem.innerHTML = `Amount:${result.amount}$`
                })
            }
        })
        .catch( error => {
            console.log('Error:', error);
        })
        return false
    }
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

