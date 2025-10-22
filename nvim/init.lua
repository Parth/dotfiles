vim.g.mapleader = ' ';

require("keyboard")
require("config")

require('auto-dark-mode').setup {
    set_dark_mode = function()
        require('dark_theme').colorscheme()
        require('packages')
    end,
    set_light_mode = function()
        require('light_theme').colorscheme()
        require('packages')
    end,
}

