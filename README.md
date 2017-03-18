Bitcoin Fee Alert Transaction
===================

Requirements
----------

 - Python 2.6+


Description
-------------
This script check the bitcoin transaction fees using bitcoinfees.21.co APIs.
when the price is under the specified fee, it will send you an email.

How to configure
-------------

Open the file with editor (ex. notepad++)
Find and change the line below
```
#### CHANGE VALUE BELOW ####
# Field "To" in the email header
email_to = "<TARGET EMAIL>"

# SMTP Host
email_host = "<EMAIL HOST>"
email_port = 25

# Username and password to login
email_user = "<EMAIL USERNAME TO LOGIN>"
email_pwd = "<EMAIL PASSWORD TO LOGIN>"

# Fee target (in satoshi)
fee_target = 250

# Period to check the fee (in seconds)
check_period = 300
#### DON'T TOUCH BELOW ####
```

Donate (btc): 3JPRaDFPjjdR1Y7gBrdkfutbJ8g5X9GQik
