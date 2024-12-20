from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List
from app.db.postgres import db_dependency
from models import Products
from schemas import ProductResponse, ProductItem

router = APIRouter(prefix="/products", tags=["Products"])

# Constants for product descriptions and positions
PRODUCT_INFO = {
    "cooler": {
        "title": "All in One Cooler",
        "description": "An integrated cooling system that combines the CPU cooler and the fan into a single unit.\n"
                      "An AIO cooler is like a built-in air conditioner for your computer.  It cools down your CPU and keeps it from overheating.",
    },

    "fan": {
        "title": "Fan",
        "description": "A device that moves air to dissipate heat generated by components like the CPU and GPU.\n"
                      "A fan is like a tiny airplane engine that blows air to cool down your computer. It helps keep your computer from overheating and keeps it running smoothly.",
    },

    "ram": {
        "title": "RAM",
        "description": "The memory that temporarily stores data for quick access by the CPU.\n"
                      "RAM is like a short-term memory for your computer. It helps your computer quickly find and use the information it needs.",
    },

    "psu": {
        "title": "PSU",
        "description": "The power supply unit that converts AC to DC power, providing the necessary energy to all components.\n"
                      "A PSU is like a transformer that changes the electricity from the wall into the right kind of power for your computer's parts.",
    },

    "cpu": {
        "title": "CPU",
        "description": "The brain of the computer, responsible for processing data and instructions.\n"
                      "A CPU is like the brain of your computer. It processes all the instructions and data to make your computer work.",
    },

    "gpu": {
        "title": "GPU",
        "description": "The graphics processing unit that handles the rendering of images and videos.\n"
                      "A GPU is like a special artist that draws pictures on your computer screen. It makes your computer's display look pretty and smooth.",
    },

    "ssd": {
        "title": "SSD",
        "description": "The component that stores data and programs, such as the hard drive or solid-state drive.\n"
                      "A storage is like a big box where your computer keeps all its files and programs. It helps your computer remember and find everything it needs.",
    },

    "case": {
        "title": "Casing",
        "description": "The protective shell that houses all the other components, providing structural support and ventilation.\n" 
                      "A case is like a big box that holds all your computer's parts. It protects them and helps them work together.",
    },

    "hdd": {
        "title": "HDD",
        "description": "The component that stores data and programs, such as the hard drive or solid-state drive.\n"
                      "A storage is like a big box where your computer keeps all its files and programs. It helps your computer remember and find everything it needs.",
    },


    "motherboard": {
        "title": "Motherboard",
        "description": "The central hub that connects all components, providing power and data pathways.\n"
                      "A motherboard is like the brain of your computer. It connects all the parts together and makes sure they can talk to each other.",
    }
}

@router.get("/", response_model=List[ProductResponse])
async def get_all_products(db: db_dependency):
    try:
        # Get all products
        products_by_category = {}
        
        # Query products with error handling
        try:
            all_products = db.query(Products).order_by(Products.product_id).all()
        except SQLAlchemyError as db_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(db_error)}"
            )
        
        # Check if products exist
        if not all_products:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No products found"
            )
        
        # Group products by category
        for product in all_products:
            if product.category not in products_by_category:
                products_by_category[product.category] = []
            products_by_category[product.category].append(product)
        
        # Create response for each category
        responses = []
        for category, products in products_by_category.items():
            try:
                # Get category info from PRODUCT_INFO, with fallback
                category_info = PRODUCT_INFO.get(category, {
                    "title": category.capitalize(),
                    "description": f"Description for {category}"
                })
                
                product_items = [
                    ProductItem(
                        product_id=product.product_id,
                        product_name=product.product_name,
                        product_category=product.category,
                        product_price=str(product.sales_price),
                        product_stock=product.stock_count,
                        img_url=product.img_url
                    )
                    for product in products
                ]
                
                responses.append(ProductResponse(
                    title=category_info["title"],
                    image=products[0].img_url if products else "",
                    description=category_info["description"],
                    product_list=product_items
                ))
                
            except Exception as category_error:
                # Log the error but continue processing other categories
                print(f"Error processing category {category}: {str(category_error)}")
                continue
        
        # Check if we have any valid responses
        if not responses:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process any product categories"
            )
        
        return responses
        
    except HTTPException as http_error:
        # Re-raise HTTP exceptions
        raise http_error
    
    except Exception as e:
        # Handle any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )