from fastapi import FastAPI
import uvicorn
from models import UserCreate
app = FastAPI()


sample_product_1 = {
    "product_id": 123,
    "name": "Smartphone",
    "category": "Electronics",
    "price": 599.99
}

sample_product_2 = {
    "product_id": 456,
    "name": "Phone Case",
    "category": "Accessories",
    "price": 19.99
}

sample_product_3 = {
    "product_id": 789,
    "name": "Iphone",
    "category": "Electronics",
    "price": 1299.99
}

sample_product_4 = {
    "product_id": 101,
    "name": "Headphones",
    "category": "Accessories",
    "price": 99.99
}

sample_product_5 = {
    "product_id": 202,
    "name": "Smartwatch",
    "category": "Electronics",
    "price": 299.99
}

sample_products = [sample_product_1, sample_product_2, sample_product_3, sample_product_4, sample_product_5]



@app.get("/products/search")
async def create_user(
    keyword: str,
    category: str = None,
    limit:int = 10
):
    resp =[]
    for product in sample_products:
        if keyword in  product["name"]:
            if category is not None:
                if product["category"] == category:
                    resp.append(product)
            else:
                pass
        if len(resp)==limit:break
    return resp


@app.get("/product/{product_id}")
async def create_user(product_id:int):
    found = False
    for product in sample_products:        
        if product["product_id"] == product_id:
            found = True
            return product
    if not found:
        return {"message":f"product with product_id {product_id} not found"}



if __name__  == "__main__":
    
    uvicorn.run("main:app", reload=True, port=8000, host="127.0.0.1")