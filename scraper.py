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

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
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
    for key, value in data.items():
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
            result[key] = value;
        else:
            result[mapping[key]] = value;
    return result

def load(url):
    driver.get(url)
    wait.until(lambda driver: driver.execute_script('return jQuery.active == 0'))

def bayside():
    print("Extracting Bayside Village Place...")
    load("https://baysidevillage.com/floor-plans/")
    # datepicker = driver.find_element_by_id("floorplan-datepicker")
    # datepicker.clear()
    # today = datetime.datetime.now()
    # next_month = today + dateutil.relativedelta.relativedelta(months=+1)
    # date = next_month.strftime("%m/%d/%Y")
    # datepicker.send_keys(date)
    # wait.until(lambda driver: driver.execute_script('return jQuery.active == 0'))
    floorplans = driver.find_elements_by_class_name("floorplan-item")
    data = {}
    for floorplan in floorplans:
        bed_type = floorplan.find_element_by_class_name("bed-count").get_attribute("innerText")
        bed_type = bed_type.split(" /")[0]
        if bed_type not in data:
            data[bed_type] = []
        units = floorplan.find_elements_by_class_name("fp-detail-unit")
        for unit in units:
            price = unit.find_elements_by_tag_name("li")[2].get_attribute("innerText")
            price = price.split(" ")[0]
            price = price.split("$")[1].replace('$','').replace(',','')
            data[bed_type].append(int(price))
    data = remapData(data, {"STUDIO": "0", "1 BED": "1", "2 BED": "2", "3 BED": "3"})
    printData(data)

def soma_square():
    print("Extracting SoMa Square Apartments...")
    load("https://www.equityapartments.com/san-francisco-bay/soma/soma-square-apartments##unit-availability-tile")
    bed_type_sections = driver.find_element_by_id("unit-availability-tile").find_elements_by_class_name("bedroom-type-section")
    data = {}
    for bed_type_section in bed_type_sections:
        bed_type = bed_type_section.find_element_by_class_name("panel-title").get_attribute("innerText")
        bed_type = bed_type.replace(' ','').replace('\r','').replace('\n','')
        bed_type = bed_type
        if bed_type not in data:
            data[bed_type] = []
        units = bed_type_section.find_elements_by_class_name("list-group-item")
        for unit in units:
            try:
                price = unit.find_element_by_class_name("pricing").get_attribute("innerText")
                price = price.split("$")[1].replace('$','').replace(',','')
                data[bed_type].append(int(price))
            except NoSuchElementException:
                data[bed_type] = []
    data = remapData(data, {"Studio": "0", "1Bed": "1", "2Bed": "2", "3Bed": "3"})
    printData(data)

def lseven():
    print("Extracting L Seven Apartments...")
    load("https://www.l7sf.com/floor-plans")
    #floorplans = driver.find_elements_by_class_name("rpfp-units")
    floorplans = driver.find_elements_by_class_name("rpfp-card")
    data = {}
    for floorplan in floorplans:
        if floorplan.get_attribute("data-availableunits") is None or int(floorplan.get_attribute("data-availableunits")) == 0:
            continue
        button = floorplan.find_element_by_class_name("rpfp-button--availability")
        driver.execute_script("arguments[0].click();", button)
        #wait.until(lambda driver: driver.execute_script('return jQuery.active == 0'))
        #wait.until(EC.presence_of_element_located((By.CLASS_NAME, "rpfp-units")))
        units = driver.find_elements_by_class_name("rpfp-unit")
        for unit in units:
            bed_type = unit.find_element_by_class_name("rpfp-beds").get_attribute("innerText")
            if bed_type not in data:
                data[bed_type] = []
            price = unit.find_element_by_class_name("rpfp-unit-rent").get_attribute("innerText")
            price = price.split("$")[1].replace('$','').replace(',','')
            data[bed_type].append(int(price))
        #availability = int(floorplan.get_attribute("data-availableunits"))
        #if availability == 0:
        #    continue
        #bed_type = floorplan.find_element_by_class_name("rpfp-beds").get_attribute("innerText")
        #if bed_type not in data:
        #    data[bed_type] = []
        #for i in range(int(floorplan.find_element_by_class_name("rpfp-badge").get_attribute("innerText"))):
        #    price = floorplan.find_element_by_class_name("rpfp-rent").get_attribute("innerText")
        #    price = price.split("$")[1].replace('$','').replace(',','')
        #    data[bed_type].append(int(price))
    data = remapData(data, {"0 BD": "0", "1 BD": "1", "2 BD": "2", "3 BD": "3"})
    printData(data)

def rincongreen():
    print("Extracting Rincon Green Apartments...")
    load("https://www.rincongreen.com/Floor-plans.aspx")
    floorplans = driver.find_elements_by_class_name("floorplan-block")
    data = {}
    for floorplan in floorplans:
        bed_type = floorplan.get_attribute("data-bed")
        if bed_type not in data:
            data[bed_type] = []
        units = floorplan.find_element_by_class_name("par-units").find_elements_by_tag_name("tr")
        units.pop(0)
        for unit in units:
            price = unit.find_elements_by_tag_name("td")[3].get_attribute("innerText")
            price = price.split("$")[1].replace('$','').replace(',','')
            data[bed_type].append(int(price))
    data = remapData(data, {"S": "0", "1": "1", "2": "2", "3": "3"})
    printData(data)

def soma788():
    print("Extracting SOMA at 788...")
    load("https://www.somaat788.com/Floor-plans.aspx")
    floorplans = driver.find_elements_by_class_name("floorplan-block")
    data = {}
    for floorplan in floorplans:
        bed_type = floorplan.get_attribute("data-bed")
        if bed_type not in data:
            data[bed_type] = []
        units = floorplan.find_element_by_class_name("par-units").find_elements_by_tag_name("tr")
        units.pop(0)
        for unit in units:
            price = unit.find_elements_by_tag_name("td")[3].get_attribute("innerText")
            price = price.split("$")[1].replace('$','').replace(',','')
            data[bed_type].append(int(price))
    data = remapData(data, {"S": "0", "1": "1", "2": "2", "3": "3"})
    printData(data)

def avalon_extract(url):
    load(url)
    result = []
    prices = driver.find_elements_by_class_name("price")
    for price in prices:
            try:
                price = price.find_element_by_class_name("brand-main-text-color").get_attribute("innerText")
                price = price.split("$")[1].replace('$','').replace(',','')
                result.append(int(price))
            except NoSuchElementException:
                continue
    return result

def avalon():
    print("Extracting Avalon...")
    data = {}
    data["0"] = avalon_extract("https://www.avaloncommunities.com/california/san-francisco-apartments/avalon-at-mission-bay/apartments?bedroom=0BD")
    data["1"] = avalon_extract("https://www.avaloncommunities.com/california/san-francisco-apartments/avalon-at-mission-bay/apartments?bedroom=1BD")
    data["2"] = avalon_extract("https://www.avaloncommunities.com/california/san-francisco-apartments/avalon-at-mission-bay/apartments?bedroom=2BD")
    data["3"] = avalon_extract("https://www.avaloncommunities.com/california/san-francisco-apartments/avalon-at-mission-bay/apartments?bedroom=3BD")
    printData(data)

def run():
    #bayside()
    #soma_square()
    lseven()
    #rincongreen()
    #soma788()
    #avalon()

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