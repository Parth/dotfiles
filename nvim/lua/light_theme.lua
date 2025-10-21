-- lua/colors/premonition_light.lua
-- Mnemonic Light Innovation – Neovim colorscheme (starter)
-- Palette mapped from your JSON.

local M = {}

local p = {
  -- Core
  bg            = "#FFFFFF",
  fg            = "#1A1A1A",
  fg_muted      = "#505050",
  comment       = "#808080",
  border        = "#D0D0D0",

  -- Accents (from JSON)
  blue          = "#207FDF",
  blue_bright   = "#66B2FF",
  magenta       = "#7855AA",
  magenta_bright= "#AC8CD9",
  green         = "#00B371",
  green_bright  = "#2DD296",
  yellow        = "#E6AC00",
  yellow_bright = "#FFBF00",
  red           = "#DF2040",
  red_bright    = "#FF6680",
  cyan          = "#0FAEBD",
  cyan_bright   = "#13DAEC",
  -- syntax cyan in your block uses 00BBCC; keep both:
  cyan_syntax   = "#00BBCC",

  -- UI
  ui            = "#FFFFFF",   -- status/tab/toolbars
  tabbar        = "#F0F0F0",
  active_line   = "#F6F6F6",   -- approx of #A0A0A010 over white
  selection     = "#EEF6FF",   -- gentle selection for light bg
  search_bg     = "#DCEFF8",   -- readable take on #13DAEC40

  -- Diagnostics backgrounds
  error_bg      = "#F5DCE0",
  warn_bg       = "#FDF5D9",
  hint_bg       = "#DCEAFB",
  info_bg       = "#E3F5EE",
}

local function set(name, val) vim.api.nvim_set_hl(0, name, val) end

local function setup_terminal()
  -- Terminal ANSI (from your "terminal.ansi.*")
  vim.g.terminal_color_0  = "#1A1A1A"   -- black
  vim.g.terminal_color_8  = "#808080"   -- bright black

  vim.g.terminal_color_1  = p.red
  vim.g.terminal_color_9  = p.red_bright

  vim.g.terminal_color_2  = p.green
  vim.g.terminal_color_10 = p.green_bright

  vim.g.terminal_color_3  = p.yellow
  vim.g.terminal_color_11 = p.yellow_bright

  vim.g.terminal_color_4  = p.blue
  vim.g.terminal_color_12 = p.blue_bright

  vim.g.terminal_color_5  = p.magenta
  vim.g.terminal_color_13 = p.magenta_bright

  vim.g.terminal_color_6  = p.cyan
  vim.g.terminal_color_14 = p.cyan_bright

  vim.g.terminal_color_7  = "#D0D0D0"  -- white
  vim.g.terminal_color_15 = "#1A1A1A"  -- bright white (your JSON maps this dark)
end

