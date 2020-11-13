# Import the Flask application instance and port
from flask_app import app, port

# Import the error handler overrides
import errorhandles

# Import the routes
import routes

# This creates the database file if it does not exist and adds the books to it
from database import create_database
create_database()

# Run Flask application instance
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port)
