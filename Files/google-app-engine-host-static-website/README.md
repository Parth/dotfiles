FROM: https://gist.github.com/darktable/873098
==============================================

App.yaml designed for serving a static site on Google App Engine (Python). Copy your static html and files into a folder called "static" next to app.yaml.  Contains a bunch of mimetype declarations from html5boilerplate's .htaccess.  May not be necessary for most situations.

    my_site
      app.yaml
      static
        index.html
        ...

The static folder is invisible when serving (i.e. my_site/static/index.html is accessed as http://your-app-name-here.appspot.com/index.html.

**Remember:** No spaces in file or path names. Case sensitive.
