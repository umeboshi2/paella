define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  
  { User, Group, RssFeed,
  RssData } = require 'models'
  MSGBUS = require 'msgbus'
      

  ########################################
  # Collections
  ########################################
  class BaseCollection extends Backbone.Collection
    # wrap the parsing to retrieve the
    # 'data' attribute from the json response
    parse: (response) ->
      return response.data

  class RssFeedList extends BaseCollection
    model: RssFeed
    url: '/rest/simplerss/feeds'

  class RssDataList extends BaseCollection
    model: RssData
    
  # set handlers on message bus
  #
  main_feed_list = new RssFeedList
  MSGBUS.reqres.setHandler 'rss:feedlist', ->
    main_feed_list

  MSGBUS.reqres.setHandler 'rss:getfeedinfo', (feed_id) ->
    console.log 'handle rss:getfeedinfo ' + feed_id
    main_feed_list.get feed_id
    

  main_data_list = new RssDataList
  
  
  MSGBUS.reqres.setHandler 'rss:feeddata', (feed_id) ->
    console.log 'handle rss:feeddata ' + feed_id
    model = main_data_list.get feed_id
    if model == undefined
      model = new RssData
        id: feed_id
      main_data_list.add model
    else
      model
      
  
  module.exports =
    RssFeedList: RssFeedList
    