from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_photo = db.Column(db.String(256), default="default_avatar.png")
    language_pref = db.Column(db.String(10), default="en")
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    trips = db.relationship("Trip", backref="owner", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"


class City(db.Model):
    __tablename__ = "cities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(120), nullable=False)
    region = db.Column(db.String(120))
    cost_index = db.Column(db.Float, default=1.0)  # 1=cheap, 5=expensive
    popularity_score = db.Column(db.Integer, default=50)  # 0-100
    description = db.Column(db.Text)
    image_url = db.Column(db.String(256))
    timezone = db.Column(db.String(60), default="UTC")

    activities = db.relationship("Activity", backref="city", lazy=True, cascade="all, delete-orphan")
    stops = db.relationship("Stop", backref="city", lazy=True)

    @property
    def cost_label(self):
        if self.cost_index is None:
            return "Unknown"
        if self.cost_index <= 1.5:
            return "Budget"
        if self.cost_index <= 3.0:
            return "Moderate"
        if self.cost_index <= 4.0:
            return "Expensive"
        return "Luxury"

    def __repr__(self):
        return f"<City {self.name}, {self.country}>"


class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(60))  # sightseeing, food, adventure, culture, shopping
    cost = db.Column(db.Float, default=0.0)
    duration_hours = db.Column(db.Float, default=2.0)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(256))
    rating = db.Column(db.Float, default=4.0)

    stop_activities = db.relationship("StopActivity", backref="activity", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Activity {self.name}>"


class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    cover_photo = db.Column(db.String(256), default="default_trip.jpg")
    is_public = db.Column(db.Boolean, default=False)
    share_token = db.Column(db.String(64), unique=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    stops = db.relationship("Stop", backref="trip", lazy=True, cascade="all, delete-orphan", order_by="Stop.order_index")
    budget = db.relationship("Budget", backref="trip", uselist=False, cascade="all, delete-orphan")
    packing_items = db.relationship("PackingItem", backref="trip", lazy=True, cascade="all, delete-orphan")
    notes = db.relationship("Note", backref="trip", lazy=True, cascade="all, delete-orphan")

    def generate_share_token(self):
        self.share_token = secrets.token_urlsafe(32)

    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    @property
    def destination_count(self):
        return len(self.stops)

    def __repr__(self):
        return f"<Trip {self.name}>"


class Stop(db.Model):
    __tablename__ = "stops"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey("cities.id"), nullable=False)
    arrival_date = db.Column(db.Date)
    departure_date = db.Column(db.Date)
    order_index = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)

    stop_activities = db.relationship("StopActivity", backref="stop", lazy=True, cascade="all, delete-orphan")

    @property
    def duration_days(self):
        if self.arrival_date and self.departure_date:
            return (self.departure_date - self.arrival_date).days + 1
        return 1

    def __repr__(self):
        return f"<Stop city_id={self.city_id} trip_id={self.trip_id}>"


class StopActivity(db.Model):
    __tablename__ = "stop_activities"

    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.Integer, db.ForeignKey("stops.id"), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"), nullable=False)
    scheduled_time = db.Column(db.String(20))  # e.g. "09:00"
    custom_notes = db.Column(db.Text)
    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False, unique=True)
    transport_budget = db.Column(db.Float, default=0.0)
    stay_budget = db.Column(db.Float, default=0.0)
    activities_budget = db.Column(db.Float, default=0.0)
    meals_budget = db.Column(db.Float, default=0.0)
    misc_budget = db.Column(db.Float, default=0.0)
    total_limit = db.Column(db.Float, default=0.0)

    @property
    def total_spent(self):
        return (
            self.transport_budget
            + self.stay_budget
            + self.activities_budget
            + self.meals_budget
            + self.misc_budget
        )

    @property
    def remaining(self):
        if self.total_limit > 0:
            return self.total_limit - self.total_spent
        return 0

    @property
    def over_budget(self):
        return self.total_limit > 0 and self.total_spent > self.total_limit


class PackingItem(db.Model):
    __tablename__ = "packing_items"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(60), default="general")  # clothing, documents, electronics, toiletries, general
    is_packed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    stop_id = db.Column(db.Integer, db.ForeignKey("stops.id"), nullable=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
