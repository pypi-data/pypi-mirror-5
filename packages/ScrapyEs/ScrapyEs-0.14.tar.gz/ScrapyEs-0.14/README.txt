###scrapy-elasticsearch-extension

A Scrapy Extension to bulk export data to elasticsearch

###required modules

[pyes](http://pyes.readthedocs.org/en/latest/)


###installation

generaly information to be found in the [Scrapy Extensions installation guide](http://doc.scrapy.org/en/latest/topics/extensions.html)

add the following line to the **EXTENSIONS** setting in your Scrapy settings:

```
  'scrapyes.Sender' : 1000
```

###configuration

the module can be configured per project in your Scrapy settings using the following options:

```
  ELASTICSEARCH_SERVER = "localhost"
  ELASTICSEARCH_PORT = 9200
  ELASTICSEARCH_INDEX = "sixx"
  ELASTICSEARCH_TYPE = "text"
  ELASTICSEARCH_BULK_SIZE = 10
```

### index configuration

the index used in Elastic Search insertion can be configured per spider [by initializing an attribute on the spider](http://doc.scrapy.org/en/latest/topics/spiders.html#spider-arguments), named index, and passing the desired value when the spider
job is scheduled.
example:
```
  curl http://192.168.33.10:6800/schedule.json -d project=psd_search_crawler  \
  -d spider=sixx_spider \
  -d index=my_index

```
if the index is not configured on the running spider, the crawler settings value for variable **ELASTICSEARCH_INDEX** will be used.

the default value for index is the value of the **BOT_NAME** variable
