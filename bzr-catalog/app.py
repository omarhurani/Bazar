from flask_app import app, port
from database import create_database
import routes
import errorhandles

create_database()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)
