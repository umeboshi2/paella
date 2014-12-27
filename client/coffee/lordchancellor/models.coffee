define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  MainBus = require 'msgbus'

  ########################################
  # Models
  ########################################

  class Page extends Backbone.Model
    validation:
      name:
        required: true
        
    
  module.exports =
    Page: Page
    
