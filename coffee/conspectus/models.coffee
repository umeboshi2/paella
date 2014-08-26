define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  MSGBUS = require 'msgbus'
  
  ########################################
  # Models
  ########################################

  class BaseLocalStorageModel extends Backbone.Model
    initialize: () ->
      @fetch()
      @on 'change', @save, @

    fetch: () ->
      console.log '===== FETCH FIRED LOADING LOCAL STORAGE ===='
      @set JSON.parse localStorage.getItem @id

    save: (attributes) ->
      console.log '===== CHANGE FIRED SAVING LOCAL STORAGE ===='
      localStorage.setItem(@id, JSON.stringify(@toJSON()))

    destroy: (options) ->
      console.log '===== DESTROY LOCAL STORAGE ===='
      localStorage.removeItem @id

    isEmpty: () ->
      _.size @attributes <= 1
      

  class AppSettings extends BaseLocalStorageModel
    id: 'app_settings'

  app_settings = new AppSettings
  MSGBUS.reqres.setHandler 'main:get_app_settings', ->
    app_settings
    
  class Page extends Backbone.Model
    url: () ->
      pathname = '/hubby/pages/'
      if window.location.pathname == '/index.local.html'
        pathname = '/pages/'
      return pathname + @id + '.json'

  module.exports =
    Page: Page
    
