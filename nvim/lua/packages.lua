local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable",
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup(
	{
		-- treesitter: richer syntax highlighting
		{
			"nvim-treesitter/nvim-treesitter",
			build = ":TSUpdate",
			config = function () 
				local configs = require("nvim-treesitter.configs")

				configs.setup({
					ensure_installed = { "c", "lua", "vim", "rust", "go" },
					sync_install = false,
					highlight = { enable = true },
					indent = { enable = true },  
				})
			end
		},

		-- telescope
		{
			'nvim-telescope/telescope.nvim',
			tag = '0.1.6',
			dependencies = { 'nvim-lua/plenary.nvim' }
		},

		-- lsp-zero
		{'VonHeikemen/lsp-zero.nvim', branch = 'v3.x'},
		{'neovim/nvim-lspconfig'},
		{'hrsh7th/cmp-nvim-lsp'},
		{'hrsh7th/nvim-cmp'},
		{'L3MON4D3/LuaSnip'},
		{'williamboman/mason.nvim'},
		{'williamboman/mason-lspconfig.nvim'},

        -- for nvim config lsp support
        { "folke/neodev.nvim", opts = {} },

        -- highlight words 
        { 'RRethy/vim-illuminate' },

        -- lua line 
        {
            'nvim-lualine/lualine.nvim',
            dependencies = { 'nvim-tree/nvim-web-devicons' }
        },

        -- lsp-status populated in lua line
        { 'nvim-lua/lsp-status.nvim' },

        -- nvim-tree
        {
            'nvim-tree/nvim-tree.lua',
            dependencies = { 'nvim-tree/nvim-web-devicons' }
        }
	},
	{
		install = {
			colorscheme = { "default" }
		}
	}
)

require('lsp-zero')
require('mason').setup({})
require('mason-lspconfig').setup({
  ensure_installed = { "rust_analyzer", "lua_ls", "gopls" },
  handlers = {
    function(server_name)
      require('lspconfig')[server_name].setup({})
    end,
  },
})

-- illuminate
require("illuminate").configure{}
vim.api.nvim_set_hl(0, "IlluminatedWordText", { link = "CursorLine" })
vim.api.nvim_set_hl(0, "IlluminatedWordRead", { link = "CursorLine" })
vim.api.nvim_set_hl(0, "IlluminatedWordWrite", { link = "CursorLine" })

-- for status line things
require('lsp-status').register_progress()
require('lualine').setup {
  options = {
    icons_enabled = true,
    theme = '16color',
    component_separators = { left = '', right = ''},
    section_separators = { left = '', right = ''},
    disabled_filetypes = {
      statusline = {},
      winbar = {},
    },
    ignore_focus = {},
    always_divide_middle = true,
    globalstatus = false,
    refresh = {
      statusline = 1000,
      tabline = 1000,
      winbar = 1000,
    }
  },
  sections = {
    lualine_a = {'mode'},
    lualine_b = {'branch', 'diff', 'diagnostics'},
    lualine_c = {'filename'},
    lualine_x = {'encoding', 'fileformat', 'filetype'},
    lualine_y = { "require'lsp-status'.status()" },
    lualine_z = {'location'}
  },
  inactive_sections = {
    lualine_a = {},
    lualine_b = {},
    lualine_c = {'filename'},
    lualine_x = {'location'},
    lualine_y = {},
    lualine_z = {}
  },
  tabline = {},
  winbar = {},
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
