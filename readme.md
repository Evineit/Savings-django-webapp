# Finance
Personal Savings website for managing expenses and subscriptions.

# Specification
Implementation of single-page-app finance client using JavaScript, HTML, and CSS. 
It fulfills the following requirements:

* Add incomes and expenses: Allow users to add incomes and expenses to the current account balance quickly.
    - Only the amount is needed to add an income/expense where balance is affected
    **** - Animated balance change 
    <!-- https://css-tricks.com/animating-number-counters/#the-new-school-css-solution -->

* Subscriptions: Allow users to add subscriptions as recurring expenses.
    - Recurring payments should have at least 2 types of scheduling (monthly, yearly)
    - View active subscriptions, including the next payment date, a description/title, and the type of schedule

* Wallets (accounts): Users can create new wallets
    - Accounts should have independent balance and payments
    - User should be able to change between accounts without reloading
    - User should be able to delete accounts without reloading

* Update recurring payments and incomes: Users should be able to edit any of their own payments.
    - Users should be able to stop a subscription without deleting the previous payments.
    - Stopping or changing the amount on a recurring payment shouldn't reload the page.
    - User should be able to edit the current subscription amount, influencing the next payments

* Order by: The incomes and expenses should be able to be ordered in the client without making another request
    - The recurring payment can be ordered by at least their next payment date, their amount, title
    - The incomes and expenses can be ordered by at least amount and date
### TODO maybe
** Response msg as alert handler

** Forecast: When a user clicks on Forecast, the user should be taken to a view where they see a text based forecast of the balance
    in the selected account given the recurring payments.

** Categories: Allow users categorize the payments in common categories.
    There should be a quick add button for incomes and expenses in every category.

** Logging: Maybe log?

** Graphs: Allow users to view a graph of the balance of the selected month.



# Understanding
In the distribution code is a Django project called project5 that contains a single app called finance. This entire application is just a single page, with JavaScript used to control the user interface. Let’s now take a closer look at the distribution code to see how that works.
I may refer to the account model as wallet or account. 

Take a look at finance/urls.py there are the routes to the API but let focus and notice that the default route loads an index function in views.py. So let’s go views.py and look at the index function. Notice that, as long as the user is signed in, this function creates a default account, if the user doesn't have any accounts, then it renders the finance/index.html template if the user is not logged in then it renders a template with only a button leading to log in.

Let’s look at that template, stored at finance/templates/finance/index.html. You’ll notice that first, the page shows the balance of the current account, after this, it has a sequence of buttons for adding incomes and expenses in the single or recurrent instance. Below that, notice that this page has a section where you get info about the account you are working with, as well as the sequence of buttons to change, add new accounts, and delete the current account. Below, the next section is defined by a sequence of div element containing a different form each. The first two contain the necessary inputs to add incomes and expenses. The next two contains the necessary information to add a recurrent income/expense, these are the most complex of the forms they require a title, amount, schedule type(Monthly or Yearly), and the starting date, this date is the date in which the recurrent payment will repeat the next months or the following years. Continuing with the rest of the forms, the next one is to change the amount of the recurrent movements (incomes/expenses), the last three contain the forms used on account management: to change, create, and delete accounts.
At the end of the template, there are four div used as containers for recurring payments and recurring incomes and simple incomes and expenses. They are filled with javascript fetch calls in the javascript file. It be can notice that there no more templates even when index.html could be refactored using smaller templates and including them its unnecessary because its a single-page web app.

Notice at the bottom of index.html, the JavaScript file finance/index.js is included. Open that file, stored at finance/static/finance/index.js, and take a look. Notice that when the DOM content of the page has been loaded, we load expenses and incomes in this account adding them to the respective container then we attach event listeners to each of the buttons and the selects inputs to order the containers, next the forms onsubmit functions are set, finally, the listeners to order are set. When the add income button is clicked, for example, we call the closeForm, then calling openForm with the argument "incomes"; What do these functions do? The closeForm function first closes any open form. Then openForm shows the form (by setting its style.display property to none). After that, if the form is submitted the function takes all of the form input fields (where the user might type in the amount) and sets their value to the empty string '' to clear them out then it makes a post request to the API creating the income. There are other functions and requests linked to the forms for handling the creation of the expenses and incomes as well as the logic of the account. The functions near the end of the javascript are used to order the incomes and expenses with various ways of sorting. 
I want to talk about the ordering client-side instead of server-side, I believe but I'm not entirely sure that it's better to request all the incomes/expenses and then ordering them to reduce the number of database queries, that's why I didn't do pagination like in the last project. But, to complete this part of the API the pagination was added but it's not used in the current web app.

