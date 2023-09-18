import pandas as pd
import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
def get_sitemap(url):
    """Scrapes an XML sitemap from the provided URL and returns XML source.

    Args:
        url (string): Fully qualified URL pointing to XML sitemap.

    Returns:
        xml (string): XML source of scraped sitemap.
    """

    response = urllib.request.urlopen(url)
    xml = BeautifulSoup(response, 
                         'lxml-xml', 
                         from_encoding=response.info().get_param('charset'))

    return xml
url = "https://vapetravellers.eu/sitemap.xml"
xml = get_sitemap(url)
def get_sitemap_type(xml):
    """Parse XML source and returns the type of sitemap.

    Args:
        xml (string): Source code of XML sitemap.

    Returns:
        sitemap_type (string): Type of sitemap (sitemap, sitemapindex, or None).
    """

    sitemapindex = xml.find_all('sitemapindex')
    sitemap = xml.find_all('urlset')

    if sitemapindex:
        return 'sitemapindex'
    elif sitemap:
        return 'urlset'
    else:
        return
def get_child_sitemaps(xml):
    """Return a list of child sitemaps present in a XML sitemap file.

    Args:
        xml (string): XML source of sitemap. 

    Returns:
        sitemaps (list): Python list of XML sitemap URLs.
    """

    sitemaps = xml.find_all("sitemap")

    output = []

    for sitemap in sitemaps:
        output.append(sitemap.findNext("loc").text)
    return output
def sitemap_to_dataframe(xml, name=None, data=None, verbose=False):
    """Read an XML sitemap into a Pandas dataframe. 

    Args:
        xml (string): XML source of sitemap. 
        name (optional): Optional name for sitemap parsed.
        verbose (boolean, optional): Set to True to monitor progress.

    Returns:
        dataframe: Pandas dataframe of XML sitemap content. 
    """

    df = pd.DataFrame(columns=['loc', 'changefreq', 'priority', 'domain', 'sitemap_name'])

    urls = xml.find_all("url")
  
    for url in urls:

        if xml.find("loc"):
            loc = url.findNext("loc").text
            parsed_uri = urlparse(loc)
            domain = '{uri.netloc}'.format(uri=parsed_uri)
        else:
            loc = ''
            domain = ''

        if xml.find("changefreq"):
            changefreq = url.findNext("changefreq").text
        else:
            changefreq = ''

        if xml.find("priority"):
            priority = url.findNext("priority").text
        else:
            priority = ''

        if name:
            sitemap_name = name
        else:
            sitemap_name = ''
              
        row = {
            'domain': domain,
            'loc': loc,
            'changefreq': changefreq,
            'priority': priority,
            'sitemap_name': sitemap_name,
        }

        if verbose:
            print(row)

        df = df.append(row, ignore_index=True)
    return df
def get_all_urls(url):
    """Return a dataframe containing all of the URLs from a site's XML sitemaps.

    Args:
        url (string): URL of site's XML sitemap. Usually located at /sitemap.xml

    Returns:
        df (dataframe): Pandas dataframe containing all sitemap content. 

    """


    xml = get_sitemap(url)
    sitemap_type = get_sitemap_type(xml)

    if sitemap_type =='sitemapindex':
        sitemaps = get_child_sitemaps(xml)
    else:
        sitemaps = [url]

    df = pd.DataFrame(columns=['loc', 'changefreq', 'priority', 'domain', 'sitemap_name'])

    for sitemap in sitemaps:
        sitemap_xml = get_sitemap(sitemap)
        df_sitemap = sitemap_to_dataframe(sitemap_xml, name=sitemap)

        df = pd.concat([df, df_sitemap], ignore_index=True)

    return df
