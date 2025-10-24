from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from .database import get_db
from .models import Product
from .schemas import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Product",
    description="Create a new product with name, price, and quantity.",
    responses={
        201: {"description": "Product created"},
        422: {"description": "Validation error"},
    },
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> ProductRead:
    """Create a new product and return the created resource."""
    product = Product(name=payload.name, price=payload.price, quantity=payload.quantity)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[ProductRead],
    summary="List Products",
    description="Return all products.",
)
def list_products(db: Session = Depends(get_db)) -> list[ProductRead]:
    """List all products."""
    items = db.query(Product).all()
    return items


# PUBLIC_INTERFACE
@router.get(
    "/{product_id}",
    response_model=ProductRead,
    summary="Get Product",
    description="Get a product by its ID.",
    responses={404: {"description": "Product not found"}},
)
def get_product(
    product_id: int = Path(..., description="Product ID", ge=1),
    db: Session = Depends(get_db),
) -> ProductRead:
    """Retrieve a product by ID."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


# PUBLIC_INTERFACE
@router.put(
    "/{product_id}",
    response_model=ProductRead,
    summary="Update Product",
    description="Replace a product's fields by ID.",
    responses={404: {"description": "Product not found"}},
)
def update_product(
    product_id: int = Path(..., description="Product ID", ge=1),
    payload: ProductUpdate = ...,
    db: Session = Depends(get_db),
) -> ProductRead:
    """Update an existing product. Only provided fields are updated."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(product, k, v)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# PUBLIC_INTERFACE
@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Product",
    description="Delete a product by its ID.",
    responses={404: {"description": "Product not found"}, 204: {"description": "Deleted"}},
)
def delete_product(
    product_id: int = Path(..., description="Product ID", ge=1),
    db: Session = Depends(get_db),
) -> None:
    """Delete a product by ID."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    db.delete(product)
    db.commit()
    return None
