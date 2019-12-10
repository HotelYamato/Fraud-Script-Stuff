""" 
Justin Moon
1/29/19
last edit: sept 29, 2019

Maintaining this python 2.7v due to python3 SSL cert shenanigans

Differences between this and python3 ver.:
    input -> raw_input
    print() -> print('')
"""

"""
Things to add:
    - check for ip branded reseller
    - prompt user for source type (epayment/tranapi/etc)
"""

"""
FOR THE NETOPS GUYS
if you want to test the script without dumping junk reports in our fraud project, just use my personal git testing project on gitlab by changing the project ID# from 62 to 218
I have to add you guys to the project if you wanna test, or you can create your own personal project and use that ID if you wish, just let me know 
"""
import datetime
import sys
import gitlab
def fraudTemplate():

    #grabs gitlab token from txt file, creates variable for issue creation later as well as handles authentication
    t = open("api_token.txt", "r")
    gl = gitlab.Gitlab('https://gitlab.usaepay.staff/',private_token = t.read())
    gl.auth()
    fraud_project = gl.projects.get(62)
    current_id = gl.user.id
    t.close()

    #first table in fraud report. user enters merch info. Any blank spaces are filled with dashes for uniform formatting
    now = datetime.datetime.now()
    print('')
    print("Merchant Info")
    print('')
    first_row = []
    merch_name = raw_input("Merchant name? ")
    merch_ID = raw_input("MID? ")
    reseller = raw_input("Reseller? ")
    if reseller in open('ip_branded_resellers.txt').read():
        reseller = reseller+" (IP Branded Reseller)"
    date = raw_input("Date? (just press enter key if you want current date) ")
    if date == "today" or not date:
        date = now.strftime("%x")
    fraud_time = raw_input("Time? (just press enter key if you want current time) ")
    if fraud_time == "now" or not fraud_time:
        fraud_time = now.strftime("%I:%M:%S %p")
    first_row.extend((merch_name, merch_ID, reseller, date, fraud_time))
    first_row = [" - " if x == "" else x for x in first_row]
    print('')

    #2nd table in report. captures fraud information
    print("Fraud Patterns (hit enter to skip any non-relevant fields)")
    print('')
    patterns = []
    card_holder = raw_input("Card Holder? ")
    avs_street = raw_input("AVS Street? ")
    card_number = raw_input("Card Number? ")
    amount = raw_input("Dollar Amount? ")
    ip_address = raw_input("IP Address(es?) ")
    description = raw_input("Any nonstandard details? (e.x. 'Testref' in description)? ")
    patterns.extend((card_holder, avs_street, card_number, amount, ip_address, description))
    patterns = [" - " if x == "" else x for x in patterns]
    total_fraud = raw_input("Total amount of fraudulent transactions? ")
    if not total_fraud:
        total_fraud = " - "
    sources = raw_input("Source(s) hit (separate multiple sources with spaces) ")
    source_list = []
    if sources:
        source_list = sources.split()
    else:
        source_list = " - "
    print('')
    
    #alternative capture method for what modules were used
    print("Please enter which fraud modlues were used via their matching numbers, separated by spaces (e.g. 1 2 4 6)")
    print('')
    f = open("FraudModuleList.txt", "r")
    print(f.read())
    print('')
    
    fraud_modules = raw_input("Used modules: ")
    choices = [int(x) for x in fraud_modules.split()]
    #print(choices)
    fraud_modules = [" "]*10
    for x in choices:
        fraud_modules.insert(x-1,"x")
    if "x" in fraud_modules[1]:
        adv_tran_fields=raw_input("What fields were specficially targeted in the Advanced Transaction Filter module, and how were they targeted?: ")
    else:
        adv_tran_fields="n/a"
    #print(fraud_modules)




    print("NetOps Details:")
    summary = raw_input("Please summarize the fraudulent activity: ")
    if summary == "":
        summary = "N/A"
    print('')
    final_resolution = raw_input("Please describe the resolution, if any: ")
    if final_resolution == "":
        final_resolution = "N/A"

    #literal text formatting for gitlab issue creation; injects captured user inputs and places them accordingly
    f = ("Merchant Information",
        '===',
        '| **Merchant Name** | **Merchant ID** | **Reseller** | **Date** | **Time** |',
        '|:-----------------:|:---------------:|:------------:|:--------:|:--------:|',
        "| "+' | '.join(first_row)+" |",
        "",

        'Fraud Information',
        '==================',
        '#### Noticeable Fraud Patterns',
        '| **Card Holder** | **AVS Street** | **Card Number** | **Dollar Amount** | **IP Address(es)** | **Description**',
        '|:---------------:|:--------------:|:---------------:|:-----------------:|:------------------:|:------------------:|',
        "| "+' | '.join(patterns)+" |",
        "",


        "#### Number of Fradulent Transactions: ",
        "| **Fraudulent Transactions**  |  **Source(s) Hit** |",
        "|:-----------------:|:---------------:|",
        "| "+ total_fraud+ " | "+ ' '.join(source_list)+ " |",
        "",

        "* **Fraud Modules Used**  ",
        "* ["+fraud_modules[0]+"] AVS Response",
        "* ["+fraud_modules[1]+"] Advanced Transaction Filter",
        "* Fields targeted by Advaned Transaction Filter: "+adv_tran_fields,
        "* ["+fraud_modules[2]+"] Block by Card Country",
        "* ["+fraud_modules[3]+"] BIN Range Blocker",
        "* ["+fraud_modules[4]+"] Country Blocker",
        "* ["+fraud_modules[5]+"] Multiple Credit Cards",
        "* ["+fraud_modules[6]+"] Transaction Amount",
        "* ["+fraud_modules[7]+"] Captcha",
        '',

        "Netops Details",
        "================",
        "### Summary of Fraud: ",
        ">>>",
        summary,
        ">>>",
        '',
        "### Final Resolution: ",
        ">>>",
        final_resolution,
        ">>>",
        '',
        '',
        "---",
        '',
        "@netops")


    q = '\n'.join(f)
    new_issue = fraud_project.issues.create({'title': 'Fraud Alert: '+merch_name+' ('+merch_ID+') ','description': q, 
        'assigne_id': current_id})


fraudTemplate()
