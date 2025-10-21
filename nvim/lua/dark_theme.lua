local M = {};

-- lua/colors/premonition_dark.lua
-- Mnemonic Dark Premonition – Neovim colorscheme (starter)
-- Palette derived from your JSON theme.

local p = {
  bg            = "#080808",
  fg            = "#FFFFFF",
  fg_muted      = "#D0D0D0",
  comment       = "#808080",
  border        = "#505050",

  -- Accents
  cyan          = "#6EECF7",
  cyan_bright   = "#9EF2FA",
  green         = "#67E4B6",
  green_bright  = "#93ECCB",
  yellow        = "#FFDB70",
  yellow_bright = "#FFE699",
  red           = "#FF6680",
  red_bright    = "#FF99AA",
  blue          = "#66B2FF",
  blue_bright   = "#80BFFF",
  magenta       = "#AC8CD9",
  magenta_bright= "#BA9FDF",

  -- UI surfaces
  ui            = "#1A1A1A",     -- status/tab/toolbars
  panel         = "#00000000",   -- transparent-ish; we’ll blend to ui
  active_line   = "#242424",     -- approx of #A0A0A020 over bg
  selection     = "#2A2A2A",     -- comfy visual selection
  search_bg     = "#16454A",     -- readable take on #13DAEC40
  gutter_bg     = "#00000000",   -- transparent in your theme

  -- Diagnostics backgrounds from your JSON (softened)
  info_bg       = "#26322D",
  hint_bg       = "#003366",
  error_bg      = "#660011",
  warn_bg       = "#806000",
}

local function set(name, val) vim.api.nvim_set_hl(0, name, val) end

local function setup_terminal()
  -- Map terminal ANSI to your palette
  vim.g.terminal_color_0  = p.border       -- black
  vim.g.terminal_color_8  = p.fg_muted     -- bright black (gray)

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

  vim.g.terminal_color_7  = p.fg_muted
  vim.g.terminal_color_15 = p.fg
end

