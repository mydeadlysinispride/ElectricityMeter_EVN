from dotenv import load_dotenv
import pandas as pd
load_dotenv()
import base64
import streamlit as st
import os
import io
from PIL import Image 
# import pdf2image
import cv2
from gemini_model import GeminiModel
import time
import openpyxl
system_prompt_1 = """
               Bạn là chuyên gia xử lý ảnh.
               Bạn sẽ đọc ảnh của người dùng đưa vào, biết ảnh đó chứa công tơ điện.
               Trích xuất đưa ra mã số của công tơ, biết mã công tơ thường ở gần mã vạch.
               Lưu ý chỉ đưa ra duy nhất mã công tơ, không lập luận hay trả lời thêm 1 từ ngữ hay số nào
               """

system_prompt_2 = """
               Bạn là chuyên gia xử lý ảnh.
               Bạn sẽ đọc ảnh của người dùng đưa vào, biết ảnh đó chứa công tơ điện.
               Biết số 180 và 380 không phải số cần đọc.
               Trích xuất đưa ra chỉ số màn hình của công tơ.
               Lưu ý chỉ đưa ra duy nhất chỉ số trên màn hình của công tơ, không lập luận hay trả lời thêm 1 từ ngữ hay số nào
               * Ví dụ:* 
                màn hình của công tơ:           380 
                                                    25881.21
                Trả về: 25881.21
                
               """

user_prompt_1 = "Cho tôi mã công tơ"
user_prompt_2 = "Cho tôi chỉ số trên màn hình của công tơ"


# image_path = "D:\\EVN\\Đọc công tơ tự động\\5fc8cf597dd0d38e8ac121.jpg"

# allow user to choose folder
st.title("Đọc công tơ tự động")
st.write("Chọn thư mục chứa ảnh cần đọc")

# Create two columns
col1, col2 = st.columns(2)

# Put a button in each column
button1 = col1.button("Đọc mã công tơ")
button2 = col2.button("Đọc chỉ số trên màn hình của công tơ")


# Check which button was pressed and set the prompts accordingly
if button1:
    user_prompt = user_prompt_1
    system_prompt = system_prompt_1
elif button2:
    user_prompt = user_prompt_2
    system_prompt = system_prompt_2

# create a bar allow user insert folder path
folder_path = st.text_input("Nhập đường dẫn thư mục")
path = folder_path.replace("\\", "\\\\")
# # Check if the Excel file exists
# if os.path.exists('Meter_Codes.xlsx'):
#     # If it exists, load the data into the DataFrame
#     df = pd.read_excel('Meter_Codes.xlsx')
# else:
#     # If it doesn't exist, initialize an empty DataFrame
#     df = pd.DataFrame(columns=['Image Path', 'Meter Code', 'Meter Reading'])

if (button1 or button2) and folder_path:
    st.write("Bat dau doc anh trong folder: ", folder_path)
    # get all image_paths in selected folder
    image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.jpg')]
    total_images = len(image_paths)

    gemini = GeminiModel()

    # If button1 was clicked, initialize a new DataFrame
    if button1:
        df = pd.DataFrame(columns=['Image Path', 'Meter Code', 'Meter Reading'])
    # If button2 was clicked and the Excel file exists, load the data into the DataFrame
    elif button2 and os.path.exists('Meter_Codes.xlsx'):
        df = pd.read_excel('Meter_Codes.xlsx')

    # Create a visual progress bar
    progress_bar = st.progress(0)
    for i, image_path in enumerate(image_paths[:5]):
        text = gemini.generate(image_path, system_prompt,user_prompt)
        # If button1 was clicked, rename the image and add the image path and meter code to the DataFrame
        if button1:
            # rename image name to text
            new_image_path = os.path.join(folder_path, text + '.jpg')
            os.rename(image_path, new_image_path)
            df = df._append({'Image Path': new_image_path, 'Meter Code': text}, ignore_index=True)

        # If button2 was clicked, update the 'Meter Reading' column for the corresponding 'Meter Code'
        elif button2:
            #convert text to float
            text = float(text)
            print(text)
            # add text to Meter Reading column that have image name equal to Meter Code column
            df.loc[df['Image Path'] == image_path, 'Meter Reading'] = text


        progress_bar.progress((i + 1) / total_images)
        time.sleep(1)
    # Write the DataFrame to an Excel file
    df.to_excel('Meter_Codes.xlsx', index=False)
    st.write("Đã hoàn thành quá trình đọc ảnh")

    # Create a download button for the Excel file
    with open('Meter_Codes.xlsx', 'rb') as f:
        bytes_data = f.read()
    st.download_button(
        label="Download Excel file",
        data=bytes_data,
        file_name='Meter_Codes.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