function M.colorscheme()
  vim.cmd("highlight clear")
  if vim.fn.exists("syntax_on") == 1 then vim.cmd("syntax reset") end

  vim.o.background = "light"
  vim.g.colors_name = "premonition_light"
  setup_terminal()

  ---------------------------------------------------------------------------
  -- Core UI
  ---------------------------------------------------------------------------
  set("Normal",         { fg = p.fg, bg = p.bg })
  set("NormalNC",       { fg = p.fg_muted, bg = p.bg })
  set("SignColumn",     { bg = p.bg })
  set("LineNr",         { fg = p.fg_muted, bg = p.bg })
  set("CursorLineNr",   { fg = p.blue, bg = p.active_line, bold = true })
  set("CursorLine",     { bg = p.active_line })
  set("CursorColumn",   { bg = p.active_line })
  set("ColorColumn",    { bg = p.active_line })
  set("VertSplit",      { fg = p.border, bg = p.bg })
  set("WinSeparator",   { fg = p.border, bg = p.bg })

  set("Folded",         { fg = p.fg_muted, bg = p.active_line })
  set("FoldColumn",     { fg = p.fg_muted, bg = p.bg })

  set("Visual",         { bg = p.selection })
  set("Search",         { fg = p.fg, bg = p.search_bg })
  set("IncSearch",      { fg = p.bg, bg = p.cyan_bright, bold = true })
  set("MatchParen",     { fg = p.yellow_bright, bold = true })

  set("Pmenu",          { fg = p.fg, bg = p.ui, blend = 0 })
  set("PmenuSel",       { fg = p.bg, bg = p.blue })
  set("PmenuSbar",      { bg = p.active_line })
  set("PmenuThumb",     { bg = p.border })

  set("StatusLine",     { fg = p.fg, bg = p.ui })
  set("StatusLineNC",   { fg = p.fg_muted, bg = p.ui })
  set("TabLine",        { fg = p.fg_muted, bg = p.tabbar })
  set("TabLineSel",     { fg = p.fg, bg = p.ui, bold = true })
  set("TabLineFill",    { bg = p.tabbar })

  set("Whitespace",     { fg = p.border })
  set("NonText",        { fg = p.border })
  set("SpecialKey",     { fg = p.border })

  ---------------------------------------------------------------------------
  -- Syntax (Vim groups)
  ---------------------------------------------------------------------------
  set("Comment",        { fg = p.comment, italic = true })
  set("Identifier",     { fg = p.fg })
  set("Function",       { fg = p.green, bold = true })
  set("Statement",      { fg = p.magenta })       -- if/for/return
  set("Keyword",        { fg = p.magenta, italic = true })
  set("Conditional",    { fg = p.magenta })
  set("Repeat",         { fg = p.magenta })
  set("Operator",       { fg = p.comment })
  set("Type",           { fg = p.blue })
  set("StorageClass",   { fg = p.blue })
  set("Structure",      { fg = p.blue })
  set("Constant",       { fg = p.cyan_syntax })
  set("Boolean",        { fg = p.cyan_syntax })
  set("Number",         { fg = p.cyan_syntax })
  set("String",         { fg = p.cyan_syntax })
  set("Character",      { fg = p.cyan_syntax })
  set("Special",        { fg = p.green })
  set("Delimiter",      { fg = p.comment })

  ---------------------------------------------------------------------------
  -- Diagnostics (LSP)
  ---------------------------------------------------------------------------
  set("Error",                 { fg = p.red })
  set("Todo",                  { fg = p.yellow_bright, bold = true })
  set("ErrorMsg",              { fg = p.red, bg = p.error_bg, bold = true })
  set("WarningMsg",            { fg = p.yellow_bright, bg = p.warn_bg })
  set("MoreMsg",               { fg = p.green })
  set("Question",              { fg = p.green })

  set("DiagnosticError",       { fg = p.red })
  set("DiagnosticWarn",        { fg = p.yellow_bright })
  set("DiagnosticInfo",        { fg = p.fg_muted })
  set("DiagnosticHint",        { fg = p.fg_muted })
  set("DiagnosticOk",          { fg = p.green })

  set("DiagnosticUnderlineError", { sp = p.red, undercurl = true })
  set("DiagnosticUnderlineWarn",  { sp = p.yellow_bright, undercurl = true })
  set("DiagnosticUnderlineInfo",  { sp = p.blue, undercurl = true })
  set("DiagnosticUnderlineHint",  { sp = p.magenta, undercurl = true })

  set("DiagnosticVirtualTextError", { fg = p.red, bg = p.error_bg })
  set("DiagnosticVirtualTextWarn",  { fg = p.yellow_bright, bg = p.warn_bg })
  set("DiagnosticVirtualTextInfo",  { fg = p.fg_muted, bg = p.info_bg })
  set("DiagnosticVirtualTextHint",  { fg = p.fg_muted, bg = p.hint_bg })

  ---------------------------------------------------------------------------
  -- Diff / Git
  ---------------------------------------------------------------------------
  set("DiffAdd",    { bg = "#E9F6F0", fg = p.green })
  set("DiffChange", { bg = "#F6F1E5", fg = p.yellow })
  set("DiffDelete", { bg = "#F6E9EC", fg = p.red })
  set("DiffText",   { bg = "#E3EFE7", bold = true })

  set("GitSignsAdd",    { fg = p.green })
  set("GitSignsChange", { fg = p.yellow })
  set("GitSignsDelete", { fg = p.red })

  ---------------------------------------------------------------------------
  -- Treesitter (link to Vim groups)
  ---------------------------------------------------------------------------
  local links = {
    ["@comment"]             = "Comment",
    ["@punctuation"]         = "Delimiter",
    ["@operator"]            = "Operator",
    ["@keyword"]             = "Keyword",
    ["@conditional"]         = "Conditional",
    ["@repeat"]              = "Repeat",

    ["@type"]                = "Type",
    ["@type.builtin"]        = "Type",
    ["@type.definition"]     = "Type",
    ["@storageclass"]        = "StorageClass",

    ["@string"]              = "String",
    ["@string.escape"]       = "Special",
    ["@string.regex"]        = "Special",
    ["@character"]           = "Character",
    ["@boolean"]             = "Boolean",
    ["@number"]              = "Number",
    ["@constant"]            = "Constant",

    ["@variable"]            = "Identifier",
    ["@variable.builtin"]    = "Identifier",
    ["@constant.builtin"]    = "Constant",

    ["@function"]            = "Function",
    ["@function.builtin"]    = "Function",
    ["@method"]              = "Function",
    ["@constructor"]         = "Function",
    ["@parameter"]           = "Identifier",
    ["@field"]               = "Identifier",
    ["@property"]            = "Identifier",
    ["@attribute"]           = "Identifier",

    ["@text.literal"]        = "String",
    ["@tag"]                 = "Type",
  }
  for from, to in pairs(links) do set(from, { link = to }) end

  ---------------------------------------------------------------------------
  -- Telescope (minimal)
  ---------------------------------------------------------------------------
  set("TelescopeNormal",       { fg = p.fg, bg = p.ui })
  set("TelescopeBorder",       { fg = p.border, bg = p.ui })
  set("TelescopeSelection",    { bg = p.selection })
  set("TelescopeMatching",     { fg = p.blue, bold = true })

  set("Cursor",                { reverse = true })
  set("VisualNOS",             { bg = p.selection })
end

M.setup = M.colorscheme
return M

