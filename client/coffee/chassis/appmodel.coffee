define (require, exports, module) ->
  AppRegions = require 'common/appregions'
  appmodel = new Backbone.Model
    hasUser: true
    brand:
      name: 'Paella'
      url: '/'
    apps:
      [
        {
          appname: 'wiki'
          name: 'Wiki'
          url: '#wiki'
        }
      ]
    appregions: AppRegions.user_appregions
    approutes: [
      'frontdoor:route'
      'wiki:route'
      ]
      
  module.exports = appmodel
  
    
