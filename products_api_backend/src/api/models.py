from sqlalchemy import Column, Integer, String, Numeric
from .database import Base

class Product(Base):
    """SQLAlchemy model representing a product entity."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    # Use Numeric for currency-like values to preserve precision
    price = Column(Numeric(10, 2), nullable=False, default=0)
    quantity = Column(Integer, nullable=False, default=0)
