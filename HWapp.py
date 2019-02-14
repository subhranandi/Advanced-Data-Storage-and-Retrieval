#  import Flask
import numpy as np
import pandas as pd
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/Hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


# Create an app, being sure to pass __name__
app = Flask(__name__)

#  list all the routes possible
@app.route("/")
def Welcome():
    """List all available API routes"""
    return (
        f"Welcome to Hawaii API Home Page:<br/>"
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f" - List of station numbers and names<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f" - List of last year's precipitation from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f" - List of last year's temperature from all stations<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f" - When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f" - When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.<br/>"
    ) 

@app.route("/api/v1.0/precipitation")
def precipitation():
    """List of last year's precipitation from all stations"""
    #last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date>year_date).\
        order_by (Measurement.date).all()
    #Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    rain_totals = []
    for result in rain:
        row = {}
        row["date"] = rain[0]
        row["prcp"] = rain[1]
        rain_totals.append(row)
    #Return the JSON representation of your dictionary.
    return jsonify(rain_totals)

@app.route("/api/v1.0/Stations")
def Stations():
    """List of station numbers and names"""
    stations_query = session.query(Station.name, Station.station)
    Stations = pd.read_sql(stations_query.statement, stations_query.session.bind)
    return jsonify(Stations.to_dict())
    
@app.route("/api/v1.0/tobs")
def tobs():
 #query for the dates and temperature observations from a year from the last data point.
    #last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temperature = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.date>year_date).\
        order_by (Measurement.date).all()

    temperature_totals = []
    for result in temperature:
        row = {}
        row["date"] = temperature[0]
        row["tobs"] = temperature[1]
        temperature_totals.append(row)
    #Return the JSON representation of your dictionary.
    return jsonify(temperature_totals)

@app.route("/api/v1.0/<start>")
def trip1(start):
    start_date= dt.datetime.strptime(start,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

@app.route("/api/v1.0/<start>/<end>")
def trip2(start,end):

    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year
    trip_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    trip = list(np.ravel(trip_data))
    return jsonify(trip)

if __name__ == "__main__":
    app.run(debug=True)