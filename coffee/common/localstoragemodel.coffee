define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  
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

    save: (attributes, options) ->
      console.log '===== CHANGE FIRED SAVING LOCAL STORAGE ===='
      localStorage.setItem(@id, JSON.stringify(@toJSON()))
      return $.ajax
        success: options.success
        error: options.error
        
    destroy: (options) ->
      console.log '===== DESTROY LOCAL STORAGE ===='
      localStorage.removeItem @id

    isEmpty: () ->
      _.size @attributes <= 1
      
  module.exports = BaseLocalStorageModel
  