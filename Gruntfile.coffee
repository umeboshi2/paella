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
        src: ['**/*.coffee']
        dest: app_dir
        ext: '.js'
        cwd: 'coffee'
                
      compileWithMaps:
        options:
          bare: false
          sourceMap: true
        expand: true
        src: ['**/*.coffee']
        dest: app_dir
        ext: '.js'
        cwd: 'coffee'
        
    compass:
      compile:
        config: 'config.rb'
        
    watch:
      coffee:
        files: ['coffee/**/*.coffee']
        tasks: ['coffee:compileWithMaps']
      compass:
        files: ['sass/**/*.scss']
        tasks: ['compass']
      buildjs:
        files: 'build.coffee'
        tasks: ['shell:compileBuildJS']
        
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

      compileBuildJS:
        command: 'python scripts/make-build-js.py'
        options:
          stdout: true
          
    # load grunt-* tasks
    require('matchdep').filterDev('grunt-*').forEach grunt.loadNpmTasks
    
    grunt.registerTask 'default', [
      'shell:bower'
      'coffee:compile'
      'compass:compile'
      'coffee:compileBuildJS'
      'coffee:compileWithMaps'
      ]
                          
        
