from newspaper import Article

url = 'https://infoweb.newsbank.com/apps/news/document-view?p=WORLDNEWS&t=country%3AUSA%21USA/stp%3AWeb-Only%2BSource%21Web-Only%2BSource/continent%3ANorth%2BAmerica%21North%2BAmerica/city%3AChicago%2B%2528IL%2529%21Chicago%2B%2528IL%2529/language%3AEnglish%21English&sort=YMD_date%3AD&hide_duplicates=2&maxresults=60&f=advanced&val-base-0=immigration&fld-base-0=alltext&bln-base-2=or&val-base-2=alltextkeyword2&fld-base-2=alltext&bln-base-3=or&val-base-3=headlinekeyword2&fld-base-3=Title&fld-nav-0=YMD_date&val-nav-0=2016%20-%202025&docref=news/19FA21E2085AE2B0'
article = Article(url)
article.download()

article.parse()

print(article.authors)

print(article.publish_date)

print(article.text)

print(article.top_image)

print(article)