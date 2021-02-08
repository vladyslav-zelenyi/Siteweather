This is a test site that receives and filters weather data by city name from [openweathermap.org](http://openweathermap.org/) and stores it in a database.
#
#### Compatibility
* Python 3.8.5
* Django 3.1.1
* SQLite / PostgreSQL as database backends
#
#### Superuser login credentials
* Login - admin
* Password - admin
#
#### Celery configuration
-A task worker -l info -B -Q celery,base,test_queue
