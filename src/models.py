from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Metrics(db.Model):
    __tablename__ = 'metrics'

    id = db.Column(db.String)
    cpu_usage = db.Column(db.ARRAY(db.Integer))
    memory_usage = db.Column(db.ARRAY(db.Integer))
    memory_percent = db.Column(db.Numeric(5,2))
    timestamp = db.Column(db.TIMESTAMP, nullable=False,  primary_key=True)

    def __init__(self, id, cpu_usage, memory_usage, memory_percent, timestamp):
        self.id = id
        self.cpu_usage = cpu_usage
        self.memory_usage = memory_usage
        self.memory_percent = memory_percent
        self.timestamp = timestamp