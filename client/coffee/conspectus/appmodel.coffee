define (require, exports, module) ->
  $ = require 'jquery'
  jQuery = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'

  AppRegions = require 'common/appregions'
  
  appmodel = new Backbone.Model
    brand:
      name: 'Conspectus'
      url: '#'
    apps:
      [
        {
          appname: 'wiki'
          name: 'Wiki'
          url: '#wiki'
        }
        {
          appname: 'bumblr'
          name: 'Bumblr'
          url: '#bumblr'
        }
        {
          appname: 'hubby'
          name: 'Hubby'
          url: '#hubby'
        }
        {
          appname: 'bookstore'
          name: 'Bookstore'
          url: '#bookstore'
        }
      ]
    appregions: AppRegions.basic_appregions
    approutes: [
      'frontdoor:route'
      'wiki:route'
      'bumblr:route'
      'hubby:route'
      'bookstore:route'
      ]
    
      
  module.exports = appmodel
  
  
    
