define (require, exports, module) ->
  $ = require 'jquery'
  _ = require 'underscore'
  Backbone = require 'backbone'
    
  ########################################
  # Models
  ########################################
  class BasePageModel extends Backbone.Model
    validation:
      name:
        required: true
      content:
        required: true

  # use name for id on get requests
  # If this model is used to add to
  # the sitetext collection, it will
  # do a PUT instead of POST.
  class GetPageModel extends BasePageModel
    idAttribute: 'name'

  class PostPageModel extends BasePageModel
    
  module.exports =
    GetPageModel: GetPageModel
    PostPageModel: PostPageModel
    
    

