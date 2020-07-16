# import everything we used in the jupyter notebook during exploration
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# import the flask modules we'll need.
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
tables = Base.classes.keys()
measurementClass = Base.classes.measurement
stationClass = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt<br/>"
        f"NOTE: Start and end dates must follow the format YYYY-MM-DD."
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation values"""
    # Query all precipitation by date
    results = session.query(measurementClass.date, measurementClass.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, precipitation in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["precipitation"] = precipitation
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query distinct stations
    results = session.query(func.distinct(measurementClass.station)).all()

    session.close()

    # This is already a list, so we don't need to do much.
    all_stations = results

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of dates and temps for the most active station"""
    # Query
    endDate = dt.datetime.strptime(session.query(measurementClass.date).order_by(measurementClass.date.desc()).first()[0], '%Y-%m-%d')
    queryDate = dt.datetime.strftime((endDate - dt.timedelta(365)), '%Y-%m-%d')

    results = session.query(measurementClass.date, measurementClass.tobs).\
    filter(measurementClass.date >= queryDate).\
    filter(measurementClass.station == "USC00519281").\
    order_by(measurementClass.date).all()

    session.close()

    # Convert list of tuples into normal list
    all_tobs = list(np.ravel(results))

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start_date>")
def tobs_2(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query
    results = session.query(func.min(measurementClass.tobs), func.avg(measurementClass.tobs), func.max(measurementClass.tobs)).\
    filter(measurementClass.date >= start_date).\
    filter(measurementClass.station == "USC00519281").all()

    session.close()
    tobs_summary = {}
    tobs_summary["TMIN"] = results[0][0]
    tobs_summary["TAVG"] = results[0][1]
    tobs_summary["TMAX"] = results[0][2]

    return jsonify(tobs_summary)

@app.route("/api/v1.0/<start_date>/<end_date>")
def tobs_3(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query

    results = session.query(func.min(measurementClass.tobs), func.avg(measurementClass.tobs), func.max(measurementClass.tobs)).\
    filter(measurementClass.date >= start_date).\
    filter(measurementClass.date <= end_date).\
    filter(measurementClass.station == "USC00519281").all()

    session.close()
    tobs_summary = {}
    tobs_summary["TMIN"] = results[0][0]
    tobs_summary["TAVG"] = results[0][1]
    tobs_summary["TMAX"] = results[0][2]

    return jsonify(tobs_summary)

if __name__ == '__main__':
    app.run(debug=True)
