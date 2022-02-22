# Dynamic scraping: Selenium is used to automate web browser interaction (logging in + webpage navigation) and Beautiful Soup is used to scrape grades

import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tabulate import tabulate


def calc_weight_grade(grade, weight):  # define function to calculate weighted grade
    weighted_grade = (grade/100)*weight
    return weighted_grade


course_list = []  # iterable list containing course objects


class Course:

    def __init__(self, name, dict=None, overall_grade=0):
        self.name = name  # instance variables are set within __init__
        course_list.append(self)
        if dict is None:
            self.dict = {}  # defaults to empty dictionary, dict argument is optional
        else:
            self.dict = dict
        self.overall_grade = round(overall_grade, 2)

    def add_grade(self, key, grade, wgrade):
        self.dict[key] = [round(grade, 2), round(wgrade, 2)]

    def add_to_overall_grade(self, grade):
        self.overall_grade += grade


# LOGIN TO SCHOOL WEBPAGE/ INITIAL BROWSER NAVIGATION
# path of chromedriver on OS. chromeDriver is a separate executable that Selenium WebDriver uses to control Chrome; https://stackoverflow.com/questions/64717302/deprecationwarning-executable-path-has-been-deprecated-selenium-python
s = Service('/Users/callyli/Documents/chromedriver')
# define an object for using webdriver function with the chrome webdriver located at inserted path
driver = webdriver.Chrome(service=s)
# initialize object for using WebDriverWait class with 2 arguments: driver object and max timeout in seconds
wait = WebDriverWait(driver, 20)
username = '***************'
password = '***************'
url = 'https://learn.senecacollege.ca/?new_loc=%2Fultra%2Finstitution-page'

# Navigate to School URL;  .get() method waits for page to load by default
driver.get(url)
# maximize browser window
driver.maximize_window()

# Accept privacy agreement
# wait until agree button is visible+clickable # can also combine --> wait.until(EC.element_to_be_clickable((By.ID,'agree_button'))).click()
wait.until(EC.element_to_be_clickable((By.ID, 'agree_button')))
# note: element_to_be_clickable() accepts 1 argument (a locator) that is a tuple of (by,path)
# click on agree button
driver.find_element(By.ID, 'agree_button').click()

wait.until(EC.element_to_be_clickable((By.ID, 'bottom_Submit')))
driver.find_element(By.ID, 'bottom_Submit').click()

# Click on input box and input username (school email)
wait.until(EC.element_to_be_clickable((By.ID, 'i0116')))
driver.find_element(By.ID, 'i0116').click()
wait.until(EC.element_to_be_clickable((By.ID, 'i0116')))
driver.find_element(By.ID, 'i0116').send_keys(
    username)

# click on Next button
wait.until(EC.element_to_be_clickable((By.ID, 'idSIButton9')))
driver.find_element(By.ID, 'idSIButton9').click()

# Input password
wait.until(EC.element_to_be_clickable((By.ID, 'i0118')))
driver.find_element(By.ID, 'i0118').click()
wait.until(EC.element_to_be_clickable((By.ID, 'i0118')))
driver.find_element(By.ID, 'i0118').send_keys(password)
wait.until(EC.element_to_be_clickable((By.ID, 'idSIButton9')))
driver.find_element(By.ID, 'idSIButton9').click()

# Choose microsoft authenticator for identity validation
wait.until(EC.element_to_be_clickable(
    (By.XPATH, '//*[@id="idDiv_SAOTCS_Proofs"]/div[1]/div/div/div[2]/div')))
driver.find_element(
    By.XPATH, '//*[@id="idDiv_SAOTCS_Proofs"]/div[1]/div/div/div[2]/div').click()
# wait for manual authentication on mobile app and redirection to the "Stay signed in?" page
wait.until(EC.element_to_be_clickable((By.ID, 'idSIButton9')))
# click 'Yes' when asked to stay signed in
driver.find_element(By.ID, 'idSIButton9').click()

