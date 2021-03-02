Finance
==== 

Applications written in python with the Flask framework as part of the [![CS50 Badge](https://img.shields.io/badge/-CS50-red)](https://cs50.harvard.edu) class problem sets.

Table of content
----
* [General info](#general-info)
* [Setup](#setup)
* [Technologies](#technologies)

### General info

This application is a web app via which the registered users can manage portfolios of stocks. The stock prices are pulled from the https://cloud-sse.iexapis.com site using an API connection with an API key.


### Setup

The application can be run locally or using the [![CS50 Badge](https://img.shields.io/badge/-CS50-red)](https://cs50.harvard.edu) <a href="https://ide.cs50.io">IDE</a> after logging in with your GitHub account. The customer data is stored in SQLite3 database tables. 

To run the program:
 1. You need to have Python installed or using the CS50 IDE
 2. You need to get an API key from: https://iexcloud.io/
 3. You need to store the API key as environment variable: `$ export API_KEY=value`
 4. To run the localhost server use: `$ flask run`

 
### Technologies
 
 Libraries:
 * os
 * datetime
 * CS50
 * flask
 * flask_session
 * tempfile
 * werkzeug.exceptions
 * werkzeug.security
 * [![Python](https://img.shields.io/badge/python%20-%2314354C.svg?&style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
