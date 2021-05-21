# CiboTracker
CiboTracker is a web-based application that allows users to track their calories and macronutrients from the foods they eat. CiboTracker was built using Flask, an infrastructure that allows developers to combine HTML/CSS/JavaScript, Python, and SQL to create clean and coherent web-based applications. All nutritional information used in this application is drawn from the [US Department of Agriculture FoodData Central API](https://fdc.nal.usda.gov/).
#### How to Run CiboTracker
Running CiboTracker requires the user to first download and unzip the `CiboTracker.zip` file. Then, using a terminal window, the user should navigate to the `CiboTracker` directory, and from there execute the following command:

`pip install -r requirements.txt`

This will ensure that the user's computer has all the Python modules necessary to run the application. (_Note that the user may opt to create a virtual environment for these packages._) From here, all that is required is to execute the command,

`export FLASK_APP=application.py`
`export API_KEY=utcqdC7JrXkRkhoJb6YRgwXoazl3Cf7Awr9BdFEx`
`flask run`

which will run the Flask application on a local server. Opening the link that then appears in a web browser (preferably Google Chrome, the browser with which CiboTracker was tested) will allow the user to access the application. To shut down the application, one must press `CTRL+C` in the terminal window. To restart the application after this point, the user must only execute the `./run` command in the `CiboTracker` directory. 