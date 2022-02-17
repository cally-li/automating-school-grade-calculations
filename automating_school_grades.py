# Dynamic scraping: Selenium is used to automate web browser interaction (logging in) and Beautiful Soup is used to scrape grades https://medium.com/ymedialabs-innovation/web-scraping-using-beautiful-soup-and-selenium-for-dynamic-page-2f8ad15efe25

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
from tabulate import tabulate

s=Service('/Users/callyli/Documents/chromedriver') #path of chromedriver on OS. chromeDriver is a separate executable that Selenium WebDriver uses to control Chrome; https://stackoverflow.com/questions/64717302/deprecationwarning-executable-path-has-been-deprecated-selenium-python
driver = webdriver.Chrome(service=s)  #define an object for using webdriver function with the chrome webdriver located at inserted path

wait = WebDriverWait(driver,20) #initialize object for using WebDriverWait class with 2 arguments: driver object and max timeout in seconds
username = '***************' 
password = '***************'
url = 'https://learn.senecacollege.ca/?new_loc=%2Fultra%2Finstitution-page'

#Navigate to School URL
driver.get(url)     #navigate to school URL #.get() method will wait for page to load by default
driver.maximize_window() # maximize the browser window

#Accept privacy agreement
wait.until(EC.element_to_be_clickable((By.ID,'agree_button'))) #wait until agree button is visible+clickable # can also combine --> wait.until(EC.element_to_be_clickable((By.ID,'agree_button'))).click()
    #note: element_to_be_clickable() accepts 1 argument (locator) that is a tuple of (by,path)
driver.find_element(By.ID,'agree_button').click() #click on agree button 

wait.until(EC.element_to_be_clickable((By.ID,'bottom_Submit')))
driver.find_element(By.ID,'bottom_Submit').click() 

#Enter username (school email)
wait.until(EC.element_to_be_clickable((By.ID,'i0116')))
driver.find_element(By.ID,'i0116').click() #click on input box

wait.until(EC.element_to_be_clickable((By.ID,'i0116')))
driver.find_element(By.ID,'i0116').send_keys(username) #inputs school email into sign in box

wait.until(EC.element_to_be_clickable((By.ID,'idSIButton9')))
driver.find_element(By.ID,'idSIButton9').click() #click on Next button

#Enter password
wait.until(EC.element_to_be_clickable((By.ID,'i0118')))
driver.find_element(By.ID,'i0118').click() 

wait.until(EC.element_to_be_clickable((By.ID,'i0118')))
driver.find_element(By.ID,'i0118').send_keys(password)

wait.until(EC.element_to_be_clickable((By.ID,'idSIButton9')))
driver.find_element(By.ID,'idSIButton9').click()

#Choose microsoft authenticator for identity validation
wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="idDiv_SAOTCS_Proofs"]/div[1]/div/div/div[2]/div')))
driver.find_element(By.XPATH,'//*[@id="idDiv_SAOTCS_Proofs"]/div[1]/div/div/div[2]/div').click() #click on 'Microsoft Authenticator' option
 #wait for manual authentication on mobile app and subsequent redirection to the "Stay signed in?" page
wait.until(EC.element_to_be_clickable((By.ID,'idSIButton9')))
driver.find_element(By.ID,'idSIButton9').click() #click 'Yes' when asked to stay signed in

#Click on Courses to see list of all courses
wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[1]/div[2]/bb-base-layout/div/aside/div[1]/nav/ul/bb-base-navigation-button[4]/div/li/a/ng-switch/div')))
driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/bb-base-layout/div/aside/div[1]/nav/ul/bb-base-navigation-button[4]/div/li/a/ng-switch/div').click()

#Go to APS145 course page
wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="course-link-_653591_1"]/h4')))
driver.find_element(By.XPATH,'//*[@id="course-link-_653591_1"]/h4').click()

#Go to 'My Grades' page of APS course
wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,'/html/body/div[1]/div[2]/bb-base-layout/div/main/div[3]/div/div[3]/div/div/div/div/div/iframe'))) #'My Grades' is embedded within an iframe. Need to switch from parent frame to iframe to access the element. Locating by full XPATH seems to work the best here. https://stackoverflow.com/questions/53203417/ways-to-deal-with-document-under-iframe https://stackoverflow.com/questions/7534622/select-iframe-using-python-selenium/24286392#24286392
wait.until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[2]/div[3]/nav/div/div[2]/div/div[2]/ul/li[6]/a'))) #full XPATH of href anchor
driver.find_element(By.XPATH,'/html/body/div[2]/div[3]/nav/div/div[2]/div/div[2]/ul/li[6]/a').click()

html = driver.page_source #page_source attribute is used to store the source HTML of 'My Grades' page. This is to be loaded into BS

#Pass source HTML into bs4. create bs4 object of parsed html
soup = BeautifulSoup(html, 'html.parser') #lxml and html5lib are also available 

APS_dict={} #define empty dictionary to house all APS grades
course_grade=0
def add_to_dict(dict_key, grade, weight_grade):   #define function to add grade and weighted grade to dictionary
    APS_dict[dict_key]= [round(grade,2), round(weight_grade,2)]

