#!/usr/bin/env python3
"""Minimal Codio login helper using Selenium."""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json
from tqdm import tqdm
import os
import dotenv

dotenv.load_dotenv()

CODIO_URL = "https://codio.com/p/login?nextPath=/home/student%3Fcourse_id%3Da40c9cfd0d8e45a5b18cb24e7dad49ee"
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

DISPLAY = True

options = Options()
if not DISPLAY:
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")

def get_full_identifier(driver, section):
    return driver.execute_script(
                "function absoluteXPath(element) {"
                "var comp, comps = [];"
                "var parent = null;"
                "var xpath = '';"
                "var getPos = function(element) {"
                "var position = 1, curNode;"
                "if (element.nodeType == Node.ATTRIBUTE_NODE) {"
                "return null;"
                "}"
                "for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {"
                "if (curNode.nodeName == element.nodeName) {"
                "++position;"
                "}"
                "}"
                "return position;"
                "};"
                "if (element instanceof Document) {"
                "return '/';"
                "}"
                "for (; element && !(element instanceof Document); element = element.nodeType ==Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {"
                "comp = comps[comps.length] = {};"
                "switch (element.nodeType) {"
                "case Node.TEXT_NODE:"
                "comp.name = 'text()';"
                "break;"
                "case Node.ATTRIBUTE_NODE:"
                "comp.name = '@' + element.nodeName;"
                "break;"
                "case Node.PROCESSING_INSTRUCTION_NODE:"
                "comp.name = 'processing-instruction()';"
                "break;"
                "case Node.COMMENT_NODE:"
                "comp.name = 'comment()';"
                "break;"
                "case Node.ELEMENT_NODE:"
                "comp.name = element.nodeName;"
                "break;"
                "}"
                "comp.position = getPos(element);"
                "}"
                "for (var i = comps.length - 1; i >= 0; i--) {"
                "comp = comps[i];"
                "xpath += '/' + comp.name.toLowerCase();"
                "if (comp.position !== null && comp.position > 1) {"
                "xpath += '[' + comp.position + ']';"
                "}"
                "}"
                "return xpath;"
                "}"
                "return absoluteXPath(arguments[0]);", section)
    
def active_scroll(driver, scroll_time=300):
    # /html/body/div[1]/div[4]/div[2]/div/div[1]/div[3]/div[3]/div[2]/div/div[1]/div[2]/iframe
    time.sleep(5)
    iframe = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div[2]/div/div[1]/div[3]/div[3]/div[2]/div/div[1]/div[2]/iframe")
    driver.switch_to.frame(iframe)
    start_time = time.time()
    for i in tqdm(range(scroll_time*10)):
        time.sleep(1/10)
        new_height = driver.execute_script("return document.body.scrollHeight - window.innerHeight")
        driver.execute_script(f"window.scrollTo(0, {round(i * new_height / scroll_time / 10)});")
        if (time.time() - start_time) > scroll_time:
            break # if scroll time is reached, break. This is a backup
    driver.switch_to.default_content()


