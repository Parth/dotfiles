'use strict'

const createSiteFile = require('./create-site-file')

function create404 () {
  return createSiteFile('404.html', '', 'text/html', { title: 'Page Not Found' })
}

module.exports = create404
