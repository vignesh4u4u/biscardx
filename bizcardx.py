# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 19:07:59 2023

@author: THIS PC
"""

import easyocr as ocr
import streamlit as st
import PIL
from PIL import Image
from PIL import ImageDraw
import numpy as np
import sqlite3
from io import BytesIO

st.title("Easy OCR-BIZ Card X")
st.markdown("## Using `easyocr`,`streamlit`")
#st.info('This is a purely informational message', icon="ℹ️")

tab1,tab2=st.tabs(["Upload Image","Saved Data"])


@st.cache_data
def load_model():
    reader=ocr.Reader(['en'],model_storage_directory='.')
    return reader
def draw_boxes(image,bounds,color='red',width=2):
  draw=ImageDraw.Draw(image)
  for bound in bounds:
    p0,p1,p2,p3=bound[0]
    draw.line([*p0,*p1,*p2,*p3,*p0],fill=color,width=width)
  return image

@st.cache_data
def insertBLOB(filename,im_data,extracted_text):
    try:
        sqliteConnection = sqlite3.connect(r"\Users\THIS PC\OneDrive\Desktop\bizcardx\bizcardx_db.db")
        cursor = sqliteConnection.cursor()
        #st.write("Connected to SQLite")
        sqlite_insert_blob_query = """ INSERT INTO biscardx
                                  (filename, image, extracted_text) VALUES (?, ?, ?)"""
        create_table="""CREATE TABLE "biscardx" (
                    "filename"	TEXT NOT NULL,
                    "image"	BLOB NOT NULL,
                    "extracted_text"	TEXT NOT NULL,
                    PRIMARY KEY("filename"))"""    
        #photo = convertToBinaryData(photo)
        
        # Convert data into tuple format
        
        data_tuple = (filename,im_data,extracted_text)
        #cursor.execute(create_table)
        st.write('table created')
        cursor.execute(sqlite_insert_blob_query,data_tuple)
        sqliteConnection.commit()
        st.write("Image and file inserted successfully as a BLOB into a table")
        cursor.close()

    except sqlite3.Error as error:
        st.write("Failed to insert blob data into sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            st.write("the sqlite connection is closed")


with tab1:
    image=st.file_uploader(label="Stuborn on vision Flexible on details",type=['png','jpg','jpeg'])
    
    
    reader=load_model()

    if image is not None:
        bytes_data = image.getvalue()
        
        
        input_image=PIL.Image.open(image)
        st.image(input_image)

        with st.spinner("Extracting text..."):
            
            #reading text from image
            result=reader.readtext(np.array(input_image),detail=1,paragraph=True)
            
            #making list of the extracted texts
            result_text=[]
            
            for text in result:
                result_text.append(text[1])
            
            #drawing boxes in image over the detected texts
            st.image(draw_boxes(input_image,result))
            
            st.write(result_text)
            
            #editing the detetcted text
            st.subheader('Edit the extracted text as you want before Saving')
            edited_list = st.experimental_data_editor(result_text,num_rows="dynamic")
            
            #making the extracted and edited text into a string to easily save in database
            extracted_text=''
            for text in edited_list:
                extracted_text+=' '+text
            st.subheader('Edited text')    
            st.write(extracted_text)
            st.success("Extraction completed")
            
            #defining all the values for database insertition
            filename=st.text_input('Save file as')
            st.caption('Quick Suggestion-->Save filename with name & Contact no to retrieve data as it creates unique value')
            
            save_button=st.button('Save image in database')
            
            if save_button:
                insertBLOB(filename,bytes_data,extracted_text)
                
                st.success("File saved successfully")
            else:
                st.write('file not saved')
    else:
        st.error('Upload Image', icon="🚨")
    
with tab2:
    saved_name=st.text_input('Enter the name you used while saving(case sensitive)')
    
    with st.spinner("Loading..."):
        def readBlobData(empIdd):
            try:
                sqliteConnection = sqlite3.connect(r"\Users\THIS PC\OneDrive\Desktop\bizcardx\bizcardx_db.db")
                cursor = sqliteConnection.cursor()
                #st.write("Connected to SQLite")

                sql_fetch_blob_query = """SELECT * from biscardx where filename = ?"""
                cursor.execute(sql_fetch_blob_query, (saved_name,))
                record = cursor.fetchall()
                for row in record:
                    name = row[0]
                    st.write(name)
                    
                    photo = row[1]
                    image_data = BytesIO(photo)
                    img = Image.open(image_data)
                    st.image(img)
                    text = row[2]
                    st.write(text)
                    
                cursor.close()

            except sqlite3.Error as error:
                st.write("Failed to read blob data from sqlite table", error)
            finally:
                if sqliteConnection:
                    sqliteConnection.close()
                    #st.write("sqlite connection is closed")
                    
        def del_dat(saved_name):
            try:
                sqliteConnection = sqlite3.connect(r"\Users\THIS PC\OneDrive\Desktop\bizcardx\bizcardx_db.db")
                cursor = sqliteConnection.cursor()
                #st.write("Connected to SQLite")
                
                sql_fetch_blob_query = """DELETE FROM biscardx WHERE filename = ?"""
                cursor.execute(sql_fetch_blob_query, (saved_name,))
                st.success('File was deleted!')
                sqliteConnection.commit()
                cursor.close()
            except sqlite3.Error as error:
                st.write("Failed to delete data from sqlite table", error)
            finally:
                if sqliteConnection:
                    sqliteConnection.close()
                
            
                    
        
        if saved_name is not None:
            get_data=st.button("Get data")
            del_data=st.button("Delete data")
            if get_data:
                readBlobData(saved_name)
                
            elif del_data:
                    del_dat(saved_name)
            else:
                st.info('click the button to chose what you want to do with the data')
        else:
            st.write("Please enter the name to get the saved data\n No data available under such name")
            
            