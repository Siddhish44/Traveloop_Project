from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, BooleanField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class TripForm(FlaskForm):
    name = StringField("Trip Name", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=1000)])
    start_date = DateField("Start Date", validators=[Optional()])
    end_date = DateField("End Date", validators=[Optional()])
    cover_photo = FileField("Cover Photo", validators=[FileAllowed(["jpg", "jpeg", "png", "gif", "webp"])])
    is_public = BooleanField("Make this trip public")
    submit = SubmitField("Save Trip")


class StopForm(FlaskForm):
    city_id = SelectField("City", coerce=int, validators=[DataRequired()])
    arrival_date = DateField("Arrival Date", validators=[Optional()])
    departure_date = DateField("Departure Date", validators=[Optional()])
    submit = SubmitField("Add Stop")


class BudgetForm(FlaskForm):
    transport_budget = FloatField("Transport ($)", validators=[Optional()], default=0.0)
    stay_budget = FloatField("Accommodation ($)", validators=[Optional()], default=0.0)
    activities_budget = FloatField("Activities ($)", validators=[Optional()], default=0.0)
    meals_budget = FloatField("Meals ($)", validators=[Optional()], default=0.0)
    misc_budget = FloatField("Miscellaneous ($)", validators=[Optional()], default=0.0)
    total_limit = FloatField("Total Budget Limit ($)", validators=[Optional()], default=0.0)
    submit = SubmitField("Save Budget")


class PackingItemForm(FlaskForm):
    name = StringField("Item Name", validators=[DataRequired(), Length(max=200)])
    category = SelectField(
        "Category",
        choices=[
            ("clothing", "Clothing"),
            ("documents", "Documents"),
            ("electronics", "Electronics"),
            ("toiletries", "Toiletries"),
            ("general", "General"),
        ],
    )
    submit = SubmitField("Add Item")


class NoteForm(FlaskForm):
    title = StringField("Title", validators=[Optional(), Length(max=200)])
    content = TextAreaField("Note", validators=[DataRequired()])
    stop_id = SelectField("Related Stop (optional)", coerce=int, validators=[Optional()])
    submit = SubmitField("Save Note")
