
" Ensure python is supported
if !has('python')
	echo "Python is not supported by vim/os, but required by superdebug"
	finish
endif

command! SDebugLaunch call SDebug#Launch()
command! SDebugQuit call SDebug#Quit()
command! SDebugBreakpointSet call SDebug#SetBreakpoint()

nnoremap <Leader>s :SDebugLaunch<CR>
