import math
import time
import datetime
import dateutil.relativedelta
import pprint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--ignore-certification")
options.add_argument("--ignore-ssl-errors")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
wait = WebDriverWait(driver, 60)

def computeData(data):
    result = {}
    for key in data:
        vacancy = len(data[key])
        mean = 0
        stddev = 0
        minimum = 0
        maximum = 0
        if vacancy != 0:
            minimum = data[key][0]
            maximum = data[key][0]
            total = 0
            for price in data[key]:
                total += price
                if price < minimum:
                    minimum = price
                if price > maximum:
                    maximum = price
            mean = total / vacancy
            total_difference_squared = 0
            for price in data[key]:
                total_difference_squared = (price - mean) * (price - mean)
            stddev = math.sqrt(total_difference_squared / vacancy)
        result[key] = {"vacancy": len(data[key]), "mean": int(mean), "stddev": int(stddev), "min": int(minimum), "max": int(maximum)}
    return result

def printData(data):
    data = computeData(data)
    pprint.pprint(data)
    result = ""
    for key in sorted(data.keys()):
        value = data[key]
        result += str(value["mean"]) if value["vacancy"] > 0 else ""
        result += ","
        result += str(value["min"]) if value["vacancy"] > 0 else ""
        result += ","
        result += str(value["max"]) if value["vacancy"] > 0 else ""
        result += ","
        result += str(value["stddev"]) if value["vacancy"] > 0 else ""
        result += ","
        result += str(value["vacancy"])
        result += ","
    print(result)
    print("")

def remapData(data, mapping):
    result = {}
    for key, value in mapping.items():
        result[value] = []
    for key, value in data.items():
        if key not in mapping.keys():
            print("ERROR: Key [" + key + "] cannot be found in mapping.")
        else:
            result[mapping[key]] = value;
    return result

def load(url, waitForLoad=True):
    driver.get(url)
    if (waitForLoad):
        wait.until(lambda driver: driver.execute_script('return window.jQuery != undefined && jQuery.active == 0'))

def bayside():
    load("https://baysidevillage.com/floor-plans/")
    print("Extracting Bayside Village Place...")
    floorplans = driver.find_elements(By.CLASS_NAME, "floorplan-item")
    data = {}
    for floorplan in floorplans:
        bed_type = floorplan.find_element(By.CLASS_NAME, "bed-count").get_attribute("innerText")
        bed_type = bed_type.split(" /")[0]
        if bed_type not in data:
            data[bed_type] = []
        units = floorplan.find_elements(By.CLASS_NAME, "fp-detail-unit")
        for unit in units:
            price = unit.find_elements(By.TAG_NAME, "li")[2].get_attribute("innerText")
            price = price.split(" ")[0]
            price = price.split("$")[1].replace('$','').replace(',','')
            data[bed_type].append(int(price))
    data = remapData(data, {"STUDIO": "0", "1 BED": "1", "2 BED": "2"})
    printData(data)

def soma_square():
    print("Extracting SoMa Square Apartments...")
    load("https://www.apartments.com/soma-square-san-francisco-ca/8zcfk91/")
    bed_type_sections = driver.find_element(By.XPATH, "//*[@class='tab-section active']").find_elements(By.XPATH, "//*[@class='pricingGridItem multiFamily hasUnitGrid']")
    data = {}
    for bed_type_section in bed_type_sections:
        bed_type = bed_type_section.find_element(By.CLASS_NAME, "modelName")
        bed_type = bed_type.get_attribute("innerText").split()[0]
        if bed_type not in data:
            data[bed_type] = []
        units = bed_type_section.find_elements(By.CLASS_NAME, "unitContainer")
        for unit in units:
            try:
                price = unit.find_element(By.CLASS_NAME, "pricingColumn")
                price = price.get_attribute("innerText").split("$")[1].replace('$','').replace(',','')
                data[bed_type].append(int(price))
            except NoSuchElementException:
                    data[bed_type] = []
    data = remapData(data, {"Studio": "0", "1": "1", "2": "2"})
    printData(data)
    

def lseven():
    print("Extracting L Seven Apartments...")
    load("https://www.l7sf.com/OnlineLeasing.aspx")
    time.sleep(10)
    driver.switch_to.frame(driver.find_element(By.TAG_NAME, "iframe"))
    floorplans = driver.find_elements(By.CLASS_NAME, 'floorplan-tile')
    data = {}
    for floorplan in floorplans:
        availability = floorplan.find_element(By.CLASS_NAME, "primary").get_attribute("innerText")
        if "Check" in availability:
            continue
        availability = availability.split("(")[1].split(")")[0].replace('(','')
        price = floorplan.find_element(By.CLASS_NAME, "range").get_attribute("innerText")
        price = price.split("$")[1].replace('$','').replace(',','').replace(' -','').replace('*','')
        bed_type = floorplan.find_element(By.CLASS_NAME, "specs").get_attribute("innerText")
        bed_type = bed_type.split("|")[0].replace(' ','')
        if bed_type not in data:
            data[bed_type] = []
        for x in range(int(availability)):
            data[bed_type].append(int(price))
    data = remapData(data, {"Studio": "0", "1Bed": "1", "2Beds": "2"})
    printData(data)

