from flask import Blueprint, render_template, request
from flask_login import login_required
from app.models import City, Activity

search_bp = Blueprint("search", __name__, url_prefix="/search")


@search_bp.route("/cities")
@login_required
def cities():
    q = request.args.get("q", "").strip()
    region = request.args.get("region", "")
    country = request.args.get("country", "")

    query = City.query
    if q:
        query = query.filter(
            City.name.ilike(f"%{q}%") | City.country.ilike(f"%{q}%")
        )
    if region:
        query = query.filter(City.region.ilike(f"%{region}%"))
    if country:
        query = query.filter(City.country == country)

    cities_list = query.order_by(City.popularity_score.desc()).all()
    regions = db.session.query(City.region).distinct().filter(City.region.isnot(None)).all()
    countries = db.session.query(City.country).distinct().order_by(City.country).all()

    return render_template(
        "search/cities.html",
        title="Explore Cities",
        cities=cities_list,
        regions=[r[0] for r in regions],
        countries=[c[0] for c in countries],
        q=q,
        selected_region=region,
        selected_country=country,
    )


@search_bp.route("/activities")
@login_required
def activities():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "")
    city_id = request.args.get("city_id", type=int)
    max_cost = request.args.get("max_cost", type=float)

    query = Activity.query
    if q:
        query = query.filter(Activity.name.ilike(f"%{q}%"))
    if category:
        query = query.filter(Activity.category == category)
    if city_id:
        query = query.filter(Activity.city_id == city_id)
    if max_cost is not None:
        query = query.filter(Activity.cost <= max_cost)

    activities_list = query.order_by(Activity.rating.desc()).all()
    cities_list = City.query.order_by(City.name).all()
    categories = ["sightseeing", "food", "adventure", "culture", "shopping", "nature", "nightlife"]

    return render_template(
        "search/activities.html",
        title="Explore Activities",
        activities=activities_list,
        cities=cities_list,
        categories=categories,
        q=q,
        selected_category=category,
        selected_city_id=city_id,
        max_cost=max_cost,
    )


# Import db for query
from app.models import db
