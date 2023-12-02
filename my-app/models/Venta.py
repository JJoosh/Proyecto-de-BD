from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Venta(db.Model):
    __tablename__ = "ventas"

    IdVentas = db.Column(db.Integer, primary_key=True)
    NombreUsuario = db.Column(db.String(255))
    NombreProducto = db.Column(db.String(255))
    fecha_venta = db.Column(db.DateTime)
    items = db.relationship("Item", backref="venta")

    def __repr__(self):
        return f"<Venta {self.IdVentas} {self.NombreUsuario} {self.NombreProducto} {self.fecha_venta}>"
