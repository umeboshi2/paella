define (require, exports, module) ->
  $ = require 'jquery'
  jQuery = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'

  AppRegions = require 'common/appregions'
  
  appmodel = new Backbone.Model
    brand:
      name: 'Paella'
      url: '#'
    apps:
      [
      ]
    appregions: AppRegions.basic_appregions
    approutes: [
      'frontdoor:route'
      ]
    
      
  module.exports = appmodel
  
  
    
