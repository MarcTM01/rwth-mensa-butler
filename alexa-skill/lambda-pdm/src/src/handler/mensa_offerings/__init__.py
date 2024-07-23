"""This package defines logic for answering users questions about the mensa menus.

The request passes through multiple phases including:
1. Checking that all required data has been specified by the user.
    Else, reprompt the user
2. Retrieve all the data from the database
3. Formulate a response to the user.
"""
