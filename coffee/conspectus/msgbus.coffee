define (require, exports, module) ->
    Marionette = require 'marionette'
    Wreqr = Backbone.Wreqr
    module.exports =
        reqres: new Wreqr.RequestResponse()
        commands: new Wreqr.Commands()
        events: new Wreqr.EventAggregator()
        