# Click on 'Courses' to see list of all courses
wait.until(EC.element_to_be_clickable(
    (By.XPATH, '/html/body/div[1]/div[2]/bb-base-layout/div/aside/div[1]/nav/ul/bb-base-navigation-button[4]/div/li/a/ng-switch/div')))
driver.find_element(
    By.XPATH, '/html/body/div[1]/div[2]/bb-base-layout/div/aside/div[1]/nav/ul/bb-base-navigation-button[4]/div/li/a/ng-switch/div').click()

# COURSE 1
APS145 = Course('APS145')
# Navigate to APS course page, and then to the 'Grades' page
wait.until(EC.element_to_be_clickable(
    (By.XPATH, '//*[@id="course-link-_653591_1"]/h4')))
driver.find_element(By.XPATH, '//*[@id="course-link-_653591_1"]/h4').click()
wait.until(EC.frame_to_be_available_and_switch_to_it(
    (By.XPATH, '/html/body/div[1]/div[2]/bb-base-layout/div/main/div[3]/div/div[3]/div/div/div/div/div/iframe')))
wait.until(EC.element_to_be_clickable(
    (By.XPATH, '/html/body/div[2]/div[3]/nav/div/div[2]/div/div[2]/ul/li[6]/a')))
driver.find_element(
    By.XPATH, '/html/body/div[2]/div[3]/nav/div/div[2]/div/div[2]/ul/li[6]/a').click()

# Generate source html and pass to BeautifulSoup for parsing
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Define dictionary/list of repeated/single assignment types with corresponding assignment weight(%)
assignments = {'Workshops': 4.4, 'Quizzes': 10.0}
single_assignments = [('Presentation', 15.0), ('VRETTA', 15.0)]

# Calculate grades for repeated assignments (workshops and quizzes):
# 1) define a list of all instances of 'Workshop' text found in the HMTL source.
# 2) define optimized range for the list (range maximum = # of workshops). Need to reverse list since the generated source HTML is backwards
# 3) navigate to the div tag (parent tag) that represents the cell which contains the assignment grade and max assignment grade; the assignment grade and the max grade are numerical values in the form of a string within span tags. The string representing the max grade contains an unwanted '/' (e.g. '/10') that needs to be stripped
# 4) cast string values (assignment grade and max grade) to float values and calculate grade as percentage
# 5) add calculated assignment grade to course dictionary. add calculated weighted grade to overall course grade
for item in assignments.items():  # each item is a tuple ('Workshops', 4.4)
    numb = 1
    all_list = soup.find_all(text=re.compile(item[0]))
    text_list = all_list[1:7]
    for text in reversed(text_list):
        try:
            cell_parent = text.parent.parent.parent
            grade = cell_parent.find('div', class_='cell grade').find(
                'span', class_='grade').string
            max_grade = cell_parent.find('div', class_='cell grade').find(
                'span', class_='pointsPossible clearfloats').string.strip('/')
            calculated_grade = float(grade)/float(max_grade) * 100
        except ValueError:  # catch errors
            continue
        key = f'{item[0]} -#{numb}'
        weighted_grade = calc_weight_grade(calculated_grade, item[1])
        APS145.add_grade(key, calculated_grade, weighted_grade)
        APS145.add_to_overall_grade(weighted_grade)
        numb += 1

# Calculate Presentation grade
pres_grade = soup.find('div', id='3046743').find(
    'div', class_='cell grade').find('span', class_='grade').string
pres_max_grade = soup.find('div', id='3046743').find('div', class_='cell grade').find(
    'span', class_='pointsPossible clearfloats').string.strip('/')
pres_calculated_grade = float(pres_grade)/float(pres_max_grade) * 100
pres_weighted_grade = calc_weight_grade(
    pres_calculated_grade, single_assignments[0][1])
APS145.add_grade(single_assignments[0][0],
                 pres_calculated_grade, pres_weighted_grade)
APS145.add_to_overall_grade(pres_weighted_grade)


# Calculate VRETTA assignment grade
vretta_grade = 100.0
weighted_grade = calc_weight_grade(vretta_grade, single_assignments[1][1])
APS145.add_grade(single_assignments[1][0],
                 vretta_grade, weighted_grade)
