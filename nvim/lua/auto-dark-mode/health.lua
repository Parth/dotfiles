local M = {}

local uv = vim.uv or vim.loop

local adm = require("auto-dark-mode")
local interval = require("auto-dark-mode.interval")

M.benchmark = function(iterations)
	local result = {
		avg = 0,
		max = 0,
		min = math.huge,
		all_results = {},
		stdout = nil,
		stderr = nil,
		parsed = nil,
	}

	for _ = 1, iterations do
		local _start = uv.hrtime()
		-- parsing the response is measured, but actually syncing the vim theme isn't performed
		local function callback(_stdout, _stderr)
			result.stdout = _stdout
			result.stderr = _stderr
			result.parsed = interval.parse_callback(_stdout, _stderr)
			vim.schedule_wrap(function()
				vim.print(result)
			end)
		end

		local success, _ = pcall(interval.poll_dark_mode, callback)
		-- bail early if polling fails
		if not success then
			break
		end
		local _end = uv.hrtime()

		table.insert(result.all_results, (_end - _start) / 1e6)
	end

	local sum = 0
	for _, v in pairs(result.all_results) do
		result.max = result.max > v and result.max or v
		result.min = result.min < v and result.min or v
		sum = sum + v
	end
	result.avg = sum / iterations

	return result
end

-- support for neovim < 0.9.0
local H = vim.health
local health = {}
health.start = H.start or H.report_start
health.ok = H.ok or H.report_ok
health.info = H.info or H.report_info
health.error = H.error or H.report_error

M.check = function()
	health.start("auto-dark-mode.nvim")

	if adm.state.setup_correct then
		health.ok("Setup is correct")
	else
		health.error("Setup is incorrect")
	end

	health.info(string.format("Detected operating system: %s", adm.state.system))
	health.info(string.format("Using query command: `%s`", table.concat(adm.state.query_command, " ")))

	interval.poll_dark_mode(function(stdout, stderr)
		vim.schedule(function()
			health.info(string.format("Query response:\nstdout: %s\nstderr: %s\n", stdout, stderr))
		end)
	end)

	local benchmark = M.benchmark(30)
	health.info(
		string.format("Benchmark: %.2fms avg / %.2fms min / %.2fms max", benchmark.avg, benchmark.min, benchmark.max)
	)

	local update_interval = adm.options.update_interval
	local ratio = update_interval / benchmark.avg
	local msg = {
		info = string.format("Update interval (%dms) is %.2fx the average query time", update_interval, ratio),
		error = string.format(
			"Update interval (%dms) seems too short compared to current benchmarks, consider increasing it",
			update_interval
		),
	}

	if ratio > 30 then
		health.ok(msg.info)
	elseif ratio > 5 then
		health.warn(msg.info)
	else
		health.error(msg.error)
	end
end

return M
