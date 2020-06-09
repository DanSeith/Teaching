from selenium import webdriver
import slack
import os
import time
import datetime as dt
import sys


def get_class_size(driver):
    # This function serves to iterate through all rows to find the size of a class
    rows = driver.find_elements_by_tag_name("tr")
    size = (len(rows)-1)/2
    return int(size)


def check_sapling(driver, section, column, min_grade, slack_address):
    # Select each class, find students with incomplete assignments
    class_one = driver.find_element_by_xpath("//option[contains(text(), '%s')]" % section)
    class_one.click()

    # Find total number of people
    class_total = get_class_size(driver)
    names_list = []
    # Iterate through table, append specific values to list
    grade_list = []
    for student in range(1, class_total):
        student_grade = driver.find_element_by_xpath(
            '//*[@id="user-grades"]/tbody/tr[%s]/td[%s]' % (student, column+1))
        grade = student_grade.text.split('%')[0]

        # If no attempt was made, there will be a dash in place of a student's grade, which cannot be typecasted to
        # a float
        try:
            if float(grade) < min_grade:
                names_list.append(student_grade.get_attribute('title').split('-')[0])
                grade_list.append(grade)
        except ValueError:
            names_list.append(student_grade.get_attribute('title').split('-')[0])
            grade_list.append(grade)
    # Assign token
    sbot_token = os.environ['SLACK_BOT_TOKEN'] = 'token'
    client = slack.WebClient(token=sbot_token)
    # Send list of delinquent students
    for x in range(len(names_list)):

        message = "Name: " + names_list[x] + ' Section: ' + str(section) + ' Score: ' + grade_list[x]

        # Slack relevant head TA
        client.chat_postMessage(channel=slack_address, text=message)

        # Send message to head TAs to maintain oversight
        client.chat_postMessage(channel="@ta1", text=message)

        client.chat_postMessage(channel="@ta2", text=message)

        client.chat_postMessage(channel="@ta3", text=message)


ta_dict = {11111: '@ta_slack_address', 11112: '@ta_slack_address_2'}

# Use chrome
driver = webdriver.Chrome('/path/to/chromedriver')

driver.get("https://www.saplinglearning.com/ibiscms/login/")

# Select the username id_box
id_box = driver.find_element_by_name('username')

# Send id information
id_box.send_keys('email@domain.com')

# Select the password id_box
pass_box = driver.find_element_by_name('password')

# Send password information
pass_box.send_keys('password123')

# Find login button
login_button = driver.find_element_by_id('submitButton')

# Click login
login_button.click()

# h4courseTitle
current_class = driver.find_element_by_class_name('h4courseTitle')

# Click current_class
current_class.click()

# Click on grades icon
grades_link = driver.find_element_by_link_text('Grades')
grades_link.click()

# Iterate over list of sapling assignments to grade
for assignment in [1, 2]:
    for section in ta_dict: 
        check_sapling(driver, section, column=assignment, min_grade=70, slack_address=ta_dict[section])

driver.quit()
