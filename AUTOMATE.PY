import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# List of search queries
search_queries = [
    "Butter Chicken Momos",
    "Corn Momos",
    "Desi Chicken Momos",
    "Chicken Cheese Momos",
    "Chicken Momos",
    "Chicken Schezwan Momos",
    "Chicken Tikka Momos",
    "Mix Veg Momos",
    "Mushroom Momos",
    "Paneer Momos",
    "Paneer Tikka Momos",
    "Veg Schezwan Momos",
    "Chicken Peri Peri Momos",
    "Chicken Kurkure Momos",
    "Mix Veg Kurkure Momos",
    "Corn & Cheese Momos",
    "Prawn Momos",
    
    # French Fries Variants
    "French Fries",
    "Peri Peri French Fries",
    "Chicken French Fries",
    "Crispy French Fries",
    "Salty French Fries",
    "Spicy French Fries",
    "Baked French Fries",
    "Pepper French Fries",
    "Peri French Fries",
    "Paneer French Fries",
    
    # Aloo Tikki Burger Variants
    "All Time Favorite Aloo Tikki Burger",
    "K-Pop Classic Aloo Tikki Burger",
    "Big Aloo Tikki Burger",
    "Aloo Tikki Cheese Burger",
    "Crispy Aloo Tikki Burger",
    "K Pop Honey Sriacha Aloo Tikki Burger",
    
    # Veg Burger Variants
    "Veg Burger",
    "Crispy Veg Burger",
    "Classic Veg Burger",
    "Mini Veg Burger",
    "Healthy Veg Burger",
    "Karachi Veg Burger",
    "Veg Barbeque Burger",
    "Veg Bun Burger",
    
    # Chicken Burger Variants
    "Chicken Burger",
    "Crispy Chicken Burger",
    "Homestyle Chicken Burger",
    "Fiery Chicken Burger",
    "KFC Chicken Burger",
    "Classic Chicken Burger",
    "Korean Chicken Burger",
    "Grilled Chicken Burger",
    "Crunchy Chicken Burger",
    
    # Spicy Chicken Burger Variants
    "Spicy Chicken Burger",
    "Chicken Spicy Burger",
    "Chicken Patty Spicy Burger",
    "Spicy Chicken Cheese Burger",
    "Mexicano Spicy Chicken Burger",
    "Hot and Spicy Chicken Burger",
    "Spicy Chicken Feast Burger",
    "Spicy Chicken Fillet Burger",
    "Spicy Chicken Steak Burger",
    
    # Lebanese Falafel Wraps
    "Lebanese Falafel Shawarma Roll",
    "Lebanese Falafel Shawarma Wrap",
    "Lebanese Falafel Veggie Wrap",
    "Lebanese Veggie Lebanese Wholewheat Wrap",
    
    # Kebab Variants
    "Hara Bara Kebab",
    "Veg Harabhara Kebab",
    
    # Chicken Tikka Variants
    "Chicken Tikka",
    "Chicken Tikka Masala",
    "Chicken Tikka Roll",
    "Classic Chicken Tikka",
    "Achari Chicken Tikka",
    
]


# Location coordinates
LAT = "17.4875418"
LNG = "78.3953462"

# Set up Selenium WebDriver (Headless Mode)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in the background
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Start WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Create an Excel writer
excel_writer = pd.ExcelWriter("Swiggy_Food_Data_New.xlsx", engine="openpyxl")

for query in search_queries:
    print(f"Fetching data for: {query}")

    # Construct API URL with proper encoding
    api_url = f"https://www.swiggy.com/dapi/restaurants/search/v3?lat={LAT}&lng={LNG}&str={query.replace(' ', '%20')}&trackingId=undefined&submitAction=ENTER"
    print(f"API URL: {api_url}")
    # Open the URL in Selenium
    driver.get(api_url)

    # Extract page source (JSON response)
    page_source = driver.find_element("tag name", "pre").text  # JSON is in <pre> tag

    # Parse JSON data
    try:
        data = json.loads(page_source)
        dish_data = []

        # Extract relevant dish details
        for card in data.get("data", {}).get("cards", []):
            grouped_card = card.get("groupedCard", {})
            if "cardGroupMap" in grouped_card:
                dishes = grouped_card["cardGroupMap"].get("DISH", {}).get("cards", [])
                for dish_card in dishes:
                    dish_info = dish_card.get("card", {}).get("card", {}).get("info", {})
                    restaurant_info = dish_card.get("card", {}).get("card", {}).get("restaurant", {}).get("info", {})
                    if dish_info:
                        dish_data.append({
                            "Dish Name": dish_info.get("name", "N/A"),
                            "Category": dish_info.get("category", "N/A"),
                            "Description": dish_info.get("description", "N/A"),
                            "Price (₹)": dish_info.get("price", 0) / 100,  # Convert paise to ₹
                            "Rating": dish_info.get("ratings", {}).get("aggregatedRating", {}).get("rating", "N/A"),
                            "Restaurant Name": restaurant_info.get("name", "N/A"),
                            "Restaurant Address": restaurant_info.get("locality", "N/A"),
                            "Cuisine": ", ".join(restaurant_info.get("cuisines", [])),
                            "Cost for Two (₹)": restaurant_info.get("costForTwoMessage", "N/A"),
                            "Average Rating": restaurant_info.get("avgRating", "N/A"),
                            "Total Ratings": restaurant_info.get("totalRatingsString", "N/A"),
                            "Delivery Time (mins)": restaurant_info.get("sla", {}).get("slaString", "N/A"),
                            "Distance (km)": restaurant_info.get("sla", {}).get("lastMileTravelString", "N/A")
                        })

        # Save to Excel
        if dish_data:
            df = pd.DataFrame(dish_data)
            df.to_excel(excel_writer, sheet_name=query[:31], index=False)
        else:
            print(f"No data found for {query}")

    except json.JSONDecodeError:
        print(f"Failed to decode JSON for {query}")

# Close Selenium WebDriver
driver.quit()

# Save Excel File
excel_writer.close()
print("Excel file 'Swiggy_Food_Data_new.xlsx' created successfully!")