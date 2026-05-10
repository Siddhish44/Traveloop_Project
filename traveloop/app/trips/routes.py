import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models import db, Trip, Stop, City, Activity, StopActivity, Budget, PackingItem, Note
from .forms import TripForm, StopForm, BudgetForm, PackingItemForm, NoteForm

trips_bp = Blueprint("trips", __name__, url_prefix="/trips")


def save_upload(file_field):
    if file_field and file_field.filename:
        filename = secure_filename(file_field.filename)
        unique_name = f"{os.urandom(8).hex()}_{filename}"
        file_field.save(os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name))
        return unique_name
    return None


# My Trips
@trips_bp.route("/")
@login_required
def list_trips():
    trips = (
        Trip.query.filter_by(user_id=current_user.id)
        .order_by(Trip.created_at.desc())
        .all()
    )
    return render_template("trips/list.html", title="My Trips", trips=trips)


# Create Trip
@trips_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_trip():
    form = TripForm()
    if form.validate_on_submit():
        trip = Trip(
            user_id=current_user.id,
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            is_public=form.is_public.data,
        )
        trip.generate_share_token()
        photo = save_upload(form.cover_photo.data)
        if photo:
            trip.cover_photo = photo
        db.session.add(trip)
        db.session.commit()
        budget = Budget(trip_id=trip.id)
        db.session.add(budget)
        db.session.commit()
        flash(f'Trip "{trip.name}" created! Start building your itinerary.', "success")
        return redirect(url_for("trips.builder", trip_id=trip.id))
    return render_template("trips/create.html", title="Create Trip", form=form)


# Edit Trip
@trips_bp.route("/<int:trip_id>/edit", methods=["GET", "POST"])
@login_required
def edit_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    form = TripForm(obj=trip)
    if form.validate_on_submit():
        trip.name = form.name.data
        trip.description = form.description.data
        trip.start_date = form.start_date.data
        trip.end_date = form.end_date.data
        trip.is_public = form.is_public.data
        photo = save_upload(form.cover_photo.data)
        if photo:
            trip.cover_photo = photo
        db.session.commit()
        flash("Trip updated successfully!", "success")
        return redirect(url_for("trips.list_trips"))
    return render_template("trips/create.html", title="Edit Trip", form=form, trip=trip)


# Delete Trip
@trips_bp.route("/<int:trip_id>/delete", methods=["POST"])
@login_required
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    db.session.delete(trip)
    db.session.commit()
    flash("Trip deleted.", "info")
    return redirect(url_for("trips.list_trips"))


# Itinerary Builder
@trips_bp.route("/<int:trip_id>/builder", methods=["GET", "POST"])
@login_required
def builder(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    stop_form = StopForm()
    cities = City.query.order_by(City.name).all()
    stop_form.city_id.choices = [(c.id, f"{c.name}, {c.country}") for c in cities]

    if stop_form.validate_on_submit():
        max_order = db.session.query(db.func.max(Stop.order_index)).filter_by(trip_id=trip_id).scalar() or 0
        stop = Stop(
            trip_id=trip_id,
            city_id=stop_form.city_id.data,
            arrival_date=stop_form.arrival_date.data,
            departure_date=stop_form.departure_date.data,
            order_index=max_order + 1,
        )
        db.session.add(stop)
        db.session.commit()
        flash("Stop added!", "success")
        return redirect(url_for("trips.builder", trip_id=trip_id))

    stops = Stop.query.filter_by(trip_id=trip_id).order_by(Stop.order_index).all()
    return render_template(
        "trips/itinerary_builder.html",
        title="Itinerary Builder",
        trip=trip,
        stops=stops,
        stop_form=stop_form,
    )


# Remove Stop
@trips_bp.route("/<int:trip_id>/stops/<int:stop_id>/delete", methods=["POST"])
@login_required
def delete_stop(trip_id, stop_id):
    stop = Stop.query.get_or_404(stop_id)
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    db.session.delete(stop)
    db.session.commit()
    flash("Stop removed.", "info")
    return redirect(url_for("trips.builder", trip_id=trip_id))


# Add Activity to Stop
@trips_bp.route("/<int:trip_id>/stops/<int:stop_id>/activities/add", methods=["POST"])
@login_required
def add_activity_to_stop(trip_id, stop_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    activity_id = request.form.get("activity_id", type=int)
    scheduled_time = request.form.get("scheduled_time", "")
    if activity_id:
        existing = StopActivity.query.filter_by(stop_id=stop_id, activity_id=activity_id).first()
        if not existing:
            sa = StopActivity(stop_id=stop_id, activity_id=activity_id, scheduled_time=scheduled_time)
            db.session.add(sa)
            db.session.commit()
            flash("Activity added to your itinerary!", "success")
        else:
            flash("Activity already in this stop.", "warning")
    return redirect(url_for("trips.builder", trip_id=trip_id))


# Remove Activity from Stop
@trips_bp.route("/<int:trip_id>/stops/<int:stop_id>/activities/<int:sa_id>/remove", methods=["POST"])
@login_required
def remove_activity_from_stop(trip_id, stop_id, sa_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    sa = StopActivity.query.get_or_404(sa_id)
    db.session.delete(sa)
    db.session.commit()
    flash("Activity removed.", "info")
    return redirect(url_for("trips.builder", trip_id=trip_id))


# Itinerary View
@trips_bp.route("/<int:trip_id>/view")
@login_required
def view(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    stops = Stop.query.filter_by(trip_id=trip_id).order_by(Stop.order_index).all()
    return render_template("trips/itinerary_view.html", title=trip.name, trip=trip, stops=stops)


# Budget
@trips_bp.route("/<int:trip_id>/budget", methods=["GET", "POST"])
@login_required
def budget(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    budget_obj = trip.budget
    if not budget_obj:
        budget_obj = Budget(trip_id=trip_id)
        db.session.add(budget_obj)
        db.session.commit()
    form = BudgetForm(obj=budget_obj)
    if form.validate_on_submit():
        budget_obj.transport_budget = form.transport_budget.data or 0.0
        budget_obj.stay_budget = form.stay_budget.data or 0.0
        budget_obj.activities_budget = form.activities_budget.data or 0.0
        budget_obj.meals_budget = form.meals_budget.data or 0.0
        budget_obj.misc_budget = form.misc_budget.data or 0.0
        budget_obj.total_limit = form.total_limit.data or 0.0
        db.session.commit()
        flash("Budget updated!", "success")
        return redirect(url_for("trips.budget", trip_id=trip_id))
    return render_template(
        "trips/budget.html",
        title="Trip Budget",
        trip=trip,
        budget=budget_obj,
        form=form,
    )


# Packing Checklist
@trips_bp.route("/<int:trip_id>/packing", methods=["GET", "POST"])
@login_required
def packing(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    form = PackingItemForm()
    if form.validate_on_submit():
        item = PackingItem(
            trip_id=trip_id,
            name=form.name.data,
            category=form.category.data,
        )
        db.session.add(item)
        db.session.commit()
        flash("Item added to checklist!", "success")
        return redirect(url_for("trips.packing", trip_id=trip_id))
    items = PackingItem.query.filter_by(trip_id=trip_id).order_by(PackingItem.category, PackingItem.name).all()
    categories = {}
    for item in items:
        categories.setdefault(item.category, []).append(item)
    return render_template(
        "trips/packing.html",
        title="Packing Checklist",
        trip=trip,
        categories=categories,
        form=form,
    )


@trips_bp.route("/<int:trip_id>/packing/<int:item_id>/toggle", methods=["POST"])
@login_required
def toggle_packed(trip_id, item_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    item = PackingItem.query.get_or_404(item_id)
    item.is_packed = not item.is_packed
    db.session.commit()
    return redirect(url_for("trips.packing", trip_id=trip_id))


@trips_bp.route("/<int:trip_id>/packing/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_packing_item(trip_id, item_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    item = PackingItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("trips.packing", trip_id=trip_id))


# Notes / Journal
@trips_bp.route("/<int:trip_id>/notes", methods=["GET", "POST"])
@login_required
def notes(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    form = NoteForm()
    stops = Stop.query.filter_by(trip_id=trip_id).order_by(Stop.order_index).all()
    form.stop_id.choices = [(0, "General (no stop)")] + [
        (s.id, s.city.name) for s in stops
    ]
    if form.validate_on_submit():
        stop_id_val = form.stop_id.data
        note = Note(
            trip_id=trip_id,
            stop_id=stop_id_val if stop_id_val and stop_id_val != 0 else None,
            title=form.title.data,
            content=form.content.data,
        )
        db.session.add(note)
        db.session.commit()
        flash("Note saved!", "success")
        return redirect(url_for("trips.notes", trip_id=trip_id))
    all_notes = Note.query.filter_by(trip_id=trip_id).order_by(Note.created_at.desc()).all()
    return render_template(
        "trips/notes.html",
        title="Trip Notes",
        trip=trip,
        notes=all_notes,
        form=form,
    )


@trips_bp.route("/<int:trip_id>/notes/<int:note_id>/delete", methods=["POST"])
@login_required
def delete_note(trip_id, note_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    flash("Note deleted.", "info")
    return redirect(url_for("trips.notes", trip_id=trip_id))


# Share / Public View
@trips_bp.route("/share/<token>")
def share(token):
    trip = Trip.query.filter_by(share_token=token, is_public=True).first_or_404()
    stops = Stop.query.filter_by(trip_id=trip.id).order_by(Stop.order_index).all()
    return render_template("trips/share.html", title=f"{trip.name} - Traveloop", trip=trip, stops=stops)


# Toggle Public
@trips_bp.route("/<int:trip_id>/toggle-public", methods=["POST"])
@login_required
def toggle_public(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    trip.is_public = not trip.is_public
    if not trip.share_token:
        trip.generate_share_token()
    db.session.commit()
    status = "public" if trip.is_public else "private"
    flash(f"Trip is now {status}.", "success")
    return redirect(url_for("trips.view", trip_id=trip_id))


# Reorder Stops (AJAX)
@trips_bp.route("/<int:trip_id>/stops/reorder", methods=["POST"])
@login_required
def reorder_stops(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if trip.user_id != current_user.id:
        abort(403)
    data = request.get_json()
    order = data.get("order", [])
    for idx, stop_id in enumerate(order):
        stop = Stop.query.get(stop_id)
        if stop and stop.trip_id == trip_id:
            stop.order_index = idx
    db.session.commit()
    return jsonify({"status": "ok"})
