vim.api.nvim_create_autocmd('FileType', {
    desc = 'start treesitter wherever a parser exists',
    callback = function(ev)
        local lang = vim.treesitter.language.get_lang(vim.bo[ev.buf].filetype)
        if not lang then return end
        if not pcall(vim.treesitter.language.add, lang) then return end
        pcall(vim.treesitter.start, ev.buf, lang)
    end,
})
