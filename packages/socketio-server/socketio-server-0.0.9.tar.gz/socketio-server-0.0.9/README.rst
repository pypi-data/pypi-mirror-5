Tools to get a socketio server running on a django site quickly

install in settings.py

    INSTALLED_APPS = (
        ...
        'socketio_server',
        ...
    )
    
Then copy the socketio_settings.sample.py into the same dir as manage.py. 
Change the settings to match your preference.

Then run:

    python manage.py socketio 
    
to turn on the socketio server. You'll probably want to create your own
namespace to run your custom socketio logic. Look to gevent_socketio for help.




