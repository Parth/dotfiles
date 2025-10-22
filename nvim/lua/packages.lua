-- illuminate
require("illuminate").configure {}
vim.api.nvim_set_hl(0, "IlluminatedWordText", { link = "CursorLine" })
vim.api.nvim_set_hl(0, "IlluminatedWordRead", { link = "CursorLine" })
vim.api.nvim_set_hl(0, "IlluminatedWordWrite", { link = "CursorLine" })

require("gitsigns").setup {
    current_line_blame = true,
}

-- for status line things
-- require('lsp-status').register_progress()
require('fidget').setup {}
require('lualine').setup {
    options = {
        icons_enabled = true,
        theme = {
            normal   = {
                a = { fg = "#000000", bg = "#66B2FF", gui = "bold" },
                b = { fg = "#FFFFFF", bg = "#242424" },
                c = { fg = "#FFFFFF", bg = "#1A1A1A" }
            },
            insert   = { a = { fg = "#1A1A1A", bg = "#FFDB70", gui = "bold" } },
            visual   = { a = { fg = "#1A1A1A", bg = "#AC8CD9", gui = "bold" } },
            replace  = { a = { fg = "#1A1A1A", bg = "#FF6680", gui = "bold" } },
            command  = { a = { fg = "#1A1A1A", bg = "#6EECF7", gui = "bold" } },
            inactive = {
                a = { fg = "#D0D0D0", bg = "#1A1A1A" },
                b = { fg = "#D0D0D0", bg = "#1A1A1A" },
                c = { fg = "#D0D0D0", bg = "#1A1A1A" }
            },
        },
        component_separators = { left = '', right = '' },
        section_separators = { left = '', right = '' },
        disabled_filetypes = {
            statusline = { 'NvimTree' },
            winbar = { 'NvimTree' },
        },
        ignore_focus = {},
        always_divide_middle = true,
        globalstatus = false,
        refresh = {
            statusline = 100,
            tabline = 100,
            winbar = 100,
        }
    },
    sections = {
        lualine_a = { 'mode' },
        lualine_b = { 'branch', {
            'diff',
            symbols = { added = ' ', modified = ' ', removed = ' ' },
            diff_color = {
                added    = { fg = '#67E4B6' },
                modified = { fg = '#66B2FF' },
                removed  = { fg = '#FF6680' },
            },
            color = { bg = '#2A2A2A', fg = '#FFFFFF' }, -- ← custom background here
        } },
        lualine_c = {},
        lualine_x = { 'filetype' },
        -- lualine_y = { "require'lsp-status'.status()" },
        lualine_z = { 'location' }
    },
    inactive_sections = {
        lualine_a = {},
        lualine_b = {},
        lualine_c = { 'filename' },
        lualine_x = { 'location' },
        lualine_y = {},
        lualine_z = {}
    },
    tabline = {},
    winbar = {
        lualine_a = {
            {
                'filename',
                path = 3, -- 0: just filename, 1: relative, 2: absolute, 3: absolute + tilde (~)
                symbols = {
                    modified = ' ●',
                    readonly = ' ',
                    unnamed = '[No Name]',
                },
            },
        },
        lualine_z = {
            {
                'diagnostics',
                sources           = { 'nvim_diagnostic' },
                sections          = { 'error', 'warn', 'info', 'hint' },
                symbols           = { error = ' ', warn = ' ', info = ' ', hint = ' ' },
                -- per-severity colors (foregrounds)
                diagnostics_color = {
                    error = { fg = '#FF6680', bg = '#2A2A2A' },         -- red text on dark gray
                    warn  = { fg = '#FFDB70', bg = '#2A2A2A' },         -- yellow
                    info  = { fg = '#6EECF7', bg = '#2A2A2A' },         -- cyan
                    hint  = { fg = '#D0D0D0', bg = '#2A2A2A' },         -- light gray
                },
                color             = { fg = '#FFFFFF', bg = '#2A2A2A' }, -- set both!
                -- always_visible = true, -- uncomment to test even with 0 diags
            },
        },
    },
    inactive_winbar = {},
    extensions = {}
}

-- for tree things
vim.g.loaded_netrw = 1
vim.g.loaded_netrwPlugin = 1
require("nvim-tree").setup({
    diagnostics = {
        enable = true
    }
})

local lspconfig = require("lspconfig")

lspconfig.rust_analyzer.setup({
    settings = {
        ["rust-analyzer"] = {
            cargo = {
                allFeatures = true,
            },
            checkOnSave = {
                command = "clippy",
            },
        },
    },
})

lspconfig.lua_ls.setup {
    settings = {
        Lua = {
            runtime = {
                -- Tell the language server which version of Lua you're using
                -- (most likely LuaJIT in the case of Neovim)
                version = 'LuaJIT',
            },
            diagnostics = {
                -- Get the language server to recognize the `vim` global
                globals = {
                    'vim',
                    'require'
                },
            },
            workspace = {
                -- Make the server aware of Neovim runtime files
                library = vim.api.nvim_get_runtime_file("", true),
            },
            -- Do not send telemetry data containing a randomized but unique identifier
            telemetry = {
                enable = false,
            },
        },
    },
}
lspconfig.nixd.setup {
    settings = {
        nixd = {
            formatting = {
                command = { "nixpkgs-fmt" }
            }
        }
    }
}
lspconfig.nil_ls.setup {}