def rincongreen():
    print("Extracting Rincon Green Apartments...")
    load("https://www.rincongreen.com/Floor-plans.aspx")
    floorplans = driver.find_elements(By.CLASS_NAME, "floorplan-block")
    data = {}
    for floorplan in floorplans:
        bed_type = floorplan.get_attribute("data-bed")
        if bed_type not in data:
            data[bed_type] = []
        units = floorplan.find_element(By.CLASS_NAME, "par-units").find_elements(By.TAG_NAME, "tr")
        units.pop(0)
        for unit in units:
            price = unit.find_elements(By.TAG_NAME, "td")[3].get_attribute("innerText")
            price = price.split("$")[1].replace('$','').replace(',','')
            data[bed_type].append(int(price))
    data = remapData(data, {"S": "0", "1": "1", "2": "2"})
    printData(data)

def soma788():
    print("Extracting SOMA at 788...")
    load("https://www.somaat788.com/Floor-plans.aspx")
    floorplans = driver.find_elements(By.CLASS_NAME, "floorplan-block")
    data = {}
    for floorplan in floorplans:
        bed_type = floorplan.get_attribute("data-bed")
        if bed_type not in data:
            data[bed_type] = []
        units = floorplan.find_element(By.CLASS_NAME, "par-units").find_elements(By.TAG_NAME, "tr")
        units.pop(0)
        for unit in units:
            price = unit.find_elements(By.TAG_NAME, "td")[3].get_attribute("innerText")
            price = price.split("$")[1].replace('$','').replace(',','')
            data[bed_type].append(int(price))
    data = remapData(data, {"S": "0", "1": "1", "2": "2"})
    printData(data)

def avalon():
    print("Extracting Avalon...")
    load("https://new.avaloncommunities.com/california/san-francisco-apartments/avalon-at-mission-bay/")
    driver.find_element(By.CLASS_NAME, "ant-modal-close").click()
    driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "load-all-units"))
    data = {}
    units = driver.find_elements(By.CLASS_NAME, "unit-item-details")
    for unit in units:
        info = unit.find_element(By.CLASS_NAME, "description").get_attribute("innerText")
        bed_type = info.split("•")[0].replace(' ','').replace('Furnished','')
        if bed_type not in data:
            data[bed_type] = []
        price = unit.find_element(By.CLASS_NAME, "unit-price").get_attribute("innerText").replace(' ','').replace('$','').replace(',','')
        data[bed_type].append(int(price))
    data = remapData(data, {"Studio": "0", "1bed": "1", "2beds": "2"})
    printData(data)

def george():
    print("Extract George...")
    load("https://www.thegeorgesf.com/apartment-availability.html", False)
    time.sleep(10)
    data = {}
    driver.switch_to.frame(driver.find_element(By.ID, "sightmap"))
    floors_list = driver.find_element(By.ID, "floor-horizontal-select")
    floors = floors_list.find_elements(By.TAG_NAME, "li")
    for i in range(len(floors)):
        if i < 2:
            continue
        floor = floors[i]
        driver.execute_script("arguments[0].click();", floor)
        floorplans = driver.find_element(By.CLASS_NAME, "list-item-container").find_elements(By.TAG_NAME, "a")
        for floorplan in floorplans:
            innerText = floorplan.get_attribute("innerText")
            if "Studio" in innerText:
                bed_type = "0"
            elif "1 Bed" in innerText:
                bed_type = "1"
            elif "2 Bed" in innerText:
                bed_type = "2"
            else:
                continue
            price = ""
            innerTextSplit = innerText.replace('\n',' ' ).split(" ")
            for text in innerTextSplit:
                if "$" in text:
                    price = text
                    break
            price = price.replace('$','').replace(',','')
            if bed_type not in data:
                data[bed_type] = []
            data[bed_type].append(int(price))
    printData(data)

def run():
    bayside()
    soma_square()
    lseven()
    rincongreen()
    soma788()
    avalon()
    george()

def test():
    data = {}
    data["0"] = []
    data["0"].append(100)
    data["0"].append(101)
    data["0"].append(102)
    data["1"] = []
    data["1"].append(200)
    data["1"].append(201)
    data["2"] = []
    data["2"].append(300)
    data["3"] = []
    printData(data)

run()
#test()

driver.quit()
