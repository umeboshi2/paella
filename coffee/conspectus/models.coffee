define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  MainBus = require 'msgbus'

  BaseLocalStorageModel = require 'common/localstoragemodel'
    
  ########################################
  # Models
  ########################################

  class AppSettings extends BaseLocalStorageModel
    id: 'app_settings'

  app_settings = new AppSettings
  MainBus.reqres.setHandler 'get_app_settings', ->
    app_settings
    
  class Page extends Backbone.Model
    validation:
      name:
        required: true
        
    
  module.exports =
    Page: Page
    
