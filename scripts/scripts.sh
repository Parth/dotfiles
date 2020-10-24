function gpu {
  lspci -k | grep -i --color 'vga' -A3
}