define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  BaseLocalStorageModel = require 'common/localstoragemodel'
    
  ########################################
  # Models
  ########################################
  class BumblrSettings extends BaseLocalStorageModel
    id: 'bumblr_settings'

  #bumblr_settings = new BumblrSettings id:'bumblr'
  consumer_key = '4mhV8B1YQK6PUA2NW8eZZXVHjU55TPJ3UZnZGrbSoCnqJaxDyH'
  bumblr_settings = new BumblrSettings consumer_key:consumer_key
  MSGBUS.reqres.setHandler 'bumblr:get_app_settings', ->
    bumblr_settings
      
  module.exports = null
