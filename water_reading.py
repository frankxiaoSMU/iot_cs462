from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost/iot_cs462'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)
CORS(app)

class WaterMeterReading(db.Model):
    __tablename__ = 'water_meter_readings'

    household_ID = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.String(50), nullable=True)
    date = db.Column(db.String(50), nullable=False)
    hour = db.Column(db.String(50), nullable=False)
    prev_reading = db.Column(db.Integer, nullable=False)
    current_reading = db.Column(db.Integer, nullable=False)

    def __init__(self, household_ID, datetime, date, hour, prev_reading, current_reading):
        self.household_ID = household_ID
        self.datetime = datetime
        self.date = date
        self.hour = hour
        self.prev_reading = prev_reading
        self.current_reading = current_reading
    
    
    def to_dict(self):
        """
        'to_dict' converts the object into a dictionary,
        in which the keys correspond to database columns
        """
        columns = self.__mapper__.column_attrs.keys()
        result = {}
        for column in columns:
            result[column] = getattr(self, column)
        return result

    def json(self):
        return {"household_ID": self.household_ID, "datetime": self.datetime, "date": self.date, "hour": self.hour, "prev_reading": self.prev_reading, "current_reading": self.current_reading}



@app.route("/get_all_reading")
def get_all_reading():
    data_all = WaterMeterReading.query.all()
    if data_all:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "data": [data.json() for data in data_all]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no data."
        }
    ), 404
    
@app.route("/post_reading", methods=['POST'])
def post_reading():
    data = request.get_json()
    reading = WaterMeterReading(None, **data)

    try:
        db.session.add(reading)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                },
                "message": "An error occurred creating the record."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": reading.json()
        }
    ), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6900, debug=True)