APS145.add_to_overall_grade(weighted_grade)


# COURSE 2
IPC144 = Course('IPC144')
course2_url = 'https://learn.senecacollege.ca/ultra/courses/_653862_1/cl/outline'
driver.get(course2_url)
wait.until(EC.frame_to_be_available_and_switch_to_it(
    (By.XPATH, '/html/body/div[1]/div[2]/bb-base-layout/div/main/div[3]/div/div[3]/div/div/div/div/div/iframe')))
wait.until(EC.element_to_be_clickable(
    (By.XPATH, '/html/body/div[2]/div[3]/nav/div/div[2]/div/div[2]/ul/li[4]/a')))
driver.find_element(
    By.XPATH, '/html/body/div[2]/div[3]/nav/div/div[2]/div/div[2]/ul/li[4]/a').click()
wait.until(EC.presence_of_element_located(
    (By.XPATH, '/html/body/div[2]/div[3]/div/div/div/div/div[2]/div[1]/ul/li[2]/a')))


html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

assignments = {'reading-exercise': 1.1}
workshop_list = [('Workshops123', 1.0),
                 ('Workshops45', 2.0), ('Workshop6', 3.0)]  # workshops are weighted differently

for item in assignments.items():
    numb = 1
    all_list = soup.find_all(text=re.compile(item[0]))
    text_list = all_list[0:8]
    # for text in reversed(text_list):
    for text in text_list:
        try:
            cell_parent = text.parent.parent.parent
            grade = cell_parent.find('div', class_='cell grade').find(
                'span', class_='grade').string
            max_grade = cell_parent.find('div', class_='cell grade').find(
                'span', class_='pointsPossible clearfloats').string.strip('/')
            calculated_grade = float(grade)/float(max_grade) * 100
        except ValueError:  # catch errors
            continue
        key = f'{item[0]} -#{numb}'
        weighted_grade = calc_weight_grade(calculated_grade, item[1])
        IPC144.add_grade(key, calculated_grade, weighted_grade)
        IPC144.add_to_overall_grade(weighted_grade)
        numb += 1

# Add workshop grades
# list of div tag IDs housing each workshop grade
divID = [3068960, 3068962, 3068964, 3068966, 3068968]
numb = 1
for index, item in enumerate(divID):
    gradep1 = soup.find('div', id=f'{item}').find('div', class_='cell grade').find(
        'span', class_='grade').string
    item += 1
    gradep2 = soup.find('div', id=f'{item}').find('div', class_='cell grade').find(
        'span', class_='grade').string
    wsgrade = (((float(gradep1))+(float(gradep2)))/10) * 100
    key = f'Workshop-#{numb}'
    if index in range(0, 3):  # Workshop 1, 2, 3 (worth 1% each)
        weighted_grade = calc_weight_grade(wsgrade, workshop_list[0][1])
    elif index in range(3, 5):  # Workshop 4, 5 (worth 2% each)
        weighted_grade = calc_weight_grade(wsgrade, workshop_list[1][1])
    IPC144.add_grade(key, wsgrade, weighted_grade)
    IPC144.add_to_overall_grade(weighted_grade)
    numb += 1

# SUMMARY: Print out tables that represent each course and their assignment/grades
    # tabulate method accepts a list of lists as its argument wherein each nested list becomes a row in the table
    # dictionary .items method iterates over each key - value, value pair => returns 'key' : [value, value]
    # dictionary items to accomodate desired table formatting by concatenating the key in a list with its associated value (grade)) https://stackoverflow.com/questions/42235918/python-tabulate-dictionary-containing-two-values-per-key
    # output of table: ['WS1', 'grade', 'weight_grade']
for course in course_list:
    print(f'COURSE: {course.name}')
    headers = ['Assignment', 'Grade(%)', 'Weighted Grade(%)']
    table = [[key] + grade for key, grade in course.dict.items()]
    print(tabulate(table, headers=headers, tablefmt='fancy_grid'))
    print(f'OVERALL {course.name} GRADE (%): {course.overall_grade}\n\n')
