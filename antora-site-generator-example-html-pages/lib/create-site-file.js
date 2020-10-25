'use strict'

const File = require('vinyl')

function createSiteFile (path, contents, mediaType, props = {}) {
  return new File({
    ...props,
    contents: Buffer.from(contents),
    mediaType,
    out: { path },
    path: path,
    pub: { url: `/${path}`, rootPath: '' },
    src: { stem: path.slice(0, path.lastIndexOf('.')) },
  })
}

module.exports = createSiteFile
