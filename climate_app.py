import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    session = Session(engine)

    if not (end_date and end_date.strip()):
        end_date = dt.date.today()

    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


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
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a dict date:prpc from the Measurement object"""
    # Query all dates
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()           

    # Convert list of tuples into normal list
    precipitation = list(np.ravel(results))
    
    return jsonify(dict([(k, v) for k,v in zip (precipitation[::2], precipitation[1::2])]))


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    # Query all Stations
    session = Session(engine)
    results = session.query(Station.station).order_by(Station.station).all()

    # Convert list of tuples into normal list
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Returns a list of temperatures for the previous year based on the last date in Measurement"""
    session = Session(engine)
    year_ago = (dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0],"%Y-%m-%d").date() - dt.timedelta(days=365)).strftime("%Y-%m-%d")

    results = session.query(Measurement.tobs).filter(Measurement.date >= year_ago).order_by(Measurement.date).all()

    tobs = list(np.ravel(results))
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def temp_by_date_start(start):
    
    results = calc_temps(start,"")
    period_temp = list(np.ravel(results))

    return jsonify(period_temp)

@app.route("/api/v1.0/<start>/<end>")
def temp_by_date_range(start,end):
    
    results = calc_temps(start,end)
    period_temp = list(np.ravel(results))

    return jsonify(period_temp)

if __name__ == '__main__':
    app.run(debug=True)
