from app import app

# This is the variable that Gunicorn looks for
application = app

if __name__ == "__main__":
    app.run()
