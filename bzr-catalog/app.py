from flask_app import app
from database import create_database
import routes

create_database()

if __name__ == '__main__':
    app.run(debug=True)
