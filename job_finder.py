from bs4 import BeautifulSoup
from collections import Counter
from nltk.stem import PorterStemmer
import requests

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def get_driver():
    """Change only if you are using a different browser. Default on the stencil is google chrome."""
    service = ChromeService(ChromeDriverManager().install())
    return webdriver.Chrome(service=service)



def user_input_cleaner(user_input: str) -> str:
    "alters the user input so that the input can be searched on indeed"
    return user_input.replace(' ', "%20")

def get_opportunities(job_input: str, driver: webdriver):
    """Returns a BeautifulSoup object for a given city from Indeed"""
    proper_input = user_input_cleaner(job_input) # turns the input into a something usuable for the link
    url = f"https://www.indeed.com/jobs?q={proper_input}&l=&from=searchOnHP"
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "result-title"))
        )
    except Exception as e:
        print("Exception while waiting for page elements:", e)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup

driver = get_driver()

class Job:
    def __init__(self, average_salary, company, location, days_since_posted, description):
        self.average_salary = average_salary
        self.company = company
        self.location = location
        self.days_since_posted = days_since_posted
        self.description = description

class NoStateError(Exception):
    pass

        
def get_salary_range(jobs) -> str:
    "scrapes and formats salary range"
    for job in jobs: 
        salary_range = job.find("div", class_ = "metadata salary-snippet-container")
        if salary_range:
            salary_format = salary_range.text.strip()
            if salary_format:
                cleaned_salary = salary_format.replace('a year', '').replace('$',"").replace(",", "")
                return cleaned_salary.strip()
    return None

def clean_salary(range: str) -> float:
    "cleans the salary range and returns the average salary"
    list_of_nums = range.replace(" ", "").split("-")
    if len(list_of_nums) == 2:
        lowest = (list_of_nums[0])
        highest = (list_of_nums[1])
        if (highest.isnumeric()) and (lowest.isnumeric()):
            return (float(highest)+float(lowest))/2
    else:
        return None


def get_company(jobs) -> str:
    "scrapes company name"
    for job in jobs:
        company_name = job.find("span", attrs={'data-testid': "company-name"})
        if company_name:
            company_format = company_name.text.strip()
            return company_format
    return None
        

def get_location(jobs) -> str:
    "scrapes job location"
    for job in jobs:
        location_info = job.find("div", attrs={'data-testid': "text-location"})
        if location_info: 
            text = location_info.text.strip()
            return text
    return None

def clean_location(location: str):
    "takes the original location input and cleans it just for the state abbreviation"
    if "," in location:
        broken_down = location.split(",")
        state = broken_down[1].strip().split()[0]
        if len(state) == 2 and state.isalpha():
            return str(state)
    return None


def get_days_since_posted(jobs) -> str:
    "scrapes for the amount of days since the job was posted"
    for job in jobs:
        days_since_posted_info = job.find("span", class_ = "date")
        if days_since_posted_info:
            days = days_since_posted_info.text.strip()
            return days
    return None

def clean_days(days_input: str) -> int:
    "takes the original day input and cleans it so it is just the number of days"
    for_use = days_input.lower().strip()
    if ("days" in for_use) and ("posted" in for_use):
        days = for_use.split()[1]
        if days == "today":
            days == 0
        if (days.isnumeric()) and (int(days) > 0):
            return int(days)
    else:
        return None


def get_job_url(link: str, driver: webdriver):
    "allows us to get data from the single job url"
    driver.get(link)
    single_job = BeautifulSoup(driver.page_source, 'html.parser')
    return single_job

def get_description(single_job) -> str:
    "gets descriptions from a single job listing webpage"
    all_text = single_job.get_text().strip()
    return all_text

 

def scrape_data(soup: BeautifulSoup):
    job_list = {}
    opportunities = []
    listings_in_opportunities = soup.find_all("li", class_ = "css-5lfssm eu4oa1w0")
    if not listings_in_opportunities:
        print("No elements found!")
    else:
        for job in listings_in_opportunities:
            average_salary = get_salary_range(job)
            company = get_company(job)
            location = get_location(job)
            days_since_posted = get_days_since_posted(job)
            job_link = job.find('a', class_ = "jcs-JobTitle css-jspxzf eu4oa1w0")
            
            if job_link:
                content = job_link['href']
                actual_url = (("https://www.indeed.com")+ (content))
                single_job_info = get_job_url(actual_url, get_driver())
                description = get_description(single_job_info)


                if (average_salary) and (days_since_posted): 
                    job_data = Job(
                        average_salary = clean_salary(average_salary),
                        company = company,
                        location = clean_location(location),
                        days_since_posted = clean_days(days_since_posted),
                        description = description
                    )
                    opportunities.append(job_data)

                for role in opportunities:
                    if role.location: 
                        if role.location not in job_list:
                            job_list[role.location] = set()
                        job_list[role.location].add(role)
    return job_list

def number_of_opportunities_per_state(job_list: dict) -> dict:
    "takes a job list (dict) organized by state and returns the number of opportunities in each included state"
    state_opportunity_count = {}
    for state in job_list.keys():
        if state not in state_opportunity_count:
            state_opportunity_count[state] = len(job_list[state])
    return state_opportunity_count

def job_in_given_state(state: str, job_dict: dict) -> int:
    "returns the number of jobs in a specific state"
    state = state.upper()
    if state in job_dict.keys():
        return job_dict[state]
    else:
        raise NoStateError


def most_opportunities(job_list: dict) -> str:
    "takes in a dictionary with list of jobs organized by state and returns the state with most job available" 
    count_dict = number_of_opportunities_per_state(job_list)
    state_w_most = max(count_dict, key=count_dict.get)
    return state_w_most



def most_recently_posted_in_state(job_dict: dict, state: str) -> Job:
    "takes is a dictionary with job opportunities and find the one that was most recently posted"
    most_recent_job = None
    minimum_days = 364
    state = state.upper()
    if state in job_dict.keys():
        for job in job_dict[state]:
            if job.days_since_posted is not None:
                if job.days_since_posted < minimum_days:
                    minimum_days = job.days_since_posted
                    most_recent_job = job.company
        return most_recent_job


def highest_salary_in_given_state(job_dict: dict, state: str) -> Job:
    "takes a dictionary with jobs and find the one with the highest average salary"
    highest_salary = 0
    highest_paying_job = None
    state = state.upper()
    if state in job_dict.keys():
        for job in job_dict[state]:
            if job.average_salary is not None:
                if job.average_salary > highest_salary:
                    highest_salary = job.average_salary
                    highest_paying_job = job.company
        return highest_paying_job

def word_in_description(job_dict: dict, word: str) -> list:
    'searches an each job description for a word and reutrn a list of all the job with that in the description'
    job_w_word = []
    for state, job_list in job_dict.items():
        for job in job_list:
            if job.description is not None:
                if word.lower() in job.description.lower():
                    job_w_word.append(job)
    return job_w_word


teach = get_opportunities("teacher", driver)
