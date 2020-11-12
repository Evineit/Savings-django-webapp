# Finance
Design a Personal Finance website for managing expenses and subscriptions.

# Understanding
In the distribution code is a Django project called project5 that contains a single app called finance.

First, after making and applying migrations for the project, run python manage.py runserver to start the web server. Open the web server in your browser, and use the “Register” link to register for a new account. The emails you’ll be sending and receiving in this project will be entirely stored in your database (they won’t actually be sent to real email servers), so you’re welcome to choose any email address (e.g. foo@example.com) and password you’d like for this project: credentials need not be valid credentials for actual email addresses.
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Once you’re signed in, you should see yourself taken to the Inbox page of the mail client, though this page is mostly blank (for now). Click the buttons to navigate to your Sent and Archived mailboxes, and notice how those, too, are currently blank. Click the “Compose” button, and you’ll be taken to a form that will let you compose a new email. Each time you click a button, though, you’re not being taken to a new route or making a new web request: instead, this entire application is just a single page, with JavaScript used to control the user interface. Let’s now take a closer look at the distribution code to see how that works.

Take a look at mail/urls.py and notice that the default route loads an index function in views.py. So let’s up views.py and look at the index function. Notice that, as long as the user is signed in, this function renders the mail/inbox.html template. Let’s look at that template, stored at mail/templates/mail/inbox.html. You’ll notice that in the body of the page, the user’s email address is first displayed in an h2 element. After that, the page has a sequence of buttons for navigating between various pages of the app. Below that, notice that this page has two main sections, each defined by a div element. The first (with an id of emails-view) contains the content of an email mailbox (initially empty). The second (with an id of compose-view) contains a form where the user can compose a new email. The buttons along the top, then, need to selectively show and hide these views: the compose button, for example, should hide the emails-view and show the compose-view; the inbox button, meanwhile, should hide the compose-view and show the emails-view.

How do they do that? Notice at the bottom of inbox.html, the JavaScript file mail/inbox.js is included. Open that file, stored at mail/static/mail/inbox.js, and take a look. Notice that when the DOM content of the page has been loaded, we attach event listeners to each of the buttons. When the inbox button is clicked, for example, we call the load_mailbox function with the argument 'inbox'; when the compose button is clicked, meanwhile, we call the compose_email function. What do these functions do? The compose_email function first hides the emails-view (by setting its style.display property to none) and shows the compose-view (by setting its style.display property to block). After that, the function takes all of the form input fields (where the user might type in a recipient email address, subject line, and email body) and sets their value to the empty string '' to clear them out. This means that every time you click the “Compose” button, you should be presented with a blank email form: you can test this by typing values into form, switching the view to the Inbox, and then switching back to the Compose view.

Meanwhile, the load_mailbox function first shows the emails-view and hides the compose-view. The load_mailbox function also takes an argument, which will be the name of the mailbox that the user is trying to view. For this project, you’ll design an email client with three mailboxes: an inbox, a sent mailbox of all sent mail, and an archive of emails that were once in the inbox but have since been archived. The argument to load_mailbox, then, will be one of those three values, and the load_mailbox function displays the name of the selected mailbox by updating the innerHTML of the emails-view (after capitalizing the first character). This is why, when you choose a mailbox name in the browser, you see the name of that mailbox (capitalized) appear in the DOM: the load_mailbox function is updating the emails-view to include the appropriate text.

Of course, this application is incomplete. All of the mailboxes simply show the name of the mailbox (Inbox, Sent, Archive) but don’t actually show any emails yet. There’s no view yet to actually see the contents of any email. And the compose form will let you type in the contents of an email, but the button to send the email doesn’t actually do anything. That’s where you come in!

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
    View active subscriptions

* Categories: Allow users categorize the payments in common categories.
    There should be a quick add button for incomes and expenses in every category.

* Forecast: When a user clicks on Forecast, the user should be taken to a view where they see a text based forecast of the balance
    in the selected account given the recurring payments.

** Movements History

** Graphs: Allow users to view a graph of the balance of the selected month.

** Wallets (accounts)
