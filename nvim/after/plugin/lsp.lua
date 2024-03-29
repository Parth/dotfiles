local lsp = require('lsp-zero')

lsp.preset('recommended')

lsp.ensure_installed({
    'rust_analyzer'
})

local cmp = require('cmp')
local cmp_select = { behavior = cmp.SelectBehavior.Select }
local cmp_mappings = lsp.defaults.cmp_mappings({
    ['<C-p>'] = cmp.mapping.select_prev_item(cmp_select),
    ['<C-n>'] = cmp.mapping.select_next_item(cmp_select),
    ['<C-y>'] = cmp.mapping.confirm(cmp_select),
    ['<C-Space>'] = cmp.mapping.complete(),
})


lsp.setup_nvim_cmp({
    mapping = cmp_mappings
})

lsp.set_preferences({
    suggest_lsp_servers = false,
    sign_icons = {
        error = 'E',
        warn = 'W',
        hint = 'H',
        info = 'I'
    }
})

local augroup = vim.api.nvim_create_augroup('LspFormatting', {})
local lsp_format_on_save = function(bufnr)
    vim.api.nvim_clear_autocmds({ group = augroup, buffer = bufnr })
    vim.api.nvim_create_autocmd('BufWritePre', {
        group = augroup,
        buffer = bufnr,
        callback = function()
            vim.lsp.buf.format()
        end,
    })
end


lsp.on_attach(function(client, bufnr)
    lsp_format_on_save(bufnr)

    local opts = { buffer = bufnr, remap = false }

    vim.keymap.set("n", "<leader>ld", function() vim.lsp.buf.definition() end, opts)
    vim.keymap.set("n", "<leader>h", function() vim.lsp.buf.hover() end, opts)
    vim.keymap.set("n", "<leader>ws", function() vim.lsp.buf.workspace_symbol() end, opts)
    vim.keymap.set("n", "<leader>vd", function() vim.diagnostic.open_float() end, opts)
    vim.keymap.set("n", "<leader>nd", function() vim.diagnostic.goto_next() end, opts)
    vim.keymap.set("n", "<leader>pd", function() vim.diagnostic.goto_prev() end, opts)
    vim.keymap.set("n", "<leader> ", function() vim.lsp.buf.code_action() end, opts)
    vim.keymap.set("n", "<leader>fr", function() vim.lsp.buf.references() end, opts)
    vim.keymap.set("n", "<leader>rn", function() vim.lsp.buf.rename() end, opts)
    vim.keymap.set("i", "<C-p>", function() vim.lsp.buf.signature_help() end, opts)
    vim.keymap.set("n", "<leader>clr", function() vim.lsp.codelens.refresh() end, opts)
    vim.keymap.set("n", "<leader>cl", function() vim.lsp.codelens.run() end, opts)
end)

lsp.setup()

vim.diagnostic.config({
    virtual_text = true
})
