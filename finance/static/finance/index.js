document.addEventListener('DOMContentLoaded', function() {
    
    document.querySelector('button[name="income"]').onclick = () => {
        closeForm()
        openForm("incomes")
    }
    document.querySelector('button[name="expense"]').onclick = () => {
        closeForm()
        openForm("expenses")
    }
    document.querySelector('button[name="recexpense"]').onclick = () => {
        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth() + 1; //January is 0!
        var yyyy = today.getFullYear();
        if (dd < 10) {
            dd = '0' + dd
        }
        if (mm < 10) {
            mm = '0' + mm
        }

        today = yyyy + '-' + mm + '-' + dd;
        document.getElementById("start").setAttribute("min", today);
        document.getElementById("start").setAttribute("value", today);
        closeForm()
        openForm("recexpenses")
    }
    document.querySelector('#incomesForm>form').onsubmit = () => {
        const account_name = document.querySelector('#content>h2').innerHTML;
        const amount = document.querySelector('#incomesForm>form>input').value;

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
                console.log(response)
            })
            .then(result => {
                // Print result
                console.log(result);
            })
            // Catch any errors and log them to the console
            .catch(error => {
                console.log('Error:', error);
            });
        console.log("test submit income")
        reload_balance(account_name)
        return false
    }
    document.querySelector('#expensesForm>form').onsubmit = () => {
        const account_name = document.querySelector('#content>h2').innerHTML;
        const amount = document.querySelector('#expensesForm>form>input').value;

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
                response.json()
                console.log(response)
            })
            .then(result => {
                // Print result
                console.log(result);
            })
            // Catch any errors and log them to the console
            .catch(error => {
                console.log('Error:', error);
            });
        console.log("test submit expense")
        reload_balance(account_name)
        return false
    }
    document.querySelector('#recexpensesForm>form').onsubmit = () => {
        const account_name = document.querySelector('#content>h2').innerHTML;
        const amount = document.querySelector('#recexpensesForm>form>input').value;
        const start_date = document.getElementById("start").value
        const schedule_type = document.getElementById("schedule_type").value
        // Send a POST request to the URL
        let csrftoken = getCookie('csrftoken');
        fetch('/accounts/'+account_name, {
                method: 'POST',
                body: JSON.stringify({
                    type: "rec_expense",
                    amount: amount,
                    // Change or remove
                    description: "test",
                    start_date: start_date,
                    schedule_type: schedule_type,
                }),
                headers: {
                    "X-CSRFToken": csrftoken
                },
                credentials: "include"
            })
            .then(response => {
                response.json()
                console.log(response)
            })
            .then(result => {
                // Print result
                console.log(result);
            })
            // Catch any errors and log them to the console
            .catch(error => {
                console.log('Error:', error);
            });
        console.log("test submit expense")
        reload_balance(account_name)
        return false
    }
});

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
}

function reload_balance(account_name) {
    const balance = document.querySelector("#balance")
    fetch('/accounts/' + account_name)
        .then(response => response.json())
        .then(account_info => {
            balance.innerHTML = account_info.balance + "$"
        });
}

