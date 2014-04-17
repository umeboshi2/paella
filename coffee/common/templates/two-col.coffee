define (require, exports, module) ->
    teacup = require 'teacup'

    renderable = teacup.renderable

    div = teacup.div
    ########################################
    # Templates
    ########################################
    two_col = renderable () ->
      div '.two-col', ->
        div '.sidebar'
        div '.right-column-content'
        
    module.exports = two-col
    
