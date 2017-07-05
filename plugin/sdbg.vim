
" Ensure python is supported
if !has('python')
	echo "Python is not supported by vim, but required by superdebug"
	finish
endif

command! DBGLaunch call sdbg#DBGLaunch()
nnoremap <Leader>b :DBGLaunch<CR>
