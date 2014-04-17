# Gruntfile for sitecontent

module.exports = (grunt) ->
  # variables to use in config
  # foo = 'bar'
  app_dir = 'javascripts'
    
  # config
  grunt.initConfig
    coffee:
      compile:
        options:
          bare: false
        expand: true
        src: ['coffee/**/*.coffee']
        dest: app_dir
        ext: '.js'
                
      compileWithMaps:
        options:
          bare: false
          sourceMap: true
        expand: true
        src: ['coffee/**/*.coffee']
        dest: app_dir
        ext: '.js'

      compileBuildJS:
        options:
          bare: true
        src: 'build.coffee'
        dest: 'build.js'
        
        
    compass:
      compile:
        config: 'config.rb'
        
    watch:
      coffee:
        files: ['**/*.coffee']
        tasks: ['coffee:compileWithMaps']
      compass:
        files: ['sass/**/*.scss']
        tasks: ['compass']
      cpcoffee:
        files: ['coffee/**/*.coffee']
        tasks: ['copy:coffee']
      buildjs:
        files: 'build.coffee'
        tasks: ['coffee:compileBuildJS']
        
      
        
    copy:
      coffee:
        files:
          [
            expand: true
            src: ['coffee/**']
            dest: 'javascripts/'
          ]  
        
        
    clean:
      js:
        src: ['javascripts/**/*.js']
      emacs:
        src: ['**/*~']
        
    shell:
      bower:
        command: 'python scripts/prepare-bower-components.py'
        options:
          stdout: true
        
    # load grunt-* tasks
    require('matchdep').filterDev('grunt-*').forEach grunt.loadNpmTasks
    
    grunt.registerTask 'default', [
      'shell:bower'
      'coffee:compile'
      'compass:compile'
      'coffee:compileBuildJS'
      ]
                          
        