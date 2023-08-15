# Recipe Forum

Recipe Forum is an app built by Andi Alifsyah as part of a test at Artivo.id in 2023. The app is deployed and can be accessed at https://artivorecipe-70cb3b9ac4bf.herokuapp.com/.

## Features

- Authentication
- Like and comment on recipes
- Add recipes

## Built With

- Flask
- JWT for authentication
- SQLAlchemy for database ORM
- Flask-Migrate for database migration

## Project Directory

```bash
RecipeForum/
├── instance 
│ └── database.sqlite 
├── migrations 
│ ├── … 
├── templates 
│ ├── … 
├── Procfile 
├── app.py 
└── requirements.txt
```

- `instance` contains the SQLite database
- `migrations` contains the migration files
- `templates` contains the frontend files
- `Procfile` contains the setup for deployment on Heroku
- `app.py` contains the main logic, routes, and views of the app
- `requirements.txt` contains the required packages

## Installation

1. Clone the repository
2. Install the required packages by running `pip install -r requirements.txt`
3. Set up the database by running `flask db init`, `flask db migrate`, and `flask db upgrade`
4. Run the app with `flask run`
