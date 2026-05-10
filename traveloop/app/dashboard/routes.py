from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Trip, City

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    recent_trips = (
        Trip.query.filter_by(user_id=current_user.id)
        .order_by(Trip.created_at.desc())
        .limit(3)
        .all()
    )
    popular_cities = City.query.order_by(City.popularity_score.desc()).limit(6).all()
    total_trips = Trip.query.filter_by(user_id=current_user.id).count()
    # Total budget across all trips
    from app.models import Budget
    budgets = (
        Budget.query.join(Trip).filter(Trip.user_id == current_user.id).all()
    )
    total_budget = sum(b.total_spent for b in budgets)

    return render_template(
        "dashboard/index.html",
        title="Dashboard",
        recent_trips=recent_trips,
        popular_cities=popular_cities,
        total_trips=total_trips,
        total_budget=total_budget,
    )
