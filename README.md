# Stack Overflow (clone) - built with Django 3.2

Project: https://binnybit.pythonanywhere.com/

Todo (Non-Windows)
```
mkdir [folder name]
cd [folder name]
python -m venv venv
venv\scripts\activate
git clone https://github.com/BenLHedgepeth/django_stackoverflow
cd django_stackoverflow
pip install -r requirements.txt
touch .env
echo SECRET_KEY='kt^e2&(7s7p3swjj2#9^szchrsx%xt%rm1pm4t!v-^n$3+^9is' >> .env
echo DEBUG='True' >> .env
python manage.py migrate
python manage.py runserver
```

Todo (Windows-Powershell)
```
mkdir [folder name]
cd [folder name]
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope Process
venv\Scripts\activate.ps1
git clone https://github.com/BenLHedgepeth/django_stackoverflow
pip install -r requirements.txt
New-Item .env (*See note below*)
echo SECRET_KEY='kt^e2&(7s7p3swjj2#9^szchrsx%xt%rm1pm4t!v-^n$3+^9is' >> .env
echo DEBUG='True' >> .env
python manage.py migrate
python manage.py runserver
```
*Note: BOM must removed from the `.env` file. Otherwise a `UnicodeDecodeError`
will be raised when executing `python manage.py migrate`

### Django features used
- Models
- ContentType
- Class Based Views
- Forms/ModelForms
- Templates
- Inclusion Tag
- Pagination

### Project features

- All Users
  - read questions posted
  - perform search queries
  - view user profiles


- Registered Users (request.user.is_authenticated == True)
  - create/edit/delete their own posts
   - clicking "delete" on an authored post DOES NOT remove the record from the database;
     rather it hides the post from public view
  - create/edit answers to posted questions
  - create/delete a vote on posts other than those authored by the user
