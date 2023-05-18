from bs4 import BeautifulSoup

basic_url = "https://www.zhipin.com"


def parse_job_cards(soup):
    job_cards = []

    job_card = soup.find("li", class_="job-card-wrapper")
    while job_card:
        job = {}

        # 详情链接
        job_link = job_card.find("a", class_="job-card-left")
        # 此处做了拼接,拼接源地址和二级地址
        job["job_link"] = basic_url + job_link["href"]

        # 职位名称
        job_name = job_card.find("span", class_="job-name")
        if job_name:
            job["job_name"] = job_name.text
        else:
            job["job_name"] = ""  # 默认值

        # 地点
        location = job_card.find("span", class_="job-area").text
        job["location"] = location

        # 薪资
        salary = job_card.find("span", class_="salary").text
        job["salary"] = salary

        #  tags
        job_tags = job_card.find_all("ul", class_="tag-list")
        job_tags = ",".join([tag.text for tag in job_tags])
        job["job_tags"] = job_tags

        # 公司
        company = job_card.find("h3", class_="company-name").text
        job["company"] = company

        # 查找下一个 job_card
        job_cards.append(job)
        job_card = job_card.find_next("li", class_="job-card-wrapper")

    return job_cards
