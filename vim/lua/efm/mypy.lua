return {
    lintCommand = "mypy --show-column-numbers --ignore-missing-imports",
    lintFormats = {
        "%f:%l:%c: %trror: %m",
        "%f:%l:%c: %tarning: %m",
        "%f:%l:%c: %tote: %m",
    },
    lintSource = "mypy",
}
