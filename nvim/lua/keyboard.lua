local builtin = require('telescope.builtin')
vim.keymap.set("n", "<C-s>", vim.cmd.wall)
vim.keymap.set("i", "<C-s>", "<ESC>:w<CR>")
vim.keymap.set("n", "<leader>w", vim.cmd.wq)
vim.keymap.set("n", "<C-q>", vim.cmd.q)

vim.keymap.set('n', '<leader>t', builtin.find_files, {})
vim.keymap.set('n', '<leader>T', builtin.git_files, {})
vim.keymap.set('n', '<leader>l', builtin.buffers, {})
vim.keymap.set('n', '<leader>g', builtin.grep_string, {})
vim.keymap.set('n', '<leader>lg', builtin.live_grep, {})
vim.keymap.set('n', '<leader>o', builtin.oldfiles, {})
vim.keymap.set("n", "<leader>ff", "<ESC>:NvimTreeFindFile<CR>")

vim.keymap.set("n", "<C-J>", "<C-W><C-J>")
vim.keymap.set("n", "<C-H>", "<C-W><C-H>")
vim.keymap.set("n", "<C-K>", "<C-W><C-K>")
vim.keymap.set("n", "<C-L>", "<C-W><C-L>")
vim.keymap.set("n", "<leader>/", vim.cmd.nohlsearch)

vim.api.nvim_create_autocmd('LspAttach', {
    desc = 'LSP actions',
    callback = function(event)
        local opts = { buffer = event.buf }

        vim.keymap.set('n', 'K', vim.lsp.buf.hover, opts)
        vim.keymap.set('n', '<leader>gd', vim.lsp.buf.definition, opts)
        vim.keymap.set('n', '<leader>fr', builtin.lsp_references, opts)
        vim.keymap.set('n', '<leader>ws', builtin.lsp_workspace_symbols, opts)
        vim.keymap.set('n', '<leader>ds', builtin.lsp_document_symbols, opts)
        vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename, opts)
        vim.keymap.set('n', '<leader>fmt', vim.lsp.buf.format, opts)
        vim.keymap.set('i', '<C-h>', vim.lsp.buf.signature_help, opts)
        vim.keymap.set('n', '<leader>vd', vim.diagnostic.open_float, opts)
        vim.keymap.set('n', '<leader>nd', function() vim.diagnostic.jump({ count = 1 }) end, opts)
        vim.keymap.set('n', '<leader>pd', function() vim.diagnostic.jump({ count = -1 }) end, opts)
        vim.keymap.set('n', '<leader> ', vim.lsp.buf.code_action, opts)

        vim.keymap.set('n', '<leader>nr', function() require('illuminate').goto_next_reference() end, opts)
        vim.keymap.set('n', '<leader>pr', function() require('illuminate').goto_prev_reference() end, opts)

        vim.lsp.completion.enable(true, event.data.client_id, event.buf, { autotrigger = true })
    end
})

vim.keymap.set('i', '<C-Space>', function() vim.lsp.completion.get() end)

for lhs, dir in pairs({ ['<Tab>'] = 1, ['<S-Tab>'] = -1 }) do
    vim.keymap.set({ 'i', 's' }, lhs, function()
        if vim.snippet.active({ direction = dir }) then
            return vim.snippet.jump(dir)
        end
        return lhs == '<Tab>' and '<Tab>' or '<S-Tab>'
    end, { expr = true })
end
