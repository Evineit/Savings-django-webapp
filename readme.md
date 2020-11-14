# Finance
Design a Personal Finance website for managing expenses and subscriptions.

# Understanding
In the distribution code is a Django project called project5 that contains a single app called finance.

First, after making and applying migrations for the project, run python manage.py runserver to start the web server. Open the web server in your browser, and use the “Register” link to register for a new account. The emails you’ll be sending and receiving in this project will be entirely stored in your database (they won’t actually be sent to real email servers), so you’re welcome to choose any email address (e.g. foo@example.com) and password you’d like for this project: credentials need not be valid credentials for actual email addresses.
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Once you’re signed in, you should see yourself taken to the Inbox page of the mail client, though this page is mostly blank (for now). Click the buttons to navigate to your Sent and Archived mailboxes, and notice how those, too, are currently blank. Click the “Compose” button, and you’ll be taken to a form that will let you compose a new email. Each time you click a button, though, you’re not being taken to a new route or making a new web request: instead, this entire application is just a single page, with JavaScript used to control the user interface. Let’s now take a closer look at the distribution code to see how that works.

# API
You’ll get to add/delete accounts, add/delete expenses, add/delete incomes, add/delete/update recurring payments and add/delete/update recurring incomes by using this application’s API.

This application supports the following API routes:

GET /accounts/
- Get user accounts

POST /accounts/
- Add new account/wallet

GET /accounts/<str:account>
- Get Account info
- Responds a Json with account info like balance

DELETE /accounts/<str:account>
- Delete Account | Confirmation needed | checkbox

POST /accounts/<str:account>
- Add new expense, income, recurring payment, recurring income.
- Receives JSON with {type, amount, extra info}

------------------------------------------------------------------- 

GET /incomes/<int:id>
- Get the selected item info

GET /expenses/<int:id>
- Get the selected item info

DELETE /incomes/<int:id>
- Delete the selected item info

DELETE /expenses/<int:id>
- Delete the selected item info

---------------------------------------------------------------------
GET /recpayments/<str:account>
- Get all the recurrent expenses of given account

GET /recpayments/<int:id>
- Get the selected item info

GET /recincomes/<int:id>
- Get the selected item info

PUT /recpayments/<int:id>
- Updates the selected item info

PUT /recincomes/<int:id>
- Updates the selected item info

DELETE /recpayments/<int:id>
- Deletes the selected item info

DELETE /recincomes/<int:id>
- Deletes the selected item info



# Specification
Implementation of single-page-app finance client using JavaScript, HTML, and CSS. 
It fulfills the following requirements:

* Quick add: Allow users to add incomes and expenses to the current account quickly.
    Only the amount is needed

* Subscriptions: Allow users to add subscriptions as recurring expenses.
    Users also can add recurring incomes for a better forecast in their budget
    Users should be able to stop a subscription without deleting the previous payments
    View active subscriptions, including the next payment date, a description or title, the type of schedule

* Movements History

* Categories: Allow users categorize the payments in common categories.
    There should be a quick add button for incomes and expenses in every category.
    

** Forecast: When a user clicks on Forecast, the user should be taken to a view where they see a text based forecast of the balance
    in the selected account given the recurring payments.


** Graphs: Allow users to view a graph of the balance of the selected month.

** Wallets (accounts)
