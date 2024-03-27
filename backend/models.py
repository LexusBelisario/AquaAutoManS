from config import db

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    
    def to_json(self):
        return{
            "id": self.id,
            "firstName": self.first_name,
        }