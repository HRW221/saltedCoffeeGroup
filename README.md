# Guardians of the Garden
https://django-server-production-1cc2.up.railway.app/
### Group Saltedcoffee
___

Guardians of the Garden is a competitive plant collecting game that encourages the user to explore and learn about their local flora.
* Take photos of real plants to collect cards and earn score
* Compete with your friends on public and private leaderboards
* Learn about many different plants in the Learn
* Complete packs of cards to earn extra points
* Modular, can be easily modified to work with other universities' campuses

<img src="./img/home.png" alt="Size Limit CLI">

## How it Works
We use the Plant.id API to recognise plants from images.

## Building
When running locally this project uses SQLite.
This project uses PostgreSQL in deployment.

### Running Locally
Clone the project from this repository. 
Ensure you are using Python 3.10 or higher. First install all the required dependencies by navigating to the folder you cloned this project into. Then execute:
``` commandline
pip install -r requirements.txt
```
Navigate to 'parent folder\guardiansOfTheGarden'. Finally, execute the following command:
``` commandline
python manage.py runserver
```
You should now be running the app locally on your machine. manage.py should give you a link to the site, but if it does not, the default URL is ```http://localhost:8000/```

The project should run in debug mode by default. To change this, navigate to the root folder of the project, and open ```variables.env```.
Replace the line ```DEBUG=True``` with ```DEBUG=False```.

### Deploying
We used Railway to deploy this project. To deploy using Railway, create a free account using your GitHub account. Then Create a new project on Railway using the **Django template**. This will create two services, a Django service, and a PostgreSQL service. Open the Django project's settings and change the **Source Repo** setting to point to your GitHub clone. Change the **Custom Start Command** option to ```gunicorn guardiansOfTheGarden.wsgi```. In the **Variables** tab, add a variable called DATABASE_URL and copy the PostgreSQL URL into this field. Finally, in your project's **variables.env** file, replace the DATABASE_URL field with the URL to the PostgreSQL URL and run ```python manage.py migrate```.

## Configuration
You can modify the app's behavior using the ```variables.env``` file.
For example, you can edit the location of the uni campus to change which institution's campus the app uses.