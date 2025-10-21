local M = {
	---@type uv_timer_t
	timer = nil,
	---@type number
	timer_id = nil,
	---@type Appearance?
	current_appearance = nil,
}

local uv = vim.uv or vim.loop

-- Parses the query response for each system, returning the current appearance,
-- or `nil` if it can't be resolved.
---@param stdout string
---@param stderr string
---@return Appearance?
local function parse_query_response(stdout, stderr)
	if M.state.system == "Linux" then
        if stderr ~= "" then
            return nil;
        end

		-- https://github.com/flatpak/xdg-desktop-portal/blob/c0f0eb103effdcf3701a1bf53f12fe953fbf0b75/data/org.freedesktop.impl.portal.Settings.xml#L32-L46
		-- 0: no preference
		-- 1: dark
		-- 2: light
		if string.match(stdout, "uint32 1") ~= nil then
			return "dark"
		elseif string.match(stdout, "uint32 [02]") ~= nil then
			return "light"
		else
			return M.options.fallback
		end
	elseif M.state.system == "Darwin" or M.state.system == "OrbStack" then
		return stdout == "Dark\n" and "dark" or "light"
	elseif M.state.system == "Windows_NT" or M.state.system == "WSL" then
		-- AppsUseLightTheme REG_DWORD 0x0 : dark
		-- AppsUseLightTheme REG_DWORD 0x1 : light
		return string.match(stdout, "0x1") and "light" or "dark"
	end

	return nil
end

-- Executes the `set_dark_mode` and `set_light_mode` hooks when needed,
-- otherwise it's a no-op.
---@param appearance Appearance
---@return nil
local function sync_theme(appearance)
	if appearance == M.current_appearance then
		return
	end

	M.current_appearance = appearance
	if M.current_appearance == "dark" then
		if vim.system then
			vim.schedule(M.options.set_dark_mode)
		else
			M.options.set_dark_mode()
		end
	elseif M.current_appearance == "light" then
		if vim.system then
			vim.schedule(M.options.set_light_mode)
		else
			M.options.set_light_mode()
		end
	end
end

-- Uses a subprocess to query the system for the current dark mode setting.
-- The callback is called with the plaintext stdout response of the query.
---@param callback? fun(stdout: string, stderr: string): nil
---@return nil
M.poll_dark_mode = function(callback)
	-- if no callback is provided, use a no-op
	if callback == nil then
		callback = function() end
	end

	if vim.system then
		vim.system(M.state.query_command, { text = true }, function(data)
			callback(data.stdout, data.stderr)
		end)
	else
		-- Legacy implementation using `vim.fn.jobstart` instead of `vim.system`,
		-- for use in neovim <0.10.0
		local stdout = ""
		local stderr = ""

		vim.fn.jobstart(M.state.query_command, {
			stderr_buffered = true,
			stdout_buffered = true,
			on_stderr = function(_, data, _)
				stderr = table.concat(data, " ")
			end,
			on_stdout = function(_, data, _)
				stdout = table.concat(data, " ")
			end,
			on_exit = function(_, _, _)
				callback(stdout, stderr)
			end,
		})
	end
end

---@param stdout string
---@param stderr string
---@return nil
M.parse_callback = function(stdout, stderr)
	local appearance = parse_query_response(stdout, stderr)

	if appearance ~= nil then
		sync_theme(appearance)
	end
end

local timer_callback = function()
	M.poll_dark_mode(M.parse_callback)
end

---@return nil
M.start_timer = function()
	---@type number
	local interval = M.options.update_interval

	-- needs to check for `vim.system` because the poll function depends on it
	if uv and vim.system then
		M.timer = uv.new_timer()
		M.timer:start(interval, interval, timer_callback)
	else
		M.timer_id = vim.fn.timer_start(interval, timer_callback, { ["repeat"] = -1 })
	end
end

---@return nil
M.stop_timer = function()
	if uv.timer_stop then
		uv.timer_stop(M.timer)
	else
		vim.fn.timer_stop(M.timer_id)
	end
end

---@param options AutoDarkModeOptions
---@param state AutoDarkModeState
---@return nil
M.start = function(options, state)
	M.options = options
	M.state = state

	-- act as if the timer has finished once to instantly sync on startup
	timer_callback()

	M.start_timer()
end

return M
