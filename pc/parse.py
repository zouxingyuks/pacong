from bs4 import BeautifulSoup

basic_url = "https://www.zhipin.com"

def parse_job_cards(soup):
    job_cards = []

    job_card = soup.find("li", class_="job-card-wrapper")
    while job_card:
        job = {}

        job_link = job_card.find("a", class_="job-card-left")
        job["job_link"] = basic_url + job_link["href"]

        job_name = job_card.find("span", class_="job-name")
        job["job_name"] = job_name.text if job_name else ""

        location = job_card.find("span", class_="job-area").text
        job["location"] = location

        salary = job_card.find("span", class_="salary").text
        job["salary"] = salary

        job_tags = job_card.select("ul.tag-list > li")
        job_tags = ",".join([tag.text for tag in job_tags if tag.text.strip()])
        job["job_tags"] = job_tags

        company = job_card.find("h3", class_="company-name").text
        job["company"] = company.strip()

        job_cards.append(job)
        job_card = job_card.find_next("li", class_="job-card-wrapper")

    return job_cards
