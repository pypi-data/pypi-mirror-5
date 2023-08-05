; $Header: /home/nash/IDLlib/RCS/imopen.pro,v 1.3 2001/03/08 16:05:16 nash Exp nash $

pro  imopen,type,fn=fn,color=color,portrait=portrait,landscape=landscape, $
            xoffset=xoffset,xsize=xsize,yoffset=yoffset,ysize=ysize,$
            progressive=progressive,jpegquality=jpegquality

;+
; NAME:
;   imopen
; PURPOSE:
;   Opens a tek, postscript, or encapsulated postscript file for graphics 
;   output.
; CATEGORY:
;   graphics
; CALLING SEQUENCE:
;   imopen
; FUNCTION RETURN VALUE:
; INPUT PARAMETERS:
;   type = (string) file type. Must be one of (upper or lower case):
;            'TEK', 'PS', 'EPS', 'CPS', 'JPEG', 'JPG', 'GIF' or 'PNG'. 
; INPUT/OUTPUT PARAMETERS:
; OPTIONAL INPUT/OUTPUT PARAMETERS:
; OUTPUT PARAMETERS:
; OPTIONAL OUTPUT PARAMETERS:
; INPUT KEYWORDS:
;   color     = (integer) color number to use. See the loadct routine for this 
;                 value
;   fn        = (string) file name. Will be appended with '.tek', ',ps', 
;                 '.eps', etc.
;   portrait  = (flag) set this to do portrait orientation
;   landscape = (flag) set this to do landscape orientation (default)
;   xoffset   = (float) number of inches to offset in the x
;               direction.  Only applies to TEK, EPS, PS and CPS file types.
;   xsize     = (float) size of plotting area in the x direction.
;               With PS, CPS, EPS and TEK, this is in inches.  With
;               other output types, this is in pixels.  Default: 512.
;   yoffset   = (float) number of inches to offset in the y
;               direction.  Only applies to TEK, EPS, PS and CPS file types.
;   ysize     = (float) size of plotting area in the y direction in inches. 
;               With PS, CPS, EPS and TEK, this is in inches.  With
;               other output types, this is in pixels.  Default: 512.
;   jpegquality = 0..100.  Percentage quality.  Higher percentages
;                 mean less data loss but larger files.  Lower
;                 percentages mean more data loss but smaller files.
;                 Anything above 95% will give effectively no gain in
;                 quality.  100% quality is still lossy compression.
;                 Defaults to 85.
;   progressive = (flag) if saving as a JPEG, use the Netscape
;                 progressive extension to the JPEG standard
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
;   imclose
; MODIFICATION HISTORY:
;   2001-03-08:nash:added system variable
;-

common imopen_imclose,filetype=filetype,filename=filename,$
  write_progressive=write_progressive,quality=quality,active=active

if(n_elements(xsize) eq 0) then xsize=512
if(n_elements(ysize) eq 0) then ysize=512

if keyword_set(active) then begin
    stop,'You have already called imopen without calling imclose.'
end

active=1

; *****save old device so that it can be restored in IMCLOSE
if  (!version.release ge '5.3')  then  defsysv,'!old_device',!d.name $
else  begin
    common  imopcl,old_device
    old_device = !d.name 
endelse

; *****set default for TYPE and FN
if  (n_elements(type) eq 0)  then  type = 'PS'
if  (n_elements(fn) eq 0)  then  fn = 'idl'
port = ((not keyword_set(landscape)) and (keyword_set(portrait)))
land = ~port
if  (port)  then  begin
    if  (n_elements(xsize) eq 0)  then  xsize = 7
    if  (n_elements(xoffset) eq 0)  then  xoffset = .75
    if  (n_elements(ysize) eq 0)  then  ysize = 9.5
    if  (n_elements(yoffset) eq 0)  then  yoffset = .75
endif  else  begin
    if  (n_elements(xsize) eq 0)  then  xsize = 9.5
    if  (n_elements(xoffset) eq 0)  then  xoffset = .75
    if  (n_elements(ysize) eq 0)  then  ysize = 7.
    if  (n_elements(yoffset) eq 0)  then  yoffset = 10.25
endelse

; save imopen_imclose common block dataa
filetype=type
filename=fn
want_progressive=keyword_set(progressive)
if n_elements(jpegquality) gt 0 then quality=jpegquality else quality=85


; *****set plot to device type wanted
case  strupcase(type)  of
    'GIF' : begin
        set_plot,'Z'
        device,set_resolution=[xsize,ysize]
        if  (n_elements(color) ne 0)  then  loadct,color
    end
    'PNG' : begin
        set_plot,'Z'
        device,set_resolution=[xsize,ysize]
        if  (n_elements(color) ne 0)  then  loadct,color
    end
    'JPG': begin
        set_plot,'Z'
        device,set_resolution=[xsize,ysize]
        if  (n_elements(color) ne 0)  then  loadct,color
    end
    'JPEG' : begin
        set_plot,'Z'
        device,set_resolution=[xsize,ysize]
        if  (n_elements(color) ne 0)  then  loadct,color
    end
    'CPS' : begin
        set_plot,'PS'
        device,file=fn+'.cps',/color,encap=0,land=land,port=port, $
               /inch,xsize=xsize,ysize=ysize,xoffset=xoffset,yoffset=yoffset
        if  (n_elements(color) ne 0)  then  loadct,color
    end
    'EPS' : begin
        set_plot,'PS'
        device,file=fn+'.eps',color=color,encap=1,land=land,port=port, $
               /inch,xsize=xsize,ysize=ysize,xoffset=xoffset,yoffset=yoffset
        if  (n_elements(color) ne 0)  then  loadct,color
    end
    'PS'  : begin
        set_plot,'PS'
        device,file=fn+'.ps',color=color,encap=0,land=land,port=port, $
               /inch,xsize=xsize,ysize=ysize,xoffset=xoffset,yoffset=yoffset
        if  (n_elements(color) ne 0)  then  loadct,color
    end
    'TEK' : begin
        set_plot,'TEK'
        device,/tek4100,file=fn+'.tek',/tty
    end
    else  : begin
        message,/cont,'Type must be TEK, PS, EPS, CPS, JPEG, JPG, GIF or PNG - Respecify'
        return
    end
endcase
return
end
