from app import app, db
from app.models import User, Certificate


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False)
