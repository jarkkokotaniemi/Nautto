# PWP SPRING 2021

## Nautto

### Group information

* Student 1. Jarkko Kotaniemi, jarkko.kotaniemi@gmail.com
* Student 2. Vili Tiinanen, vili.tiinanen@live.fi

## Installation

To run the application you should run the following commands (on PowerShell):

```powersehll
git clone https://github.com/jarkkokotaniemi/Nautto
cd ./nautto
pip install -r requirements.txt
pip install .
$env:FLASK_APP="nautto"
```
On cmd:

```cmd
git clone https://github.com/jarkkokotaniemi/Nautto
cd .\nautto
pip install -r requirements.txt
pip install .
set FLASK_APP=nautto
```

## Initialize the database

Before starting the application, you must initialize the database. This can be done by running the following command:

```powershell
flask db-init
```

Then, you can populate the database with dummy data by running:

```powershell
flask db-populate
```

To drop all current tables use:

```powershell
flask db-drop
```

## Test the database

The database tests can be ran with the following command:

```powershell
python3 -m pytest tests 
# OR with coverage
python3 -m pytest tests --cov=nautto
```

## Run the API

Run command:

```powershell
flask run
```

## Database dump

Database dump is in the dump folder
