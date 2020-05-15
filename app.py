import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )


@app.route("/api/v1.0/precipitation")
def names():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of date and prcp"""
    # Query all station
    results = session.query(measurement.date, measurement.prcp).all()

    session.close()
    # Create a dictionary from the row data and append to a list of all_passengers
    all_prcp = []
    for date, prcp in results:
         prcp_dict = {}
         prcp_dict["date"] = date
         prcp_dict["prcp"] = prcp
         all_prcp.append(prcp_dict)
    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
     session = Session(engine)

     """Return a list of stations"""
     # Query all stations
     results = session.query(station.name).all()

     session.close()

     # Convert list of tuples into normal list
     all_stations = list(np.ravel(results))
     return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temp():
    # Create our session (link) from Python to the DB
     session = Session(engine)

     """Find the most active station, then list temp"""
     #calc last year
     dummy = session.query(measurement.date).order_by(measurement.date.desc()).first()
     format_str = '%Y-%m-%d' # The format
     datetime_obj = dt.datetime.strptime(dummy[0], format_str)
     query_date = datetime_obj.date() - dt.timedelta(days=365) 

     #most active station
     activest = session.query(measurement.station,func.count(measurement.tobs)).\
group_by(measurement.station).order_by(func.count(measurement.tobs).desc()).first()
     activest = str(activest[0])

     # Query station temps
     results = session.query(measurement.date,measurement.tobs).filter(measurement.date > query_date, measurement.station == activest).order_by(measurement.date).all()
     session.close()

     # Create a dictionary from the row data and append to a list of all_tobs
     all_tobs = []
     for date, temp in results:
         temp_dict = {}
         temp_dict["date"] = date
         temp_dict["temp"] = temp
         all_tobs.append(temp_dict)

     return jsonify(all_tobs)

@app.route("/api/v1.0/start/<start>", methods=['GET'])
def start_date_temp(start):
    
     """Return list of the min temp, avg temp, and the max temp for a given start date that matches
       the path variable supplied by the user, or a 404 if not."""
     # Create our session (link) from Python to the DB
     session = Session(engine)

     # Query station temps
     temps = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date >= start).first()
     count = session.query(func.count(measurement.tobs)).filter(measurement.date >= start).first()
     
     session.close()

     if count[0] > 0:
        return jsonify(temps)
     else: 
        return jsonify({"error": f"Data for {start} not found, insure date is contained in the data set and the format is yyyy/mm/dd."}), 404

@app.route("/api/v1.0/start/end/<start>/<end>", methods=['GET'])
def start_end_date_temp(start, end):
    
     """Return list of the min temp, avg temp, and the max temp for a given start date that matches
       the path variable supplied by the user, or a 404 if not."""
     # Create our session (link) from Python to the DB
     session = Session(engine)

     # Query station temps
     temps = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date >= start, measurement.date <= end).first()
     count = session.query(func.count(measurement.tobs)).filter(measurement.date >= start, measurement.date <= end).first()
     
     session.close()

     if count[0] > 0:
        return jsonify(temps)
     else: 
        return jsonify({"error": f"Data for {start} and {end} not found, insure date is contained in the data set and the format is yyyy/mm/dd."}), 404    

if __name__ == '__main__':
    app.run(debug=True)
