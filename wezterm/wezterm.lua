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

print(wezterm.gui.get_appearance())

if wezterm.gui.get_appearance():find 'Dark' then
    config.colors = {
        ansi = {
            '#505050',
            '#FF6680',
            '#67E4B6',
            '#FFDB70',
            '#66B2FF',
            '#AC8CD9',
            '#6EECF7',
            '#D0D0D0',
        },
        brights = {
            '#D0D0D0',
            '#FF99AA',
            '#93ECCB',
            '#FFE699',
            '#80BFFF',
            '#BA9FDF',
            '#9EF2FA',
            '#FFFFFF',
        },

        foreground = '#FFFFFF',
        background = '#080808',
   }
else
    config.colors = {
        ansi = {
            '#1A1A1A',
            '#DF2040',
            '#00B371',
            '#CC9900',
            '#207FDF',
            '#7855AA',
            '#0FAEBD',
            '#D0D0D0',
        },
        brights = {
            '#808080',
            '#FF6680',
            '#2DD296',
            '#FFBF00',
            '#66B2FF',
            '#AC8CD9',
            '#13DAEC',
            '#1A1A1A',
        },

        foreground = '#000000',
        background = '#FFFFFF',
    }
end

return config