def main() -> None:
    driver = webdriver.Chrome(options=options)
    driver.get(CODIO_URL)
    driver.implicitly_wait(1000)
    button = driver.find_element(By.XPATH, "/html/body/main/div/div[1]/div/div[2]/div[1]/form/div/div[1]/div/input")
    button.send_keys(USERNAME)
    button = driver.find_element(By.XPATH, "/html/body/main/div/div[1]/div/div[2]/div[1]/form/div/div[2]/div/div/input")
    button.send_keys(PASSWORD)
    button = driver.find_element(By.XPATH, "/html/body/main/div/div[1]/div/div[2]/div[1]/form/div/button")
    button.click()
    print("Logged in")
    driver.implicitly_wait(1000)
    chapters = driver.find_elements(By.XPATH, "/html/body/main/div/div[1]/main/div[2]/div/div/div[1]/div/div[3]/div/div[*]")
    # chapters
    # /html/body/main/div/div[1]/main/div[2]/div/div/div[1]/div/div[3]/div/div[1]
    # sections
    # /html/body/main/div/div[1]/main/div[2]/div/div/div[1]/div/div[3]/div/div[1]/div/div/div/div/div/div/table/tbody/tr[1]
    information = {
        "chapters": [],
        "total_grade": 0,
        "total_answered": 0,
        "total_status": 0,
        "total_completed": 0
    }
    for chapter in chapters:
        # /html/body/main/div/div[1]/main/div[2]/div/div/div[1]/div/div[3]/div/div[5]/h3/button/span[1]/div
        text = chapter.find_element(By.XPATH, "./h3/button/span[1]/div").text
        chapter_details = {
            "name": text,
            "sections": []
        }
        driver.implicitly_wait(1000)
        section = chapter.find_elements(By.XPATH, "./div/div/div/div/div/div/table/tbody/tr[*]")
        for section in section:
            section_details = {
                "name": "",
                "grade": "",
                "answered": "",
                "status": "",
                "completed": False,
                "identifier": ""
            }
            section_details["name"] = section.find_element(By.XPATH, "./td[1]").text
            section_details["grade"] = section.find_element(By.XPATH, "./td[2]").text
            section_details["answered"] = section.find_element(By.XPATH, "./td[3]").text
            section_details["status"] = section.find_element(By.XPATH, "./td[4]").text
            # ./td[5]/span/span[1]/input
            if section.find_element(By.XPATH, "./td[5]").text != "":
                completed = section.find_element(By.XPATH, "./td[5]/span/span[1]/input").get_attribute("checked")
                if completed:
                    section_details["completed"] = True
                else:
                    section_details["completed"] = False
            section_details["identifier"] = section.get_attribute("xpath") if section.get_attribute("xpath") else get_full_identifier(driver, section)
            print(section_details)
            chapter_details["sections"].append(section_details)
        information["chapters"].append(chapter_details)
        print("--------------------------------")
    
    json.dump(information, open("information.json", "w"))
    
    print("Done")
    print("--------------------------------")
    tasks = []
    for chapter in information["chapters"]:
        for section in chapter["sections"]:
            # Skip if completed
            if section["completed"]:
                continue
            # Skip if status is disabled or completed
            if section["status"] in ["disabled", "completed"]:
                continue
            # Skip if name contains "chip" or answered is not empty
            if "chip" in section["name"].lower() or section["answered"] != "":
                continue
            tasks.append(section)
            print(section)
    print("--------------------------------")
    print(f"Total tasks: {len(tasks)}")
    print("--------------------------------")
    if os.path.exists("checkpoints.json"):
        checkpoints = json.load(open("checkpoints.json"))
    else:
        checkpoints = {}
    # Remove tasks whose name is in checkpoints and marked completed
    tasks = [task for task in tasks if not (task["name"] in checkpoints and checkpoints[task["name"]].get("completed"))]
    print(f"Total tasks after removing completed tasks: {len(tasks)}")
    print("--------------------------------")
    for task in tasks:
        if task["name"] in checkpoints:
            continue
        print(f"Working on task: {task['name']}")
        driver.find_element(By.XPATH, task["identifier"]).click() # this will replace the current page
        time.sleep(5)
        driver.implicitly_wait(1000)
        active_scroll(driver, scroll_time=300) # scroll to the bottom of the page in 300s
        driver.implicitly_wait(1000)
        
        # reset page
        driver.get(CODIO_URL)
        driver.implicitly_wait(1000)
        driver.find_element(By.XPATH, "/html/body/main/div/div[1]/main/div[2]/div/div/div[1]/div/div[3]/div/div/ul").click()
        driver.implicitly_wait(1000)
        checkpoints[task["name"]] = {"completed": True, "timestamp": time.time()}
        json.dump(checkpoints, open("checkpoints.json", "w"))

    time.sleep(600)

if __name__ == "__main__":
    main()
