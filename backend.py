from ollama import chat
import json
import requests
from pymongo_get_database import get_database


PIXABAY_API_KEY = <key>

class TextInterface: #FIXME: FEATURE : Get nutritional data for each grocery item.
    @staticmethod #Runs without saving instance of class.
    def set_context_and_process_image(uploaded_file_text): #Returns dictionary of food items. 
        print(uploaded_file_text)
        messages = [
            {
                "role": "system", #Specify role as system.
                "content": (
                    "You are a helpful health coach assistant. I will provide you with raw grocery receipt text extracted by OCR, which may be noisy, contain OCR errors, or irrelevant lines.\n\n"
                    "Your task is to:\n"
                    "1. Clean the text by removing irrelevant lines (like DATE, SPECIAL, TOTAL, SUBTOTAL, CASH, LOYALTY, CHANGE, etc.).\n"
                    "2. Correct common OCR mistakes (e.g., fix misspelled items like 'TUCHINNI' → 'ZUCCHINI', 'k9' or 'kq' → 'kg').\n"
                    "3. Extract only the grocery item names from the cleaned text.\n"
                    "4. Return a Python list named `Items` containing only the corrected item names from the receipt here is an example of an ocr-text (e.g.: Items = ['durian', 'cabbage', 'grapes', ...]).\n"
                    "5. Return **ONLY the exact Python list** with no additional explanation or formatting.\n\n"
                    "Here is the raw OCR text:"
                )
            },
            {
                "role": "user",  #Specify role as user.
                "content": uploaded_file_text  # The entire raw OCR string you got from Tesseract :)
            }
        ]

        response = chat(model="gemma3", messages=messages)

        pantry_items = response['message']['content']

        start = pantry_items.find('[') + 1
        end = pantry_items.find(']')

        pantry_items = pantry_items[start:end]
        pantry_items = pantry_items.split(',')

        pantry_dict = [{"item_name": items} for items in pantry_items]

        return pantry_dict
    
    @staticmethod
    def chat_with_llm(streamlit_messages):
        response = chat(model="gemma3", messages=streamlit_messages)
        return response['message']['content']
    
    
    # Call with dictionary from image process, receive JSON of dish name, description, ingredients, and imagelink.
    # Dict is structured: name:, description:, ingredients:, image:.
    @staticmethod
    def create_dishes_with_images(food_items):
        food_list_str = "\n".join(f"- {item}" for item in food_items)

        prompt = f"""
        You are a creative recipe generator.

        You will be given a fixed dictionary of available food items.  
        You must create exactly **6 imaginative dishes** using ONLY these food items.  
        You are NOT allowed to use any ingredient that is not explicitly listed.  

        Guidelines:
        1. ONLY use the items in the dictionary — no other ingredients.
        2. You MAY use any cooking method or presentation style (roasting, baking, mashing, layering, skewering, etc.).
        3. Each dish must have a **restaurant-style, appetizing name**.
        4. Each description must be **creative and sensory-rich**: mention textures (creamy, crispy, smooth), preparation (roasted, blended, stacked), and presentation (layered, bowls, rolls) — but never invent new ingredients.
        5. Each dish must include a list of ingredients from the dictionary.
        6. If a valid dish cannot be created, write "error".

        STRICT RULES:
        1. Use ONLY the provided items. No extra ingredients.
        2. Each dish must have the following keys, spelled exactly:
           - "dish_name"
           - "description"
           - "ingredients"
           - "image"
        3. Do NOT use any alternative keys (e.g., "dish_name", "title", "recipe_name").  
        4. Return ONLY a valid JSON array, no commentary or extra text.
        
        5. Every dish must contain ALL 4 keys: "dish_name", "description", "ingredients", "image".
        6. If any of these keys are missing, the entire answer is invalid.

        YOU WILL FOLLOW THIS JSON OUTPUT SCHEMA EXACTLY OR ELSE EVERYTHING WILL CRASH:
        [
          {{
            "dish_name": "Roasted Tomato Medley",
            "description": "Juicy roasted tomatoes layered with crispy onions for a warm, rustic dish.",
            "ingredients": ["tomato", "onion"],
            "image": "https://via.placeholder.com/400x300.png?text=Roasted+Tomato+Medley"
          }}
        ]

        Dictionary of available food items:
        {food_list_str}

        Now return exactly 6 valid dishes following the rules above.  
        Return ONLY the JSON array, with no commentary, no code fences, no extra text.
        """

        response = chat(
            model="gemma3:latest",
            messages=[{"role": "user", "content": prompt}]
        )
        dishes_str = response['message']['content']
        print(type(dishes_str))

        start = dishes_str.find('[')
        end = dishes_str.rindex(']') + 1 #FIXME: INCORRECT INDEXING

        dishes_str = dishes_str[start:end]
        print(dishes_str)

        try:
            dishes_json = json.loads(dishes_str)

            # RETURN ON SUCCESS
            return dishes_json

        except json.JSONDecodeError:
            # Sometimes the model adds extra text; you may need to clean it first
            print("Invalid JSON, model may have added extra text.")

        return 'empty'

        #Send in string='garlic butter chicken', return string of image http:// link. 
    @staticmethod
    def get_image_link(query_string):
        
        url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&q={query_string}&image_type=photo&per_page=3"

        response = requests.get(url).json()
        image_url = response["hits"][0]["webformatURL"]

        return image_url
        
    
class PantryStorage: 
    @staticmethod
    def create_user_pantry(name='no_name'):

        dbname = get_database()

        collection_name = dbname[name]   #BECOMES: dbname[f'{name}_pantry']

        return collection_name
    
    @staticmethod
    def insert_groceries(name = 'no_name', item_list_response= {'None' : 'Name not passed'}):
        #Retrieves collection name/object. If this collection name is new, it is a new collection.
        dbname = PantryStorage.create_user_pantry(name)

        #Inserts the dictionary of k:v items into MongoDB atlas.
        dbname.insert_many(item_list_response) 
    @staticmethod
    def get_groceries(name = 'no_name', item_list_response= {'None' : 'Name not passed'}):
        dbname = PantryStorage.create_user_pantry(name)

        #Inserts the dictionary of k:v items into MongoDB atlas.
        item_files = dbname.find(item_list_response)
        json_docs = [json.loads(json.dumps(item, default=str)) for item in item_files]
        return json_docs


