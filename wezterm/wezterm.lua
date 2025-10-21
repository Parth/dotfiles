local wezterm = require 'wezterm'

local config = wezterm.config_builder()

config.enable_tab_bar = false

config.window_padding = {
  left = 20,
  right = 20,
  top = 20,
  bottom = 20,
}
config.macos_window_background_blur = 100
config.win32_system_backdrop = 'Acrylic'

-- presently broken on linux as my system has no real way to set dark / light mode
print(wezterm.gui.get_appearance())

if wezterm.gui.get_appearance():find 'Dark' then
    config.colors = {
        ansi = {
            '#505050', -- black
            '#FF6680', -- red
            '#67E4B6', -- green
            '#FFDB70', -- yellow
            '#66B2FF', -- blue
            '#AC8CD9', -- magenta
            '#6EECF7', -- cyan
            '#D0D0D0', -- white
        },
        brights = {
            '#D0D0D0', -- brblack
            '#FF99AA', -- brred
            '#93ECCB', -- brgreen
            '#FFE699', -- bryellow
            '#80BFFF', -- brblue
            '#BA9FDF', -- brmagenta
            '#9EF2FA', -- brcyan
            '#FFFFFF', -- brwhite
        },

        foreground = '#FFFFFF',
        background = '#000000',
   }
else
    config.colors = {
        ansi = {
            '#1A1A1A', -- black
            '#DF2040', -- red
            '#00B371', -- green
            '#CC9900', -- yellow
            '#207FDF', -- blue
            '#7855AA', -- magenta
            '#0FAEBD', -- cyan
            '#D0D0D0', -- white
        },
        brights = {
            '#808080', -- brblack
            '#FF6680', -- brred
            '#2DD296', -- brgreen
            '#FFBF00', -- bryellow
            '#66B2FF', -- brblue
            '#AC8CD9', -- brmagenta
            '#13DAEC', -- brcyan
            '#1A1A1A', -- brwhite
        },

        foreground = '#000000',
        background = '#FFFFFF',
    }
end

return config
