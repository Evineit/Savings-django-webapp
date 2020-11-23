# Finance
Personal Savings website for managing expenses and subscriptions.

# Understanding
In the distribution code is a Django project called project5 that contains a single app called finance. This entire application is just a single page, with JavaScript used to control the user interface. Let’s now take a closer look at the distribution code to see how that works.
I may refer to the account model as wallet or account. 

Take a look at finance/urls.py and notice that the default route loads an index function in views.py. So let’s up views.py and look at the index function. Notice that, as long as the user is signed in, this function creates a default account if the user doesn't have any accounts then it renders the finance/index.html template.

 Let’s look at that template, stored at finance/templates/finance/index.html. You’ll notice that first the page shows the balance of the current account , after this it has a sequence of buttons for adding incomes and expense in single or recurrent instance. Below that, notice that this page has a section where you get info about the account you are working with, as well as the sequence of buttons to change or add new accounts. Below the next section is each defined by a div element containing a different form. The first four contains the necessary inputs to add incomes and expenses. The next one is to change the amount of the recurrent movements, the last two contain the forms used on account management to change and create accounts.
 At the end of the template there are two div used as container for the recurring payments and recurring incomes. They are filled with javascript fetch calls.

Notice at the bottom of index.html, the JavaScript file finance/index.js is included. Open that file, stored at finance/static/finance/index.js, and take a look. Notice that when the DOM content of the page has been loaded, we load the recurrent expenses and recurring incomes in this account adding them to the respective container then we attach event listeners to each of the buttons and set the forms onsubmit functions. When the add income button is clicked, for example, we call the closeForm, then calling openForm with the argument "incomes";What do these functions do? The closeForm function first closes any open form. Then openForm show the form (by setting its style.display property to none). After that, if the form is submitted the function takes all of the form input fields (where the user might type in the amount) and sets their value to the empty string '' to clear them out then it makes a post request to the API creating the income. There are other functions and request linked to the forms for handling the creation of the expenses and incomes as well as the accounts logic. The function today at the end of the javascript is to set the value of the date input for the recurring movements creation white todays date.



# API
You’ll get to add/delete accounts, add/delete expenses, add/delete incomes, add/delete/update recurring payments and add/delete/update recurring incomes by using this application’s API.

This application supports the following API routes:

<!-- GET /accounts/
- Get user accounts -->

POST /accounts/
- Add new account/wallet

GET /accounts/<str:account>
- Get Account info (Balance)
<!-- - Responds a Json with account info like balance -->

<!--
DELETE /accounts/<str:account>
- Manage the default index account if default is deleted
- Delete Account | Confirmation needed | checkbox 

Put /accounts/<str:account>/name
- Manage the default index account if default name is changed
- Change account name
-->

POST /accounts/<str:account>
- Add new expense, income, recurring payment
- Receives JSON with {type, amount, extra info}

GET /accounts/<str:account>/incomes
- Get all the incomes of given account

GET /accounts/<str:account>/expenses
- Get all the expenses of given account

GET /accounts/<str:account>/recpayments
- Get all the recurrent expenses of given account

GET /accounts/<str:account>/recincomes
- Get all the recurrent incomes of given account

POST /accounts/<str:account>/recincomes
- Add new recurring income.

------------------------------------------------------------------- 

<!-- GET /incomes/<int:id>
- Get the selected item info

GET /expenses/<int:id>
- Get the selected item info

DELETE /incomes/<int:id>
- Delete the selected item info

DELETE /expenses/<int:id>
- Delete the selected item info
-->
---------------------------------------------------------------------

GET /recpayments/<int:id>
- Get the selected item info

PUT /recpayments/<int:id>
- takes an "action" parameter to stop or change the current  payment amount 

<!-- DELETE /recpayments/<int:id>
- Deletes the selected item info -->

GET /recincomes/<int:id>
- Get the selected item info

PUT /recincomes/<int:id>/stop
- Stops the selected recurrent payment

PUT /recincomes/<int:id>/edit
- Changes the current amount affecting future payments

<!-- 
DELETE /recincomes/<int:id>
- Deletes the selected item info -->



# Specification
Implementation of single-page-app finance client using JavaScript, HTML, and CSS. 
It fulfills the following requirements:

* Quickly add incomes and expenses: Allow users to add incomes and expenses to the current account balance quickly.
    - Only the amount is needed to add an income/expense where balance is affected

    **** - Animated balance change 
    <!-- https://css-tricks.com/animating-number-counters/#the-new-school-css-solution -->

* Subscriptions: Allow users to add subscriptions as recurring expenses.
    - Recurring payments should have at least 2 types of scheduling (monthly, yearly)
    - View active subscriptions, including the next payment date, a description/title and the type of schedule

* Wallets (accounts): Users can create new wallets
    - Accounts should have independent balanc e and payments
    - User should be able to change between accounts without reloading
    <!-- TODO: Users should only be able to interact with their own things API-wise -->
    <!-- TODO: Delete account -->

* Update recurring payments and incomes: Users should be able edit any of their own payments.
    - Users should be able to stop a subscription without deleting the previous payments.
    - Stopping or changing the amount on a recurring payment shouldn't reload the page.
    - User should be able to edit the current subscription amount, influencing next payments
  
* Recurring incomes: Users can add recurring incomes in the current account

* Order by: The incomes and expenses should be able to be ordered in the client without making another request
    - The recurring payment can be ordered by at least their next payment date, their amount, title
    - The incomes and expenses can be ordered by at least amount and date

** Forecast: When a user clicks on Forecast, the user should be taken to a view where they see a text based forecast of the balance
    in the selected account given the recurring payments.

** Categories: Allow users categorize the payments in common categories.
    There should be a quick add button for incomes and expenses in every category.

** Logging: Maybe log?

** Graphs: Allow users to view a graph of the balance of the selected month.

