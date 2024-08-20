from job_finder import *
import pytest

def test_clean_location():
    "tests the accuracy of the clean location function"
    assert clean_location('Berryville, VA 22611') == 'VA' # normal case
    assert clean_location("Clermont, FL") == 'FL' # second normal case
    assert clean_location('New York') == None # incorrect format case
    assert clean_location('Denver, Colorado, USA') == None # too many commas case
    assert clean_location('Rio, B') == None
    assert clean_location('Augustus, L@') == None
    assert clean_location("Orlando, Florida") == None # has comma but state is not an abbreviation
    assert clean_days("") == None # empty case
    print("all clean_function tests passed!")
test_clean_location()

def test_clean_days():
    "tests the accuracy of the clean days function"
    assert clean_days("Posted 18 days ago") == 18 # normal case
    assert clean_days("POSTED 7 DAYS AGO") == 7 # case sensitive case
    assert clean_days("Posted 100 days ago") == 100 # should return 100
    assert clean_days("Posted eight days ago") == None # number by not numeric
    assert clean_days("Posted -9 days ago") == None # negative number
    assert clean_days("Posted 6") == None # no days case
    assert clean_days("Posted days") == None # no number
    print("all clean_days tests passed!")
test_clean_days()

job_list1 = {'NY': 1, 'VA': 1, 'NC': 1, 'CA': 1, 'MD': 1, 'IL': 1, 'FL': 4, 'OH': 1, 'WA': 1, 'NV': 0}
job_list2 = {'AR': 1, 'WY': 2, 'IA': 1, 'FL': 7, 'N': 1, 'TX': 7}


opportunities_list1 = {'AZ': [1, 10, 3, 2,], 'IL': [1], 'FL': [7, 14, 2, 35, 6, 7], 'TX': [13, 45, 67, 8, 9]}
opportunities_list2 = {
    'AZ': [12, 24, 36], 
    'WA': [13, 65, 78, 32, 45], 
    'IL': [65, 33, 2, 78, 89, 5], 
    'FL': [2],
    'NC': [67],
    'TX': [43]}
opportunities_list3 = {'MT': [1]}
opportunities_list4 = {}

def test_most_opportunities():
    "tests the functionality of the most opportunites function"
    "NOTE: because number_of_opportunities_per_state is called with most opportunites, that function is also tested"
    assert most_opportunities(opportunities_list2) == 'IL' #normal case
    assert most_opportunities(opportunities_list1) == 'FL' or 'TX' #  tied case
    assert most_opportunities(opportunities_list3) == 'MT' # one state case
    with pytest.raises(TypeError): # the function takes in a with lists as the values, not int
        most_opportunities({job_list1})
    with pytest.raises(TypeError):
        most_opportunities({opportunities_list4})
    print("all most_opportunities tests passed!")
test_most_opportunities()

def test_jobs_in_given_state():
    "test the functionality of the jobs_in_given_states function "
    assert job_in_given_state("NC", job_list1) == 1 # normal case
    assert job_in_given_state("ca" ,job_list1) == 1 # lower case input
    with pytest.raises(NoStateError): # empty dictionary
       job_in_given_state("CA", job_list2)
    with pytest.raises(NoStateError): # state not in dictionary
       job_in_given_state("KS", job_list2)
    print("all jobs_in_given_state tests passed!")
test_jobs_in_given_state()

jobs1 = {
    'CA': [
        Job(10000, "Microsoft", "CA", 20, "Just a job that needs coding"), 
        Job(2000, "Apple", "CA", 3, "Want coding, customer service needed"),
        Job(30000, "Uber", "CA", None, "Looking for coding experience")
        ], 
    'FL': [
        Job(None, "Microsoft", "FL", None, "Perfect for new-grads!"), 
        Job(None, "Apple", "FL", None, "customer service needed"),
        Job(None, "Uber", "FL", None, "Looking for coding geniuses")
        ],
    'SC': [
        Job(50000, "Microsoft", "FL", None, None), 
        Job(2000, "Apple", "FL", None, None),
        Job(30000, "Uber", "FL", 2, None)
    ]


}
def test_most_recently_posted_in_state():
    "tests the accutacy of the most recently posted function"
    assert most_recently_posted_in_state(jobs1, "CA") == "Apple"
    assert most_recently_posted_in_state(jobs1, "SC") == "Uber"
    assert most_recently_posted_in_state(jobs1, "NY") == None  # Testing for a state not in the dictionary
    assert most_recently_posted_in_state({}, "CA") == None  # Testing for an empty dictionary
    assert most_recently_posted_in_state(jobs1, "FL") == None  # No jobs with 'days_since_posted' in FL
    assert most_recently_posted_in_state(jobs1, "NC") == None  # No jobs in NC
    assert most_recently_posted_in_state(jobs1, "TX") == None  # No 'days_since_posted' in TX
    print("all test_most_recently_posted_in_state tests passed")
test_most_recently_posted_in_state()

def test_highest_salary_in_given_state():
    "tests the accuracy of higheest salary in given state"
    assert highest_salary_in_given_state(jobs1, "CA") == "Uber"
    assert highest_salary_in_given_state(jobs1, "FL") == None
    assert highest_salary_in_given_state(jobs1, "SC") == "Microsoft"
    assert highest_salary_in_given_state(jobs1, "NY") == None  # Testing for a state not in the dictionary
    assert highest_salary_in_given_state({}, "CA") == None  # Testing for an empty dictionary
    assert highest_salary_in_given_state(jobs1, "FL") == None  # No salaries in FL
    assert highest_salary_in_given_state(jobs1, "NC") == None  # No jobs in NC
    assert highest_salary_in_given_state(jobs1, "TX") == None  # No salaries in TX
    print("all test_highest_salary tests passed!")
test_highest_salary_in_given_state()

def test_word_in_description():
    "tests the functionality of the word in description" 
    with pytest.raises(AttributeError): 
       word_in_description(jobs1, None)  
    assert word_in_description({}, "coding") == [] # empty dictionary
    assert len(word_in_description(jobs1, "coding")) == 4
    assert len(word_in_description(jobs1, "python")) == 0  # Assuming there are jobs with "python" in the description
    assert len(word_in_description(jobs1, "geniuses")) == 1  
    assert all("coding" in job.description.lower() for job in word_in_description(jobs1, "coding"))
    print("all tests word_in_description tests passed!")
test_word_in_description()


"""NOTE: there is no need to test a state without jobs case because the only states that are included in the dictionary are 
those that are present in the job_list, therefore a state without matching jobs would not be in the dictionary"""
    