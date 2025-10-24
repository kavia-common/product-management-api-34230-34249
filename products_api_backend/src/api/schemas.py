from pydantic import BaseModel, Field, conint, confloat

# PUBLIC_INTERFACE
class ProductBase(BaseModel):
    """Base schema for product shared fields."""
    name: str = Field(..., description="Product name", min_length=1, max_length=255)
    price: confloat(ge=0) = Field(..., description="Unit price; must be >= 0")
    quantity: conint(ge=0) = Field(..., description="Available quantity; must be >= 0")

# PUBLIC_INTERFACE
class ProductCreate(ProductBase):
    """Schema for creating a product."""
    pass

# PUBLIC_INTERFACE
class ProductUpdate(BaseModel):
    """Schema for updating a product; all fields optional but validated if provided."""
    name: str | None = Field(None, description="Product name", min_length=1, max_length=255)
    price: confloat(ge=0) | None = Field(None, description="Unit price; must be >= 0")
    quantity: conint(ge=0) | None = Field(None, description="Available quantity; must be >= 0")

# PUBLIC_INTERFACE
class ProductRead(ProductBase):
    """Schema returned for product resources."""
    id: int = Field(..., description="Product identifier")

    class Config:
        from_attributes = True
