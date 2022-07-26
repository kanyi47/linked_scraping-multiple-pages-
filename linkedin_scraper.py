from selenium.webdriver.common.keys import Keys
from parsel import Selector
from selenium.webdriver.common.by import By
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import numpy as np
import json

# saving the output to data.json
with open("data.json", "w") as f:
    json.dump([], f)


# open webdriver. You don't need to have it installed
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.maximize_window()
sleep(0.5)

# get the linkedin link
driver.get('https://www.linkedin.com')
sleep(2)

# click on the sign in button to input the username and password
driver.find_element(
    By.XPATH, '//a[@class="nav__button-secondary btn-md btn-secondary-emphasis"]').click()
sleep(2)

# find the xpath to the username field and input username. Same with password
username_input = driver.find_element(By.XPATH, '//input[@name="session_key"]')
username_input.send_keys('fgfds@gmail.com')
sleep(2)

password_input = driver.find_element(By.ID, 'password')
password_input.send_keys('45534uih')
sleep(2)

# find xpath to sign in button and click
driver.find_element(By.XPATH, '//div/button[text()="Sign in"]').click()
sleep(2)

# locate the search bar to perform profile search
search_input = driver.find_element(By.XPATH, '//input[@placeholder="Search"]')
sleep(1)

# input the search term
search_input.send_keys('software engineer')
search_input.send_keys(Keys.RETURN)
sleep(8)

# locate the people filter option to specify people only
driver.find_element(By.XPATH, '//button[text() = "People"]').click()
sleep(8)

# specify location as United States
driver.find_element(By.XPATH, '//button[text() = "Locations"]').click()
sleep(8)
location_input = driver.find_element(
    By.XPATH, '//input[@placeholder = "Add a location"]')
# you need to type Unied States first for you to get the drop down list specifying US
location_input.send_keys('United States')
location_input.send_keys(Keys.RETURN)
sleep(4)

# click on the US option and the click the apply filter button
driver.find_element(By.XPATH, '//span[text()="United States"]').click()
sleep(4)

driver.find_elements(
    By.XPATH, '//*[@aria-label="Apply current filter to show results"]')[1].click()
sleep(4)
pages = 0

# the while loop is used to loop over the pages. You can specify the number of pages you want scraped to stop the loop
while True:

    # we start with a function to write the data to json
    def write_json(new_data, filename='data.json'):
        with open(filename, 'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details
            file_data.append(new_data)
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent=4)

    pages = pages + 1  # update the page number everytime so we can stop the loop

    # we need to click each profile under the search results to collect the profile details.
    # However, once we have scraped all the profiles in first page, we need to go back to the profiles results page
    # so that the loop can take us to the next page. That's why we're saving the starting url
    starting_url = driver.current_url

# Get the xpath to each profile and then loop over all the profiles to collect profile data
    profiles = driver.find_elements(
        By.XPATH, '//div[@class="display-flex"]/span/span/a')
    profiles = [profile.get_attribute('href') for profile in profiles]
    for profile in profiles:
        driver.get(profile)
        sleep(4)
        # this helps us use xpath selectors to scrape data
        sel = Selector(text=driver.page_source)

# specify xpaths to the fields you need
        name = sel.xpath(
            '//title/text()').extract_first().split(' | ')[0].split(') ')[1]
        current_company = sel.xpath(
            '//a[@href = "#experience"]/h2/div/text()').extract_first()
        job_title = sel.xpath(
            '//*[@class="text-body-medium break-words"]/text()').extract_first()

        sleep(4)

        # for education, skills, and experience, if there are more than 3 datapoints, you have to click the "show more" link
        #  to access the entire collection. We need an if statement for this.

        # education, previous_companies, skills
        secondary_links = driver.find_elements(
            By.XPATH, '//div[contains (@class, "pvs-list__footer-wrapper")]/div/a')  # xpath to the sub-links
        secondary_links = [link.get_attribute(
            'href') for link in secondary_links]  # access the href to be able to click

        # education
        for link in secondary_links:
            if 'education' in link:  # visit the education section to scrape the data if the profile has more than three education data points
                driver.get(link)
                sleep(3)

                sel = Selector(driver.page_source)
                education = sel.xpath(
                    '//span[contains(@class, "mr1 hoverable-link-text t-bold")]/span[1]/text()').extract()
                education = np.array(education)
                education = np.unique(education).tolist()
                sleep(3)

                driver.find_element(
                    By.XPATH, '//*[@aria-label="Back to the main profile page"]').click()  # click the "back" button to go back to profile page
                sleep(3)

            else:
                # else collect the education datapoints specified in the profiles homepage
                sel = Selector(driver.page_source)
                education = sel.xpath(
                    '//span[contains(text(), "Education")]//following::div[1]/ul/li/div//child::span[contains(@class, "mr1 hoverable-link-text t-bold")]/span[1]/text()').extract()
                sleep(3)

            # skills
            if 'skills' in link:  # follows similar style to the education section
                driver.get(link)
                sleep(3)

                sel = Selector(driver.page_source)
                all_skills = sel.xpath(
                    '//span[contains(@class, "mr1 t-bold")]/span[1]/text()').extract()
                skills = np.array(all_skills)
                skills = np.unique(skills).tolist()
                sleep(4)

                driver.find_element(
                    By.XPATH, '//*[@aria-label="Back to the main profile page"]').click()
                sleep(2)

            else:
                sel = Selector(driver.page_source)
                skills = sel.xpath(
                    '//*[contains(text(), "Skills")][1]//following::div[1]//child::span[contains(@class, "mr1 t-bold")]/span[1]/text()').extract()
                sleep(3)

            # experience
            if 'experience' in link:
                driver.get(link)
                sleep(3)

                sel = Selector(driver.page_source)
                former_companies = sel.xpath(
                    '//span[@class="t-14 t-normal"]//child::span[1]/text()').extract()
                sleep(3)

                driver.find_element(
                    By.XPATH, '//*[@aria-label="Back to the main profile page"]').click()
                sleep(3)

            else:
                sel = Selector(driver.page_source)
                companies = sel.xpath(
                    '//span[contains(text(), "Full-time")]/text()')
                for company in companies:
                    former_companies = company.extract().split()[0]
                    sleep(3)
                    if former_companies == "Full-time":
                        sel = Selector(driver.page_source)
                        former_companies = sel.xpath(
                            '//a[@data-field="experience_company_logo"]//child::span[@class="mr1 hoverable-link-text t-bold"]/span[1]/text()')[1:].extract()
                    else:
                        former_companies = company.extract().split()[0]
        print('\n')
        print(name)
        print(current_company)
        print(former_companies)
        print(job_title)
        print(skills)
        print(education)
        print('\n')

        # specify the datapoints you need collected and saved to the output file
        write_json({'name': name, 'current_company': current_company, 'former_companies': former_companies,
                    'job_title': job_title, 'skills': skills, 'education': education})

# once all the profiles in the first page have been scraped, we need to go back to the results page so we can specify how to click the next page button
    driver.get(starting_url)

    # scroll down to make the "next page" code available
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    sleep(7)

    # click the next button to get the next page of profile results
    next_page = driver.find_element(By.XPATH, '//button[@aria-label="Next"]')
    next_page.click()
    sleep(6)
    if pages == 100:  # specify the maximum number of pages you want scraped.
        break

else:
    driver.quit()
