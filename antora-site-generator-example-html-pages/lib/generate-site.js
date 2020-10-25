'use strict'

const aggregateContent = require('@antora/content-aggregator')
const buildNavigation = require('@antora/navigation-builder')
const buildPlaybook = require('@antora/playbook-builder')
const classifyContent = require('@antora/content-classifier')
const convertDocuments = require('@antora/document-converter')
const create404Page = require('./create-404-page')
const createPageComposer = require('@antora/page-composer')
const loadUi = require('@antora/ui-loader')
const mapSite = require('@antora/site-mapper')
const produceRedirects = require('@antora/redirect-producer')
const publishSite = require('@antora/site-publisher')
const { resolveConfig: resolveAsciiDocConfig } = require('@antora/asciidoc-loader')

async function generateSite (args, env) {
  const playbook = buildPlaybook(args, env)
  const asciidocConfig = resolveAsciiDocConfig(playbook)
  const [contentCatalog, uiCatalog] = await Promise.all([
    aggregateContent(playbook).then((contentAggregate) => {
      const htmlFiles = contentAggregate.reduce((accum, { name: component, version, files }) => {
        return accum.concat(
          files
            .filter((it) => it.mediaType === 'text/html')
            .map((it) => {
              Object.assign(it.src, { component, version, family: 'page' })
              return it
            })
        )
      }, [])
      const catalog = classifyContent(playbook, contentAggregate, asciidocConfig)
      htmlFiles.forEach((it) => {
        const pathSegments = it.path.split('/')
        pathSegments.shift()
        it.src.module = pathSegments.shift()
        pathSegments.shift()
        it.src.relative = pathSegments.join('/')
        catalog.addFile(it)
      })
      return catalog
    }),
    loadUi(playbook),
  ])
  const pages = convertDocuments(contentCatalog, asciidocConfig)
  const navigationCatalog = buildNavigation(contentCatalog, asciidocConfig)
  const composePage = createPageComposer(playbook, contentCatalog, uiCatalog, env)
  pages.forEach((page) => composePage(page, contentCatalog, navigationCatalog))
  const siteFiles = mapSite(playbook, pages).concat(produceRedirects(playbook, contentCatalog))
  if (playbook.site.url) siteFiles.push(composePage(create404Page()))
  const siteCatalog = { getAll: () => siteFiles }
  return publishSite(playbook, [contentCatalog, uiCatalog, siteCatalog])
}

module.exports = generateSite
