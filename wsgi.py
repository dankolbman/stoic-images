import os
from images import create_app 

app = create_app(os.getenv('FLASK_CONFIG') or 'development')

if __name__ == "__main__":
    app.run()
