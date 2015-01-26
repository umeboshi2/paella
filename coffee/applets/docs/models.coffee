define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  BaseLocalStorageModel = require 'common/localstoragemodel'
    
  ########################################
  # Models
  ########################################

  class Page extends Backbone.Model
    url: () ->
      "/paella/pages/#{@id}.json"
      
    validation:
      name:
        required: true
        
    
  module.exports =
    Page: Page
    
