from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from database import Base


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False)

    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=False)