def calc_weight_grade(grade,weight):       #define function to calculate weighted grade
    weighted_grade=(grade/100)*weight
    return weighted_grade

#Calculate grades for workshops. Loop through each workshop cell and caluclate grade
text_list = soup.find_all(text=re.compile('Workshops'))    # define a list of all instances of 'Workshop' text found in the HMTL source. re.compile(regular expressions) used to search for the exact specific pattern we want (avoid whitespaces that are a part of the tag strings)
ws_text_list= text_list[1:6] #define a list with only elements of index 1-5 (workshop 1 to workshop 5)
ws_numb=1
for ws_text in reversed(ws_text_list):   # need to reverse list because source HTML stored by Selenium is reversed 
    ws_cell_parent= ws_text.parent.parent.parent #navigate to the parent tag of the text iterable, then to their parent, then to their parent
    ws_grade_div= ws_cell_parent.find('div', class_='cell grade')# within cell parent, find div with class=cellgrade
    ws_grade_span= ws_grade_div.find('span', class_='grade') # within above div tag (class=cellgrade), find span tag with class=grade
    ws_grade=ws_grade_span.string #since above span tag only has one child (the value of the grade as a navigable string), we can use .string attribute
    ws_max_grade_span= ws_grade_div.find('span', class_='pointsPossible clearfloats') #find span tag containing the max grade possible for this assignment
    ws_max_grade_out_of = ws_max_grade_span.string #Note: the string within the span tag has an unwanted fowardslash in front of the value (e.g., '/10')
    ws_max_grade = ws_max_grade_out_of.strip('/') # remove the '/' from above string. Note: .strip attribute only removes leading and traililng characters
    ws_calculated_grade= float(ws_grade)/float(ws_max_grade) * 100 #cast string values to float and calculate grade as percentage
    ws_key = f'WS{ws_numb}'
    ws_weighted_grade=calc_weight_grade(ws_calculated_grade, 4.4)
    add_to_dict(ws_key,ws_calculated_grade, ws_weighted_grade)
    course_grade+=ws_weighted_grade
    ws_numb+=1

#Calculate grade for quizzes
qzall_text_list = soup.find_all(text=re.compile('Quizzes'))    
qz_text_list= qzall_text_list[1:] #define a list with only elements of index 1 to the end (quiz 1 to...)
qz_numb=1
for qz_text in reversed(qz_text_list):
    qz_cell_parent= qz_text.parent.parent.parent 
    qz_grade_div= qz_cell_parent.find('div', class_='cell grade')
    qz_grade_span= qz_grade_div.find('span', class_='grade')
    qz_grade=qz_grade_span.string 
    qz_max_grade_span= qz_grade_div.find('span', class_='pointsPossible clearfloats')
    qz_max_grade_out_of = qz_max_grade_span.string
    qz_max_grade = qz_max_grade_out_of.strip('/')
    qz_calculated_grade= float(qz_grade)/float(qz_max_grade) * 100 
    qz_key = f'Quiz {qz_numb}'
    qz_weighted_grade=calc_weight_grade(qz_calculated_grade, 10.0)
    add_to_dict(qz_key,qz_calculated_grade, qz_weighted_grade)
    course_grade+=qz_weighted_grade
    qz_numb+=1

#Calculate grade for presentation (only 1 presentation)
pres_div_parent = soup.find('div', id='3046743')
pres_div = pres_div_parent.find('div', class_='cell grade')
pres_span = pres_div.find('span', class_='grade')
pres_grade = pres_span.string
pres_max_grade_span= pres_div.find('span', class_='pointsPossible clearfloats') 
pres_max_grade_out_of = pres_max_grade_span.string 
pres_max_grade = pres_max_grade_out_of.strip('/')
pres_calculated_grade= float(pres_grade)/float(pres_max_grade) * 100 
pres_weighted_grade=calc_weight_grade(pres_calculated_grade, 15.0)
add_to_dict('Presentation',pres_calculated_grade, pres_weighted_grade)
course_grade+=pres_weighted_grade

#Add VRETTA assignment grade to course grade
vretta_grade=100.0
vretta_weighted_grade=15.0
add_to_dict('VRETTA', vretta_grade, vretta_weighted_grade)
course_grade+=vretta_weighted_grade


#Print out grades into a table
headers= ['Assignment', 'Grade(%)', 'Weighted Grade(%)']
print(tabulate([[dict_key,] + grade for dict_key, grade in APS_dict.items()], headers=headers, tablefmt='fancy_grid')) 
# tabulate method accepts a list of lists as the argument. each list is a row in the table
# dictionary's .items method iterates over each key + value pair => Example: WS1 ['grade', 'weighted grade']
# Need to flatten dictionary items to accommodate desired table formatting (above, we're concatenating the key in a list with its associated grade (value)) https://stackoverflow.com/questions/42235918/python-tabulate-dictionary-containing-two-values-per-key

print(f'COURSE GRADE (%): {course_grade}')