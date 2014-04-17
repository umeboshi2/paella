define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  ########################################
  # Models
  ########################################

  class RssFeed extends Backbone.Model
    defaults:
      name: 'No RSS'
      url: '#'
    url: '/rest/simplerss/feeds'
    validation:
      name:
        required: true
      url:
        required: true
        
  class RssData extends Backbone.Model
    url: () ->
      '/rest/simplerss/feeds/' + @id + '/feeddata'
          
  module.exports =
    RssFeed: RssFeed
    RssData: RssData

