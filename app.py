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
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# List all routes that are available.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>" 
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Create our session (link) from Python to the DB
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    print("Query Date: ", query_date)

    # Perform a query to retrieve the data and precipitation scores
    precip = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= query_date, Measurement.prcp != None).\
    order_by(Measurement.date).all()
    session.close()
    # Convert the query results to a dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.
    return jsonify(dict(precip))
    
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # Create our session (link) from Python to the DB
    session.query(Station.station).count()
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                         group_by(Measurement.station).\
                         order_by(func.count(Measurement.station).desc()).all()
    session.close()
    return jsonify(dict(active_stations))


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Create our session (link) from Python to the DB
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temps = session.query(Measurement.tobs).\
    filter(Measurement.date >= query_date, Measurement.station == "USC00519281").\
    order_by(Measurement.tobs).all()
    session.close()
    results_list = []
    
    for t in temps:
        results_dict = {"tobs": t.tobs}
        results_list.append(results_dict) 
    return jsonify(results_list)

# calculate min, max and avg for a given start or start-end range

@app.route("/api/v1.0/<start>")
def calc_temps(start):
    session = Session(engine)
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
   
    temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()
    temps = list(np.ravel(temps))
    temp_dict = {"Min": temps[0], "Max": temps[1], "Avg": temps[2]}
    return jsonify(temp_dict)
    

@app.route("/api/v1.0/<start>/<end>")
def calc(start, end):
    session = Session(engine)
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).all()
    session.close()
    temps = list(np.ravel(temps))
    temp_dict = {"Min": temps[0], "Max": temps[1], "Avg": temps[2]}
    return jsonify(temp_dict)

if __name__ == "__main__":
    app.run(debug = True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    