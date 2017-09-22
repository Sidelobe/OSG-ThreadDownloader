import requests
from bs4 import BeautifulSoup
import urllib2
import re
import math

#########
# forum Settings
posts_per_page = 15

# Get all images from a thread (even if it's on multiple pages)

def buildUrl(topic_id, start_post):
    return 'http://www.offsetguitars.com/forums/viewtopic.php?f=8&t=' + str(topic_id) + "&start=" + str(start_post)

def main():

    # topic_id = 12121
    topic_id = 33329  # motorikII

    soup = aggregate_all_posts(topic_id)

    # replace Avatars with default avatar image
    for avatar_img_tag in soup.find_all('img', {'alt': r'User avatar'}):
        del avatar_img_tag['height']
        del avatar_img_tag['width']
        avatar_img_tag['src'] = "avatar_placeholder.gif"


    with open("output_allpages.html", "w") as file:
        file.write(str(soup.prettify('utf-8')))


def aggregate_all_posts(topic_id):

    basepage_soup, number_of_posts, number_of_pages = prefetch_post(topic_id)

    postClass = re.compile(r"post (bg1|bg2)")

    # hollow out the page (remove all post divs)
    isFirstPost = True
    for divider in basepage_soup.findAll('hr', {'class': 'divider'}):
        if isFirstPost:
            first_post = divider.findPrevious('div', {'class': postClass})
            first_post['placeholder'] = "FIRST_POST_PLACEHOLDER"
            isFirstPost = False

        post_div = divider.findNext('div').extract() # remove post
        divider.extract()   # remove divider

    # DEBUG output
    #with open("output_base.html", "w") as file:
    #    file.write(str(bSoup.prettify('utf-8')))

    ##########
    post_divs = fetch_all_posts(number_of_pages, postClass, topic_id)

    # create a list with divider tags
    post_tags = list()
    for i in range(0, len(post_divs)):
        post_tags.append(createDividerTag(basepage_soup))

    #interleave the two lists
    divided_post_list = [val for pair in zip(post_divs, post_tags) for val in pair]

    # find first post in Base Soup and start appending
    first_post = basepage_soup.find('div', {'placeholder': 'FIRST_POST_PLACEHOLDER'})
    divider_tag = createDividerTag(basepage_soup)
    first_post.insert_after(divider_tag)
    cursor = divider_tag

    for tag in divided_post_list:
        cursor.insert_after(tag)
        cursor = tag

    return basepage_soup

def createDividerTag(bSoup):
    divider_tag = bSoup.new_tag('hr')
    divider_tag.attrs['class'] = 'divider'
    return divider_tag

def prefetch_post(topic_id):
    """ Fetch first page to obtain HTML code of page - everything without the posts themselves -
        and information such as number of pages """
    url = buildUrl(topic_id, 0)
    content = urllib2.urlopen(url).read()
    basepage_soup = BeautifulSoup(content, "lxml")
    number_of_posts_raw = basepage_soup.findAll('div', {'class': 'pagination'})
    number_of_posts = re.search('\d+', number_of_posts_raw[0].text).group(0)
    number_of_pages = int(math.ceil(float(number_of_posts) / posts_per_page))
    return basepage_soup, number_of_posts, number_of_pages

def fetch_all_posts(number_of_pages, postClass, topic_id):
    # Gather all the posts on all pages of thread
    unique_images = set()
    post_divs = list()
    for page_idx in range(0, number_of_pages):
        url = buildUrl(topic_id, page_idx * posts_per_page)
        content = urllib2.urlopen(url).read()
        soup = BeautifulSoup(content, "lxml")

        for post_div in soup.find_all('div', {'class': postClass}):
            post_divs.append(post_div)

        # Gather all images in posts
        for post in soup.find_all('div', {'class': 'content'}):
            for img in post.find_all('img'):
                # print(img.get('src'))
                pass  # unique_images.add(img.get('src'))

    return post_divs

if __name__ == "__main__":
    main()