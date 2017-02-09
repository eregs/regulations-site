module.exports = function toExport(grunt) {
  grunt.initConfig({

    /**
     * Pull in the package.json file so we can read its metadata.
     */
    pkg: grunt.file.readJSON('package.json'),

    /**
     *
     *  Pull in config-specific vars
     *
     */
    config: grunt.file.readJSON('config.json'),

    env: {
      dev: {
        NODE_ENV: 'development',
      },
      dist: {
        NODE_ENV: 'production',
      },
    },

    /**
     * Copy dependencies into static paths
     */
    copy: {
      main: {
        files: [
          {
            expand: true,
            flatten: true,
            src: ['node_modules/respond.js/dest/*'],
            dest: '<%= config.frontEndPath %>/js/built/lib/respond/',
            filter: 'isFile',
          },
        ],
      },
    },

    /**
     * https://github.com/gruntjs/grunt-contrib-sass
     */
    sass: {
      dev: {
        options: {
          style: 'expanded',
        },
        files: {
          '<%= config.frontEndPath %>/css/style.css': '<%= config.frontEndPath %>/css/scss/main.scss',
        },
      },
    },

    /**
     * CSSMin: https://github.com/gruntjs/grunt-contrib-cssmin
     *
     * Minify CSS for production
     */
    cssmin: {
      target: {
        files: {
          '<%= config.frontEndPath %>/css/regulations.min.css': ['<%= config.frontEndPath %>/css/style.css'],
        },
      },
    },
    /**
     * ESLint: https://github.com/sindresorhus/grunt-eslint
     *
     * Validate files with ESLint.
     */
    eslint: {
      target: [
        'Gruntfile.js',
        '<%= config.frontEndPath %>/js/source/*.js',
        '<%= config.frontEndPath %>/js/source/events/**/*.js',
        '<%= config.frontEndPath %>/js/source/models/**/*.js',
        '<%= config.frontEndPath %>/js/source/views/**/*.js',
        '<%= config.frontEndPath %>/js/source/views/**/*.jsx',
      ],
    },

    /**
    * Browserify:
    *
    * Require('modules') in the browser/bundle up dependencies.
    */
    browserify: {
      dev: {
        files: {
          '<%= config.frontEndPath %>/js/built/regulations.js': ['<%= config.frontEndPath %>/js/source/regulations.js', '<%= config.frontEndPath %>/js/source/regulations.js'],
        },
        options: {
          transform: ['babelify', 'browserify-shim'],
          browserifyOptions: {
            debug: true,
          },
        },
      },
      dist: {
        files: {
          '<%= config.frontEndPath %>/js/built/regulations.min.js': ['<%= config.frontEndPath %>/js/source/regulations.js'],
        },
        options: {
          transform: ['babelify', 'browserify-shim'],
          browserifyOptions: {
            debug: true,
            extensions: ['.js', '.jsx'],
          },
          plugin: [
            [function minifyify(b) {
              b.plugin('minifyify', {
                map: '/static/regulations/js/built/regulations.min.map',
                output: grunt.template.process('<%= config.frontEndPath %>/js/built/regulations.min.map'),
              });
            }],
          ],
        },
      },
    },

    mocha_istanbul: {
      coverage: {
        src: ['<%= config.frontEndPath %>/js/unittests/specs/**/*.js'],
        options: {
          root: '<%= config.frontEndPath %>/js',
          scriptPath: require.resolve('isparta/lib/cli'),
          istanbulOptions: ['--include-all-sources'],
          mochaOptions: ['--compilers', 'js:babel-register'],
          nodeExec: require.resolve('.bin/babel-node'),
          coverageFolder: '<%= config.frontEndPath %>/js/unittests/coverage',
          coverage: false,
        },
      },
    },
  });

  /* eslint-disable global-require,import/no-extraneous-dependencies */
  grunt.event.on('coverage', (lcov, done) => {
    require('coveralls').handleInput(lcov, (err) => {
      if (err) {
        done(err);
      }
      done();
    });
  });
  /**
   * The above tasks are loaded here.
   */
  require('load-grunt-tasks')(grunt);
  /* eslint-enable */

  /**
   * Create task aliases by registering new tasks
   */
  grunt.registerTask('test', ['eslint', 'mocha_istanbul']);
  grunt.registerTask('test-js', ['eslint', 'mocha_istanbul']);
  grunt.registerTask('build-dev', ['env:dev', 'copy', 'browserify:dev', 'sass']);
  grunt.registerTask('build-dist', ['env:dist', 'copy', 'browserify:dist', 'sass', 'cssmin']);
  grunt.registerTask('default', ['build-dist']);
};
