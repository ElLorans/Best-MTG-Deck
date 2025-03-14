from flask_wtf import FlaskForm
from wtforms import StringField, SelectField


class DeckFormatter(FlaskForm):
    deck_name = StringField("Deck Name")
    player_name = StringField("Player Name")
    event_name = StringField("Event Name")
    player_role = SelectField(
        "Player Role",
        choices=[
            ("Winner", "Winner"),
            ("Finalist", "Finalist"),
            ("Top4", "Top4"),
            ("Top8", "Top8"),
            ("Top16", "Top16"),
        ],
    )
    note_redazione = StringField("Note Redazione")
