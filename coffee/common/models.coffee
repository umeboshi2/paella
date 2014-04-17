define (require, exports, module) ->
    $ = require 'jquery'
    _ = require 'underscore'
    Backbone = require 'backbone'
    ########################################
    # Collections
    ########################################

    class User extends Backbone.Model
        defaults:
            objtype: 'user'

    class Group extends Backbone.Model
        defaults:
            objtype: 'group'

    class CurrentUser extends Backbone.Model
        url: '/rest/current/user'

    class CurrentPage extends Backbone.Model
        url: '/rest/webviews/default'
        
    module.exports =
        User: User
        Group: Group
        CurrentUser: CurrentUser
        CurrentPage: CurrentPage
        