Now let's get back to the views.py, as we have seen the index function, we will start with the account, accounts_delete, and accounts functions, the first of the three manage the creation of accounts and the GET request for getting a serialize object with the id, the name, and the current balance in every account from the user, the second function is a DELETE request with the id <int:account_id> given as a parameter is used to delete one of the user accounts. The third function if the request method is GET it will return the balance of the selected account using the account model with the function update_balance that value is then returned in a JSON response to update the balance shown in the template. The next functions have a pattern: all_incomes, all_expenses, all_***** these are used to get the objects associated with the account and to add incomes/expenses, and new recurrent incomes/expenses, at the end these functions return (if successful) a serialized version of the newly added object. After this, there are four functions to modify the previously mentioned recurrent objects with PUT requests, if successful these return a msg. These are for changing the amount in a recurrent income/expense and stopping the recurrent object from updating from the current date onwards.

The last thing we are gonna look at is models.py and the complementary util.py, there are 7 models including the user, we can see how the incomes and expenses models are fairly simple, even so, they have a serialize function which is used in the previously seen views.py. The more complex models are the account, the recurrent expenses, and the recurrent incomes, first, we'll focus on the account model. The account model has a update_balance function that takes the sum of the account expenses and incomes, this affects one of its fields (the balance) but there is something tricky, the function doesn't appear to be taking into account the recurrent payment and expenses, but it does as we'll see in the next 2 models. The RecurringPayment and the RecurringIncome model have a similar structure to the nonrecurrent objects, but they have a schedule_type a start_date and end_date, the reason to mention those field I because in the model there are 3 defined functions, but they are only wrappers that use the previously mentioned fields, these functions come from the last file (util.py).

In the last file util.py, we have four functions the first three are the same functions that the previous models wrap, all these functions receive a recurring object, the first function returns the next date that payment will be added based on the schedule type of that object, notice there are three schedule types but the first is only for testing purposes. The second function updates the recurring objects up to the provided date or the current time if left by default, using the cycles_at_date function the second function creates incomes or expenses up to the date provided. These incomes and expenses become children of the recurring object, this is how the account model calculates the recurring payments and updates its balance only using incomes and expenses. The third function returns an integer, the number is the cycles up to the provided date based on the schedule type of the recurring object. The last function in util.py is add_months, the function returns a new date with the months added to the source date.  

This is the end of the project description, I think it fulfills the complexity requirement by doing a single app page the complexity level increases there were many points were making a new page would be simpler but I wanted to test how well a single page app would end up without using a framework. I think the most important lesson was the testing, it gives you a foundation to work.
One of the most complex parts and the one I think makes the distinctiveness assignment fulfill to me, is the recurrent payments, the idea of generating children was pretty logical but I expected it to be easier to make, it was pretty hard but ended up pretty good. I think in none of the previous projects the idea of a recurrent event or handling a future event was featured, so I believe it's complex and distinctive.


# API
You’ll get to add/delete accounts, add/delete expenses, add/delete incomes, add/delete/update recurring payments and add/delete/update recurring incomes by using this application’s API.
<!-- TODO: Complete the api -->
This application supports the following API routes:

GET  /accounts/
- Get all accounts from the user serialized as JSON including the id, the name, and the current balance.

POST /accounts/
- Add new account/wallet, requires a name and starting amount

GET  /accounts/<int:account_id>
- Get Account balance
<!-- - Responds a Json with account info like balance -->
<!-- TODO: send more info -->

DELETE /accounts/<int:account_id>/delete
- Delete Account with given id if the user is the owner

<!--
Put /accounts/<int:account_id>/name
- Manage the default index account if default name is changed
- Change account name
-->

GET  /accounts/<int:account_id>/incomes
- Get all the incomes of given account

POST /accounts/<int:account_id>/incomes
- Add new income to given account


GET  /accounts/<int:account_id>/expenses
- Get all the expenses of given account

POST /accounts/<int:account_id>/expenses
- Add new expense to given account


GET  /accounts/<int:account_id>/recpayments
- Get all the recurrent expenses of given account

POST /accounts/<int:account_id>/recpayments
- Add new recurring expense to given account.


GET  /accounts/<int:account_id>/recincomes
- Get all the recurrent incomes of given account

POST /accounts/<int:account_id>/recincomes
- Add new recurring income to given account.

---------------------------------------------------------------------

<!-- GET /incomes/<int:id>
- Get the selected item info

GET /expenses/<int:id>
- Get the selected item info

DELETE /incomes/<int:id>/delete
- Delete the selected income 

DELETE /expenses/<int:id>/delete
- Delete the selected expense -->

---------------------------------------------------------------------

GET  /recpayments/<int:id>
- Get JSON response including the selected payment info. 

PUT  /recpayments/<int:id>/edit
- Changes the current amount affecting future payments

PUT  /recpayments/<int:id>/stop
- Stops the selected recurrent payment


GET  /recincomes/<int:id>
- Get JSON response including the selected income info. 

PUT  /recincomes/<int:id>/stop
- Stops the selected recurrent income

PUT  /recincomes/<int:id>/edit
- Changes the current amount affecting future incomes

<!-- DELETE /recpayments/<int:id>
- Deletes the selected item info -->

<!-- 
DELETE /recincomes/<int:id>
- Deletes the selected item info -->
