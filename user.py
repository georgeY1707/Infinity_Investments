from fireo.models import Model
from fireo.fields import TextField, MapField


class User(Model):
    name = TextField()
    password = TextField()
    phone = TextField()
    bills = MapField()