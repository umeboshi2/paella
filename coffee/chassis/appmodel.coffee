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
          appname: 'diskrecipes'
          name: 'Disk Recipes'
          url: '#diskrecipes'
        }
        {
          appname: 'machines'
          name: 'Machines'
          url: '#machines'
        }
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
      ]
    appregions: AppRegions.user_appregions
    approutes: [
      'frontdoor:route'
      'diskrecipes:route'
      'machines:route'
      'wiki:route'
      'bumblr:route'
      'hubby:route'
      ]
      
  module.exports = appmodel
  
    
