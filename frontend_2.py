import streamlit as st
from backend import TextInterface as TI
from backend import PantryStorage as PS
from imageProcessing import ImageProcessor as impPrc 

st.set_page_config(layout="wide")

st.title("Grocery App Prototype")
uploaded_file = st.file_uploader("Upload the receipt image", type=["jpg", "jpeg", "png"])  #NEWWWW type=[...]

if not uploaded_file:
    st.write("Please upload picture of the receipt")
else: 
    # Avoid re-processing the same uploaded file
    if (
        "last_uploaded_file" not in st.session_state
        or st.session_state.last_uploaded_file != uploaded_file
    ):
        with st.status("Analyzing receipt...", expanded=True) as status: 
            st.write("Extracting items from image... Please wait.")
            processed_receipt = impPrc.returnString(uploaded_file)    #String transcription of receipt.
            status.update(label="Contacting backend...", state="running")

            #Ai parse for each grocery item. This return as dictionary {"item_name": items}. 
            item_list_response = TI.set_context_and_process_image(processed_receipt)
            
            st.session_state.processed_receipt = processed_receipt
            st.session_state.item_list_response = item_list_response
            st.session_state.last_uploaded_file = uploaded_file
            status.update(label="Done", state="complete")

        if "item_list_response" in st.session_state:
            st.success("Items extracted from receipt:")
            PS.insert_groceries(name='user_1_pantry', item_list_response=st.session_state.item_list_response)
   

        #Receive and or make table and insert st.session_state.item_list_response
        #current_collection = PS.insert_many(st.session_state.item_list_response)


# Continue with chat input, history, etc. as before
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user chat input (after image is uploaded AND PROCESSED)
if uploaded_file:

    st_cols = [col for col in st.columns(6)]

    st.write(st.session_state.item_list_response)
    Dishes_json_data = TI.create_dishes_with_images(st.session_state.item_list_response)

    status.update(label="Proposing dish recipes...", state="running")

    with st.status("Analyzing receipt...", expanded=True) as status: 
        status.update(label="Proposing dish recipes...", state="running")

        for (item, col) in zip(Dishes_json_data, st_cols):
            col.write(item['dish_name'])
            col.write(item['description'])
            col.image(TI.get_image_link(item['dish_name']))

        st.success("Items extracted from receipt:")

