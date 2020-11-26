# Finance
Personal Savings website for managing expenses and subscriptions.

# Understanding
In the distribution code is a Django project called project5 that contains a single app called finance. This entire application is just a single page, with JavaScript used to control the user interface. Let’s now take a closer look at the distribution code to see how that works.
I may refer to the account model as wallet or account. 

Take a look at finance/urls.py there are the routes to the api but let focus and notice that the default route loads an index function in views.py. So let’s up views.py and look at the index function. Notice that, as long as the user is signed in, this function creates a default account, if the user doesn't have any accounts, then it renders the finance/index.html template if the user is not logged in then it renders a template with only a button leading to log in.

 Let’s look at that template, stored at finance/templates/finance/index.html. You’ll notice that first the page shows the balance of the current account, after this it has a sequence of buttons for adding incomes and expense in single or recurrent instance. Below that, notice that this page has a section where you get info about the account you are working with, as well as the sequence of buttons to change, add new accounts and delete the current account. Below the next section is each defined by a div element containing a different form. The first four contains the necessary inputs to add incomes and expenses. The next one is to change the amount of the recurrent movements (incomes/expenses), the last three contain the forms used on account management to change, create and delete accounts.
 At the end of the template there are four div used as containers for the recurring payments and recurring incomes and simple incomes and expenses. They are filled with javascript fetch calls in the javascript file. It be can notice that there no more templates even when index.html could be refactor using smaller templates and including them its unnecessary because its a single paged webapp.

Notice at the bottom of index.html, the JavaScript file finance/index.js is included. Open that file, stored at finance/static/finance/index.js, and take a look. Notice that when the DOM content of the page has been loaded, we load expenses and incomes in this account adding them to the respective container then we attach event listeners to each of the buttons and the selects inputs to order the containers, next the forms onsubmit functions are set, finally the listeners for ordering are set. When the add income button is clicked, for example, we call the closeForm, then calling openForm with the argument "incomes";What do these functions do? The closeForm function first closes any open form. Then openForm show the form (by setting its style.display property to none). After that, if the form is submitted the function takes all of the form input fields (where the user might type in the amount) and sets their value to the empty string '' to clear them out then it makes a post request to the API creating the income. There are other functions and request linked to the forms for handling the creation of the expenses and incomes as well as the accounts logic. The function today() near the end of the javascript is to set the value of the date input for the recurring movements creation white todays date. 
I want to talk about the ordering client-side instead of server-side, i believe but I'm no entirely sure that its better to request all the incomes/expenses and then ordering them in order to reduce the amount of database queries, thats why I didn't do pagination like in the last project. But, to complete this part of the API the pagination was added but it's not used in the current webapp.

Now let's get back to the views.py, as we have seen the index function, we will start with the account and accounts functions, these 2 manage the creation of accounts and the the request for getting the current balance in the account from the user with the id <int:account_id> given as parameter. The second function uses the account model with the function update_balance that value is then returned in a Json response in order to update the balance shown in the template. The next function have a pattern all_incomes, all_expenses, all_***** these are used to get the objects associated with the account and to add new incomes and expenses, at the end this functions return (if successful) a serialized version of the new add object. After this there are functions to modify the previous mentioned objects with PUT request, if successful these return a msg.

The last thing we are gonna look is models.py and the complementary util.py, there are 7 models including the user, we can see how the incomes and expenses models are fairly simple, even so, they have a serialize function which is used in the previously seen views.py. The more complex models are the account, the recurrent expenses and the recurrent incomes, first we'll focus in the account model. The account model has a update_balance function that takes the sum of the account expenses and incomes, this affects one of its fields (the balance) but there is something tricky, the function doesn't appear to be taking in account the recurrent payment and expenses, but it does as we'll see in the next 2 models. The RecurringPayment and the RecurringIncome model have a similar structure to the non recurrent objects, but they have a schedule_type a start_date and end_date, the reason to mention those field i because in the model there are 3 defined functions, but they are only wrappers that use the previously mentioned fields, these functions come from the last file (util.py).

In the the last file util.py we have four functions the first three are the same functions that the previous models wrap, all these functions receive a recurring object, the first function returns the next date that a payment will be added based on the schedule type of that object, notice there are three schedule types but the first is only for testing purposes. The second function updates the recurring objects up to the provided date or the current time if left by default, using the cycles_at_date function the second function creates incomes or expenses up to the date provided. This incomes and expenses become children of the recurring object, this is how the account model calculates the recurring payments and updates its balance only using incomes and expenses. The third function returns a integer, the number is the cycles up to the provided date based on the schedule type of the recurring object. The last function in util.py is add_months, the function return a new date with the months added to source date.  

This is the end of the project description, I think it fulfills the complexity requirement by doing a single app page the complexity level increases there were many points were making a new page would be simpler but I really wanted to test how well a single page app would end up without using a framework. I think the most important lesson was the testing, it really gives you a foundation to work.
One of the most complex part to me is the recurrent payments, the idea of generating children was pretty logic but I expected it to be easier to make, it was pretty hard but ended up pretty good.

# API
You’ll get to add/delete accounts, add/delete expenses, add/delete incomes, add/delete/update recurring payments and add/delete/update recurring incomes by using this application’s API.
<!-- TODO: Complete the api -->
This application supports the following API routes:

GET /accounts/
- Get all user accounts id

POST /accounts/
- Add new account/wallet

GET /accounts/<int:account_id>
- Get Account info (Balance)
<!-- - Responds a Json with account info like balance -->
<!-- TODO: send more info -->

DELETE /accounts/<int:account_id>/delete
- Delete Account 

<!--
Put /accounts/<int:account_id>/name
- Manage the default index account if default name is changed
- Change account name
-->

POST /accounts/<int:account_id>
- Add new expense, income, recurring payment
- Receives JSON with {type, amount, extra info}

GET /accounts/<int:account_id>/incomes
- Get all the incomes of given account

GET /accounts/<int:account_id>/expenses
- Get all the expenses of given account

GET /accounts/<int:account_id>/recpayments
- Get all the recurrent expenses of given account

GET /accounts/<int:account_id>/recincomes
- Get all the recurrent incomes of given account

POST /accounts/<int:account_id>/recincomes
- Add new recurring income.

------------------------------------------------------------------- 

<!-- GET /incomes/<int:id>
- Get the selected item info

GET /expenses/<int:id>
- Get the selected item info

DELETE /incomes/<int:id>/delete
- Delete the selected income 

DELETE /expenses/<int:id>/delete
- Delete the selected expense -->

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
    - Accounts should have independent balance e and payments
    - User should be able to change between accounts without reloading
    <!-- FIX:  use unique together in model to avoid repeated accounts name error
                or show the id and the name id:name-->

* Update recurring payments and incomes: Users should be able edit any of their own payments.
    - Users should be able to stop a subscription without deleting the previous payments.
    - Stopping or changing the amount on a recurring payment shouldn't reload the page.
    - User should be able to edit the current subscription amount, influencing next payments
  
* Recurring incomes: Users can add recurring incomes in the current account

* Order by: The incomes and expenses should be able to be ordered in the client without making another request
    - The recurring payment can be ordered by at least their next payment date, their amount, title
    - The incomes and expenses can be ordered by at least amount and date

** Response msg as alert handler

** Forecast: When a user clicks on Forecast, the user should be taken to a view where they see a text based forecast of the balance
    in the selected account given the recurring payments.

** Categories: Allow users categorize the payments in common categories.
    There should be a quick add button for incomes and expenses in every category.

** Logging: Maybe log?

** Graphs: Allow users to view a graph of the balance of the selected month.

