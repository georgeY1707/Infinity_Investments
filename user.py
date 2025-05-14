from fireo.models import Model
from fireo.fields import TextField, MapField, NumberField
from fireo.database import db
from google.cloud import firestore
import os


class User(Model):
    class Meta:
        collection_name = "user"

    name = TextField()
    password = TextField()
    phone = TextField(required=True)
    balance_rub = NumberField(default=100000)
    portfolio = MapField(default={})

    def save(self, **kwargs):
        # Initialize Firestore connection if not already present
        if not hasattr(db, 'conn'):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "config/infproject-t-firebase-adminsdk-fbsvc-59f397aa40.json"
            db.conn = firestore.Client()

        if not self.id:
            return super().save(**kwargs)
        else:
            doc_ref = db.conn.collection("user").document(self.id)
            doc_ref.set({
                'name': self.name,
                'password': self.password,
                'phone': self.phone,
                'balance_rub': self.balance_rub,
                'portfolio': self.portfolio
            }, merge=True)
            return self