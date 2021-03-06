document.addEventListener('DOMContentLoaded', function() {
    let starting_acc = document.getElementById('accountName').dataset.accountId
    reload_lists(starting_acc)
    set_buttons()
    set_listeners()

    // These listeners enable the dropdown selector to change the sorting order of each list
    // based on the value of the dropdown selector
    // These are only called at the start because the targets won't change like the other listeners
    // in set_listeners()
    document.getElementById("rec_exp_order").addEventListener('change',() =>{
        order_rec_container_by(document.getElementById("rec_expenses_container"),document.getElementById("rec_exp_order").value)
    })
    document.getElementById("rec_inc_order").addEventListener('change',() =>{
        order_rec_container_by(document.getElementById("rec_incomes_container"),document.getElementById("rec_inc_order").value)
    })
    document.getElementById("inc_order").addEventListener('change',() =>{
        order_container_by(document.getElementById("incomes_container"),document.getElementById("inc_order").value)
    })
    document.getElementById("exp_order").addEventListener('change',() =>{
        order_container_by(document.getElementById("expenses_container"),document.getElementById("exp_order").value)
    })
});

function set_listeners(){
    let current_account_id = document.querySelector('#accountName').dataset.accountId;

    document.querySelector('#changeAccForm>form').onsubmit = function() {
        const new_account_id = document.getElementById("change_account").value
        if (new_account_id === current_account_id){
            closeForm()
            return false
        }
        const current_name = document.querySelector('#accountName')
        current_name.innerHTML = document.getElementById("change_account").selectedOptions[0].innerHTML
        current_name.dataset.accountId = new_account_id
        set_listeners()
        reload_balance(new_account_id)
        reload_lists(new_account_id)
        closeForm()
        return false
    }

    document.querySelector('#delete_accForm>form').onsubmit = function() {
        let csrftoken = getCookie('csrftoken');
        fetch(`/accounts/${current_account_id}/delete`,{
            method: 'DELETE',
            headers:{
                "X-CSRFToken": csrftoken
            }
        })
        .then( response =>{
            if (response.ok){
                document.querySelector(`#change_account>option[value="${current_account_id}"]`).remove()
                let csrftoken = getCookie('csrftoken');
                fetch('/accounts',{
                    method: 'GET',
                    headers:{
                        "X-CSRFToken": csrftoken
                    }
                })
                .then(response =>{
                    if (response.ok){
                        response.json().then(result=>{
                            if (result.length === 0) {
                                location.reload()
                                return false
                            }
                            const new_account = result[0]
                            const current_name = document.querySelector('#accountName')
                            current_name.innerHTML = new_account.name
                            current_name.dataset.accountId = new_account.id
                            set_listeners()
                            reload_balance(new_account.id)
                            reload_lists(new_account.id)
                            closeForm()
                        })
                    }
                })
                .catch( error => {
                    console.log('Error:', error);
                })

            }
        })
        .catch( error => {
            console.log('Error:', error);
        })
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
                response.json().then(result=>{
                    let new_account = document.createElement('option')
                    new_account.value = result.id
                    new_account.innerHTML = title
                    document.getElementById("change_account").append(new_account)
                })
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
        let csrftoken = getCookie('csrftoken');
        fetch(`/accounts/${current_account_id}/incomes`, {
                method: 'POST',
                body: JSON.stringify({
                    amount: amount
                }),
                headers: {
                    "X-CSRFToken": csrftoken
                },
                credentials: "include"
            })
            .then(response => {
                if (response.status === 201){
                    response.json().then(result =>{
                        let new_sub = create_basic_mov(result.sub)
                        new_sub.className += " subs-income"
                        document.getElementById("incomes_container").prepend(new_sub)
                        reload_balance(current_account_id)
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

    document.querySelector('#expensesForm>form').onsubmit = () => {
        const amount = document.querySelector('#expensesForm>form>input').value;
        document.querySelector('#expensesForm>form>input').value = null;
        let csrftoken = getCookie('csrftoken');
        fetch(`/accounts/${current_account_id}/expenses`, {
                method: 'POST',
                body: JSON.stringify({
                    amount: amount
                }),
                headers: {
                    "X-CSRFToken": csrftoken
                },
                credentials: "include"
            })
            .then(response => {
                if (response.status === 201){
                    response.json().then(result =>{
                        let new_sub = create_basic_mov(result.sub)
                        new_sub.className += " subs-expense"
                        document.getElementById("expenses_container").prepend(new_sub)
                        reload_balance(current_account_id)
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

    document.querySelector('#recexpensesForm>form').onsubmit = () => {
        const title = document.querySelector('#recexpensesForm>form>input[name="title"]').value;
        const amount = document.querySelector('#recexpensesForm>form>input[name="amount"]').value;
        const start_date = document.getElementById("start").value
        const schedule_type = document.getElementById("schedule_type").value
        reset_recurrent_form("recexpensesForm")
        // Send a POST request to the URL
        let csrftoken = getCookie('csrftoken');
        fetch(`/accounts/${current_account_id}/recpayments`, {
                method: 'POST',
                body: JSON.stringify({
                    amount: amount,
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
                        let new_sub = create_recurrent(result.sub, "recpayments", change_amount)
                        document.getElementById("rec_expenses_container").prepend(new_sub)
                        reload_balance(current_account_id)
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

    document.querySelector('#recIncomesForm>form').onsubmit = () => {
        const title = document.querySelector('#recIncomesForm>form>input[name="title"]').value;
        const amount = document.querySelector('#recIncomesForm>form>input[name="amount"]').value;
        const start_date = document.getElementById("income_start").value
        const schedule_type = document.getElementById("income_schedule_type").value
        reset_recurrent_form("recIncomesForm")
        // Send a POST request to the URL
        let csrftoken = getCookie('csrftoken');
        fetch(`/accounts/${current_account_id}/recincomes`, {
                method: 'POST',
                body: JSON.stringify({
                    amount: amount,
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
                        let new_sub = create_recurrent(result.sub, "recincomes", change_recincomes_amount)
                        document.getElementById("rec_incomes_container").prepend(new_sub)
                        reload_balance(current_account_id)
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
        reset_recurrent_form("recexpensesForm")
        closeForm()
        openForm("recexpenses")
    }
    document.querySelector('button[name="recincome"]').onclick = () => {
        reset_recurrent_form("recIncomesForm")
        closeForm()
        openForm("recIncomes")
    }

    document.querySelector('#acc-change').onclick = () => {
        closeForm()
        openForm("changeAcc")
    }
    document.querySelector('#acc-new').onclick = () => {
        closeForm()
        openForm("newAcc")
    }
    document.querySelector('#acc-delete').onclick = () => {
        closeForm()
        openForm("delete_acc")
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

function reload_lists(account_id) {
    const subs_div = document.getElementById("rec_expenses_container")
    const rec_incomes_div = document.getElementById("rec_incomes_container")
    const incomes_div = document.getElementById("incomes_container")
    const expenses_div = document.getElementById("expenses_container")
    subs_div.innerHTML = ''
    rec_incomes_div.innerHTML = ''
    incomes_div.innerHTML = ''
    expenses_div.innerHTML = ''

    fetch('/accounts/'+account_id+'/recpayments')
        .then(response => response.json())
        .then(payments => {
            payments.forEach(payment => {
                let new_subscription = create_recurrent(payment, "recpayments", change_amount)
                document.getElementById("rec_expenses_container").append(new_subscription)
            });
            order_rec_container_by(document.getElementById("rec_expenses_container"),"nex_pay_asc")
        });
    fetch('/accounts/'+account_id+'/recincomes')
    .then(response => response.json())
    .then(payments => {
        payments.forEach(payment => {
            let new_sub = create_recurrent(payment, "recincomes", change_recincomes_amount)
            document.getElementById("rec_incomes_container").append(new_sub)
        });
        order_rec_container_by(document.getElementById("rec_incomes_container"),"nex_pay_asc")
    });
    fetch('/accounts/'+account_id+'/incomes')
    .then(response => response.json())
    .then(payments => {
        payments.forEach(payment => {
            let new_sub = create_basic_mov(payment)
            new_sub.className+= " subs-income"
            incomes_div.append(new_sub)
        });
        order_container_by(document.getElementById("incomes_container"),"date_dsc")
    });
    fetch('/accounts/'+account_id+'/expenses')
    .then(response => response.json())
    .then(payments => {
        payments.forEach(payment => {
            let new_sub = create_basic_mov(payment)
            new_sub.className += " subs-expense"
            expenses_div.append(new_sub)
        });
        order_container_by(document.getElementById("expenses_container"),"date_dsc")
    });
}

// Refactored function to add the recurring incomes and expenses with the type and the change_amount function as parameter
function create_recurrent(payment, typeStr, change_amount_fun){
    const element = document.createElement('div')
    const top_div = document.createElement('div')
    const bot_div = document.createElement('div')
    const title = document.createElement('h6')
    const amount = document.createElement('h6')
    const stop_button = document.createElement('button')
    const amount_button = document.createElement('button')
    const schedule_type = document.createElement('h6')
    const next_date = document.createElement('h6')
    schedule_type.className = "btn-secondary subs-top-info btn-sm"
    next_date.className =     "btn-secondary subs-top-info btn-sm"
    element.className = "subs subs-expense"
    if (typeStr === "recincomes") element.className = "subs subs-income"
    top_div.className = "subs-top-container"
    bot_div.className = "subs-bot-container"
    amount.className = "subs-amount"
    element.dataset.id = payment.id
    element.dataset.title = payment.description
    element.dataset.amount = payment.amount
    element.dataset.next_date = payment.next_date_timestamp
    title.style = "flex: 1;"
    stop_button.innerText = "Stop"
    stop_button.className = "btn btn-outline-danger btn-hidden"
    stop_button.addEventListener('click', () =>{
        hide_payment(element)
        let csrftoken = getCookie('csrftoken');
        fetch(`/${typeStr}/${payment.id}/stop`,{
            method: 'PUT',
            headers:{
                "X-CSRFToken": csrftoken
            }
        })
        .catch( error => {
            console.log('Error:', error);
        })
    })
    amount_button.innerText = "Change amount"
    amount_button.className = "btn btn-outline-primary btn-hidden"
    amount_button.addEventListener('click', () =>{
        change_amount_fun(payment.id, amount)
    })

    title.innerHTML = `${payment.description}`;
    schedule_type.innerHTML = `Schedule:${payment.schedule_type}`
    next_date.innerHTML = `Next payment date: ${payment.next_date}`
    amount.innerHTML = `Amount:${payment.amount}$`
    top_div.append(title)
    top_div.append(schedule_type)
    top_div.append(next_date)
    bot_div.append(amount_button)
    bot_div.append(stop_button)
    bot_div.append(amount)
    element.append(top_div)
    element.append(bot_div)

    return element
}

function create_basic_mov(payment){
    const element = document.createElement('div')
    const top_div = document.createElement('div')
    const title = document.createElement('h6')
    const amount = document.createElement('h6')
    element.className = "subs"
    top_div.className = "subs-top-container"
    element.style.animation ="none"
    element.style.height = "60px"
    element.dataset.id = payment.id
    element.dataset.amount = payment.amount
    element.dataset.next_date = payment.timestamp
    title.style = "flex: 1;"
    title.innerHTML = `Added date: ${payment.added_date}`;
    amount.innerHTML = `Amount:${payment.amount}$`
    top_div.append(title)
    top_div.append(amount)
    element.append(top_div)
    return element
}

function change_amount(payment_id, amount_elem){
    document.getElementById("amount_form").style.display = "block";
    document.querySelector('#amount_form>form').onsubmit = function() {
        const amount = document.querySelector('#amount_form>form>input').value;
        document.querySelector('#amount_form>form>input').value = null;
        let csrftoken = getCookie('csrftoken');
        fetch(`/recpayments/${payment_id}/edit`,{
            method: 'PUT',
            body: JSON.stringify({
                amount: amount
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

function change_recincomes_amount(payment_id, amount_elem){
    document.getElementById("amount_form").style.display = "block";
    document.querySelector('#amount_form>form').onsubmit = function() {
        const amount = document.querySelector('#amount_form>form>input').value;
        document.querySelector('#amount_form>form>input').value = null;
        let csrftoken = getCookie('csrftoken');
        fetch(`/recincomes/${payment_id}/edit`,{
            method: 'PUT',
            body: JSON.stringify({
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

function hide_payment(element){
    element.style.animationPlayState = 'running'
    setTimeout(() => {
        element.remove()
    }, 3000);
}

function reset_recurrent_form(form){
    let today = new Date().toISOString().split("T")[0]
    document.querySelector(`#${form}>form>input`).value = null;
    document.querySelector(`#${form}>form>input[name="amount"]`).value = null
    document.getElementById("start").setAttribute("min", today);
    document.getElementById("start").setAttribute("value", today);
    document.getElementById("income_start").setAttribute("min", today);
    document.getElementById("income_start").setAttribute("value", today);
}

function sort_by_amount_asc(a,b){
    if (+a.dataset.amount > +b.dataset.amount) {
      return 1;
    }
    if (+a.dataset.amount < +b.dataset.amount) {
      return -1;
    }
    return 0;
}
function sort_by_timestamp(a,b){
    if (+a.dataset.next_date > +b.dataset.next_date) {
        return 1;
      }
      if (+a.dataset.next_date < +b.dataset.next_date) {
        return -1;
      }
      return 0;
}

function order_rec_container_by(containerElem, sort){
    let arr = Array.from(containerElem.children)
    containerElem.innerHTML = ''
    let new_arr;
    if (sort === "amount_asc") {
        new_arr = arr.sort(sort_by_amount_asc);
    } else if (sort === "amount_dsc") {
        new_arr = arr.sort(sort_by_amount_asc).reverse();
    } else if (sort === "nex_pay_asc") {
        new_arr = arr.sort(sort_by_timestamp)
    } else if (sort === "nex_pay_dsc") {
        new_arr = arr.sort(sort_by_timestamp).reverse()
    } else if (sort === "title_asc") {
        new_arr = arr.sort((a, b) => a.dataset.title.localeCompare(b.dataset.title))
    } else if (sort === "title_dsc") {
        new_arr = arr.sort((a, b) => b.dataset.title.localeCompare(a.dataset.title))
    } else {
        return
    }
    new_arr.forEach(elem =>{
        containerElem.append(elem)
    })
  }
  function order_container_by(containerElem, sort){
    let arr = Array.from(containerElem.children)
    containerElem.innerHTML = ''
      let new_arr;
      if (sort === "amount_asc") {
          new_arr = arr.sort(sort_by_amount_asc);
      } else if (sort === "amount_dsc") {
          new_arr = arr.sort(sort_by_amount_asc).reverse();
      } else if (sort === "date_asc") {
          new_arr = arr.sort(sort_by_timestamp)
      } else if (sort === "date_dsc") {
          new_arr = arr.sort(sort_by_timestamp).reverse()
      } else {
          return
      }
    new_arr.forEach(elem =>{
        containerElem.append(elem)
    })
  }