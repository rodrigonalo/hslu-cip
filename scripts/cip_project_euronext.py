#Tech with tim: https://www.youtube.com/watch?v=b5jt2bhSeXs&list=PLzMcBGfZo4-n40rB1XaJ0ak1bemvlqumQ&index=2
#Check: https://www.youtube.com/watch?v=OISEEL5eBqg&list=PLzMcBGfZo4-n40rB1XaJ0ak1bemvlqumQ&index=4
import sys

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys # used to send keys
from selenium.webdriver.common.by import By # used to send keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC # used for exception handling
import sys
import time
import pandas as pd
import os
import numpy as np


# Get the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the 'CIP' directory, which is the parent of the 'scripts' directory
cip_dir = os.path.join(script_dir, '..', '..')

# Now, construct the path to the 'raw_data' directory within the 'CIP/data' directory
raw_data_dir = os.path.join(cip_dir, 'data', 'raw_data')

# Finally, create the full path to the 'indexes_to_scrap.xlsx' file
excel_file_path = os.path.join(raw_data_dir, 'indexes_to_scrap.xlsx')

# Reading the Excel file into a DataFrame
df_excel = pd.read_excel(excel_file_path)

# Concatenating the 'ISIN' and 'TRADING LOCATION' columns into a new column in the DataFrame
df_excel['ISIN-MIC'] = df_excel['ISIN'] + '-' + df_excel['TRADING LOCATION']

print(df_excel.head())


#for windows
driver = webdriver.Chrome()

url = 'https://live.euronext.com/en/product/equities/'
indixes_list = ['FR0000121014-XPAR', 'FR0000052292-ETLX', 'IT0004056880-MTAA']

for i in indixes_list:
    comple_url = url + i
    #//Öffnet die webseite
    #ISIN FR0000121014
    #Exchange XPAR
    driver.get(comple_url)
    #print(driver.title)

    #Returns the source code
    #print(driver.page_source)

    #inserts in search bar ISIN and presses RETURN
    #search = driver.find_element(By.ID,"edit-search-input-quote--2")
    #search.clear()
    #search.send_keys("FR0000121014")
    #search.send_keys(Keys.RETURN)



    #Wants to read the Quotes page and waits max. 10 seconds to load
    #Loads currency & market cap into a dictionary.
    share = {"ISIN": i}

    try:
        element_header_main_wrapper = WebDriverWait(driver,10).until( #waits max 10 until the page is loaded
            EC.presence_of_element_located((By.ID, "main-wrapper")))

        element_header_instrument_name = element_header_main_wrapper.find_element(By.ID,"header-instrument-name")
        print("Instrument name is:",element_header_instrument_name.text)

        element_table_responsive = element_header_main_wrapper.find_element(By.CLASS_NAME, "table.border-top.border-bottom-0.mb-2.text-white")
        for element in element_table_responsive.find_elements(By.CSS_SELECTOR,"tr"):
            td_element_list = element.find_elements(By.CSS_SELECTOR, "td")
            match td_element_list[0].text:
                case "Currency":
                    share.update({"Currency": td_element_list[1].text})
                    print("currency added with value:",td_element_list[1].text)
                case "Market Cap":
                    share.update({"Market Cap": td_element_list[1].text})
                    print("Market Cap added with value:", td_element_list[1].text)
            continue
    except NoSuchElementException:
       print("Didn't find the element")
       print(sys.exc_info()[0])
    #finally:
        #driver.quit()  # closes the browser at the end. Doesn't matter if successful or not

    #go to page ESG
    esg_button = WebDriverWait(driver,10).until( #waits max 10seconds until the page is loaded
             EC.presence_of_element_located((By.CLASS_NAME, "nav-item.nav-link.esg-nav-link")))
    esg_button.click()
    # print(driver.page_source)
    time.sleep(3)
    esg_ratings = {"ISIN": "FR0000121014"}
    esg_ratings_list = []

    # esg_ratings_block_description=driver.find_element(By.ID, "EsgRatingsBlockDescription")
    # print(esg_ratings_block_description.text)
    # your code to find and interact with the element

    esg_rating_fields = ["CDP", "FTSE4Good", "MSCI ESG Ratings", "Moody's ESG Solution", "Sustainalytics"]
    other_esg_information = ["Carbon footprint (total GHG emissions / enterprise value)", "Share of women in total workforce", "Rate of resignation"]


    for element in driver.find_elements(By.TAG_NAME, "tr"):
        td_element_list = element.find_elements(By.TAG_NAME, "td")

        if td_element_list: # check if there is an element
            field = td_element_list[0].text.strip()
            if field in esg_rating_fields:
                # Extract the text from the first two cells for each required row
                # Add the Ratings of the ESG Rating row to the dictionary
                share.update({field: field, "Rating" : td_element_list[1].text.strip()})
            elif field in other_esg_information:
                esg_ratings_list.append([field, td_element_list[1].text.strip(),td_element_list[2].text.strip()])
                esg_ratings.update({field: field, "Unit": td_element_list[1].text.strip(),"Rating": td_element_list[2].text.strip()})

    print(share)
    print(esg_ratings)
    print(esg_ratings_list)

    #go to page Characteristics
    try:
        character_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "CHARACTERISTICS"))
        )

        character_button.click()
        characteristics_list = []
        characteristics = ["Type", "Sub type", "Market", "ISIN Code", "Industry","SuperSector", "Sector", "Subsector"]
        time.sleep(3)
        # print(driver.page_source)

        # With this approach it iterates trough many useless "td" labels. but because of the inexistens of id or unique classe names it is not possible otherwise
        for element in driver.find_elements(By.TAG_NAME, "tr"):
            element_list = element.find_elements(By.TAG_NAME, "td")

            if element_list: # check if there is an element
                field = element_list[0].text.strip()
                if field in characteristics:
                    # Extract the text from the first two cells for each required row
                    # Add the Ratings of the ESG Rating row to the dictionary
                    characteristics_list.append([field, element_list[1].text.strip()])
        print("character liste", characteristics_list)
    except:
        print("Unexpected error:", sys.exc_info())


    #selenium returns the first item which it find. Therefore look fore something that is uniquie.  search for first for id then name then class

driver.quit()
