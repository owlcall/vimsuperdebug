
" Ensure python3 is supported
if !has('python3')
	echo "Python3 is not supported by vim/os, but required by superdebug"
	finish
endif

command! DBGLaunch call sdbg#DBGLaunch()
nnoremap <Leader>s :DBGLaunch<CR>
