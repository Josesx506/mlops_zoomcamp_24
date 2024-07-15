import json
from datetime import datetime

# import geopandas as gpd
import networkx as nx
import osmnx as ox
from flask import Flask, jsonify, request
from flask_cors import CORS
from geopandas import GeoDataFrame, points_from_xy, sjoin
from osmnx.distance import nearest_nodes
from pkg.app.load_model import load_trained_model
from pkg.app.utils import load_nyc_graphml
from pkg.model.data import load_shapefile
from shapely import Point, LineString

ox.settings.log_console=True
ox.settings.use_cache=True

def create_app(ml_model,shp_file):
    app = Flask("motor_incident_predictions")
    CORS(app)

    # Preload the osm NYC area road graphs
    graph = load_nyc_graphml()

    def prepare_route_coords(json_resp, graph,optm="length"):
        coords = json_resp["coords"]
        start_lnglat = (float(coords["start-address"]["lng"]),
                        float(coords["start-address"]["lat"]))
        end_lnglat = (float(coords["end-address"]["lng"]),
                        float(coords["end-address"]["lat"]))
        
        # find the nearest node using the preloaded openstreetmap graphs
        orig_node = nearest_nodes(graph, start_lnglat[0],start_lnglat[1])
        dest_node = nearest_nodes(graph, end_lnglat[0], end_lnglat[1])

        route = nx.shortest_path(graph, orig_node, dest_node, weight=optm)
        route_coords = [(graph.nodes[node]["x"], graph.nodes[node]["y"]) for node in route]

        return route_coords

    def prepare_features(osm_route, cur_time, shp):
        points = [Point(pnt) for pnt in osm_route]
        points = GeoDataFrame(geometry=points, crs="4326")
        bourough_ids = sjoin(points, shp, how="left", predicate="within")
        bourough_ids["dowk"] = cur_time.weekday()
        bourough_ids["hour"] = cur_time.hour
        filt_boroughs = bourough_ids.drop_duplicates(subset=["location_id"]).reset_index(drop=True)
        features = filt_boroughs[["location_id", "dowk", "hour"]]
        features = features.astype({"location_id":int, "dowk":int, "hour":int})
        zones = filt_boroughs["zone"].to_list()
        return features, zones

    def predict(features):
        preds = ml_model.predict(features)
        return preds


    @app.route("/predict_collisions", methods=["POST"])
    def get_vehicle_collisions():
        curr_time = datetime.now()
        query = request.get_json()
        drive_route = prepare_route_coords(query, graph=graph)
        features, boroughs = prepare_features(drive_route,curr_time,shp=shp_file)
        pred_incidents = predict(features)

        high_incident_cutoff = 3.5
        route_geojson = LineString(drive_route).__geo_interface__
        filt_boroughs = [bor for bor, incid in zip(boroughs, pred_incidents) if incid > high_incident_cutoff]
        filt_incid = pred_incidents[pred_incidents>high_incident_cutoff].tolist()

        result = {"incidents": filt_incid,
                  "route": route_geojson,
                  "boroughs": filt_boroughs}
        
        return jsonify(result)
    
    return app


# Load the important data
model = load_trained_model("s3")
nyc_taxi_zones = load_shapefile()
app = create_app( model, nyc_taxi_zones)

if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port = 8534)