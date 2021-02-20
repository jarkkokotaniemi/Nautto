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
pip3 install -r requirements.txt
pip3 install .
$env:FLASK_APP="nautto"
```

## Initializing the database

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

## Run the API

Run command:

```powershell
flask run
```
