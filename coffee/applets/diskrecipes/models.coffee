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
        
  class RaidRecipe extends Backbone.Model
    url: () ->
      "/paella/rest/v0/main/raidrecipes/#{@name}"
        
    
  module.exports =
    Recipe: Recipe
    RaidRecipe: RaidRecipe
    
    
    