function M.colorscheme()
  vim.cmd("highlight clear")
  if vim.fn.exists("syntax_on") == 1 then vim.cmd("syntax reset") end

  vim.o.background = "dark"
  vim.g.colors_name = "premonition_dark"
  setup_terminal()

  ---------------------------------------------------------------------------
  -- Core editor
  ---------------------------------------------------------------------------
  set("Normal",         { fg = p.fg, bg = p.bg })
  set("NormalNC",       { fg = p.fg_muted, bg = p.bg })
  set("SignColumn",     { bg = p.bg })
  set("LineNr",         { fg = p.fg_muted, bg = p.bg })
  set("CursorLineNr",   { fg = p.cyan, bg = p.active_line, bold = true })
  set("CursorLine",     { bg = p.active_line })
  set("CursorColumn",   { bg = p.active_line })
  set("ColorColumn",    { bg = p.active_line })
  set("VertSplit",      { fg = p.border, bg = p.bg })
  set("WinSeparator",   { fg = p.border, bg = p.bg })

  set("Folded",         { fg = p.fg_muted, bg = p.active_line })
  set("FoldColumn",     { fg = p.fg_muted, bg = p.bg })

  set("Visual",         { bg = p.selection })
  set("Search",         { fg = p.bg, bg = p.search_bg })
  set("IncSearch",      { fg = p.bg, bg = p.cyan })
  set("MatchParen",     { fg = p.yellow, bold = true })

  set("Pmenu",          { fg = p.fg, bg = p.ui })
  set("PmenuSel",       { fg = p.bg, bg = p.cyan })
  set("PmenuSbar",      { bg = p.active_line })
  set("PmenuThumb",     { bg = p.border })

  set("StatusLine",     { fg = p.fg, bg = p.ui })
  set("StatusLineNC",   { fg = p.fg_muted, bg = p.ui })
  set("TabLine",        { fg = p.fg_muted, bg = p.ui })
  set("TabLineSel",     { fg = p.fg, bg = p.active_line, bold = true })
  set("TabLineFill",    { bg = p.ui })

  set("Whitespace",     { fg = p.border })
  set("NonText",        { fg = p.border })
  set("SpecialKey",     { fg = p.border })

  ---------------------------------------------------------------------------
  -- Syntax (Vim groups)
  ---------------------------------------------------------------------------
  set("Comment",        { fg = p.comment, italic = true })
  set("Identifier",     { fg = p.fg })
  set("Function",       { fg = p.green, bold = true })
  set("Statement",      { fg = p.magenta })       -- e.g. if/for/return
  set("Keyword",        { fg = p.magenta, italic = true })
  set("Conditional",    { fg = p.magenta })
  set("Repeat",         { fg = p.magenta })
  set("Operator",       { fg = p.comment })
  set("Type",           { fg = p.blue })
  set("StorageClass",   { fg = p.blue })
  set("Structure",      { fg = p.blue })
  set("Constant",       { fg = p.cyan })
  set("Boolean",        { fg = p.cyan })
  set("Number",         { fg = p.cyan })
  set("String",         { fg = p.cyan })
  set("Character",      { fg = p.cyan })
  set("Special",        { fg = p.green })
  set("Delimiter",      { fg = p.comment })

  ---------------------------------------------------------------------------
  -- Diagnostics (LSP)
  ---------------------------------------------------------------------------
  set("Error",                 { fg = p.red })
  set("Todo",                  { fg = p.yellow, bold = true })
  set("ErrorMsg",              { fg = p.red, bg = p.error_bg, bold = true })
  set("WarningMsg",            { fg = p.yellow, bg = p.warn_bg })
  set("MoreMsg",               { fg = p.green })
  set("Question",              { fg = p.green })

  set("DiagnosticError",       { fg = p.red })
  set("DiagnosticWarn",        { fg = p.yellow })
  set("DiagnosticInfo",        { fg = p.fg_muted })
  set("DiagnosticHint",        { fg = p.fg_muted })
  set("DiagnosticOk",          { fg = p.green })

  set("DiagnosticUnderlineError", { sp = p.red, undercurl = true })
  set("DiagnosticUnderlineWarn",  { sp = p.yellow, undercurl = true })
  set("DiagnosticUnderlineInfo",  { sp = p.blue, undercurl = true })
  set("DiagnosticUnderlineHint",  { sp = p.magenta, undercurl = true })

  set("DiagnosticVirtualTextError", { fg = p.red, bg = p.error_bg })
  set("DiagnosticVirtualTextWarn",  { fg = p.yellow, bg = p.warn_bg })
  set("DiagnosticVirtualTextInfo",  { fg = p.fg_muted, bg = p.info_bg })
  set("DiagnosticVirtualTextHint",  { fg = p.fg_muted, bg = p.hint_bg })

  ---------------------------------------------------------------------------
  -- Diff / Git
  ---------------------------------------------------------------------------
  set("DiffAdd",    { bg = "#1f2b26", fg = p.green })  -- soft green bg
  set("DiffChange", { bg = "#2b2b1f", fg = p.yellow })
  set("DiffDelete", { bg = "#2b1f23", fg = p.red })
  set("DiffText",   { bg = "#354134", bold = true })

  set("GitSignsAdd",    { fg = p.green })
  set("GitSignsChange", { fg = p.yellow })
  set("GitSignsDelete", { fg = p.red })

  ---------------------------------------------------------------------------
  -- Treesitter (link to Vim groups to keep it lean)
  ---------------------------------------------------------------------------
  local links = {
    -- Basics
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

    -- Diagnostics / misc
    ["@text.literal"]        = "String",
    ["@tag"]                 = "Type",
  }
  for from, to in pairs(links) do set(from, { link = to }) end

  ---------------------------------------------------------------------------
  -- Plugin niceties (Telescope minimal)
  ---------------------------------------------------------------------------
  set("TelescopeNormal",       { fg = p.fg, bg = p.ui })
  set("TelescopeBorder",       { fg = p.border, bg = p.ui })
  set("TelescopeSelection",    { bg = p.selection })
  set("TelescopeMatching",     { fg = p.cyan, bold = true })

  -- Make current line stand out just a bit
  set("Cursor",                { reverse = true })
  set("VisualNOS",             { bg = p.selection })
end

M.setup = M.colorscheme
return M

