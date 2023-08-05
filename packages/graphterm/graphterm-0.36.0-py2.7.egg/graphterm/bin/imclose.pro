; $Header: /home/nash/IDLlib/RCS/imclose.pro,v 1.2 2001/03/08 15:52:37 nash Exp $
function imclose_colorimage
common colors, r_orig, g_orig, b_orig, r_curr, g_curr, b_curr
greyimage=tvrd()

imagesize=size(greyimage)
if(imagesize[0] ne 2) then $
  stop,'Unexpected image size from tvrd: image was not 2-dimensional'

colorimage=bytarr(3,imagesize[1],imagesize[2])
colorimage[0,*,*]=r_curr[greyimage]
colorimage[1,*,*]=g_curr[greyimage]
colorimage[2,*,*]=b_curr[greyimage]

return,colorimage
end


pro  imclose,dum

;+
; NAME:
;   imclose
; PURPOSE:
;   Closes the currently opened graphics file.
; CATEGORY:
;   graphics
; CALLING SEQUENCE:
;   imclose
; FUNCTION RETURN VALUE:
; INPUT PARAMETERS:
; INPUT/OUTPUT PARAMETERS:
; OPTIONAL INPUT/OUTPUT PARAMETERS:
; OUTPUT PARAMETERS:
; OPTIONAL OUTPUT PARAMETERS:
; INPUT KEYWORDS:
; INPUT/OUTPUT KEYWORDS:
; OUTPUT KEYWORDS:
; COMMON BLOCKS:
;   (IMOPCL) for versions < 5.3
;   old_device = device value before executing imopen
; REQUIRED ROUTINES:
; @ FILES:
; RESTRICTIONS:
; SIDE EFFECTS:
; DIAGNOSTIC INFORMATION:
; PROCEDURE:
; EXAMPLES:
; REFERENCE:
; FURTHER INFORMATION:
; RELATED FUNCTIONS AND PROCEDURES:
;   imopen
; MODIFICATION HISTORY:
;   2001-03-08:nash:added system variable
;-

; *****save image file if necessary
common imopen_imclose,filetype=filetype,filename=filename,$
  write_progressive=write_progressive,quality=quality,active=active
common colors, r_orig, g_orig, b_orig, r_curr, g_curr, b_curr

; make sure imopen was called since the last imclose
if ~keyword_set(active) then begin
  message,/cont,'There is no file to close.  (Either you have not successfully called imopen or you have already called imclose.)'
  return
end

; declare the imopen...imclose block to be ended so future calls to
; imclose will give an error:
active=0

full_fn=filename+'.'+filetype
case strupcase(filetype) of
    'PNG': begin
        write_png,full_fn,tvrd(),r_curr,g_curr,b_curr
    end
    'GIF': begin
        write_gif,full_fn,tvrd(),r_curr,g_curr,b_curr
    end
    'JPG': begin
        write_jpeg,full_fn,imclose_colorimage(),progressive=want_progressive,$
                   quality=quality,true=1
    end
    'JPEG': begin
        write_jpeg,full_fn,imclose_colorimage(),progressive=want_progressive,$
                   quality=quality,true=1
    end
endcase

; *****close files
catch,error_status
if (error_status) then begin
    ; We reach this line if the "device,/close" line below fails.
    message,/cont,'There is no file to close.  (Either you have not successfully called imopen or you have already called imclose.)'
    return
endif
device,/close
catch,/cancel

; *****get old device so that it can be restored
if  (!version.release lt '5.3')  then  common  imopcl,old_device $
else  begin
    defsysv,'!old_device',exists=e
    if  (e)  then  old_device = !old_device $
    else  old_device = !d.name
endelse

; *****if no old device specified, exit
if  (n_elements(old_device) eq 0)  then  return

; *****reset old device
set_plot,old_device

return
end
