define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
  ########################################
  # Models
  ########################################
  class PageModel extends Backbone.Model
    validation:
      name:
        required: true
      content:
        required: true
        
  module.exports =
    PageModel: PageModel
    

