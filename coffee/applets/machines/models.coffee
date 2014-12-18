define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
    
  ########################################
  # Models
  ########################################
  class Recipe extends Backbone.Model
    url: () ->
      "/paella/rest/v0/main/recipes/#{@name}"
        
    
  module.exports =
    Recipe: Recipe
    
    
